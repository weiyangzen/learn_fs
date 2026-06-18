# sources/distributed-fs/ceph-client/include/linux/sched/coredump.h

Purpose: declares dumpability constants and helpers for reading/updating `mm_struct` coredump policy bits.

Important APIs and types: `SUID_DUMP_DISABLE`, `SUID_DUMP_USER`, `SUID_DUMP_ROOT`, `__mm_flags_get_dumpable()`, `__mm_flags_set_mask_dumpable()`, `set_dumpable()`, `__get_dumpable()`, and `get_dumpable()` are the main symbols.

Control flow: exec, credential, proc, and coredump paths set or inspect dumpability through `mm->flags`; callers must distinguish `SUID_DUMP_USER` from other nonzero modes because root-owned setuid dumping has different semantics.

State and persistence: state is the dumpability bitfield inside a live `mm_struct`. It lasts for the address-space lifetime and influences coredump and ptrace/proc access behavior.

Dependencies and integration points: depends on MM flag helpers and integrates scheduler task/MM code with coredump, exec, credentials, and security decisions.

Risks and test signals: risks include treating dumpability as boolean, mask drift in MM flags, and incorrect privilege-transition updates. Test setuid/exec transitions, `/proc/sys/fs/suid_dumpable`, coredump generation, ptrace/proc access checks, and mm flag helpers.
