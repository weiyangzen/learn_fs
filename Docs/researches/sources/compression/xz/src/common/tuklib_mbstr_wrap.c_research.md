<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_wrap.c -->
# sources/compression/xz/src/common/tuklib_mbstr_wrap.c

Purpose: word-wraps multibyte strings to a `FILE` stream, with support for indentation modes and selected control-character markup.

Important APIs/types/functions: `tuklib_wraps`, `tuklib_wrapf`, `struct tuklib_wrap_opt`, `tuklib_mbstr_width_mem`, `vasprintf`/`vsnprintf`, and `TUKLIB_WRAP_*` status flags.

Control flow: validate margins, track current/pending indentation and newline state, scan to next break opportunity, measure width, wrap when needed, suppress trailing spaces, handle `\t`, `\b`, `\v`, `\r`, `\n`, and implicit final newline. `wrapf` formats into a temporary buffer before wrapping.

State and persistence: local state only; writes to caller-provided stream. `wrapf` allocates a temporary string and frees it.

Dependencies and integration: used for translated help/messages where manual wrapping is error-prone.

Risks: writes one byte at a time, so stream buffering matters. Invalid multibyte input aborts wrapping. Fallback `vsnprintf` path truncates at 128 KiB.

Test signals: wrap fixtures for long words, multiple spaces, zero-width tabs, unbreakable blocks, alternative indentation, invalid UTF-8, and simulated I/O errors.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_wrap.c -->
