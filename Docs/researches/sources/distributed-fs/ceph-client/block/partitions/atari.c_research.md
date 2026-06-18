<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/atari.c -->
# sources/distributed-fs/ceph-client/block/partitions/atari.c

## Purpose
`atari.c` detects Atari AHDI partition tables, XGM extended chains, and ICD/Supra extra partition entries.

## Important APIs, Types, and Functions
- Entry point: `atari_partition()`.
- Validation macros/helpers: `VALID_PARTITION()` and `OK_id()`.
- On-disk structures are defined in `atari.h`: `rootsector` and `partition_info`.

## Control Flow
The parser first requires a 512-byte logical block size because the Atari format assumes 512-byte LBAs. It reads sector 0 and accepts the table only if at least one primary partition entry is active, alphanumeric, and within disk size. It emits `AHDI`, iterates four primary entries, publishes ordinary active entries, and follows `XGM` extended chains by reading rootsectors at linked offsets and publishing their first partition. If no XGM format was found, it optionally scans ICD/Supra entries 5 through 12 and publishes entries with accepted IDs (`GEM`, `BGM`, `RAW`, `LNX`, `SWP`).

## State and Persistence Behavior
State is limited to `parsed_partitions` and printk/seq output. The parser does not persist or modify Atari rootsector data.

## Dependencies and Integration Points
It depends on `check.h`, `atari.h`, `ctype`, big-endian conversion, and `CONFIG_ATARI_PARTITION`. It is invoked after Amiga in the generic probe list.

## Risks and Edge Cases
The format has no reliable magic, so false positives are mitigated by entry validation. XGM chains can be malformed: missing active first subpartition, wrong second-entry ID, read failure, and partition-limit exhaustion are handled with messages and breaks. Non-512 logical sectors are rejected early to prevent bad arithmetic.

## Test Signals
Test valid AHDI, XGM extended, ICD/Supra, malformed chains, non-512 logical block devices, invalid active entries, out-of-range sizes, and partition-limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/atari.c -->
