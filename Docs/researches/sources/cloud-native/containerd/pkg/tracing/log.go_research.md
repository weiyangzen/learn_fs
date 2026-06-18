<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/log.go -->
# sources/cloud-native/containerd/pkg/tracing/log.go

## Purpose
Logrus hook that turns log entries into OpenTelemetry span events and can inject trace_id into log fields.

## Important APIs, Types, And Functions
NewLogrusHook, WithTraceIDField, LogrusHook.Levels, Fire, and logrusDataToAttrs.

## Control Flow
Fire extracts span from entry context, optionally adds trace_id to entry.Data when span context is valid, and if recording adds a span event with log fields, level, and timestamp.

## State And Persistence
Mutates the log entry Data map by adding trace_id when enabled. No persistence.

## Dependencies And Integration Points
Depends on containerd/log and otel trace/attribute. Used to correlate logs and traces.

## Risks And Edge Cases
entry.Data must be non-nil if trace_id injection is enabled. Non-recording spans still get trace_id injection but no event.

## Test Signals
log_test.go covers trace_id injection enabled, disabled, and no-span cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/log.go -->
