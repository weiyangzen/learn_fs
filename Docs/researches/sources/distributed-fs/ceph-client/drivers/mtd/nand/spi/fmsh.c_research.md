<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/fmsh.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/fmsh.c

Purpose: Fudan Micro/FMSH SPI NAND support for FM25S01A and FM25S01BI3.

Important APIs/types/functions: Defines manufacturer ID `0xa1`, common op variants, simple no-ECC-visible OOB layout for FM25S01A, 128-byte OOB layout for FM25S01BI3, `fm25s01bi3_ecc_get_status()`, tables, and `fmsh_spinand_manufacturer`.

Control flow: Core matches opcode-dummy IDs `0xe4` or `0xd4`, selects operation variants, enables quad for FM25S01BI3, installs per-chip OOB layout, and uses the custom BI3 ECC status mapper for corrected ranges 1-3, 4-6, 7-8, and uncorrectable errors.

State and persistence: Descriptor-only state. FM25S01A exposes the whole OOB after two BBM bytes as free with no visible ECC sections. FM25S01BI3 places ECC in bytes 64-127 and free data in four 12-byte regions.

Dependencies/integration: Uses SPI NAND core descriptor macros and MTD OOB layout callbacks. Manufacturer ID `0xa1` overlaps with Paragon, so matching relies on each manufacturer's table and ID method/device IDs.

Risks: Overlapping manufacturer ID can cause match-order sensitivity if future devices share IDs. FM25S01A has no custom ECC status callback; generic interpretation must be correct. The indented `#define` lines under the ECC mask are unusual style but preprocessor-valid.

Test signals: Probe both device IDs, verify OOB layout, corrected-bit ECC accounting for BI3 status values, quad-enable behavior for BI3, and conflict testing with Paragon IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/fmsh.c -->
