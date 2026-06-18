<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_wrap.h -->
# sources/compression/xz/src/common/tuklib_mbstr_wrap.h

Purpose: public API and detailed contract for multibyte word wrapping.

Important APIs/types/functions: `TUKLIB_WRAP_WARN_OVERLONG`, error flags, `struct tuklib_wrap_opt`, `tuklib_wraps`, and printf-annotated `tuklib_wrapf`.

Control flow: header-only; documents special markup semantics for `\t`, `\b`, `\v`, `\r`, and `\n`, and translator guidance via `W_`.

State and persistence: no state; output state is in the target `FILE`.

Dependencies and integration: included by CLI message/help code and tied to gettext extraction comments.

Risks: only `\n` and sometimes `\t` should appear in translatable strings; other control markup can confuse translators/tools. Right-to-left and no-space languages may need manual care.

Test signals: compile-time format checking for `wrapf`; golden output tests for documented control characters and status flags.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_wrap.h -->
