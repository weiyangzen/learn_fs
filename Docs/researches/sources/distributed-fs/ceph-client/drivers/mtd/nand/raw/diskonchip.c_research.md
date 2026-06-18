# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/diskonchip.c

## Purpose
Implements the legacy M-Systems DiskOnChip 2000, Millennium, and Millennium Plus raw NAND driver. It probes fixed physical memory windows or a configured address, identifies DiskOnChip ASIC variants, exposes them through the raw NAND/MTD stack, and performs DiskOnChip-specific ECC, bad-block-table, NFTL, and INFTL media-header handling.

## Important APIs, Types, And Functions
`struct doc_priv` embeds `nand_controller` state plus mapped I/O address, chip/floor selection, detected geometry, media-header pages, Reed-Solomon decoder, and a `late_init()` callback. Module parameters control probing, debug output, 32-bit read probing, ECC failure suppression, automatic partitioning, firmware partition exposure, and writable INFTL BBTs. The controller hooks are `doc200x_exec_op()`, `doc2001plus_exec_op()`, and `doc200x_attach_chip()`. ECC is wired through `doc200x_enable_hwecc()`, `doc200x_calculate_ecc()`, `doc200x_correct_data()`, and `doc_ecc_decode()`, using the generic RS library with DiskOnChip syndrome conversion.

## Control Flow
`init_nanddoc()` probes either `doc_config_location` or platform address tables. `doc_probe()` reserves and maps the region, resets/enables the ASIC, checks chip ID and toggle behavior, filters aliases, allocates the NAND/private/BBT bundle, initializes RS decoding and NAND controller ops, then calls the variant initializer. `doc2000_init()`, `doc2001_init()`, and `doc2001plus_init()` select NFTL or INFTL late initialization and establish chip counts. After `nand_scan()`, `nftl_scan_bbt()` or `inftl_scan_bbt()` manually creates the BBT and registers MTD partitions built from media headers unless `no_autopart` is set.

## State And Persistence
Persistent flash state includes NFTL/INFTL media headers, BBT descriptors, optional writable INFTL BBT blocks, bad-block marks, and generated partitions. Runtime state is global through `doclist`, and per-device through selected floor/chip, current media-header pages, and ECC decoder state. Cleanup unregisters MTD devices, releases mappings/regions, frees RS codecs, and frees allocations.

## Dependencies And Integration Points
Depends on raw NAND, MTD partitions, `doc2000.h` register macros, `inftl.h` media structures, Linux I/O mapping, and Reed-Solomon library support. It integrates with `nand_scan()`, `nand_create_bbt()`, `mtd_device_register()`, legacy NAND ECC callbacks, and the modern `exec_op` instruction model.

## Risks
Probe writes to control registers before full identification and relies on old fixed memory maps. The code mutates NAND/MTD geometry after scan for NFTL virtual erase sizing, making it sensitive to NAND-core internal changes. ECC handling has a `no_ecc_failures` escape hatch that can hide corruption. Multi-floor INFTL is unsupported, Millennium Plus 32 MB is rejected, and OOB free regions are intentionally out of order for compatibility.

## Test Signals
Useful signals are successful probe messages, correct variant/chip-count detection, `nand_scan()` success, NFTL/INFTL media-header discovery, BBT creation, partition registration, ECC corrected/failed counters during page reads, alias-probe rejection of duplicate windows, and unload cleanup without resource leaks.
