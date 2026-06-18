<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hw_breakpoint.h

## Purpose
`hw_breakpoint.h` exposes userspace constants for configuring hardware breakpoints and watchpoints through perf events.

## Important APIs, types, and functions
The header defines breakpoint length constants `HW_BREAKPOINT_LEN_1` through `HW_BREAKPOINT_LEN_8` and type bits `HW_BREAKPOINT_EMPTY`, `HW_BREAKPOINT_R`, `HW_BREAKPOINT_W`, `HW_BREAKPOINT_RW`, `HW_BREAKPOINT_X`, and `HW_BREAKPOINT_INVALID`. These values are used in `perf_event_attr.bp_type` and `bp_len`.

## Control flow
User space configures a perf event with a breakpoint address, type mask, and length. The perf and architecture-specific breakpoint code programs hardware debug registers and reports events when the access condition matches.

## State and persistence behavior
Breakpoint state is per perf event and per task or CPU depending on how the event is opened. It persists until the event fd is closed, disabled, or reconfigured.

## Dependencies and integration points
It integrates with `perf_event_open`, architecture debug-register backends, ptrace/debugger tooling, and kernel breakpoint reservation.

## Risks and test signals
Risks include unsupported lengths on some architectures despite the generic 1-8 constants, limited hardware slots, alignment constraints, confusing read/write/execute semantics, and privilege restrictions. Test signals include perf breakpoint selftests, invalid length/type rejection, signal/event delivery tests, per-task versus per-CPU coverage, and architecture-specific slot exhaustion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hw_breakpoint.h -->
