<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/stacktrace.h

Purpose: Declares RISC-V stack walking data structures and helpers.

Important APIs/types/functions: Defines `struct stackframe`, `walk_stackframe()`, and unwind helper declarations.

Control flow: Callers seed frame pointer/return address and iterate frames through the architecture unwinder.

State and persistence: State is transient unwind cursor state plus stack contents produced by call frames.

Dependencies and integration points: Used by dump_stack, perf callchains, ftrace, livepatch-style checks, and debugging.

Risks: Bad frame validation can read invalid stacks or produce misleading traces.

Test signals: Stacktrace selftests, perf callchain, ftrace, exception-stack traces, and frame-pointer/non-frame-pointer builds.

Source read size: 29 lines, 774 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/stacktrace.h -->
