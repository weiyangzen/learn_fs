<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/context.go -->
# sources/cloud-native/containerd/pkg/epoch/context.go

Purpose: context carrier for `SOURCE_DATE_EPOCH` values without relying on environment variables.

Important APIs and types: private context key type, `WithSourceDateEpoch`, and `FromContext`.

Control flow and state: `WithSourceDateEpoch` stores a `*time.Time` in context; `FromContext` retrieves it and returns nil when absent or wrong type.

Dependencies and integration: used by `archive.WriteDiff` to apply reproducible timestamp limits from context if no explicit write option is set.

Risks and test signals: stores a pointer, so caller mutation of the pointed time after insertion would affect readers. This file intentionally does not read the environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/context.go -->
