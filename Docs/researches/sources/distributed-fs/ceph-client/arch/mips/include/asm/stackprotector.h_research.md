# sources/distributed-fs/ceph-client/arch/mips/include/asm/stackprotector.h

## Purpose

`stackprotector.h` provides MIPS GCC stack protector guard initialization.

## Important APIs, Types, And Functions

`boot_init_stack_canary()` seeds `current->stack_canary` from `get_random_canary()` and publishes it to the global `__stack_chk_guard`, which is the symbol GCC expects on MIPS. Macros/constants: `_ASM_STACKPROTECTOR_H`. Functions/prototypes/helpers: `boot_init_stack_canary`, `get_random_canary`.

## Control Flow

The helper is called from non-returning early/thread setup paths and must remain always-inline so the compiler cannot emit protected prologue/epilogue code around canary initialization.

## State And Persistence

The persistent state is the per-task `stack_canary` plus the architecture-wide global `__stack_chk_guard`; MIPS cannot use distinct per-task guards for GCC's global guard model on SMP.

## Dependencies And Integration Points

It integrates with `CONFIG_STACKPROTECTOR`, task setup, random canary generation, and compiler-emitted `__stack_chk_fail` checks.

## Risks

Risks are predictable canaries, calling from a returning protected function, and SMP-wide guard reuse.

## Test Signals

Test signals are stack-protector boot builds, forced stack-smash tests, and inspection that early init paths call the helper before protected code returns.
Static review signal: this source currently has 35 lines and 1022 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
