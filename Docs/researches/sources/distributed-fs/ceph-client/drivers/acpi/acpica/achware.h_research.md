# sources/distributed-fs/ceph-client/drivers/acpi/acpica/achware.h

Purpose: declares ACPICA hardware-facing interfaces for ACPI mode switching, register access, sleep/wake, port validation, GPE register manipulation, and PCI ID derivation.

Important APIs/functions: defines `_SST` indicator values. Declares `acpi_hw_set_mode`, `acpi_hw_get_mode`, register validate/read/write helpers, bit-register lookup/read/write, PM1 control write, status clear, legacy and extended sleep/wake functions, sleep-method execution, validated port I/O, GPE read/write/bit/set/clear/status helpers, runtime GPE enable helpers, and `acpi_hw_derive_pci_id` with an `AE_SUPPORT` fallback when PCI is not configured.

Control flow: higher layers call these functions to enable ACPI mode, manipulate PM registers, enter/leave sleep states, manage GPE enable/status registers, and service PCI config operation regions.

State and persistence: no state is owned here, but functions operate on global ACPI hardware state and on `acpi_generic_address`, GPE structures, and PCI IDs.

Dependencies and integration: bridges event, sleep, region, and interpreter code to platform hardware and OS port/MMIO access. Included broadly via `accommon.h`.

Risks: wrong GAS widths/addresses, preserved/write-only bit handling, reduced-hardware configs, and sleep sequencing mistakes can break firmware interaction. PCI-disabled fallback must be handled by callers.

Test signals: ACPI mode transitions, PM register validation, fixed-event clearing, GPE enable/disable/status, S-state suspend/resume on legacy and extended platforms, invalid I/O block rejection, reduced-hardware builds, and PCI-disabled builds.
