## sources/distributed-fs/juicefs/pkg/chunk/utils_darwin.go

Purpose: Darwin-specific helpers for cache file metadata and OS cache handling.

Important APIs/types/functions: `getAtime` extracts access time from `syscall.Stat_t.Atimespec`. `dropOSCache` is a no-op on Darwin.

State and persistence: reads file metadata only; does not mutate state.

Dependencies and integration points: used by disk-cache scans to preserve access time and by read/write paths when `OSCache` is disabled.

Risks and test signals: Darwin atime availability depends on filesystem mount behavior. No-op cache dropping means disabling OS cache has no effect on Darwin through this helper.
