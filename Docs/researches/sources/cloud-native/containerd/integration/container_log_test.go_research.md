# sources/cloud-native/containerd/integration/container_log_test.go

## Purpose

This file validates CRI container log formatting for edge cases around partial lines and maximum log line splitting. It ensures containerd writes Kubernetes CRI log lines with timestamps, streams, tags, and payloads in the expected shape.

## Important APIs, Types, And Functions

- `TestContainerLogWithoutTailingNewLine` verifies output without a trailing newline is tagged as `P`/partial.
- `TestLongContainerLog` verifies lines at `MaxContainerLogLineSize - 1`, exactly at max, and over max are tagged/split correctly.
- `checkContainerLog` parses log lines and validates RFC3339Nano timestamps plus expected CRI stream/tag/message fields.
- `CRIConfig` provides the configured max log line size.

## Control Flow

Each test creates a temporary pod log directory, starts a sandbox with `WithPodLogDirectory`, creates a BusyBox container with `WithLogPath`, waits until the container exits, reads the log file, and checks its lines. The long-line test constructs shell loops that print repeated characters to exercise full and partial line behavior.

## State And Persistence Behavior

The relevant persisted state is the pod log file under the temporary log directory. The test does not mutate long-lived containerd state beyond normal sandbox/container creation and cleanup.

## Dependencies And Integration Points

It depends on CRI log configuration, CRI runtime status polling, BusyBox shell behavior, and `k8s.io/cri-api` constants for stream and log tag names. It also integrates with the shared `CRIConfig` helper, which reads verbose CRI status.

## Risks And Edge Cases

The test is sensitive to exact log tag semantics and max-size configuration. The shell loop uses `printf` without quoting the payload character, which is safe for the fixed characters used here. It assumes log writing is complete by the time container state is `EXITED`.

## Test Signals

Passing confirms CRI logs preserve partial final lines, split oversized lines, and use parseable timestamps and expected tags.
