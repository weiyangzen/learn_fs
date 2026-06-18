# sources/cloud-native/moby/daemon/events/filter.go

Purpose: converts API filter arguments into event-stream predicates for daemon event subscriptions.

Important APIs and control flow: `Filter` wraps `filters.Args`. `Include` composes event action, type, scope, per-object name/ID filters, image matching, and label matching. `matchEvent` preserves compatibility for `health_status`, `exec_create`, and `exec_start` by fuzzily matching action prefixes when users filter without the suffix after the colon. `fuzzyMatchName` matches either actor ID or `Actor.Attributes["name"]` against the event-type-specific filter key. `matchImage` handles both image events (`name` attribute) and container events (`image` attribute), comparing full ID/name and `stripTag` variants. `stripTag` uses distribution reference parsing and falls back to the original string on parse failure.

State, dependencies, and risks: the filter is stateless after construction and depends on `daemon/internal/filters` matching semantics plus distribution reference normalization. Matching is intentionally permissive for historical event strings. Risks include unexpected matches from fuzzy name filters, and `stripTag` returning familiar repository names that may collide across registries. Test coverage is indirect through event subscription behavior; no dedicated filter table tests appear in this group.
