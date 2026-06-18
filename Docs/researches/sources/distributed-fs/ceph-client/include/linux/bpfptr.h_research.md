# sources/distributed-fs/ceph-client/include/linux/bpfptr.h

Purpose: Provides `bpfptr_t`, a kernel/userspace pointer wrapper used by BPF syscall and helper paths that may receive data from either kernel memory or user memory. It aliases `sockptr_t` and adds BPF-named constructors and copy/string helpers.

Important APIs/types/functions: `bpfptr_is_kernel()` reads the address-space tag. `KERNEL_BPFPTR()` and `USER_BPFPTR()` construct tagged pointers. `make_bpfptr()` converts a raw 64-bit address plus kernel/user flag. `bpfptr_is_null()` and `bpfptr_add()` inspect and adjust pointers. `copy_from_bpfptr_offset()` copies from user with `copy_from_user()` or from kernel with `copy_from_kernel_nofault()`, while `copy_from_bpfptr()` uses offset zero. `copy_to_bpfptr_offset()` delegates to `copy_to_sockptr_offset()`. `kvmemdup_bpfptr_noprof()` allocates a kernel buffer and copies from the source, with `kvmemdup_bpfptr()` wrapped in allocation hooks. `strncpy_from_bpfptr()` chooses kernel nofault or user string copy.

Control flow: Callers build a `bpfptr_t` from syscall/user or kernel context, validate sizes elsewhere, copy or duplicate data through these helpers, and receive `-EFAULT`/ERR_PTR on bad memory or `-ENOMEM` on allocation failure.

State/persistence: No persistent state; the wrapper carries a pointer and `is_kernel` tag by value. Duplicated buffers persist until the caller frees them.

Dependencies/integration: Depends on memory management allocation helpers, `sockptr_t`, user access helpers, `copy_from_kernel_nofault()`, and BPF syscall argument parsing.

Risks/test signals: Risks include accidentally tagging user pointers as kernel, pointer arithmetic overflow, missing size validation before duplication, and treating nofault kernel copies as normal trusted loads. Test signals include BPF syscall tests for kernel/user attr paths, fault-injection for bad user pointers, KASAN/KMSAN usercopy checks, zero-length/null-pointer cases, and string-copy boundary tests.
