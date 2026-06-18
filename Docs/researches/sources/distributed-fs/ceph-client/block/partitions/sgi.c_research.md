<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sgi.c -->
# sources/distributed-fs/ceph-client/block/partitions/sgi.c

## Purpose

`sgi.c` parses SGI disk labels. It validates the SGI label magic and checksum, then publishes non-volume partitions from the SGI partition array.

## Important APIs, Types, And Functions

The entry point is `sgi_partition(struct parsed_partitions *state)`. It defines `SGI_LABEL_MAGIC`, SGI partition constants, local `struct sgi_disklabel`, and uses big-endian conversion for label fields. It calls `read_part_sector()` and `put_partition()`.

## Control Flow

The parser reads sector 0, checks the big-endian magic, computes the label checksum by summing 32-bit words, and rejects labels whose checksum is nonzero. It scans up to the SGI partition count and `state->limit`, skips empty entries and whole-volume entries, emits start/size pairs, and prints ` [sgi]`.

## State And Persistence Behavior

The parser holds only a sector mapping during the scan. SGI disklabel contents are persistent on disk; emitted partitions are transient parser results.

## Dependencies And Integration Points

It depends on `check.h` and endian helpers. It integrates through the block partition parser framework.

## Risks And Edge Cases

Checksum handling is important because SGI labels use a zero-sum scheme over the label block. The parser must skip volume-header/entire-volume entries to avoid duplicate whole-disk partitions. It does not deeply validate that starts and sizes fall inside device capacity.

## Test Signals

Tests should include wrong magic, bad checksum, empty entries, whole-volume entries, and valid SGI partitions. Expected signals are `0` for non-SGI, `1` with ` [sgi]` for valid labels, and correct big-endian start/size decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sgi.c -->
