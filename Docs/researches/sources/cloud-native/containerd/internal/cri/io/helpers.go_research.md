# sources/cloud-native/containerd/internal/cri/io/helpers.go

## Purpose

This file contains shared CRI IO primitives: attach option shape, stream type constants, FIFO/stream URL construction, stdio opening, and a waitgroup-aware closer used by both container and exec IO.

## Important APIs, Types, and Functions

`AttachOptions` carries client stdin/stdout/stderr, TTY mode, `StdinOnce`, and a `CloseStdin` callback to close the runtime side. `StreamType` defines `Stdin`, `Stdout`, and `Stderr`. `wgCloser` owns a cancelable context, waitgroup, and closers. `newFifos` creates `root/io` and a `cio.FIFOSet`, blanking stdin when disabled. `newStreams` builds a `cio.FIFOSet` containing streaming URLs with `streaming_id` query parameters. `newStdioStream` opens the configured stdin/stdout/stderr endpoints. `openStdin` and `openOutput` choose local pipe versus streaming endpoint by checking for `://`.

## Control Flow

`newStdioStream` creates a background context and opens each configured endpoint in order. If any open fails, already-opened closers are closed and the context is canceled. The returned `wgCloser` lets callers wait for copy goroutines, close all endpoints, or cancel pending opens/copies. URL-less endpoints go through platform `openPipe`; URL endpoints go through streaming helpers.

## State and Persistence Behavior

The only persistent filesystem state created here is the FIFO directory and FIFO files under the supplied root. Streaming mode stores no local files; it encodes stream identity into URL fields that are later opened on demand.

## Dependencies and Integration Points

It depends on CRI runtime stream constants, `pkg/cio`, standard `syscall` open flags, and platform-specific `openPipe` implementations. It is the central abstraction used by `container_io.go` and `exec_io.go`.

## Risks and Edge Cases

The local-versus-stream decision is string-based on `://`, so malformed paths containing that token would be treated as URLs. Partial open failures must close already-opened resources. Stdin can be disabled by blanking its path, which must be respected by attach logic. Stream URL query key must match the streaming server contract.

## Test Signals

Tests should validate FIFO path layout, stdin disabled behavior, stream URL generation for TTY and non-TTY, partial open cleanup, and local/stream dispatch.
