# sources/cloud-native/cri-o/internal/config/nsmgr/types_freebsd.go

Purpose: supplies FreeBSD namespace type/config structures and a minimal namespace implementation.

Important APIs/types/functions: `supportedNamespacesForPinning` returns only `NETNS`; `PodNamespacesConfig`, `PodNamespaceConfig`, internal `namespace`, `Path`, `Type`, `Remove`, and `GetNamespace`.

Control flow: `Remove` is idempotent via a mutex and `closed` flag. `GetNamespace` wraps a jail name into a namespace object without validation.

State and persistence behavior: namespace state is in memory (`closed`, `nsType`, `jailName`). No files or mounts are manipulated.

Dependencies/integration points: FreeBSD variant used by `nsmgr_freebsd.go` and shared callers.

Risks: only network namespace pinning is represented, and jail names are not validated.

Test signals: no direct tests.
