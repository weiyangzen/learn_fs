# sources/cloud-native/containerd/core/content/adaptor.go

Purpose: filter adaptor for `content.Info` values.

Important APIs: `AdaptInfo(info Info)` returns a `filters.Adaptor` supporting `digest` and `labels.*` field paths. `checkMap` joins nested label field path components with `.` before looking up a map key.

Control flow and state: stateless closure over one `Info`. Empty field paths are absent. `size` is recognized but deliberately unsupported with a TODO for size-based filtering.

Dependencies and integration: integrates with containerd's `pkg/filters` package, allowing content stores or walkers to evaluate filters against content metadata.

Risks: label keys containing dots are intentionally addressed through joined field paths, but there is no escaping distinction between nested and literal dots. Size filters silently appear unsupported, which can surprise callers.

Test signals: `adaptor_test.go` covers empty paths, digest, unsupported size, simple labels, and dotted label keys.
