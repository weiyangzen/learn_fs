<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr.h -->
# sources/compression/xz/src/common/tuklib_mbstr.h

Purpose: public declarations for multibyte string display-width helpers.

Important APIs/types/functions: `tuklib_mbstr_width`, `tuklib_mbstr_width_mem`, and `tuklib_mbstr_fw`.

Control flow: declaration-only; comments define behavior for invalid, partial, or non-printable multibyte input and printf field-width alignment.

State and persistence: none.

Dependencies and integration: used by terminal/help/list formatting where byte length differs from column width.

Risks: callers must handle `(size_t)-1` and `-1` error returns. `tuklib_mbstr_fw` has undefined behavior for null strings, nonpositive minimum columns, or field widths over `INT_MAX`.

Test signals: width tests for ASCII, UTF-8, invalid sequences, CJK, combining characters, and fallback single-byte builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr.h -->
