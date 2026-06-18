# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pf.h

## Purpose
Declares the PF-side fm10k mailbox ABI and public PF helpers used by the PF implementation, VF-facing handlers, and generic fm10k integration. It is the header contract for PF TLV message IDs, PF TLV attribute IDs, packed switch-manager ABI structs, and handler registration macros.

## Important APIs, Types, and Functions
Public helpers are `fm10k_glort_valid_pf`, `fm10k_queues_per_pool`, `fm10k_vf_queue_index`, `fm10k_iov_select_vid`, `fm10k_iov_msg_msix_pf`, `fm10k_iov_msg_lport_state_pf`, `fm10k_msg_lport_map_pf`, and `fm10k_msg_err_pf`. Message IDs in `enum fm10k_pf_tlv_msg_id_v1` cover xcast mode changes, MAC forwarding updates, LPORT map/create/delete, config, PVID updates, and flow-table operations. Attribute IDs in `enum fm10k_pf_tlv_attr_id_v1` define error, LPORT map, xcast, MAC/VLAN/config/flow payload, port, and PVID attributes. ABI structs are `fm10k_mac_update`, `fm10k_global_table_data`, and `fm10k_swapi_error`, all packed and 4-byte aligned for TLV serialization. Handler macros bind message IDs to `fm10k_tlv_attr` tables.

## Control Flow
The header has no runtime execution. It shapes PF mailbox dispatch by providing sorted message-handler macro entries consumed by `fm10k_msg_data_pf` in `fm10k_pf.c`, and it provides the attribute schemas that `fm10k_tlv_msg_parse` uses before calling PF handlers.

## State and Persistence Behavior
The packed structs are persistent firmware/switch-manager ABI payloads embedded in TLV messages. `fm10k_mac_update` carries MAC, VLAN, GLORT, flags, and add/remove action. `fm10k_swapi_error` persists switch API status and global table usage counters for MAC, nexthop, and FFU tables. The header itself stores no runtime state.

## Dependencies and Integration Points
Includes `fm10k_type.h` and `fm10k_common.h`, and depends on the TLV parser types declared through those headers. It integrates with `fm10k_pf.c` for implementation, with `fm10k_tlv.c` for parse/build behavior, and with PF/VF mailbox initialization code that installs `fm10k_info`.

## Risks
Message and attribute numeric values are ABI-sensitive. Reordering handler tables without preserving sorted ID order can break parser lookup because dispatch walks until `data->id >= msg_id`. Changing packed struct layout, endian fields, or alignment can break switch-manager communication while still compiling. The header contains future flow-table IDs not implemented in the C file, so callers must tolerate not-implemented replies.

## Test Signals
Compile coverage for all includers, TLV parsing of LPORT map/PVID/error replies, MAC update message generation, switch-manager error table decoding, unknown PF message fallback, and ABI size/alignment checks for packed structs are the main signals.
