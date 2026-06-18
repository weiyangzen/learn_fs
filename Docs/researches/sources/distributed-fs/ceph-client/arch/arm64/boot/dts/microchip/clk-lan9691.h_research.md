# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/microchip/clk-lan9691.h

## Purpose
This binding header assigns clock IDs for the Microchip LAN9691 clock controller. DTS files use these numeric IDs in `clocks` or clock-controller specifier cells.

## APIs, Types, And Constants
The macro API defines generic clock IDs `GCK_ID_QSPI0` through `GCK_ID_USB_REFCLK` with values 0 through 11, followed by gate clock IDs `GCK_GATE_USB_DRD`, `GCK_GATE_MCRAMC`, and `GCK_GATE_HMATRIX` with values 12 through 14.

## Control Flow And State
There is no executable control flow or state. The constants are compiled into DTBs and then interpreted by the LAN9691 clock provider driver.

## Dependencies And Integration
The header is protected by `_DTS_CLK_LAN9691_H` and uses no includes. Its integration point is the binding contract between LAN9691 DTS nodes and the clock driver.

## Risks And Test Signals
The risk is ABI mismatch: changing IDs or inserting values can break existing DTBs and driver lookup tables. Build tests catch missing includes, but functional tests require booting LAN9691 boards and verifying clock consumers probe successfully.
