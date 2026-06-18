# sources/cloud-native/containers-storage/pkg/mflag/flag.go

Purpose: implements a Docker-derived command-line flag package with multiple names per flag, deprecated/hidden names, grouped short booleans, argument-count validation, and flag-set merging.

Important APIs, types, and functions: value types for bool/int/int64/uint/uint64/uint16/string/float64/duration; `Value`, `Getter`, `ErrorHandling`, `FlagSet`, `Flag`; top-level `CommandLine`; registration methods like `BoolVar`, `Int`, `String`, `Duration`; lookup/visit/set helpers; `Parse`, `ParseFlags`, `ReportError`, `Require`, `CheckArgs`, `Merge`, and `IsEmpty`.

Control flow: flags are registered in `formal` under every normalized name, with `#` stripped for lookup but retained in `Flag.Names` to hide/deprecate usage output. `parseOne` consumes one flag, splits `name=value`, strips quotes, handles implicit boolean true, consumes following args for non-bools, emits deprecation warnings, and records `actual`. Unknown multi-letter names return `ErrRetry`, causing `Parse` to retry letter-by-letter for grouped short flags.

State and persistence: no persistence. State lives in `FlagSet`: parsed args, formal definitions, actual values, output writer, and argument requirements. Top-level helpers mutate the global `CommandLine`.

Dependencies and integration points: depends on stdlib parsing/formatting packages and `homedir` for usage path shortening. Used by CLI entry points needing Docker-compatible flag behavior.

Risks and edge cases: not concurrency-safe. `ShortUsage` writes to `CommandLine.output` directly and can be nil. `ParseFlags` exits the process on help or bad args. Grouped-short retry can produce surprising behavior for unknown multi-letter flags. Duplicate names panic in `Var`.

Test signals: `flag_test.go` covers all built-in value types, parsing forms, quotes, help, count functions, deprecated/hidden names, grouped flags, user-defined values, merge behavior, output routing, and argument requirements.
