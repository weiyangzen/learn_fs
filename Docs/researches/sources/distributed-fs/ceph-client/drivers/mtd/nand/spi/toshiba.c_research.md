<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/toshiba.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/toshiba.c

Purpose: Toshiba/Kioxia SPI NAND support for TC58/TH58 CVG/CYG/NYG families.

Important APIs/types/functions: Defines manufacturer ID `0x98`, cache operation variants, `tx58cxgxsxraix_ooblayout_ecc()`, `tx58cxgxsxraix_ooblayout_free()`, `tx58cxgxsxraix_ecc_get_status()`, a broad `toshiba_spinand_table`, and `toshiba_spinand_manufacturer`.

Control flow: Core matches Toshiba IDs across 1.8V/3.3V and different capacity variants, installs the Toshiba OOB layout, enables quad where table flags request it, and maps ECC status. Status with normal corrected bitflips returns ECC strength, threshold status returns bitflip threshold, and uncorrectable returns `-EBADMSG`.

State and persistence: No private runtime state. Table entries encode page/OOB sizes, blocks, LUNs, and ECC requirements for multiple generations. OOB layout uses per-section ECC and free regions tailored to Toshiba spare layout.

Dependencies/integration: Descriptor-only SPI NAND integration through core manufacturer array and MTD OOB layout callbacks.

Risks: Many table entries are near-duplicates, making geometry or ID mistakes likely during maintenance. Returning threshold/strength rather than exact corrected counts is conservative but less precise. Different voltage families must not be confused in board validation.

Test signals: Probe representative CVG/CYG/NYG parts, confirm page/OOB/size reporting, ECC status threshold handling, OOB free/ECC regions, quad operation selection, and boot filesystems such as UBI on corrected-bitflip media.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/toshiba.c -->
