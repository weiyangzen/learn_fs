# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_main.c lines 9670-9815

## Chunk Scope

This chunk covers the Linux `net_device_ops` boundary for the Intel E800 `ice`
driver's PF netdevice. It includes the public close callback `ice_stop()`, the
TX offload guard `ice_features_check()`, and the normal versus safe-mode
`struct net_device_ops` tables that bind the rest of the driver to the kernel
networking stack.

The code sits immediately after `ice_open()`/`ice_open_internal()`. The open
path updates PHY/link state, initializes user PHY configuration when needed,
brings the physical link up when media is available, and calls
`ice_vsi_open()`. This chunk provides the corresponding close path and then
publishes the driver callback surface used for open/close, transmit, feature
management, VLAN, SR-IOV VF controls, bridge/FDB operations, traffic control,
XDP/AF_XDP, and PTP hardware timestamping.

## Purpose and Responsibilities

- Quiesce a PF netdevice through `ice_stop()` when the interface is
  administratively brought down, while refusing to race a PF reset/rebuild.
- Optionally force the PHY link down on close when the private
  `link-down-on-close` flag is enabled, before releasing VSI queue resources.
- Validate per-packet checksum/GSO offload eligibility against the ice TX
  descriptor encoding limits, especially for encapsulated traffic.
- Expose a restricted safe-mode netdev operation set when the driver did not
  load a usable DDP package or is otherwise in reduced-function mode.
- Expose the full normal netdev operation table for data path, offload,
  virtualization, bridge, XDP, AF_XDP, and timestamping integration.

## Important APIs, Types, and Functions

- `int ice_stop(struct net_device *netdev)`: `ndo_stop` implementation. It
  retrieves `struct ice_netdev_priv` via `netdev_priv()`, then uses `np->vsi`
  and `vsi->back` to reach the PF. It returns `-EBUSY` during reset and `-EIO`
  if optional PHY-down reconfiguration fails; otherwise it closes the VSI and
  returns zero.
- `static netdev_features_t ice_features_check(struct sk_buff *skb, struct net_device *netdev, netdev_features_t features)`:
  `ndo_features_check` implementation. It preserves features for packets that
  do not request `CHECKSUM_PARTIAL`, removes GSO for too-small MSS, and removes
  checksum plus GSO offloads when header lengths cannot be represented by the
  hardware TX descriptor context.
- `struct ice_netdev_priv`: private netdev storage that links the kernel
  `struct net_device` to its `struct ice_vsi`.
- `struct ice_vsi`: VSI object representing the PF's LAN interface. In this
  chunk it supplies `vsi->back`, `vsi->netdev`, `vsi->vsi_num`, and the
  queue/interrupt resources that `ice_vsi_close()` releases.
- `struct ice_pf`: PF-wide state. `ice_stop()` gates on `pf->state` reset bits
  and reads `pf->flags` for `ICE_FLAG_LINK_DOWN_ON_CLOSE_ENA`.
- `ice_is_reset_in_progress(pf->state)`: common reset guard used by open,
  stop, feature changes, suspend, and other netdev-facing paths so userspace
  callbacks do not mutate queue or PHY state while reset recovery owns it.
- `ice_phy_cfg(vsi, bool link_en)`: PHY programming helper. With `false`, the
  stop path asks firmware/shared-code to disable the physical link if media is
  present and if the current PHY configuration needs a change. It can return
  `-ENOMEDIUM` when no media is attached.
- `ice_vsi_close(vsi)`: lower-level VSI shutdown from `ice_lib.c`. It marks
  `ICE_VSI_DOWN`, calls `ice_down()` if this is the first close, clears NAPI
  queue associations, frees IRQs, and frees TX/RX rings.
- `ice_netdev_safe_mode_ops`: reduced callback table used by `ice_set_ops()`
  when `ice_is_safe_mode(pf)` is true. It keeps basic open/stop/transmit,
  address, MTU, stats, TX timeout, and an XDP handler that rejects XDP with an
  extack explaining that working DDP firmware is required.
- `ice_netdev_ops`: full callback table for normal PF operation. It connects
  the kernel netdev core to local helpers for queue selection, feature checks,
  RX mode, MAC/MTU/statistics, VF management, VLAN, TC, bridge/FDB, RFS,
  BPF/XDP, AF_XDP wakeups, and PTP hwtstamp get/set.

## Control Flow

### `ice_stop()`

The stop path starts from the kernel netdev core through `.ndo_stop`. It maps
`netdev -> ice_netdev_priv -> ice_vsi -> ice_pf` and first checks whether a
reset is already in progress. If so, it logs `"can't stop net device while reset
is in progress"` and returns `-EBUSY`; this preserves reset ownership over VSI
and PHY teardown.

When `ICE_FLAG_LINK_DOWN_ON_CLOSE_ENA` is set in `pf->flags`, `ice_stop()`
calls `ice_phy_cfg(vsi, false)` before queue teardown. A `-ENOMEDIUM` result is
treated as an informational "Skipping link reconfig" condition because a
medialess port cannot be programmed. Other PHY failures are reported as
errors. In both failure cases, the code still calls `ice_vsi_close(vsi)` to
stop software/hardware queues and free per-open resources, then returns `-EIO`.

If the PHY-down step is disabled or succeeds, the function calls
`ice_vsi_close(vsi)` once and returns zero. The close work itself is delegated
to the VSI layer, which performs idempotence through `ICE_VSI_DOWN` and handles
queue, NAPI, interrupt, and ring cleanup.

### `ice_features_check()`

The feature-check callback is invoked by the networking stack during transmit
feature negotiation for a specific `skb`. It first tests `skb_is_gso(skb)` and
then exits early unless `skb->ip_summed == CHECKSUM_PARTIAL`. That early exit is
important: if software checksum is already selected, the hardware descriptor
limits in this function do not matter.

For GSO packets, the function removes `NETIF_F_GSO_MASK` when
`skb_shinfo(skb)->gso_size` is below `ICE_TXD_CTX_MIN_MSS` (64 bytes), because
the TX context descriptor cannot encode a smaller MSS. It then validates outer
L2 and L3 lengths:

- `skb_network_offset(skb)` must fit `ICE_TXD_MACLEN_MAX` and be even.
- `skb_network_header_len(skb)` must fit `ICE_TXD_IPLEN_MAX` and be even.

For encapsulated packets, it adds inner-header validation. When a GSO packet is
GRE or UDP tunnel traffic, it calculates the outer L4/tunnel header span as
`skb_inner_network_header(skb) - skb_transport_header(skb)` and checks it
against `ICE_TXD_L4LEN_MAX` with the same even-length requirement. It also
checks the inner network header length against `ICE_TXD_IPLEN_MAX`.

Any header length violation jumps to `out_rm_features`, returning
`features & ~(NETIF_F_CSUM_MASK | NETIF_F_GSO_MASK)`. This does not drop the
packet; it tells the stack to avoid checksum and segmentation offloads for that
frame so software can handle it.

### Netdev Operation Tables

`ice_netdev_safe_mode_ops` is deliberately small. It supports enough callbacks
for a netdevice to open, close, transmit basic traffic, change MAC/MTU, validate
addresses, report stats, handle TX timeouts, and reject XDP setup cleanly. It
does not advertise feature checks, TC, VLAN, SR-IOV VF controls, bridge/FDB,
AF_XDP, or PTP timestamping.

`ice_netdev_ops` is the normal table. It includes all safe-mode basics plus
driver-specific callbacks for queue selection, features validation/fix/set,
multicast/unicast filter programming, queue max-rate, SR-IOV VF settings and
stats, VLAN add/delete, TC offloads, bridge mode, FDB operations, optional RFS
steering, XDP attach/transmit, AF_XDP wakeup, and hwtstamp control. Earlier in
the file, `ice_set_ops()` assigns one of these tables to `netdev->netdev_ops`;
`netif_is_ice()` also uses pointer equality against these two tables to
recognize ice netdevices.

## State and Persistence Behavior

- `pf->state` is the primary concurrency gate. `ice_stop()` refuses to run
  during reset/rebuild, matching nearby open and feature-change guards. The
  actual reset machinery is elsewhere in `ice_main.c`, but this callback must
  not free rings or reprogram PHY while reset recovery is already tearing down
  or rebuilding those resources.
- `pf->flags` holds durable driver/private-flag configuration. In this chunk
  the relevant bit is `ICE_FLAG_LINK_DOWN_ON_CLOSE_ENA`, exposed through the
  driver's private ethtool flag `link-down-on-close`. The setting persists as
  PF software intent and changes whether administrative close affects the
  physical link, not just netdev queue state.
- VSI runtime state is changed by `ice_vsi_close()`, not directly in this
  chunk. The close helper sets `ICE_VSI_DOWN`, stops data path activity,
  disconnects NAPI queues, releases IRQ resources, and frees TX/RX rings. These
  resources are reallocated by `ice_vsi_open()` on a later `ndo_open`.
- PHY state is firmware/hardware state. `ice_phy_cfg(vsi, false)` may program
  a link-disabled PHY configuration, but only when media/topology allow it. A
  medialess port cannot be reconfigured, so the driver still closes the VSI and
  logs the skipped PHY update.
- `ice_features_check()` does not persist state. It computes a per-SKB feature
  mask from current packet layout and the descriptor field limits defined in
  `ice_lan_tx_rx.h`.
- The two `net_device_ops` structures are static read-only callback contracts.
  Assignment of either table persists in `netdev->netdev_ops` for the netdev
  lifetime or until setup/recovery code changes the mode.

## Dependencies and Integration Points

- Linux netdev lifecycle: `.ndo_open = ice_open` and `.ndo_stop = ice_stop`
  are called for administrative `IFF_UP`/down transitions. `.ndo_start_xmit`
  enters the normal TX data path, and `.ndo_tx_timeout` integrates with the
  netdev watchdog.
- Linux SKB/offload model: `skb_is_gso()`, `skb_shinfo()`,
  `skb_network_offset()`, `skb_network_header_len()`,
  `skb_inner_network_header()`, `skb_transport_header()`, `CHECKSUM_PARTIAL`,
  `SKB_GSO_GRE`, `SKB_GSO_UDP_TUNNEL`, `NETIF_F_GSO_MASK`, and
  `NETIF_F_CSUM_MASK` are core networking APIs used to decide whether TX
  offloads are safe for a specific frame.
- Hardware descriptor definitions: `ICE_TXD_CTX_MIN_MSS`,
  `ICE_TXD_MACLEN_MAX`, `ICE_TXD_IPLEN_MAX`, and `ICE_TXD_L4LEN_MAX` come from
  `ice_lan_tx_rx.h` and encode the limits of ice TX descriptor fields.
- PHY/shared-code path: `ice_phy_cfg()` uses AdminQ/shared-code PHY capability
  and configuration commands. The stop path depends on its media checks and
  error returns to decide logging and final status.
- VSI lifecycle path: `ice_vsi_close()` in `ice_lib.c` owns the real queue and
  interrupt teardown, keeping the netdev callback small and aligned with other
  users such as reset, suspend, and subfunction close paths.
- SR-IOV: normal ops expose `ice_set_vf_spoofchk()`, `ice_set_vf_mac()`,
  `ice_get_vf_cfg()`, `ice_set_vf_trust()`, `ice_set_vf_port_vlan()`,
  `ice_set_vf_link_state()`, `ice_get_vf_stats()`, and `ice_set_vf_bw()`.
  These integrate PF netdev netlink operations with VF state in `ice_sriov.c`.
- VLAN, TC, bridge, and FDB integration: normal ops connect VLAN RX filter
  changes, traffic-control setup, bridge mode get/set, and FDB add/delete to
  the PF switch/filtering logic in this file and related modules.
- XDP and AF_XDP: normal ops call `ice_xdp()`, `ice_xdp_xmit()`, and
  `ice_xsk_wakeup()`. Safe mode only provides `ice_xdp_safe_mode()`, which
  rejects setup because the DDP package is required for full programmable data
  path support.
- PTP timestamping: normal ops expose `ice_ptp_hwtstamp_get()` and
  `ice_ptp_hwtstamp_set()`, linking standard hwtstamp ioctl/netlink control to
  the driver's PTP module.

## Risks and Edge Cases

- The comment above `ice_stop()` says "Returns success only - not allowed to
  fail", but the implementation can return `-EBUSY` during reset and `-EIO`
  after PHY reconfiguration failure. Callers and tests should treat the actual
  behavior as authoritative; this mismatch is a documentation hazard.
- If `link-down-on-close` is enabled and no media is attached,
  `ice_phy_cfg()` returns `-ENOMEDIUM`; `ice_stop()` logs an informational
  skip, still closes the VSI, but returns `-EIO`. That may surface an error to
  userspace even though the practical queue teardown succeeded.
- The reset guard prevents racing reset recovery, but it also means a user
  administrative close attempted during reset can fail and leave the netdev
  logically up from the stack's perspective until retried or recovery completes.
- PHY-down-on-close changes physical link behavior for the whole port. In
  multi-function, SR-IOV, or management-controller environments, tests should
  verify that forcing link down on PF close matches platform expectations.
- `ice_features_check()` relies on SKB header pointers being valid and
  representing the tunnel layout expected by the stack. Incorrect tunnel
  metadata could cause the callback to preserve offloads for a frame whose
  hardware context is not representable, or to disable offloads unnecessarily.
- The even-length checks are easy to overlook. Descriptor fields express some
  lengths in words or dwords, so odd L2/L3/L4 header spans cause checksum and
  GSO offloads to be stripped even when the absolute length is below the max.
- For encapsulated GSO, the outer L4 length calculation is intentionally only
  applied to GRE and UDP tunnel GSO types. IPIP/SIT-style packets can have
  transport header placement that would make the same subtraction invalid.
  Changes to tunnel/GSO type handling need to preserve that distinction.
- Safe-mode and normal-mode operation tables are selected by pointer assignment
  and later recognized by pointer comparison. Adding another ice netdev ops
  table without updating `netif_is_ice()` can break code that asks whether a
  netdev belongs to this driver.
- Feature exposure differs sharply between safe mode and normal mode. Any
  caller that assumes XDP, hwtstamp, VF controls, TC, VLAN, or bridge callbacks
  always exist must handle safe-mode absence or `-EOPNOTSUPP`.

## Test Signals and Validation Ideas

- Bring a PF netdev up and down normally. Confirm `ice_open()` allocates queues
  and `ice_stop()` calls the VSI close path without reset warnings, leaked IRQs,
  or ring allocation leftovers on repeated cycles.
- Toggle the private `link-down-on-close` flag and close the interface with
  media present. Verify the physical link is disabled on close and restored by
  the next open path.
- Repeat close with `link-down-on-close` enabled and no media attached. The
  expected signal is the "Skipping link reconfig - no media attached" log, VSI
  resources released, and the observed userspace error path documented.
- Trigger or fault-inject a PF reset while issuing netdev close/open requests.
  `ice_stop()` should return `-EBUSY` and avoid double-freeing queue, NAPI, or
  IRQ resources owned by reset recovery.
- Exercise TX with CHECKSUM_PARTIAL and GSO packets near descriptor limits:
  MSS below 64 should clear GSO; oversized or odd outer L2/L3 lengths should
  clear checksum and GSO; valid packets should preserve requested features.
- Exercise encapsulated GRE and UDP tunnel GSO packets with boundary L4 and
  inner-L3 header lengths. Confirm offload retention below limits and software
  fallback above limits.
- Test IPIP/SIT-style encapsulation to ensure the GRE/UDP-specific L4 header
  subtraction is not incorrectly applied while inner network length validation
  still runs.
- Boot or force safe mode by withholding a working DDP package. Verify the
  netdev uses `ice_netdev_safe_mode_ops`, basic open/stop/stat/MTU/MAC paths
  behave, and XDP setup fails with the safe-mode extack.
- In normal mode, verify representative callbacks from `ice_netdev_ops`:
  feature toggles, VLAN add/delete, TC setup, VF MAC/VLAN/trust/rate/stats,
  bridge get/setlink, FDB add/delete, XDP attach and `ndo_xdp_xmit`, AF_XDP
  wakeup, and hwtstamp get/set.
- Validate compile coverage with and without `CONFIG_RFS_ACCEL`, since
  `.ndo_rx_flow_steer` is conditionally present in the normal operation table.
