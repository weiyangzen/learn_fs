# sources/cloud-native/containers-storage/types/default_override_test.conf

Purpose: small TOML fixture for testing `CONTAINERS_STORAGE_CONF` override behavior.

Important fields and flow: defines `[storage]` with an empty `driver`, `graphroot = "environment_override_graphroot"`, and `rootless_storage_path = "environment_override_rootless_storage_path"`. It is not meant to be a full storage configuration.

State and persistence: fixture-only. It simulates an explicitly selected config file whose paths should be returned or parsed by configuration helpers.

Dependencies and integration: used by `types/utils_test.go` through `t.Setenv("CONTAINERS_STORAGE_CONF", "default_override_test.conf")` to assert `DefaultConfigFile` resolves the environment override for both rootless and root contexts.

Risks: relative path assumptions mean tests must run from the `types` package directory or with Go's package test working-directory semantics.

Test signals: successful override tests show that `CONTAINERS_STORAGE_CONF` has priority over default rootful and rootless config locations.
