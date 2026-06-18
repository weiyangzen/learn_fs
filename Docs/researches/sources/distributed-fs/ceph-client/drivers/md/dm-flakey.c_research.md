# `sources/distributed-fs/ceph-client/drivers/md/dm-flakey.c`

## Purpose

`dm-flakey.c` implements the `flakey` test target, which simulates intermittent device failures and data corruption. It alternates between configured up and down intervals and can error reads, drop or error writes, corrupt fixed bytes, or randomly corrupt reads/writes with configured probabilities.

## Important APIs, Types, and Functions

`struct flakey_c` stores the backing device, start time, offset, up/down intervals, feature flags, fixed corruption parameters, and random corruption probabilities. `struct per_bio_data` records whether a bio can be corrupted and preserves the original iterator for read completion corruption. `parse_features()` handles `error_reads`, `drop_writes`, `error_writes`, `corrupt_bio_byte`, `random_read_corrupt`, and `random_write_corrupt`, while rejecting conflicting combinations. `flakey_map()` implements interval-based behavior. `flakey_end_io()` applies read corruption after successful lower-device completion. `clone_bio()` creates private write copies so corrupting a write does not mutate the caller's original bio.

## Control Flow

Constructor syntax is `<dev_path> <offset> <up interval> <down interval> [<#feature args> [<arg>]*]`. If no feature is specified, down intervals default to erroring both reads and writes. During up intervals, bios are simply remapped. During down intervals, reads may be killed, passed through for later corruption, or randomly corrupted on completion. Writes may be dropped, failed, fixed-byte corrupted, random-byte corrupted, or passed through. Zone-management operations bypass failure behavior and are always remapped.

## State and Persistence Behavior

The target has no persistent metadata. Runtime behavior is based on `jiffies - start_time` modulo the up/down period, so reloading the table resets the failure schedule. Corruption settings and random probabilities live only in `flakey_c`.

## Dependencies and Integration Points

The target integrates through `.ctr`, `.dtr`, `.map`, `.end_io`, `.status`, `.prepare_ioctl`, `.iterate_devices`, and optional zoned `.report_zones`. It uses device-mapper argument parsing, per-bio data, random helpers, bio cloning, page allocation, and block ioctl forwarding. It advertises zoned host-managed support and crypto pass-through.

## Risks and Edge Cases

Feature conflicts are important: dropping or erroring writes cannot be combined with write corruption, and erroring reads cannot be combined with read corruption. Write corruption clones can fail allocation, in which case the original bio is remapped uncorrupted. Random corruption probabilities are compared against `PROBABILITY_BASE` and should be tested at 0, 1, and full-base values. The target mutates data buffers, so read corruption only occurs after successful IO and only when the saved iterator still describes the original data range.

## Test Signals

Tests should cover interval transitions, default all-IO failure mode, each feature and conflict, fixed-byte corruption offsets, flag-mask matching, random corruption probabilities, write-clone allocation failure behavior, zone-management bypass, status table round-trip, ioctl forwarding, and report-zones forwarding.
