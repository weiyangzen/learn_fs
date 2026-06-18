# sources/distributed-fs/ceph-client/drivers/spi/spi-meson-spifc.c

## Purpose

`spi-meson-spifc.c` is the Amlogic Meson SPI flash controller driver. It exposes a single-chipselect, 8-bit SPI host that transfers data through the controller's 64-byte internal command/data buffer and manages its clock with runtime PM.

## Important APIs, Types, And Functions

`struct meson_spifc` stores the SPI host, regmap, input clock, and device. Key functions are `meson_spifc_wait_ready()`, `meson_spifc_drain_buffer()`, `meson_spifc_fill_buffer()`, `meson_spifc_setup_speed()`, `meson_spifc_txrx()`, `meson_spifc_transfer_one()`, `meson_spifc_hw_init()`, probe/remove, and system/runtime PM hooks.

## Control Flow, State, And Persistence

Probe allocates a host, initializes an MMIO regmap, enables the clock, sets 8-bit-only transfer support and min/max speeds from the clock, resets the hardware, enables runtime PM, and registers the controller. A transfer programs the divider, disables AHB mode, splits the transfer into up to 64-byte chunks, fills the buffer for TX, configures DOUT and DIN stages, handles CS continuation according to transfer/message boundaries, starts the user command, waits up to 5 ms for `SLAVE_TRST_DONE`, drains RX if needed, and finally re-enables AHB mode.

State is volatile controller registers and runtime PM clock state. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on platform/OF, regmap MMIO, clocks, runtime PM, and SPI core. It matches `amlogic,meson6-spifc` and `amlogic,meson-gxbb-spifc`.

## Risks And Test Signals

Risks include unaligned `u32 *` buffer accesses, chunked CS-change semantics, fixed 5 ms ready timeout, and clock disable/enable ordering across system and runtime PM. Test flash reads/writes spanning 64-byte chunks, TX/RX/full-duplex transfers, CS-change cases, runtime suspend/resume, and ready-timeout injection.
