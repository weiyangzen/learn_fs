# sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/wrappers.h

Purpose: Provides a tiny compatibility wrapper for the `listns` namespace syscall used by namespace selftests. The file exists so tests can call a stable `sys_listns()` helper even when the userspace syscall number header does not yet define `__NR_listns`.

Important APIs/types/functions: Includes `<linux/nsfs.h>` for `struct ns_id_req`, `<linux/types.h>` for `__u64`, and syscall headers. It conditionally defines `__NR_listns` for alpha, MIPS o32/n32/n64, and default architectures, then exposes `static inline int sys_listns(const struct ns_id_req *req, __u64 *ns_ids, size_t nr_ns_ids, unsigned int flags)`.

Control flow: There is no runtime branching beyond the syscall itself. Compile-time preprocessor logic selects the numeric syscall constant, and `sys_listns()` forwards all arguments to `syscall(__NR_listns, ...)`.

State and persistence behavior: The wrapper owns no state. Any persistence is in kernel namespace state returned by the syscall into the caller-provided `ns_ids` buffer.

Dependencies and integration points: Depends on kernel UAPI types and libc `syscall()`. Integrated by namespace selftests that need to exercise new syscall behavior before all libc/kernel header combinations expose the number.

Risks: Hard-coded syscall numbers are architecture-sensitive; stale numbers would make tests fail with wrong syscalls or `ENOSYS`. The default number assumes most supported architectures use 470. It has no runtime feature detection.

Test signals: Successful consumers can compile without `__NR_listns` from libc and receive kernel return values from `listns`. Failures usually appear as build errors for missing `struct ns_id_req` or runtime syscall errors.
