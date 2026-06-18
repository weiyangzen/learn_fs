# sources/cloud-native/ostree/src/ostree/ot-builtin-remote.c

## Purpose
Implements the `ostree remote` command dispatcher. It selects a remote subcommand, adjusts arguments, prints help for missing or unknown subcommands, and invokes the corresponding implementation from `ot-remote-builtins.h`.

## Important APIs, Types, And Functions
`remote_subcommands[]` declares subcommands such as `add`, `delete`, `show-url`, `list`, GPG key operations, cookie operations when HTTP support exists, `refs`, and `summary`. `remote_option_context_new_with_commands()` builds the help summary. `ostree_builtin_remote()` parses out the first non-option command and dispatches through `OstreeCommand`.

## Control Flow
The dispatcher scans `argv` from index 1, removing the first non-option argument as the subcommand name while preserving other options and stopping at `--`. It then searches the static command table. If not found, it builds a context, lets shared option parsing handle global options such as version/help, emits a missing or unknown subcommand error, prints help, and returns false. For a valid subcommand it updates `g_get_prgname()` to include the subcommand, constructs a sub-invocation, and calls the subcommand function with the adjusted argc/argv.

## State And Persistence
The dispatcher itself is stateless except for mutating the process program name and argv layout. Persistent effects depend on the selected subcommand, such as remote config, GPG keys, cookies, or remote queries.

## Dependencies And Integration Points
It depends on `ot-main.h` command invocation conventions through `ot-builtins.h`, remote builtin declarations, compile-time GPG and HTTP feature gates, and shared option parsing. This file is the public CLI routing layer for remote management.

## Risks And Edge Cases
Argument rewriting is in-place, so future options that look like commands must preserve the first non-option rule. `--` stops command discovery, which can produce no subcommand. Feature-gated commands disappear from help and dispatch when compiled without GPGME or HTTP support. Help/error behavior relies on shared option parsing not consuming normal remote subcommands.

## Test Signals
Tests should verify dispatch to each compiled subcommand, missing and unknown subcommand help, global help/version behavior, options before and after the subcommand, `--` behavior, and feature-gated command visibility.
