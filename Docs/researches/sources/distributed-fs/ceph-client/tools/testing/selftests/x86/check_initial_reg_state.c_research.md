# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/check_initial_reg_state.c

## Purpose

`check_initial_reg_state.c` verifies the initial general-purpose register and flags state at process entry after `execve()`. It uses a custom assembly entry point to capture registers before libc or the dynamic loader can modify them.

## Important APIs, Types, and Functions

Global variables store captured registers: `ax`, `bx`, `cx`, `dx`, `si`, `di`, `bp`, `sp`, `flags`, and on x86_64 `r8` through `r15`. Inline assembly defines global function `real_start`, stores registers into globals, captures flags with `pushf/popf`, and jumps to `_start`. The Makefile links this test statically with `-Wl,-ereal_start -static`.

## Control Flow

At process entry, `real_start` runs first and records register state. Normal startup then calls `main()`, which fails if `sp` is zero, verifies all GPRs except stack pointer are zero, prints each unexpected value on failure, and verifies `FLAGS == 0x202`.

## State and Persistence Behavior

State is just global variables in the test process. There is no persistence.

## Dependencies and Integration Points

It depends on static linking and the Makefile's custom entry point so no interpreter destroys initial state. It integrates with x86 selftest build modes for both 32-bit and 64-bit.

## Risks and Edge Cases

The expected zero-register ABI is sensitive to kernel exec setup and architecture mode. If the binary is accidentally linked dynamically or without `real_start`, the test detects `sp == 0` or false register values.

## Test Signals

Pass signals are `[OK] All GPRs except SP are 0` and `[OK] FLAGS is 0x202`, with zero exit status.
