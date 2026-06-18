# File Research: sources/block-storage/util-linux/libmount/src/fuzz.c

This is a libFuzzer entry point for mount table parsing, focused on mountinfo-like input.

Key behavior:

- `LLVMFuzzerTestOneInput()` rejects empty inputs and inputs larger than 128 KiB.
- It allocates a `libmnt_table`, opens the fuzzer bytes through `fmemopen()` in read mode, enables comments, and calls `mnt_table_parse_stream(tb, f, "mountinfo")`.
- It ignores parser return values, then releases the table and stream.

Dependencies and interactions:

- Exercises table allocation, comment parsing, and stream parsing paths.
- Uses `err_oom()` and `err()` for unrecoverable local harness setup failures.

Risk notes:

- The harness is intentionally narrow: it does not fuzz mount/umount execution or hook behavior, only parser handling of bounded input.
