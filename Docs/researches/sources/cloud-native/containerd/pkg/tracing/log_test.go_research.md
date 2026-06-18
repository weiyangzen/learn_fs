<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/log_test.go -->
# sources/cloud-native/containerd/pkg/tracing/log_test.go

## Purpose
Unit tests for trace_id field injection in LogrusHook.

## Important APIs, Types, And Functions
TestLogrusHookTraceID uses fixed TraceID/SpanID and table cases.

## Control Flow
Each case builds a context with or without span context, fires the hook, and asserts trace_id presence/value.

## State And Persistence
Pure in-memory test state.

## Dependencies And Integration Points
Exercises NewLogrusHook, WithTraceIDField, and Fire.

## Risks And Edge Cases
Does not cover recording span event emission or attribute conversion.

## Test Signals
Direct coverage for log correlation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/log_test.go -->
