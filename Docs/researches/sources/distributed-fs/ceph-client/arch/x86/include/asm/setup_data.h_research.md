<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/setup_data.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/setup_data.h

Purpose: extends UAPI setup-data records with kernel-only x86 boot payload structures. Important types are `pci_setup_rom` for PCI option ROM handoff and `efi_setup_data` for EFI setup information.

Control flow: early boot walks the setup_data linked list from boot params and interprets records by type, including PCI ROM and EFI data. State is bootloader-provided memory consumed during boot and not persistent after initialization.

Dependencies include UAPI setup_data layout, PCI, EFI, and bootloader contracts. Risks are packed layout/width mismatches with bootloaders and wrong physical-address handling. Test signals include EFI boots, kexec with setup_data, PCI ROM handoff tests, and boot parameter parser coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/setup_data.h -->
