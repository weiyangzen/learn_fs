<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libbfd.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/libbfd.h

## Purpose

`libbfd.h` declares perf's optional libbfd integration and provides stubs when libbfd support is absent.

## Important APIs, Types, and Functions

With `HAVE_LIBBFD_SUPPORT`, it declares addr2line, DSO a2l cleanup, symbol disassembly, build-id reading, debuglink reading, and BPF disassembly. Without libbfd, inline stubs return failure or no-op, with BPF disassembly returning `SYMBOL_ANNOTATE_ERRNO__NO_LIBOPCODES_FOR_BPF`.

## Control Flow

Build configuration selects real declarations or stubs at compile time. Callers can invoke the functions unconditionally and handle failure.

## State and Persistence Behavior

The header defines no state. Real implementations cache state in DSOs.

## Dependencies and Integration Points

It depends on perf annotate, build-id, DSO, inline-node, and symbol types. It integrates symbolization and annotation code with optional libbfd availability.

## Risks and Edge Cases

Stub return values must match caller expectations. Header comments use C++-style comments around preprocessor branches, which is accepted in this C codebase but should remain build-compatible.

## Test Signals

Build matrix tests should cover libbfd enabled and disabled, and callers should gracefully fall back when stubs return failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libbfd.h -->
