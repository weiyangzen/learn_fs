# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/config.go

This file provides `NewDaemonOpt` option constructors that populate the persistent and runtime fields of a `Daemon`. The options set socket directory, initial reference count, log directory, stdout logging, log level, log rotation size, config directory, mountpoint, nydusd thread count, filesystem driver, failover policy, and daemon mode.

State effects are direct mutations of `Daemon.States` or `Daemon.ref`. `WithSocketDir` and `WithConfigDir` create per-daemon directories named by `d.ID()`. `WithSocketDir` sets `APISocket` to `<dir>/<daemon-id>/api.sock`, while `WithConfigDir` sets `ConfigDir` to `<dir>/<daemon-id>`. `WithLogDir` creates the root log directory and stores a per-daemon log subpath, but does not create that subdirectory itself. `WithLogLevel` falls back to `constant.DefaultLogLevel` for an empty input.

These options are used by filesystem daemon creation and manager recovery paths. Dependencies include global `config` daemon mode types, the default log-level constant, and OS directory creation. Risks include partial directory creation if a later option fails, assumptions that `d.ID()` is already set, and path package mixing (`path` and `filepath`). There are no direct tests for these options; behavior is indirectly covered by daemon creation and manager command-building tests.
