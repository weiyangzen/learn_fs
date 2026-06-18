# sources/distributed-fs/ceph-client/include/asm-generic/uaccess.h

Purpose: generic userspace access helpers for architectures with shared kernel/user address space, especially NOMMU-style configurations. It provides the fallback `get_user`, `put_user`, `clear_user`, raw copy, and nofault kernel access primitives.

Important APIs/types/functions: `__get_user_fn`, `__put_user_fn`, `raw_copy_from_user`, `raw_copy_to_user`, `__put_user`, `put_user`, `__get_user`, `get_user`, `__clear_user`, `clear_user`, `strncpy_from_user`, and `strnlen_user`. Under `CONFIG_UACCESS_MEMCPY`, single-value access uses unaligned loads/stores directly; otherwise the file falls back to `raw_copy_{from,to}_user`.

Control flow: public `get_user`/`put_user` call `might_fault()`, check `access_ok()`, then dispatch through size-specific switch statements for 1/2/4/8-byte transfers. Unsupported object sizes deliberately call noreturn bad-size helpers. `clear_user` returns the uncleared byte count on an access check failure.

State and persistence: no persistent state. The observable state is copied data and the return code/uncopied byte count.

Dependencies and integration points: depends on `linux/string.h`, `linux/unaligned.h` when enabled, `asm-generic/access_ok.h`, and `asm/extable.h`. It is pulled by architecture uaccess layers that do not provide stronger hardware-fault-backed implementations.

Risks: direct memcpy-style access assumes the architecture can safely dereference user pointers after `access_ok`; that is not valid on MMU architectures needing exception-table recovery. Size dispatch must stay compile-time bounded or bad-size paths break callers. Callers must check negative `-EFAULT` returns and partial clear/copy counts.

Test signals: compile coverage across `CONFIG_UACCESS_MEMCPY` on/off, sparse `__user` pointer checking, fault-injection tests for invalid user pointers, and libc/syscall smoke tests exercising user copy paths.
