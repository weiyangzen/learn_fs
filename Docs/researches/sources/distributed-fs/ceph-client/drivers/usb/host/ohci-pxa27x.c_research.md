# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-pxa27x.c

## Purpose

`ohci-pxa27x.c` is PXA27x/PXA3x OHCI platform glue. It programs PXA-specific USB host registers, supports DT-to-platform-data conversion, controls optional per-port VBUS regulators, and overrides hub control for port power.

## Important APIs, Types, and Functions

`struct pxa27x_ohci` stores the USB clock, MMIO base, three VBUS regulators, and per-port regulator state. Important functions are `pxa27x_ohci_select_pmm()`, `pxa27x_ohci_set_vbus_power()`, `pxa27x_ohci_hub_control()`, `pxa27x_setup_hc()`, `pxa27x_reset_hc()`, `pxa27x_start_hc()`, `pxa27x_stop_hc()`, `ohci_pxa_of_init()`, probe/remove, and PM callbacks.

## Control Flow

Probe converts DT properties into `pxaohci_platform_data` if present, gets IRQ and clock, creates HCD with private state, maps registers, obtains enabled-port VBUS regulators, starts hardware, selects port power-management mode, forces `ohci->num_ports = 3`, then registers the HCD. The overridden hub-control callback intercepts port power set/clear to enable or disable matching VBUS regulators before delegating to generic `ohci_hub_control()`. Suspend calls `ohci_suspend()` and stops PXA hardware; resume restarts hardware, reapplies PMM mode, and calls `ohci_resume()`.

## State and Persistence Behavior

State includes platform data flags, clock state, PXA UHC register programming, VBUS regulator enable flags, HCD state, and hard-coded three-port root-hub state. Hardware register settings persist while clocks and reset state remain active.

## Dependencies and Integration Points

It depends on PXA SoC helpers, `platform_data/usb-ohci-pxa27x.h`, regulator framework, clocks, OF properties named `marvell,*`, USB OTG pin-hold clearing, and generic OHCI callbacks initialized through `ohci_init_driver()`.

## Risks and Test Signals

Risks include busy-waiting indefinitely for `UHCHR_FSBIR`, unchecked regulator-get errors stored in the array, VBUS index assumptions, DT/platform-data parity, hard-coded three ports, and platform callback failures. Test signals include all PMM modes, per-port regulator toggling from hub requests, DT property parsing, suspend/resume with VBUS state, and enumeration on enabled ports only.
