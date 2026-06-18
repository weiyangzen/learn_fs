# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace.h

Purpose: central ptrace helper implementation for powerpc selftests, covering attach/detach, scalar SPRs, GPR/FPR, VMX/VSX, checkpointed TM regsets, and TM SPR readout.

Important APIs/types/functions: defines fallback `NT_PPC_*` regset constants, `struct fpr_regs`, `struct tm_spr_regs`, `start_trace()`, `stop_trace()`, `ptrace_read_regs()`, `ptrace_write_regs()`, TAR/PPR/DSCR helpers, checkpointed GPR/FPR/VMX/VSX helpers, `show_tm_spr()`, and TEXASR analysis helpers.

Control flow: most helpers build an `iovec`, issue `ptrace(PTRACE_GETREGSET/SETREGSET)` or legacy requests, copy relevant pieces into caller buffers, and return `TEST_PASS/TEST_FAIL`. Basic trace helpers attach and wait before reads, then detach afterward for the generic read/write wrappers.

State and persistence behavior: no durable state; allocations are per-call. Some error paths return without freeing allocated buffers, which is tolerable in short selftests but relevant if reused in long-running tools.

Dependencies and integration points: depends on Linux UAPI ptrace, powerpc `reg.h`, `utils.h`, and TM SPR definitions. It is included as implementation by many tests rather than compiled as a library.

Risks and test signals: helpers assume caller has already stopped the child for many direct regset accesses. Error messages sometimes name GETREGSET for SET failures, so diagnostics can be imprecise.
