# sources/cloud-native/containers-storage/pkg/system/stat_freebsd.go

Purpose: FreeBSD conversion from `syscall.Stat_t` to `StatT`, including filesystem flags.

Important APIs/types/functions: `platformStatT{flags uint32}`, `StatT.Flags()`, and `fromStatT`.

Control flow: builds a `StatT` with size, mode, uid, gid, rdev, mtime, dev, then stores `s.Flags`.

State/persistence: read-only conversion of syscall stat data.

Dependencies/integration: supports FreeBSD deletion flag reset and caller visibility into file flags.

Risks: assigns `dev` twice, harmless but redundant. FreeBSD-specific `Flags` behavior is not available on other platforms.

Test signals: `stat_freebsd_test.go` validates mode/time and file flags after `Lchflags`.
