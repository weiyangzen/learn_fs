# sources/control-plane/rook/pkg/util/error.go

## Purpose
`error.go` aggregates multiple errors into a single human-readable error message.

## Important APIs, Types, and Functions
`AggregateErrors(errs []error, format string, args ...interface{}) error` returns nil for no errors or an `errors.Errorf` with a formatted header and one indented line per error.

## Control Flow, State, and Persistence
The function is pure. It discards wrapped error structure and keeps only `err.Error()` text in the aggregate message.

## Dependencies and Integration Points
It depends on `fmt` and `github.com/pkg/errors`. Reconciler paths can use it to report multiple validation or cleanup failures together.

## Risks
Structured error identity is lost, so `errors.Is`/`As` cannot inspect original causes through the aggregate. Nil entries in a non-empty slice would panic when calling `err.Error()`.

## Test Signals
No direct mapped tests. Useful signals would cover empty lists, formatting args, multiple errors, nil error entries, and wrapped error identity expectations.
