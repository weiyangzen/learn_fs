# sources/cloud-native/containers-storage/pkg/system/stat_netbsd.go

Purpose: NetBSD `syscall.Stat_t` conversion for the shared `StatT` abstraction.

Important APIs/types/functions: `fromStatT`.

Control flow: copies size, mode, uid, gid, rdev, and `Mtimespec`.

State/persistence: read-only stat conversion.

Dependencies/integration: used by Unix `Stat` and `Fstat` on NetBSD.

Risks: does not populate `dev`, so callers needing filesystem identity get zero. Platform fields must stay aligned with Go's NetBSD syscall struct.

Test signals: NetBSD compile and stat behavior tests should confirm expected metadata.
