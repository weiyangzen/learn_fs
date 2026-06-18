## sources/cloud-native/containers-storage/pkg/config/config.go

Purpose: storage option TOML structs and graph-driver option flattening.

Important APIs/types/functions: `AufsOptionsConfig`, `BtrfsOptionsConfig`, `OverlayOptionsConfig`, `VfsOptionsConfig`, `ZfsOptionsConfig`, `OptionsConfig`, and `GetGraphDriverOptions`.

Control flow: `GetGraphDriverOptions` switches on driver name and emits `driver.key=value` strings. Driver-specific nested fields generally override legacy/common top-level fields; unknown drivers return no options.

State and persistence: no persistence; struct tags map config file TOML into memory.

Dependencies and integration points: used by storage configuration parsing to pass driver options for aufs, btrfs, overlay/overlay2, vfs, and zfs. `ForceMask` mixes top-level `os.FileMode` with overlay-specific string option.

Risks: option precedence is manual and can drift as config fields change. `ForceMask` formatting with `%s` on `os.FileMode` relies on its `String` method, which may not produce an octal-like config value. Boolean-like options are strings in many places, so validation must happen downstream.

Test signals: `config_test.go` covers precedence and emitted substrings for all supported switch cases. Local execution blocked by missing `go`.
