# sources/distributed-fs/ceph-client/lib/raid6/loongarch.h

Purpose: provides shared LoongArch RAID6 SIMD definitions for kernel and userspace test builds.

Important APIs and flow: in-kernel builds include CPU feature and FPU helpers. Userspace builds define HWCAP values if needed, no-op `kernel_fpu_begin/end`, and map `cpu_has_lsx/lasx` to `getauxval(AT_HWCAP)`.

State and persistence: no persistent state.

Dependencies and integration: included by LoongArch syndrome and recovery SIMD files.

Risks and test signals: userspace compatibility macros must match kernel feature semantics. Signals include kernel builds and standalone RAID6 test builds on glibc/musl LoongArch systems.
