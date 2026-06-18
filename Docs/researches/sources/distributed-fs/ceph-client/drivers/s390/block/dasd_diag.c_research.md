# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_diag.c

## Purpose

`dasd_diag.c` implements the DASD `DIAG` discipline for z/VM virtual DASD devices. Instead of using normal SSCH channel programs, it uses z/VM DIAG 0x250 calls to initialize block I/O, submit read/write block lists, terminate the DIAG environment, and complete asynchronous I/O through external interrupts.

## Important APIs, Types, and Functions

- `struct dasd_diag_private` stores per-device DIAG state: read-device-characteristics data, reusable RW and init I/O blocks, partition-table/label block offset, and CCW device ID.
- `struct dasd_diag_req` is embedded in `dasd_ccw_req->data` and holds a block count plus flexible array of DIAG bio descriptors.
- `__dia250()` is the inline assembly wrapper around `diag ...,0x250`, with exception-table handling and return-code composition.
- `dia250()` increments the DIAG statistic and calls `__dia250()`.
- `mdsk_init_io()` and `mdsk_term_io()` issue `INIT_BIO` and `TERM_BIO`.
- `dasd_start_diag()` fills `struct dasd_diag_rw_io`, submits `RW_BIO`, and maps return codes to synchronous success, asynchronous in-I/O, or error recovery.
- `dasd_ext_handler()` handles CP service external interrupts for 31-bit and 64-bit DIAG interrupt parameters and completes or requeues requests.
- `dasd_diag_check_device()` probes a device for DIAG support, reads characteristics, determines FBA/ECKD label block, finds block size, reads CMS label data, initializes block metadata, and starts the DIAG environment.
- `dasd_diag_build_cp()` converts a Linux block request into a `dasd_ccw_req` containing one `dasd_diag_bio` per DASD block.
- `dasd_diag_discipline` registers the discipline callbacks used by DASD core.

## Control Flow

Module init rejects non-z/VM machines, converts the discipline EBCDIC name, registers the CP service external interrupt handler, and publishes `dasd_diag_discipline_pointer`.

Device checking allocates private and block structures, calls `diag210()` for virtual device characteristics, selects label position (`pt_block` 1 for FBA, 2 for ECKD), terminates any old DIAG environment, and probes block sizes from 512 bytes through `PAGE_SIZE`. For each candidate it initializes DIAG I/O, reads the expected CMS label block synchronously, and terminates DIAG again. If a CMS1 label is found, the block size and count come from the label; otherwise the reported DIAG `end_block` is used. A final `mdsk_init_io()` sets the runtime block size; return code 4 marks the device read-only but is not fatal.

Request building validates read/write direction, computes first/last DASD record from request sectors and `s2b_shift`, verifies every bio segment is block-aligned, counts blocks, allocates enough request data for all DIAG bio entries, and fills each entry with type, 1-based DIAG block number, and buffer pointer. Start I/O then submits the whole bio list asynchronously by default. DIAG rc 0 means synchronous completion and returns `-EACCES` to signal only bottom-half scheduling is needed; rc 8 means asynchronous I/O started; other codes trigger DIAG ERP and `-EIO`.

The external interrupt handler filters DIAG subcodes, resolves the interrupt parameter to a CQR, verifies the request magic against the discipline, takes the CCW-device lock, handles pending clear, marks success or requeues on subcode error, optionally starts the next queued request immediately, manages timers, and schedules the device bottom half.

## State and Persistence Behavior

The discipline stores all device state in memory under `device->private` and `device->block`. Runtime state includes the DIAG I/O environment, block size/count, read-only flag, reusable I/O blocks, request retry counts, timers, status fields, and external interrupt completion timestamps. It has no durable persistence. `dasd_diag_erp()` tears down and reinitializes the DIAG environment after errors, and can update the read-only flag if z/VM reports access changed.

## Dependencies and Integration Points

The file integrates with z/VM DIAG 0x250 and DIAG 0x210, S/390 external interrupt registration, DASD core discipline callbacks, block request iteration, VTOC/CMS label formats, request allocation/free helpers, device timers, bottom-half scheduling, path verification, and generic DASD ERP postaction handlers. `dasd_diag.h` defines the packed ABI structures shared with the DIAG call.

## Risks

DIAG parameter structures are ABI-sensitive and packed/aligned; field or alignment regressions can break hypervisor calls. The code assumes full-block I/O and rejects partial-block segments. The external interrupt path trusts the interrupt parameter as a CQR after magic validation, so stale or corrupted interrupt parameters are critical. The block-size probing loop issues real synchronous reads and must clean up label/bio allocations on every failure. A correct distinction between rc 0, rc 4, rc 8, and exception rc 3 is essential for read-only detection, async completion, and unsupported 64-bit DIAG behavior.

## Test Signals

Useful signals include z/VM-only module load behavior, successful diag210 characteristic reads for FBA/ECKD virtual disks, block-size probing with and without CMS1 labels, read-only rc 4 handling, request build rejection for partial blocks or invalid direction, sync rc 0 and async rc 8 start paths, interrupt completion and fast-start of the next queued request, clear-pending completion, DIAG ERP reinitialization, and max-sector calculation from the static two-page request buffer.
