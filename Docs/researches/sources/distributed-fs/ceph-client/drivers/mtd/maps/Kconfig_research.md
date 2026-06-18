<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/Kconfig

Purpose: defines MTD map-driver configuration for physical, platform, PCI, PCMCIA, legacy board, SoC, and firmware-ROM mappings.

Important APIs, types, and functions: key symbols include `MTD_COMPLEX_MAPPINGS`, `MTD_PHYSMAP`, `MTD_PHYSMAP_OF`, `MTD_PHYSMAP_GPIO_ADDR`, platform add-ons `MTD_PHYSMAP_VERSATILE`, `MTD_PHYSMAP_GEMINI`, `MTD_PHYSMAP_IXP4XX`, and individual board/chipset drivers such as `MTD_AMD76XROM`, `MTD_ICHXROM`, `MTD_ESB2ROM`, `MTD_CK804XROM`, `MTD_PCMCIA`, `MTD_PCI`, `MTD_PLATRAM`, `MTD_PISMO`, and `MTD_LANTIQ`.

Control flow: menu visibility requires `MTD!=n` and `HAS_IOMEM`. Symbols select or depend on chip probe families, buses, architectures, OF, GPIO, syscon, PCI, or PCMCIA as needed. Compat options provide static physmap start/length/bankwidth, while OF/platform paths use runtime resources.

State and persistence: no runtime state; it controls compiled code and module availability.

Dependencies and integration points: ties map drivers to chip drivers (`MTD_CFI`, `MTD_JEDECPROBE`, `MTD_ROM`, `MTD_RAM`, `MTD_LPDDR`) and architecture/platform options.

Risks: many entries target legacy boards and BIOS flashing; incorrect enablement can expose writable firmware. Some compile paths depend on `MTD_COMPLEX_MAPPINGS` for custom map hooks. Test signals are Kconfig dependency resolution, module names matching help text, and build coverage for OF/platform/legacy combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/Kconfig -->
