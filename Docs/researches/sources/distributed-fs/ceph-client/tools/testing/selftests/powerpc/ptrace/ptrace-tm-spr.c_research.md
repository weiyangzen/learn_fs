# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spr.c

Purpose: tests ptrace readout of transactional-memory SPRs (`TFHAR`, `TEXASR`, `TFIAR`) from a child stopped while a transaction is suspended.

Important APIs/types/functions: `struct shared` carries a completion flag plus `struct tm_spr_regs`; `validate_tm_spr()` checks expected `TFHAR` and tolerated KVM reschedule encoding; `tm_spr()` constructs the transaction; `trace_tm_spr()` calls `show_tm_spr()`.

Control flow: the child computes the transaction fail-handler address around `tbegin.`, suspends, signals readiness through a second shared-memory page, and loops. The parent attaches, fetches TM SPRs into shared memory, marks the flag, detaches, and waits. The abort path then validates the fetched data against the locally calculated `tfhar`.

State and persistence behavior: two SysV shared-memory regions separate SPR payload from the simple ready flag. The expected `tfhar` is a process global in the child and is adjusted for instruction distance.

Dependencies and integration points: requires `ptrace.h` TM regset constants, `tm.h` HTM checks, and working `NT_PPC_TM_SPR`.

Risks and test signals: instruction-layout assumptions are central; compiler/assembler changes near `tbegin.` can break `tfhar` expectations. The test treats synthetic TM as skip and uses child exit status as the final signal.
