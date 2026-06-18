# sources/cloud-native/containers-storage/pkg/system/rm_common.go

Purpose: default implementation of file-flag reset for platforms that do not need FreeBSD `chflags` cleanup.

Important APIs/types/functions: `resetFileFlags(dir string) error` returns nil.

Control flow: no traversal or syscall is performed.

State/persistence: none.

Dependencies/integration: called by `EnsureRemoveAll` after `EPERM`; on non-FreeBSD it assumes immutable flags are not handled here.

Risks: if a non-FreeBSD platform supports immutable flags that block removal, this no-op leaves the original `RemoveAll` failure unresolved.

Test signals: `EnsureRemoveAll` tests on non-FreeBSD confirm ordinary deletion paths; platform-specific immutable tests belong elsewhere.
