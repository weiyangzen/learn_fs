<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_asm.S

Purpose: Assembly support for VMX/Altivec register preservation tests. It fills, checks, and repeatedly mutates vector registers across syscall/preemption/signal scenarios.

Important APIs and types: Exports `check_vmx`, `test_vmx`, and `preempt_vmx` via `FUNC_START/FUNC_END`. It relies on helper macros from `basic_asm.h` and `vmx_asm.h` to load, compare, and poison vector registers.

Control flow: `check_vmx` validates a vector register image against memory. `test_vmx` loads all VMX registers, performs a syscall path driven by the caller, and verifies registers. `preempt_vmx` coordinates thread startup/running flags while spinning through VMX register checks under scheduler pressure.

State and persistence: The functions mutate architectural VMX registers and caller-visible status return values. Persistent test state lives in C globals supplied by callers, not in assembly storage.

Dependencies and integration points: Used by `vmx_preempt.c`, `vmx_signal.c`, and `vmx_syscall.c`; depends on powerpc VMX support, ABI-compatible vector register save/restore, and selftest assembly macros.

Risks: This code is highly ABI-sensitive: incorrect clobber expectations, missing VMX enablement, or kernel lazy-save bugs show up as false mismatches. Assembly loops can run for long periods and assume C-side flags remain valid.

Test signals: Passing VMX preempt, signal, and syscall tests indicates the kernel preserves Altivec state across context switches, signal delivery, and syscall entry/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_asm.S -->
