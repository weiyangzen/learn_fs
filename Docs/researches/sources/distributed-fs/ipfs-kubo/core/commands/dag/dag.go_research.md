<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/dag.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/dag.go

## Purpose

Defines the `ipfs dag` command family and shared output types for IPLD DAG put, get, resolve, import, export, and stat.

## Important APIs, Types, and Functions

`DagCmd` registers all DAG subcommands. Output types include `OutputObject`, `ResolveOutput`, `CarImportStats`, `CarImportOutput`, `RootMeta`, `DagStat`, and `DagStatSummary`. Command variables configure help, arguments, options, encoders, and post-run hooks for `DagPutCmd`, `DagGetCmd`, `DagResolveCmd`, `DagImportCmd`, `DagExportCmd`, and `DagStatCmd`.

## Control Flow

This file primarily wires handlers implemented in sibling files. Encoders handle CID base selection, import root/status formatting, and DAG stat tabular/JSON output. `DagResolveCmd` infers CID output base from the input path unless `--cid-base` is explicitly set. `DagImportCmd` exposes pin, local-only, stats, and fast-provide knobs, with text output validating event shape.

## State and Persistence Behavior

The state effects are in sibling handlers: DAG put/import write blocks and may pin/provide, export/get/stat/resolve read DAG state. This file defines command metadata and output formatting only.

## Dependencies and Integration Points

Uses `go-ipfs-cmds`, CID encoders, `cmdutils.AllowBigBlockOption`, human-size formatting, CSV/JSON encoders, and constants shared by DAG sibling files.

## Risks and Edge Cases

Event encoders assume import events contain exactly one of `Root` or `Stats`. `DagStatSummary.calculateSummary` divides by total size and assumes nonzero traversal. CID-base inference in resolve intentionally falls back if path extraction fails.

## Test Signals

Command tree tests cover DAG subcommand registration. Behavior coverage should target each sibling handler plus text/JSON encoders for import and stat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/dag.go -->
