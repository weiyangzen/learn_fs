# sources/cloud-native/containerd/plugins/services/opt/service.go

## Purpose
`service.go` registers an internal opt manager plugin that prepares an opt directory and prepends its `bin` and `lib` paths to process environment variables.

## Important APIs, Types, And Functions
`Config` has a TOML `path` field. The internal plugin ID is `opt`. Initialization writes `ic.Meta.Exports["path"]`, creates `<path>/bin` and `<path>/lib`, and updates `PATH` and `LD_LIBRARY_PATH`. The returned `manager` type is empty.

## Control Flow
At plugin initialization, the configured path defaults from the platform file. The service creates directories with mode `0711`, then calls `os.Setenv` to prepend the new executable and library paths.

## State And Persistence
The plugin persists directories on disk and mutates the daemon process environment. The environment mutation is global to the process and can affect later plugin execution and child processes.

## Dependencies And Integration Points
It uses the containerd plugin registry, `plugins.InternalPlugin`, filesystem APIs, and platform path defaults.

## Risks
`LD_LIBRARY_PATH` is Unix-centric but used unconditionally, including Windows builds. Prepending paths can change binary/library resolution order for later subprocesses. Directory creation failures stop plugin initialization.

## Test Signals
No direct tests are in this subset. Startup behavior and plugin metadata exports are the expected validation points.
