# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-usb.h

## Purpose
This header binds the A80 USB CCU C file to its public clock and reset dt-bindings and defines the onecell array size.

## Important APIs, Types, And Functions
It includes `sun9i-a80-usb.h` clock/reset binding headers and defines `CLK_NUMBER` as `CLK_USB_HSIC + 1`.

## Control Flow
It has no runtime flow. The provider uses the constant to size `sun9i_a80_usb_hw_clks`.

## State And Persistence
No state is stored. The value is a compile-time contract between binding IDs and onecell provider sizing.

## Dependencies And Integration Points
It integrates with `ccu-sun9i-a80-usb.c` and DT consumers of USB HCI, OHCI, PHY, and HSIC clocks/resets.

## Risks
Incorrect sizing can truncate the last clock ID or leave lookup holes, causing `of_clk_get()` failures for USB consumers.

## Test Signals
Build and USB controller probe tests validate that all exported IDs resolve.
