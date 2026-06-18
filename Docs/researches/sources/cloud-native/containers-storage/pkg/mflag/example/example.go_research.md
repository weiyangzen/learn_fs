# sources/cloud-native/containers-storage/pkg/mflag/example/example.go

Purpose: demonstrates the custom `mflag` command-line parser, including aliases, deprecated/hidden names, boolean flags, string/int flags, and help output.

Important APIs, types, and functions: package-level variables `i`, `str`, `b`, `b2`, `h`; `init` flag registrations; and `main` output logic.

Control flow: `init` registers several flags with names prefixed by `#` for hidden/deprecated behavior and calls `flag.Parse`. `main` prints defaults when help was requested, otherwise prints parsed values and remaining args.

State and persistence: no persistence. Program state is command-line flag values held in package variables and the global `mflag.CommandLine` set.

Dependencies and integration points: depends on `fmt` and `github.com/containers/storage/pkg/mflag`. It is an executable example for developers using `mflag`.

Risks and edge cases: parsing during `init` makes this example unsuitable as an importable helper. Some registered variables share the same destination pointer, intentionally demonstrating aliases but also showing how names can overwrite the same value.

Test signals: no tests; behavior is illustrative and complements `flag_test.go`.
