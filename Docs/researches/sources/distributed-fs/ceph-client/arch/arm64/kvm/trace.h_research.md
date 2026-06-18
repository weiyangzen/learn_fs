<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/trace.h

## Purpose
This is a small umbrella trace header for arm64 KVM. It includes the architecture tracepoint definitions split across `trace_arm.h` and `trace_handle_exit.h`.

## Important APIs, Types, And Functions
- Includes `trace_arm.h` for guest entry/exit, fault, MMIO, timer, nested exception, and forwarded sysreg trap tracepoints.
- Includes `trace_handle_exit.h` for exit handling tracepoints such as WFx, HVC, sysreg trap, sysreg access, and guest debug changes.

## Control Flow
Translation units include this header to make the trace event prototypes available. The included headers define trace events and instantiate trace metadata through `trace/define_trace.h`.

## State And Persistence Behavior
No runtime state is stored here. It gates compile-time inclusion of tracepoint definitions.

## Dependencies And Integration Points
This header is consumed by arm64 KVM code such as `sys_regs.c`. It integrates with Linux ftrace/perf tracepoint infrastructure under `TRACE_SYSTEM kvm`.

## Risks And Edge Cases
Because both included trace headers define trace metadata, include guards and `TRACE_HEADER_MULTI_READ` behavior must remain correct. Include path macros in the child headers must point at the source layout expected by trace generation.

## Test Signals
Successful kernel build with tracepoints enabled is the primary signal. Runtime enabling of KVM trace events should show events from both included headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace.h -->
