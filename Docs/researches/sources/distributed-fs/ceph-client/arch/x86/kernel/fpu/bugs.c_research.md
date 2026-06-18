# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/bugs.c

## Purpose
Performs boot-time detection of the classic Pentium FDIV FPU bug.

## Important APIs, Types, And Functions
`fpu__init_check_bugs()` uses `kernel_fpu_begin()`/`kernel_fpu_end()` and inline x87 instructions over constants `4195835.0` and `3145727.0`; it sets `X86_BUG_FDIV` on `boot_cpu_data` when the computed result is nonzero.

## Control Flow
If the boot CPU lacks hardware FPU, the check exits. Otherwise it enters a kernel FPU section, initializes x87 state, performs divide/multiply/subtract, stores the integer residual, exits the FPU section, and warns if a bug is detected.

## State, Persistence, And Dependencies
Persistent state is the CPU bug bit and warning. It depends on patched alternatives being ready for kernel FPU usage, hardware FPU availability, and x87 instruction behavior.

## Integration Points
Runs during CPU/FPU bug checks and influences `/proc/cpuinfo` bug reporting and mitigation awareness.

## Risks
Must not run before kernel FPU use is legal. The test intentionally ignores non-bug feature/status reporting.

## Test Signals
Normal CPUs should leave `X86_BUG_FDIV` clear. Emulated buggy FDIV behavior should set the bug bit and log the warning.
