<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/helpers_spanopts.go -->
# sources/cloud-native/containerd/pkg/tracing/helpers_spanopts.go

## Purpose
Span option helper that adds containerd namespace attribute when present.

## Important APIs, Types, And Functions
WithNamespace returns a SpanOpt that appends trace.WithAttributes(Attribute("namespace", ns)) if namespaces.NamespaceRequired succeeds.

## Control Flow
When StartSpan applies the option, it reads namespace from the supplied context and appends span options best-effort.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Integrates pkg/namespaces with OpenTelemetry tracing helpers.

## Risks And Edge Cases
Missing namespace is silently ignored, so absence may be hard to diagnose in traces.

## Test Signals
No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/helpers_spanopts.go -->
