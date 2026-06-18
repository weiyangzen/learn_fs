# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_fba.c

## Purpose
This file implements the S/390 DASD FBA discipline and ccw driver for fixed-block architecture DASD devices. Compared with ECKD, it has a simpler linear block model: read device characteristics, expose one block device, build Define Extent plus Locate plus READ/WRITE channel programs, support discard/write-zeroes, and use default DASD ERP.

## Important APIs, Types, and Functions
The binding is `dasd_fba_driver` with `dasd_fba_ids`; the discipline is `dasd_fba_discipline`. Per-device state is `struct dasd_fba_private`, containing only `struct dasd_fba_characteristics`. Startup and geometry use `dasd_fba_check_characteristics()`, `dasd_fba_do_analysis()`, and `dasd_fba_fill_geometry()`. Channel-program helpers are `define_extent()`, `locate_record()`, `dasd_fba_build_cp_regular()`, `dasd_fba_build_cp_discard()`, and `dasd_fba_build_cp()`. Cleanup and diagnostics use `dasd_fba_free_cp()`, `dasd_fba_dump_sense()`, and `dasd_fba_dump_sense_dbf()`.

## Control Flow
Module init converts the discipline name to EBCDIC, allocates a DMA-capable zero page for discard workarounds, registers the ccw driver, and waits for probing. Online attaches the FBA discipline through the generic DASD online path.

`dasd_fba_check_characteristics()` allocates private state and a DASD block object, reads 32 bytes of FBA characteristics, sets default timeout/retries, marks all paths allowed with `LPM_ANYPATH`, sets read-only state when appropriate, enables the DASD discard feature bit, and logs capacity and block size. `dasd_fba_do_analysis()` validates the hardware block size, sets `block->blocks`, `bp_block`, and the 512-sector-to-block shift. Geometry uses a synthetic 16-head layout with sectors scaled by block size.

Normal read/write request building validates full-block bio segments, computes first and last logical records, decides whether IDALs are needed, allocates a CQR, writes a Define Extent for the requested range, emits one Locate Record for data-chaining devices or one per block for devices lacking data chaining, then emits one READ or WRITE CCW per block. Discard and write-zeroes requests are implemented as WRITE commands: unaligned leading/trailing parts write real zero data from `dasd_fba_zero_page`, while page-aligned middle ranges use a zero-length WRITE command that z/VM treats as block discard/zeroing.

## State and Persistence
State is volatile per-device private data plus the generic DASD block object. The zero page is global module state. FBA characteristics determine block count, block size, feature behavior, and data-chain behavior. Hardware state is affected only by normal write/discard I/O; the driver does not maintain persistent metadata.

## Dependencies and Integration Points
The file depends on the ccw bus, DASD core, block request iteration, IDAL helpers, DASD page-cache bounce buffering, generic path verification, and default ERP helpers. It integrates through `dasd_discipline` callbacks for analysis, I/O construction/freeing, max sectors, geometry, state-change detection, sense dumping, and information reporting. User-visible behavior is a standard DASD block device with discard support and FBA information from DASD ioctls.

## Risks and Test Signals
Risk areas include block-size validation, request segments that are not multiples of the FBA block size, IDAL and optional page-cache bounce cleanup, different Locate Record chaining for devices without data chaining, discard alignment workarounds for z/VM, and zero page lifetime. The init path currently frees the zero page only in cleanup; if `ccw_driver_register()` fails after zero-page allocation, the failure path should be checked for leakage. Test signals include probe on 3370/9336 IDs, readonly flag handling, blocksize rejection, read/write across multi-segment requests, devices with and without data chaining, IDAL-needed memory, page-cache bounce reads/writes, discard and write-zeroes for unaligned/aligned ranges, state-change attention handling, default ERP retry exhaustion, and sense dump output.
