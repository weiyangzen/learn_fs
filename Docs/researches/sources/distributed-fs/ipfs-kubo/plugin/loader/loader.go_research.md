<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/loader.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/loader.go

## Purpose

`loader.go` implements Kubo's plugin lifecycle manager: load preloaded and dynamic plugins, initialize them with repo/config context, inject extension points, start daemon plugins, and close started plugins.

## Important APIs, Types, and Functions

`Preload` appends compiled-in plugins during init. `loaderState` and `PluginLoader` enforce lifecycle phases. `NewPluginLoader` reads plugin config, loads preloaded plugins, and scans the repo plugins directory. `readPluginsConfig` reads only the config `Plugins` section. `Load`, `LoadDirectory`, and `loadDynamicPlugins` handle duplicate/disabled/executable checks. `Initialize`, `Inject`, `Start`, and `Close` transition states. Injection helpers register datastore parsers, IPLD codecs, tracers, and Fx option functions.

## Control Flow, State, and Integration

The loader is a strict state machine: loading -> initializing -> initialized -> injecting -> injected -> starting -> started -> closing/closed, with `loaderFailed` on errors. Dynamic plugin scan ignores directories, rejects non-executable files, and uses the platform `loadPluginFunc`. Started plugins that implement `io.Closer` are closed in startup order. State is in memory, while config is read from the repo.

## Dependencies, Risks, and Test Signals

Dependencies include config parsing, fsrepo datastore registry, core/CoreAPI, multicodec default registry, OpenTracing global tracer, and platform dynamic loading. Risks include process-global registry mutations, duplicate plugin names, disabled config semantics, dynamic plugin ABI failures, partial startup cleanup, and error aggregation on close. Built-in plugin initialization, example setup, and daemon startup are major signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/loader.go -->
