# sources/distributed-fs/ceph-client/include/uapi/linux/userfaultfd.h

Purpose: Defines the userfaultfd UAPI for userspace page-fault handling, memory migration, write protection, minor-fault resolution, poisoning, and related virtual-memory events.

Important APIs/types/functions: `USERFAULTFD_IOC_NEW` creates fds via `/dev/userfaultfd`; `UFFD_API` identifies the negotiated API. Feature masks advertise pagefault write-protect flag, fork/remap/remove/unmap events, hugetlbfs/shmem missing and minor faults, SIGBUS mode, thread ID, exact address, WP on hugetlbfs/shmem/unpopulated, poison, async WP, and move. Ioctls include API negotiation, register/unregister, wake, copy, zeropage, move, writeprotect, continue, and poison. `struct uffd_msg` is read from the fd for pagefault/fork/remap/remove/unmap events. Request structs include `uffdio_api`, `uffdio_range`, `uffdio_register`, `uffdio_copy`, `uffdio_zeropage`, `uffdio_writeprotect`, `uffdio_continue`, `uffdio_poison`, and `uffdio_move`. `UFFD_USER_MODE_ONLY` restricts faults to user-mode.

Control flow: Userspace creates a userfaultfd, negotiates features with `UFFDIO_API`, registers address ranges and modes, polls/reads events, resolves missing faults with copy/zeropage, resolves minor faults with continue, manages write-protection, wakes waiters, poisons ranges, or moves page contents. Event flags distinguish write, write-protect, and minor faults.

State and persistence behavior: Registered ranges and feature negotiation live on the userfaultfd and target mm lifetime. Page contents, write-protection state, poison markers, and moved pages persist in the process address space until changed.

Dependencies and integration points: Includes `linux/types.h`; integrates with `userfaultfd(2)`, `/dev/userfaultfd`, memory management, shmem, hugetlbfs, live migration, post-copy VM migration, garbage collectors, checkpoint/restore, and sandboxing.

Risks: Deadlocks are possible if the fault handler faults on registered memory or fails to wake waiters. Feature negotiation must be honored before using ioctls. DONTWAKE, WP async, move, poison, and exact-address semantics are subtle. Return fields at the end of structs are kernel-written and intentionally not read by `copy_from_user`.

Test signals: Run kernel userfaultfd selftests for missing, WP, minor, shmem, hugetlbfs, fork/remap/remove/unmap, SIGBUS, thread ID, exact address, async WP, poison, move, unregister/wake, and `/dev/userfaultfd` creation with `UFFD_USER_MODE_ONLY`.
