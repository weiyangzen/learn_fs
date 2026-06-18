# sources/distributed-fs/beegfs-go/ctl/internal/util/error.go

Purpose: defines CTL-specific errors that carry an intended process exit code.

Important APIs/types/functions: `CtlError`; `CtlExitCode`; constants `Success`, `GeneralError`, `PartialSuccess`; `NewCtlError`; `GetExitCode`; `Error`.

Control flow: commands wrap an underlying error and exit-code classification, then the top-level command runner can inspect the error type and choose the exit code.

State and persistence: no state.

Dependencies and integration points: used by command packages such as remote push/status/cleanup to distinguish partial success from fatal failure.

Risks: `GetExitCode` has pointer receiver while `NewCtlError` returns a value; callers using type assertions must account for value vs pointer forms. There is no `Unwrap`, so standard `errors.Is/As` cannot inspect the inner error through `CtlError`.

Test signals: no direct tests. Useful tests would cover string conversion, exit-code values, and top-level error handling for value/pointer assertions.
