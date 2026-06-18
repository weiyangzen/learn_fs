# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_vf.h

## Purpose
Declares the VF-side fm10k mailbox message IDs, attribute IDs, handler registration macros, VF message attribute tables, VF message handlers, and exported `fm10k_vf_info`. It is the shared protocol contract between `fm10k_vf.c`, PF-side VF handlers, and TLV dispatch setup.

## Important APIs, Types, and Functions
`enum fm10k_vf_tlv_msg_id` defines VF test, MSI-X, MAC/VLAN, and LPORT-state messages. `enum fm10k_tlv_mac_vlan_attr_id` defines VLAN, set, MAC, default-MAC, and multicast attributes. `enum fm10k_tlv_lport_state_attr_id` defines disable, xcast-mode, and ready attributes. Macros `FM10K_VF_MSG_MSIX_HANDLER`, `FM10K_VF_MSG_MAC_VLAN_HANDLER`, and `FM10K_VF_MSG_LPORT_STATE_HANDLER` build `struct fm10k_msg_data` entries. Declared handlers are `fm10k_msg_mac_vlan_vf` and `fm10k_msg_lport_state_vf`.

## Control Flow
The header has no runtime flow, but it defines how VF mailbox dispatch tables are built and how PF/VF code identify TLV attributes inside parsed result arrays.

## State and Persistence Behavior
The header stores no runtime state. Its enums are persistent PF/VF mailbox ABI values, and the declared attribute tables control validation for MAC/VLAN and LPORT-state messages.

## Dependencies and Integration Points
Includes `fm10k_type.h` and `fm10k_common.h`, and depends on the TLV handler/attribute types from the fm10k include chain. It is included by `fm10k_vf.c` and `fm10k_pf.c` because the PF handles VF-originated MSI-X and LPORT-state messages.

## Risks
Message and attribute IDs are ABI-sensitive between PF and VF. Attribute IDs must stay below `FM10K_TLV_RESULTS_MAX`. Handler macros assume the attribute tables are defined and sorted. Adding a VF message without updating both VF and PF dispatch paths can result in not-implemented mailbox replies.

## Test Signals
Compile PF and VF builds, VF mailbox dispatch table initialization, PF-side handling of MSI-X and LPORT-state requests, VF-side handling of MAC/VLAN and ready replies, unknown VF message fallback, and ABI compatibility of enum values are useful signals.
