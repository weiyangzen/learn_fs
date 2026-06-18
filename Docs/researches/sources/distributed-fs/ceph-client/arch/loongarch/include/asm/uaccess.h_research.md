<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uaccess.h

Purpose: implements LoongArch user memory access primitives, address-limit checks, and exception-table guarded copy helpers.
Important APIs and types: provides `access_ok`, `__get_user`, `__put_user`, raw copy helpers, clear-user, `unsafe_get_user`, `unsafe_put_user`, and masked user access support around `__ua_limit` on 64-bit.
Control flow: accessors validate user ranges, emit inline load/store assembly with fixups, and return `-EFAULT` on exception. Bulk copy functions are delegated to architecture routines and generic wrappers.
State and persistence: no independent state, but it reads the process address limit and may zero or partially copy caller-provided buffers on faults.
Dependencies and integration: central to syscalls, signal frame copy, ptrace, filesystem/network I/O, BPF, and Spectre-v1 user pointer mitigation.
Risks and test signals: range-check or fixup errors are security critical. Signals include `lib/test_user_copy`, LKDTM usercopy, signal/ptrace tests, KASAN, and fault-injection around bad user pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uaccess.h -->
