# sources/cloud-native/moby/daemon/internal/cleanups/composite_test.go

## Purpose
Tests cleanup aggregation and reverse execution order.

## APIs, Control Flow, and Integration
`TestCall` registers four cleanups: one direct error, one nil, one wrapped error, and one `errors.Join` group. It calls `Composite.Call`, unwraps the multi-error, checks all component messages/errors are present, and asserts reverse-order placement for the non-nil cleanup errors.

## State, Dependencies, and Risks
No external state. The test documents that nil cleanup results are omitted from the joined error and that wrapped/joined errors remain discoverable with `errors.Is`. It does not cover `Release` behavior or concurrent mutation.
