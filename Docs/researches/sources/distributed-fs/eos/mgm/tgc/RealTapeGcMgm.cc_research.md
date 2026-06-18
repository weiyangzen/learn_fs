# sources/distributed-fs/eos/mgm/tgc/RealTapeGcMgm.cc

## Purpose
`RealTapeGcMgm.cc` implements the production bridge between tape-GC logic and EOS MGM services: FsView config/stats, namespace metadata, eviction command execution, QuarkDB namespace scanning, filesystem-to-space mapping, and shell-command stdout capture.

## Important APIs, Types, And Functions
Implemented methods include `getTapeGcSpaceConfig()`, `getSpaceConfigMemberString()`, `getSpaceConfigMemberUint64()`, `fileInNamespaceAndNotScheduledForDeletion()`, `getSpaceStats()`, `getFileSizeBytes()`, `evictAsRoot()`, `getFsIdToSpaceMap()`, `getSpaces()`, `getSpaceToDiskReplicasMap()`, and `getStdoutFromShellCmd()`.

## Control Flow
Config methods read `FsView::mSpaceView` under read lock and parse values, falling back to defaults on any error. File metadata methods prefetch before taking the namespace lock, then inspect `IFileMD`. `getSpaceStats()` sums free and capacity bytes for a space and scales by layout size factor when a space policy layout exists. Replica-map population builds an FSID-to-space map, scans QuarkDB with `FileScanner`, maps each file location to a space, stores matching fids ordered by ctime, honors a shared stop flag, and warns about FS IDs without spaces. Shell execution waits up to five seconds, handles timeout/signal/non-zero exit, and reads stdout with a maximum length.

## State And Persistence
The class stores only an `XrdMgmOfs&`; all persistent or live state is held by FsView, namespace services, QuarkDB, and admin command infrastructure. It does not cache internally.

## Dependencies And Integration Points
It integrates with `XrdMgmOfs`, `FsView`, `Policy`, `EvictCmd`, `VirtualIdentity::Root`, namespace prefetch/file service, QuarkDB `QClient`, `FileScanner`, `ShellCmd`, and `CtaUtils`. It is constructed by `XrdMgmOfs` and supplied to `MultiSpaceTapeGc`.

## Risks And Edge Cases
Config getters catch all exceptions and silently return defaults, which can mask invalid operational config. `getSpaceStats()` returns zeroed stats if the space is absent rather than throwing. `getFsIdToSpaceMap()` calls `getSpaces()` while already holding `FsView::ViewMutex`; whether this is safe depends on the lock being recursively readable. `FileIdAndCtime` ordering can drop files with identical ctime. Shell command strings are built elsewhere and executed through a shell, so config validation matters.

## Test Signals
Tests should cover config default fallback and parse errors, space stat scaling by layout, missing space behavior, namespace prefetch failures, scheduled-for-deletion container ID zero, eviction command errors, duplicate FSID detection, QuarkDB scan stop behavior, FS IDs without spaces, shell timeout/signal/exit/read-length paths, and integration with `SmartSpaceStats`.
