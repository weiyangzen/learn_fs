<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/signal.h

Purpose: defines LoongArch signal stack sizing and imports generic signal ABI definitions.
Important APIs and types: sets `MINSIGSTKSZ` to 4096 and `SIGSTKSZ` to 16384 before including `asm-generic/signal.h`.
Control flow: userspace libraries use these constants for alternate signal stack sizing; kernel signal code enforces stack layout indirectly.
State and persistence: constants are userspace ABI expectations.
Dependencies and integration: tied to signal frame size, extended FPU/vector contexts, libc, and sigaltstack.
Risks and test signals: undersized values cause signal delivery failures with large contexts. Signals include sigaltstack tests with LSX/LASX/LBT state and libc header checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/signal.h -->
