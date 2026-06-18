<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_common.h -->
# sources/compression/xz/src/common/tuklib_common.h

Purpose: common base header for tuklib modules.

Important APIs/types/functions: `TUKLIB_SYMBOL_PREFIX`, `TUKLIB_SYMBOL`, concatenation macros, C++ declaration guards, `TUKLIB_GNUC_REQ`, `tuklib_attr_format_printf`, `tuklib_attr_noreturn`, and `TUKLIB_DOSLIKE`.

Control flow: include `tuklib_config.h`, define symbol-prefixing and attributes based on compiler/language/platform macros.

State and persistence: compile-time only.

Dependencies and integration: every tuklib module includes it; allows symbol prefixing when tuklib is embedded in libraries.

Risks: prefix settings must be consistent across declarations and definitions. Attribute selection affects diagnostics and ABI annotations.

Test signals: compile tuklib modules with custom `TUKLIB_SYMBOL_PREFIX`, C++, C23, GCC/Clang/MSVC, and DOS-like targets.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_common.h -->
