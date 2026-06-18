<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.cpp

**Purpose:** Implements BeeGFS storage filesystem utilities for directory creation/removal, filesystem statistics, lock/pid files, storage format files, persistent ID/token files, directory enumeration, chunk path layout, recursive deletion, mount lookup, and bounded file reads.

**Important APIs/types/functions:** Implements `initHashPaths`, `createPathOnDisk` path and fd-relative variants, `removePathDirsFromDisk`, `statStoragePath`, `statStoragePathOverride`, basename/dirname helpers, `lockWorkingDirectory`, `createAndLockPIDFile`, format-file creation/loading/updating, `deprecateNodeStringIDFiles`, target/registration/numeric ID file helpers, filtered `readdir`, `readCompleteDir`, chunk path helpers, `removeDirRecursive`, `findLongestMountedPrefix`, `findMountForPath`, `readFile`, and private `readNumFromFile`.

**Control flow:** Directory creation walks path elements and accepts existing directories after stat/fstat validation. Format writing serializes key/value lines through `TempFileTk::storeTmpAndMove`; loading reads via `MapTk`, validates a `version` key, and rejects incompatible versions. ID helpers read existing files first and atomically create missing files with generated IDs or numeric values. Mount lookup parses `/proc/self/mounts`-style streams, unescapes octal path escapes, and tracks the longest prefix match. Recursive deletion uses `nftw` depth-first.

**State and persistence behavior:** Persists and updates important node/storage state: `format.conf`, lock pid files, `targetID`, `targetNumID`, `nodeNumID`, `storagePoolID`, `registrationToken`, deprecated string ID marker files, and optional free space/inode override files. `StorageTk::idCounter` is process-global, initialized from current seconds shifted into the high 32 bits, and used for file/target/registration IDs.

**Dependencies and integration points:** Uses BeeGFS config/file helpers (`ICommonConfig`, `MapTk`, `TempFileTk`, `LockFD`, `FDHandle`, `Path`, `PathInfo`, `HashTk`, `UnitTk`), POSIX/Linux APIs (`mkdir`, `mkdirat`, `statfs`, `flock`, `nftw`, `realpath`, `open`, `lseek`, `read`), and BeeGFS storage constants. It is central to daemon startup, storage target initialization, chunk layout, and capacity reporting.

**Risks:** Many methods throw `InvalidConfigException` on invalid persistent files; callers must distinguish initialization from fatal corruption. `readFile` performs a single `read` after sizing, so short reads are not retried. Recursive deletion removes everything under the supplied path and must receive trusted paths. `findMountForPath` requires `realpath`, so non-existing paths fail despite prefix lookup supporting non-existing raw paths. ID generation assumes clocks do not move backward across restarts and fewer than 2^32 IDs per second.

**Test signals:** `TestLockFD.cpp`, `TestPreallocatedFile.cpp`, and path-related tests indirectly exercise lock files, recursive removal, and file allocation. Dedicated storage tests should cover format version upgrades, ID file mismatch handling, mount escape parsing, Btrfs free-space behavior, override files, and partial I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StorageTk.cpp -->
