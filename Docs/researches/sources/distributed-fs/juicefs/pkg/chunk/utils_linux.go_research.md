## sources/distributed-fs/juicefs/pkg/chunk/utils_linux.go

Purpose: Linux-specific helpers for atime extraction and kernel page-cache dropping.

Important APIs/types/functions: `getAtime` reads `syscall.Stat_t.Atim`. `dropOSCache` calls `unix.Fadvise` with `FADV_DONTNEED` when passed an `*os.File`, logging warnings on failure.

State and persistence: reads metadata and asks the kernel to drop cached pages for a file descriptor; no file contents are changed.

Dependencies and integration points: used by disk-cache scans and by cache/object reads when JuiceFS config disables OS cache.

Risks and test signals: `dropOSCache` only works for readers that are `*os.File`; other `ReadCloser` implementations are ignored. Fadvise behavior is advisory and platform/kernel dependent.
