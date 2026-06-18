# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/Kconfig

Purpose: this Kconfig file defines AMD Platform Management Framework support and optional PMF debug logging.

Important APIs, types, and functions: `AMD_PMF` is a tristate depending on ACPI, PCI, POWER_SUPPLY, AMD_NODE, TEE/AMDTEE, AMD_SFH_HID, and I/O memory, and selecting ACPI platform profile support. `AMD_PMF_DEBUG` gates additional debug logs for OEM-provided power settings.

Control flow: selecting `AMD_PMF` builds the composite PMF module. Selecting debug enables verbose dump helpers inside PMF sources.

State and persistence: only kernel config state exists.

Dependencies and integration points: dependencies reflect runtime use of ACPI APMF/APTS, root PCI/SMN, power-supply notifications, platform profile, AMD TEE policy engine, AMD SFH sensors, and MMIO.

Risks: the hard dependency on TEE/AMDTEE and AMD SFH means PMF availability is constrained even for systems that might only use static-slider features. Debug builds can expose extensive OEM configuration in logs.

Test signals: Kconfig visibility, module build as `amd_pmf`, successful compile with debug enabled/disabled, and dependency-driven symbol selection.
