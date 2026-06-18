## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hyp_image.h

Purpose: defines symbol and section naming helpers for KVM nVHE/hyp images.

Important APIs/types/functions: exports `kvm_nvhe_sym`, `HYP_SECTION_NAME`, `HYP_SECTION_SYMBOL_NAME`, `BEGIN_HYP_SECTION`, `END_HYP_SECTION`, `HYP_SECTION`, `KVM_NVHE_ALIAS`, and `KVM_NVHE_ALIAS_HYP`.

Control flow: assembler/linker macros place code/data into hyp sections and create aliases between kernel and hyp symbol namespaces.

State and persistence: affects link-time section layout and symbol aliases in the kernel/hyp images.

Dependencies and integration: used by KVM nVHE build, linker scripts, and hyp relocation/symbol access code.

Risks: wrong aliases or section boundaries break hyp text/data relocation and pKVM isolation. Test signals are KVM selftests, nVHE/pKVM boot, kallsyms/linker map inspection, and module-free allconfig builds.
