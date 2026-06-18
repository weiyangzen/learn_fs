# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Printing.hh

## Purpose
This header declares formatting options and helper methods for inspector metadata output. It defines which fields are shown by default for file and container records and exposes static formatting functions.

## Important APIs, Types, and Functions
`FilePrintingOptions` contains booleans for id, parent/container id, uid/gid, size, layout id, flags, name, link name, ctime, mtime, checksum, locations, unlink locations, xattrs, stime, and atime. `ContainerPrintingOptions` controls id, parent, uid/gid, tree size, mode, flags, name, ctime, mtime, stime, and xattrs. `Printing` declares multi-line file/container print methods, time conversion methods, `escapeNonPrintable()`, and templated `parseTimespec()`.

## Control Flow
The header has no complex runtime flow. `parseTimespec()` conditionally copies raw bytes into a local `timespec` and returns it; all other behavior is implemented in `Printing.cc`.

## State and Persistence Behavior
No state is stored. The option structs are value configuration objects for output functions. The time parser reflects the persistent metadata encoding of timestamps as raw `timespec` bytes in protobuf fields.

## Dependencies and Integration Points
It includes EOS namespace macros plus file and container protobuf headers. It is consumed by `OutputSink`, `Inspector`, and any code needing inspector-compatible metadata formatting.

## Risks and Test Signals
The raw-byte timestamp parser needs tests for empty and correctly sized fields. Option defaults should be snapshot-tested because inspector CLI output depends on them. Compile tests should ensure the header can be included without pulling scanner or qclient dependencies.
