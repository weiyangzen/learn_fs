# sources/cloud-native/containerd/cmd/containerd/server/server.go

Purpose: initializes and manages the main containerd server by applying process config, loading plugins, registering proxy plugins, starting server plugins, tracking readiness, and stopping plugin instances.

Important APIs/types/functions: `CreateTopLevelDirectories()`, `New()`, `recordConfigDeprecations()`, `server` interface, `Server` struct, `Start()`, `Stop()`, `RegisterReadiness()`, `Wait()`, `LoadPlugins()`, `proxyClients.getClient()`, and `readString()`.

Control flow: `New()` applies platform process settings, parses timeout config into global timeout registry, loads plugin graph, registers stream processors, computes GRPC/TTRPC addresses from plugin config with defaults, initializes plugins in dependency order, decodes plugin config, tracks required plugin failures, collects server plugins, and records deprecation hooks. `Start()` starts collected server plugins. `Stop()` walks initialized plugins in reverse and closes instances implementing `io.Closer`.

State and persistence: creates root/state/temp directories with permissions in `CreateTopLevelDirectories()`. Plugin init contexts receive per-plugin root/state directories and server addresses. `Server.ready` is a wait group used by plugins to delay readiness. Proxy gRPC client connections are cached by address in `proxyClients`.

Dependencies/integration: integrates plugin registry, proxy snapshot/content/sandbox/diff clients, OpenTelemetry gRPC stats, `dialer`, defaults, `timeout`, stream processor registration, warning service, and platform-specific `apply()`.

Risks: required plugin handling and readiness registration are strict: a plugin that registers readiness cannot later fail without aborting startup. Proxy plugin registration captures loop variables carefully through local variables; changes here can introduce closure bugs. `Stop()` logs close errors but continues. `readString()` only traverses `map[string]any` and ignores other TOML-decoded shapes.

Test signals: `server_test.go` covers top-level directory validation and plugin config migration through `New()`. Plugin graph, proxy plugin behavior, readiness, and server start/stop ordering rely on broader integration coverage.
