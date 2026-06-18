# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_fcoe.c

## Purpose

`cxgb4_fcoe.c` implements the Chelsio `cxgb4` FCoE offload control helpers when `CONFIG_CHELSIO_T4_FCOE` is enabled. It validates supported FCoE SOF/EOF frame markers and toggles netdev feature bits for FCoE CRC offload and FCoE MTU handling.

The implementation is small but sits on sensitive boundaries: it changes advertised netdev capabilities and validates Fibre Channel over Ethernet framing before offload.

## Important APIs And Functions

- `cxgb_fcoe_sof_eof_supported(struct adapter *adap, struct sk_buff *skb)` reads the FCoE header at `skb_network_header(skb)`, accepts only `FC_SOF_I3` or `FC_SOF_N3`, copies the EOF byte from the final four bytes of the skb, and accepts only `FC_EOF_N` or `FC_EOF_T`.
- `cxgb_fcoe_enable(struct net_device *netdev)` enables FCoE offload features for a port. It rejects T4 chips and adapters that have not completed full initialization, sets `NETIF_F_FCOE_CRC` in `features` and `vlan_features`, enables `netdev->fcoe_mtu`, calls `netdev_features_change()`, and marks `pi->fcoe.flags` with `CXGB_FCOE_ENABLED`.
- `cxgb_fcoe_disable(struct net_device *netdev)` requires the enabled flag, clears the flag, removes FCoE CRC from `features` and `vlan_features`, disables `fcoe_mtu`, and calls `netdev_features_change()`.

## Control Flow

The enable path starts from a netdev, recovers `struct port_info` and `struct adapter`, rejects unsupported chips with `is_t4(adap->params.chip)`, rejects incomplete adapter initialization, logs enablement, updates netdev feature masks, notifies the networking core, and records the runtime enabled bit.

The disable path recovers the same objects, rejects disable when the feature was not enabled, logs disablement, clears the runtime flag, removes feature bits, disables FCoE MTU support, and notifies the networking core.

The SOF/EOF validation path is used on an skb containing an FCoE frame. It reads the SOF byte directly from the FCoE header, then copies one byte from `skb->len - 4` to inspect EOF. Unsupported markers produce device error logs and return `false`; accepted markers return `true`.

## State And Persistence

The only driver-owned persistent state is `pi->fcoe.flags`, specifically `CXGB_FCOE_ENABLED`. The netdev state also persists while enabled:

- `netdev->features` includes `NETIF_F_FCOE_CRC`.
- `netdev->vlan_features` includes `NETIF_F_FCOE_CRC`.
- `netdev->fcoe_mtu` is set.

There is no on-disk persistence. State is runtime-only and tied to the netdev/adapter lifetime.

## Dependencies And Integration Points

- Compiled only under `CONFIG_CHELSIO_T4_FCOE`.
- Includes `<scsi/fc/fc_fs.h>` for Fibre Channel SOF/EOF constants and `<scsi/libfcoe.h>` for FCoE definitions.
- Includes `cxgb4.h` for adapter, port, feature flags, chip helpers, and netdev private data.
- Integrates with Linux netdev feature negotiation via `netdev_features_change()`.
- Depends on `CXGB4_FULL_INIT_DONE` being set before enabling offload.

## Risks And Edge Cases

- `cxgb_fcoe_sof_eof_supported()` assumes the skb is long enough and laid out such that `skb_network_header()` points to an FCoE header and `skb->len - 4` contains EOF. Callers must ensure frame validity before invoking it.
- Enable rejects T4 chips but permits later chips only after full init; error reporting is simply `-EINVAL`, so callers need context to distinguish unsupported chip from initialization state.
- Directly mutating `netdev->features` and `vlan_features` must remain synchronized with the driver's feature-fixup paths elsewhere in the driver.
- Disable returns `-EINVAL` if not currently enabled, which makes repeated disable non-idempotent.

## Test Signals

- Build coverage with `CONFIG_CHELSIO_T4_FCOE=y` and disabled.
- Enable tests on T4 and non-T4 chips, before and after full initialization.
- Feature verification after enable/disable through `ethtool -k` or direct netdev inspection for FCoE CRC and VLAN feature changes.
- skb validation tests for accepted SOF/EOF pairs, unsupported SOF, unsupported EOF, and too-short/malformed skb handling by callers.
- Repeated enable/disable sequencing tests to confirm flag and netdev feature state stay consistent.
