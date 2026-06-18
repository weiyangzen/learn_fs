# sources/distributed-fs/ceph-client/include/acpi/proc_cap_intel.h

Purpose: Defines Intel-specific processor capability bits used by OSPM to communicate supported power-management and performance-control mechanisms to firmware.

Important APIs, types, and functions: Exports bit macros such as `ACPI_PROC_CAP_P_FFH`, `ACPI_PROC_CAP_C_C1_HALT`, `ACPI_PROC_CAP_C_C1_FFH`, `ACPI_PROC_CAP_C_C2C3_FFH`, `ACPI_PROC_CAP_SMP_P_HWCOORD`, and `ACPI_PROC_CAP_COLLAB_PROC_PERF`, plus combined masks `ACPI_PROC_CAP_EST_CAPABILITY_SMP`, `ACPI_PROC_CAP_EST_CAPABILITY_SWSMP`, and `ACPI_PROC_CAP_C_CAPABILITY_SMP`.

Control flow: No runtime control flow. Processor/ACPI code ORs these bits into capability buffers passed through firmware methods such as `_PDC`.

State and persistence: Bits represent communicated capability state, not stored state in this header.

Dependencies and integration points: Integrates with ACPI processor P-state, C-state, T-state, FFH, SpeedStep/coordination, and CPPC capability negotiation on Intel processors.

Risks and test signals: Risks include advertising unsupported capabilities, failing to advertise hardware coordination, and firmware choosing bad control paths. Test `_PDC` payload generation, Intel CPU feature combinations, firmware behavior before/after capability updates, and suspend/resume processor power management.
