<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/atari.h -->
# sources/distributed-fs/ceph-client/block/partitions/atari.h

## Purpose
`atari.h` defines the packed on-disk Atari rootsector and partition-entry layout consumed by `atari.c`.

## Important APIs, Types, and Functions
There are no functions. `struct partition_info` stores flags, a three-byte ID, big-endian start sector, and big-endian size. `struct rootsector` contains boot-code padding, eight ICD partition slots, disk size, four primary entries, bad-sector-list fields, and checksum.

## Control Flow
The header has no executable flow. Its field offsets determine how `atari_partition()` interprets sector zero and optional ICD entries.

## State and Persistence Behavior
The structs model persistent Atari disk metadata. The Linux parser reads them but does not update them.

## Dependencies and Integration Points
It includes `<linux/compiler.h>` for `__packed` and uses Linux integer/endian types. It is tightly coupled to `atari.c`; changes must preserve binary layout.

## Risks and Edge Cases
Any padding/layout change would corrupt parsing. The checksum field exists but is not used by the current parser. Comments document ID semantics but validation policy lives in `atari.c`.

## Test Signals
Compile layout checks, parsing known Atari images, big-endian field conversion tests, and structure size/offset assertions are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/atari.h -->
