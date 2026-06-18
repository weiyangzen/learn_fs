# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_diag.h

## Purpose

`dasd_diag.h` defines the constants, numeric request codes, block-number typedefs, and packed/aligned parameter structures used by the z/VM DIAG DASD discipline in `dasd_diag.c`. It is the local ABI description for DIAG 0x250 block I/O and DIAG 0x210 characteristics data.

## Important APIs, Types, and Functions

- `MDSK_WRITE_REQ` and `MDSK_READ_REQ` identify per-block write/read entries in a DIAG bio list.
- `INIT_BIO`, `RW_BIO`, and `TERM_BIO` are the function selectors passed to DIAG 0x250 for setup, I/O, and teardown.
- `DEV_CLASS_FBA` and `DEV_CLASS_ECKD` classify supported virtual DASD device types.
- `DASD_DIAG_CODE_31BIT` and `DASD_DIAG_CODE_64BIT` identify external-interrupt subcodes and therefore how the interrupt parameter is decoded.
- `DASD_DIAG_RWFLAG_ASYNC` and `DASD_DIAG_RWFLAG_NOCACHE` control runtime I/O behavior.
- `DASD_DIAG_FLAGA_FORMAT_64BIT` and `DASD_DIAG_FLAGA_DEFAULT` select the 64-bit parameter format used by this driver.
- `blocknum_t` and `sblocknum_t` provide unsigned/signed 64-bit block numbering.
- `struct dasd_diag_characteristics` is the DIAG 0x210 characteristics layout.
- `struct dasd_diag_bio` is one block operation descriptor: type, status, ALET, block number, and buffer pointer.
- `struct dasd_diag_init_io` describes DIAG block I/O initialization/termination state including device number, block size, offset, start block, and end block.
- `struct dasd_diag_rw_io` describes an RW request, including device number, key, flags, block count, interrupt parameter, and pointer to a bio list.

## Control Flow

The header has no executable control flow. Its structures are populated by `dasd_diag.c`: initialization calls fill `dasd_diag_init_io`, request start fills `dasd_diag_rw_io`, and request build fills arrays of `dasd_diag_bio`. The external interrupt handler uses the DIAG subcode constants to interpret 31-bit versus 64-bit interrupt parameters.

## State and Persistence Behavior

The header defines transient in-memory layouts only. State is held by instances embedded in `struct dasd_diag_private`, allocated request payloads, or temporary stack/heap objects in the DIAG discipline. The explicit `packed` and `aligned` attributes are part of the ABI contract with z/VM and are more important than normal C layout convenience.

## Dependencies and Integration Points

The definitions depend on Linux fixed-width integer types and are included by `dasd_diag.c`. The layouts integrate directly with S/390 DIAG instructions, z/VM minidisk I/O conventions, and the DASD discipline's request conversion path. `struct dasd_diag_characteristics` is cast-compatible with the DIAG 0x210 call site.

## Risks

The principal risk is ABI drift. Changing field order, size, signedness, pointer width assumptions, packing, or alignment can make DIAG 0x250 or 0x210 fail or corrupt I/O. The default 64-bit format must remain consistent with the interrupt subcode handling in `dasd_diag.c`. The pointer in `struct dasd_diag_bio` and `bio_list` in `struct dasd_diag_rw_io` mean addressability and format flags must match the running architecture/hypervisor expectations.

## Test Signals

Compile-time structure-size/alignment checks, successful 64-bit DIAG initialization, correct external interrupt parameter decoding, valid block count/end block results, and read/write completion against z/VM virtual FBA/ECKD disks are the relevant signals. Runtime failures often surface as DIAG rc 3 exceptions, unsupported-device errors, or missing asynchronous completions.
