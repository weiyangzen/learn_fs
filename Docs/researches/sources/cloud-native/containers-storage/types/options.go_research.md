# sources/cloud-native/containers-storage/types/options.go

Purpose: main configuration loader and option model for `containers/storage`. It converts TOML storage config, environment overrides, rootless heuristics, and platform defaults into `StoreOptions`.

Important APIs and control flow: `TomlConfig` mirrors storage.conf tables. `StoreOptions` carries run/graph roots, image store, rootless path, graph driver and options, ID maps, auto-userns limits, pull options, volatile and transient settings. `loadDefaultStoreOptions` initializes package defaults once, honoring `CONTAINERS_STORAGE_CONF`, `XDG_CONFIG_HOME`, override config, and system config. `loadStoreOptionsFromConfFile` starts from defaults, applies rootless options when needed, reloads explicit config, expands `$UID` and environment variables, and rejects missing roots or `ImageStore == GraphRoot`. `DefaultStoreOptions` and `UpdateStoreOptions` expose cached or refreshed values. `ReloadConfigurationFile` decodes TOML, warns on undecoded keys, resets previous options, maps config fields to driver options, handles `STORAGE_DRIVER` and `STORAGE_OPTS`, and normalizes `overlay2` to `overlay`.

State and persistence: package-level `sync.Once` values cache default and current options. `prevReloadConfig` caches parsed config by file path and modtime. `Save` removes and recreates the default config file; `StorageConfig` reads it.

Dependencies and integration: uses BurntSushi TOML, storage config helpers, homedir/runtime helpers, rootless detection, file existence checks, idtools, and logrus. Integrates with all store initialization code.

Risks: global caches make tests and long-running process reconfiguration sensitive to call order. `Save` does not close the created file explicitly. Modtime-based cache can miss changes with coarse timestamps. Environment overrides can replace config-derived driver options wholesale.

Test signals: `options_test.go` verifies rootless driver selection, environment overrides, overlay2 normalization, and malformed config warnings; broader store tests exercise final options during store initialization.
