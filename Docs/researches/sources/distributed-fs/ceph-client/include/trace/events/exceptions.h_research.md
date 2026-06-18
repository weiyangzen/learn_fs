<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/exceptions.h -->
# sources/distributed-fs/ceph-client/include/trace/events/exceptions.h

## Purpose
Defines generic page-fault tracepoints under the `exceptions` trace system for user and kernel faults.

## APIs, Control Flow, and State
The `exceptions` event class takes a fault address, `struct pt_regs *`, and architecture error code. It records the faulting address, instruction pointer via `instruction_pointer(regs)`, and raw error code. `page_fault_user` and `page_fault_kernel` are the concrete events. Output uses `%ps` for symbolic address formatting where possible. The header has no persistent state and relies entirely on the exception handling path to classify user vs kernel faults correctly.

## Dependencies, Integration, Risks, and Tests
Depends on tracepoints, `struct pt_regs`, and architecture-provided `instruction_pointer()`. Integration points are architecture page fault handlers and MM diagnostics. Risks include arch-specific error-code interpretation not being decoded here, invalid or incomplete register frames, symbolization leaking kernel addresses depending on pointer restrictions, and fault-path overhead if enabled at high rate. Test signals include user and kernel fault injection, tracefs event enablement during page fault tests, architecture build coverage, and comparing emitted IP/address values with oops or perf samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/exceptions.h -->
