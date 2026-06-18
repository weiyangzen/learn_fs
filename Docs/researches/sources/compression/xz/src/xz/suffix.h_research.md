# sources/compression/xz/src/xz/suffix.h

Purpose: internal header for `xz` filename suffix policy.

Important APIs: declares `suffix_get_dest_name(const char *)`, `suffix_set(const char *)`, and `suffix_is_set(void)`. `suffix_get_dest_name()` returns a newly allocated destination filename or `NULL` after printing a warning; `suffix_set()` copies the supplied suffix and may terminate via `message_fatal()` if the suffix is invalid.

Control flow and integration: callers configure optional suffix policy once through `suffix_set()`, then ask for a destination path per input file. The result depends on global command mode and format in `suffix.c`; the header deliberately does not expose those globals.

State and persistence: hides the `custom_suffix` allocation behind the three functions. No persistent state exists outside process memory.

Dependencies: consumers need standard `bool` and command-private memory/message conventions. The allocation contract means callers must free successful return values.

Risks: the API depends on side-effectful global options rather than explicit mode arguments, so call order matters. `suffix_set()` being fatal on invalid data is appropriate for option parsing but unsuitable for non-fatal validation use.

Test signals: suffix CLI tests should verify custom suffix replacement, invalid empty/path suffixes, compression suffix collision warnings, and decompression unknown-suffix skipping.
