# sources/control-plane/mayastor/io-engine/src/lvm/cli.rs

## Purpose
This file is the async process-execution layer for the LVM backend. It wraps `pvcreate`, `vgcreate`, `lvs`, `dmsetup`, `blockdev`, and related commands, standardizes JSON report parsing, and provides query argument and serde helpers.

## Important APIs, types, and functions
`CmnQueryArgs` carries optional name, uuid, and tag filters with constructors for all resources, Mayastor-owned resources, and optional filters. `LvmSubCmd` maps enum variants to concrete command names using `strum`. `LvmCmd` wraps a `tokio::process::Command`, optional stdin, and command name.

Builder methods construct specific subcommands and append arguments/tags. `report<T>` expects LVM's top-level JSON `report` array and returns the first report block. `output_json<T>` decodes command stdout as JSON. `run` discards output on success. `output` executes the command, handles SPDK-thread trampoline via `crate::tokio_run!`, maps spawn failures and non-zero exits to `Error`, and logs the command at trace level. `cmder` optionally writes stdin and uses `pre_exec` to set `CLOEXEC` on fd range 3..1024. `de::number_from_string` and `de::comma_separated` decode LVM JSON fields.

## Control flow
Callers build a command fluently, then await `run`, `output`, `output_json`, or `report`. If running on an SPDK thread, process execution is submitted onto the tokio runtime and the result is returned through a oneshot bridge. JSON report callers depend on upstream arguments including `--report-format=json`.

## State and persistence behavior
The file itself keeps no durable state, but commands mutate host LVM/device-mapper state. LVM tags are passed as command-line flags through `Property::add`/`del`. Stdin is consumed once when present.

## Dependencies and integration points
It depends on `tokio::process`, `tokio::io::AsyncWriteExt`, `serde`, `snafu`, `nix`, `strum`, and the LVM property/error modules. It is the foundation used by `vg_pool`, `lv_replica`, and `dm_setup`.

## Risks and test signals
Command error mapping relies on stderr text at higher layers, so LVM version/localization changes are risky. `close_range(3,1024)` is a bounded best-effort fd cleanup and may miss higher descriptors. The SPDK-thread trampoline is critical to avoid blocking reactors. Tests should mock or isolate LVM binaries; high-value cases include JSON parse failures, report-missing, stdin command execution, non-zero exit mapping, and query argument validation.
