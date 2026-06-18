# sources/cloud-native/containers-storage/pkg/unshare/unshare.go

Purpose: shared unshare package helper for resolving the current user's home directory.

Important APIs/types/functions: package-level `homeDirOnce`, `homeDirErr`, `homeDir`; `HomeDir() (string, error)`.

Control flow: `HomeDir` caches the first result. It prefers `$HOME`; if unset, it looks up the user by `GetRootlessUID()` and returns that user's home directory.

State/persistence: process-local cached home directory and error via `sync.Once`.

Dependencies/integration: used by rootless storage configuration paths that need a stable home directory. Depends on platform `GetRootlessUID`.

Risks: cache does not update if `$HOME` or rootless UID changes later in process lifetime. User lookup can fail in minimal containers or NSS-restricted environments.

Test signals: tests should cover `$HOME` set, `$HOME` missing with user lookup, and lookup failure/caching behavior.
