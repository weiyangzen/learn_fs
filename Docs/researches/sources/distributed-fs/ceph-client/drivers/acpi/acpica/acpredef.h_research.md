# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acpredef.h

## Purpose
Defines ACPICA's canonical table of ACPI predefined methods/objects and, for compiler/help builds, predefined resource descriptor and scope names. The table describes which reserved ACPI names may be evaluated, required method argument counts/types, allowed return bit types, and package return layouts.

## Important APIs, Types, And Data
`enum acpi_return_package_types` classifies return package shapes such as fixed elements, variable elements, package-count forms, revision-prefixed packages, UUID-pair packages, and custom validators. `METHOD_*ARGS`, `METHOD_RETURNS`, and `PACKAGE_INFO` pack method metadata into `union acpi_predefined_info` entries. When `ACPI_CREATE_PREDEFINED_TABLE` is defined, `acpi_gbl_predefined_methods[]` is emitted with entries for names such as `_ADR`, `_CRS`, `_DSD`, `_DSM`, `_PRT`, `_PRS`, `_Sx_`, `_STA`, `_UID`, and `_WAK`. With `ACPI_CREATE_RESOURCE_TABLE && ACPI_APPLICATION`, `acpi_gbl_resource_names[]` and `acpi_gbl_scope_names[]` expose ASL-only resource/scope names to iASL and acpi_help.

## Control Flow, State, And Persistence
The file is declarative but drives runtime validation elsewhere. Namespace/evaluation code looks up entries, extracts argument counts via `METHOD_GET_ARG_COUNT`, walks packed argument types with `METHOD_GET_NEXT_TYPE`, and validates returned objects/package elements against the following `PACKAGE_INFO` row. The table is static read-only process/kernel state; it persists for the lifetime of ACPICA and is not mutated.

## Dependencies And Integration Points
The table depends on ACPICA object type constants, return bitmaps, and `union acpi_predefined_info` from common ACPICA headers. It integrates with predefined-name validation/repair code, namespace evaluation, the iASL compiler, the ACPICA help utility, and resource descriptor field-name checking. Package formats encode firmware compatibility decisions, including tolerating common `_S0_` through `_S5_` package length deviations and warning about common `_PRT` source/source-index reversal.

## Risks And Test Signals
Risk is spec drift or packed metadata mistakes: one wrong type/count can reject valid firmware, accept invalid firmware, or break compiler diagnostics. Because package descriptors are adjacent table rows, insertion/removal errors can desynchronize method entries and package metadata. Test signals include ACPICA predefined-name tests, iASL diagnostics, kernel boot logs for predefined return warnings, `_DSM`/`_DSD` validation, resource-name help output, and systems with known nonconforming firmware.
