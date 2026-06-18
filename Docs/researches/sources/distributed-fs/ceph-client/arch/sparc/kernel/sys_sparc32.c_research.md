# sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc32.c

Purpose: implements sparc64 compat syscall wrappers where 32-bit user ABI argument and structure layouts differ from native 64-bit kernel APIs.

Important APIs/types/functions: defines compat syscalls for `truncate64`, `ftruncate64`, `stat64`, `lstat64`, `fstat64`, `fstatat64`, `sparc_sigaction`, `rt_sigaction`, `pread64`, `pwrite64`, `readahead`, `fadvise64`, `fadvise64_64`, `sync_file_range`, and `fallocate`. `cp_compat_stat64()` converts `struct kstat` to `struct compat_stat64`.

Control flow: most wrappers combine high/low 32-bit words into 64-bit offsets or lengths, then call `ksys_*` helpers. Stat wrappers query VFS into `kstat` then copy fields, encoded devices, munged UID/GID, timestamps, and padding to user memory. Signal-action wrappers convert handler/restorer pointers and compat sigsets before/after `do_sigaction()`.

State and persistence: no owned state. It reads kernel file/stat/signal data and writes user buffers. File size operations persist through VFS helpers, not this conversion layer.

Dependencies and integration points: connects 32-bit syscall table entries to generic VFS, signal, and syscall helper APIs; depends on `compat_stat64`, `compat_sigaction`, and SPARC signal ABI.

Risks: high/low word ordering and sign/zero extension are ABI-critical. `cp_compat_stat64()` must keep padding and timestamp layout compatible with old userspace. Signal numbers are negated for legacy SPARC `sparc_sigaction` convention.

Test signals: 32-bit stat family ABI tests, large-file truncate/ftruncate/pread/pwrite/fallocate, `rt_sigaction` with compat masks/restorer, and fault injection on user-copy failures.
