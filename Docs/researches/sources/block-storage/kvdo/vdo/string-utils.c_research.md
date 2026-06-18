# File Research: sources/block-storage/kvdo/vdo/string-utils.c

This file implements fixed-buffer and append formatting helpers. `uds_wrap_vsnprintf()` wraps `vsnprintf()`, supports `buf == NULL` for size probing, returns `UDS_UNEXPECTED_RESULT` on formatting failure, optionally reports required bytes, and can return/log a caller-provided overflow error.

`uds_fixed_sprintf()` is a varargs wrapper that rejects null output buffers. `uds_v_append_to_buffer()` and `uds_append_to_buffer()` append formatted text into an existing `[buffer, buf_end)` span, silently truncating and advancing to `buf_end` on overflow.
