# sources/control-plane/rook/cmd/rook/ceph/ceph.go

## Purpose

Defines the hidden top-level `rook ceph` Cobra command and shared Ceph command configuration.

## Important APIs, Types, and Functions

`Cmd` is the hidden parent command for Ceph operator and daemon commands. Package globals include `cfg`, `clusterInfo`, and `logger`. The `config` struct stores device, metadata device, data dir, force format, CRUSH location, config override, OSD store config, monitor endpoints, node name, and PVC-backed flags. `createContext()` returns a Rook cluster context with config directory/override. `addCephFlags()` registers shared Ceph flags and reads namespace from the pod namespace environment variable.

## Control Flow

Package `init()` attaches cleanup, operator, OSD, mgr, and config subcommands. Subcommands call `createContext` and `addCephFlags` as needed to share cluster identity and config handling.

## State and Persistence Behavior

This file initializes process-level globals and reads environment state. Persistent effects are produced by subcommands, not by this parent file directly.

## Dependencies and Integration Points

It integrates with Cobra, Rook context creation, Ceph client cluster info, OSD store config, Kubernetes namespace environment conventions, and all Ceph subcommands.

## Risks and Edge Cases

Global mutable `cfg` and `clusterInfo` simplify CLI wiring but couple subcommands within one process. Namespace is captured during flag registration, so callers must ensure the pod namespace environment variable exists before command execution.

## Test Signals

Coverage is indirect through command/unit tests and integration tests that launch `rook ceph operator`, OSD, mgr, cleanup, and config subcommands.
