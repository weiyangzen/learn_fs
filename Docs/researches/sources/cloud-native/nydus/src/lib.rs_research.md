# sources/cloud-native/nydus/src/lib.rs

## Purpose
`lib.rs` is the shared crate facade used by Nydus binaries. It re-exports service APIs, logging, signal registration, and provides small helpers for command-line argument access and build-time version reporting.

## Important APIs, Types, And Functions
`SubCmdArgs` wraps top-level and subcommand `ArgMatches`, with `new` and `values_of`. Its `ServiceArgs` implementation provides `value_of` and `is_present`, checking subcommand values first and falling back to global/top-level values. The `built_info` module exposes compile-time environment values. `dump_program_info` logs version information. `get_build_time_info` returns both a formatted version string and a `BuildTimeInfo` struct.

## Control Flow
Binaries call `get_build_time_info` to populate Clap versions and daemon API info. `nydusd` wraps parsed arguments in `SubCmdArgs` so shared service constructors can read either subcommand-specific or global options. `dump_program_info` logs build details after logging is initialized.

## State And Persistence
This file has no mutable state. Build info is compiled into constants through environment variables. Logging output is produced by callers that invoke `dump_program_info`.

## Dependencies And Integration Points
It depends on Clap `ArgMatches`, `nydus_api::BuildTimeInfo`, the local `logger` and `signal` modules, and re-exports all of `nydus_service`. It is imported by `nydus-image`, `nydusctl`, and `nydusd`.

## Risks
The `ServiceArgs::value_of` fallback uses `try_get_one(...).unwrap_or_default()`, suppressing Clap lookup errors as absent values. `is_present` only recognizes boolean flags with value `true`, not counted flags or value presence. Build info environment variables must be defined by the build system or compilation fails.

## Test Signals
There are no direct tests. Effective coverage is indirect through CLI binaries using build-info strings and `SubCmdArgs` in global/subcommand option combinations.
