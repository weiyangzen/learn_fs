# sources/compression/xz/tests/tests.h

Purpose: common header for XZ C test applications, wiring liblzma types into the `tuktest` assertion framework.

Important APIs/types: includes `sysdefs.h`, `tuklib_integer.h`, `lzma.h`, and `tuktest.h`. Defines `INVALID_LZMA_CHECK_ID`, `enum_strings_lzma_ret`, `assert_lzma_ret`, `enum_strings_lzma_check`, and `assert_lzma_check`.

Control flow: no runtime control flow beyond static initialization of enum-name arrays. Assertion macros delegate to `assert_enum_eq`.

State and persistence: header-local static constant arrays are compiled into each test translation unit; no persistent state.

Dependencies and integration: used by liblzma tests such as `test_vli.c`. Its enum string arrays must track the public liblzma enum ordering to keep diagnostics accurate.

Risks: if liblzma adds or reorders `lzma_ret` or `lzma_check` values, assertion diagnostics may become misleading or out of bounds. The invalid check value intentionally avoids the `LZMA_` prefix to prevent confusion with API values.

Test signals: improves failed assertion output by showing symbolic liblzma return and check names instead of raw integers.
