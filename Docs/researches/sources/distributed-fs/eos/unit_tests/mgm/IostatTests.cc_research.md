# sources/distributed-fs/eos/unit_tests/mgm/IostatTests.cc

## Purpose
Tests MGM IO statistics collection configuration, UDP popularity target encoding, rolling transfer-period buffers, percentile transfer duration calculation, and sequential transfer accounting.

## Important APIs, types, and functions
Coverage includes `Iostat`, `StartCollection`, `StopCollection`, `StoreIostatConfig`, `ApplyConfig`, `AddUdpTarget`, `RemoveUdpTarget`, `EncodeUdpPopularityTargets`, and `IostatPeriods` methods such as `Add`, `GetDataInPeriod`, `StampBufferZero`, `UpdateTransferSampleInfo`, `GetTimeToPercComplete`, `GetLongestTransferTime`, and `GetTotalSum`.

## Control flow
Fixture tests verify initial config keys, start/stop state, mock FsView config storage/application, and UDP target list mutation. Period tests add long transfers, query many rolling windows, stamp bins to zero, test integer and fractional per-bin accumulation, update percentile summaries, and generate random sequential transfers.

## State and persistence
`Iostat` stores in-memory running/config state and persists config through `FsView` global config in production. `IostatPeriods` maintains rolling time-bin buffers and percentile summaries.

## Dependencies and integration points
Depends on Google Test, MGM iostat internals, FsView, maps, and common random utilities. It feeds MGM monitoring/reporting and popularity logic.

## Risks and test signals
The period test is broad but loop-heavy. Random sequential transfer lengths introduce slight nondeterminism. Important risks include off-by-one bin boundaries, ceil rounding, config key drift, and UDP target serialization compatibility.
