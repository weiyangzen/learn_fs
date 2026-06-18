# File Research: sources/block-storage/stratisd/src/jsonrpc/client/key.rs

## Purpose

Implements client-side key management commands for setting, unsetting, and listing kernel key descriptions.

## Main Types and Behavior

- `key_set` either opens a provided keyfile or prompts for a verified passphrase.
- Prompted passphrases are written into a pipe and the read file descriptor is sent over JSON-RPC.
- The return value is `Option<bool>`: `None` means no effect, `Some(false)` means newly created, and `Some(true)` means changed existing value.
- `key_unset` uses standard changed-result handling.
- `key_list` prints key descriptions in a table.

## Integration Points

Uses `KeyDescription`, password prompting from `client/utils.rs`, FD passing from request macros, and server-side `key_set`.

## Notable Semantics

For interactive `key_set`, empty password input is rejected before any request is sent.
