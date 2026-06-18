# sources/distributed-fs/ceph-client/drivers/pci/rom.c

Purpose: Provides PCI expansion ROM access helpers. It enables and disables ROM decoding, maps the ROM BAR into kernel virtual address space, determines the real image length inside the resource window, and unmaps/restores decode state.

Important APIs and functions: Exports `pci_enable_rom()`, `pci_disable_rom()`, `pci_map_rom()`, and `pci_unmap_rom()`. The internal `pci_get_rom_size()` parser walks one or more PCI ROM images using the `0xaa55` ROM header signature, the `PCIR` data structure signature, the image length field, and the last-image bit.

Control flow: `pci_enable_rom()` rejects devices without a ROM resource, no-ops for shadow ROM copies, converts the kernel resource to bus coordinates, preserves non-address bits from `pdev->rom_base_reg`, writes the ROM base address plus `PCI_ROM_ADDRESS_ENABLE`, and returns success. `pci_map_rom()` assigns the ROM resource if needed, reads start and length, enables decoding, `ioremap()`s the window, shrinks `*size` to the parsed image length, and unwinds on map or validation failure. `pci_unmap_rom()` unmaps the address and disables decoding unless the resource was already marked enabled by the caller or platform.

State and persistence: Mutates the ROM BAR enable bit and possibly the ROM BAR address in PCI config space. It may trigger resource assignment for `PCI_ROM_RESOURCE`. The returned mapping is temporary kernel virtual state owned by the caller until `pci_unmap_rom()`. Shadow ROM resources are treated as already accessible RAM and do not change hardware decode bits.

Dependencies and integration points: Depends on PCI resource helpers, bus/resource address translation, `pci_assign_resource()`, config-space accessors, `ioremap()`/`iounmap()`, and endian-safe MMIO reads. It is used by PCI drivers and core paths that need firmware ROM contents, option ROMs, or video BIOS data while preserving device decode behavior.

Risks: Enabling ROM decoding can disable access to other MMIO regions on devices with shared decoders, as the file comment warns. Some devices report buggy disabled ROM BAR values, so the helper rewrites the address while enabling. `pci_get_rom_size()` trusts only bounded parsing and clamps to the resource window because ROM length fields can be wrong. Callers must always pair successful maps with `pci_unmap_rom()` and must not assume the resource window length equals image length.

Test signals: ROM read tests on devices with real ROM BARs and shadow ROMs, invalid-signature handling, multi-image ROM parsing, failure unwinding when assignment or mapping fails, preservation of caller-enabled ROM state, and driver flows that copy or inspect option ROM data without losing MMIO access after unmap.
