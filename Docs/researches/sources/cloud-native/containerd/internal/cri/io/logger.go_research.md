# sources/cloud-native/containerd/internal/cri/io/logger.go

## Purpose

This file converts raw container stdout/stderr bytes into CRI log format. It emits timestamped lines with stream name and full/partial tags, splits overly long lines, preserves partial final lines, drains output on write errors, and updates CRI logging metrics.

## Important APIs, Types, and Functions

`NewDiscardLogger` returns a write closer backed by `io.Discard`. `NewCRILogger(path, w, stream, maxLen)` creates an `io.Pipe`, starts `redirectLogs`, and returns the writer plus a stop channel. `readLine` is a custom buffered line reader that distinguishes newline-terminated lines from EOF without newline. `redirectLogs` performs CRI formatting, line splitting, metric increments, and final cleanup.

## Control Flow

`redirectLogs` reads with a bounded `bufio.Reader`, accumulates chunks in `buf`, and tracks total length. When `maxLen` is exceeded, it emits a partial line containing the first `maxLen` bytes and retains the overflow for the next output entry. When a complete line is seen, it emits a full tag; when EOF/error arrives with buffered bytes and no newline, it emits a partial tag. Each output line is formatted as timestamp, stream, tag, payload, newline.

## State and Persistence Behavior

The file writes to the provided writer, normally a container log file. It does not open the path itself; `path` is used for diagnostics. Metrics counters track input entries/bytes, output entries/bytes, and split-created entries.

## Dependencies and Integration Points

It uses CRI log tag constants, containerd `pkg/ioutil`, logging, and counters from `metrics.go`. Container creation/start paths pass log writers into container IO writer groups.

## Risks and Edge Cases

Line splitting has careful boundary logic around buffer size, CRLF, EOF without newline, and `maxLen <= 0`. Write errors are logged but do not stop draining, avoiding container blockage at the cost of dropped log output. The custom `readLine` panics on theoretically impossible `UnreadByte` or unexpected error states.

## Test Signals

`logger_test.go` covers stdout/stderr, newline and no-newline endings, exact buffer boundaries, long lines, disabled max length, non-divisible max length, and CRLF behavior. Additional tests could assert metric increments and write-error draining.
