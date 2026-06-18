<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/fxtest/fxtest.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/fxtest/fxtest.go

## Purpose

This built-in test plugin validates the `PluginFx` extension mechanism without affecting production unless explicitly enabled by environment.

## Important APIs, Types, and Functions

`fxtestPlugin` implements `PluginFx`. `Options` returns existing FX options and, when `TEST_FX_PLUGIN` is set, appends an `fx.Invoke` that logs a debug statement.

## Control Flow, State, and Integration

The plugin is preloaded and initialized like other plugins. Its runtime effect is gated by an environment variable.

## Dependencies, Risks, and Test Signals

Dependencies are Uber Fx, Kubo core FX info, and go-log. Risks are minimal, but accidental env setting could add an invocation. FX plugin tests should assert the invocation path works.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/fxtest/fxtest.go -->
