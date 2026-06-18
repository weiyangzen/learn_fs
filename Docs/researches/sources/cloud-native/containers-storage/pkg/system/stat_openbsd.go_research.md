# sources/cloud-native/containers-storage/pkg/system/stat_openbsd.go

Purpose: OpenBSD conversion from `syscall.Stat_t` into `StatT`.

Important APIs/types/functions: `fromStatT`.

Control flow: copies size, mode, uid, gid, rdev, and `Mtim`.

State/persistence: no mutation.

Dependencies/integration: selected by OpenBSD build constraints for shared stat APIs.

Risks: `dev` is not populated. Cross-platform code using `Dev()` must handle zero on this platform.

Test signals: OpenBSD stat tests should validate mode, mtime, owner, and device expectations.
