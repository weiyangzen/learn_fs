# sources/distributed-fs/eos/unit_tests/mgm/tgc/FreedBytesHistogramTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/tgc/FreedBytesHistogramTests.cc

Purpose: tests `FreedBytesHistogram`, which tracks bytes freed over a rolling time window for tape garbage collection reporting.

Important APIs and types: `FreedBytesHistogram`, `DummyClock`, `RealClock`, TGC constants, `bytesFreed`, `getTotalBytesFreed`, `getNbBytesFreedInLastNbSecs`, `getFreedBytesInBin`, `setBinWidthSecs`, and exceptions `InvalidNbBins`, `InvalidBinWidth`, `InvalidBinIndex`, and `TooFarBackInTime`.

Control flow: constructor tests validate bin count/width and zero initialization. Invalid constructor and setter tests assert exceptions for zero or too-large values. The main sequence advances a dummy clock through bins, records bytes, checks rolling totals by lookback duration, then advances beyond one full history window. Bin-width migration tests change width from 3 seconds to 4, 5, 6, 2, and 1, asserting redistribution into new bins. Additional tests cover multiple passes, many updates in the same bin, and a time gap larger than the histogram window.

State and persistence: histogram state is in-memory rolling bins plus total freed bytes. Dummy clock provides deterministic time.

Dependencies and integration: feeds TGC telemetry and JSON/status reporting. Accurate rolling-window math is important for operational decisions.

Risks and test signals: this is high-value coverage for off-by-one time boundaries, bin migration, and history-window overflow. It does not test concurrency.
