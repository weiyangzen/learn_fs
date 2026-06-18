<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_fw.c -->
# sources/compression/xz/src/common/tuklib_mbstr_fw.c

Purpose: computes a printf field width that aligns a multibyte string to a minimum terminal column count.

Important APIs/types/functions: `tuklib_mbstr_fw(const char *str, int columns_min)` calls `tuklib_mbstr_width`.

Control flow: get display width and byte length; return `-1` on width failure, `0` if string already exceeds minimum columns, otherwise add the column shortfall to byte length and return it as field width.

State and persistence: stateless.

Dependencies and integration: supports table formatting in CLI output.

Risks: relies on caller meeting header preconditions; cast to `int` assumes result fits.

Test signals: align ASCII and multibyte names in formatted tables; invalid sequence should return `-1`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_fw.c -->
