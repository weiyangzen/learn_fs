# sources/cloud-native/containers-storage/types/utils_test.go

Purpose: tests for default storage option path expansion and config-file override selection.

Important APIs and control flow: `TestDefaultStoreOpts` skips outside per-user storage, loads `storage_test.conf`, computes `$HOME/<rootlessUID>/containers/storage`, and asserts `RunRoot`, `GraphRoot`, and `RootlessStoragePath`. The two override tests set `CONTAINERS_STORAGE_CONF` to `default_override_test.conf` and assert `DefaultConfigFile` returns it.

State and persistence: mutates environment through `t.Setenv`; no filesystem writes beyond test package behavior.

Dependencies and integration: uses rootless detection from `unshare`, path utilities, and `gotest.tools/v3/assert`.

Risks: rootless-only test coverage means CI that runs only rootful skips a significant path. The root/rootless names on the override tests are descriptive only; both rely on the same process context.

Test signals: protects precedence of `CONTAINERS_STORAGE_CONF` and correct expansion of `$HOME`/`$UID` in config-derived paths.
