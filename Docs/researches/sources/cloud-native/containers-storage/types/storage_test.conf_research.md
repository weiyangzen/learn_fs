# sources/cloud-native/containers-storage/types/storage_test.conf

Purpose: rootless path expansion fixture for storage option tests.

Important fields and flow: `[storage]` sets empty `driver`, `runroot`, `graphroot`, and `rootless_storage_path` to `$HOME/$UID/containers/storage`. `[storage.options]` has an empty `additionalimagestores` list, and `[storage.options.overlay]` sets `mountopt = "nodev"`.

State and persistence: fixture-only. It models a config where all root paths should expand through environment and rootless UID substitution.

Dependencies and integration: consumed by `TestDefaultStoreOpts` and shared config loading code. The overlay mount option is converted through option mapping in `ReloadConfigurationFile`.

Risks: tests using this fixture skip when not in per-user storage mode, so coverage is conditional on rootless test environment.

Test signals: successful tests prove `$HOME` and `$UID` expansion and rootless storage path fallback logic.
