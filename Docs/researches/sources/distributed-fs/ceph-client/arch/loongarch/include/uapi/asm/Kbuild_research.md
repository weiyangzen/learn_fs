<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/Kbuild

Purpose: controls which LoongArch UAPI asm headers are generated or exported to userspace.
Important APIs and types: lists generic-y/generated-y header mappings for the UAPI install step.
Control flow: Kbuild consumes this during `headers_install`; there is no runtime path.
State and persistence: installed header set becomes userspace ABI distribution state.
Dependencies and integration: integrates with kernel UAPI header installation, libc header generation, and syscall-number generation.
Risks and test signals: missing headers break userspace builds; exporting wrong generated headers causes ABI drift. Signals include `make headers_check` and libc/toolchain header builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/Kbuild -->
