## sources/cloud-native/moby/daemon/logger/factory.go

Purpose: Provides the global logging driver registry, plugin fallback lookup, option-validator registry, and built-in logging option validation.

Important APIs and types: `Creator`, `LogOptValidator`, `logdriverFactory`, `ListDrivers`, `RegisterLogDriver`, `RegisterLogOptValidator`, `GetLogDriver`, and `ValidateLogOpts`. The factory stores creators and validators under a mutex. `builtInLogOpts` reserves `mode` and `max-buffer-size`.

Control flow and state: Registration rejects duplicate driver or validator names. Driver existence checks consult the registry and, if missing, ask plugin lookup when `pluginGetter` is available. `GetLogDriver` returns a registered creator or acquires a plugin-backed creator. `ValidateLogOpts` allows `none`, validates blocking/non-blocking mode, ensures `max-buffer-size` is only used with non-blocking mode and parses as bytes, validates external/plugin options, checks driver registration/plugin availability, strips built-in options, then invokes any driver-specific validator.

Dependencies and integration points: Integrates with `containertypes.LogMode`, Docker units parser, plugin getter lifecycle, external logging validation, and all driver `register.go` files.

Risks: Global mutable registry is process-wide; tests adding drivers must avoid duplicate names. Plugin lookup during validation can return errors unrelated to built-in validation. Built-in option stripping means driver validators do not see `mode`/`max-buffer-size`.

Test signals: Driver-specific tests indirectly exercise validator registration and `ValidateLogOpts`; no focused factory tests in this subset.
