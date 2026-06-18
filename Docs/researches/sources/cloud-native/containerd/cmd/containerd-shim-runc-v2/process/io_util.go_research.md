# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io_util.go

## Purpose
Contains utility helpers for shim binary IO, command construction, pipe wrappers, file closing, and conditional runc IO creation.

## Important APIs, Control Flow, And State
The file provides helpers used by `io.go` and console logging paths: creating OS pipe structs, closing groups of files, constructing the logging binary command from a `binary://` or `binary-v2://` URI, and selecting conditional stdin/stdout/stderr pipe creation based on stdio config. It centralizes low-level fd and command details so both terminal and nonterminal logging can pass the expected extra file descriptors. State is OS file descriptors and spawned command configuration; no daemon metadata is mutated.

## Dependencies And Integration
Depends on OS/exec/url/filepath-style primitives, go-runc IO options, and stdio configuration. It is tightly integrated with `NewBinaryIO` and `linuxPlatform.CopyConsole`.

## Risks And Test Signals
Risks include URI-to-command compatibility, fd ordering mismatches with logger binaries, failure to close all descriptors on errors, and nil/empty stdio handling. Tests should cover command args/env, close error aggregation, conditional IO options, and malformed URI inputs.
