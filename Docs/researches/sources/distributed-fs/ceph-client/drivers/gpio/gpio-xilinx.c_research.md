# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xilinx.c

## Purpose
Implements gpiolib and optional interrupt support for Xilinx XPS/AXI GPIO IP. It handles one or two channels, configurable widths, default output/direction state, runtime PM/clock management, and software edge detection for per-line IRQs.

## Important APIs, Types, And Functions
- `struct xgpio_instance` stores the gpiochip, MMIO base, logical-to-hardware bitmap map, shadow state/direction/IRQ bitmaps, raw spinlock, optional parent IRQ, and clock.
- Channel helpers `xgpio_read_ch`, `xgpio_write_ch`, `xgpio_read_ch_all`, and `xgpio_write_ch_all` abstract 32-bit channel register accesses.
- GPIO callbacks `xgpio_get`, `xgpio_set`, `xgpio_set_multiple`, `xgpio_dir_in`, and `xgpio_dir_out` translate software offsets through the sparse hardware bitmap.
- PM callbacks `xgpio_request`, `xgpio_free`, runtime suspend/resume, and system suspend/resume manage clock/runtime PM.
- IRQ callbacks `xgpio_irq_mask`, `xgpio_irq_unmask`, `xgpio_set_irq_type`, and `xgpio_irqhandler` implement per-line edge detection from channel-change interrupts.
- `xgpio_probe` parses properties, initializes shadows and hardware, configures optional IRQ, and registers the chip.

## Control Flow
Probe reads `xlnx,is-dual`, default output and tristate properties, channel widths, builds a 64-bit hardware map, maps registers, enables the optional clock, starts runtime PM, writes initial data and direction registers, and optionally initializes interrupt registers and a chained irqchip. GPIO set/direction operations update shadow bitmaps under the raw spinlock and write the corresponding channel register. The interrupt handler acks per-channel status, reads current hardware values, compares them with `last_irq_read`, filters by enabled/rising/falling bitmaps, gathers hardware bits back into logical GPIO offsets, and dispatches child IRQs.

## State And Persistence
The driver maintains shadow output `state`, direction `dir`, last IRQ sample, enabled IRQs, and requested rising/falling edges. These shadows are rewritten to hardware on probe and used for RMW safety. Runtime PM disables/enables the clock; system sleep may force runtime suspend unless the parent IRQ is configured as a wake source.

## Dependencies And Integration Points
Depends on device properties from Xilinx IP, optional clock provider, platform MMIO/IRQ resources, PM runtime, gpiolib irqchip integration, and OF compatible `xlnx,xps-gpio-1.00.a`.

## Risks And Edge Cases
The hardware only reports channel-level changes, so per-line IRQs are synthesized by comparing snapshots; missed changes are possible if a line toggles back between samples. Width and bitmap mapping are critical for dual-channel devices and sparse logical numbering. `xgpio_request` returns a negative PM error but does not undo a failed `pm_runtime_get_sync`. Clock state and GPIO access depend on correct request/free and IRQ-resource PM balancing. Only edge triggers are supported.

## Test Signals
Cover single and dual channel widths, invalid widths over 32, default state/tri properties, set_multiple mapping, runtime PM request/free clock behavior, IRQ type rejection for level triggers, rising/falling/both edge detection from `last_irq_read`, channel interrupt enable/disable transitions, and suspend behavior with and without wake IRQ.
