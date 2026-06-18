# sources/distributed-fs/ceph-client/drivers/gpio/gpio-stmpe.c

## Purpose
This MFD child driver exposes STMPE GPIO expander blocks as gpiolib chips with optional threaded IRQ support. It handles multiple STMPE variants with different register maps, interrupt capabilities, and GPIO counts up to 24.

## Important APIs, Types, and Functions
`struct stmpe_gpio` stores the gpio chip, parent `struct stmpe`, IRQ mutex, no-request mask, and cached interrupt control registers (`regs` and `oldregs`) for rising, falling, and enable bits. GPIO callbacks read/write STMPE registers, set directions, and request GPIO alternate function ownership. IRQ callbacks implement bus lock/sync unlock, mask/unmask, type selection, and threaded IRQ demux. Debugfs output is provided by `stmpe_dbg_show()`.

## Control Flow
Probe obtains the parent STMPE object, validates GPIO count, initializes state, copies the template chip, reads optional `st,norequest-mask`, enables the GPIO block through the MFD core, optionally requests a threaded parent IRQ, configures a threaded gpio IRQ chip with valid-mask filtering, and registers the gpio chip. IRQ type/mask changes update cached arrays under `irq_lock`; `irq_bus_sync_unlock()` writes only changed registers to the bus. The threaded IRQ handler block-reads status banks, masks by cached IE bits, handles nested child IRQs, and clears status/edge-detect registers on variants where writes clear them.

## State and Persistence
GPIO state is in the STMPE device. Interrupt control state is cached in software until sync unlock to reduce bus writes and maintain atomic-looking irqchip operations over slow buses. `norequest_mask` prevents unavailable pins from GPIO and IRQ use. Managed cleanup disables the GPIO block on detach.

## Dependencies and Integration Points
The driver depends on the STMPE MFD core register map/index table, platform child devices, gpiolib, threaded IRQs, pinctrl-like STMPE alternate-function control, firmware properties, and debugfs when enabled.

## Risks
Variant differences are substantial: STMPE801 and STMPE1600 lack rising/falling-edge registers, STMPE1600 requires GPMR reads to get pin IRQs, and status register order differs by variant. The valid-mask loop checks `sizeof(u32)` iterations rather than `ngpios`, which effectively covers 32 bits but is visually easy to misread. IRQ cache correctness depends on bus lock/unlock pairing.

## Test Signals
Test each supported STMPE variant's register order and IRQ feature set, no-request mask enforcement for GPIO and IRQ, set/clear variants with shared or separate registers, bus-sync cache writes, threaded IRQ status dispatch and clear behavior, debugfs output, GPIO block enable/disable cleanup, and parent IRQ absence.
