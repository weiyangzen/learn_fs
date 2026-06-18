# sources/cloud-native/composefs-rs/crates/composefs-ctl/src/main.rs

## Purpose
This binary entry point implements `cfsctl` multi-call behavior. It dispatches directly to `mkcomposefs` or `composefs-info` when invoked under those names, supports `cfsctl mkcomposefs ...` and `cfsctl composefs-info ...`, initializes containers-storage helper mode when applicable, and otherwise starts the async `cfsctl` CLI.

## Important APIs, types, and functions
`binary_name` extracts `argv[0]` basename. `rest_of_args` returns arguments after the hidden tool token. `main` performs multi-call dispatch and creates the Tokio runtime for the primary CLI. `async_main` initializes logging, handles bare systemd socket activation through `run_if_socket_activated`, parses `App`, and calls `composefs_ctl::run_app`.

## Control flow
The first dispatch branch uses argv0 names `mkcomposefs` and `composefs-info`. The next branches inspect `argv[1]` to forward hidden subcommands before clap parsing. For normal `cfsctl`, containers-storage helper initialization runs before the Tokio runtime is created. The runtime then executes `async_main`, which checks socket activation before clap so a no-argument activated process can serve varlink.

## State and persistence behavior
This file owns no repository state, but it determines which subsystem receives process control. It initializes environment-based logging and may serve a long-lived varlink service. The containers-storage helper path can exit early if the process was spawned as a helper.

## Dependencies and integration points
It depends on `composefs_ctl` library APIs, `tokio` runtime construction, `env_logger`, `clap::Parser`, and optional `cstorage::init_if_helper`. It is the integration point for symlink/hardlink compatibility binaries and systemd socket activation behavior.

## Risks
`std::env::args_os().nth(1)` is called separately in match guards; this is fine because each call creates a fresh iterator, but it is easy to misread. Multi-call dispatch bypasses `env_logger::init` for direct `mkcomposefs` and `composefs-info`. Runtime creation happens after hidden tool dispatch, so those tools cannot use async code unless they create their own runtime. Socket activation must remain before clap for bare activation but after helper initialization for containers-storage semantics.

## Test signals
There are no local tests. Integration tests should cover argv0 dispatch, hidden subcommand forwarding including `--help`, normal CLI dispatch, containers-storage helper startup ordering, and no-argument socket activation.
