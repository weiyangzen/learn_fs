# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/Kconfig

Purpose: this Kconfig option enables the AMD Heterogeneous Core Hardware Feedback Interface driver.

Important APIs, types, and functions: the sole symbol is `AMD_HFI`, a bool depending on ACPI, AMD CPU support, and `SCHED_MC_PRIO`.

Control flow: when selected, the hfi subdirectory Makefile links `hfi.o` into the kernel. The bool nature means it is built-in rather than a loadable module.

State and persistence: configuration persists in `.config`; no runtime state exists in this file.

Dependencies and integration points: the dependency on `SCHED_MC_PRIO` reflects the driver's use of scheduler ITMT/core-priority hooks. ACPI is required for the platform device and PCCT data.

Risks: missing scheduler or CPU feature dependencies would create compile-time or runtime failures. Since the driver is bool-only, unload/reload style testing is not available.

Test signals: config visibility only on matching dependency sets, successful kernel link, and boot-time HFI initialization on systems with matching ACPI and CPU features.
