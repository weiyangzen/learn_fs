# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-platform.c

## Purpose

`ohci-platform.c` is the generic platform and devicetree OHCI driver. It handles clocks, optional shared resets, endian/port-count DT properties, runtime PM setup, and generic platform HCD registration.

## Important APIs, Types, and Functions

`struct ohci_platform_priv` stores up to four clocks and a reset-control array. Key functions are `ohci_platform_power_on()`, `ohci_platform_power_off()`, `ohci_platform_probe()`, `ohci_platform_remove()`, `ohci_platform_suspend()`, `ohci_platform_resume_common()`, `ohci_platform_resume()`, and `ohci_platform_restore()`.

## Control Flow

Probe supplies default platform data when none is provided, coerces a 32-bit DMA mask, gets IRQ, creates HCD with extra private state, parses DT endian and `num-ports` properties, obtains clocks and shared resets, validates endian Kconfig support, enables runtime PM, powers on clocks, maps registers, records TPL support, and calls `usb_add_hcd()`. Remove wakes the device, removes HCD, powers off, asserts resets, puts clocks, releases HCD, and disables runtime PM. Suspend calls generic OHCI suspend, powers off, and asserts resets; resume deasserts resets, powers on, calls `ohci_resume()`, and refreshes runtime PM state.

## State and Persistence Behavior

State consists of HCD private clock/reset handles, OHCI quirk flags from firmware properties, `ohci->num_ports`, runtime PM flags, and hardware reset/clock state. No durable data is stored.

## Dependencies and Integration Points

It depends on platform bus, OF properties from generic OHCI bindings, clock and reset frameworks, runtime PM, USB OF TPL helper, generic OHCI core, and optional board-supplied `usb_ohci_pdata`. It matches `generic-ohci`, `cavium,octeon-6335-ohci`, and `ti,ohci-omap3`.

## Risks and Test Signals

Risks include endian property/Kconfig mismatches, incomplete clock lists, shared reset ordering, runtime PM state imbalance, and platform-data versus DT default differences. Test signals include DT probes with big-endian properties, clock/reset failure injection, suspend/resume/restore, TPL property propagation, and remove/reprobe with all clocks released.
