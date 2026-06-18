# sources/distributed-fs/eos/mgm/groupdrainer/DrainProgressTracker.cc

## Purpose
Implements a thread-safe per-filesystem progress counter for group drain scheduling.

## Important APIs, types, and functions
`setTotalFiles()` records the largest known total file count for an FSID. `increment()` increases scheduled/drained count. `getDrainStatus()` returns scheduled count divided by total as a percent. `dropFsid()` and `clear()` remove tracked entries. `getTotalFiles()` and `getFileCounter()` expose counters.

## Control flow
`GroupDrainer` calls `setTotalFiles()` when populating file lists and `increment()` after successfully scheduling a converter job. Status reporting reads the counters to format per-FSID progress.

## State and persistence
Two maps hold total files and scheduled counters. They are protected by separate mutexes and are not persisted.

## Dependencies and integration points
Uses `common/FileSystem.hh` FSID type. Integrated into `GroupDrainer::getStatus()`.

## Risks and test signals
`getDrainStatus()` can exceed 100 percent because failed/retried schedules may increment more than the original total. Tests should cover concurrent increments, increasing totals, zero totals, dropped FSIDs, and lock ordering.
