## sources/distributed-fs/juicefs/pkg/chunk/utils_unix.go

Purpose: Unix shared filesystem helpers for disk cache metadata, permissions, and root-volume detection.

Important APIs/types/functions: `getNlink` extracts hard-link count from `syscall.Stat_t.Nlink`. `getDiskUsage` wraps `syscall.Statfs` and returns blocks/free blocks/files/free files. `changeMode` recursively chmods a directory tree when mode differs, logging errors. `inRootVolume` compares device IDs of a dir and `/` to determine whether the cache is on the root volume.

State and persistence: reads filesystem stats and may mutate permissions through chmod.

Dependencies and integration points: used by disk-cache scanning to identify hard-linked staging files, free-space checks, directory creation permission correction, and conservative root-volume free-ratio adjustment.

Risks and test signals: recursive chmod can be expensive on large cache trees. Device comparison can fail on unusual filesystems. Tests cover `inRootVolume`.
