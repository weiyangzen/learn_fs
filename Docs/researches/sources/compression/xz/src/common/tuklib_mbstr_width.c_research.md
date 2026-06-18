<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_width.c -->
# sources/compression/xz/src/common/tuklib_mbstr_width.c

Purpose: calculates terminal display width for null-terminated or length-delimited multibyte strings.

Important APIs/types/functions: `tuklib_mbstr_width`, `tuklib_mbstr_width_mem`, `mbrtowc`, `wcwidth`, and `mbsinit`.

Control flow: null-terminated wrapper records byte length with `strlen`; length-based function either returns byte length in single-byte fallback mode or decodes each multibyte character, sums `wcwidth`, and validates shift state.

State and persistence: stateless.

Dependencies and integration: used by field-width and wrapping helpers for localized CLI output.

Risks: returns `(size_t)-1` for invalid sequences or negative `wcwidth`. Without `wcwidth`, each multibyte character is assumed one column, which is wrong for CJK but better than byte count.

Test signals: UTF-8 width fixtures under locales with and without `wcwidth`; invalid/partial sequences should fail.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_width.c -->
