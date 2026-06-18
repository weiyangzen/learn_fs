# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-st.c

## Purpose

`ohci-st.c` is STMicroelectronics OHCI platform glue for `st,st-ohci-300x`. It extends generic platform handling with multiple clocks, optional 48 MHz clock rate programming, power and soft reset controls, and a USB PHY.

## Important APIs, Types, and Functions

`struct st_ohci_platform_priv` stores up to three clocks, optional `clk48`, power and softreset reset controls, and a PHY. Important functions are `st_ohci_platform_power_on()`, `st_ohci_platform_power_off()`, `st_ohci_platform_probe()`, `st_ohci_platform_remove()`, `st_ohci_suspend()`, and `st_ohci_resume()`.

## Control Flow

Probe gets IRQ, creates an HCD with private state, gets the USB PHY, collects unnamed OF clocks, obtains optional 48 MHz clock and reset controls, powers on by deasserting power/reset, setting `clk48` to 48 MHz, enabling clocks, initializing and powering the PHY, maps registers, and calls `usb_add_hcd()`. Remove unregisters the HCD, powers off, releases clocks, and drops the HCD. Suspend calls `ohci_suspend()` then platform power-off; resume powers on and calls `ohci_resume()`.

## State and Persistence Behavior

State includes clock handles, reset handles, PHY state, HCD/OHCI state, and platform data pointing at default power callbacks. Hardware state is reset/clock/PHY controlled and not persisted after power-off.

## Dependencies and Integration Points

It depends on OF platform resources, clock framework, reset framework, generic PHY API, `usb_ohci_pdata`, generic OHCI initialization, and `st,st-ohci-300x` binding data.

## Risks and Test Signals

Risks include asserting power before softreset on power-off, optional reset semantics, PHY init/power unwind ordering, missing runtime PM compared with generic platform driver, and assuming unnamed clock order. Test signals include PHY/reset/clock failure injection, 48 MHz rate programming, suspend/resume, probe deferral for PHY/clocks/resets, and clean remove after active devices.
