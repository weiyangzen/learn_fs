# File Research: sources/block-storage/kvdo/vdo/string-utils.h

This header declares string helper APIs and an inline `uds_bool_to_string()` returning `"true"` or `"false"`. It includes kernel string/kernel headers and local compiler/type definitions.

The declared helpers provide:
- fixed-size formatting with explicit overflow error reporting,
- `vsnprintf()` wrapping with size-needed output,
- append-to-buffer helpers for varargs and `va_list`.

Functions are annotated with `__printf` for format checking and `__must_check` where callers should handle errors.
