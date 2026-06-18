# Research: sources/cloud-native/containerd/client/install_opts.go

## Purpose
Defines the small option surface for `Client.Install`, separating install policy from the layer extraction implementation.

## Important APIs, Control Flow, And State
`InstallOpts` mutates an `InstallConfig` containing `Libs`, `Replace`, and `Path`. `WithInstallLibs` enables library extraction, `WithInstallReplace` permits overwriting existing files, and `WithInstallPath` overrides opt-service path discovery. There is no external state or control flow beyond deterministic in-memory mutation of the config struct.

## Dependencies And Integration
This file has no imports. It is consumed by `install.go` and public callers of the client package. The option values directly drive archive filtering and overwrite checks.

## Risks And Test Signals
The main risk is semantic drift with `Install` if new install behavior is added without extending the config. Tests should validate default zero values, option composition order, and that options affect extraction behavior as expected.
