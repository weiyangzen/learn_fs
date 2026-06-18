# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/Makefile

Purpose: kselftest makefile for ptrace ABI tests.

Important APIs and functions: sets `CFLAGS += -std=c99 -pthread -Wall $(KHDR_INCLUDES)` and builds `get_syscall_info`, `set_syscall_info`, `peeksiginfo`, `vmaccess`, and `get_set_sud`.

Control flow: includes `../lib.mk` for standard build and run behavior.

State and persistence: no runtime state.

Dependencies and integration: requires kernel headers exposing recent ptrace constants and pthread support.

Risks and test signals: some tests depend on ptrace permissions and architecture-specific syscall ABI behavior.
