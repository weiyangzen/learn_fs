# sources/distributed-fs/ipfs-kubo/test/cli/bootstrap_auto_test.go

Purpose: tests CLI bootstrap command behavior when AutoConf uses the `auto` placeholder. It verifies adding, listing, removing, and mixed static-plus-auto bootstrap configurations.

Important test: `TestBootstrapCommandsWithAutoPlaceholder`. Subtests cover `bootstrap add default`, explicit `bootstrap add auto`, conversion of `default` to stored `auto`, failure when AutoConf is disabled, selective removal errors when `auto` is present, `rm --all` and `rm all`, and mixed specific peer plus `auto` configurations.

Control flow initializes test-profile nodes, sets `AutoConf.Enabled` and `Bootstrap`, runs `ipfs bootstrap` subcommands, and asserts stdout/stderr plus stored config values. State is persistent repo config for `Bootstrap` and AutoConf settings. Dependencies are harness command execution and bootstrap command validation code. Risks include exact user-facing error strings and semantics around mixing `auto` with specific peers. Test signal is strong for preserving placeholder semantics: `default` maps to `auto`, disabled AutoConf rejects auto insertion, individual removals are blocked when placeholder expansion would be ambiguous, and all-removal clears everything.
