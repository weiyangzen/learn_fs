# sources/distributed-fs/eos/mgm/drain/Drainer.hh

## Purpose
Declares the central drainer service that coordinates multiple per-filesystem drains and exposes configuration and monitoring APIs.

## Important APIs and Types
- `DrainMap` maps node hostport strings to sets of active `DrainFs` supervisors.
- `DrainHdrInfo` maps display column names to internal `DrainTransferJob` info tags.
- Public API includes lifecycle (`Start`, `Stop`), drain control (`StartFsDrain`, `StopFsDrain`), thread-pool access/info, job info rendering, and config apply/set/serialize.
- Private helpers store config, run the central thread, handle queued requests, and stop all active drains.

## Control Flow and State
The header defines an assisted central thread, protected active drain map, pending queue, shared transfer thread pool, and atomic max-filesystems-per-node limit. `StartFsDrain` and `StopFsDrain` document that callers must hold the `FsView` read lock.

## Dependencies and Integration Points
Depends on MGM namespace, logging, thread pool, assisted thread, filesystem types, `DrainFs`, `DrainTransferJob`, and table formatting. The implementation integrates with `FsView`, `gOFS`, and master state.

## Risks
- `mCfgMutex` is declared but unused in the implementation.
- `DrainMap` set ordering by shared pointer can make output/order nondeterministic.
- The public `GetThreadPool` returns a mutable reference to the internal pool, which allows external code to alter behavior outside `Drainer` config paths.
- Stop/destructor lifecycle depends on `AssistedThread::join` being safe when the thread was never started.

## Test Signals
Header-level tests should validate API use with required locks, config serialization, mutable thread-pool access expectations, and drain map/pending queue behavior through public methods.
