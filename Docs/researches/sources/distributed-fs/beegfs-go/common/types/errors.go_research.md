# sources/distributed-fs/beegfs-go/common/types/errors.go

Purpose: defines `MultiError`, a small aggregate error type for combining independent operation failures.

Important APIs are `MultiError.Errors`, `(*MultiError).Error`, and `(*MultiError).Unwrap() []error`.

Control flow: `Error` iterates over contained errors, collects each `err.Error()` string, and joins them with `"; "`. `Unwrap` returns the underlying slice to support Go 1.20 multi-error unwrapping semantics for `errors.Is` and `errors.As`.

State is the exported `Errors []error` field. There is no persistence.

Dependencies are only `strings`.

Integration points are callers that need to return multiple failures while preserving sentinel matching. The file comment warns that `errors.Is` or `errors.As` will match any contained chain, not a specific operation.

Risks: nil entries in `Errors` would panic in `Error`. The exported slice can be mutated by callers after construction. There is no formatting that includes operation labels, so context must be embedded in each child error.

Test signals: no direct tests in this subset.
