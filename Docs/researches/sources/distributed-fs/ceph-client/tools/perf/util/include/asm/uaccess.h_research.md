# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/uaccess.h

Purpose: userspace perf shim for kernel `asm/uaccess.h`. It provides trivial user-access macros to allow imported kernel-style code to compile when the "user" pointer is just an address perf can dereference in its own process context.

Important APIs and types: `__get_user(src, dest)` assigns `*dest` to `src` and returns `0`; `get_user` aliases `__get_user`; `access_ok(addr, size)` always returns `1`.

Control flow: macro-only. `__get_user` expands to a GNU statement expression with a direct load and success return.

State and persistence: no stored state; it may read pointed-to process memory directly.

Dependencies and integration: used by perf's imported helper code that references kernel uaccess primitives. It bypasses kernel access checks because perf tools run in userspace.

Risks: `access_ok()` always succeeding means invalid pointers are not guarded here. Direct dereference can segfault if used on untrusted or remote addresses. This must remain limited to code paths where the pointer is known to be valid in the perf process.

Test signals: build coverage plus sanitizer or crash tests for any consumer that could pass invalid pointers. Review signal is more important than unit tests because the macros are intentionally unsafe outside their narrow compatibility context.
