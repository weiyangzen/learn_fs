<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/adaptor.go -->
# sources/cloud-native/containerd/pkg/filters/adaptor.go

Purpose: abstraction layer mapping parsed filter field paths to concrete object values.

Important APIs and types: `Adaptor`, `AdapterFunc`, and `AdapterFunc.Field`.

Control flow and state: no state. `AdapterFunc` lets callers use closures as adaptors by implementing `Field(fieldpath []string)`.

Dependencies and integration: consumed by `Filter.Match` implementations in `filter.go`; callers implement this to adapt containers/images/tasks/etc. to generic filter syntax.

Risks and test signals: field path semantics are caller-defined, so interoperability depends on consistent adaptor implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/adaptor.go -->
