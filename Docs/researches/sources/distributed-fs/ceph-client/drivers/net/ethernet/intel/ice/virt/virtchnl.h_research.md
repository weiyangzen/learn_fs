# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/virtchnl.h

## Purpose
This header defines the ICE VF virtchnl operation interface, constants, and exported helpers used when PCI SR-IOV support is enabled. It centralizes the callback table that `virtchnl.c` fills and other virtualization modules call.

## Important APIs, Types, And Functions
Important constants include `ICE_MAX_VLAN_PER_VF`, `ICE_MAX_MACADDR_PER_VF`, `ICE_FLEX_DESC_RXDID_MAX_NUM`, and the intentionally static VF-visible `ICE_VF_VSI_ID`. `struct ice_virtchnl_ops` is the key type: it contains function pointers for version/resource negotiation, reset, MAC, queue, interrupt, RSS, stats, promiscuous mode, VLAN v1/v2, FDIR, QoS, queue bandwidth/quanta, and PTP handlers. The header declares dispatcher helpers such as `ice_vc_process_vf_msg()` and response/event helpers such as `ice_vc_send_msg_to_vf()`.

## Control Flow
The header itself has no executable flow, but its operation table defines the dynamic dispatch path used in `ice_vc_process_vf_msg()`. `ice_virtchnl_set_dflt_ops()` and `ice_virtchnl_set_repr_ops()` switch a VF between normal PF-controlled behavior and representor/switchdev behavior by changing the table pointer.

## State And Persistence
No storage is allocated here. The state implications are in the function signatures: nearly every operation receives `struct ice_vf *`, and several helpers receive `struct ice_vsi *` or `struct ice_vlan *` to mutate VF/VSI state and hardware filters.

## Dependencies And Integration Points
The header includes Linux types, bit operations, Ethernet constants, the kernel AVF virtchnl ABI, and `ice_vf_lib.h`. It provides stub inline functions returning no-op or `-EOPNOTSUPP` when `CONFIG_PCI_IOV` is disabled, allowing non-SRIOV builds to compile without the virtchnl implementation.

## Risks
The operation table must stay synchronized with both default and representor implementations. Adding a callback to only one table can create null pointer dispatch or mode-specific feature loss. The static `ICE_VF_VSI_ID` avoids leaking PF topology but requires all VF requests to use this synthetic id.

## Test Signals
Build both `CONFIG_PCI_IOV=y` and disabled configurations. Runtime tests should verify that all opcode callbacks are populated in both operation tables, unsupported no-IOV stubs return stable errors, and VF-visible VSI id validation accepts only `ICE_VF_VSI_ID`.
