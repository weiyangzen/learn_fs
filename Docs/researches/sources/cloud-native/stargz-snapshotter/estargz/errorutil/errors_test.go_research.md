# sources/cloud-native/stargz-snapshotter/estargz/errorutil/errors_test.go

Purpose: Verifies legacy behavior of the deprecated `errorutil.Aggregate` helper.

Important APIs tested: `Aggregate`.

Control flow: `TestNoError` expects nil for nil and empty slices. `TestOneError` expects the exact same error object to be returned for a single input. `TestMultipleErrors` expects a non-nil error whose string exactly matches the historical multi-line format.

State and persistence: No state or I/O.

Dependencies and integration: Uses standard `errors` and `testing`.

Risks covered: Protects compatibility-sensitive formatting and object identity. Since the helper is deprecated, these tests mainly prevent accidental behavior drift before removal.

Test signals: Complete for the tiny helper's current branching logic. Does not test nil elements inside a non-empty slice.
