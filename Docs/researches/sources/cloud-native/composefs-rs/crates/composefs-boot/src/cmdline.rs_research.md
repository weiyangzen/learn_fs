# sources/cloud-native/composefs-rs/crates/composefs-boot/src/cmdline.rs

## Purpose
This module provides kernel command-line parsing and formatting helpers for composefs boot support. Its main responsibility is locating and constructing `composefs=` arguments, including the optional insecure marker that means fs-verity validation can be skipped.

## Important APIs, types, and functions
`split_cmdline` is a crate-private iterator helper that splits on ASCII whitespace while preserving whitespace inside double quotes. It intentionally matches the kernel's simple quoting model and does not implement backslash escaping.

`get_cmdline_value(cmdline, prefix)` scans split command-line items and returns the suffix of the first item that starts with a requested prefix. `get_cmdline_composefs<ObjectID>` finds `composefs=`, parses the hash using the `FsVerityHashValue` implementation, and returns `(ObjectID, insecure)`. A leading `?` on the value sets the insecure flag and is stripped before hash parsing. `make_cmdline_composefs(id, insecure)` emits either `composefs=<id>` or `composefs=?<id>`.

## Control flow
Parsing is linear. The splitter toggles an `in_quotes` flag when encountering `"`, and a character becomes a delimiter only if it is ASCII whitespace outside quotes. `get_cmdline_composefs` first requires a `composefs=` item, then chooses the secure or insecure parse branch based on `strip_prefix('?')`. Parse errors are annotated with expected hex length and algorithm name.

## State and persistence behavior
There is no persistent state. All functions operate on borrowed strings and return borrowed slices or owned formatted strings. The only externally visible state encoded by this module is the `?` prefix in the command-line value.

## Dependencies and integration points
It depends on `anyhow` for contextual errors and on `composefs::fsverity::FsVerityHashValue` for algorithm-specific hex parsing. `bootloader.rs` uses `split_cmdline` and `make_cmdline_composefs` to update BLS options. `write_boot.rs` uses `get_cmdline_composefs` to verify a UKI's embedded `.cmdline` points at the expected composefs image hash before writing it to the boot partition.

## Risks
The quoting behavior deliberately does not support escaping. An unmatched quote causes the rest of the string to be treated as quoted, which may hide later whitespace splits. `get_cmdline_value` returns the first matching prefix and does not detect duplicate `composefs=` values. It also does not dequote the returned value, which is acceptable for current composefs hash use but would matter if reused for more general parameters.

## Test signals
This file has no local tests. It is indirectly tested through `bootloader.rs` command-line adjustment tests and `write_boot.rs` UKI validation paths. Dedicated tests for quoted command lines, duplicate parameters, insecure parsing, invalid hash lengths, and unmatched quotes would strengthen coverage.
