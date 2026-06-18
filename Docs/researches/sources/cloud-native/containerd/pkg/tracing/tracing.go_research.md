<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/tracing.go -->
# sources/cloud-native/containerd/pkg/tracing/tracing.go

## Purpose
General OpenTelemetry tracing convenience wrappers for spans, attributes, HTTP clients, and status mapping.

## Important APIs, Types, And Functions
StartConfig, SpanOpt, WithAttribute, UpdateHTTPClient, StartSpan, SpanFromContext, Span methods, Name, Attribute, and HTTPStatusCodeAttributes.

## Control Flow
StartSpan applies SpanOpts, chooses parent tracer provider when valid, starts a span, and wraps it. Span methods delegate to otel span operations. UpdateHTTPClient wraps transport with otelhttp.

## State And Persistence
Mutates http.Client.Transport in place; spans are exported according to global provider state.

## Dependencies And Integration Points
Depends on otel, otelhttp, trace/codes/attribute. Used throughout containerd for consistent tracing APIs.

## Risks And Edge Cases
UpdateHTTPClient overwrites any existing transport by wrapping it; callers must configure client before calling. Name simply joins with dots and does not sanitize segments.

## Test Signals
Covered indirectly by tracing users; log tests cover context/span interaction partially.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/tracing.go -->
