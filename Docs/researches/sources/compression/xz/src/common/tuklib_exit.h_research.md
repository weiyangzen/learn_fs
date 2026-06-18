<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_exit.h -->
# sources/compression/xz/src/common/tuklib_exit.h

Purpose: declaration for `tuklib_exit`.

Important APIs/types/functions: prefixed `tuklib_exit` symbol and `tuklib_attr_noreturn` declaration.

Control flow: header-only.

State and persistence: none.

Dependencies and integration: documents dependency on tuklib progname/gettext modules.

Risks: callers should not expect return; incorrect status arguments can hide write errors.

Test signals: compile with compilers honoring noreturn and check no fallthrough warnings at call sites.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_exit.h -->
