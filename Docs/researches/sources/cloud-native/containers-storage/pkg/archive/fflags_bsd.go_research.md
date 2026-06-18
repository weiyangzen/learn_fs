<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/fflags_bsd.go -->
# sources/cloud-native/containers-storage/pkg/archive/fflags_bsd.go

Purpose: FreeBSD implementation for preserving BSD file flags in tar PAX records and resetting immutable flags before layer mutations.

Important APIs/types/functions: `paxSCHILYFflags`, maps `flagNameToValue` and `flagValueToName`, `parseFileFlags`, `formatFileFlags`, `ReadFileFlagsToTarHeader`, `WriteFileFlagsFromTarHeader`, and `resetImmutable`.

Control flow: reading formats flags from `system.Lstat(path).Flags()` and writes `SCHILY.fflags` into PAX records. Writing parses comma-separated flags, supports `no<flag>` clear operations, reads current flags, and applies `(current & ^clear) | set` with `system.Lchflags`. `resetImmutable` clears system/user immutable bits before delete/replace operations.

State/persistence: reads and writes FreeBSD file flags; tar headers carry flag metadata through PAX records.

Dependencies/integration: used by archive tar creation/extraction and `diff.go` replacement/deletion handling. Depends on `system` FreeBSD flag constants and `syscall.Stat_t.Flags`.

Risks: unknown flags cause hard errors, which can block archive operations. Clearing immutable flags is necessary but security-sensitive. The reverse map emits only short names, so formatting is normalized rather than round-tripping aliases.

Test signals: BSD-specific tests outside this subset cover file flag diffs, copy preservation, and applying layers to immutable files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/fflags_bsd.go -->
