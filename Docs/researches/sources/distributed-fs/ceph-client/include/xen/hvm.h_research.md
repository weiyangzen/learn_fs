<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/hvm.h -->
# sources/distributed-fs/ceph-client/include/xen/hvm.h

## Purpose
This header provides small wrappers around Xen HVM parameter hypercalls and callback-vector setup.

## Important APIs, Types, And Functions
- `param_name()` maps known `HVM_PARAM_*` indices to names for logging and returns `reserved`/`unknown` for gaps/out-of-range values.
- `hvm_get_parameter()` fills `struct xen_hvm_param`, calls `HYPERVISOR_hvm_op(HVMOP_get_param)`, logs failures, and returns the value.
- `HVM_CALLBACK_VECTOR(x)` composes a vector callback descriptor using type `HVM_CALLBACK_VIA_TYPE_VECTOR` shifted into the high bits.
- `xen_setup_callback_vector()` and `xen_set_upcall_vector()` set callback vectors globally/per CPU.

## Control Flow
HVM setup calls `hvm_get_parameter()` for Xen-provided PFNs/event channels and callback configuration, then configures event upcalls through vector helpers. Errors are logged with parameter names.

## State And Persistence
No state is stored in the header. Hypervisor HVM parameters and callback vector registration persist in Xen/domain state.

## Dependencies And Integration Points
It depends on Xen HVM param ABI and ARM/x86 hypercall wrappers. Consumers include HVM boot, Xenstore/console setup, event callback setup, and per-CPU upcall configuration.

## Risks And Edge Cases
`param_name()` only lists a subset of parameters; newer indices log as reserved/unknown. Callers must handle negative hypercall returns. Callback vector composition uses high-bit type fields, so integer width must remain 64-bit.

## Test Signals
Signals include successful retrieval of store/console/callback parameters, meaningful error logs for invalid indices, callback vector setup on boot and CPU bring-up, and event upcalls delivered through the configured vector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/hvm.h -->
