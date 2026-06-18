# sources/distributed-fs/ceph-client/tools/include/uapi/linux/memfd.h

Purpose: defines flags for `memfd_create(2)`, controlling close-on-exec, sealing, hugetlb backing, executable policy, and huge-page size selection.

Important APIs/types: flags include `MFD_CLOEXEC`, `MFD_ALLOW_SEALING`, `MFD_HUGETLB`, `MFD_NOEXEC_SEAL`, and `MFD_EXEC`. Huge-page selectors are aliases to `HUGETLB_FLAG_ENCODE_*` values for 64KB through 16GB pages. There are no structs or functions.

Control flow, state, and persistence: userspace calls `memfd_create(name, flags)`. Kernel creates an anonymous file descriptor with the requested sealing/exec/hugetlb behavior. State persists in the anonymous file and seals until all fds are closed; hugetlb allocation consumes persistent kernel memory resources while live.

Dependencies and integration points: depends on `<asm-generic/hugetlb_encode.h>`. Integrates shared-memory IPC, sealed blobs, executable loaders, sandboxing, guest-memory backends, and hugetlbfs.

Risks and test signals: risks include incompatible exec flags, missing `MFD_ALLOW_SEALING` before adding seals, hugetlb privilege/resource failures, and huge page size unsupported by the host. Tests should create memfds with sealing and exec variants, add seals, mmap/exec where permitted, allocate hugetlb sizes, and validate error returns for unsupported flag combinations.
