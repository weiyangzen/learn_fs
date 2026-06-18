# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acmacros.h

Purpose: provides low-level C macros used across ACPICA for unaligned/endian data movement, integer formatting, power-of-two math, alignment/rounding, bit search, masks, register bit insertion, descriptor inspection, AML opcode table construction, error reporting, hardware optionality, UUID initialization, octal checks, and ASL converter hooks.

Important macro families: `ACPI_GET/SET*`, `ACPI_MOVE_*`, `ACPI_FORMAT_UINT64`, power-of-two division/multiply/modulo helpers, rounding and alignment helpers, `ACPI_FIND_FIRST/LAST_BIT_*`, power-of-two rounding, mask-above/below helpers, register bit helpers, pathname character tests, descriptor pointer/type accessors, `ACPI_OP`, `ARGP/ARGI_LIST*`, error/predefined warning macros, `ACPI_HW_OPTIONAL_FUNCTION`, `ACPI_INIT_UUID`, and `ASL_CV_*`.

Control flow: compile-time branches select endian mode, unaligned-transfer strategy, native bit finder usage, error-message availability, reduced-hardware callback presence, and compiler-comment conversion hooks.

State and persistence: no owned state, but many macros directly read/write caller memory and descriptor fields.

Dependencies and integration: underpins opcode table metadata, AML argument encoding, register manipulation, resource parsing, table access, descriptor inspection, and debug/error reporting.

Risks: macro arguments can have side effects; architecture alignment/endian settings must be correct; full-width shifts need guarded mask macros; descriptor macros rely on common field layout shared by namespace nodes and operand objects.

Test signals: big-endian and strict-alignment builds, UBSAN/ASAN where usable, opcode table checks, register bit manipulation tests, error-message-disabled builds, reduced-hardware builds, and ASL compiler builds.
