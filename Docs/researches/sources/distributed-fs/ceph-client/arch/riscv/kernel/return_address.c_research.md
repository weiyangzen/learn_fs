<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/return_address.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/return_address.c

Purpose: Implements `return_address()` for RISC-V by walking stack frames until the requested call depth is reached.

Important APIs/types/functions: Uses `struct return_address_data`, callback `save_return_addr()`, and exported `return_address()`.

Control flow: `return_address()` seeds a skip counter, invokes `walk_stackframe()` on the current task, and the callback records the PC when the requested level is reached.

State and persistence: No persistent state; the result is computed from live frame-pointer stack state.

Dependencies and integration points: Depends on `stacktrace.c` frame walking and is used by generic debugging, tracing, and diagnostics that need caller return PCs.

Risks: Results are only as reliable as frame pointers/unwinder data. Interrupt, exception, and optimized frames can limit depth or return NULL.

Test signals: Build with frame pointers, compare `return_address()` levels against known call chains, and exercise through interrupt and scheduler contexts.

Source read size: 48 lines, 847 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/return_address.c -->
