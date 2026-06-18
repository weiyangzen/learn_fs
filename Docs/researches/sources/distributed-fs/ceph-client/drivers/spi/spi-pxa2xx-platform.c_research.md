# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-platform.c

## Purpose
`spi-pxa2xx-platform.c` is platform/ACPI/OF glue for the shared PXA2xx SSP SPI core. It discovers or requests an `ssp_device`, initializes platform data from firmware properties, configures optional Intel LPSS private DMA matching, enables runtime PM, and delegates controller registration to `pxa2xx_spi_probe()`.

## Important APIs, Types, And Functions
- `pxa2xx_spi_idma_filter()` matches iDMA channels by parent device pointer.
- `pxa2xx_spi_init_ssp()` maps MMIO resources, gets the SSP clock and IRQ, sets SSP type and ACPI UID-derived port ID.
- `pxa2xx_spi_ssp_request()` requests an already-registered PXA SSP device and installs managed release.
- `pxa2xx_spi_init_pdata()` builds `struct pxa2xx_spi_controller` from platform data, match data, or firmware property `intel,spi-pxa2xx-type`.
- `pxa2xx_spi_platform_probe()` initializes runtime PM and calls `pxa2xx_spi_probe()`.
- `pxa2xx_spi_platform_remove()` resumes the device, calls core remove, and disables runtime PM.
- ACPI and OF match tables enumerate Intel ACPI IDs and `marvell,mmp2-ssp`.

## Control Flow
Probe first uses explicit platform data if present; otherwise it builds it. `pxa2xx_spi_init_pdata()` prefers an existing SSP registry entry from `pxa_ssp_request()`, then match data, then the Intel type property. It sets `num_chipselect`, target/slave mode, DMA defaults, and initializes an embedded `ssp_device` if no external SSP object exists. The platform probe enables runtime PM with a 50 ms autosuspend delay and calls the common core.

## State And Persistence Behavior
The platform data and embedded `ssp_device` are managed allocations tied to the platform device. Runtime PM state is enabled at probe and disabled on remove. No persistent storage is used. If an external SSP device is requested, a managed release action returns it to the PXA SSP subsystem.

## Dependencies And Integration Points
The file integrates ACPI, OF match data, generic device properties, platform resources, clock lookup, `pxa_ssp_request()/pxa_ssp_free()`, runtime PM, optional iDMA filtering, and the exported PXA2xx SPI core API. It imports the `"SPI_PXA2xx"` namespace and has a soft dependency on `dw_dmac`.

## Risks
- Firmware must provide either an existing SSP, match data, or a valid `intel,spi-pxa2xx-type`; otherwise probe fails as missing platform data.
- DMA is enabled by default and may later be disabled by the core if channels are unavailable; this fallback should be expected.
- ACPI UID parsing controls bus numbering; missing UID maps to `-1`.
- Remove uses `pm_runtime_get_sync()` without checking a negative return before core remove.

## Test Signals
- ACPI IDs `80860F0E`, `8086228E`, `INT33C0`, `INT33C1`, `INT3430`, and `INT3431`.
- OF `marvell,mmp2-ssp` match data.
- Existing PXA SSP registry path versus embedded SSP initialization path.
- `spi-slave`, `num-cs`, and Intel type firmware properties.
- Runtime PM autosuspend and remove sequencing.
