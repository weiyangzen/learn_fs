# sources/distributed-fs/ceph-client/drivers/mtd/maps/scx200_docflash.c

Purpose: NatSemi SCx200 DOCCS flash map driver. It either probes an existing BIOS mapping or allocates/programs a DOCCS memory aperture, sets 8/16-bit width, probes the requested flash type, and registers four boot/BIOS/filesystem partitions.

Important APIs/types/functions: module parameters `probe`, `size`, `width`, `flashtype`; `docmem`; `scx200_docflash_map`; `init_scx200_docflash()`; `cleanup_scx200_docflash()`. It depends on PCI bridge discovery, `scx200_cb_present()`, SCx200 DOCCS config registers, PMR width bit, `allocate_resource()` or `request_resource()`, `ioremap()`, `do_map_probe()`, and static MTD partitions.

Control flow: init locates the SCx200 bridge and config block. In probe mode it validates an existing base/control mapping, checks power-of-two size, infers width, and reserves the resource. In setup mode it validates parameters, allocates a high memory region, writes DOCCS base/control, and updates PMR width. It maps the aperture, probes `flashtype`, derives high-BIOS and filesystem partition bounds from detected size, and registers partitions. Cleanup unregisters/destroys and releases mappings/resources.

State and persistence: module parameters drive hardware configuration. DOCCS base/control and PMR writes alter chipset state. Partition boundaries depend on detected MTD size at runtime.

Risks and test signals: `docmem.end = base + size` is inclusive-style suspicious compared with common `end = start + size - 1`. Invalid non-power-of-two sizes are rejected. Tests should cover probe/setup modes, width validation, resource conflicts, mapping smaller than flash warning, partition size calculation, and cleanup after probe failure.
