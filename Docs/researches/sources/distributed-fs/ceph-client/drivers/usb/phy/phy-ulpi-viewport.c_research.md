<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi-viewport.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi-viewport.c

## Purpose
Generic ULPI viewport backend for legacy USB PHYs whose ULPI registers are accessed through one memory-mapped viewport register.

## Important APIs, Types, And Functions
`ulpi_viewport_wait()` polls for `WAKEUP` or `RUN` to clear. `ulpi_viewport_read()` wakes the viewport, issues a read transaction, and extracts the data byte. `ulpi_viewport_write()` wakes the viewport and issues a write transaction. The exported `ulpi_viewport_access_ops` provides `.read` and `.write` callbacks.

## Control Flow
Controller drivers set `usb_phy->io_priv` to the viewport MMIO address and use these ops through generic ULPI code. Each access is synchronous and atomically polls up to 2 ms.

## State And Persistence
No private software state. Hardware state is the viewport register and downstream ULPI register file.

## Dependencies And Integration Points
Depends on MMIO helpers, `readl_poll_timeout_atomic()`, and the legacy `usb_phy` I/O abstraction. Tegra ULPI uses it with `regs + ULPI_VIEWPORT`.

## Risks
Negative timeout errors must be handled by callers. Wrong `io_priv` or a controller with incompatible viewport layout can corrupt MMIO. Atomic polling can spin for the full timeout.

## Test Signals
ULPI scratch integrity tests, stuck `WAKEUP`/`RUN` timeouts, read/write byte packing, and error propagation through generic ULPI init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi-viewport.c -->
