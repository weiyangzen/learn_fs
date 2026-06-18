<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/ftrace.h

## Purpose
Defines Xtensa ftrace entry metadata and return-address hook.

## Important APIs, Types, And Functions
Declares `return_address`, defines `ftrace_return_address(n)`, and under `CONFIG_FUNCTION_TRACER` defines `MCOUNT_ADDR`, `MCOUNT_INSN_SIZE`, `_mcount`, and `mcount`.

## Control Flow
No runtime flow in the header; ftrace code patches or calls `_mcount` based on the declared instruction size and symbol address.

## State And Persistence
No owned state. Ftrace runtime state is managed by tracing core.

## Dependencies And Integration Points
Depends on Xtensa processor conventions, function tracer implementation, and return-address unwinding support.

## Risks And Edge Cases
`MCOUNT_INSN_SIZE` must match the actual call instruction size. Return address depth handling must match windowed/call0 ABI stack frames.

## Test Signals
Build with function tracer, enable ftrace function graph/function tracing, and verify return addresses for nested calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/ftrace.h -->
