# subset-b-005894 Research

Grouped research for MTD headers under `sources/distributed-fs/ceph-client/include/linux/mtd`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/doc2000.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/doc2000.h

## Purpose

Defines the private register map, chip IDs, access helpers, and core data structures for legacy M-Systems DiskOnChip 2000/Millennium/Millennium Plus NAND-like devices.

## Important APIs, Types, and Functions

Important exports are the `ReadDOC()`/`WriteDOC()` register helpers, `struct Nand`, `struct DiskOnChip`, chip/floor limits, address-mode constants, ECC control bits, and `doc_decode_ecc()` for 512-byte-sector ECC syndrome decoding.

Source-visible symbols include structs: `struct Nand`, `struct DiskOnChip`, `struct Nand *chips;`, `struct mtd_info *nextdoc;`, `struct mutex lock;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `return __raw_readl(addr + reg);`, `return __raw_readw(addr + reg);`, `int doc_decode_ecc(unsigned char sector[512], unsigned char ecc1[6]);`; representative macros: `__MTD_DOC2000_H__`, `DoC_Sig1`, `DoC_Sig2`, `DoC_ChipID`, `DoC_DOCStatus`, `DoC_DOCControl`, `DoC_FloorSelect`, `DoC_CDSNControl`, `DoC_CDSNDeviceSelect`, `DoC_ECCConf`, `DoC_2k_ECCStatus`, `DoC_CDSNSlowIO`, `DoC_ECCSyndrome0`, `DoC_ECCSyndrome1`, `DoC_ECCSyndrome2`, `DoC_ECCSyndrome3`.

## Control Flow

Driver code selects the architecture-specific MMIO accessor, then writes DiskOnChip control registers such as `DOCControl`, `CDSNControl`, `FloorSelect`, and `CDSNDeviceSelect` to choose floor/chip, command/address/data mode, write protect, and ECC state. The `DiskOnChip` object tracks current floor/chip and serializes operations with its mutex.

## State and Persistence Behavior

Runtime state is controller-local: mapped physical/virtual base addresses, detected chip ID, geometry, per-chip `curadr` and `curmode`, current floor/chip selection, and a linked list of detected devices. Persistence is on flash only; this header does not define file-backed metadata.

## Dependencies and Integration Points

It depends on MTD core types and mutexes, and on Linux MMIO helpers selected by architecture. It integrates with the DiskOnChip MTD driver and the NAND translation layers that consume the exposed `mtd_info`.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`, `#include <linux/mutex.h>`.

## Risks and Edge Cases

The main risks are stale support for unusual bus widths, architecture-specific raw access differences, floor/chip selection races if callers bypass the mutex, and ECC decode assumptions fixed to 512-byte sectors.

## Test Signals

Useful signals are build coverage on ARM/PPC/generic access paths, probe tests for each chip ID, register trace validation for floor/chip selection, and ECC fixtures that cover clean, corrected, and uncorrectable sectors.

Source read signal: 206 lines, 5505 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/doc2000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/flashchip.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/flashchip.h

## Purpose

Provides common NOR/OneNAND-style flash-chip state tracking used by map and chip drivers while erase, write, suspend, sync, lock, and XIP operations are in flight.

## Important APIs, Types, and Functions

Key types are `flstate_t`, `struct flchip`, and `struct flchip_shared`. The state enum unifies historical NOR, NAND, and OneNAND operation states such as `FL_READY`, `FL_ERASING`, `FL_WRITING`, `FL_PM_SUSPENDED`, `FL_READING`, and `FL_CACHEDPRG`.

Source-visible symbols include structs: `struct flchip`, `struct mutex mutex;`, `struct flchip_shared`, `struct mutex lock;`, `struct flchip *writing;`, `struct flchip *erasing;`; enums: none visible in this header; typedefs: `typedef enum {`; prototypes: none visible in this header; representative macros: `__MTD_FLASHCHIP_H__`.

## Control Flow

Chip drivers change `flchip.state` while holding `flchip.mutex`, sleep on `flchip.wq` while another operation owns the device, and use `flchip_shared` to prevent write/erase contention across partitions that address the same physical chip.

## State and Persistence Behavior

All state is volatile kernel state: current and old operation state, suspend bits, in-progress block address/mask, timing estimates, point-reference counts, and driver private data.

## Dependencies and Integration Points

It depends on scheduler, mutex, and waitqueue primitives. Integration points are CFI/JEDEC map drivers, LPDDR/PFOW code, and OneNAND code that share the same state vocabulary.

Direct includes observed in the source are: `#include <linux/sched.h>`, `#include <linux/mutex.h>`, `#include <linux/wait.h>`.

## Risks and Edge Cases

Incorrect state transitions can deadlock waiters, permit erase/write overlap across partitions, or resume the wrong suspended operation. Timing fields are policy inputs and must match actual device behavior closely enough for robust wait logic.

## Test Signals

Stress read/write/erase/suspend/resume paths, partition contention, point/unpoint reference accounting, and shutdown/unload transitions.

Source read signal: 100 lines, 2502 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/flashchip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/ftl.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/ftl.h

## Purpose

Defines the on-media erase unit header and block allocation bit encodings for the historical Flash Translation Layer format.

## Important APIs, Types, and Functions

The central type is `erase_unit_header_t`; macros decode erase-unit flags and Block Allocation Information words with `BLOCK_FREE()`, `BLOCK_DELETED()`, `BLOCK_TYPE()`, `BLOCK_ADDRESS()`, and block type constants.

Source-visible symbols include structs: none visible in this header; enums: none visible in this header; typedefs: `typedef struct erase_unit_header_t {`; prototypes: none visible in this header; representative macros: `_LINUX_FTL_H`, `HIDDEN_AREA`, `REVERSE_POLARITY`, `DOUBLE_BAI`, `BLOCK_FREE`, `BLOCK_DELETED`, `BLOCK_TYPE`, `BLOCK_ADDRESS`, `BLOCK_NUMBER`, `BLOCK_CONTROL`, `BLOCK_DATA`, `BLOCK_REPLACEMENT`, `BLOCK_BAD`.

## Control Flow

FTL mount/format code reads erase-unit headers from flash, interprets tuple fields and BAM offsets, then classifies block mappings using the macros in this header.

## State and Persistence Behavior

The header describes persistent flash metadata: erase counts, logical erase-unit numbers, formatted size, alternate header offset, BAM offset, flags, serial number, and block-state words.

## Dependencies and Integration Points

It relies on fixed-width integer types and is consumed by the FTL block translation implementation.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Endian/layout drift would corrupt format interpretation. The macros assume exact legacy bit encodings; accepting partially erased or power-failed BAM words needs defensive callers.

## Test Signals

Use golden FTL images with free, deleted, control, data, replacement, and bad block entries, plus malformed erase-unit headers.

Source read signal: 74 lines, 2551 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/ftl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/gen_probe.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/gen_probe.h

## Purpose

Defines the generic map-chip probe shim used to connect CFI/JEDEC probe implementations with the MTD map infrastructure.

## Important APIs, Types, and Functions

Important interfaces are `struct chip_probe` with a `probe_chip()` callback and `mtd_do_chip_probe()` returning an `mtd_info` for a `map_info`.

Source-visible symbols include structs: `struct chip_probe`, `struct mtd_info *mtd_do_chip_probe(struct map_info *map, struct chip_probe *cp);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_GEN_PROBE_H__`.

## Control Flow

The generic probe walks candidate map bases, records chip presence in a chip bitmap, fills CFI private data, then hands the recognized map to a chip driver.

## State and Persistence Behavior

Probe state is transient and held in caller-provided `chip_map` and `cfi_private` data. No persistent state is introduced.

## Dependencies and Integration Points

It includes `flashchip.h`, `map.h`, `cfi.h`, and bit operations; integration is with `do_map_probe()` and CFI/JEDEC probe modules.

Direct includes observed in the source are: `#include <linux/mtd/flashchip.h>`, `#include <linux/mtd/map.h>`, `#include <linux/mtd/cfi.h>`, `#include <linux/bitops.h>`.

## Risks and Edge Cases

Incorrect base/chip-map accounting can double-detect interleaved chips or miss aliases. Probes must honor bus width and map access ordering.

## Test Signals

Probe mocked maps with no chip, one chip, interleaved chips, and aliasing behavior; assert returned `mtd_info` and chip bitmap contents.

Source read signal: 23 lines, 615 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/gen_probe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/hyperbus.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/hyperbus.h

## Purpose

Provides the HyperBus controller/device abstraction used to expose HyperFlash or HyperRAM through MTD/map-style access.

## Important APIs, Types, and Functions

Key types are `enum hyperbus_memtype`, `struct hyperbus_device`, `struct hyperbus_ops`, and `struct hyperbus_ctlr`; exports are `hyperbus_register_device()` and `hyperbus_unregister_device()`.

Source-visible symbols include structs: `struct hyperbus_device`, `struct map_info map;`, `struct device_node *np;`, `struct mtd_info *mtd;`, `struct hyperbus_ctlr *ctlr;`, `struct hyperbus_ops`, `struct hyperbus_ctlr`, `struct device *dev;`; enums: `enum hyperbus_memtype`, `enum hyperbus_memtype memtype;`; typedefs: none visible in this header; prototypes: `int hyperbus_register_device(struct hyperbus_device *hbdev);`, `void hyperbus_unregister_device(struct hyperbus_device *hbdev);`; representative macros: `__LINUX_MTD_HYPERBUS_H__`, `HYPERBUS_RW_WRITE`, `HYPERBUS_RW_READ`, `HYPERBUS_AS_MEM`, `HYPERBUS_AS_REG`, `HYPERBUS_BT_WRAPPED`, `HYPERBUS_BT_LINEAR`.

## Control Flow

A controller supplies 16-bit register-space operations, copy operations, and optional calibration. Registration probes the HyperBus slave from its device node and controller ops, then creates an MTD device for flash-backed memory.

## State and Persistence Behavior

The device keeps its `map_info`, device tree node, resulting `mtd_info`, controller pointer, memory type, and private controller data. The controller tracks whether calibration has completed.

## Dependencies and Integration Points

It builds on `map.h`, device tree nodes, and MTD map probing. HyperFlash users depend on correct command/address-space bit construction.

Direct includes observed in the source are: `#include <linux/mtd/map.h>`.

## Risks and Edge Cases

Calibration state, burst type/address-space selection, and 16-bit transaction width are hardware-sensitive. Misclassification between HyperFlash and HyperRAM changes whether MTD registration is valid.

## Test Signals

Exercise controller ops against known ID/CFI space reads, registration failure cleanup, calibration-once behavior, and unregister paths.

Source read signal: 95 lines, 2893 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/hyperbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/inftl.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/inftl.h

## Purpose

Defines kernel-side state and helper prototypes for the Inverse NAND Flash Translation Layer block translation driver.

## Important APIs, Types, and Functions

Important APIs are `INFTL_mount()`, `INFTL_formatblock()`, dump helpers, OOB read/write helpers, and `struct INFTLrecord` embedding `mtd_blktrans_dev`.

Source-visible symbols include structs: `struct INFTLrecord`, `struct mtd_blktrans_dev mbd;`, `struct INFTLMediaHeader MediaHdr;`, `struct erase_info instr;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int INFTL_mount(struct INFTLrecord *s);`, `int INFTL_formatblock(struct INFTLrecord *s, int block);`, `void INFTL_dumptables(struct INFTLrecord *s);`, `void INFTL_dumpVUchains(struct INFTLrecord *s);`; representative macros: `__MTD_INFTL_H__`, `INFTL_MAJOR`, `INFTL_PARTN_BITS`.

## Control Flow

Mount reads INFTL media headers and builds physical-unit and virtual-unit tables. Block formatting and OOB helpers operate through the underlying `mtd_info` while the block translation layer exposes disk geometry.

## State and Persistence Behavior

Runtime state includes media unit, erase size, media header, use count, CHS geometry, virtual/physical unit tables, free-unit tracking, boot-block counts, and a reusable `erase_info`. Persistent state is the INFTL media header and translation metadata stored on flash/OOB.

## Dependencies and Integration Points

It depends on MTD block translation, MTD core, NFTL definitions, and the user-visible INFTL header.

Direct includes observed in the source are: `#include <linux/mtd/blktrans.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/nftl.h>`, `#include <mtd/inftl-user.h>`.

## Risks and Edge Cases

PU/VU table corruption or mismatched OOB semantics can remap logical blocks incorrectly. Geometry fields are legacy but still affect block device behavior.

## Test Signals

Mount known INFTL images, format blocks, verify PU/VU chains, exercise OOB helpers across page boundaries, and test malformed media headers.

Source read signal: 63 lines, 1599 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/inftl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/jedec.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/jedec.h

## Purpose

Models the JEDEC NAND parameter page layout and related feature/optional-command bits.

## Important APIs, Types, and Functions

Key types are packed `struct jedec_ecc_info` and `struct nand_jedec_params`, plus feature macros such as `JEDEC_FEATURE_16_BIT_BUS` and `JEDEC_OPT_CMD_READ_CACHE`.

Source-visible symbols include structs: `struct jedec_ecc_info`, `struct nand_jedec_params`, `struct jedec_ecc_info ecc_info[4];`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_JEDEC_H`, `JEDEC_FEATURE_16_BIT_BUS`, `JEDEC_OPT_CMD_READ_CACHE`.

## Control Flow

Raw NAND identification code reads parameter pages, validates the signature and CRC elsewhere, then copies fields from this packed layout into NAND memory organization and ECC requirement structures.

## State and Persistence Behavior

This is a persistent wire/on-flash description format: manufacturer/model, JEDEC ID, page/OOB/block/LUN geometry, timing grades, optional commands, ECC/endurance data, vendor revision, and CRC.

## Dependencies and Integration Points

It depends on fixed-width and little-endian Linux types and is included by raw NAND identification code.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Packed layout and little-endian fields must exactly match the standard. Callers must validate CRC and parameter-page count before trusting geometry.

## Test Signals

Parse golden JEDEC parameter pages, reject bad signatures/CRC, and verify ECC/endurance fields map into `nand_ecc_props` correctly.

Source read signal: 94 lines, 1973 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/jedec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/lpc32xx_mlc.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/lpc32xx_mlc.h

## Purpose

Provides platform data for the LPC32xx MLC NAND controller.

## Important APIs, Types, and Functions

The single exported type is `struct lpc32xx_mlc_platform_data` with a `dma_filter_fn dma_filter` field.

Source-visible symbols include structs: `struct lpc32xx_mlc_platform_data`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_LPC32XX_MLC_H`.

## Control Flow

Board or platform code passes a DMA channel filter to the LPC32xx MLC controller driver during probe so the driver can request appropriate DMA resources.

## State and Persistence Behavior

No runtime or persistent state is stored here; it is probe-time configuration.

## Dependencies and Integration Points

It depends on the DMA engine API and the LPC32xx MLC NAND controller driver.

Direct includes observed in the source are: `#include <linux/dmaengine.h>`.

## Risks and Edge Cases

A wrong or missing DMA filter can force probe failure or fall back to slower/unsupported transfer paths depending on the driver.

## Test Signals

Probe with valid and invalid DMA filter functions and verify DMA channel selection.

Source read signal: 17 lines, 348 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/lpc32xx_mlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/lpc32xx_slc.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/lpc32xx_slc.h

## Purpose

Provides platform data for the LPC32xx SLC NAND controller.

## Important APIs, Types, and Functions

The single exported type is `struct lpc32xx_slc_platform_data` with a `dma_filter_fn dma_filter` field.

Source-visible symbols include structs: `struct lpc32xx_slc_platform_data`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_LPC32XX_SLC_H`.

## Control Flow

Platform code supplies DMA filtering during controller probe; the SLC controller consumes it when acquiring DMA channels.

## State and Persistence Behavior

The header contains only static platform configuration and no persistent state.

## Dependencies and Integration Points

It depends on the DMA engine API and the LPC32xx SLC controller implementation.

Direct includes observed in the source are: `#include <linux/dmaengine.h>`.

## Risks and Edge Cases

Incorrect DMA channel matching can break high-throughput or DMA-required NAND access.

## Test Signals

Board probe tests should confirm filter acceptance, channel acquisition, and fallback behavior.

Source read signal: 17 lines, 348 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/lpc32xx_slc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/map.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/map.h

## Purpose

Defines the central memory-map abstraction for parallel NOR/flash devices, including bank-width handling, `map_word` operations, inline MMIO accessors, and chip-driver registration.

## Important APIs, Types, and Functions

Important APIs include `struct map_info`, `struct mtd_chip_driver`, `map_word` helpers, `map_read()`, `map_write()`, `map_copy_from()`, `map_copy_to()`, `simple_map_init()`, `do_map_probe()`, `map_destroy()`, and chip-driver register/unregister calls.

Source-visible symbols include structs: `struct device_node;`, `struct module;`, `struct mtd_chip_driver;`, `struct map_info`, `struct device_node *device_node;`, `struct mtd_chip_driver *fldrv;`, `struct mtd_chip_driver`, `struct mtd_info *(*probe)(struct map_info *map);`, `struct module *module;`, `struct list_head list;`, `struct mtd_info *do_map_probe(const char *name, struct map_info *map);`; enums: none visible in this header; typedefs: `typedef union {`; prototypes: `void register_mtd_chip_driver(struct mtd_chip_driver *);`, `void unregister_mtd_chip_driver(struct mtd_chip_driver *);`, `void map_destroy(struct mtd_info *mtd);`, `extern void simple_map_init(struct map_info *);`; representative macros: `__LINUX_MTD_MAP_H__`, `map_bankwidth`, `map_bankwidth_is_1`, `map_bankwidth_is_large`, `map_words`, `MAX_MAP_BANKWIDTH`, `map_bankwidth_is_1`, `map_bankwidth_is_2`, `MAX_MAP_BANKWIDTH`, `map_bankwidth_is_2`, `map_bankwidth_is_4`, `MAX_MAP_BANKWIDTH`, `map_bankwidth_is_4`, `map_calc_words`, `map_bankwidth_is_8`, `MAX_MAP_BANKWIDTH`.

## Control Flow

Map drivers fill physical/virtual/cached address fields, bank width, optional complex accessors, cache invalidation, and VPP controls. Probe code calls `do_map_probe()`, which invokes a chip driver and returns an `mtd_info`; chip drivers then use `map_read/write/copy` and `map_word_*` helpers for bus-width-neutral command/data cycles.

## State and Persistence Behavior

Runtime state includes map identity, size, physical and virtual addresses, optional cached alias, byte-swap flag, bank width, PFOW base, private words, device tree node, and flash-driver private data. No flash metadata is persisted by this header.

## Dependencies and Integration Points

It depends on Linux I/O, unaligned access, memory barriers, and MTD chip drivers. It is the integration point for CFI, JEDEC, physmap, LPDDR/PFOW, HyperFlash, and other mapped flash drivers.

Direct includes observed in the source are: `#include <linux/bug.h>`, `#include <linux/io.h>`, `#include <linux/ioport.h>`, `#include <linux/string.h>`, `#include <linux/types.h>`, `#include <linux/unaligned.h>`, `#include <asm/barrier.h>`.

## Risks and Edge Cases

Bank-width configuration controls memory access size and stack layout for wide maps. Missing barriers, wrong cached alias invalidation, or unsupported bank widths can corrupt command sequences or stale reads.

## Test Signals

Compile every configured bank width, probe simple and complex mappings, test `map_word_load_partial()` on endian variants, verify VPP reference behavior, and exercise cached/uncached copy paths.

Source read signal: 466 lines, 13053 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/mtd.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/mtd.h

## Purpose

Defines the Linux MTD core device contract: `struct mtd_info`, erase/OOB operations, partition/master relationships, callback wrappers, pairing schemes, registration, notifiers, and common geometry helpers.

## Important APIs, Types, and Functions

Key types include `struct erase_info`, `mtd_oob_ops`, `mtd_oob_region`, `mtd_ooblayout_ops`, `mtd_pairing_scheme`, `mtd_part`, `mtd_master`, and `mtd_info`. Public functions include `mtd_erase/read/write/read_oob/write_oob`, OTP accessors, lock/bad-block helpers, device registration/unregistration, `get_mtd_device*()`, notifiers, and mmap capability helpers.

Source-visible symbols include structs: `struct mtd_info;`, `struct erase_info`, `struct mtd_erase_region_info`, `struct mtd_req_stats`, `struct mtd_oob_ops`, `struct mtd_req_stats *stats;`, `struct mtd_oob_region`, `struct mtd_ooblayout_ops`, `struct mtd_oob_region *oobecc);`, `struct mtd_oob_region *oobfree);`, `struct mtd_pairing_info`, `struct mtd_pairing_scheme`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int mtd_ooblayout_count_freebytes(struct mtd_info *mtd);`, `int mtd_ooblayout_count_eccbytes(struct mtd_info *mtd);`, `return dev_of_node(&mtd->dev);`, `int mtd_pairing_groups(struct mtd_info *mtd);`, `int mtd_erase(struct mtd_info *mtd, struct erase_info *instr);`, `int mtd_unpoint(struct mtd_info *mtd, loff_t from, size_t len);`, `int mtd_read_oob(struct mtd_info *mtd, loff_t from, struct mtd_oob_ops *ops);`, `int mtd_write_oob(struct mtd_info *mtd, loff_t to, struct mtd_oob_ops *ops);`, `int mtd_lock_user_prot_reg(struct mtd_info *mtd, loff_t from, size_t len);`, `int mtd_erase_user_prot_reg(struct mtd_info *mtd, loff_t from, size_t len);`, `int mtd_lock(struct mtd_info *mtd, loff_t ofs, uint64_t len);`, `int mtd_unlock(struct mtd_info *mtd, loff_t ofs, uint64_t len);`, `int mtd_is_locked(struct mtd_info *mtd, loff_t ofs, uint64_t len);`, `int mtd_block_isreserved(struct mtd_info *mtd, loff_t ofs);`; representative macros: `__MTD_MTD_H__`, `MTD_FAIL_ADDR_UNKNOWN`, `mtd_device_register`.

## Control Flow

MTD users call `mtd_*()` wrappers rather than driver callbacks directly. The wrappers validate ranges, translate partition offsets through `mtd_get_master_ofs()`, dispatch to master callbacks, and maintain suspend state at the master. OOB helpers use `mtd_ooblayout_ops`; pairing helpers translate NAND write-unit ordering for MLC/TLC devices.

## State and Persistence Behavior

Each `mtd_info` stores public geometry, flags, OOB layout, ECC stats, bitflip threshold, optional erase regions, callback table, owner/refcount/device/nvmem handles, partition list, parent pointer, and master locks/suspend bit. Persistent flash state is accessed through callbacks; this header itself holds only kernel runtime state.

## Dependencies and Integration Points

It depends on Linux device, notifier, list, kref, NVMEM, device tree, ABI definitions, and low-level MTD drivers that fill the callback table.

Direct includes observed in the source are: `#include <linux/types.h>`, `#include <linux/uio.h>`, `#include <linux/list.h>`, `#include <linux/notifier.h>`, `#include <linux/device.h>`, `#include <linux/of.h>`, `#include <linux/nvmem-provider.h>`, `#include <mtd/mtd-abi.h>`.

## Risks and Edge Cases

Bypassing wrappers skips partition translation and validation. Wrong geometry or write/OOB sizes affects every filesystem and block translation user. Suspend state, refcounting, and partition list locks are shared integration points.

## Test Signals

Use MTD core tests for range validation, partition offset translation, OOB layout mapping, bad block handling, bitflip/ECC error return semantics, notifier delivery, suspend/resume, and registration cleanup.

Source read signal: 724 lines, 22834 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/mtd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/mtdram.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/mtdram.h

## Purpose

Declares the helper for creating a RAM-backed MTD device.

## Important APIs, Types, and Functions

The exported API is `mtdram_init_device(struct mtd_info *mtd, void *mapped_address, unsigned long size, const char *name)`.

Source-visible symbols include structs: none visible in this header; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__MTD_MTDRAM_H__`.

## Control Flow

A caller provides an `mtd_info`, backing memory, size, and name; the implementation initializes MTD callbacks that emulate flash operations over RAM.

## State and Persistence Behavior

Runtime state is the caller-provided mapped memory and initialized `mtd_info`; contents persist only as long as RAM is retained.

## Dependencies and Integration Points

It depends on the MTD core and the mtdram implementation.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`.

## Risks and Edge Cases

The backing address and size must remain valid for the MTD lifetime. RAM-backed semantics may not reproduce erase/program constraints of real flash.

## Test Signals

Initialize small devices, exercise read/write/erase boundaries, and verify unregister/lifetime cleanup.

Source read signal: 9 lines, 257 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/mtdram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-mtk.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-mtk.h

## Purpose

Defines the MediaTek NAND ECC engine interface used by NAND controller drivers to encode/decode pages through a shared ECC hardware block.

## Important APIs, Types, and Functions

Key items are `enum mtk_ecc_mode`, `enum mtk_ecc_operation`, `struct mtk_ecc_stats`, `struct mtk_ecc_config`, `struct mtk_ecc`, and exported helpers for getting/releasing the engine, enabling/disabling it, and waiting for completion.

Source-visible symbols include structs: `struct device_node;`, `struct mtk_ecc;`, `struct mtk_ecc_stats`, `struct mtk_ecc_config`, `struct mtk_ecc *of_mtk_ecc_get(struct device_node *);`; enums: `enum mtk_ecc_mode`, `enum mtk_ecc_operation`, `enum mtk_ecc_operation op;`, `enum mtk_ecc_mode mode;`; typedefs: none visible in this header; prototypes: `int mtk_ecc_encode(struct mtk_ecc *, struct mtk_ecc_config *, u8 *, u32);`, `void mtk_ecc_get_stats(struct mtk_ecc *, struct mtk_ecc_stats *, int);`, `int mtk_ecc_wait_done(struct mtk_ecc *, enum mtk_ecc_operation);`, `int mtk_ecc_enable(struct mtk_ecc *, struct mtk_ecc_config *);`, `void mtk_ecc_disable(struct mtk_ecc *);`, `void mtk_ecc_adjust_strength(struct mtk_ecc *ecc, u32 *p);`, `unsigned int mtk_ecc_get_parity_bits(struct mtk_ecc *ecc);`, `void mtk_ecc_release(struct mtk_ecc *);`; representative macros: `__DRIVERS_MTD_NAND_MTK_ECC_H__`.

## Control Flow

A controller builds an ECC config describing mode, operation, strength, sector count, length, and buffer addresses, enables the engine for encode or decode, waits for interrupt/poll completion, consumes stats, then disables/releases it.

## State and Persistence Behavior

Runtime state belongs to the hardware engine and the config/stat objects. Corrected, failed, and max-bitflip counts are transient per operation; no persistent metadata is defined.

## Dependencies and Integration Points

It depends on Linux types, device tree lookup, and the MediaTek ECC driver. It integrates with NAND ECC engine selection and MediaTek NFI host drivers.

Direct includes observed in the source are: `#include <linux/types.h>`.

## Risks and Edge Cases

Mismatched sector size, strength, and DMA/NFI mode can cause silent ECC miscorrection. Completion handling and stats propagation must match MTD bitflip/ECC error semantics.

## Test Signals

Run encode/decode vectors at each supported strength, injected bitflip tests, timeout/error paths, and shared-engine get/release lifecycle tests.

Source read signal: 47 lines, 1213 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-mtk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-mxic.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-mxic.h

## Purpose

Defines the Macronix NAND ECC engine interface used by host drivers that offload ECC to a Macronix block.

## Important APIs, Types, and Functions

It exposes opaque `struct mxic_ecc_engine`, config structures, and helper calls to get/put the engine, enable/disable operations, process pages, and retrieve ECC status.

Source-visible symbols include structs: `struct mxic_ecc_engine;`, `struct nand_ecc_engine *mxic_ecc_get_pipelined_engine(struct platform_device *spi_pdev);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `void mxic_ecc_put_pipelined_engine(struct nand_ecc_engine *eng);`, `return ERR_PTR(-EOPNOTSUPP);`; representative macros: `__MTD_NAND_ECC_MXIC_H__`.

## Control Flow

The host initializes an ECC configuration, enables the engine for read or write, runs data through the hardware pipeline, waits/collects status, then disables the engine before returning data to MTD/NAND core.

## State and Persistence Behavior

State is transient hardware and per-request ECC configuration/status. Persistent flash layout is determined by the caller's OOB/ECC placement.

## Dependencies and Integration Points

It integrates with the generic NAND ECC engine model and Macronix controller code. Correct use depends on `nand_device`/`mtd_info` geometry and OOB layout choices.

Direct includes observed in the source are: `#include <linux/platform_device.h>`, `#include <linux/device.h>`.

## Risks and Edge Cases

Risks are unsupported geometry, wrong OOB placement, missed error propagation, and shared-engine lifetime mistakes.

## Test Signals

Exercise get/put, enable/disable, clean decode, corrected bitflips, uncorrectable pages, and geometry rejection.

Source read signal: 49 lines, 1353 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-mxic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-sw-bch.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-sw-bch.h

## Purpose

Defines the software BCH ECC configuration and helper interface for NAND pages.

## Important APIs, Types, and Functions

Key type is `struct nand_ecc_sw_bch_conf`; exported helpers initialize/cleanup the BCH context, calculate ECC, correct data, and provide the software BCH engine when configured.

Source-visible symbols include structs: `struct nand_ecc_sw_bch_conf`, `struct nand_ecc_req_tweak_ctx req_ctx;`, `struct bch_control *bch;`, `struct nand_ecc_engine *nand_ecc_sw_bch_get_engine(void);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int nand_ecc_sw_bch_init_ctx(struct nand_device *nand);`, `void nand_ecc_sw_bch_cleanup_ctx(struct nand_device *nand);`; representative macros: `__MTD_NAND_ECC_SW_BCH_H__`.

## Control Flow

A NAND driver chooses BCH step size/strength, initializes a context, calculates ECC over outgoing data, and on reads compares read and calculated ECC to correct bitflips or report uncorrectable errors.

## State and Persistence Behavior

Runtime state is the BCH context, calculated/read ECC buffers, and ECC parameters. No persistent state exists beyond ECC bytes stored in flash OOB or interleaved layouts by callers.

## Dependencies and Integration Points

It depends on the generic NAND ECC engine contract, raw NAND glue, and kernel BCH support selected by config.

Direct includes observed in the source are: `#include <linux/mtd/nand.h>`, `#include <linux/bch.h>`.

## Risks and Edge Cases

The ECC byte count, OOB layout, strength, and step size must align. BCH can be CPU-expensive and must return MTD-compatible bitflip/error counts.

## Test Signals

Use deterministic BCH vectors, injected bitflips up to and above strength, erased-page cases, and disabled-config stub behavior.

Source read signal: 71 lines, 2117 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-sw-bch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-sw-hamming.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-sw-hamming.h

## Purpose

Defines software Hamming ECC support for NAND, including layout/order options and engine access.

## Important APIs, Types, and Functions

It provides `struct nand_ecc_sw_hamming_conf`, raw NAND calculation/correction hooks, cleanup, and `nand_ecc_sw_hamming_get_engine()` when enabled.

Source-visible symbols include structs: `struct nand_ecc_sw_hamming_conf`, `struct nand_ecc_req_tweak_ctx req_ctx;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int nand_ecc_sw_hamming_init_ctx(struct nand_device *nand);`, `void nand_ecc_sw_hamming_cleanup_ctx(struct nand_device *nand);`; representative macros: `__MTD_NAND_ECC_SW_HAMMING_H__`.

## Control Flow

Raw NAND code initializes Hamming parameters, calculates 3-byte-style ECC per step on writes, and corrects single-bit errors or reports uncorrectable conditions on reads. SmartMedia byte-order mode is represented by options.

## State and Persistence Behavior

State is a small per-chip context and ECC buffers; persistent bytes are stored by the caller in OOB according to the selected layout.

## Dependencies and Integration Points

It integrates with raw NAND ECC callbacks and the generic NAND ECC engine.

Direct includes observed in the source are: `#include <linux/mtd/nand.h>`.

## Risks and Edge Cases

Wrong byte ordering or OOB position breaks compatibility with existing media. Hamming strength is limited and must not be over-advertised.

## Test Signals

Single-bit correction vectors, double-bit failure vectors, SmartMedia order compatibility, and erased-page behavior.

Source read signal: 89 lines, 2714 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-sw-hamming.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/nand-gpio.h

## Purpose

Declares platform data for GPIO-driven raw NAND control lines.

## Important APIs, Types, and Functions

The exported type is `struct gpiomtd_platform_data`, carrying GPIO numbers/line names and an embedded platform NAND data object.

Source-visible symbols include structs: `struct gpio_nand_platdata`, `struct mtd_partition *parts;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_NAND_GPIO_H`.

## Control Flow

A GPIO NAND driver consumes the platform data to map CLE/ALE/NCE/RDY and I/O resources, then delegates chip behavior through platform/raw NAND structures.

## State and Persistence Behavior

Only static board configuration is described; no persistent state exists.

## Dependencies and Integration Points

It depends on platform NAND/raw NAND declarations and board-specific GPIO numbering.

Direct includes observed in the source are: `#include <linux/mtd/rawnand.h>`.

## Risks and Edge Cases

Wrong GPIO polarity or line assignment can corrupt command/address cycles or ready/busy polling.

## Test Signals

Probe with valid/invalid GPIOs, command/control toggling traces, and ready/busy timeout behavior.

Source read signal: 15 lines, 330 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-qpic-common.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/nand-qpic-common.h

## Purpose

Defines Qualcomm QPIC NAND controller common register offsets, bit fields, DMA transaction structures, controller property/state structures, and helper prototypes shared by QPIC raw NAND and SPI NAND support.

## Important APIs, Types, and Functions

Important types are `struct bam_transaction`, `struct desc_info`, `struct nandc_regs`, `struct qcom_nand_controller`, and `struct qcom_nandc_props`. Important helpers allocate/clear/free BAM transactions, prepare BAM/ADM descriptors, read/write registers and data through DMA, submit descriptors, and allocate/unallocate controller resources.

Source-visible symbols include structs: `struct bam_transaction`, `struct bam_cmd_element *bam_ce;`, `struct scatterlist *cmd_sgl;`, `struct scatterlist *data_sgl;`, `struct dma_async_tx_descriptor *last_data_desc;`, `struct dma_async_tx_descriptor *last_cmd_desc;`, `struct completion txn_done;`, `struct desc_info`, `struct dma_async_tx_descriptor *dma_desc;`, `struct list_head node;`, `struct scatterlist adm_sgl;`, `struct`; enums: `enum dma_data_direction dir;`; typedefs: none visible in this header; prototypes: `void qcom_free_bam_transaction(struct qcom_nand_controller *nandc);`, `void qcom_clear_bam_transaction(struct qcom_nand_controller *nandc);`, `void qcom_qpic_bam_dma_done(void *data);`, `void qcom_nandc_dev_to_mem(struct qcom_nand_controller *nandc, bool is_cpu);`, `int qcom_submit_descs(struct qcom_nand_controller *nandc);`, `void qcom_clear_read_regs(struct qcom_nand_controller *nandc);`, `void qcom_nandc_unalloc(struct qcom_nand_controller *nandc);`, `int qcom_nandc_alloc(struct qcom_nand_controller *nandc);`; representative macros: `__MTD_NAND_QPIC_COMMON_H__`, `READ_LOCATION_OFFSET_MASK`, `READ_LOCATION_SIZE_MASK`, `READ_LOCATION_LAST_MASK`, `NAND_DEV_CMD_VLD_VAL`, `dev_cmd_reg_addr`, `reg_buf_dma_addr`, `QPIC_PER_CW_CMD_ELEMENTS`, `QPIC_PER_CW_CMD_SGL`, `QPIC_PER_CW_DATA_SGL`, `QPIC_NAND_COMPLETION_TIMEOUT`, `NAND_BAM_NO_EOT`, `NAND_BAM_NWD`, `NAND_BAM_NEXT_SGL`, `NAND_ERASED_CW_SET`, `MAX_ADDRESS_CYCLE`.

## Control Flow

Drivers populate `nandc_regs`, translate register writes into BAM command elements or ADM descriptors, queue command/data scatterlists, submit DMA, wait for `txn_done`, then read status/error registers. Constants describe page read/program/erase ops, ECC modes, erased-codeword detection, read-location registers, and controller version fields.

## State and Persistence Behavior

Runtime state includes MMIO base, clocks, DMA channels, descriptor lists, local data and register-read buffers, DMA addresses, max codewords per page, cached command-valid registers, and whether status reads are part of exec-op write handling. Persistent data is NAND contents only.

## Dependencies and Integration Points

It integrates with Linux DMA engine, scatterlists, completions, clocks, raw NAND controller ops, QPIC SPI NAND glue, and Qualcomm DT match-data properties.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Descriptor sizing, EOT/NWD flags, erased-codeword detection state, codeword count, and ECC mode selection are all hardware-critical. DMA buffer lifetime or register-offset mistakes can hang the controller or corrupt flash.

## Test Signals

Validate descriptor construction for BAM and ADM, ECC mode/page geometry combinations, erased-page detection, timeout cleanup, multi-chip host lists, and register programming against hardware traces.

Source read signal: 483 lines, 14608 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand-qpic-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/nand.h

## Purpose

Defines the generic NAND device model used by raw NAND, SPI NAND, and other NAND-like layers, including memory organization, positions, page I/O requests, ECC engine abstraction, bad-block table state, and MTD bridge helpers.

## Important APIs, Types, and Functions

Key types include `nand_memory_organization`, `nand_pos`, `nand_page_io_req`, `nand_ecc_props`, `nand_ops`, `nand_ecc_engine`, `nand_device`, and `nand_io_iter`. Public helpers cover ECC engine init/cleanup/prepare/finish, software/on-die/on-host engine lookup, request tweaking, device init/register/unregister, offset/position conversions, page/block iterators, BBT operations, and MTD erase/max-bad-block bridge functions.

Source-visible symbols include structs: `struct nand_device;`, `struct nand_memory_organization`, `struct nand_row_converter`, `struct nand_pos`, `struct nand_page_io_req`, `struct nand_pos pos;`, `struct nand_ecc_props`, `struct nand_bbt`, `struct nand_ops`, `struct nand_ecc_context`, `struct nand_ecc_props conf;`, `struct nand_ecc_engine_ops`; enums: `enum nand_page_io_req_type`, `enum nand_page_io_req_type type;`, `enum nand_ecc_engine_type`, `enum nand_ecc_placement`, `enum nand_ecc_algo`, `enum nand_ecc_engine_type engine_type;`, `enum nand_ecc_placement placement;`, `enum nand_ecc_algo algo;`, `enum nand_ecc_engine_integration`, `enum nand_ecc_engine_integration integration;`; typedefs: none visible in this header; prototypes: `void of_get_nand_ecc_user_config(struct nand_device *nand);`, `int nand_ecc_init_ctx(struct nand_device *nand);`, `void nand_ecc_cleanup_ctx(struct nand_device *nand);`, `bool nand_ecc_is_strong_enough(struct nand_device *nand);`, `int nand_ecc_register_on_host_hw_engine(struct nand_ecc_engine *engine);`, `int nand_ecc_unregister_on_host_hw_engine(struct nand_ecc_engine *engine);`, `void nand_ecc_put_on_host_hw_engine(struct nand_device *nand);`, `void nand_ecc_cleanup_req_tweaking(struct nand_ecc_req_tweak_ctx *ctx);`, `return container_of(mtd, struct nand_device, mtd);`, `return nanddev_target_size(nand) * nanddev_ntargets(nand);`, `void nanddev_cleanup(struct nand_device *nand);`, `return mtd_device_register(&nand->mtd, NULL, 0);`, `return mtd_device_unregister(&nand->mtd);`, `return mtd_get_of_node(&nand->mtd);`; representative macros: `__LINUX_MTD_NAND_H`, `NAND_MEMORG`, `NAND_ECCREQ`, `NAND_ECC_MAXIMIZE_STRENGTH`, `nanddev_io_for_each_page`, `nanddev_io_for_each_block`.

## Control Flow

Specialized NAND layers fill memorg and ECC requirements, call `nanddev_init()`, then expose MTD callbacks. MTD requests are split by `nanddev_io_for_each_page()` or block iterators into `nand_page_io_req` objects. ECC engines prepare a request before I/O and finish it after I/O, while bad-block helpers gate erase/markbad/isbad operations.

## State and Persistence Behavior

Runtime state is embedded in `nand_device`: MTD core object, memory geometry, ECC defaults/requirements/user config/context, row conversion shifts, BBT cache, and low-level ops. Request tweak contexts may allocate bounce buffers to adapt partial/OOB requests.

## Dependencies and Integration Points

It depends on MTD core and is included by raw NAND and SPI NAND layers. It also integrates with device tree ECC configuration and optional software/on-host/on-die ECC engines.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`.

## Risks and Edge Cases

Offset-to-position math must match geometry, especially multi-target/LUN/plane devices. ECC engine selection and request tweaking can change buffers; callers must restore requests and propagate bitflip/ECC errors correctly.

## Test Signals

Unit-test position conversions, page/block iterators, ECC config negotiation, BBT status transitions, bad-block MTD bridge behavior, and partial data/OOB request tweaking.

Source read signal: 1144 lines, 34539 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/ndfc.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/ndfc.h

## Purpose

Defines platform data for IBM/PowerPC NDFC NAND flash controller instances.

## Important APIs, Types, and Functions

The main type is `struct ndfc_controller_settings`, carrying bank settings and chip-select/platform details used by the NDFC driver.

Source-visible symbols include structs: `struct ndfc_controller_settings`, `struct ndfc_chip_settings`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_NDFC_H`, `NDFC_CMD`, `NDFC_ALE`, `NDFC_DATA`, `NDFC_ECC`, `NDFC_BCFG0`, `NDFC_BCFG1`, `NDFC_BCFG2`, `NDFC_BCFG3`, `NDFC_CCR`, `NDFC_STAT`, `NDFC_HWCTL`, `NDFC_REVID`, `NDFC_STAT_IS_READY`, `NDFC_MAX_BANKS`.

## Control Flow

Platform code passes NDFC timing/bank configuration to the controller driver, which then initializes raw NAND controller resources and partitions.

## State and Persistence Behavior

Only static platform/controller configuration is represented.

## Dependencies and Integration Points

It integrates with raw NAND, platform device setup, and board-specific NDFC resources.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Wrong bank or timing configuration causes failed probe or unreliable command/data cycles.

## Test Signals

Board probe validation, chip-select mapping, and read/write/erase smoke tests on NDFC-backed NAND.

Source read signal: 61 lines, 2084 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/ndfc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nftl.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/nftl.h

## Purpose

Defines kernel-side state and helper prototypes for the NAND Flash Translation Layer block translation driver.

## Important APIs, Types, and Functions

Important pieces are `struct NFTLrecord`, `NFTL_mount()`, `NFTL_formatblock()`, table dump helpers, and `nftl_read_oob()`/`nftl_write_oob()`.

Source-visible symbols include structs: `struct NFTLrecord`, `struct mtd_blktrans_dev mbd;`, `struct NFTLMediaHeader MediaHdr;`, `struct erase_info instr;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int NFTL_mount(struct NFTLrecord *s);`, `int NFTL_formatblock(struct NFTLrecord *s, int block);`; representative macros: `__MTD_NFTL_H__`, `NFTL_MAJOR`, `MAX_NFTLS`, `MAX_SECTORS_PER_UNIT`, `NFTL_PARTN_BITS`.

## Control Flow

NFTL mount scans media headers and builds erase-unit and replacement-chain tables; block operations translate logical sectors to physical NAND pages and use OOB metadata for status.

## State and Persistence Behavior

Runtime state includes an embedded `mtd_blktrans_dev`, media header, erase size, use count, geometry, virtual unit chains, replacement/free block tracking, last free block, and erase instruction. Persistent state is NFTL metadata stored in flash and OOB.

## Dependencies and Integration Points

It depends on MTD core, block translation, and the user NFTL media-format header.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/blktrans.h>`, `#include <mtd/nftl-user.h>`.

## Risks and Edge Cases

Translation-table corruption, free-block exhaustion, and OOB incompatibility can expose stale or wrong logical data.

## Test Signals

Mount golden NFTL images, test replacement chains, bad/deleted/free block handling, OOB helpers, and recovery from malformed metadata.

Source read signal: 57 lines, 1734 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/nftl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/onenand.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/onenand.h

## Purpose

Defines the OneNAND chip model, platform data, scan/release APIs, BufferRAM bookkeeping, option flags, and helper macros for Samsung/Numonyx OneNAND devices.

## Important APIs, Types, and Functions

Important APIs are `onenand_scan()`, `onenand_release()`, `onenand_bbt_read_oob()`, address conversion helpers, `flexonenand_region()`, `struct onenand_chip`, `struct onenand_platform_data`, and option/manufacturer macros.

Source-visible symbols include structs: `struct onenand_bufferram`, `struct onenand_chip`, `struct onenand_bufferram	bufferram[MAX_BUFFERRAM];`, `struct completion	complete;`, `struct onenand_manufacturers`, `struct mtd_oob_ops *ops);`, `struct mtd_partition;`, `struct onenand_platform_data`, `struct mtd_partition *parts;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `extern int onenand_scan(struct mtd_info *mtd, int max_chips);`, `extern void onenand_release(struct mtd_info *mtd);`, `unsigned short (*read_word)(void __iomem *addr);`, `unsigned onenand_block(struct onenand_chip *this, loff_t addr);`, `loff_t onenand_addr(struct onenand_chip *this, int block);`, `int flexonenand_region(struct mtd_info *mtd, loff_t addr);`; representative macros: `__LINUX_MTD_ONENAND_H`, `MAX_DIES`, `MAX_BUFFERRAM`, `ONENAND_PAGES_PER_BLOCK`, `ONENAND_CURRENT_BUFFERRAM`, `ONENAND_NEXT_BUFFERRAM`, `ONENAND_SET_NEXT_BUFFERRAM`, `ONENAND_SET_PREV_BUFFERRAM`, `ONENAND_SET_BUFFERRAM0`, `ONENAND_SET_BUFFERRAM1`, `FLEXONENAND`, `ONENAND_GET_SYS_CFG1`, `ONENAND_SET_SYS_CFG1`, `ONENAND_IS_DDP`, `ONENAND_IS_MLC`, `ONENAND_IS_2PLANE`.

## Control Flow

OneNAND drivers issue commands through replaceable `command`, `wait`, `bbt_wait`, BufferRAM read/write, word access, chip-probe, block-markbad, and scan-BBT hooks. BufferRAM macros toggle between the two internal buffers; option macros adapt behavior for Flex-OneNAND, DDP, MLC, 2-plane, cache program, and 4K pages.

## State and Persistence Behavior

Runtime state includes MMIO base, die boundaries and sizes, chip/device/version/technology IDs, geometry shifts, current BufferRAM index, completion/IRQ, spinlock/waitqueue, `flstate_t` state, page/OOB/verify buffers, bad-block management pointer, private data, and an `ongoing` multi-command flag.

## Dependencies and Integration Points

It depends on `flashchip.h`, OneNAND register definitions, bad-block management, completions/spinlocks, and MTD core.

Direct includes observed in the source are: `#include <linux/spinlock.h>`, `#include <linux/completion.h>`, `#include <linux/mtd/flashchip.h>`, `#include <linux/mtd/onenand_regs.h>`, `#include <linux/mtd/bbm.h>`.

## Risks and Edge Cases

BufferRAM index mistakes, Flex-OneNAND die boundary calculations, and command sequence status handling can corrupt data. Locking must coordinate interrupt completion with synchronous waiters.

## Test Signals

Scan/release lifecycle, BufferRAM switching, read/program/erase, cache-program sequences, Flex-OneNAND region mapping, bad-block marking, and IRQ/timeout wait paths.

Source read signal: 240 lines, 7974 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/onenand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/onenand_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/onenand_regs.h

## Purpose

Defines the OneNAND memory-map translation, register offsets, command codes, status bits, ECC bits, device-ID fields, and OTP offsets.

## Important APIs, Types, and Functions

This header is macro-only. It includes `ONENAND_MEMORY_MAP()`, register offsets like `ONENAND_REG_COMMAND`, command values such as `ONENAND_CMD_READ/PROG/ERASE/RESET`, system configuration bits, interrupt/status bits, write-protect bits, ECC status masks, and Flex-OneNAND PI/OTP constants.

Source-visible symbols include structs: none visible in this header; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__ONENAND_REG_H`, `ONENAND_MEMORY_MAP`, `ONENAND_REG_MANUFACTURER_ID`, `ONENAND_REG_DEVICE_ID`, `ONENAND_REG_VERSION_ID`, `ONENAND_REG_DATA_BUFFER_SIZE`, `ONENAND_REG_BOOT_BUFFER_SIZE`, `ONENAND_REG_NUM_BUFFERS`, `ONENAND_REG_TECHNOLOGY`, `ONENAND_REG_START_ADDRESS1`, `ONENAND_REG_START_ADDRESS2`, `ONENAND_REG_START_ADDRESS3`, `ONENAND_REG_START_ADDRESS4`, `ONENAND_REG_START_ADDRESS5`, `ONENAND_REG_START_ADDRESS6`, `ONENAND_REG_START_ADDRESS7`.

## Control Flow

OneNAND code writes address/start-buffer registers, issues command values through `ONENAND_REG_COMMAND`, then polls or waits on controller status/interrupt bits and checks ECC/write-protect fields.

## State and Persistence Behavior

The defined state is hardware register state and persistent device OTP/PI fields. The header itself has no runtime storage.

## Dependencies and Integration Points

It is consumed by `onenand.h` and OneNAND controller implementations that perform MMIO word access.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Register offsets are word-address translated; treating them as byte offsets without `ONENAND_MEMORY_MAP()` would hit wrong registers. Status-bit handling differs across SLC/MLC/Flex devices.

## Test Signals

Hardware or register-model tests should verify command programming, interrupt clear/status detection, ECC classification, write-protect status, and Flex-OneNAND PI access.

Source read signal: 221 lines, 7217 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/onenand_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/onfi.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/onfi.h

## Purpose

Defines ONFI NAND parameter-page structures, feature addresses, timing mode bits, CRC base, and helper declarations for ONFI identification and timing conversion.

## Important APIs, Types, and Functions

Key types include ONFI parameter/timing/extended parameter structures and exported helpers for ONFI CRC, SDR/NV-DDR timing extraction, and parameter-page parsing used by raw NAND.

Source-visible symbols include structs: `struct nand_onfi_params`, `struct onfi_ext_ecc_info`, `struct onfi_ext_section`, `struct onfi_ext_param_page`, `struct onfi_ext_section sections[ONFI_EXT_SECTION_MAX];`, `struct onfi_params`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_ONFI_H`, `ONFI_VERSION_1_0`, `ONFI_VERSION_2_0`, `ONFI_VERSION_2_1`, `ONFI_VERSION_2_2`, `ONFI_VERSION_2_3`, `ONFI_VERSION_3_0`, `ONFI_VERSION_3_1`, `ONFI_VERSION_3_2`, `ONFI_VERSION_4_0`, `ONFI_FEATURE_16_BIT_BUS`, `ONFI_FEATURE_NV_DDR`, `ONFI_FEATURE_EXT_PARAM_PAGE`, `ONFI_DATA_INTERFACE_SDR`, `ONFI_DATA_INTERFACE_NVDDR`, `ONFI_DATA_INTERFACE_NVDDR2`.

## Control Flow

Raw NAND detection reads ONFI parameter pages, validates signature/CRC, extracts geometry, timing, features, optional commands, and ECC information, then builds NAND memory organization and interface timing configs.

## State and Persistence Behavior

This header models persistent ONFI parameter data and feature-register addresses. Runtime state is stored by callers in `nand_parameters` and timing config objects.

## Dependencies and Integration Points

It integrates with raw NAND identification, `nand_interface_config`, and vendor feature handling.

Direct includes observed in the source are: `#include <linux/types.h>`, `#include <linux/bitfield.h>`.

## Risks and Edge Cases

Packed layout, endian conversion, CRC validation, and multiple-parameter-page fallback are critical. Timing mode conversion must not overdrive the controller or chip.

## Test Signals

Golden ONFI parameter pages for multiple revisions, CRC failures, timing mode conversion, feature set/get bitmaps, and extended parameter parsing.

Source read signal: 190 lines, 4999 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/onfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/partitions.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/partitions.h

## Purpose

Defines MTD partition descriptors, parser interfaces, parser registration, and parser data used to split master MTD devices into child partitions.

## Important APIs, Types, and Functions

Key types are `struct mtd_partition`, `struct mtd_part_parser_data`, and `struct mtd_part_parser`; functions include parser register/unregister helpers, parser lookup/put, and partition parse/delete helpers.

Source-visible symbols include structs: `struct mtd_partition`, `struct device_node *of_node;`, `struct mtd_info;`, `struct device_node;`, `struct mtd_part_parser_data`, `struct mtd_part_parser`, `struct list_head list;`, `struct module *owner;`, `struct mtd_part_parser_data *);`, `struct mtd_partitions`, `struct module *owner);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `extern void deregister_mtd_parser(struct mtd_part_parser *parser);`, `int mtd_del_partition(struct mtd_info *master, int partno);`, `uint64_t mtd_get_device_size(const struct mtd_info *mtd);`; representative macros: `MTD_PARTITIONS_H`, `MTDPART_OFS_RETAIN`, `MTDPART_OFS_NXTBLK`, `MTDPART_OFS_APPEND`, `MTDPART_SIZ_FULL`, `register_mtd_parser`, `module_mtd_part_parser`.

## Control Flow

MTD registration can pass fixed partitions and parser names. Parser modules inspect device contents or DT/platform data, return `mtd_partition` arrays, and the core creates child `mtd_info` partitions with offsets, sizes, masks, and parser metadata.

## State and Persistence Behavior

Partition definitions are static or parser-generated metadata. Runtime partition state lives in child `mtd_info.part` fields and parser reference counts.

## Dependencies and Integration Points

It depends on MTD core, module/device tree support, and parser implementations such as cmdline, fixed-partitions, RedBoot, or platform-specific parsers.

Direct includes observed in the source are: `#include <linux/types.h>`.

## Risks and Edge Cases

Incorrect offsets/sizes can expose overlapping partitions or hide data. Parser lifetime and dynamically allocated partition arrays must be managed consistently.

## Test Signals

Fixed partition registration, parser priority/order, overlap/bounds rejection, DT label propagation, and parser module refcount cleanup.

Source read signal: 115 lines, 3946 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/partitions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/pfow.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/pfow.h

## Purpose

Defines the PFOW command register interface for LPDDR/Numonyx-style object-mode flash programming and erase operations over an MTD map.

## Important APIs, Types, and Functions

It provides PFOW register offsets, LPDDR command codes, DSR status/error masks, and `send_pfow_command()` which writes command, address, length, optional data, and execute registers through `map_write()`.

Source-visible symbols include structs: none visible in this header; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PFOW_H`, `PFOW_QUERY_STRING_P`, `PFOW_QUERY_STRING_F`, `PFOW_QUERY_STRING_O`, `PFOW_QUERY_STRING_W`, `PFOW_MANUFACTURER_ID`, `PFOW_DEVICE_ID`, `PFOW_PROGRAM_BUFFER_OFFSET`, `PFOW_PROGRAM_BUFFER_SIZE`, `PFOW_COMMAND_CODE`, `PFOW_COMMAND_DATA`, `PFOW_COMMAND_ADDRESS_L`, `PFOW_COMMAND_ADDRESS_H`, `PFOW_DATA_COUNT_L`, `PFOW_DATA_COUNT_H`, `PFOW_COMMAND_EXECUTE`.

## Control Flow

Callers build `map_word` commands with the LPDDR helper macros, write command/address/count/data registers at `map->pfow_base`, and start execution by writing `LPDDR_START_EXECUTION`; later code checks the DSR ready/error bits.

## State and Persistence Behavior

Hardware PFOW command and status registers carry transient operation state. Persistent state is flash blocks, locks, and OTP contents changed by commands.

## Dependencies and Integration Points

It depends on `map.h` and `qinfo.h` command helpers. It integrates with LPDDR flash chip drivers.

Direct includes observed in the source are: `#include <linux/mtd/qinfo.h>`.

## Risks and Edge Cases

Address/count splitting uses `map_bankwidth()` bits-per-chip; wrong bank width or PFOW base sends commands to wrong registers. DSR error bits must be fully checked and cleared.

## Test Signals

Mock map writes for word program, buffer program, erase, lock/unlock, OTP commands, plus DSR error handling and wide-bank address splitting.

Source read signal: 124 lines, 4489 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/pfow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/physmap.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/physmap.h

## Purpose

Defines platform data for the generic physically mapped flash driver.

## Important APIs, Types, and Functions

The main type is `struct physmap_flash_data` with bus width, init/exit/VPP callbacks, PFOW base, probe type, partition list, and partition parser names.

Source-visible symbols include structs: `struct map_info;`, `struct platform_device;`, `struct physmap_flash_data`, `struct mtd_partition	*parts;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PHYSMAP__`.

## Control Flow

Board/platform code supplies physical map configuration; the physmap driver maps memory, initializes `map_info`, toggles VPP through callbacks, probes the specified chip type, and registers fixed or parsed partitions.

## State and Persistence Behavior

This is static platform configuration. Runtime map and MTD state are created by the physmap driver.

## Dependencies and Integration Points

It depends on MTD core, partition descriptors, platform devices, and map/chip probe infrastructure.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/partitions.h>`.

## Risks and Edge Cases

Wrong width, probe type, PFOW base, or VPP callback can prevent detection or make writes unsafe.

## Test Signals

Probe with each configured width, fixed and parser-based partitions, VPP enable/disable counts, and init/exit cleanup.

Source read signal: 31 lines, 808 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/physmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/pismo.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/pismo.h

## Purpose

Defines board data for the PISMO memory driver.

## Important APIs, Types, and Functions

The exported type is `struct pismo_pdata`, containing a VPP callback/data pointer and up to five chip-select physical addresses.

Source-visible symbols include structs: `struct pismo_pdata`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PISMO_H`.

## Control Flow

The PISMO driver consumes this board data to locate chip-select windows and control write/program voltage.

## State and Persistence Behavior

Only platform configuration is represented.

## Dependencies and Integration Points

It integrates with PISMO memory platform code and mapped flash drivers.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Incorrect chip-select addresses or VPP callback data can target the wrong memory window or fail writes.

## Test Signals

Probe with populated/empty chip-select entries and verify VPP callback invocation.

Source read signal: 14 lines, 271 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/pismo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/plat-ram.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/plat-ram.h

## Purpose

Defines platform data for generic RAM-backed MTD map devices.

## Important APIs, Types, and Functions

Key items are `PLATRAM_RO`, `PLATRAM_RW`, and `struct platdata_mtd_ram` with map/probe names, partition data, bank width, and optional `set_rw()` control callback.

Source-visible symbols include structs: `struct platdata_mtd_ram`, `struct mtd_partition	*partitions;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PLATRAM_H`, `PLATRAM_RO`, `PLATRAM_RW`.

## Control Flow

The platform RAM driver uses this data to initialize a map, choose probes/partition parsers, and optionally switch hardware between read-only and writable modes.

## State and Persistence Behavior

Configuration is static platform data; actual contents are in the mapped RAM region.

## Dependencies and Integration Points

It integrates with map probes, partition descriptors, and platform devices.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Bank width and read/write control must match the hardware window. The `set_rw()` callback must not race with active MTD writes.

## Test Signals

Probe RO/RW modes, partition registration, bank-width access, and `set_rw()` transitions around writes.

Source read signal: 30 lines, 668 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/plat-ram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/platnand.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/platnand.h

## Purpose

Defines legacy platform data containers for raw NAND chips and controllers.

## Important APIs, Types, and Functions

Key types are `struct platform_nand_chip`, `struct platform_nand_ctrl`, and `struct platform_nand_data`, carrying chip scan limits, partition data, options/BBT options, parser names, and optional controller callbacks.

Source-visible symbols include structs: `struct platform_nand_chip`, `struct mtd_partition *partitions;`, `struct platform_nand_ctrl`, `struct platform_nand_data`, `struct platform_nand_chip chip;`, `struct platform_nand_ctrl ctrl;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PLATNAND_H`.

## Control Flow

A platform NAND driver combines chip-level geometry/options with controller-level `probe`, `remove`, ready, select, command-control, and buffer callbacks, then scans/registers raw NAND through the raw NAND core.

## State and Persistence Behavior

The header stores static platform configuration and a private controller pointer. Runtime state is in `nand_chip` and controller driver objects.

## Dependencies and Integration Points

It depends on partition definitions, raw NAND APIs, and platform devices.

Direct includes observed in the source are: `#include <linux/mtd/partitions.h>`, `#include <linux/mtd/rawnand.h>`, `#include <linux/platform_device.h>`.

## Risks and Edge Cases

Legacy callbacks must match raw NAND command sequencing. Wrong chip count, options, or BBT flags can misdetect chips or lose bad-block metadata.

## Test Signals

Legacy command-control traces, ready polling, partition parser selection, multi-chip scan, and BBT option handling.

Source read signal: 74 lines, 2542 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/platnand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/qinfo.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/qinfo.h

## Purpose

Defines LPDDR flash query-info structures, private chip state, command helpers, fixup IDs, and the LPDDR command-set probe entry.

## Important APIs, Types, and Functions

Key types are `struct lpddr_private`, `struct qinfo_query_info`, and `struct qinfo_chip`; helpers include `lpddr_build_cmd()`, `CMD`, `CMDVAL`, and `lpddr_cmdset()`.

Source-visible symbols include structs: `struct lpddr_private`, `struct qinfo_chip *qinfo;`, `struct flchip chips[] __counted_by(numchips);`, `struct qinfo_query_info`, `struct qinfo_chip`, `struct mtd_info *lpddr_cmdset(struct map_info *);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_QINFO_H`, `LPDDR_MFR_ANY`, `LPDDR_ID_ANY`, `NUMONYX_MFGR_ID`, `R18_DEVICE_ID_1G`, `CMD`, `CMDVAL`.

## Control Flow

LPDDR probe code reads qinfo records, builds `qinfo_chip` geometry/timing data, initializes `flchip` entries, and uses map-word commands for subsequent command-set operations.

## State and Persistence Behavior

Runtime state includes manufacturer/device IDs, qinfo pointer, chip count, chipshift, and an array of `flchip` state objects. Persistent qinfo data is read from the flash information query area.

## Dependencies and Integration Points

It depends on map, wait/spinlock/delay, MTD core, flashchip state, and partitions.

Direct includes observed in the source are: `#include <linux/mtd/map.h>`, `#include <linux/wait.h>`, `#include <linux/spinlock.h>`, `#include <linux/delay.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/flashchip.h>`, `#include <linux/mtd/partitions.h>`.

## Risks and Edge Cases

The flexible array is sized by `numchips`; allocation must match. Query record interpretation controls device size, block size, partitioning, and operation timing.

## Test Signals

Probe known LPDDR qinfo records, fixup manufacturer/device IDs, command-word construction for each bank width, and timing-derived wait behavior.

Source read signal: 92 lines, 2553 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/qinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/rawnand.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/rawnand.h

## Purpose

Defines MTD-related contracts for `rawnand.h`.

## Important APIs, Types, and Functions

The important API surface is captured by the source-derived symbol inventory below.

Source-visible symbols include structs: `struct nand_chip;`, `struct gpio_desc;`, `struct nand_parameters`, `struct onfi_params *onfi;`, `struct nand_id`, `struct nand_ecc_step_info`, `struct nand_ecc_caps`, `struct nand_ecc_ctrl`, `struct nand_sdr_timings`, `struct nand_nvddr_timings`, `struct nand_interface_config`, `struct nand_timings`; enums: `enum nand_ecc_engine_type engine_type;`, `enum nand_ecc_placement placement;`, `enum nand_ecc_algo algo;`, `enum nand_interface_type`, `enum nand_interface_type type;`, `enum nand_op_instr_type`, `enum nand_op_instr_type type;`; typedefs: none visible in this header; prototypes: `return ERR_PTR(-EINVAL);`, `return ERR_PTR(-EINVAL);`, `return container_of(mtd, struct nand_chip, base.mtd);`, `return mtd_get_of_node(nand_to_mtd(chip));`, `int nand_create_bbt(struct nand_chip *chip);`, `int rawnand_sw_hamming_init(struct nand_chip *chip);`, `void rawnand_sw_hamming_cleanup(struct nand_chip *chip);`, `int rawnand_sw_bch_init(struct nand_chip *chip);`, `void rawnand_sw_bch_cleanup(struct nand_chip *chip);`, `int nand_write_oob_std(struct nand_chip *chip, int page);`, `int nand_read_oob_std(struct nand_chip *chip, int page);`, `int nand_reset(struct nand_chip *chip, int chipnr);`, `int nand_reset_op(struct nand_chip *chip);`, `int nand_status_op(struct nand_chip *chip, u8 *status);`; representative macros: `__LINUX_MTD_RAWNAND_H`, `NAND_MAX_CHIPS`, `NAND_NCE`, `NAND_CLE`, `NAND_ALE`, `NAND_CTRL_CLE`, `NAND_CTRL_ALE`, `NAND_CTRL_CHANGE`, `NAND_CMD_READ0`, `NAND_CMD_READ1`, `NAND_CMD_RNDOUT`, `NAND_CMD_PAGEPROG`, `NAND_CMD_READOOB`, `NAND_CMD_ERASE1`, `NAND_CMD_STATUS`, `NAND_CMD_SEQIN`.

## Control Flow

Control flow is implemented by including drivers; this header supplies the constants, structures, or prototypes those drivers use.

## State and Persistence Behavior

State behavior is limited to the fields declared here and any hardware/media state represented by constants.

## Dependencies and Integration Points

Dependencies are visible from the include list and neighboring MTD subsystem headers.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/nand.h>`, `#include <linux/mtd/flashchip.h>`, `#include <linux/mtd/bbm.h>`, `#include <linux/mtd/jedec.h>`, `#include <linux/mtd/onfi.h>`, `#include <linux/mutex.h>`, `#include <linux/of.h>`.

## Risks and Edge Cases

Risks center on ABI/layout drift and callers misinterpreting the declared constants or callback contracts.

## Test Signals

Build coverage plus targeted driver tests should exercise the declared symbols.

Source read signal: 1640 lines, 53764 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/rawnand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/sh_flctl.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/sh_flctl.h

## Purpose

Defines registers, bit fields, platform data, and driver state for the Renesas SuperH FLCTL NAND controller.

## Important APIs, Types, and Functions

Important items are FLCTL register macros, command/control bit masks, `enum flctl_ecc_res_t`, `struct sh_flctl`, `struct sh_flctl_platform_data`, and `mtd_to_flctl()`.

Source-visible symbols include structs: `struct dma_chan;`, `struct sh_flctl`, `struct nand_chip	chip;`, `struct platform_device	*pdev;`, `struct dev_pm_qos_request pm_qos;`, `struct dma_chan		*chan_fifo0_rx;`, `struct dma_chan		*chan_fifo0_tx;`, `struct completion	dma_complete;`, `struct sh_flctl_platform_data`, `struct mtd_partition	*parts;`; enums: `enum flctl_ecc_res_t`; typedefs: none visible in this header; prototypes: `return container_of(mtd_to_nand(mtdinfo), struct sh_flctl, chip);`; representative macros: `__SH_FLCTL_H__`, `FLCMNCR`, `FLCMDCR`, `FLCMCDR`, `FLADR`, `FLADR2`, `FLDATAR`, `FLDTCNTR`, `FLINTDMACR`, `FLBSYTMR`, `FLBSYCNT`, `FLDTFIFO`, `FLECFIFO`, `FLTRCR`, `FLHOLDCR`, `_4ECCCNTEN`.

## Control Flow

The driver programs FLCMNCR/FLCMDCR/FLADR/FLDATAR/FIFO/ECC registers, tracks staged SEQIN/ERASE command parameters, uses DMA channels when available, and maps `mtd_info` back to the enclosing `sh_flctl` through the embedded `nand_chip`.

## State and Persistence Behavior

Runtime state includes the raw NAND chip, platform device, PM QoS request, MMIO base, FIFO address, data buffer, command staging fields, address-cycle settings, base register values, page-size/ECC/hold/QoS flags, DMA channels, and DMA completion.

## Dependencies and Integration Points

It depends on completions, MTD/raw NAND/partition APIs, PM QoS, platform devices, and DMA engine.

Direct includes observed in the source are: `#include <linux/completion.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/rawnand.h>`, `#include <linux/mtd/partitions.h>`, `#include <linux/pm_qos.h>`.

## Risks and Edge Cases

Clock divider bits, hold control, ECC result handling, and DMA FIFO synchronization are hardware-sensitive. The fixed `done_buff` size assumes maximum 2048+64 page/OOB data.

## Test Signals

Probe platform data variations, 512/2048 page modes, hardware ECC result classes, DMA read/write completion, timeout paths, and PM QoS hold behavior.

Source read signal: 180 lines, 5927 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/sh_flctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/sharpsl.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/sharpsl.h

## Purpose

Defines SharpSL NAND platform data for legacy Sharp handheld boards.

## Important APIs, Types, and Functions

The exported type is `struct sharpsl_nand_platform_data` with bad-block pattern, ECC OOB layout, partitions, partition count, and parser names.

Source-visible symbols include structs: `struct sharpsl_nand_platform_data`, `struct nand_bbt_descr	*badblock_pattern;`, `struct mtd_partition	*partitions;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `_MTD_SHARPSL_H`.

## Control Flow

The SharpSL NAND driver uses this board data to choose BBT scanning, ECC layout, and partition registration for its raw NAND chip.

## State and Persistence Behavior

Only static platform metadata is described.

## Dependencies and Integration Points

It depends on raw NAND and partition APIs.

Direct includes observed in the source are: `#include <linux/mtd/rawnand.h>`, `#include <linux/mtd/partitions.h>`.

## Risks and Edge Cases

Wrong bad-block pattern or ECC layout can make existing media unreadable or mark blocks incorrectly.

## Test Signals

Board probe, bad-block-pattern scans, ECC-layout compatibility, and fixed/parser partition registration.

Source read signal: 22 lines, 485 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/sharpsl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/spear_smi.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/spear_smi.h

## Purpose

Defines platform data for ST SPEAr SMI serial NOR controller instances.

## Important APIs, Types, and Functions

Key items are `MAX_NUM_FLASH_CHIP`, `DEFINE_PARTS`, `struct spear_smi_flash_info`, and `struct spear_smi_plat_data`.

Source-visible symbols include structs: `struct spear_smi_flash_info`, `struct mtd_partition *partitions;`, `struct spear_smi_plat_data`, `struct spear_smi_flash_info *board_flash_info;`, `struct device_node *np[MAX_NUM_FLASH_CHIP];`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__MTD_SPEAR_SMI_H`, `MAX_NUM_FLASH_CHIP`, `DEFINE_PARTS`.

## Control Flow

Platform code supplies controller clock rate, flash count, per-flash mapped base/size/fast-mode/partition data, and DT nodes; the SMI driver probes up to four serial NOR chips.

## State and Persistence Behavior

This is static platform/board configuration. Runtime MTD and controller state are allocated by the SMI driver.

## Dependencies and Integration Points

It depends on MTD core, partitions, platform devices, and device tree.

Direct includes observed in the source are: `#include <linux/types.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/partitions.h>`, `#include <linux/platform_device.h>`, `#include <linux/of.h>`.

## Risks and Edge Cases

Incorrect memory base/size or fast-mode capability can break reads, and partition macros must not create overlapping regions.

## Test Signals

Multi-flash probe, fast/slow mode selection, DT-node matching, and partition registration.

Source read signal: 66 lines, 1793 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/spear_smi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/spi-nor.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/spi-nor.h

## Purpose

Defines the SPI NOR core public contract: standard opcodes/status bits, SPI protocol encodings, controller capability masks, controller operations, command-extension modes, and `struct spi_nor` state.

## Important APIs, Types, and Functions

Important APIs include opcode/status macros, `enum spi_nor_protocol`, protocol-width helpers, `struct spi_nor_hwcaps`, capability masks, `struct spi_nor_controller_ops`, `enum spi_nor_cmd_ext`, `struct spi_nor`, flash-node accessors, and `spi_nor_scan()`.

Source-visible symbols include structs: `struct spi_nor_hwcaps`, `struct spi_nor;`, `struct spi_nor_controller_ops`, `struct flash_info;`, `struct spi_nor_manufacturer;`, `struct spi_nor_flash_parameter;`, `struct spi_nor`, `struct mtd_info		mtd;`, `struct mutex		lock;`, `struct spi_nor_rww`, `struct device		*dev;`, `struct spi_mem		*spimem;`; enums: `enum spi_nor_protocol`, `enum spi_nor_cmd_ext`, `enum spi_nor_protocol	read_proto;`, `enum spi_nor_protocol	write_proto;`, `enum spi_nor_protocol	reg_proto;`, `enum spi_nor_cmd_ext	cmd_ext_type;`; typedefs: none visible in this header; prototypes: `return spi_nor_get_protocol_data_nbits(proto);`, `return mtd_get_of_node(&nor->mtd);`; representative macros: `__LINUX_MTD_SPI_NOR_H`, `SPINOR_OP_READ_1_1_1_DTR`, `SPINOR_OP_READ_1_2_2_DTR`, `SPINOR_OP_READ_1_4_4_DTR`, `SPINOR_OP_READ_1_1_1_DTR_4B`, `SPINOR_OP_READ_1_2_2_DTR_4B`, `SPINOR_OP_READ_1_4_4_DTR_4B`, `SR_E_ERR`, `SR_P_ERR`, `SR1_QUAD_EN_BIT6`, `SR_BP_SHIFT`, `SR2_QUAD_EN_BIT1`, `SR2_QUAD_EN_BIT7`, `SNOR_PROTO_INST_MASK`, `SNOR_PROTO_INST_SHIFT`, `SNOR_PROTO_INST`.

## Control Flow

Controller drivers supply register/data read/write/erase operations and hardware capability masks. `spi_nor_scan()` identifies the flash, parses SFDP/fixups, fills opcodes/protocols/address width/erase parameters, sets MTD callbacks, and may use spi-mem dirmap descriptors for data paths.

## State and Persistence Behavior

Runtime state includes embedded `mtd_info`, lock, read-while-write synchronization state, SPI device handles, DMA bounce buffer, JEDEC ID, manufacturer/info pointers, address bytes, selected opcodes, protocol modes, flags, command-extension type, SFDP data, debugfs root, controller ops, flash parameters, dirmaps, and private data.

## Dependencies and Integration Points

It depends on MTD core, bit operations, and SPI memory APIs. It integrates with SPI NOR manufacturer/fixup tables, SFDP parsing, MTD partition registration, and SPI controller drivers.

Direct includes observed in the source are: `#include <linux/bitops.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/spi/spi-mem.h>`.

## Risks and Edge Cases

Capability priority controls high-speed protocol selection; wrong quad/octal/DTR enablement or 4-byte addressing can make data inaccessible. RWW synchronization must serialize reads/program/erase per bank.

## Test Signals

Scan common JEDEC/SFDP parts, protocol capability negotiation, 3-byte/4-byte addressing, quad/octal/DTR register handling, lock/unlock/security registers, bounce-buffer paths, dirmap reads/writes, and RWW contention.

Source read signal: 453 lines, 16734 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/spi-nor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/spinand.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/spinand.h

## Purpose

Defines the SPI NAND core contract, including spi-mem operation templates, status/config bits, manufacturer/device tables, on-die ECC, OTP support, bus-interface selection, operation variants, and `struct spinand_device`.

## Important APIs, Types, and Functions

Key exports are `SPINAND_*_OP` spi-mem templates, feature/status macros, ID/read-ID types, manufacturer tables, `spinand_op_variants`, `spinand_ecc_info`, OTP operation structs, `spinand_info` macros, `spinand_mem_ops`, `spinand_device`, conversion helpers, match/init, register/config/write-enable/select/wait/read/write helpers, OTP helpers, and MTD OTP setup.

Source-visible symbols include structs: `struct spinand_op;`, `struct spinand_device;`, `struct spinand_id`, `struct spinand_devid`, `struct spinand_manufacturer_ops`, `struct spinand_manufacturer`, `struct spinand_op_variants`, `struct spinand_ecc_info`, `struct spinand_ondie_ecc_conf`, `struct spinand_otp_layout`, `struct spinand_fact_otp_ops`, `struct otp_info *buf, size_t *retlen);`; enums: `enum spinand_readid_method`, `enum spinand_bus_interface`, `enum spinand_bus_interface iface);`, `enum spinand_bus_interface bus_iface;`, `enum spinand_readid_method rdid_method);`; typedefs: none visible in this header; prototypes: `return container_of(mtd_to_nanddev(mtd), struct spinand_device, base);`, `return nanddev_to_mtd(&spinand->base);`, `return container_of(nand, struct spinand_device, base);`, `int spinand_upd_cfg(struct spinand_device *spinand, u8 mask, u8 val);`, `int spinand_read_reg_op(struct spinand_device *spinand, u8 reg, u8 *val);`, `int spinand_write_reg_op(struct spinand_device *spinand, u8 reg, u8 val);`, `int spinand_write_enable_op(struct spinand_device *spinand);`, `int spinand_select_target(struct spinand_device *spinand, unsigned int target);`, `size_t spinand_otp_page_size(struct spinand_device *spinand);`, `size_t spinand_fact_otp_size(struct spinand_device *spinand);`, `size_t spinand_user_otp_size(struct spinand_device *spinand);`, `int spinand_set_mtd_otp_ops(struct spinand_device *spinand);`; representative macros: `__LINUX_MTD_SPINAND_H`, `SPINAND_RESET_1S_0_0_OP`, `SPINAND_WR_EN_1S_0_0_OP`, `SPINAND_WR_DIS_1S_0_0_OP`, `SPINAND_READID_1S_1S_1S_OP`, `SPINAND_SET_FEATURE_1S_1S_1S_OP`, `SPINAND_GET_FEATURE_1S_1S_1S_OP`, `SPINAND_BLK_ERASE_1S_1S_0_OP`, `SPINAND_PAGE_READ_1S_1S_0_OP`, `SPINAND_PAGE_READ_FROM_CACHE_1S_1S_1S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_FAST_1S_1S_1S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_3A_1S_1S_1S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_FAST_3A_1S_1S_1S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_1S_1D_1D_OP`, `SPINAND_PAGE_READ_FROM_CACHE_1S_1S_2S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_3A_1S_1S_2S_OP`.

## Control Flow

The SPI NAND core matches a read ID against manufacturer tables, selects the best read/write/update cache operation variants supported by the SPI memory controller, issues page-read/program-exec/block-erase sequences, polls status, applies on-die ECC status translation, and delegates generic NAND page requests through `nand_device`.

## State and Persistence Behavior

Runtime state includes embedded generic NAND device, SPI memory handle, mutex, read ID, flags, SSDR/ODTR operation templates, current bus interface, dirmaps, current target, ECC info, per-die config cache, data/OOB/scratch DMA-safe buffers, manufacturer/private data, chip configuration hooks, continuous-read capability, OTP descriptors, and read-retry hooks.

## Dependencies and Integration Points

It depends on MTD core, generic NAND core, SPI and SPI memory APIs, vendor manufacturer drivers, and optional on-die ECC/OTP implementations.

Direct includes observed in the source are: `#include <linux/mutex.h>`, `#include <linux/bitops.h>`, `#include <linux/device.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/nand.h>`, `#include <linux/spi/spi.h>`, `#include <linux/spi/spi-mem.h>`.

## Risks and Edge Cases

Operation variant selection must respect controller bus-width/DTR support. Config cache must stay coherent per die. Status ECC translation and raw-access flags affect MTD error semantics and user-visible raw/OOB reads.

## Test Signals

Manufacturer ID matching, read-ID method variants, SSDR/ODTR operation selection, config register update, target selection, wait timeouts, ECC status mapping, continuous read enable/disable, OTP read/write/lock, and page read/write across OOB modes.

Source read signal: 905 lines, 30951 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/spinand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/super.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/super.h

## Purpose

Declares helper functions for mounting filesystems on MTD devices with the modern fs_context mount API.

## Important APIs, Types, and Functions

Exports `get_tree_mtd()` and `kill_mtd_super()` under `__KERNEL__`.

Source-visible symbols include structs: `struct fs_context *fc));`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `extern void kill_mtd_super(struct super_block *sb);`; representative macros: `__MTD_SUPER_H__`.

## Control Flow

An MTD-aware filesystem passes a `fill_super` callback to `get_tree_mtd()`, which resolves/acquires the MTD device and constructs the superblock. `kill_mtd_super()` tears down the superblock and releases the MTD reference.

## State and Persistence Behavior

Runtime state is the mounted superblock and held MTD device reference; no persistent metadata is defined in this header.

## Dependencies and Integration Points

It depends on MTD core, VFS superblock/fs_context types, and filesystem implementations such as JFFS2 or other MTD filesystems.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`, `#include <linux/fs.h>`, `#include <linux/mount.h>`.

## Risks and Edge Cases

Mount/teardown must balance MTD references and handle invalid device names/numbers. Filesystems must still validate flash geometry and erase/write constraints.

## Test Signals

Mount failure paths, successful mount/unmount reference balancing, invalid MTD specifiers, and filesystem fill-super error cleanup.

Source read signal: 25 lines, 578 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/super.h -->
