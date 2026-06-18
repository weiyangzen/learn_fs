<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_nonprint.c -->
# sources/compression/xz/src/common/tuklib_mbstr_nonprint.c

Purpose: detects non-printable characters in strings and masks them with `?`.

Important APIs/types/functions: static `is_next_printable`, `has_nonprint`, public `tuklib_has_nonprint`, `tuklib_mask_nonprint_r`, and `tuklib_mask_nonprint`.

Control flow: with `mbrtowc`, decode one multibyte character at a time, treating incomplete/invalid/non-printable sequences as non-printable; without it, use `isprint` bytewise. Masking frees old caller memory, returns original string if printable, otherwise allocates a modified copy replacing bad characters.

State and persistence: `tuklib_mask_nonprint` uses a static allocation and is not thread-safe; reentrant form uses caller-owned `char **mem`. `errno` is preserved.

Dependencies and integration: used for safe display of untrusted filenames or messages.

Risks: allocation failure returns `"???"`, losing the original string. Windows UTF-16 replacement behavior is special-cased for non-BMP UTF-8.

Test signals: strings with control bytes, invalid UTF-8, incomplete trailing sequences, printable Unicode, and repeated reentrant calls.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_nonprint.c -->
