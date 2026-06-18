# sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/Printing.cc

## Purpose
This file implements reusable formatting helpers for namespace file and container protobufs. It is used by inspector commands that need full multi-line diagnostic output rather than compact key-value rows.

## Important APIs, Types, and Functions
`Printing::escapeNonPrintable()` turns non-printable bytes into `\xNN` sequences and handles NUL as `\x00`. `timespecToTimestamp()` formats seconds and nanoseconds as `sec.nsec`. `timespecToFileinfo()` combines `ctime_r()` output with the timestamp form. `printMultiline(ContainerMdProto)` prints ids, name, ownership, ctime/mtime/stime, tree size, mode, flags, and xattrs. `printMultiline(FileMdProto)` prints ids, name/link, ownership, size, times, octal flags, checksum, expected stripes, ETag, locations, unlink locations, and xattrs.

## Control Flow
The functions are direct serializers. Protobuf byte fields containing `timespec` are parsed by `Printing::parseTimespec()` from the header. File checksum strings are generated with `appendChecksumOnStringProtobuf()`, expected stripe count comes from `LayoutId::GetStripeNumber() + 1`, and ETags come from `calculateEtag()`.

## State and Persistence Behavior
No state is persisted or cached. The code only observes protobuf fields. It assumes serialized time byte strings are either empty or large enough to hold `struct timespec`; that assumption comes from the metadata serialization contract.

## Dependencies and Integration Points
It depends on layout id helpers, checksum helpers, ETag generation, string conversion, file metadata interfaces, and protobuf types. It is used by `Inspector` repair previews and per-object print commands.

## Risks and Test Signals
`parseTimespec()` copies `sizeof(timespec)` whenever the field is non-empty, so malformed short time fields could cause out-of-bounds reads. `timespecToFileinfo()` seeks back one byte after `ctime_r()` to remove the newline; stream state should be tested. Tests should cover empty and valid time fields, non-printable names/xattrs, checksum rendering, ETag rendering, octal flags, and location vector formatting.
