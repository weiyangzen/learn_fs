<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/userfaultfd.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/userfaultfd.h

Purpose: this header defines the userfaultfd ABI for userspace-managed page faults, write protection, minor faults, page movement, poisoning, and `/dev/userfaultfd` creation.

Important APIs/types: `UFFD_API`, feature masks, and ioctl bitmasks advertise available modes. Ioctls include API negotiation, register/unregister, wake, copy, zeropage, move, writeprotect, continue, and poison. `struct uffd_msg` defines read events for pagefault, fork, remap, remove, and unmap. `struct uffdio_api`, `uffdio_range`, `uffdio_register`, `uffdio_copy`, `uffdio_zeropage`, `uffdio_writeprotect`, `uffdio_continue`, `uffdio_poison`, and `uffdio_move` are the request/response structs.

Control flow: userspace creates a userfaultfd, negotiates `UFFDIO_API`, registers memory ranges, polls/reads `uffd_msg` events, resolves faults with copy/zeropage/continue/move/poison/writeprotect ioctls, and wakes waiting threads unless DONTWAKE is set.

State and persistence: registered ranges and enabled features persist while the fd and mappings exist. Ioctl result fields are intentionally at the end because the kernel writes them without reading them from userspace.

Dependencies/integration: depends on `linux/types.h`; used by live migration, post-copy VM migration, checkpoint/restore, memory managers, and fault-injection tests.

Risks and test signals: risks include feature negotiation mistakes, range alignment, wake semantics, async write-protection behavior, fork/remap/unmap event ordering, and security restrictions for kernel vs user-mode faults. Test all register modes, feature probes, short/failed ioctls, event delivery, and race handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/userfaultfd.h -->
