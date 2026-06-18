# sources/distributed-fs/ceph/src/rgw/rgwam.py

## Purpose

`rgwam.py` is the command-line wrapper for the RGW assist-for-multisite tooling. It parses top-level `realm` and `zone` subcommands, adapts CLI environment options to `RGWAMEnvMgr`, invokes `RGWAM` core operations, and reports command failures. The file was read as a complete 240-line Python script.

## Important APIs, Types, and Functions

`RGWAMCLIMgr` builds a `ceph`/tool argument prefix from `-c`, `-n`, and `-k`, executes external programs via `subprocess.run()`, and stubs orchestrator-style methods `apply_rgw()` and `list_daemons()`. `RealmCommand` dispatches `bootstrap` and `new_zone_creds`. `ZoneCommand` dispatches `run` and `create`. `CommonArgs` stores common Ceph options. `TopLevelCommand._parse()` handles top-level command parsing and help propagation. `main()` sets logging, builds `EnvArgs`, invokes the selected command, and exits based on return code or `RGWAMException`.

## Control Flow

CLI flow starts in `main()`, which calls `TopLevelCommand()._parse()`. The top-level parser separates common options from the remaining subcommand args and preserves subcommand help flags by removing them before top-level parsing and appending them back. The selected top-level method constructs a subcommand class, whose `parse()` maps hyphenated subcommand names to method names, creates a subparser for command-specific arguments, and returns the matching bound method. That method delegates to `RGWAM(self.env)` core methods such as `realm_bootstrap()`, `realm_new_zone_creds()`, `zone_create()`, or `run_radosgw()`.

## State and Persistence Behavior

This script owns no persistent state. Persistence and cluster mutation are delegated to `RGWAM` core and external tools invoked through `RGWAMCLIMgr.tool_exec()`. Runtime state is limited to parsed arguments, command prefixes, stdout/stderr from subprocesses, and process exit status.

## Dependencies and Integration Points

It imports `ceph.rgw.rgwam_core.RGWAM`, `EnvArgs`, `ceph.rgw.types.RGWAMEnvMgr`, and `RGWAMException`. It also imports several standard modules, though some are unused in this wrapper (`random`, `string`, `json`, `socket`, `base64`, `urlparse`). The command is processed by build tooling to substitute the Python shebang/version.

## Risks and Edge Cases

The dynamic dispatch pattern requires method names to match parsed command names after hyphen replacement for realm commands; zone commands currently check the literal subcommand name, which works for `run` and `create` but would need care for future hyphenated zone subcommands. `RGWAMCLIMgr.tool_exec()` decodes stdout/stderr as UTF-8 without error handling. `apply_rgw()` and `list_daemons()` are no-ops in the CLI manager, so any core path requiring orchestrator behavior must handle that. `RGWAMException` handling prints `e.message`, which depends on that attribute being present.

## Test Signals

Tests should cover parser dispatch for each command, subcommand `-h/--help` behavior, propagation of common `-c/-n/-k` arguments into `tool_exec()`, nonzero return logging/exit behavior, `RGWAMException` rendering, and CLI integration with mocked `RGWAM` core methods.
