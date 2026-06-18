# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/handlers.S

## Purpose
This RISC-V assembly file implements the guest exception vector entry used by selftests with custom exception/interrupt handlers.

## Important APIs, Types, and Functions
`save_context` stores integer registers plus `sepc`, `sstatus`, `stval`, and `scause` into a stack frame. `restore_context` restores those CSRs and registers. The global `exception_vectors` entry calls C `route_exception()` and returns with `sret`.

## Control Flow
On trap entry, the vector subtracts stack space, saves context, passes the stack frame pointer in `a0`, calls the C router, restores context, and resumes guest execution with `sret`.

## State, Dependencies, and Integration
State is per-trap stack data. It depends on RISC-V CSR names and must match the C `pt_regs` layout expected by `processor.c`. `vcpu_init_vector_tables()` programs `stvec` to this symbol.

## Risks and Test Signals
Incorrect frame offsets or CSR restore order can corrupt guest state or loop traps. Unexpected exceptions are routed to ucall failure paths in `processor.c`.
