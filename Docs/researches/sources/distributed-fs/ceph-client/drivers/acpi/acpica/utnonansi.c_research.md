## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utnonansi.c

Purpose: `utnonansi.c` supplies small non-ANSI or portability string helpers used by ACPICA tools and debug paths, including case conversion, case-insensitive compare, and bounded string copy/append wrappers.

Important APIs and functions: `acpi_ut_strlwr` and `acpi_ut_strupr` mutate an input string in place after a null check. `acpi_ut_stricmp` compares two strings case-insensitively and returns the usual signed difference. Under debugger/application/debug-output builds, `acpi_ut_safe_strcpy`, `acpi_ut_safe_strcat`, `acpi_ut_safe_strncat`, and `acpi_ut_safe_strncpy` provide size-aware wrappers; `acpi_ut_safe_strncpy` delegates to Linux `strscpy_pad`.

Control flow: conversion helpers walk until the terminating null byte and call `tolower`/`toupper` for each byte. The safe helpers precompute source/destination lengths and return `TRUE` if the requested operation would not fit; otherwise they call the normal C library operation.

State and dependencies: no persistent state. The file depends on C character/string routines and ACPICA build-condition macros.

Integration points: memory tracking copies module names with the safe copy helper; debugger and application command paths use the bounded routines to protect fixed command buffers. The case helpers support ACPICA parser and utility paths that need platform-independent behavior.

Risks: `acpi_ut_stricmp` does not accept null pointers. The safe append functions use the classic `>= dest_size` fit test and assume `dest` is already null-terminated. `strncat` may scan beyond the intended transfer length if callers provide inconsistent strings, so callers must pass valid C strings.

Test signals: empty strings, mixed-case equality, prefix ordering, exact destination-size boundaries, `max_transfer_length` shorter than source, and null inputs for only the helpers that explicitly allow null are useful.
