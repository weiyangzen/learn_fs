# sources/distributed-fs/ceph-client/include/acpi/platform/acgcc.h

Purpose: Supplies GCC-specific ACPICA compiler definitions, attributes, varargs support, native math flags, flexible-array workaround, and non-string annotations.

Important APIs, types, and functions: Defines `ACPI_INLINE`, `ACPI_GET_FUNCTION_NAME`, `ACPI_PRINTF_LIKE()`, `ACPI_UNUSED_VAR`, `COMPILER_VA_MACRO`, `ACPI_USE_NATIVE_MATH64`, fallback `__has_attribute`, `ACPI_FALLTHROUGH`, `ACPI_FLEX_ARRAY`, and `ACPI_NONSTRING` when supported.

Control flow: Compile-time feature detection selects attributes based on compiler support. Kernel builds include `linux/stdarg.h`; non-kernel builds include `stdarg.h`.

State and persistence: No runtime state; this changes compiler diagnostics, generated code, and structure declarations.

Dependencies and integration points: Used by all GCC ACPICA builds, including Linux kernel and ACPICA utilities. It supports packed ACPI table definitions and debug/log format checking.

Risks and test signals: Risks include attribute availability assumptions, flexible-array layout differences, and format warnings missed if `ACPI_PRINTF_LIKE` breaks. Test with multiple GCC/Clang versions, `-Wimplicit-fallthrough`, `-Wformat`, and structures using `ACPI_FLEX_ARRAY`.
