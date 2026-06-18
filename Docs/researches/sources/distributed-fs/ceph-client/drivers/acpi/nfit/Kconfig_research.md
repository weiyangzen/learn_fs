# sources/distributed-fs/ceph-client/drivers/acpi/nfit/Kconfig

Purpose: this Kconfig file declares build options for the ACPI NFIT driver and its security debug mode. NFIT support discovers ACPI 6 NVDIMM Firmware Interface Tables and registers libnvdimm topology and platform/DIMM DSM access.

Important APIs, types, and functions: `config ACPI_NFIT` is a tristate option named "ACPI NVDIMM Firmware Interface Table (NFIT)" and selects `LIBNVDIMM`. It depends on `PHYS_ADDR_T_64BIT`, `BLK_DEV`, and `ARCH_HAS_PMEM_API`. `config NFIT_SECURITY_DEBUG` is a boolean gated by `ACPI_NFIT`.

Control flow: there is no runtime control flow; the file controls compilation. Selecting `ACPI_NFIT=m` builds a module named `nfit`. Enabling security debug changes debug visibility for NVDIMM security command payloads in the driver implementation.

State and persistence: Kconfig choices persist in kernel configuration and determine whether NFIT code is built in, modular, or absent.

Dependencies and integration: integrates ACPI NFIT with persistent memory architecture support, block device infrastructure, and libnvdimm. Security debug is intentionally opt-in because command payloads may contain sensitive clear-text material.

Risks: enabling security debug on non-development systems can expose sensitive material in logs. Missing dependency selections prevent NFIT from appearing even on ACPI systems with NVDIMMs.

Test signals: verify menu visibility under supported architectures, built-in and module builds, dependency exclusion when persistent-memory APIs are unavailable, and that `NFIT_SECURITY_DEBUG` only appears with `ACPI_NFIT`.
