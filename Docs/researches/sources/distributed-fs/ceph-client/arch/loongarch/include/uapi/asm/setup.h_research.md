<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/setup.h

Purpose: defines LoongArch userspace-visible setup constants.
Important APIs and types: sets `COMMAND_LINE_SIZE` to 4096.
Control flow: boot and tooling use this compile-time size for command-line buffers.
State and persistence: constant is ABI-adjacent for boot interfaces and tools.
Dependencies and integration: used by boot protocol, procfs command-line exposure, and userspace header consumers.
Risks and test signals: mismatched sizes truncate or overread command lines. Signals include boot with long command lines and headers_check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/setup.h -->
