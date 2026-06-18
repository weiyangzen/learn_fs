# `sources/distributed-fs/ceph-client/include/linux/usb/ohci_pdriver.h`

## Purpose

`ohci_pdriver.h` defines platform data for generic OHCI host controller platform drivers. It captures endian quirks, port count, and board-specific power callbacks.

## Important APIs, Types, and Constants

- `struct usb_ohci_pdata` contains `big_endian_desc`, `big_endian_mmio`, `no_big_frame_no`, and `num_ports`.
- `power_on()`, `power_off()`, and `power_suspend()` callbacks manage clocks, regulators, and suspend-only hotplug/VBUS power.

## Control Flow and Lifetimes

Platform code attaches `usb_ohci_pdata` before probe. The OHCI platform driver reads endian and port fields while initializing the HCD and calls power callbacks during probe, remove, and suspend transitions.

## State and Persistence Behavior

The structure is static platform configuration. Runtime HCD and OHCI register state live in the host controller driver.

## Dependencies and Integration Points

It integrates generic OHCI platform glue with board/SoC power management and endian-specific OHCI accessors. It references `struct platform_device`.

## Risks and Edge Cases

Wrong endian flags corrupt descriptor or MMIO interpretation. Power callbacks must be ordered with HCD registration/removal to avoid interrupts against unpowered hardware. `power_suspend()` must leave enough circuitry alive for hotplug/wakeup if promised.

## Test Signals

Probe OHCI platform controllers on endian variants, enumerate devices, suspend/resume with wakeup, test remove after failed probe, validate port count, and use DMA/API debugging for descriptor endian mistakes.
