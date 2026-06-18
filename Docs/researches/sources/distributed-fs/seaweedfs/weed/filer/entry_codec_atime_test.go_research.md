# sources/distributed-fs/seaweedfs/weed/filer/entry_codec_atime_test.go

## Purpose
This file tests access-time handling in filer entry attribute protobuf conversion.

## Important APIs, Types, and Functions
- `TestEntryCodec_AtimeRoundTrip` verifies seconds and nanoseconds are encoded and decoded.
- `TestEntryCodec_AtimeZeroFallsBackToMtime` verifies older/missing atime fields default to mtime.
- `TestEntryCodec_AtimeSubSecondEpochPreserved` verifies `Atime=0` with nonzero `AtimeNs` is treated as a valid timestamp.

## Control Flow and State
Tests construct `Entry` or `FuseAttributes`, convert through `EntryAttributeToPb` and `PbToEntryAttribute`, and compare exact timestamps.

## State and Persistence Behavior
The tests protect compatibility of persisted metadata blobs, especially distinguishing missing atime from an actual timestamp in the first second of the Unix epoch.

## Dependencies and Integration Points
They use `filer_pb.FuseAttributes`, `util.FullPath`, and the conversion functions in `entry_codec.go`.

## Risks and Edge Cases
The sub-second epoch case is subtle because protobuf `Atime` seconds can be zero for both missing values and real timestamps; preserving `AtimeNs` prevents incorrect fallback.

## Test Signals
These are focused regression tests for atime serialization and backward compatibility.
