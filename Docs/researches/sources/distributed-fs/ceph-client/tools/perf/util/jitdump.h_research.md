<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jitdump.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/jitdump.h

## Purpose

`jitdump.h` defines the on-disk jitdump file format structures and constants used by JIT runtimes and perf's jitdump reader.

## Important APIs, Types, and Functions

It defines magic values, version, alignment macros, timestamp flag bits, `struct jitheader`, `enum jit_record_type`, record prefix `struct jr_prefix`, record payloads for code load, close, move, debug info, and unwinding info, `union jr_entry`, and inline helpers `debug_entry_next()` and `debug_entry_file()`.

## Control Flow

There is no runtime flow beyond inline pointer arithmetic for variable-length debug entries. `jitdump.c` reads a header, then repeatedly reads a `jr_prefix` followed by `total_size` bytes and interprets the union by record id.

## State and Persistence Behavior

These structures are the persistent ABI of jitdump files. Header flags indicate whether record timestamps are perf-clock values or architecture timestamps requiring conversion.

## Dependencies and Integration Points

The header depends on fixed-width integer types, time headers, and string length for inline helpers. It integrates JIT runtimes that emit dumps with perf inject/report tooling.

## Risks and Edge Cases

The ABI is packed only by C layout convention; producers and consumers must agree on sizes and alignment. Variable-length strings and debug entries require careful `total_size` validation by readers. Reserved flags must be rejected to avoid misinterpreting future formats.

## Test Signals

Format tests should validate magic, swapped magic, version, reserved flags, 8-byte alignment, debug-entry iteration, and each record type's serialized size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jitdump.h -->
