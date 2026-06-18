# sources/cloud-native/containerd/internal/nri/config.go

## Purpose
Defines containerd's NRI configuration and converts it into options for the NRI adaptation layer.

## Important APIs, Types, And Functions
`Config` includes disable flag, socket/plugin/config paths, plugin timeouts, external-connection disabling, and default validator config. `DefaultConfig`, `toOptions`, and `ConfigureTimeouts` are key functions.

## Control Flow
Default config copies NRI defaults. `toOptions` conditionally appends adaptation options, metrics, default validator, and OpenTelemetry ttrpc interceptors. `ConfigureTimeouts` updates package-level NRI timeout settings when non-zero.

## State And Persistence
Config is usually loaded from TOML/JSON. `ConfigureTimeouts` mutates global timeout settings in the NRI adaptation package.

## Dependencies And Integration Points
Uses local `tomlext.Duration`, `containerd/nri` adaptation, default validator, otel ttrpc, and ttrpc client/server options.

## Risks
Global timeout mutation affects all NRI adaptation behavior in process. Nil default validator disables the built-in validator option.

## Test Signals
No direct tests in this subset; NRI startup and plugin tests elsewhere likely exercise option conversion.
