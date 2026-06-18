<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/configmgr/manager.go -->
# sources/distributed-fs/beegfs-go/common/configmgr/manager.go

Purpose: generic configuration manager that merges pflags, environment variables, optional TOML config files, validates application config, and pushes dynamic updates to listeners on SIGHUP.

Important APIs/types/functions: flags `FlagConfigFile`, `FlagVersion`, `FlagDumpConfig`; interfaces `Configurable` and `Listener`; type `ConfigManager`; functions/methods `New`, `AddListener`, `UpdateListeners`, `Get`, `Manage`, and `updateConfiguration`.

Control flow: `New` initializes the manager and performs an initial update, then subscribes to SIGHUP. `Manage` loops, refreshing configuration at startup and after each update signal until context cancellation. `updateConfiguration` constructs a fresh Viper, binds pflags, scans environment variables with the configured prefix, optionally reads/merges a TOML config file, removes manager-only keys, unmarshals exactly into a new `Configurable`, validates it, enforces `UpdateAllowed` after initial config, swaps `currentConfig`, and updates listeners.

State and persistence: state is in-memory current config, listener list, update signal channel, initial-config flag, and decode hooks. It intentionally does not persist config through Viper.

Dependencies and integration points: depends on `pflag`, `viper`, `mapstructure`, `zap`, and `types.MultiError`. Integrates with application configs implementing `Configurable` and components implementing `Listener`.

Risks: `AddListener` is not synchronized with `UpdateListeners`. Listener failures after `currentConfig` swap cannot roll back. Environment binding maps prefix-stripped names to lower-case dotted/kebab keys, so naming conventions are part of the API. `WithPKBase`-style bug is not here, but strict `UnmarshalExact` means manager-only keys must be deleted or config is rejected.

Test signals: no tests in this subset; behavior likely covered by downstream application tests if any.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/configmgr/manager.go -->
