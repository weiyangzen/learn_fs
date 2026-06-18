# sources/cloud-native/moby/daemon/logger/log_cache_opts.go

Purpose: extends logger option validation for non-driver cache/proxy options.

Important APIs/types/functions: `RegisterExternalValidator`, `AddBuiltinLogOpts`, and `validateExternal`.

Control flow/state/persistence: package-level slices/maps accumulate validators and built-in option names during init. `validateExternal` runs each registered validator against a config map.

Dependencies/integration: used by cache validation packages and logger factory option validation.

Risks: global mutable registration is init-order sensitive and not concurrency-protected, so it must be used only during initialization as documented.

Test signals: cache validation tests exercise external validator behavior.
