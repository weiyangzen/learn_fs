# sources/cloud-native/cri-o/internal/criocli/criocli_test.go

Purpose: tests selected CLI helper behavior: string-slice parsing, zsh completion quoting, and specific global flag merges.

Important APIs/types/functions: `StringSliceTrySplit`, test-only `ZshQuoteCmd`, `GetFlagsAndMetadata`, `GetConfigFromContext`, and `GetAndMergeConfigFromContext`.

Control flow: first suite constructs a `flag.FlagSet` with a `cli.StringSlice`, then verifies dense comma-separated, whitespace-trimmed comma-separated, and separately repeated values all normalize to three entries, and returned slices are copies. Completion tests use a table to verify single-quote default, double-quote fallback for usage containing apostrophes, and dollar escaping only in double-quoted output. Flag tests create an app/context, apply bool flags with `HasBeenSet`, and verify config merge changes for `hostnetwork-disable-selinux` and `disable-hostport-mapping`.

State and persistence behavior: all state is in-memory cli flag/app state.

Dependencies/integration points: Ginkgo/Gomega, urfave/cli, Go `flag`, and CRI-O config metadata.

Risks: coverage is narrow compared to the size of `criocli.go`; most flags, config file loading, runtime parsing, and command actions are untested.

Test signals: good regression coverage for helper parsing and two recently important bool flags.
