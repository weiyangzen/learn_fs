# sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss-pci.c

Purpose: PCI transport wrapper for Intel LPSS controllers across many Intel SoC generations. It maps PCI IDs to LPSS platform descriptions and invokes the common LPSS MFD core.

Important APIs/types/functions: `intel_lpss_pci_probe()`, `intel_lpss_pci_remove()`, `intel_lpss_pci_ids`, `quirk_ids`, and per-family `intel_lpss_platform_info` records. Quirks include `QUIRK_IGNORE_RESOURCE_CONFLICTS` for specific Surface Go I2C resource conflicts and `QUIRK_CLOCK_DIVIDER_UNITY` for a Dell XPS clock-divider firmware bug.

Control flow: probe enables the PCI function with managed PCI helpers, allocates one IRQ vector, copies the matched platform info, fills BAR0 and IRQ vector, applies subsystem quirks, disables D3cold delay, enables bus mastering/MWI, calls `intel_lpss_probe()`, and allows runtime PM. Remove forbids runtime PM, synchronously resumes, and calls `intel_lpss_remove()`.

State and persistence: per-device LPSS state is allocated by the core. This file maintains only static match/property data. PCI power policy is adjusted through runtime PM and `d3cold_delay`.

Dependencies and integration: integrates PCI enumeration with the LPSS core, software-node properties, clock connector names, DesignWare I2C/UART, PXA2xx SPI, and idma64 child support through the core.

Risks: the huge PCI ID table is easy to regress when adding new platforms; wrong info records affect clock rate, SPI type, I2C timings, or UART clock lookup. Quirk matching is subsystem-specific, so overbroad IDs could hide real resource conflicts or force wrong dividers.

Test signals: PCI modalias binding, successful MFD child registration, runtime PM transitions, I2C/SPI/UART functional tests on affected generations, and targeted tests for Surface Go and Dell XPS quirk paths.
