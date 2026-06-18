# sources/distributed-fs/ceph-client/drivers/parisc/hppb.c

## Purpose
This file is the HP-PB bus driver for NOVA and K-Class PA-RISC systems. It claims GeckoBoa bus-controller MMIO windows so downstream HP-PB bus space is represented in the kernel resource tree.

## Important APIs, Types, And Functions
The local state type is `struct hppb_card`, containing the controller HPA, claimed MMIO resource, and a linked-list pointer. The driver entry points are `hppb_probe()` and `hppb_init()`, registered through a PA-RISC device table for GeckoBoa BCPORT devices.

## Control Flow
At `arch_initcall`, `hppb_init()` registers the `gecko_boa` PA-RISC driver. `hppb_probe()` appends or reuses a `hppb_card` entry, records the device HPA, reads the bus low/high MMIO bounds from the controller’s `bc_module` registers via `gsc_readl()`, and calls `ccio_request_resource()` to claim the resulting memory range. It logs whether the range was claimed and returns zero so the platform device is considered handled.

## State And Persistence
The file maintains a simple linked list rooted in `hppb_card_head`; entries persist for the lifetime of the system. Claimed resources remain inserted in the CCIO/iomem resource tree. There is no removal or cleanup path.

## Dependencies And Integration Points
It depends on PA-RISC parisc-driver matching, GSC MMIO reads, CCIO resource routing, and `struct bc_module` layout from architecture headers. It shares the `iommu.h` CCIO abstraction used by other PA-RISC bus code.

## Risks
The linked list is unsynchronized but populated only during early device discovery. If allocation of a second card fails, probe returns `1` rather than a conventional negative errno. The driver only logs resource-claim failure and still returns success, which may hide overlapping or invalid platform resource descriptions.

## Test Signals
Signals include GeckoBoa discovery logs, correct `io_io_low`/`io_io_high` decoding, resource tree entries labeled `HP-PB Bus`, and no conflicts with CCIO-managed regions. Multi-controller systems should verify list allocation and logging for each bus.
