# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-vsx.c

Purpose: checks ptrace VMX/VSX live and checkpoint state while a child is in a transaction and validates that checkpoint writes become the restored state after abort.

Important APIs/types/functions: `tm_vsx()`, `trace_tm_vsx()`, `load_vsx_vmx()`, `show_vsx()`, `show_vmx()`, `show_vsx_ckpt()`, `show_vmx_ckpt()`, `write_vsx_ckpt()`, and `write_vmx_ckpt()` are the important pieces.

Control flow: the child loads checkpoint vector state, starts a transaction, loads live vector state, suspends to signal readiness, resumes, and loops. The parent verifies live VSX/VMX state against `fp_load`, checkpoint state against `fp_load_ckpt`, writes the new checkpoint vector pair built from `fp_load_ckpt_new`, releases the child, and expects the abort path to store and compare the new values.

State and persistence behavior: shared memory has release and ready slots. Global vector buffers persist across fork and are used as deterministic per-run expectations.

Dependencies and integration points: requires HTM, non-synthetic TM, VSX hardware support implied by regsets, `ptrace-vsx.h` validation, and kernel ptrace regset plumbing.

Risks and test signals: VMX/VSX endian layout is a major risk; helper validation handles it. Failure surfaces as `FAIL_IF`, parent kill, or nonzero child exit.
