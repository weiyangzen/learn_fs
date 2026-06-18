# sources/distributed-fs/ceph-client/drivers/mtd/parsers/bcm63xxpart.c

Purpose: Broadcom BCM63XX CFE partition parser that creates the top-level NOR layout around CFE, NVRAM, and the Linux firmware region.

Important APIs/types/functions: `bcm63xx_parse_cfe_partitions()` is the registered parser. `bcm63xx_detect_cfe()` verifies a CFE boot environment on MIPS by checking `fw_arg3 == CFE_EPTSEAL`. `bcm63xx_read_nvram()` reads and validates `struct bcm963xx_nvram` using `bcm963xx_nvram_checksum()`. `bcm63xx_parse_cfe_nor_partitions()` builds three partitions and marks `linux` with `types = { "bcm963xx-imagetag" }`.

Control flow: the parser rejects non-CFE boots, allocates an NVRAM buffer with `vzalloc()`, reads NVRAM at offset 0x580, warns on checksum mismatch, defaults missing PSI size, and only supports non-NAND devices. NOR partition creation rounds CFE and NVRAM sizes to at least 64 KiB erase alignment, creates `CFE` at offset 0, `nvram` at the end of flash, and `linux` spanning the remaining area. The `linux` partition is passed to the BCM963XX imagetag subparser.

State and persistence: persistent inputs are CFE boot ABI and NVRAM flash contents. The function does not modify flash; it only marks partition metadata. Runtime state is temporary NVRAM and allocated partition structures.

Dependencies and integration: depends on BCM963XX NVRAM/tag headers, MIPS CFE bootinfo when built for MIPS, MTD type helpers, and parser chaining to `bcm963xx-imagetag`. Risks include false negatives outside MIPS, unsupported NAND, invalid PSI sizes, and continued operation after NVRAM checksum warnings. Test signals include CFE/non-CFE boot simulation, bad checksum NVRAM, zero `psi_size`, erase-size rounding, NAND rejection, and validation that the `linux` partition invokes imagetag parsing.
