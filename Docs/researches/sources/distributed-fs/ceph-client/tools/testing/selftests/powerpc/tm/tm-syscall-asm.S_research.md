# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-syscall-asm.S

Purpose: assembly syscall primitives for testing `sc` and `scv` behavior in active and suspended transactions.

Important APIs/types/functions: exports `getppid_tm_active`, `getppid_tm_suspended`, `getppid_scv_tm_active`, and `getppid_scv_tm_suspended`; defines `scv` instruction encoding macro.

Control flow: active variants begin a transaction and issue getppid directly, expecting transaction abort. Suspended variants begin, suspend, issue syscall, resume, and commit. Abort handler paths return -1.

State and persistence behavior: stateless aside from CPU TM state and return registers; `scv` variants use stack save/restore macros.

Dependencies and integration points: called by `tm-syscall.c` and requires syscall number headers plus assembler support for emitted `scv`.

Risks and test signals: incorrect abort return handling would confuse C failure-code checks. `scv` paths are only used when hardware capability reports support.
