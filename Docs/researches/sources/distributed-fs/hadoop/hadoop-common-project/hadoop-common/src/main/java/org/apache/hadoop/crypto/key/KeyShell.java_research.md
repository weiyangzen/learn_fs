# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyShell.java

## Purpose
`KeyShell` is the `hadoop key` command-line utility for managing Hadoop key providers. It supports key creation, deletion, rolling, listing, metadata display, and cache invalidation.

## Important APIs and types
The class extends `CommandShell`. It parses commands in `init()`, prints detailed usage in `getCommandUsage()`, and defines nested command classes: `ListCommand`, `RollCommand`, `DeleteCommand`, `CreateCommand`, and `InvalidateCacheCommand`. The abstract nested `Command` resolves the active `KeyProvider` via `KeyProviderFactory`.

## Control flow
`init()` walks arguments, creates the appropriate subcommand, mutates `KeyProvider.Options` for `-size`, `-cipher`, `-description`, and `-attr`, sets provider configuration for `-provider`, toggles metadata listing, force deletion, and strict password behavior. Provider selection uses the first configured provider when user supplied `-provider`; otherwise it chooses the first non-transient provider. Commands validate provider and command-specific inputs, warn for transient providers, execute provider operations, call `flush()` for persistent mutations, and print user-facing success/failure messages. Delete prompts unless `-f`/`-force` disables interactivity.

## State and persistence
Shell state includes `interactive`, `strict`, and `userSuppliedProvider`, plus subcommand-local key names/options. Persistence is delegated to the selected provider and usually committed by `flush()`. `invalidateCache` does not call `flush()` because it changes cache state rather than key material.

## Dependencies and integration points
It depends on Hadoop `CommandShell`, `ToolRunner`, `KeyProviderFactory`, and provider implementations. It is the administrative entry point for JCEKS and KMS key operations.

## Risks
Argument parsing for `-attr` assumes an `=` is present; malformed input without it can throw rather than produce a friendly message. Default provider selection intentionally skips transient providers unless explicitly requested, which can surprise tests using `user:///`. Strict password mode only affects create validation, not all commands. CLI output is part of compatibility for scripts.

## Test signals
Tests should cover every command, provider selection with transient and non-transient providers, strict/no-password behavior, delete confirmation and force paths, metadata listing, duplicate/malformed attributes, error prettification, and `flush()` invocation on mutations.
