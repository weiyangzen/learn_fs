# sources/distributed-fs/ceph-client/drivers/bus/brcmstb_gisb.c

## Purpose
Implements the Broadcom STB GISB arbiter driver. It decodes internal bus timeout, target-abort, breakpoint, die, and panic errors into useful address/master diagnostics and exposes the arbiter timeout through sysfs.

## Important APIs, Types, And Functions
`struct brcmstb_gisb_arb_device` stores MMIO base, SoC-specific register offset table, endian mode, mutex, global list node, valid master mask, master names, and suspend-saved timeout. Helpers `gisb_read()`, `gisb_write()`, `gisb_read_address()`, and `gisb_read_bp_address()` abstract SoC register layouts. Error decode paths include `brcmstb_gisb_arb_decode_addr()`, IRQ handlers for timeout/target abort/breakpoint, MIPS bus error handling, and panic/die notifier callbacks. Sysfs is `gisb_arb_timeout`.

## Control Flow
Probe maps the MMIO resource, chooses an offset table from the OF compatible, requests required timeout and target-abort IRQs plus optional breakpoint IRQ, parses master masks/names, adds the device to a global list, installs the MIPS bus error handler when applicable, and registers panic/die notifiers for the first device. IRQ and notifier paths read captured status/address/master registers, print a critical diagnostic, then clear the capture register. Suspend stores the timeout register; noirq resume restores it before interrupt handling can observe stale values.

## State And Persistence
Runtime state includes the global list of arbiters, per-device master naming, and saved timeout. Hardware state includes timeout and captured error registers. Sysfs writes change the live hardware timeout and are not persistently stored by the driver.

## Dependencies And Integration Points
The driver depends on platform/OF probing, Broadcom compatible strings, interrupt delivery, optional MIPS trap integration, panic/die notifier chains, sysfs attribute groups, and PM sleep callbacks.

## Risks And Test Signals
Risks include incorrect offset tables for a compatible, endian mismatches, optional register absence, not clearing the right capture register, notifier ordering during panic, and invalid timeout values. Test signals are sysfs timeout read/write, injected GISB timeout/TEA/breakpoint diagnostics with decoded master names, suspend/resume retaining timeout, and MIPS bus error fixup behavior.
