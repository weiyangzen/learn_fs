# sources/distributed-fs/ceph-client/include/linux/avf/virtchnl.h

## Purpose
Defines Intel AVF/IAVF virtual channel ABI used by a virtual function (VF) driver to communicate with a physical function (PF) over the admin queue. The header is a wire contract: opcode numbers, status codes, capability flags, fixed-size structures, variable-length payload sizing helpers, and inline validation must remain layout-stable across VF/PF versions.

## Important APIs, types, and functions
- `enum virtchnl_status_code`, `enum virtchnl_ops`, `struct virtchnl_version_info`, and `VIRTCHNL_VERSION_*` describe the base protocol and compatibility gates.
- Resource and queue setup types include `virtchnl_vf_resource`, `virtchnl_vsi_resource`, `virtchnl_txq_info`, `virtchnl_rxq_info`, `virtchnl_vsi_queue_config_info`, `virtchnl_irq_map_info`, `virtchnl_queue_select`, and `virtchnl_vf_res_request`.
- Feature families cover MAC/VLAN filters, RSS, cloud filters, RDMA interrupt mapping, FDIR, PTP, QoS, queue bandwidth, and quanta.
- `VIRTCHNL_CHECK_STRUCT_LEN` and `VIRTCHNL_CHECK_UNION_LEN` intentionally fail compilation if ABI layouts drift.
- `virtchnl_struct_size()` handles legacy flexible-array sizing for selected message structs.
- `virtchnl_vc_validate_vf_msg()` is the only executable logic: it maps an opcode to the expected payload length and rejects malformed VF messages.

## Control flow and state
The documented VF initialization sequence is version negotiation, reset, resource discovery, queue and interrupt configuration, queue enablement, optional filter/offload setup, then traffic. The reset operation is asynchronous and has no PF response; the VF polls hardware reset state instead. `virtchnl_vc_validate_vf_msg()` switches on the opcode, computes a fixed or flexible payload length, performs selected semantic checks such as nonzero element counts and nonzero quanta size, and returns `VIRTCHNL_STATUS_ERR_OPCODE_MISMATCH` or `VIRTCHNL_STATUS_ERR_PARAM` for invalid input.

## State and persistence behavior
The header itself persists no state, but it defines state exchanged between PF and VF: VF capabilities, queue resources, VLAN/offload settings, RSS keys/LUTs, flow IDs, PTP capability grants, QoS limits, and reset states. Flexible arrays are protocol payloads and must be sized from count fields. Reserved fields are compatibility state and should be zeroed and validated by participants.

## Dependencies and integration points
Depends on kernel bit macros, overflow/`struct_size()` helpers, and Ethernet address constants. Integrated by Intel virtual NIC PF/VF drivers and RDMA clients that route opaque RDMA messages. The `REQ` style validation is PF-side defensive code for messages arriving from a VF and should align with firmware admin-queue transport constraints.

## Risks
ABI drift is the dominant risk: changing enum values, structure padding, or legacy size constants can break PF/VF interoperability. Flexible-array length calculations are sensitive to untrusted count fields. Several comments mark deprecated or legacy fields that must still be understood. PTP and VLAN v2 negotiation require cross-checking requested capability bits against PF-granted bits.

## Test signals
Compile-time layout assertions should remain green on all target architectures. Unit or driver tests should feed `virtchnl_vc_validate_vf_msg()` valid and invalid payloads for fixed-size, zero-length, flexible-array, and reserved opcodes. Integration tests should cover VF startup, reset polling, queue setup, VLAN v1/v2 negotiation, RSS/FDIR programming, and capability downgrade paths with older PFs.
