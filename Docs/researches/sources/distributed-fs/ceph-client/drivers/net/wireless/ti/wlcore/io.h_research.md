# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/io.h

## Purpose
`io.h` declares wlcore IO APIs and implements inline raw, translated, register, data, hardware-address, power, and 32-bit bus access helpers. It is the main abstraction boundary between wlcore core code and the lower SDIO/SPI bus operations.

## Important APIs and helpers
Constants define hardware access ranges and partition register offsets. Declarations cover IRQ wrappers, IO reset/init, address translation, partition setup, block-size setup, and dummy packet TX.

Inline helpers include `wlcore_raw_read()`, `wlcore_raw_write()`, `wlcore_raw_read_data()`, `wlcore_raw_write_data()`, `wlcore_raw_read32()`, `wlcore_raw_write32()`, `wlcore_read()`, `wlcore_write()`, `wlcore_write_data()`, `wlcore_read_data()`, `wlcore_read_hwaddr()`, `wlcore_read32()`, `wlcore_write32()`, `wlcore_read_reg()`, `wlcore_write_reg()`, `wl1271_power_off()`, and `wl1271_power_on()`.

## Control flow
Raw access checks `WL1271_FLAG_IO_FAILED` and rejects most IO while in ELP except the ELP control register. It calls `wl->if_ops->read()` or `write()` and marks IO failed on errors while the device is not off. Translated helpers convert wlcore virtual addresses using `wlcore_translate_addr()`. Register/data helpers index `wl->rtable`. Power helpers call optional bus power callbacks and maintain `WL1271_FLAG_GPIO_POWER`.

## State and persistence behavior
The helpers update `WL1271_FLAG_IO_FAILED` after transport errors and `WL1271_FLAG_GPIO_POWER` after power transitions. They depend on persistent `wl->curr_part`, `wl->rtable`, `wl->buffer_32`, device state, and ELP flags. The IO failed flag persists until higher-level recovery clears or reinitializes state.

## Dependencies and integration points
This header depends on lower bus `if_ops`, partition state from `io.c`, chip address conversion callbacks, and shared wlcore flags. It is included throughout command, event, init, debugfs, TX/RX, and chip-specific code.

## Risks
Because many functions are inline and widely used, error semantics must remain stable. Marking IO failed suppresses later accesses and drives recovery behavior. Returning `-EIO` when in ELP catches illegal sleep-state access but can expose callers that forgot runtime PM wakeup. `wl->buffer_32` is shared scratch storage and must be used under appropriate serialization.

## Test signals
Transport fault injection, ELP access checks, raw and translated 32-bit register reads/writes, power-on/off state transitions, command mailbox IO, debugfs device-memory access, and recovery after IO failure are the main signals.
