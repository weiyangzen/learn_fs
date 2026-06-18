# sources/distributed-fs/eos/namespace/ns_quarkdb/tools/InspectionTool.cc

## Purpose
`InspectionTool.cc` is the main command-line front end for inspecting, scanning, validating, and repairing a QuarkDB-backed EOS namespace. It wires a large CLI surface to the `Inspector` service and its output sinks.

## Important APIs, Types, and Functions
`MemberValidator` validates comma-separated QuarkDB member strings through `qclient::Members::parse()`. `IdValidator` validates uint64 strings but is not actively used in the visible option setup. `addClusterOptions()` attaches common `--members`, retry, password, and password-file options. `addDryRun()` adds the common `--no-dry-run` gate for mutating commands. `main()` defines all subcommands and dispatches to `Inspector` methods.

## Control Flow
The CLI requires a subcommand. Read-only commands include deprecated `dump`, `scan`, `print`, `stripediff`, `one-replica-layout`, `scan-dirs`, `scan-files`, `scan-deathrow`, `check-naming-conflicts`, `check-cursed-names`, `check-orphans`, `check-fsview-missing`, `check-fsview-extra`, `check-shadow-directories`, and `check-simulated-hardlinks`. Dangerous repair commands include `fix-detached-parent`, `fix-shadow-file`, `drop-from-deathrow`, `drop-empty-cid`, `change-fid`, `rename-fid`, `rename-cid`, and `overwrite-container`; these default to dry-run unless `--no-dry-run` is supplied. After parsing, the tool reads an optional password file, parses an optional metadata filter expression, constructs `QdbContactDetails`, builds a `qclient::QClient`, selects a text or JSON output sink, checks connectivity, sets the metadata filter, and dispatches to exactly one `Inspector` method.

## State and Persistence Behavior
Read-only commands stream namespace metadata and consistency findings. Repair commands can mutate FileMD, ContainerMD, deathrow entries, parent/container maps, fsview-related metadata, or raw protobuf fields depending on the selected inspector method. Dry-run is the default for commands marked dangerous, but the tool still connects to and scans live QuarkDB.

## Dependencies and Integration Points
The tool integrates CLI11, QuarkDB `qclient`, EOS password handling, `QdbContactDetails`, metadata filter parsing, inspector operations, and output sink abstractions (`StreamSink`, `JsonStreamSink`, `JsonLinedStreamSink`). It is an operational entry point over the lower-level namespace inspector library.

## Risks and Edge Cases
Because this file is mostly option wiring, risks concentrate in argument ambiguity, dry-run semantics, and dispatch correctness. Shared variables such as `fid`, `cid`, `json`, `fullPaths`, and `newParent` are reused across subcommands; CLI11 subcommand isolation makes that workable but easy to break when adding options. Several commands are explicitly dangerous and rely on operator intent plus `--no-dry-run`. Client-side filtering still streams all metadata, so `--where` can be expensive. Password-file permission checks happen in `PasswordHandler`, and connection retry behavior changes when `--connection-retries` is zero.

## Test Signals
Useful tests should cover command parsing, required option groups, default dry-run behavior, password/password-file exclusivity, JSON/minimal sink selection, filter parse failures, connectivity failure handling, and one dispatch smoke test per subcommand using a fake or controlled `Inspector`.
