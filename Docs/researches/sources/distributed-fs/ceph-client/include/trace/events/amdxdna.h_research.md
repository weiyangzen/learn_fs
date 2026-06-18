# sources/distributed-fs/ceph-client/include/trace/events/amdxdna.h

## Purpose
`amdxdna.h` defines tracepoints for AMD XDNA driver debugging: generic debug points, DRM scheduler jobs, mailbox head/tail updates, and mailbox IRQ handling.

## Important APIs, types, and functions
Events are `amdxdna_debug_point`, `xdna_job`, `mbox_set_tail`, `mbox_set_head`, and `mbox_irq_handle`. `xdna_mbox_msg` is the shared event class for mailbox head/tail updates.

## Control flow
Driver call sites emit debug points with a name, number, and string; job events snapshot scheduler fence context/sequence plus a driver sequence; mailbox events trace channel id, opcode, and message id; IRQ handling traces device/mailbox name and IRQ number.

## State and persistence behavior
No state is stored by the header. Events snapshot dynamic strings, DRM fence identifiers, mailbox ids, and IRQ numbers for later correlation.

## Dependencies and integration points
It depends on `<drm/gpu_scheduler.h>` and `<linux/tracepoint.h>`. It integrates with the DRM scheduler, AMD XDNA mailbox code, and generic trace consumers.

## Risks and test signals
Risks include null or invalid `sched_job->s_fence`, string lifetime assumptions before `__assign_str()`, and event names that are too generic outside the `amdxdna` trace system. Test signals are traces around job submission/completion, mailbox doorbell activity, and IRQ execution with matching message ids.
