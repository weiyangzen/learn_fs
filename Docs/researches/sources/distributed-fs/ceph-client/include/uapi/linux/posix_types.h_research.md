<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/posix_types.h

Purpose: provides generic Linux POSIX type declarations and includes architecture-specific type definitions needed by UAPI headers.

Important APIs and types: the header defines the `__FD_SETSIZE` baseline, `__kernel_fd_set`, `__kernel_sighandler_t`, `__kernel_key_t`, and `__kernel_mqd_t`, then includes `<asm/posix_types.h>` for architecture-width types such as inode, mode, pid, uid, gid, clock, and time representations.

Control flow: there is no runtime control flow. It is a foundational compile-time include used by many exported headers to stabilize type names.

State and persistence: no state is stored. ABI persistence is the stable size and signedness of exported POSIX scalar types per architecture.

Dependencies and integration points: depends on `linux/stddef.h` and arch UAPI `asm/posix_types.h`; integrates broadly with syscall structs, libc, filesystem, process, time, and socket ABIs.

Risks and test signals: risks include architecture type width drift, fd-set size assumptions, and userspace/libc redefinition conflicts. Test exported headers with `make headers_install`, cross-architecture compile checks, and ABI comparison tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_types.h -->
