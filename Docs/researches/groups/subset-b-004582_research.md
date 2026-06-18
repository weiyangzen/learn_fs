# subset-b-004582 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_devlink.c

## Purpose
This file implements devlink shared-buffer support for the Ocelot switch core. It models the switch queue-system watermarks as two devlink shared buffers: packet-buffer cells and frame references. For each shared buffer it exposes ingress and egress pools, per-port reservations, per-port traffic-class reservations, and occupancy reporting. It also normalizes hardware reset defaults by disabling over-large reservations and making the drop-precedence-0 sharing watermarks consume all non-reserved resources.

## Important APIs, types, and functions
The exported APIs are `ocelot_sb_pool_get/set()`, `ocelot_sb_port_pool_get/set()`, `ocelot_sb_tc_pool_bind_get/set()`, `ocelot_sb_occ_snapshot()`, `ocelot_sb_occ_max_clear()`, `ocelot_sb_occ_port_pool_get()`, `ocelot_sb_occ_tc_port_bind_get()`, `ocelot_devlink_sb_register()`, `ocelot_devlink_sb_unregister()`, and watermark helpers `ocelot_wm_enc()`, `ocelot_wm_dec()`, `ocelot_wm_stat()`. The internal address macros map resource classes into the 4 hardware resource planes: ingress buffer, ingress reference, egress buffer, and egress reference.

## Control flow and state
Registration publishes two devlink SBs using `devlink_sb_register()`, seeds `ocelot->pool_size[][]` from `packet_buffer_size` and `num_frame_refs`, then calls `ocelot_watermark_init()`. Pool and reservation setters optimistically write the new state, validate aggregate reservations against pool size, roll back on error, and recompute sharing watermarks. Occupancy reads go through `QSYS_RES_STAT`; max-use values are clear-on-read, so `ocelot_sb_occ_max_clear()` simply walks the relevant watermark indexes and reads them.

Persistent runtime state is split between hardware `QSYS_RES_CFG`/`QSYS_RES_STAT` registers and `ocelot->pool_size`. The code has no durable storage; all configuration is lost on device reset and rebuilt by driver initialization or devlink operations.

## Dependencies and integration points
The file depends on `struct ocelot`, regmap-backed `ocelot_read_gix()`/`ocelot_write_gix()`, chip-specific `ocelot->ops->wm_enc`, `wm_dec`, and `wm_stat`, and devlink SB callbacks wired from `ocelot_net.c`. The exported helpers are also used by SoC variants that share the Ocelot switch library.

## Risks and test signals
The critical risk is incorrect resource accounting: `ocelot_setup_sharing_watermarks()` subtracts reservations from pool sizes, so validation must run before underflow. Pool-index naming is easy to misread because `pool_index` is mapped to ingress/egress with local constants. Test signals should include devlink `sb pool set`, `sb port pool set`, `sb tc bind set`, invalid over-reservation rollback, max occupancy clear, and traffic under congestion to confirm DP0 sharing and DP1 behavior match the intended drop model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_fdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_fdma.c

## Purpose
This file provides the FDMA fast-path for Ocelot frame extraction and injection. It replaces the register-based queue-system injection/extraction path with DMA descriptor rings, NAPI polling, page recycling for RX, and ring cleanup for TX. It is enabled globally through the `ocelot_fdma_enabled` static key after a platform FDMA IRQ and descriptor rings are successfully initialized.

## Important APIs, types, and functions
The public entry points are `ocelot_fdma_init()`, `ocelot_fdma_start()`, `ocelot_fdma_deinit()`, `ocelot_fdma_inject_frame()`, `ocelot_fdma_netdev_init()`, and `ocelot_fdma_netdev_deinit()`. The ring helpers manage descriptor indexes, DMA addresses, channel activation, safe-stop polling, and DCB setup. RX is centered around `ocelot_fdma_rx_get()`, `ocelot_fdma_get_skb()`, `ocelot_fdma_receive_skb()`, and `ocelot_fdma_rx_restart()`. TX is centered around `ocelot_fdma_prepare_skb()`, `ocelot_fdma_send_skb()`, and `ocelot_fdma_tx_cleanup()`.

## Control flow and state
Initialization allocates an `ocelot_fdma` context, requests the FDMA IRQ, allocates a single coherent DCB block split into TX and RX rings, pre-populates RX buffers, and marks the last RX descriptor with a NULL LLP. `ocelot_fdma_start()` switches QS group 0 to DMA mode, enables FDMA interrupts, enables NAPI, and activates the RX channel. The IRQ acknowledges LLP/frame interrupts, disables further FDMA interrupts, and schedules NAPI. NAPI cleans completed TX descriptors, detects whether RX stopped at a NULL LLP, drains received DCBs up to budget, replenishes RX buffers, restarts RX if needed, and reenables interrupts when complete.

RX state lives in `rx_ring->next_to_clean`, `next_to_use`, `next_to_alloc`, and a partial `rx_ring->skb` for multi-fragment packets. Page halves are reused when refcount and pfmemalloc checks allow it; otherwise DMA mappings are torn down. TX state lives in `next_to_use`, `next_to_clean`, per-descriptor SKB/DMA mappings, and `xmit_lock`.

## Dependencies and integration points
FDMA depends on the Ocelot IFH helpers, QS register definitions from `ocelot_qs.h`, DSA Ocelot tag parsing, the PTP RX timestamp helper, and netdev/NAPI/DMA APIs. `ocelot_net.c` selects this path through the static key, initializes NAPI on the first port netdev, and sets headroom/tailroom to accommodate IFH and FCS.

## Risks and test signals
Key risks are ring off-by-one errors, leaked DMA mappings on partial RX/TX cleanup, stale NULL LLP handling, and `devm_free_irq()` being called with a different `dev_id` than `devm_request_irq()` used. `ocelot_fdma_inject_frame()` returns `NETDEV_TX_BUSY` internally but `ocelot_port_xmit_fdma()` currently ignores that return value. Test signals include sustained bidirectional traffic, jumbo/fragmented frames, PTP RX/TX traffic through FDMA, allocation failure handling, queue stop/wake behavior under TX ring pressure, module unload, and FDMA error interrupt logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_fdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_fdma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_fdma.h

## Purpose
This header defines the FDMA register offsets, descriptor bit fields, ring sizing, buffer sizing, static key, data structures, and exported function prototypes used by `ocelot_fdma.c` and the Ocelot netdev glue. It is the local contract for enabling DMA-based extraction/injection instead of the normal CPU port register path.

## Important APIs, types, and functions
The DCB status macros encode and decode hardware descriptor state: block offset, processed-done, abort, EOF, SOF, and block length. Register macros cover channel LLP registers, safe/activate/disable/forcedis controls, error/status registers, and interrupt enable/status registers. `MSCC_FDMA_INJ_CHAN` is channel 2 and `MSCC_FDMA_XTR_CHAN` is channel 0. Ring sizes are fixed at 512 RX DCBs and 128 TX DCBs, with half-page RX buffers and aligned SKB-frag accounting.

The important structs are `ocelot_fdma_dcb`, `ocelot_fdma_tx_buf`, `ocelot_fdma_tx_ring`, `ocelot_fdma_rx_buf`, `ocelot_fdma_rx_ring`, and `ocelot_fdma`. These capture coherent descriptors, DMA addresses, SKB/page ownership, ring cursors, NAPI context, IRQ number, and the Ocelot back-pointer.

## Control flow and state
The header itself has no executable control flow, but its state model is precise: TX descriptors own SKBs until TX cleanup unmaps and consumes them; RX descriptors own page halves until packet assembly either reuses the page or unmaps it. The `ocelot_fdma_enabled` static key allows `ocelot_net.c` to avoid a runtime branch cost when FDMA is unavailable.

## Dependencies and integration points
It includes `ocelot.h`, uses Linux SKB, DMA unmap metadata, NAPI, and platform-device types through included headers. `ocelot_net.c` consumes `ocelot_fdma_inject_frame()` and per-netdev init/deinit. `ocelot_fdma.c` consumes all register and ring constants. The QS register definitions are separate in `ocelot_qs.h`.

## Risks and test signals
The most important invariants are descriptor alignment, matching ring sizes to allocated coherent memory, leaving one free ring slot to disambiguate full and empty, and keeping `OCELOT_FDMA_RXB_SIZE` compatible with IFH, Ethernet payload, FCS, and SKB shared-info placement. Compile-time coverage catches missing prototypes, but functional tests need DMA traffic across RX/TX, cache-sync correctness on reused pages, and validation that static-key switching does not route frames to FDMA before rings and NAPI are ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_fdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_flower.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_flower.c

## Purpose
This file translates Linux tc flower rules into Ocelot VCAP and optional PSFP hardware filters. It implements the chain-number UAPI for IS1, IS2, ES0, and PSFP, validates allowed goto topology, parses supported actions and keys, manages dummy rules used as chain topology anchors, and exposes replace/destroy/stats operations used by the netdev tc callbacks.

## Important APIs, types, and functions
Exported APIs are `ocelot_cls_flower_replace()`, `ocelot_cls_flower_destroy()`, and `ocelot_cls_flower_stats()`. Chain mapping is handled by `ocelot_chain_to_block()`, `ocelot_chain_to_lookup()`, `ocelot_chain_to_pag()`, and `ocelot_is_goto_target_valid()`. Action parsing lives in `ocelot_flower_parse_action()`, with helpers for ingress VLAN modification, egress VLAN modification, redirect/mirror port resolution, and ES0 VLAN delta patching. Key parsing lives in `ocelot_flower_parse_key()` and supports VLAN, Ethernet addresses, IPv4 protocol/address, L4 ports, and egress `indev` metadata for ES0.

## Control flow and state
Replace first rejects non-zero chains that are not reached by an existing dummy or PAG rule, then maps the chain to a hardware block. If the cookie already exists, ingress filters are shared by OR-ing the port into `ingress_port_mask`; ES0 shared filters are rejected. New filters are allocated, action-parsed first, then key-parsed unless the target is PSFP. Dummy filters are linked into `ocelot->dummy_rules` and not programmed into hardware. VCAP filters are programmed through `ocelot_vcap_filter_add/replace/del`; PSFP filters are delegated to optional `ocelot->ops->psfp_*` hooks.

State is stored in allocated `struct ocelot_vcap_filter` objects, VCAP block rule lists, `dummy_rules`, ingress port masks, per-filter action fields, and hardware VCAP entries. There is no persistent storage beyond driver lifetime.

## Dependencies and integration points
The file depends on tc flower dissector/action APIs, `ocelot_police.h`, `ocelot_vcap.h`, and SoC-specific PSFP hooks. It is called from `ocelot_net.c` only for ingress flower offload in this driver, though the parser has ES0 egress support. It shares policing validation with matchall policing and VCAP policer index allocation with the Ocelot core.

## Risks and test signals
Risks include chain UAPI regressions, silently accepting topology that hardware cannot execute, action ordering violations around GOTO, and key/action combinations that do not match VCAP key types. IPv6 address matching is explicitly unsupported despite IPv6 trap helpers elsewhere. Test signals should cover valid and invalid chain skeletons, shared ingress rule cookies across ports, ES0 VLAN rewrite requiring full VLAN key mask, policing index bounds, mirror/redirect to Ocelot and foreign devices with `skip_sw`, PSFP unsupported hardware paths, and stats updates for VCAP and PSFP filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_flower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_io.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_io.c

## Purpose
This file centralizes low-level register access for the Ocelot switch library. It maps logical `enum ocelot_reg` values to regmap targets and offsets, provides indexed read/write/rmw/bulk-read helpers, creates per-port target accessors, initializes regmap fields, and builds MMIO regmaps from platform resources.

## Important APIs, types, and functions
Exported APIs are `__ocelot_bulk_read_ix()`, `__ocelot_read_ix()`, `__ocelot_write_ix()`, `__ocelot_rmw_ix()`, `ocelot_port_readl()`, `ocelot_port_writel()`, `ocelot_port_rmwl()`, `ocelot_regfields_init()`, and `ocelot_regmap_init()`. Non-exported target-index helpers `__ocelot_target_read_ix()` and `__ocelot_target_write_ix()` directly address a known target and register index.

## Control flow and state
For logical register helpers, the function calls `ocelot_reg_to_target_addr()` to split the logical register into a target and base address, warns if no target was resolved, then calls the appropriate regmap operation at `addr + offset`. Port helpers derive the target from the encoded register and use the port-specific regmap stored in `struct ocelot_port`. `ocelot_regfields_init()` iterates all known `REGFIELD_MAX` descriptors, translates their register addresses through `ocelot->map`, and stores devm-managed `regmap_field` objects in `ocelot->regfields[]`. `ocelot_regmap_init()` maps an MMIO resource and initializes a 32-bit regmap with 4-byte stride.

State is mostly indirect: `ocelot->targets[]`, `ocelot->map[][]`, and `ocelot->regfields[]` are populated or consumed. The static `ocelot_regmap_config` has its `name` updated from the resource before each regmap initialization, so it is shared mutable configuration during probe.

## Dependencies and integration points
All higher-level files in this group depend on these helpers for hardware access, including devlink watermarks, policing, stats, PTP, MAC Merge, netdev VLAN mode, and FDMA through its own regmap target. The file depends on Linux regmap, devm MMIO mapping, and Ocelot target/register encoding.

## Risks and test signals
The helpers rely on correct target encoding and register maps supplied by the SoC driver; a bad map can redirect writes globally. `WARN_ON(!target)` does not prevent a regmap access, so invalid register descriptions can still cause faults. `ocelot_port_rmwl()` is read-modify-write rather than `regmap_update_bits()`, so concurrent writers need external serialization. Test signals include probe on every supported Ocelot variant, regfield allocation failure paths, stats bulk reads, per-port register accesses, and sparse/debug warnings for invalid logical register definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_mm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_mm.c

## Purpose
This file implements MAC Merge layer and IEEE 802.3 frame preemption support for TSN-capable Ocelot-family switches. It exposes ethtool MAC Merge set/get behavior, tracks verification and TX-active status, updates active preemptible traffic classes, and handles MM status interrupts.

## Important APIs, types, and functions
The important public functions are `ocelot_port_set_mm()`, `ocelot_port_get_mm()`, `ocelot_mm_irq()`, `ocelot_mm_init()`, `ocelot_port_change_fp()`, and `ocelot_port_update_active_preemptible_tcs()`. Internal helpers convert hardware verify state into ethtool status and human-readable debug strings. State is kept in `struct ocelot_mm_state` per port, allocated in `ocelot->mm`.

## Control flow and state
Initialization allocates per-port MM state only when `ocelot->mm_supported` is true and seeds `verify_status` from `DEV_MM_STATUS`. `ocelot_port_set_mm()` validates minimum fragment size, programs RX/TX enable bits, verification timing/disable bits, and QSYS additional fragment size under `fwd_domain_lock`. When disabling TX, it explicitly processes any pending status interrupt while `mm->tx_enabled` is still true to avoid an IRQ storm. `ocelot_mm_irq()` locks the forwarding domain and scans every port, updating verification state, TX-active state, active preemptible TCs, and sticky error acknowledgments.

Active preemptible TCs are not simply the configured mask. They are committed only when MM TX is active and, on QSGMII, only at gigabit speed. The update calls `tas_guard_bands_update()` because preemptible priorities affect guard bands, cut-through forwarding, and oversize drop logic.

## Dependencies and integration points
This file depends on ethtool MM APIs, DEV and QSYS register definitions, phylink-maintained port speed/phy mode, and chip ops `tas_guard_bands_update()`. Stats for MM and PMAC counters are reported by `ocelot_stats.c`; netdev ethtool hooks are supplied by the wider Ocelot integration.

## Risks and test signals
Risks include stale `tx_active` state if interrupts are missed, QSGMII speed-specific hangs if preemption is enabled below 1 Gbps, and inconsistent guard-band/cut-through state if callers modify preemptible TCs without holding `fwd_domain_lock`. Test signals include `ethtool --set-mm`/`--show-mm`, verify enable/disable, link speed transitions, QSGMII non-gigabit operation, IRQ sticky bit acknowledgment, PMAC traffic, and MM statistics matching expected preempted frame behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_mrp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_mrp.c

## Purpose
This file implements switchdev MRP object handling for Ocelot. It records per-port MRP ring membership, traps MRP control/test frames to the CPU when needed, redirects MRP test frames between partner ring ports for MRC operation, and installs locked blackhole MAC-table entries for standard MRP multicast addresses.

## Important APIs, types, and functions
Public APIs are `ocelot_mrp_add()`, `ocelot_mrp_del()`, `ocelot_mrp_add_ring_role()`, and `ocelot_mrp_del_ring_role()`. Internal helpers locate the partner port for a ring, add/delete VCAP redirect filters, build trap keys, and add/delete locked MRP multicast MAC entries. VCAP cookies are derived from `OCELOT_VCAP_IS2_MRP_REDIRECT()` and `OCELOT_VCAP_IS2_MRP_TRAP()`.

## Control flow and state
Adding an MRP object records `mrp_ring_id` on a port only if the switchdev object references that netdev as primary or secondary ring port. Deleting clears the ring ID when it matches. Adding a ring role first validates either MRC role or software backup support, then blackholes standard MRP multicast addresses. Non-MRC roles use a CPU trap. MRC role finds the partner port with the same ring ID, installs an IS2 redirect rule from source port to partner port for test frames, then installs the trap. If trap installation fails, the redirect rule is rolled back. Deleting ring role removes trap and redirect; when no port retains any ring ID, the blackhole MAC entries are removed.

State persists in `ocelot_port->mrp_ring_id`, hardware MAC table entries, and VCAP IS2 filters. There is no durable state across driver reload.

## Dependencies and integration points
MRP events enter through switchdev object handlers in `ocelot_net.c`. The file depends on bridge MRP UAPI, Ocelot VCAP helpers, `ocelot_trap_add/del()`, and MAC table learn/forget helpers. It also assumes the standalone PVID for locked multicast entries.

## Risks and test signals
Risks include redirect rule leaks when trap deletion fails, blackhole MAC entries being global to all rings, and partner-port lookup ambiguity if more than two ports share a ring ID. The role validation deliberately rejects unsupported ring roles unless software backup is indicated. Test signals should include MRC ring formation with two ports, non-MRC trap-only behavior, add/delete ordering, failure rollback of redirect on trap-add failure, multiple rings, and packet tests confirming MRP frames are trapped or redirected as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_mrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_net.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_net.c

## Purpose
This is the main Linux netdev, switchdev, tc, devlink, phylink, and port-probe glue for the standalone Ocelot switch driver. It translates kernel networking operations into common Ocelot switch-library calls, wires devlink shared-buffer callbacks, manages tc matchall/flower offloads, handles bridge and LAG notifier events, and creates/releases per-port net devices.

## Important APIs, types, and functions
External entry points include `ocelot_port_devlink_init()`, `ocelot_port_devlink_teardown()`, `ocelot_setup_tc_cls_flower()`, `ocelot_port_to_netdev()`, `ocelot_netdev_to_port()`, `ocelot_probe_port()`, and `ocelot_release_port()`. It exports notifier blocks `ocelot_netdevice_nb`, `ocelot_switchdev_nb`, and `ocelot_switchdev_blocking_nb`, plus `ocelot_devlink_ops`. Netdev ops cover open/stop/xmit/MTU/RX mode/MAC/FDB/VLAN/features/tc/ioctl/hwtstamp. Ettool ops delegate stats, link settings, timestamp info, and timestamp stats.

## Control flow and state
Port probe allocates an Ethernet netdev, embeds `struct ocelot_port_private`, records `ocelot->ports[port]`, assigns ops/features, chooses or derives the MAC address, learns it to the CPU PGID, initializes the hardware port, creates phylink, optionally initializes FDMA NAPI state, links the devlink port, and registers the netdev. Release reverses netdev registration, FDMA netdev hookup, phylink connection, and netdev allocation.

Transmit selects FDMA when the static key is enabled, otherwise uses injection group 0. Both paths call `ocelot_xmit_timestamp()` to queue or configure PTP timestamping and set the IFH rewrite operation. TC block binding registers ingress or egress callbacks. Matchall supports one action: ingress police or mirred to another Ocelot port; flower delegates to `ocelot_flower.c`. Feature changes reject disabling HW TC while offloads are active. Switchdev bridge/LAG paths offload bridge ports, sync STP/ageing/VLAN filtering/flags, allocate bridge numbers, handle LAG bridge inheritance, and process lower-state active changes.

State is distributed across `priv->tc` offload IDs/count, `ocelot_port` bridge/LAG fields, bridge-number bitmap, multicast workqueue jobs, learned MAC/FDB/VLAN/MDB hardware entries, and phylink state.

## Dependencies and integration points
This file integrates all other files in this group: devlink SB operations from `ocelot_devlink.c`, policing from `ocelot_police.c`, flower from `ocelot_flower.c`, FDMA from `ocelot_fdma.c`, PTP from `ocelot_ptp.c`, stats from `ocelot_stats.c`, MRP from `ocelot_mrp.c`, and low-level Ocelot library functions. It also depends on Linux bridge, switchdev, flow offload, phylink, PHY, VLAN, FDB, and notifier APIs.

## Risks and test signals
Risks include notifier ordering around bridge/LAG leave, inconsistent offload counters preventing feature toggles, multicast workqueue actions racing teardown, FDMA xmit ignoring the `NETDEV_TX_BUSY` return from `ocelot_fdma_inject_frame()`, and tc shared-block restrictions applying only to matchall. Test signals should cover port probe/remove failure unwinding, bridge join/leave, VLAN filtering and FDB dump, LAG join/leave and active-member changes, tc police/mirred/flower offloads, PTP hwtstamp get/set and TX, FDMA and non-FDMA transmit, and ethtool statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_police.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_police.c

## Purpose
This file configures Ocelot QoS policers and validates tc police actions that can be offloaded. It translates line/data/frame rate policer settings into ANA policer register fields, supports port policer add/delete, and provides common validation used by both matchall and flower offload paths.

## Important APIs, types, and functions
Public APIs are `qos_policer_conf_set()`, `ocelot_policer_validate()`, `ocelot_port_policer_add()`, and `ocelot_port_policer_del()`. The key constants define hardware frame modes, port and queue policer index bases, and default policer order. The input type is `struct qos_policer_conf` from `ocelot_police.h`, and port policer wrappers consume `struct ocelot_policer`.

## Control flow and state
`qos_policer_conf_set()` normalizes the requested mode into hardware units. Data and line rate use 33 1/3 kbps rate units and 4096-byte burst units; frame rate has high and low modes with different frame units. Dual leaky bucket mode optionally enables CIR, coupling, and discard-state programming. Disabled policers are represented by maximum PIR and zero burst. After bounds checks for PIR/CIR/PBS/CBS, the function writes mode, PIR config/state, and CIR config/state registers for the selected policer index. Port add builds a data-rate PIR-only policer from kbps/burst, programs `POL_IX_PORT + port`, and enables ANA port policing with a fixed order. Delete programs disabled mode and clears port policer enable while preserving the order field.

State lives in ANA policer registers and ANA port policer config. There is no software cache apart from tc cookies in `ocelot_net.c`.

## Dependencies and integration points
The file depends on Ocelot ANA register macros, Linux flow action structures, and netlink extack reporting. Matchall policing in `ocelot_net.c` and flower policing in `ocelot_flower.c` both call `ocelot_policer_validate()`. Flower additionally maps tc `hw_index` into VCAP policer ranges and stores rate/burst in filter action state.

## Risks and test signals
Risks include unit conversion truncation/overflow, unsupported tc actions being accidentally accepted, and hardware burst limits rejecting large user values. `ocelot_policer_validate()` rejects peakrate, avrate, overhead, packets-per-second, non-drop exceed actions, and non-pipe/non-accept conform actions. Test signals include tc matchall police add/delete, flower police with `hw_index`, invalid conform/exceed actions, zero-rate discard behavior, high and low frame-rate modes through direct helper coverage, and register inspection for policer order and enable bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_police.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_police.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_police.h

## Purpose
This header defines the public policing configuration contract for the Ocelot driver. It describes supported rate measurement modes, the software representation of a hardware policer, and the functions used by tc and port-policing code to validate and program policers.

## Important APIs, types, and functions
`enum mscc_qos_rate_mode` enumerates disabled, line-rate, data-rate, and frame-rate operation. `struct qos_policer_conf` carries dual-leaky-bucket configuration, coupling, CIR/CBS, PIR/PBS, and IPG size. The prototypes are `qos_policer_conf_set()` and `ocelot_policer_validate()`. Port-level add/delete wrappers are implemented in `ocelot_police.c` but are likely declared elsewhere through common Ocelot headers.

## Control flow and state
The header has no runtime control flow. Its state model mirrors the hardware policer: line/data/frame mode determines units, DLB enables CIR in addition to PIR, coupling can add CIR into PIR, and zero rate plus zero burst means discard in the implementation. `ipg` is meaningful only for line-rate mode.

## Dependencies and integration points
It includes `ocelot.h` and `<net/flow_offload.h>`, which makes it available to both driver-internal register programming and tc action validation. `ocelot_flower.c` includes this header to validate flower police actions, and `ocelot_net.c` includes it for matchall policing.

## Risks and test signals
The main risk is semantic mismatch between units in this structure and user-visible tc units. Callers must pass PIR/CIR in kbps or frames-per-second according to mode and bursts in bytes or frames according to mode. Header-level test signals are compile coverage across files that include it, plus functional tests that exercise every enum mode through `qos_policer_conf_set()` to catch assumptions that only data-rate mode exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_police.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_ptp.c

## Purpose
This file implements the Ocelot PTP hardware clock, timestamping configuration, PTP trap rules, TX timestamp queueing/completion, RX/TX hwtstamp reporting, and PHC registration. It bridges Linux PTP clock APIs and hwtstamp ioctls to Ocelot PTP, SYS, ANA, and VCAP hardware.

## Important APIs, types, and functions
PHC callbacks include `ocelot_ptp_gettime64()`, `ocelot_ptp_settime64()`, `ocelot_ptp_adjtime()`, `ocelot_ptp_adjfine()`, `ocelot_ptp_verify()`, and `ocelot_ptp_enable()`. Hwtstamp APIs are `ocelot_hwstamp_get()`, `ocelot_hwstamp_set()`, and `ocelot_get_ts_info()`. TX timestamp flow uses `ocelot_port_txtstamp_request()`, `ocelot_get_txtstamp()`, queue/dequeue helpers, and `ocelot_get_hwtimestamp()`. Initialization is `ocelot_init_timestamp()`/`ocelot_deinit_timestamp()`.

## Control flow and state
Clock get/set/adjust operations serialize on `ptp_clock_lock` and use the TOD access pin. Small `adjtime` deltas use hardware delta action; large deltas fall back to read-modify-set. `adjfine` computes adjustment interval in picoseconds or nanoseconds and disables adjustment if the interval cannot fit. Perout requests map PTP pins, validate phase and duty cycle, and program waveform high/low periods or PPS sync.

RX timestamping is enabled by adding/removing VCAP traps for L2 PTP EtherType and UDP IPv4/IPv6 event/general ports. `ocelot_hwstamp_set()` translates hwtstamp filters to trap sets and stores `ocelot_port->ptp_cmd`. TX timestamping classifies outgoing PTP packets. One-step Sync stores a rewrite command and increments unconfirmed stats. Two-step timestamping clones the SKB, assigns a timestamp ID under `ts_id_lock`, queues the clone, and marks TX in progress. `ocelot_get_txtstamp()` drains hardware timestamp FIFO entries, matches by TX port, timestamp ID, and PTP sequence ID, completes SKB timestamps, and accounts stale or unmatched entries.

State includes `ocelot->ptp_clock`, pin descriptors, `ocelot_port->trap_proto`, `ptp_cmd`, per-port `tx_skbs`, global `ptp_skbs_in_flight`, and per-port timestamp stats.

## Dependencies and integration points
The file depends on Linux PTP, hwtstamp, SKB timestamping, PTP classification, Ocelot VCAP trap helpers, and Ocelot IFH rewrite commands. `ocelot_net.c` calls hwtstamp get/set and TX timestamp request paths; FDMA RX calls the RX timestamp helper through the common Ocelot tag flow; stats are exposed by `ocelot_stats.c`.

## Risks and test signals
Risks include timestamp-ID exhaustion, stale queued SKBs, sequence-ID mismatch, FIFO overflow, one-step fallback behavior, trap rollback on partial failure, and PHC adjustment edge cases for negative nanoseconds. Test signals include `phc2sys`/`ptp4l`, `ethtool -T`, hwtstamp filter changes, L2 and L4 PTP RX traps, two-step TX completion, one-step Sync rewrite, stale TX timeout accounting, perout/PPS generation, and PHC adjtime/adjfine under concurrent timestamp traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_qs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_qs.h

## Purpose
This header defines Queue System extraction and injection register fields used by the Ocelot CPU port and FDMA paths. It describes extraction status tokens, extraction/injection group configuration, injection control, injection status, and injection error bits.

## Important APIs, types, and functions
The extraction status macros define EOF variants, pruned, abort, escape, not-ready, and valid-byte decoding. Register macros cover `QS_XTR_GRP_CFG`, `QS_XTR_RD`, `QS_XTR_FRM_PRUNING`, `QS_XTR_CFG`, `QS_INJ_GRP_CFG`, `QS_INJ_WR`, `QS_INJ_CTRL`, `QS_INJ_STATUS`, and `QS_INJ_ERR`. Field macros encode mode, status-word position, byte swap, watermarks, gap size, abort, EOF, SOF, valid bytes, FIFO-ready, in-progress, and sticky error bits.

## Control flow and state
The header has no executable control flow. Runtime state is represented in QS hardware registers programmed by other files. In this subset, `ocelot_fdma_start()` uses `QS_INJ_GRP_CFG_MODE(2)`, `QS_INJ_CTRL_GAP_SIZE(0)`, and `QS_XTR_GRP_CFG_MODE(2)` to switch group 0 into DMA mode for FDMA extraction/injection.

## Dependencies and integration points
It is consumed by FDMA and by the wider Ocelot queue-system CPU injection/extraction code outside this work item. The macros depend on Linux `BIT()` and `GENMASK()` definitions through transitive includes. They must stay consistent with the switch register map in SoC-specific headers.

## Risks and test signals
The explicit TODO notes big-endian handling risk for extraction words. Incorrect mode or byte-swap definitions would break CPU-port traffic globally. Test signals include FDMA and non-FDMA RX/TX, CPU-injected frames with all valid-byte endings, extraction abort/pruned handling, and endian coverage on architectures where byte ordering differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_qs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_rew.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_rew.h

## Purpose
This header defines register field macros for the Ocelot Rewriter block. The rewriter controls per-port VLAN insertion/rewriting, tag behavior, port configuration, DSCP and PCP/DEI mappings, PTP rewrite settings, redundancy tag settings, sticky error bits, and PPT register stride.

## Important APIs, types, and functions
Important groups include `REW_PORT_VLAN_CFG_*` for default port TPID/PCP/DEI/VID, `REW_TAG_CFG_*` for tag selection and PCP/DEI behavior, `REW_PORT_CFG_*` for ES0 enable and FCS/flush/age controls, `REW_PCP_DEI_QOS_MAP_CFG_*` for PCP/DEI to QoS mapping, `REW_PTP_CFG_*` for PTP one-step/two-step/UDP behavior, `REW_RED_TAG_CFG_*` for redundancy tags, and `REW_REW_STICKY_ES0_TAGB_PUSH_FAILED` for sticky failure reporting.

## Control flow and state
The header has no runtime control flow. It defines how other code encodes and masks rewriter state into hardware registers. In this subset, flower ES0 actions populate VCAP action fields for VLAN rewrite/push behavior, while PTP code chooses IFH rewrite operations; the actual rewriter register programming is performed by common Ocelot code outside this file.

## Dependencies and integration points
These macros integrate with the Ocelot common rewriter setup, VLAN handling, ES0 VCAP egress rewriting, PTP timestamp correction/origin rewrite behavior, and QoS mapping code. They rely on the hardware register layout matching the map used by `ocelot_io.c`.

## Risks and test signals
Risks include field-width mismatch, wrong tag TPID selection, and sticky ES0 push failures being ignored by higher layers. Test signals should include VLAN push/pop/modify offloads, ES0 enable/disable paths, PTP one-step and two-step TX, PCP/DEI classification, FCS update behavior on CPU and non-CPU frames, and hardware sticky-bit checks after invalid tag actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_rew.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_stats.c

## Purpose
This file implements Ocelot statistics collection and ethtool/netdev statistics reporting. It maps hardware SYS counters into a stable `enum ocelot_stat`, periodically reads 32-bit hardware counters, extends them into software 64-bit counters, and serves legacy ethtool strings, rtnl stats64, ethtool standard MAC/PHY/RMON/pause/MM stats, and timestamp stats.

## Important APIs, types, and functions
Public APIs include `ocelot_stats_init()`, `ocelot_stats_deinit()`, `ocelot_get_strings()`, `ocelot_get_sset_count()`, `ocelot_get_ethtool_stats()`, `ocelot_port_get_pause_stats()`, `ocelot_port_get_mm_stats()`, `ocelot_port_get_rmon_stats()`, `ocelot_port_get_eth_ctrl_stats()`, `ocelot_port_get_eth_mac_stats()`, `ocelot_port_get_eth_phy_stats()`, `ocelot_port_get_ts_stats()`, and `ocelot_port_get_stats64()`. The core internal helpers are `ocelot_prepare_stats_regions()`, `ocelot_port_update_stats()`, `ocelot_port_transfer_stats()`, `ocelot_check_stats_work()`, and `ocelot_port_stats_run()`.

## Control flow and state
Initialization allocates `ocelot->stats` as `num_phys_ports * OCELOT_NUM_STATS`, optionally allocates per-port timestamp stats when PTP is enabled, creates a single-thread workqueue, initializes locks, builds contiguous counter regions for efficient bulk reads, and schedules delayed polling. The worker locks `stat_view_lock`, switches `SYS_STAT_CFG` to each port, bulk-reads all regions, transfers counters under `stats_lock`, calls optional chip `update_stats()`, and reschedules itself. On-demand ethtool reads use the same update-transfer-callback pattern for a single port.

Hardware counters are 32-bit. `ocelot_port_transfer_stats()` detects wrap by comparing the new low 32 bits with the previous low 32 bits and increments the high half. MM-supported devices use an expanded layout including PMAC and MAC Merge counters; non-MM devices expose only common counters. Timestamp stats use `u64_stats_sync` rather than the main stats lock.

## Dependencies and integration points
This file depends on Ocelot SYS counter register maps, `ocelot_io.c` bulk reads, ethtool netlink standard stats structures, workqueues, spinlocks, and mutexes. `ocelot_net.c` exposes these through netdev and ethtool operations. `ocelot_ptp.c` updates timestamp stats, and `ocelot_mm.c` enables meaningful MM/PMAC stats on supported hardware.

## Risks and test signals
Risks include enum/register order drift breaking contiguous bulk regions, missed wraps if polling is too slow for 32-bit counters, lock ordering mistakes between `stat_view_lock` and `stats_lock`, and aggregate stats depending on the backing netdev. The code warns if register addresses are not increasing. Test signals include ethtool `-S`, `ip -s link`, ethtool standard stats by EMAC/PMAC/aggregate source, wrap simulation or high-rate traffic, PTP timestamp stats, MM stats on supported hardware, workqueue teardown, and probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_stats.c -->
