# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-pkey.c

## Purpose
`ptrace-pkey.c` verifies ptrace read/write behavior for POWER pkey registers AMR, IAMR, and UAMOR while a child actively uses protection keys.

## Important APIs, Types, and Functions
Important routines are `child()`, `parent()`, `ptrace_pkey()`, and `main()`. `struct shared_info` stores synchronization state, valid and invalid AMR/IAMR/UAMOR values, and expected register results.

## Control Flow and State
The child allocates pkeys, maps memory with selected access permissions, updates pkey registers, and synchronizes around user read/write phases. The parent ptrace-attaches, reads pkey registers, attempts valid and invalid writes, checks kernel rejection of disallowed values, and resumes the child. State is shared memory, pkey allocations, child registers, and ptrace stop status.

## Dependencies and Integration Points
It depends on local `pkeys.h`, `child.h`, powerpc ptrace register sets, memory protection key syscalls, and kselftest macros.

## Risks and Test Signals
Risks are absent pkey hardware, permission-dependent ptrace failures, and stale expected masks. A pass means ptrace exposes pkey registers accurately and enforces valid writable bits.
