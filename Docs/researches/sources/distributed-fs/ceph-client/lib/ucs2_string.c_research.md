<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ucs2_string.c -->
# sources/distributed-fs/ceph-client/lib/ucs2_string.c

## Purpose
UCS-2 string helper implementation for length, bounded copy, comparison, UTF-8 size calculation, and UCS-2 to UTF-8 conversion.

## APIs, Types, and Functions
Exports `ucs2_strnlen()`, `ucs2_strlen()`, `ucs2_strsize()`, `ucs2_strscpy()`, `ucs2_strncmp()`, `ucs2_utf8size()`, and `ucs2_as_utf8()`. Operates on `ucs2_char_t` and emits UTF-8 bytes into `u8` buffers.

## Control Flow, State, and Persistence
Length helpers walk until NUL or maximum character count. `ucs2_strsize()` converts bounded character length to bytes. `ucs2_strscpy()` rejects zero size or count overflow, copies up to `count` UCS-2 code units, returns copied characters when a terminator is found, or NUL-terminates the last destination slot and returns `-E2BIG` on truncation. `ucs2_strncmp()` performs lexicographic comparison up to `len` or NUL. UTF-8 helpers count or emit one-, two-, or three-byte sequences for BMP code units and NUL-terminate only if space remains.

## Dependencies and Integration
Depends on `linux/ucs2_string.h` and module exports. It is used by firmware/EFI and other subsystems that expose UCS-2 strings.

## Risks and Test Signals
Risks include no surrogate-pair handling because UCS-2 is not full UTF-16, caller confusion between byte and character counts, partial UTF-8 output without NUL when buffer is full, and undefined overlap behavior for `ucs2_strscpy()`. Test signals include boundary counts, truncation return values, maximum count overflow warning, lexicographic NUL handling, UTF-8 exact sizing, and conversion buffers ending one or two bytes before a multibyte character.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ucs2_string.c -->
