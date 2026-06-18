# sources/distributed-fs/ceph-client/drivers/acpi/acpica/accommon.h

Purpose: umbrella include for ACPICA source files, centralizing the ordered internal include set needed by most implementation units.

Important contract: includes `<acpi/acconfig.h>`, `acmacros.h`, `aclocal.h`, `acobject.h`, `acstruct.h`, `acglobal.h`, `achware.h`, `acutils.h`, and optionally `acclib.h` when `ACPI_USE_SYSTEM_CLIBRARY` is not set.

Control flow: no runtime flow. Compile-time flow gives ACPICA `.c` files configuration constants, macros, internal types, operand objects, shared structures, globals, hardware prototypes, utility prototypes, and library shims in a consistent order.

State and persistence: owns no state but exposes declarations for subsystem-global state through included headers.

Dependencies and integration: depends on include ordering; earlier headers define macros/types consumed by later ones. This is the main integration include for ACPICA objects listed in the Makefile.

Risks: include-order changes can break most ACPICA files. Adding platform-heavy includes here increases compile impact. C-library selection must match kernel versus application build mode.

Test signals: full ACPI builds, minimal translation-unit header checks, and config matrix builds around `ACPI_USE_SYSTEM_CLIBRARY`.
