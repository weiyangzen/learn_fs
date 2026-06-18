# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-at91.c

## Purpose
`ohci-at91.c` is the Atmel/Microchip AT91 platform glue for the generic OHCI USB host driver. It supplies clock control, platform data derived from device tree, per-port VBUS GPIO control, optional overcurrent GPIO handling, AT91-specific port suspend through SMC or SFR regmap, and HCD hook overrides for root-hub status/control.

## Important APIs, types, and functions
`struct at91_usbh_data` stores VBUS GPIOs, overcurrent GPIOs, root-hub port count, and per-port overcurrent status/change bits. `struct ohci_at91_priv` is OHCI private extension data containing interface/function/AHB clocks, `clocked`, saved wakeup state, optional SFR regmap, and optional suspend SMC id. `ohci_at91_drv_overrides` sets `.extra_priv_size`.

Clock and controller helpers are `at91_start_clock()`, `at91_stop_clock()`, `at91_start_hc()`, and `at91_stop_hc()`. Probe/remove are split between `usb_hcd_at91_probe()`/`usb_hcd_at91_remove()` and platform-driver wrappers `ohci_hcd_at91_drv_probe()`/`ohci_hcd_at91_drv_remove()`. Hub overrides are `ohci_at91_hub_status_data()` and `ohci_at91_hub_control()`. Suspend support uses `at91_dt_suspend_smc()`, `at91_dt_syscon_sfr()`, `ohci_at91_port_suspend()`, `ohci_hcd_at91_drv_suspend()`, and `ohci_hcd_at91_drv_resume()`. `ohci_hcd_at91_overcurrent_irq()` is the GPIO overcurrent ISR.

## Control flow
Module init calls `ohci_init_driver()`, then overwrites the generated OHCI HCD driver's `hub_status_data` and `hub_control` callbacks before registering the platform driver. Platform probe coerces a 32-bit DMA mask, allocates and attaches `at91_usbh_data`, reads `num-ports`, acquires indexed optional `atmel,vbus` GPIOs as output-high, acquires indexed optional `atmel,oc` GPIOs as inputs, requests shared overcurrent IRQs, enables wakeup, then calls `usb_hcd_at91_probe()`.

`usb_hcd_at91_probe()` allocates the HCD, maps registers, gets `ohci_clk`, `uhpck`, and `hclk`, discovers the suspend control path, sets `ohci->num_ports`, starts clocks and holds the controller in reset, sets `OHCI_CTRL_RWC`, and calls `usb_add_hcd()`. Removal unregisters the HCD, shuts down the controller, disables clocks, turns off VBUS GPIOs, and drops wakeup.

Hub control intercepts Set/ClearPortFeature POWER to toggle per-port VBUS GPIOs, Set/ClearPortFeature SUSPEND to call AT91-specific SFR/SMC suspend control, and overcurrent clear requests to update software flags. Other requests are delegated to `ohci_hub_control()`, then GetHubDescriptor is patched to advertise individual power switching and optional individual overcurrent protection, and GetPortStatus is patched to reflect GPIO power and software overcurrent bits.

System suspend saves whether wakeup is allowed outside slow-clock mode, enables IRQ wake when needed, calls `ohci_suspend()`, then either halts root-hub state and stops clocks or leaves clocks active for wake while asserting AT91 port suspend. Resume clears port suspend, disables IRQ wake or restarts clocks, and calls `ohci_resume()` with reset requested when clocks were stopped.

## State and persistence behavior
State is in device-managed GPIO/clock/regmap resources, `pdev->dev.platform_data`, OHCI private memory, and the OHCI core. `overcurrent_status[]` and `overcurrent_changed[]` are software latched status exposed through root-hub status and cleared through hub feature requests. `clocked` prevents duplicate clock enable/disable operations. `wakeup` persists only across suspend/resume.

## Dependencies and integration points
The driver depends on the generic OHCI core (`ohci.h`, `ohci_init_driver()`, `ohci_setup` through generic start, `ohci_hub_control()`, `ohci_hub_status_data()`, `ohci_suspend()`, `ohci_resume()`), Linux clock, GPIO descriptor, platform device, OF, DMA, regmap/syscon, ARM SMCCC, and AT91 SFR APIs. Device-tree bindings include `atmel,at91rm9200-ohci`, `num-ports`, indexed `atmel,vbus`, indexed `atmel,oc`, and optional `microchip,suspend-smc-id`; SFR fallback matches `atmel,sama5d2-sfr` or `microchip,sam9x60-sfr`.

## Risks and edge cases
`pdata->ports` defaults to zero if `num-ports` is absent, which would register an OHCI controller with no platform-described ports. VBUS GPIO acquisition errors are logged but do not fail probe, so missing power control may surface later as dead ports. Overcurrent IRQ setup failures are informational and overcurrent protection may be absent. The ISR only latches active-low overcurrent notification and does not explicitly clear status on exit; user-visible clearing depends on hub feature requests. Suspend behavior depends on slow-clock mode and on either SMC or SFR regmap availability; errors from `ohci_at91_port_suspend()` are ignored in some hub-control/suspend paths.

## Test signals
Test with AT91 device trees covering one to three ports, with and without VBUS GPIOs, with and without overcurrent GPIOs, and with SMC versus SFR suspend paths. Observe root-hub descriptors for individual power/overcurrent flags, per-port power changes through hub requests, overcurrent IRQ latching and clearing through `C_OVER_CURRENT`, system suspend/resume both with wakeup enabled and with clocks stopped, and regression against generic OHCI enumeration for low/full-speed devices.
