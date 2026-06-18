<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/vbios_quirk.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/vbios_quirk.c

Purpose: Supplies a PCI fixup for ATI VGA devices whose ROM is shadowed by Loongson firmware rather than exposed in the PCI ROM BAR.

Important APIs/types/functions: `pci_fixup_video(struct pci_dev *pdev)` and `DECLARE_PCI_FIXUP_CLASS_HEADER()` for ATI device 0x9615 VGA class.

Control flow: If the ROM resource is empty and firmware provided `vgabios_addr`, disables PCI ROM decoding, releases any parent resource, and fills the ROM resource with the physical shadowed VBIOS address, fixed 256 KiB size, and fixed/shadow flags.

State and persistence: Mutates the PCI device ROM resource during header fixup.

Dependencies and integration: Uses `loongson_sysconf.vgabios_addr` from LEFI parsing and generic PCI quirk infrastructure.

Risks: Assumes shadowed VBIOS size is 256 KiB and address is valid. Only covers one ATI device ID.

Test signals: Affected VGA device should log a shadowed ROM resource and userspace should be able to read the ROM through PCI sysfs/resource paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/vbios_quirk.c -->
