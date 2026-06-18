# sources/distributed-fs/ceph-client/tools/include/uapi/linux/hw_breakpoint.h

Purpose: exposes generic hardware breakpoint/watchpoint length and access-type constants for perf events and ptrace/debug tooling.

Important APIs/types: length enum values define byte lengths 1 through 8. Type enum values define empty, read, write, read/write, execute, and invalid combinations. There are no structs or functions.

Control flow, state, and persistence: the header is compile-time constants only. Runtime flow is consumers passing these values in breakpoint attributes to kernel perf/debug APIs; kernel and architecture code validate whether the requested type and length can be represented by hardware debug registers.

Dependencies and integration points: standalone UAPI header. It integrates perf hardware breakpoints, debuggers, tracing tools, and architecture-specific breakpoint backends.

Risks and test signals: risks are assuming every architecture supports all lengths/types, using `HW_BREAKPOINT_INVALID`, and confusing execute breakpoints with read/write watchpoints. Tests should create perf breakpoint events for supported and unsupported lengths, verify read/write/execute triggers, and validate rejection of invalid combinations on each target architecture.
