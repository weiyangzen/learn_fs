# sources/distributed-fs/eos/mgm/inspector/FileInspectorStats.hh

## Purpose

`FileInspectorStats.hh` defines the data model for file-inspector scan results and the string keys used when serializing those results. The struct aggregates health classifications, time distributions, size distributions, owner/group cost and byte accounting, total counters, and link statistics.

## Important APIs, Types, and Functions

- Serialization key macros include `SCAN_STATS_KEY`, `FAULTY_FILES_KEY`, access/birth/birth-vs-access keys, size-distribution keys, size-vs-birth keys, cost/byte keys, fault count, scan time, and link keys.
- `struct FileInspectorStats` declares copy/move constructors and assignment operators implemented in `FileInspectorStats.cc`.
- `ScanStats` is a layout-id to named-counter map for scan classifications such as zero-size, volume, physical size, missing location, shadow location, and replication deltas.
- `FaultyFiles` maps failure type to file id and layout id examples.
- Access, birth, birth-vs-access, size, and birth-vs-size maps capture histogram data.
- `UserCosts`, `GroupCosts`, `TotalCosts`, `UserBytes`, `GroupBytes`, and `TotalBytes` are two-element disk/tape accounting arrays.
- Scalar counters include `NumFaultyFiles`, `TotalFileCount`, `TotalLogicalBytes`, `HardlinkCount`, `HardlinkVolume`, `SymlinkCount`, and `TimeScan`.

## Control Flow

This header has no runtime control flow beyond constructors. The default constructor initializes `TimeScan` to zero and in-class initializers set totals/link counters to zero. `FileInspector::Process()` fills the maps and counters, `FileInspectorStats.cc` copies/moves them, and `FileInspector::QdbHelper` serializes a subset of the fields.

## State and Persistence Behavior

The struct is the state container for both current and last file-inspector scans. Key macros define the persistence schema used by QuarkDB hash storage. The schema includes keys for size distributions and birth-vs-size distributions, but the inspected `QdbHelper::Store()`/`Load()` implementation does not use those keys. This mismatch means the header advertises persistence fields that may not survive restart.

## Dependencies and Integration Points

The header depends on standard maps/sets/atomics, EOS namespace macros, and qclient. It is included by `FileInspector.hh` and implemented by `FileInspectorStats.cc`. Its field names and key macros are coupled to `common/json/Json.hh` `Marshal`/`Unmarshal` calls in `FileInspector.cc`.

## Risks and Edge Cases

- Costs are stored in `uint64_t` maps even though `FileInspector::Process()` computes disk/tape costs as doubles, causing truncation.
- Key macro `BIRTH_VS_ACCESS_TIME_VOLUME_KEY` has value `birth-vs-access-volume-files`, which is awkwardly named and should be kept compatible if already persisted.
- Size and birth-vs-size key macros can give a false sense of persistence coverage because current storage code omits them.
- Copy/move assignment must be kept in sync manually with this struct; missing fields cause silent loss of stats.
- `qclient/QClient.hh` appears unnecessary in this pure data header and increases compile coupling.

## Test Signals

Tests should verify default initialization, copy/move preservation of every field, JSON marshal/unmarshal compatibility for all map and array shapes, persistence key coverage against `QdbHelper::Store()`/`Load()`, and cost precision expectations for fractional cost accumulation.
