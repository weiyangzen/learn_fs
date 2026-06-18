# sources/cloud-native/containers-storage/pkg/mflag/flag_test.go

Purpose: tests the custom `mflag` package behavior across value types, parsing modes, errors, usage, and merging.

Important APIs, types, and functions: `ResetForTesting`, `TestEverything`, `TestGet`, `testParse`, `TestParse`, `TestFlagSetParse`, `TestUserDefined`, `TestUserDefinedBool`, `TestSetOutput`, `TestChangingArgs`, `TestHelp`, `TestFlagCounts`, `TestSortFlags`, `TestMergeFlags`, and helper custom value types.

Control flow: tests reset the global command line, define flags, parse synthetic arg lists, inspect resulting pointer values and set state, and validate visitor ordering. User-defined tests verify repeated custom values and bool-like custom values. Help and output tests check special parse paths.

State and persistence: no persistence. Tests mutate global `CommandLine`, `os.Args`, and in-memory `FlagSet` maps.

Dependencies and integration points: depends on `bytes`, `fmt`, `os`, `sort`, `strings`, `testing`, `time`, and `testify`. It protects command-line compatibility for consumers using `mflag`.

Risks and edge cases: tests intentionally manipulate globals, so isolation depends on `ResetForTesting` and deferred restoration. Process-exit paths in `ParseFlags` are not directly exercised.

Test signals: broad coverage for parsing syntax, quoting, typed getters, grouped short flags, deprecation counting, sorting idempotence, merge forwarding, and custom value semantics.
