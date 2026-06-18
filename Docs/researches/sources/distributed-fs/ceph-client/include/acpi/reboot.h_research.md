# sources/distributed-fs/ceph-client/include/acpi/reboot.h

Purpose: Declares the ACPI reboot entry point with a no-op fallback for non-ACPI builds.

Important APIs, types, and functions: Exports `acpi_reboot()` when `CONFIG_ACPI` is enabled; otherwise defines an inline empty function.

Control flow: Reboot paths can call `acpi_reboot()` unconditionally and either perform ACPI reset register logic or do nothing if ACPI is unavailable.

State and persistence: No state in the header. Runtime reset state is firmware/hardware controlled.

Dependencies and integration points: Integrates with architecture machine restart paths and ACPI FADT reset-register handling.

Risks and test signals: Risks are callers assuming reboot occurred after the no-op stub, and platform reset register regressions. Test ACPI/non-ACPI builds and reboot on systems using ACPI reset versus fallback restart mechanisms.
