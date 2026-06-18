# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/Makefile

Purpose: builds powerpc syscall ABI tests for unmuxed IPC syscalls and RTAS syscall filtering.

Important APIs/types/functions: `TEST_GEN_PROGS := ipc_unmuxed rtas_filter`; includes common kselftest make files and adds `$(KHDR_INCLUDES)`.

Control flow: both tests link `../harness.c` and `../utils.c`.

State and persistence behavior: build-only file with no runtime state.

Dependencies and integration points: requires kernel headers for syscall numbers and RTAS ABI definitions.

Risks and test signals: missing headers can remove IPC cases or fail RTAS compilation.
