# sources/cloud-native/moby/integration-cli/checker/checker.go

## Purpose
Compatibility comparison helpers for legacy integration-cli assertions.

## Important APIs and Types
Defines `Compare` and helpers `False`, `True`, `Equals`, `Contains`, `Not`, `DeepEquals`, `HasLen`, `IsNil`, and `GreaterThan`.

## Control Flow, State, and Persistence
Each helper returns a function that adapts a value into a `gotest.tools/assert` comparison. `Not` negates another comparison and preserves diagnostic strings.

## Dependencies, Integration Points, Risks, and Test Signals
Used by older tests that predate direct gotest-tools calls. It stores no state. Risks are weak typing with `any`, diagnostics that may be less precise than direct assertions, and divergence from upstream assertion semantics. Compile and legacy test execution validate it.
