# sources/distributed-fs/ceph-client/arch/mips/kernel/r4k-bugs64.c

## Purpose
Detects known 64-bit R4000/R4400 errata at boot and panics if required compiler/CPU workarounds are missing.

## Important APIs, Types, and Functions
- `check_mult_sh()` tests multiply/shift interaction errata across instruction alignments.
- `do_daddi_ov()` is a temporary overflow exception handler for DADDI testing.
- `check_daddi()` tests whether `daddi` correctly raises overflow.
- `check_daddiu()` tests DADDIU result correctness and records `daddiu_bug`.
- `check_bugs64_early()` runs early multiply/shift and DADDIU checks.
- `check_bugs64()` runs the later DADDI overflow check.

## Control Flow
Early setup calls `check_bugs64_early()` when configured. It runs carefully aligned inline assembly with interrupts disabled to detect errata-sensitive instruction sequences, compares raw and workaround results, and panics with a targeted workaround message if the workaround is absent. Later CPU finalize calls `check_bugs64()`, which installs an overflow exception vector, executes the DADDI sequence, restores the old handler, and verifies that either no bug exists or the workaround triggers expected overflow.

## State and Persistence
`daddiu_bug` records DADDIU bug detection. `daddi_ov` records whether the temporary overflow handler ran. No persistent storage.

## Dependencies and Integration Points
Integrated from `setup.c` via `check_bugs64_early()` and `arch_cpu_finalize_init()`/`check_bugs64()`. Depends on CP0 exception vector installation, context tracking in exception handlers, local IRQ control, and compiler workaround Kconfig options.

## Risks
The detection code intentionally executes errata-triggering sequences; incorrect alignment or compiler optimization could hide a bug. It manipulates exception vectors and must restore them. False negatives would allow unreliable CPU operation; false positives panic otherwise bootable systems.

## Test Signals
Boot logs should print the three bug checks and either `no`, `yes, workaround... yes`, or panic with a clear workaround instruction. Known affected CPUs should require the matching workaround configs.
