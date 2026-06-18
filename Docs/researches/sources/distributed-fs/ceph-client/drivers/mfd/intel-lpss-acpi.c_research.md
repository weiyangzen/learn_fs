# sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss-acpi.c

Purpose: ACPI transport wrapper for Intel LPSS multifunction devices. It matches LPSS ACPI IDs, attaches per-generation clock rates and software-node properties for SPI, I2C, and UART child drivers, and delegates common initialization to `intel_lpss_probe()`.

Important APIs/types/functions: `intel_lpss_acpi_ids`, `intel_lpss_acpi_probe()`, `intel_lpss_acpi_remove()`, `platform_driver`, and `struct intel_lpss_platform_info`. Software nodes provide properties such as `intel,spi-pxa2xx-type`, I2C timing values, `reg-io-width`, `reg-shift`, and `snps,uart-16550-compatible`.

Control flow: probe obtains match data with `device_get_match_data()`, duplicates immutable platform info, fills MEM and IRQ resources from the ACPI platform device, calls the LPSS core, then marks and enables runtime PM. Remove calls the shared LPSS cleanup and disables runtime PM.

State and persistence: no persistent storage. Runtime state is devres-managed and owned by the LPSS core after probe. Runtime PM state is configured on the platform device.

Dependencies and integration: depends on ACPI/platform bus matching, Linux property/software-node APIs, `pxa2xx` SPI type definitions, and the shared `intel-lpss` core exported in namespace `INTEL_LPSS`.

Risks: ACPI ID table data must match the actual controller type and timing requirements. Bad firmware resources or missing IRQs surface in the shared core. Timing property mistakes can break I2C/SPI/UART child probing or board-level electrical timing.

Test signals: useful checks are ACPI modalias binding, successful child creation under `intel-lpss`, runtime PM suspend/resume, and boot logs on SPT/CNL/BXT/APL systems with I2C, SPI, and UART LPSS instances.
