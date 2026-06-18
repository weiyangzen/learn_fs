<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pch.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pch.c

## Purpose
PCI GPIO driver for Intel EG20T and ROHM/LAPIS ML7223 PCH/IOH devices. It provides MMIO direction/value operations, per-line IRQs through generic IRQ chips, and suspend/resume context restore.

## Important APIs, types, and functions
`struct pch_regs` maps registers; `struct pch_gpio` stores MMIO, chip, saved context, IRQ base, type, and spinlock. GPIO callbacks handle direction, get/set, and `to_irq()`. IRQ callbacks program mode, mask/unmask, ack, and dispatch parent status.

## Control flow
Probe enables PCI, maps BAR 1, selects pin count, registers GPIO, allocates IRQ descriptors, masks/enables interrupts, requests the PCI IRQ, and allocates a generic IRQ chip. Output direction writes PO then PM. IRQ type writes `im0`/`im1` four-bit mode fields and selects edge/level flow.

## State and persistence behavior
Suspend saves interrupt, output, direction, mode, and device-specific registers. Resume pulses reset and restores saved values.

## Dependencies and integration points
Uses managed PCI resources, generic IRQ chip APIs, gpiolib, MMIO accessors, and simple PM ops.

## Risks and edge cases
If IRQ descriptor allocation fails, GPIO remains registered with `irq_base = -1`. Unsupported IRQ types return 0. Restore must handle variant-specific registers such as ML7223n `gpio_use_sel`.

## Test signals
PCI ID coverage, direction/value operations, IRQ descriptor and trigger setup, suspend/resume restore, and no-IRQ path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pch.c -->
