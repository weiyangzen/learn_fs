# sources/distributed-fs/eos/mgm/groupbalancer/GroupBalancer.cc

## Purpose
Implements the per-space group balancer service thread that periodically classifies groups, picks source/target groups, selects eligible files, and schedules converter jobs to move data between groups.

## Important APIs, types, and functions
The constructor creates the default stddev engine and starts the assisted thread. `Configure()` reads space config (`groupbalancer`, `groupbalancer.ntx`, min/max file sizes, engine, attempts, thresholds, blocklist) and checks converter availability. `GroupBalance()` is the main loop. `chooseFidFromGroup()` picks random filesystems and random FIDs. `chooseFileFromGroup()` filters by converter metadata and size bounds. `prepareTransfer()` selects groups via the engine. `scheduleTransfer()` builds a converter tag and calls `ConverterEngine::ScheduleJob()`. `UpdateTransferList()` prunes finished jobs through `mFidTracker`.

## Control flow
The thread waits for namespace boot, runs only on the master MGM, refreshes config when `mDoConfigUpdate` is set, cleans converter tracker state, recreates the engine when the configured type changes, refreshes group-size caches every 60 seconds or after engine changes, and schedules up to `groupbalancer.ntx` transfers when the engine can pick source and target groups.

## State and persistence
In-memory state includes current config, engine instance, engine config map, transfer map, last cache refresh, and proc-path filter. Persistent effects are indirect: converter jobs are scheduled and can cause files to be converted/moved; no config is written by this file.

## Dependencies and integration points
Integrates `FsView`, `FsSpace`, `FsGroup`, namespace services, `ConverterEngine`, `FidTracker`, `BalancerEngineFactory`, `GroupsInfoFetcher`, and `ConverterUtils`. The proc conversion tag includes `^groupbalancer^`.

## Risks and test signals
`mEngine.reset()` in the main loop is not guarded by `mEngineMtx`, while `Status()` can read the engine under that lock. File selection is random and may fail silently after many attempts. Tests should cover disabled converter, invalid thresholds per engine, engine switching, cache expiry, transfer pruning, size filtering, duplicate transfer suppression, and non-master behavior.
