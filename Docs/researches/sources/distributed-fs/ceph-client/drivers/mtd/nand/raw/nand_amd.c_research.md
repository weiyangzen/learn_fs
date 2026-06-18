# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_amd.c

## Purpose
`nand_amd.c` contains manufacturer-specific raw NAND hooks for AMD/Spansion/Cypress NAND devices. It adjusts generic extended-ID decoding for a known Spansion ID layout corner case and sets conservative bad-block-marker scan locations for SLC parts whose datasheets allow markers in multiple pages of an eraseblock.

## Important APIs, Types, and Functions
The exported object is `amd_nand_manuf_ops`, a `struct nand_manufacturer_ops` with `.detect = amd_nand_decode_id` and `.init = amd_nand_init`. `amd_nand_decode_id()` obtains the MTD and NAND memory-organization structures, calls `nand_decode_ext_id()`, then optionally overrides `pages_per_eraseblock` and `mtd->erasesize` for a Spansion/AMD five-byte ID pattern. `amd_nand_init()` checks `nand_is_slc()` and sets `NAND_BBM_FIRSTPAGE`, `NAND_BBM_SECONDPAGE`, and `NAND_BBM_LASTPAGE` when appropriate.

## Control Flow
During manufacturer detection, the raw NAND core calls the detect hook after matching the manufacturer. The hook first runs the generic extended-ID decoder. It then checks for a nonzero fifth ID byte, zero sixth through eighth ID bytes, and a decoded 512-byte page size. This pattern corresponds to Spansion S30ML-P ORNAND style IDs where the erase size implied by the generic NAND ID table may conflict with the extended ID. When matched, the function computes `pages_per_eraseblock` from ID byte 3 and updates the MTD erase size.

During manufacturer initialization, the NAND core calls `amd_nand_init()`. For SLC devices, it broadens bad-block marker policy so the core checks the first, second, and last page of each eraseblock. Non-SLC devices are left unchanged.

## State and Persistence Behavior
The file has no persistent state and allocates no runtime resources. It mutates the in-memory NAND geometry (`nand_memory_organization`) and MTD erase size during detection, and it mutates `chip->options` during initialization. Any on-flash bad-block information remains owned by the NAND core and device media.

## Dependencies and Integration Points
The file integrates directly with raw NAND manufacturer dispatch from `internals.h`, `nand_decode_ext_id()`, `nanddev_get_memorg()`, MTD geometry, SLC detection, and NAND bad-block-marker option flags. It has no platform, OF, IRQ, DMA, clock, or MTD registration logic.

## Risks
The detection override is intentionally narrow, but it depends on ID-byte interpretation and a specific 512-byte page-size condition. If a future AMD/Spansion-compatible device reuses the same byte pattern with different semantics, eraseblock geometry could be misdecoded. The SLC bad-block-marker expansion can increase scan work and may affect devices with unusual marker conventions, but it is conservative for the cited Cypress/Spansion behavior.

## Test Signals
Useful signals include ID decode tests for the Spansion repeating-byte pattern, negative tests where any of bytes 4 through 7 or page size do not match, verification that `mtd->erasesize` follows the recomputed pages-per-eraseblock, SLC initialization setting all three BBM location flags, and non-SLC initialization leaving BBM options untouched.
