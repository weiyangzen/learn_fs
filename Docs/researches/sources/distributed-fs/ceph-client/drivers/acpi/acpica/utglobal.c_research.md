# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utglobal.c

Purpose: `utglobal.c` defines ACPICA global data tables and exported globals that are shared across the subsystem, including sleep/power method names, predefined namespace names, fixed hardware register metadata, fixed event metadata, PLD decode strings, and public debug/table counters.

Important APIs/types/functions: Data includes `acpi_gbl_sleep_state_names`, lowest/highest D-state method names, lower/upper hex digit strings, `acpi_gbl_pre_defined_names`, `acpi_gbl_bit_register_info`, `acpi_gbl_fixed_event_info`, and optional PLD string lists. It exports `acpi_gbl_FADT`, `acpi_dbg_level`, `acpi_dbg_layer`, `acpi_gpe_count`, and `acpi_current_gpe_count`.

Control flow: This file has no active control flow beyond compile-time conditional inclusion for reduced hardware, disassembler, and compiler builds. Consumers index these arrays by ACPI enum values.

State and persistence behavior: The arrays are persistent global constants or global metadata. Exported counters/debug globals are mutable elsewhere but defined here under `DEFINE_ACPI_GLOBALS`.

Dependencies and integration points: It is included by initialization, namespace setup, hardware/event code, debug code, table code, compiler/disassembler paths, and Linux-exported ACPICA interfaces. The predefined name table seeds namespace root children such as `_SB_`, `_TZ_`, `_REV`, `_OS_`, `_GL_`, and `_OSI`.

Risks and test signals: Risks include enum/table ordering mismatch, reduced-hardware build differences, incorrect predefined namespace type/value, and fixed-event/register metadata drift with ACPI specs. Tests should assert array sizes against enum counts, predefined namespace creation, `_REV` compatibility value, fixed event enable/status bit mapping, and exported debug globals in module builds.
