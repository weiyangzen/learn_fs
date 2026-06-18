# sources/distributed-fs/ceph-client/drivers/usb/dwc2/params.c

## Purpose
`params.c` detects DWC2 hardware capabilities, derives default core parameters, applies platform-specific overrides from OF/ACPI/PCI match data, reads firmware properties, validates parameters against hardware limits, and exports match tables used by platform and PCI glue.

## Important APIs, Types, And Functions
- Match tables: `dwc2_of_match_table`, `dwc2_acpi_match`, and exported `dwc2_pci_ids`.
- Platform override callbacks: `dwc2_set_bcm_params()`, `dwc2_set_his_params()`, Ingenic, Loongson, Samsung, Intel SoCFPGA, Rockchip, Lantiq, Amlogic, AMCC/APM, Sophgo, and STM32 parameter setters.
- Default derivation: `dwc2_set_default_params()` calls helpers for OTG caps, PHY type, speed, UTMI width, power-down, LPM, FIFO defaults, DMA capability, and host/gadget defaults.
- Firmware properties: `dwc2_get_device_properties()` reads gadget FIFO sizes, OTG capabilities, and overcurrent disable.
- Validation: `dwc2_check_params()` plus helpers such as `dwc2_check_param_otg_cap()`, `dwc2_check_param_phy_type()`, `dwc2_check_param_speed()`, `dwc2_check_param_power_down()`, `dwc2_check_param_tx_fifo_sizes()`, and `dwc2_check_param_eusb2_disc()`.
- Hardware discovery: public `dwc2_get_hwparams()` and private `dwc2_get_host_hwparams()` / `dwc2_get_dev_hwparams()`.
- Public initialization: `dwc2_init_params()`.

## Control Flow
Probe calls `dwc2_get_hwparams()` after core reset. That function reads `GHWCFG1-4` and `GRXFSIZ`, decodes op mode, architecture, FIFO depth, host channel count, PHY support, DMA descriptor support, power/LPM capabilities, and maximum transfer/packet counts. It temporarily forces host or device mode where needed to read mode-specific reset FIFO values.

Later `dwc2_init_params()` sets hardware-derived defaults, reads firmware properties, applies an OF/ACPI match callback when present, or PCI driver data when applicable. It then applies maximum-speed policy from `usb_get_maximum_speed()` and calls `dwc2_check_params()` to clamp invalid values back to supported defaults or disable unsupported booleans.

The platform setter callbacks are narrow tables of SoC-specific corrections. They tune FIFO sizes, DMA enablement, PHY type and width, power-down mode, burst length, LPM features, overcurrent/ID/VBUS detection quirks, and low-power FS/LS host behavior.

## State And Persistence Behavior
The file populates `hsotg->hw_params` and `hsotg->params`, both runtime in-memory structures used by the rest of the driver. `hw_params` is derived from controller registers; `params` is derived from hardware, firmware, and match data. There is no disk persistence. Some fields become long-lived policy for the controller lifetime, such as DMA mode, FIFO sizes, host channel count, PHY choice, LPM, power-down strategy, and platform quirks.

## Dependencies And Integration Points
`platform.c` uses the OF and ACPI match tables and calls `dwc2_get_hwparams()` and `dwc2_init_params()` during probe. `pci.c` uses `dwc2_pci_ids`. Host interrupt and queue code depend on `params.host_dma`, `params.dma_desc_enable`, `params.uframe_sched`, FIFO sizes, max transfer sizes, and FS/LS low-power settings. Gadget code depends on gadget FIFO and DMA params. The code uses firmware property APIs, USB OF helpers, generic PHY bus-width query, PCI ID matching, and DWC2 register definitions from `hw.h`.

## Risks
- `dwc2_set_param_phy_type()` assigns FS for FS-only cases but then unconditionally assigns `val`; this pattern depends on `val` already representing the intended fallback.
- Hardware mode forcing during parameter reads must happen immediately after reset; calling it later could disturb active operation.
- Platform overrides can disable DMA/LPM/power features for correctness. Removing or generalizing them risks regressions on specific SoCs.
- Validation macros silently replace invalid values with defaults after warnings. Bad defaults can hide firmware errors until runtime.
- FIFO size validation must respect total depth and per-FIFO hardware sizes; mistakes can cause endpoint allocation or transfer failures.
- PCI fallback assumes parent device is a PCI device when no match data exists.

## Test Signals
- Probe logs should show valid core release and no invalid-parameter warnings for known-good device trees.
- Boot host, gadget, and dual-role configurations across representative SoCs or emulated configs.
- Validate FIFO sizing by running gadget endpoints with multiple TX FIFOs and host transfers using periodic/non-periodic FIFOs.
- Test maximum-speed firmware limits, especially full-speed forcing and invalid low-speed forcing.
- Confirm platform-specific quirks: STM32 ID/VBUS detection, Ingenic overcurrent property, Loongson partial power-down, CV1800 non-DMA mode, and Rockchip LPM disable.
- Build with OF, ACPI, and PCI combinations to verify exported match tables and fallback paths.
