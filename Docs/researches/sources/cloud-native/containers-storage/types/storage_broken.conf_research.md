# sources/cloud-native/containers-storage/types/storage_broken.conf

Purpose: malformed-but-partly-valid TOML fixture for `ReloadConfigurationFile` warning tests.

Important fields and flow: includes an unexpected top-level key `foo = "bar"` and an unexpected `storage.options.graphroot` key, while still providing `[storage]`, empty `driver`, and `runroot = "/run/containers/test"`.

State and persistence: fixture-only; it should not be used as a real config.

Dependencies and integration: loaded by `TestReloadConfigurationFile`, which expects parsing to succeed, the valid `runroot` to be applied, and undecoded keys to be logged.

Risks: if TOML schema changes to include the formerly unknown keys, the warning assertion must change. Relative path use relies on Go package test working directory.

Test signals: protects tolerant parsing behavior: unknown keys warn but do not reject otherwise usable config.
