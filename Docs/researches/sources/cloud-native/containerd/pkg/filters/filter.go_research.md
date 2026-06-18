<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/filter.go -->
# sources/cloud-native/containerd/pkg/filters/filter.go

Purpose: filter composition and selector matching for containerd's generic filter language.

Important APIs and types: `Filter`, `FilterFunc`, `Always`, `Any`, `All`, `operator`, and `selector`.

Control flow and state: `Any.Match` short-circuits on first matching filter; `All.Match` short-circuits on first non-match. `selector.Match` queries the adaptor and applies present, equal, not-equal, or regexp match operators. Regex patterns are compiled lazily into `selector.re`, but because the receiver is by value this cache is not retained across calls.

Dependencies and integration: parser builds these selectors from user filter strings; logging reports regex compile failures.

Risks and test signals: `operatorNotEqual` returns true for missing fields whose value is empty unless adaptor returns the same value, matching existing semantics. Lazy regex cache by value may repeatedly compile. Tests cover operator strings and filter behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/filter.go -->
