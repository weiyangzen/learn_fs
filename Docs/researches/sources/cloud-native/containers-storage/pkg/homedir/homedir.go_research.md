## sources/cloud-native/containers-storage/pkg/homedir/homedir.go

Purpose: cross-platform XDG data/cache home helpers built on platform-specific home directory lookup.

Important APIs/types/functions: `GetDataHome` and `GetCacheHome`.

Control flow: returns `XDG_DATA_HOME`/`XDG_CACHE_HOME` when set, otherwise uses `Get()` and appends `.local/share` or `.cache`; errors if neither env nor home is available.

State and persistence: reads environment only; no directory creation.

Dependencies and integration points: used by storage config/runtime path selection. Depends on platform-specific `Get`.

Risks: does not validate whether env-provided paths are absolute despite XDG expectations. Empty `Get()` causes an error.

Test signals: selected homedir tests only validate `Get` and shortcut string, not data/cache helpers.
