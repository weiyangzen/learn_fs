# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw-cmd.h

Purpose: Defines the packed DPAA2 Management Complex ABI for Data Path Switch commands. It is the private wire-format layer used by `dpsw.c` to configure switch objects, interfaces, VLANs, FDBs, ACLs, control queues, flooding, learning, and reflection.

Important APIs, types, and constants: Command version macros encode base and v2 IDs. Command IDs cover object lifecycle, IRQs, attributes, link configuration, TCI/STP, counters, VLAN membership, FDB creation and entries, FDB dump, ACL management, control-interface attributes/pools/queues, port MAC lookup, egress flood, learning mode, and reflection. Bitfield helpers `dpsw_set_field()`, `dpsw_get_field()`, and `dpsw_get_bit()` pack sub-byte fields. Packed structs include `dpsw_rsp_get_attr`, `dpsw_rsp_if_get_attr`, `dpsw_cmd_vlan_add_if`, `dpsw_cmd_fdb_unicast_op`, `dpsw_cmd_fdb_multicast_op`, `dpsw_prep_acl_entry`, and `dpsw_cmd_acl_entry`.

Control flow and state: This header has no executable flow, but its structure layout determines how `dpsw.c` populates command buffers. State represented in payloads includes object attributes, interface bitmaps, FDB IDs, VLAN IDs, ACL IDs, DMA IOVA pointers, control queue destination configuration, and event masks.

Dependencies and integration points: Includes `dpsw.h` for public constants such as `DPSW_MAX_IF` and `DPSW_MAX_DPBP`. The packed ABI integrates directly with MC firmware. `__le16`, `__le32`, and `__le64` fields require consumers to do explicit endian conversion.

Risks: The command ABI is dense and version-sensitive. Interface sets are represented by bitmaps in `__le64 if_id`; callers must cap IDs at `DPSW_MAX_IF`. MAC addresses are stored in firmware byte order expected by `dpsw.c`, which reverses bytes during command construction and decoding. ACL entry preparation requires a caller-provided DMA-able 256-byte buffer, so layout mismatches or non-zero stale padding can affect rule matching.

Test signals: Build coverage for all command structs, firmware API version checks, VLAN/FDB/ACL round trips, FDB dump into DMA memory, and packet-level validation of ACL, learning, flooding, and reflection behavior.
