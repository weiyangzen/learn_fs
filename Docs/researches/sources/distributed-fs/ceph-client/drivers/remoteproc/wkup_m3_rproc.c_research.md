# sources/distributed-fs/ceph-client/drivers/remoteproc/wkup_m3_rproc.c

## Purpose

This file implements the remoteproc driver for the TI AM335x/AM437x Wakeup M3 processor. The Wakeup M3 is a small firmware-controlled power-management processor; this driver exposes it to the remoteproc framework, maps its UMEM/DMEM regions for firmware loading, and controls reset through either a reset-controller handle or legacy platform data callbacks.

## Important APIs, Types, And Functions

`struct wkup_m3_mem` records CPU virtual address, bus address, M3 device address, and size for each internal memory region. `struct wkup_m3_rproc` stores the `rproc`, platform device, two memory descriptors, and optional reset control.

The remoteproc ops are `wkup_m3_rproc_start()`, `wkup_m3_rproc_stop()`, and `wkup_m3_rproc_da_to_va()`. Start deasserts reset; stop asserts reset. If no reset controller is present, legacy `wkup_m3_platform_data` callbacks provide reset operations. `wkup_m3_rproc_da_to_va()` translates firmware device addresses into mapped UMEM/DMEM kernel addresses.

`wkup_m3_rproc_probe()` performs all setup: reads `ti,pm-firmware`, enables runtime PM, allocates the remoteproc, gets reset control or platform callbacks, maps named memory resources `umem` and `dmem`, computes M3-relative device addresses, and registers the remoteproc.

## Control Flow

Probe requires a firmware filename from device tree. Runtime PM is enabled and a `devm_add_action_or_reset()` callback balances the initial `pm_runtime_get_sync()`. The remoteproc is allocated with `auto_boot = false` and `sysfs_read_only = true`, so firmware is not automatically started and sysfs users cannot mutate normal remoteproc state. Memory mapping processes `umem` first, because the M3 address space treats UMEM as device address zero; each region's device address is then normalized by subtracting UMEM's bus offset.

At remoteproc start, reset is deasserted through the reset framework or platform callback. Stop mirrors this with reset assertion. Address translation scans both internal memories and returns NULL for zero-length or out-of-range requests.

## State And Persistence

Driver state is devm-managed under the platform device. The memory map persists while the device is bound. The M3 firmware lifecycle is explicitly non-autoboot, and the driver keeps runtime PM active for its lifetime by refusing runtime suspend with `-EBUSY`.

## Dependencies And Integration Points

The driver integrates with remoteproc, runtime PM, reset framework, devicetree resources, and legacy `linux/platform_data/wkup_m3.h`. It binds `ti,am3352-wkup-m3` and `ti,am4372-wkup-m3`. Required resource names are `umem` and `dmem`, and required DT firmware property is `ti,pm-firmware`.

## Risks And Edge Cases

The fallback path requires complete platform data if the reset controller is absent; otherwise probe fails. `of_get_address()` results are dereferenced without an explicit NULL check after resource mapping, so malformed DT address data could be risky. Runtime suspend always returns busy, which is intentional for availability but prevents deeper PM states for this device. The driver has no crash recovery or mailbox handling of its own.

## Test Signals

Probe tests should cover firmware property absence, reset-controller and platform-data reset paths, resource mapping for both memories, and address translation boundaries. Runtime tests should verify start/stop reset polarity and that PM runtime references are balanced on probe failure and device removal.
