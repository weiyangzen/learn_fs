# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/OutputSink.cc

## Purpose
This file implements output formatting for inspector metadata rows. It converts file and container protobuf fields into string maps, augments rows with resolved paths or child counts, and provides stream, JSON array, and JSON-lines sink implementations.

## Important APIs, Types, and Functions
`populateMetadata(ContainerMdProto, ContainerPrintingOptions, map&)` emits cid, parent id, uid/gid, tree size, mode, flags, name, ctime, mtime, stime, and xattrs according to options. `populateMetadata(FileMdProto, FilePrintingOptions, map&)` emits fid, parent/container id, uid/gid, size, layout, flags, name, link name, ctime, mtime, checksum, locations, unlink locations, xattrs, stime, and atime. `populateFullPath()` waits on scanner-provided full-path futures and suppresses path output on exceptions. `countAsString()` waits on count futures and emits `N/A` on failure.

`OutputSink::print()` overloads dispatch protobufs to maps. `printWithCustomPath()` adds a supplied path. `printWithAdditionalFields()` merges caller-provided fields with file metadata. `StreamSink::print()` emits escaped `key=value` pairs. `JsonStreamSink` wraps records in one JSON array. `JsonLinedStreamSink` emits one compact JSON object per line and overrides JSON-value printing.

## Control Flow
The common flow is: create a `std::map`, populate selected metadata fields, optionally wait for async path/count futures, then call the virtual map `print()` method. Stream output iterates the map in key order. JSON array output prints an opening bracket at construction, inserts commas between records, and prints a closing bracket in the destructor. JSON-lines output uses `Json::StreamWriter` with empty indentation.

## State and Persistence Behavior
This file manages no persistent namespace state. It consumes protobuf state and scanner futures. Its main stateful behavior is output framing in `JsonStreamSink::mFirst` and the JSON-lines writer object. Moving scanner futures while resolving paths/counts means the associated scanner item should not be reused for another path/count read afterward.

## Dependencies and Integration Points
It depends on `FileScanner::Item`, `ContainerScanner::Item`, `Printing`, EOS checksum serialization, protobuf types, folly futures, and jsoncpp. It is the formatting layer used by `Inspector` scans and layout checks.

## Risks and Test Signals
There are option-gating mistakes worth testing: container `flags` is guarded by `showMode`, and file `unlink_locations` is guarded by `showLocations` rather than `showUnlinkLocations`. Futures are waited synchronously, so slow path resolution or count queries can stall output. Tests should cover escaping, JSON array destructor framing, JSON-lines custom JSON values, failed path futures, failed count futures, all print option combinations, and deterministic key ordering.
