# sources/cloud-native/stargz-snapshotter/estargz/errorutil/errors.go

Purpose: Provides a deprecated error aggregation helper retained for compatibility.

Important API: `Aggregate(errs []error) error`. It returns nil for an empty slice, the sole error unchanged for one entry, or a new formatted error listing all messages for multiple entries.

Control flow: Uses a switch on slice length. The multiple-error case builds a string slice with header `N error(s) occurred:` and bullet lines prefixed with tab plus `*`, then returns `errors.New(strings.Join(...))`.

State and persistence: Stateless, no I/O.

Dependencies and integration: Uses standard `errors`, `fmt`, and `strings`. The comment marks it deprecated in favor of `errors.Join` and scheduled for removal in v0.19.0.

Risks: Unlike `errors.Join`, the returned aggregate does not preserve `errors.Is`/`errors.As` behavior for individual errors. Formatting is part of existing test expectations, so changing it can break consumers.

Test signals: `errors_test.go` covers nil/empty, single-error identity, and exact multi-error formatting.
