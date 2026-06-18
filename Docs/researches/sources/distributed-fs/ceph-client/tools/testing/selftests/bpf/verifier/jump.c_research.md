# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jump.c

Purpose: tests general jump validation, stack-state merging, loop/back-edge handling, call/jump boundary validation, and dead-code elimination.

Important APIs/types/functions: uses conditional jumps, `BPF_JMP_IMM(BPF_JA)`, raw subprogram calls, map delete helper, scheduler classifier program type, and stack stores through frame pointers.

Control flow: early tests branch through many paths storing to stack slots and merging pointer state, with unprivileged pointer comparison rejections. Mid-file tests exercise long forward/backward jump layouts that are accepted as bounded. Call/jump tests distinguish valid jump loops from invalid subprogram call targets or missing exits. Final test uses signed/unsigned range checks and dead-code elimination to prove the safe return path.

State and persistence behavior: verifier state includes stack-slot initialization, pointer comparison restrictions, reachability, loop recognition, and cross-instruction state merging.

Dependencies and integration points: some tests require hash-map fixups and scheduler classifier program type; unprivileged expected errors are part of the contract.

Risks: jump target validation interacts with subprogram boundaries and dead-code pruning. Off-by-one target changes can accept jumps into invalid instruction regions.

Test signals: accepted cases return expected values or `-ENOENT`; rejected cases report `jump out of range from insn ...`, `last insn is not an exit or jmp`, or unprivileged `R1 pointer comparison`.
