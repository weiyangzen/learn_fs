# sources/distributed-fs/ceph-client/drivers/mtd/parsers/redboot.c

Purpose: RedBoot FIS partition parser. It reads the Flash Image System directory and converts image descriptors into sorted MTD partitions.

Important APIs/types/functions: `parse_redboot_partitions()` is the parser entry and module alias `RedBoot`. `struct fis_image_desc` models the 256-byte RedBoot descriptor. `parse_redboot_of()` optionally overrides the module `directory` block using `fis-index-block`. `redboot_checksum()` currently accepts all descriptors.

Control flow: it chooses the FIS directory eraseblock from the configured index, supporting negative indexes from the end and skipping bad blocks. It reads one eraseblock into a vmalloc buffer, locates the `FIS directory` descriptor, detects byte-swapped tables, updates slot count from descriptor size, and optionally byte-swaps all entries. It builds a sorted linked list by `flash_base`, adjusting origin from parser data or masking by device size. It then allocates partition structs plus names, optionally inserts `unallocated` gaps, marks RedBoot/config/FIS directory read-only when configured, and frees the temporary list and buffer.

State and persistence: persistent state is the RedBoot FIS table in flash and optional DT/module directory setting. Runtime state is a vmalloc directory buffer, linked list, and returned partition array. No flash writes occur.

Dependencies and integration: depends on MTD bad-block handling, OF, Kconfig options for read-only and unallocated gaps, and parser origin data. Risks include accepting unchecked descriptors, global mutable `directory`, endian heuristic mistakes, name `strlen()` on corrupt non-terminated data, and gap math tied to eraseblock size. Test signals include positive/negative directory indexes, bad block skipping, swapped and native tables, deleted/end markers, origin adjustment, unallocated gaps, read-only config, and no-table returns.
