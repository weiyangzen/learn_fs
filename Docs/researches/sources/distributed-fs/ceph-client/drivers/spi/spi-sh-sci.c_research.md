# sources/distributed-fs/ceph-client/drivers/spi/spi-sh-sci.c

## Purpose

`spi-sh-sci.c` is a bitbanged SPI driver using SuperH SCI pin-control register bits as GPIO-like SCK, MOSI, and MISO signals. It wraps the generic `spi_bitbang` framework and delegates chip-select control to platform data.

## Important APIs, Types, and Functions

`struct sh_sci_spi` embeds `struct spi_bitbang`, MMIO base, cached SCSPTR output value, platform `struct sh_spi_info`, and platform device. Low-level helpers are `setbits()`, `setsck()`, `setmosi()`, and `getmiso()`. The included `spi-bitbang-txrx.h` uses these helpers through four mode-specific wrappers: `sh_sci_spi_txrx_mode0()` through mode3. `sh_sci_spi_chipselect()` calls the platform chip-select callback.

Probe/remove allocate/release the SPI host, map/unmap SCI registers, initialize pins, start/stop bitbang, and restore pin state.

## Control Flow

Probe requires platform data for bus number, chip-select count, and optional chip-select callback. It configures the bitbang controller and txrx functions, maps the SCI resource, caches the current SCSPTR value, sets initial SCK/TXD/output-enable bits, and starts the bitbang engine. Runtime transfers are handled by the SPI bitbang core, which calls the mode-specific txrx function, toggles SCK/MOSI via `setbits()`, samples MISO from SCSPTR, delays with `ndelay()`, and invokes the platform CS callback.

## State and Persistence Behavior

The only driver state is the cached SCSPTR byte and platform data pointer. There is no persistence. The driver assumes it is the sole user of SCSPTR bits and therefore avoids locking around the cached read-modify-write model.

## Dependencies and Integration Points

The file depends on legacy SuperH platform data in `<asm/spi.h>`, MMIO helpers, `spi_bitbang`, and platform devices. It does not use OF, DMA, interrupts, clocks, or runtime PM.

## Risks and Edge Cases

Correctness depends on exclusive ownership of SCSPTR; any other user changing those bits will desynchronize `sp->val`. Speed and delays are governed by spi-bitbang timing rather than hardware clocks, so performance is low and CPU-bound. Missing platform data prevents probe. Chip-select semantics are entirely platform-callback-defined. Because MISO and MOSI share `PIN_TXD` definitions for this SCI mode, board wiring assumptions are critical.

## Test Signals

Test all four SPI modes, platform chip-select callback polarity, initialization and cleanup pin values, transfers with no RX or no TX, concurrent SCSPTR users if any exist on target boards, and behavior when platform data or memory resources are absent.
