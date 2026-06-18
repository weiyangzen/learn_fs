# File Research: sources/block-storage/stratisd/src/jsonrpc/client/utils.rs

## Purpose

Contains JSON-RPC client request macros, table formatting macros, byte-size formatting, and passphrase prompting utilities.

## Main Types and Behavior

- `do_request!` connects to the RPC socket, builds `StratisParams`, optionally attaches an FD, checks response variant matching, and returns the typed payload.
- `do_request_standard!` expects `(changed, rc, rs)` tuples and converts nonzero return codes or unchanged results into `StratisError`.
- `left_align!`, `right_align!`, `align!`, and `print_table!` format aligned terminal tables.
- `to_suffix_repr` formats byte counts using binary suffixes down to two decimal places.
- `get_pass` disables terminal echo for TTY input, restores terminal settings, trims trailing newline, and returns `None` for empty input.
- `prompt_password` optionally verifies two passphrase entries.

## Integration Points

All client pool/filesystem/key wrappers depend on these macros and helpers.

## Notable Semantics

The table macro enforces equal-length columns. `to_suffix_repr` intentionally truncates/rounds down two decimal places to avoid misleading unit promotion near boundaries.
