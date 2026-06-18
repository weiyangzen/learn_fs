<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.c

Purpose: IXP4xx-specific physmap add-on that corrects expansion-bus endianness/address coherency for 16-bit flash.

Important APIs, types, and functions: `flash_read16()` and `flash_write16()` abstract big- vs little-endian behavior. Custom map hooks are `ixp4xx_read16()`, `ixp4xx_copy_from()`, and `ixp4xx_write16()`. `of_flash_probe_ixp4xx()` installs them for `intel,ixp4xx-flash`.

Control flow: for non-IXP4xx nodes the helper returns 0. For matching nodes, it sets custom 16-bit read/write/copy-from operations and leaves `copy_to` NULL because command writes use 16-bit access. Little-endian systems XOR address bit 1 and byte-swap words to undo CPU/expansion-bus swizzling; `ixp4xx_copy_from()` reconstructs byte streams from 16-bit reads including unaligned starts.

State and persistence: no private persistent state; only map function pointers are changed.

Dependencies and integration points: physmap OF path, MTD map APIs, CPU endian config, and `CONFIG_MTD_CFI_BE_BYTE_SWAP` when little-endian CFI data needs unswapping.

Risks: bank width is assumed to match 16-bit access. Missing or wrong byte-swap config can corrupt command/data interpretation. Test signals are byte-accurate reads at odd/even offsets, CFI probe success on little- and big-endian IXP4xx, and write command placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.c -->
