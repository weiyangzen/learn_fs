# sources/cloud-native/containers-storage/types/utils.go

Purpose: utility functions for path expansion, default config file resolution, and best-effort cached config reload.

Important APIs and control flow: `expandEnvPath` replaces `$UID`, expands environment variables, resolves symlinks when possible, and otherwise returns a cleaned path. `DefaultConfigFile` respects explicit default path, `CONTAINERS_STORAGE_CONF`, rootful override file existence, rootless `XDG_CONFIG_HOME`, or `$HOME/.config/containers/storage.conf`. `reloadConfigurationFileIfNeeded` is a non-returning helper that checks modtime and config path under a mutex, reuses cached options when unchanged, and logs warnings instead of failing.

State and persistence: reads environment and filesystem metadata. Shares `prevReloadConfig` mutable cache with `options.go`.

Dependencies and integration: uses `fileutils.Exists`, homedir resolution, logrus, and package globals such as `defaultConfigFileSet` and `defaultOverrideConfigFile`. It is called during rootless/default option loading.

Risks: symlink resolution fallback silently accepts unresolved paths. The non-returning reload helper can hide config read failures from callers. Cache assignment stores the caller's pointer in one path, which can be surprising if mutated later.

Test signals: `utils_test.go` verifies env override resolution and rootless config path behavior; `options_test.go` indirectly covers path expansion.
