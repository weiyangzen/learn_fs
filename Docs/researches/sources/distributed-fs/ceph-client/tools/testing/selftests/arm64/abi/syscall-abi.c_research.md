# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi.c

Purpose: validates arm64 syscall ABI preservation/clearing rules across FPSIMD, SVE, SME streaming mode, ZA, ZT0, predicates, FFR, SVCR, and GPRs.

Important APIs/types/functions: global buffers for each register class; setup/check pairs (`setup_gpr`/`check_gpr`, `setup_fpr`/`check_fpr`, `setup_z`/`check_z`, `setup_p`/`check_p`, `setup_ffr`/`check_ffr`, `setup_svcr`/`check_svcr`, `setup_za`/`check_za`, `setup_zt`/`check_zt`); `regset[]` dispatch table; `do_test()` calls assembly `do_syscall()`; `test_one_syscall()` runs combinations for `getpid()` and `sched_yield()`; `sve_count_vls()` and `sme_count_vls()` enumerate supported VLs; `main()` plans and reports.

Control flow: enumerate SVE/SME vector lengths from high to low, then for each syscall run FPSIMD-only, each SVE VL, each SME VL with SM+ZA, SM, and ZA, and cross-product SVE/SME cases. Setup fills random inputs; assembly performs syscall; check functions enforce expected preservation or zeroing.

State and persistence: random test patterns and output buffers are process globals. No persistence.

Dependencies/integration: requires arm64 auxv HWCAPs, prctl SVE/SME VL controls, signal context size macros, kselftest, and `syscall-abi-asm.S`.

Risks and test signals: test count scales with hardware-supported vector lengths. Emulator slowness is mitigated by `ARCH_SVE_VQ_MAX 16`. Assumes syscall clobber/preserve rules in comments; mismatches print detailed register diagnostics.
