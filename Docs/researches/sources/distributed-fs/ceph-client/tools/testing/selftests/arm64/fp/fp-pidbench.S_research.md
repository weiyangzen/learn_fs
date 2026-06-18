<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-pidbench.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-pidbench.S

Purpose: standalone nolibc-style AArch64 assembly benchmark for measuring `getpid` syscall overhead before and after SVE use. It isolates libc/toolchain FP side effects by issuing raw syscalls and timer reads.

Important APIs and functions: `_start` is the only entry point. `test_loop` is a macro that times a fixed loop using `CNTVCT_EL0`, `__NR_getpid`, optional per-iteration SVE work, and `putdec`/`puts` helpers from `assembler.h`. It probes SVE by reading `ID_AA64PFR0_EL1` and uses `rdvl` to establish active vector length.

Control flow: print iteration count, time `getpid` with no SVE, check SVE support, touch SVE once, time subsequent syscalls, time syscalls with `rdvl` before each `svc`, then time no-SVE work again after SVE has been used. It exits via raw `__NR_exit`.

State and persistence: no persistent state; only registers, timer values, and stdout output. Dependencies include `asm/unistd.h`, `assembler.h`, privileged-readable architectural feature registers, and SVE instruction availability.

Integration points: built as an arm64 selftest helper/benchmark in the FP test folder. It complements correctness tests by detecting syscall overhead changes caused by lazy SVE/FPSIMD state management.

Risks: direct `ID_AA64PFR0_EL1` access assumes userspace visibility on the target kernel/config; benchmark results are noisy under virtualization and CPU frequency changes. It is not TAP-plan based and reports raw timings.

Test signals: successful output has timing lines for "No SVE", "SVE used once", "SVE used per syscall", and "No SVE after SVE"; unsupported SVE prints a skip-like message and exits cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-pidbench.S -->
