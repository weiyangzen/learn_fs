<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_efi.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_efi.c

Purpose: prepares EFI-specific metadata for kexec on LoongArch.
Important APIs and types: implements helpers to pass EFI system table, memory map, and boot parameters to a kexec target kernel.
Control flow: kexec file load/build code invokes EFI helpers to construct the target boot parameter block and preserve runtime information.
State and persistence: generated handoff metadata persists until the new kernel boots.
Dependencies and integration: depends on EFI table parsing, kexec image loading, memblock/memory map data, and LoongArch boot protocol.
Risks and test signals: incomplete EFI handoff breaks second-kernel EFI/runtime behavior. Signals include kexec boot from EFI, kdump under EFI, and runtime service checks after kexec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kexec_efi.c -->
