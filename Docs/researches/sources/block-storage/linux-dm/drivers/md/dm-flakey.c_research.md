# File Research: sources/block-storage/linux-dm/drivers/md/dm-flakey.c

## Role
Implements the `flakey` device-mapper test target, which alternates between up and down intervals and can fail, drop, or corrupt IO during the down interval.

## Target Interface
- Constructor syntax is `<dev_path> <offset> <up interval> <down interval> [<#feature args> [<arg>]*]`.
- Intervals are seconds measured from target construction time using jiffies.
- Optional features are `drop_writes`, `error_writes`, and `corrupt_bio_byte <Nth_byte> <r|w> <value> <bio_flags>`.
- `drop_writes` and `error_writes` are mutually exclusive and cannot be combined with write corruption.

## IO Behavior
- During up intervals, bios are remapped normally to the lower device and start offset.
- During down intervals:
  - Plain reads are killed unless a feature path maps them for later corruption or write-handling semantics.
  - Writes can be silently ended (`drop_writes`), completed with error (`error_writes`), corrupted before submission, or killed by default.
  - Reads submitted during the down interval can be corrupted in `flakey_end_io()` after successful lower-device completion.
- Zone management operations bypass flakey failure logic and are remapped.

## Corruption Logic
- `corrupt_bio_data()` overwrites the configured 1-based byte offset in the bio payload with an 8-bit value.
- Optional `bio_flags` require all configured flags to be present before corruption.
- Direction controls whether corruption happens before lower-device write submission or after read completion.

## Status and Device Helpers
- Table status reconstructs the lower device, offset, intervals, and feature list.
- `prepare_ioctl()` passes ioctls through only when the target covers the whole lower device with zero offset.
- Zoned devices support `report_zones` by remapping the requested sector through the target offset.

## Important Invariants
- Per-bio data records whether a bio was submitted during a down interval so `end_io` only mutates eligible reads.
- Up/down interval sum must be nonzero and must not overflow.
- Feature parser tracks duplicate/conflicting options explicitly.

## Filesystem/Storage Relevance
`dm-flakey` is a broad failure-injection target for testing filesystem and storage-stack behavior under intermittent device failure, lost writes, write errors, and data corruption.

## Notable Risks
- Dropped writes are completed successfully, intentionally modeling dangerous storage behavior.
- Corruption is byte-offset based inside bio segments and does not understand filesystem or sector structure.
