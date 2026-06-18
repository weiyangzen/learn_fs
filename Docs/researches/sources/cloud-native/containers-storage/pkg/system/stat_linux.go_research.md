# sources/cloud-native/containers-storage/pkg/system/stat_linux.go

Purpose: Linux conversion from `syscall.Stat_t` to the package's stable `StatT`, plus an exported converter for archive change code.

Important APIs/types/functions: `fromStatT` and exported `FromStatT`.

Control flow: copies size, mode, uid, gid, rdev, `Mtim`, and device ID to `StatT`; `FromStatT` delegates to the unexported converter.

State/persistence: no mutation; represents a stat snapshot.

Dependencies/integration: used by `Stat`, `Fstat`, and `pkg/archive/changes` on Linux.

Risks: `Rdev` and `Dev` conversions are intentionally marked with `nolint:unconvert`, so type changes in syscall definitions should be checked carefully.

Test signals: `stat_linux_test.go` and `stat_unix_test.go` verify mode, mtime, uid/gid, and rdev mapping.
