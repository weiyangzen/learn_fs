<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vermagic.h

Purpose: adds LoongArch-specific feature strings to module version magic.
Important APIs and types: defines `MODULE_PROC_FAMILY`, page-size/module ABI fragments, and final vermagic suffixes based on CPU/configuration.
Control flow: module build embeds these strings; module loader compares them when loading modules.
State and persistence: vermagic becomes persistent metadata in built kernel modules.
Dependencies and integration: integrates with module loader ABI checks, CPU family/page-size configuration, and kernel build system.
Risks and test signals: missing ABI-affecting flags can allow incompatible modules; excessive flags reject valid modules. Signals include module load tests across page-size/config variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vermagic.h -->
