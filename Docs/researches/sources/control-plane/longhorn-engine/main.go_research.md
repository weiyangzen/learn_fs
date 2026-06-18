<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/main.go -->
## sources/control-plane/longhorn-engine/main.go

Purpose: main binary entrypoint for `longhorn`, wiring the CLI, metadata, logging, panic handling, optional CPU profiling, and `ssync` reexec registration.

Important APIs/types/functions: `main` defers `cleanup`, registers `ssync`, and runs `longhornCli` after `reexec.Init`. `ResponseLogAndError` prints/logs recoverable errors and runtime panics. `cleanup` converts panics to process exit. `longhornCli` configures `urfave/cli` flags and command list, sets version metadata, configures logrus caller formatting, honors `PPROFILE`, and registers controller, replica, sync-agent, backup, frontend, info, and profiler commands.

Control flow: process startup optionally enters a reexec child. Normal startup initializes cli app state, global flags (`url`, `volume-name`, `engine-instance-name`, `debug`), and command handlers from `app/cmd`, then runs with `os.Args`.

State and persistence: writes CPU profiles if `PPROFILE` is set. Sets global `meta` version variables from linker-injected `Version`, `GitCommit`, and `BuildDate`.

Dependencies and integration points: depends on `moby/sys/reexec`, `longhorn/sparse-tools/cli/ssync`, `urfave/cli`, `logrus`, and command packages. It is the user-facing binary copied into the container image.

Risks: panic handling prints to stdout and exits 1, which is useful for CLI but may expose messages in automation logs. `PPROFILE` file creation failures call `log.Fatal`. Version values depend on ldflags. Command registration drift can hide features.

Test signals: command package tests and packaging smoke tests should validate command availability. Runtime smoke should run `longhorn --version` and representative subcommands.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/main.go -->
