# sources/cloud-native/containers-storage/pkg/system/xattrs_unsupported.go

Purpose: fallback xattr implementation for platforms without Linux/Darwin/FreeBSD support.

Important APIs/types/functions: zero-valued errno aliases and unsupported `Lgetxattr`, `Lsetxattr`, and `Llistxattr`.

Control flow: all operations immediately return `ErrNotSupportedPlatform`.

State/persistence: none.

Dependencies/integration: keeps common xattr callers buildable on unsupported targets.

Risks: zero-valued errno constants are placeholders; code comparing them directly on unsupported platforms can behave unexpectedly. Metadata fidelity is lost where callers ignore unsupported errors.

Test signals: platform tests should assert unsupported return values and caller tolerance for missing xattrs.
