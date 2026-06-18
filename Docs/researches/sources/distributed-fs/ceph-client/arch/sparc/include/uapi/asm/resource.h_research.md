<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/resource.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/resource.h

Purpose: SPARC resource-limit constants and compatibility values.

Important APIs and control flow: preserves SPARC-specific ordering for `RLIMIT_NOFILE` and `RLIMIT_NPROC`. On 32-bit SPARC, `RLIM_INFINITY` remains the old signed-compatible `0x7fffffff`; other definitions come from `asm-generic/resource.h`.

State, dependencies, and risks: state is process rlimit values exchanged through getrlimit/setrlimit. Dependencies include generic resource UAPI and libc. Risks are ABI ordering differences from other architectures and infinity value compatibility. Test signals are rlimit syscall tests on 32-bit and 64-bit SPARC and libc constant checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/resource.h -->
