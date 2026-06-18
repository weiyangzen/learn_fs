<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sun.c -->
# sources/distributed-fs/ceph-client/block/partitions/sun.c

## Purpose

`sun.c` parses Sun disk labels. It verifies the Sun label magic and checksum, supports optional VTOC sanity checks, and publishes up to eight Sun partition entries.

## Important APIs, Types, And Functions

The entry point is `sun_partition(struct parsed_partitions *state)`. It uses constants `SUN_LABEL_MAGIC`, `SUN_VTOC_SANITY`, and partition ids such as `SUN_WHOLE_DISK`. It reads `struct sun_disklabel` from sector 0 and emits partitions through `put_partition()`.

## Control Flow

The parser reads sector 0, verifies the magic, and computes the checksum across 16-bit words. It determines the number of entries from the VTOC when sane, otherwise defaults to the classic Sun count. For each entry, it skips empty partitions and whole-disk entries, computes the start from cylinder and sector geometry encoded in the label, emits size, and prints ` [sun]`.

## State And Persistence Behavior

There is no persistent kernel state. The persistent input is the Sun disk label. The parser fills `parsed_partitions` only during the scan.

## Dependencies And Integration Points

It depends on `check.h` and Sun partition definitions available through kernel partition headers. It is called by the generic block partition scanner.

## Risks And Edge Cases

Checksum validation and endian conversion are key correctness points. Whole-disk entries are skipped to avoid duplicate device nodes. Geometry-derived starts can be wrong if the on-disk label is malformed. `state->limit` bounds output slots.

## Test Signals

Tests should cover wrong magic, checksum failure, sane and legacy VTOC entry counts, whole-disk entries, sparse entries, and starts computed from cylinder offsets. Expected output includes ` [sun]` only for accepted labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sun.c -->
