# sources/distributed-fs/ceph-client/arch/powerpc/mm/maccess.c

Purpose: defines the PowerPC policy for `copy_from_kernel_nofault()` source validation.

Important APIs and control flow: `copy_from_kernel_nofault_allowed()` returns true only when the source pointer is a kernel address according to `is_kernel_addr()`. There is no page-table walk or exception handling here; generic nofault copy machinery performs the guarded access later.

State and dependencies: no persistent state. It depends on PowerPC address classification helpers and generic `uaccess`/nofault copy infrastructure. Risks are policy mismatch with special kernel mappings that are not classified as kernel addresses, or allowing aliases that should not be inspected. Test signals include nofault copy tests from kernel, user, vmalloc, ioremap, and invalid addresses, plus callers such as probes and diagnostics that rely on graceful failure.
