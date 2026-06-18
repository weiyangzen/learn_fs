# sources/cloud-native/containers-storage/pkg/system/stat_solaris.go

Purpose: Solaris conversion from syscall stat structures into the package's `StatT`.

Important APIs/types/functions: `fromStatT`.

Control flow: copies size, mode, uid, gid, rdev, and `Mtim`.

State/persistence: no mutation.

Dependencies/integration: selected for Solaris builds of shared stat helpers.

Risks: `dev` is not populated. Solaris field widths and semantics should be checked when updating Go versions.

Test signals: Solaris compile and stat tests should confirm metadata accessors remain correct.
