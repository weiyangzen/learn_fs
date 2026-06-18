## sources/distributed-fs/juicefs/pkg/chunk/utils_windows.go

Purpose: Windows-specific cache filesystem helpers.

Important APIs/types/functions: `getAtime` returns `fi.ModTime()` instead of true access time. `dropOSCache` is a no-op. `getNlink` returns 0. `getDiskUsage` calls `windows.GetDiskFreeSpaceEx` and reports total/free bytes with inode counts as zero. `changeMode` is a no-op. `inRootVolume` returns false.

State and persistence: reads disk free-space data only.

Dependencies and integration points: used by the same disk-cache code paths as Unix helpers while acknowledging Windows lacks or does not use inode/link/permission behavior here.

Risks and test signals: hard-link/staging detection and atime eviction are less precise on Windows. Free-space logic ignores inode pressure. No OS-cache drop support.
