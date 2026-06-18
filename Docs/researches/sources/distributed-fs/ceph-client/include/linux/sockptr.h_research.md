<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sockptr.h -->
# sources/distributed-fs/ceph-client/include/linux/sockptr.h

Purpose: This header provides `sockptr_t`, a small tagged pointer abstraction for socket options and similar APIs that can accept either kernel memory or user memory without duplicating copy logic.

Important APIs/types/functions: `sockptr_t` stores either `void *kernel` or `void __user *user` plus `is_kernel`. Constructors are `KERNEL_SOCKPTR()` and `USER_SOCKPTR()`. Helpers cover null checks, offset copies, safe fixed-size copies, extensible struct copies, copy-to, memdup with and without NUL termination, string copy, and zero-tail validation.

Control flow: Callers receive a `sockptr_t` and branch only through helpers. User-backed paths use `copy_from_user()`, `copy_to_user()`, `copy_struct_from_user()`, `strncpy_from_user()`, and `check_zeroed_user()`. Kernel-backed paths use `memcpy()`, `memset()`, `memchr_inv()`, and local string length checks.

State and persistence: The abstraction has no persistence; it wraps pointer provenance for a single call. Allocating helpers return kernel allocations via `kmalloc_track_caller_noprof()` and report errors as `ERR_PTR()`.

Dependencies/integration: Depends on slab allocation and uaccess helpers. It is integrated heavily with socket option paths where the same implementation may be reached from syscalls, BPF/kernel callers, or internal protocol code.

Risks and test signals: The deprecated `copy_from_sockptr()` is unsafe unless the caller already validated length. `copy_struct_from_sockptr()` must reject non-zero excess bytes for forward-compatible kernel inputs and zero-fill short kernel inputs. Test with small `optlen`, user fault injection, oversized non-zero tails, kernel pointer callers, NUL termination, and KASAN/KMSAN coverage for offset arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sockptr.h -->
