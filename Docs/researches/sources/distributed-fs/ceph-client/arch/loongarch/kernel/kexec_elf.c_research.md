<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_elf.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_elf.c

Purpose: handles ELF image loading details for LoongArch kexec.
Important APIs and types: implements architecture ELF kexec probe/load helpers, segment placement, and entry/boot argument preparation.
Control flow: kexec file loader validates the ELF image, maps/load segments, prepares control data, and records the target entry point.
State and persistence: kexec image metadata and loaded segments persist until reboot into the new kernel.
Dependencies and integration: integrates with generic kexec_file, ELF parser, crash kernel, EFI handoff, and low-level relocation/reboot code.
Risks and test signals: segment placement or entry mistakes fail kexec or crash kernels. Signals include normal kexec, kdump, signed image loading where enabled, and memory-range validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_elf.c -->
