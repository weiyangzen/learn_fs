# sources/distributed-fs/ceph-client/drivers/scsi/sense_codes.h

## Purpose

`sense_codes.h` is a macro-consumed table of T10 SCSI Additional Sense Code and Additional Sense Code Qualifier values mapped to human-readable descriptions. It supports SCSI sense decoding and diagnostic logging.

## Important APIs, Types, and Functions

There are no functions or C types. The interface is repeated `SENSE_CODE(0xAABB, "description")` entries, with ASC in the high byte and ASCQ in the low byte. Comments document wildcard ranges that are not represented as concrete entries, such as `0x40NN`, `0x4DNN`, and `0x70NN`.

## Control Flow

The including file defines `SENSE_CODE()`, includes this header to generate switch cases or lookup tables, then undefines the macro. This header has no include guard or standalone declarations by design.

## State and Persistence Behavior

There is no mutable runtime state. The including translation unit turns the table into static lookup data. Updating this file changes decoded sense text after rebuild.

## Dependencies and Integration Points

The file depends on an external `SENSE_CODE` macro. It integrates with SCSI sense-printing helpers used by disk, enclosure, transport, and other SCSI drivers when reporting command failures.

## Risks and Edge Cases

Syntax errors, duplicate codes, stale descriptions, or unescaped strings affect every include site or degrade diagnostics. Newer or vendor-specific ASC/ASCQ values may be absent and must fall back to numeric output. Tests that assert exact log strings can be sensitive to description updates.

## Test Signals

Build every include site. Verify representative lookups including `0x0000`, `0x0401`, `0x2000`, `0x2400`, `0x2800`, `0x2900`, `0x3A00`, `0x5000`, `0x7400`, and unknown/vendor-specific codes. Static checks can detect duplicate numeric keys and malformed macro entries.
