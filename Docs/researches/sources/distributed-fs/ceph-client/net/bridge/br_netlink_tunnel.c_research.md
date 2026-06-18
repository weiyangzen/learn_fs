# sources/distributed-fs/ceph-client/net/bridge/br_netlink_tunnel.c

## Purpose
`br_netlink_tunnel.c` implements the netlink view and mutation path for per-VLAN tunnel metadata on bridge ports. It lets userspace dump VLAN-to-tunnel-ID mappings and add/delete singleton or range mappings when a port has `BR_VLAN_TUNNEL` enabled.

## Important APIs, types, and functions
- `struct vtunnel_info` comes from `br_private_tunnel.h` and carries `tunid`, `vid`, and range flags parsed from netlink.
- `br_parse_vlan_tunnel_info()` validates nested `IFLA_BRIDGE_VLAN_TUNNEL_*` attributes.
- `br_process_vlan_tunnel_info()` consumes singleton or begin/end range requests and calls `br_vlan_tunnel_info()` for each VLAN.
- `br_vlan_tunnel_info()` delegates add/delete to `nbp_vlan_tunnel_info_add()` and `nbp_vlan_tunnel_info_delete()`.
- `br_get_vlan_tunnel_info_size()` and `br_fill_vlan_tunnel_info()` count and emit dump entries, compressing consecutive VLAN/tunnel-ID runs into range begin/end records.
- `vlan_tunid_inrange()` compares consecutive tunnel IDs after converting the stored 64-bit tunnel ID to a 32-bit key.

## Control flow
Dump sizing counts usable VLAN entries with nonzero tunnel IDs under RCU. Dump filling walks the sorted VLAN list, skips inactive/context-only VLANs and entries without `tinfo.tunnel_dst`, groups consecutive VLAN IDs whose tunnel IDs also increment by one, and writes either one nested mapping or range begin/end mappings.

Mutation starts in `br_afspec()` in `br_netlink.c`, which requires a bridge port with `BR_VLAN_TUNNEL`. The parser requires both tunnel ID and VLAN ID, rejects VLAN IDs greater than or equal to `VLAN_VID_MASK`, and records optional range flags. A range begin is cached in `tinfo_last`; a range end must match the pending begin and have equal VLAN and tunnel-ID span. The loop applies each mapping and coalesces notification ranges through `__vlan_tunnel_handle_range()`.

## State and persistence
Mappings live in per-port VLAN group entries as `struct br_tunnel_info` (`tunnel_id` and RCU `metadata_dst`). The file does not allocate the metadata itself; it calls VLAN tunnel helpers. Changes are in-memory and observable through bridge VLAN netlink notifications and future dumps.

## Dependencies and integration points
This file depends on bridge VLAN filtering data structures, `dst_metadata`, rtnetlink nested attribute parsing, `br_vlan_find()`, `br_vlan_can_enter_range()`, and `br_vlan_notify()`. It is enabled only when the port-level `BR_VLAN_TUNNEL` flag is set by netlink/sysfs control paths.

## Risks and edge cases
Range requests are rejected if a new begin appears before an end, an end appears without a begin, or VLAN and tunnel-ID spans differ. Dump sizing checks `tinfo.tunnel_id`, while dump filling checks `tinfo.tunnel_dst`; any inconsistency in lower helpers could skew size estimates. Notification range coalescing depends on the current VLAN entry being found after mutation.

## Test signals
Exercise singleton add/delete, valid ranges with matching VID/VNI spans, malformed ranges, dump compression, disabling `BR_VLAN_TUNNEL` after mappings exist, and operation with inactive/global-context VLAN entries.
