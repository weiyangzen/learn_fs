# sources/cloud-native/nydus/src/bin/nydusctl/main.rs

## Purpose
`main.rs` is the `nydusctl` CLI entrypoint. It defines the command-line surface, creates a Unix-socket API client, maps subcommands to command structs, and runs them on a Tokio runtime.

## Important APIs, Types, And Functions
The async `main` function is annotated with `#[tokio::main]`. It uses build-time information from `nydus::get_build_time_info` for version output. It defines global `--sock` and `--raw`, subcommands `info`, `set`, `metrics`, `mount`, and `umount`, then dispatches to `CommandDaemon`, `CommandBackend`, `CommandCache`, `CommandFsStats`, `CommandMount`, or `CommandUmount`.

## Control Flow
After parsing, the code unwraps required `--sock`, reads the raw-output flag, and constructs `NydusdClient`. `info` calls daemon info. `set` builds a map from `KIND`/`VALUE`. `metrics` selects backend/cache/fsstats and optionally passes `interval`. `mount` collects source, mountpoint, config path, and type into a context map. `umount` collects mountpoint. If no recognized subcommand is provided, the program returns `Ok(())` without printing help.

## State And Persistence
The file itself keeps no persistent state. It can cause daemon state changes by dispatching `set`, `mount`, and `umount`. All command context is transient `HashMap<String, String>` data.

## Dependencies And Integration Points
It integrates Clap argument parsing, Tokio runtime setup, the local `client` and `commands` modules, and the shared Nydus build-info helper. It is the user-facing companion to `nydusd/api_server_glue.rs`.

## Risks
The CLI requires `--sock` as a non-global argument; users must provide it before subcommands according to Clap behavior. Several required values are unwrapped after Clap validation. There is no explicit fallback help output when no subcommand matches. The accepted `metrics --interval` string is validated later, not by Clap.

## Test Signals
There are no direct tests in this file. Existing tests in `client.rs` and `commands.rs` cover the components it dispatches to. Useful integration tests should run `nydusctl` against a test API socket for each subcommand and raw/non-raw output mode.
