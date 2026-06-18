## sources/distributed-fs/beegfs/meta/source/storage/SyncedDiskAccessPath.h

Purpose: Extends `Path` with serialized disk-access helpers and a monotonically increasing storage version for metadata path updates.

Important APIs/types/functions: Constructors initialize version state. `storageUpdateBegin()`/`storageUpdateEnd()` lock and unlock `diskMutex`. `incStorageVersion()` increments a combined high/low version. `createSubPathOnDisk()` and `removeSubPathDirsFromDisk()` wrap `StorageTk` path creation/removal under the mutex.

Control flow: `incStorageVersion()` increments low bits cheaply until a threshold, then samples current seconds to advance the high part when time changes. Path methods lock, compose base and subpath, call the `StorageTk` operation, and unlock.

State and persistence: Maintains in-memory `storageVersion`, `highVersion`, `lowVersion`, and a mutex. Disk changes are serialized at this path object; version values can identify updates but are not persisted in this class.

Dependencies and integration: Inherits `Path`, uses `System::getCurrentTimeSecs`, `Mutex`, and metadata `StorageTkEx`/common `StorageTk` helpers. It is meant for metadata storage paths where directory updates must not race.

Risks and test signals: Manual begin/end locking is exception-unsafe if callers add throwing work between them. The low-version mask `((lowVersion << 10) >> 10)` assumes unsigned width behavior. Tests should cover concurrent create/remove, version monotonicity under same-second bursts, and low-version rollover.
