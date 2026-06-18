# sources/cloud-native/containers-storage/pkg/system/stat_darwin.go

Purpose: Darwin conversion from `syscall.Stat_t` to the package-neutral `StatT`.

Important APIs/types/functions: `fromStatT(s *syscall.Stat_t) (*StatT, error)`.

Control flow: copies size, mode, uid, gid, rdev, and `Mtimespec` into `StatT`.

State/persistence: no mutation; captures a filesystem stat snapshot.

Dependencies/integration: called by Unix `Stat`/`Fstat` on Darwin.

Risks: does not populate `dev`, so `StatT.Dev()` remains zero on Darwin. Platform field names and integer widths must match Go's Darwin syscall definitions.

Test signals: Darwin stat tests should verify mode/time/ownership and whether missing `dev` is acceptable for callers.
