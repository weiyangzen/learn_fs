# sources/distributed-fs/ceph-client/arch/parisc/lib/memcpy.c

Purpose: wraps the assembly `pa_memcpy()` routine for kernel `memcpy()` and raw user-copy primitives on PA-RISC, setting the correct source and destination space registers before entering assembly.

Important APIs/types/functions: `raw_copy_to_user()`, `raw_copy_from_user()`, exported `memcpy()`, and `copy_from_kernel_nofault_allowed()`. `get_user_space()` reads `SR_USER`; `get_kernel_space()` uses `SR_KERNEL`; `pa_memcpy()` returns bytes not transferred.

Control flow: `raw_copy_to_user()` sets source space to kernel and destination space to user, then delegates all copying and fault residual computation to `pa_memcpy()`. `raw_copy_from_user()` first probes each page of the requested user range with `prober_user()` and shortens the copy length at the first inaccessible page; it then returns the bytes skipped by pre-probe plus the assembly residual. `memcpy()` sets both temporary spaces to kernel and ignores the residual because kernel-to-kernel faults are not expected. `copy_from_kernel_nofault_allowed()` rejects only null-page sources.

State and dependencies: mutates PA-RISC temporary space registers around the copy; otherwise no persistence. Depends on `linux/uaccess.h`, `linux/mm.h`, `PAGE_SIZE`, `PAGE_ALIGN_DOWN`, and the assembly routine in `lusercopy.S`.

Risks: the pre-probe loop is page-granular and depends on correct wrap-free `start + len` arithmetic. Space register setup must match `pa_memcpy` assumptions. `memcpy()` has no overlap guarantees. The nofault allow-list is intentionally minimal and leaves I/O-space filtering as a comment.

Test signals: usercopy API tests, page-boundary permission failures, fault-injection around the first inaccessible page, kernel memcpy alignment tests, and nofault read tests for null-page rejection.
