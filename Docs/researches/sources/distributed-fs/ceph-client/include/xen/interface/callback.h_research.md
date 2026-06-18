<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/callback.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/callback.h

## Purpose
This Xen public header defines callback registration ABI constants and structures for guest callback entry points.

## Important APIs, Types, And Functions
- `CALLBACKTYPE_*` values identify event, failsafe, syscall, deprecated sysenter, NMI, sysenter, and syscall32 callbacks, mostly x86-specific.
- `CALLBACKF_mask_events` requests event masking during callbacks where applicable.
- `CALLBACKOP_register` and `CALLBACKOP_unregister` select callback hypercall operations.
- `struct callback_register` contains type, flags, and `xen_callback_t address`.
- `struct callback_unregister` contains type and padding.

## Control Flow
Guest setup code builds a register or unregister structure and passes it to the Xen callback op hypercall. Xen then uses the registered callback address for event, failsafe, syscall, or NMI delivery.

## State And Persistence
Callback registrations persist in hypervisor domain state until changed, unregistered, or domain shutdown.

## Dependencies And Integration Points
It depends on `xen/interface/xen.h` for `xen_callback_t`. It integrates with architecture entry code, event delivery, NMI/syscall handling, and Xen callback hypercalls.

## Risks And Edge Cases
Some callbacks cannot be unregistered and can return `-EINVAL`. Several callback types are deprecated or architecture-specific; using them on unsupported hypervisor/guest combinations will fail. Event masking semantics do not apply uniformly.

## Test Signals
Signals include successful callback registration, event delivery through the registered address, expected `-EINVAL` on unsupported unregister/type attempts, and correct behavior with `CALLBACKF_mask_events`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/callback.h -->
