# sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-usb2-clock-sel.c

## Purpose
Implements the R-Car Gen3 USB2.0 clock selector as a small common-clock provider. Although the hardware resembles a mux between `usb_extal` and `usb_xtal`, the driver exposes a gate-like clock named `rcar_usb2_clock_sel` because the EHCI/OHCI platform drivers do not switch parents. It coordinates USB module resets, the required bus/interface clocks, runtime PM, and the `USB20_CLKSET0` register bits needed for extal-only operation.

## Important APIs, Types, and Functions
`struct usb2_clock_sel_priv` stores the MMIO base, registered `clk_hw`, two bulk clocks (`ehci_ohci` and `hs-usb-if`), a shared reset-control array, and booleans indicating whether `usb_extal` and `usb_xtal` are present and have rates. `usb2_clock_sel_enable()` deasserts resets, enables the bulk clocks, then programs extal-only mode if needed. `usb2_clock_sel_disable()` reverses that sequence. `rcar_usb2_clock_sel_probe()` maps the resource, acquires clocks and resets, probes optional input oscillator rates, enables runtime PM, registers the clock, and publishes it through `of_clk_add_hw_provider()`.

## Control Flow, State, and Persistence
Probe initializes persistent device state in devm-managed storage and stores it as driver data. Enable state is controlled by CCF callbacks and not stored beyond hardware register state. If `usb_extal` exists and `usb_xtal` does not, `usb2_clock_sel_enable_extal_only()` writes `CLKSET0_EXTAL_ONLY`; suspend clears this to `CLKSET0_PRIVATE`, and resume reapplies it after a runtime-PM get. Error handling in enable asserts resets again if bulk clock enable fails.

## Dependencies, Integration Points, Risks, and Test Signals
The driver depends on the platform device resource, reset controller API, runtime PM, CCF, DT compatible `renesas,rcar-gen3-usb2-clock-sel`, and clocks named `ehci_ohci`, `hs-usb-if`, `usb_extal`, and `usb_xtal`. Consumers obtain the single provided clock from the node. Key tests are probe with extal-only and xtal boards, EHCI/OHCI operation across enable/disable, suspend/resume, and failure injection for bulk-clock enable to verify reset reassertion.
