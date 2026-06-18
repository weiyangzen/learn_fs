<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.c

Purpose: exhaustive ptrace selftest for arm64 FPSIMD, SVE, streaming SVE, SME ZA, SME2 ZT, SVCR, vector lengths, and FPMR. It verifies both initial ptrace visibility and effects of ptrace writes across mode/VL transitions.

Important APIs, types, and functions: `struct test_config` captures input and expected SVE/SME VL plus SVCR state; `struct test_definition` describes supported/write/expected callbacks. Feature probes use `getauxval(AT_HWCAP/HWCAP2)`. Regset operations use `PTRACE_GETREGSET`/`PTRACE_SETREGSET` for `NT_PRFPREG`, `NT_ARM_SVE`, `NT_ARM_SSVE`, `NT_ARM_ZA`, `NT_ARM_ZT`, and `NT_ARM_FPMR`. Key routines include `run_child`, `run_parent`, `continue_breakpoint`, `check_ptrace_values_*`, `set_initial_values`, `check_memory_values`, `fpsimd_write`, `sve_write_sve`, `sve_write_fpsimd`, `za_write`, `zt_write`, `fpmr_write`, `probe_vls`, `run_sve_tests`, and `run_sme_tests`.

Control flow: main probes supported VLs, computes the kselftest plan, installs a SIGALRM timeout handler, then runs FPSIMD-only, SVE, and SME matrix tests. Each test fills globals with random valid state, forks a child, has the child set requested VLs and call `load_and_save`, checks initial ptrace-visible state while stopped at BRK, optionally writes new regset state, resumes the child to save state, reads saved globals via `process_vm_readv`, detaches, waits for clean exit, and compares saved state to expected data.

State and persistence: global buffers hold input, expected, and output register state for all tested register classes. No disk persistence. The parent relies on fork-inherited virtual addresses to read child memory directly. Random values are seeded by PID and masked for safe FPMR bits.

Dependencies and integration: depends on `fp-ptrace-asm.S`, `fp-ptrace.h`, `sme-inst.h`, `kselftest.h`, asm sigcontext/SVE ptrace layout macros, and arm64 Linux regset ABI. It integrates with the selftests Makefile as the high-coverage FP ptrace contract test.

Risks: the state-space is large on systems with both SVE and SME. Some expectations encode delicate ABI rules: FPSIMD writes flush SVE state, SME VL changes can clear ZA/ZT/SVE data, streaming mode changes whether NT_ARM_SVE/SSVE returns full SVE or FPSIMD-format state, and FFR validity depends on FA64. A code-level risk is that pointer arithmetic on `void *` relies on GNU C.

Test signals: TAP results for each test definition and VL/SVCR combination. Failures print precise mismatch names such as initial/saved V, Z, P, FFR, ZA, ZT, FPMR, SVCR, SVE VL, or SME VL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.c -->
