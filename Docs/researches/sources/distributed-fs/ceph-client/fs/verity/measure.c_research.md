<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/measure.c -->
# sources/distributed-fs/ceph-client/fs/verity/measure.c

Purpose: Implements APIs for retrieving the digest of a verity file through ioctl, internal kernel callers, and optional BPF LSM kfuncs.

Important APIs, types, and functions: Exports `fsverity_ioctl_measure()` and `fsverity_get_digest()`. Under `CONFIG_BPF_SYSCALL`, defines `bpf_get_fsverity_digest()`, BTF kfunc id sets, filter `bpf_get_fsverity_digest_filter()`, and `fsverity_init_bpf()`.

Control flow: The ioctl requires existing `fsverity_info`, reads the caller-provided digest buffer size, rejects undersized buffers with `-EOVERFLOW`, writes the algorithm and digest size, then copies the cached file digest. `fsverity_get_digest()` returns zero for non-verity files or copies raw digest plus fs-verity and/or generic hash algorithm ids. The BPF kfunc validates dynptr size, alignment, and LSM program type, then writes as much digest as fits and zero-fills extra space.

State and persistence: Reads only cached `fsverity_info->file_digest`. No filesystem metadata is modified.

Dependencies and integration points: Used by userspace `FS_IOC_MEASURE_VERITY`, IMA/LSM-style kernel consumers, and optional BPF LSM programs. Depends on `fsverity_get_info()`, user copy helpers, BPF dynptr internals, and BTF kfunc registration.

Risks and test signals: Risks include returning a digest without an algorithm id, buffer-size ABI mistakes, BPF dynptr alignment bugs, and stale zero result before a verity inode has been opened and info cached. Test ioctl on non-verity and verity files, undersized and oversized buffers, SHA-256/SHA-512 files, kernel `fsverity_get_digest()` callers, and BPF LSM kfunc access filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/measure.c -->
