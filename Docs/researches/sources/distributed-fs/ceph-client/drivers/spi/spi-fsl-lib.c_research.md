# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-lib.c

## Purpose
Provides shared helper code for the classic Freescale SPI/eSPI family, especially buffer accessor functions, platform-data conversion, mode-name formatting, and common probe initialization for `struct mpc8xxx_spi`.

## Important APIs, Types, And Functions
Macro-generated exports implement `mpc8xxx_spi_rx_buf_u8/u16/u32()` and `mpc8xxx_spi_tx_buf_u8/u16/u32()`. Other exports are `to_of_pinfo()`, `mpc8xxx_spi_strmode()`, `mpc8xxx_spi_probe()`, and `of_mpc8xxx_spi_probe()`.

## Control Flow
The generated TX helpers read one typed value from the current TX pointer, shift it by `tx_shift`, advance the pointer, and return zero for dummy TX. RX helpers shift incoming register data by `rx_shift`, store one typed value, and advance RX. `mpc8xxx_spi_probe()` initializes controller mode bits, private buffer functions, flags, input clock, IRQ, shifts, bus number, chip-select count, and completion. `of_mpc8xxx_spi_probe()` allocates OF-backed platform data, determines bus number and clock, and sets mode flags from `mode` or compatible strings.

## State And Persistence
State lives in `struct mpc8xxx_spi` and platform data attached to the device. Buffer pointers are advanced during transfers; completion is initialized once. No persistent state is stored.

## Dependencies And Integration Points
Depends on SPI core, platform devices, OF, Freescale platform data, and optionally `get_brgfreq()`/`fsl_get_sys_freq()` under `CONFIG_FSL_SOC`. It is used by `spi-fsl-spi.c` and CPM helpers.

## Risks
The typed buffer helpers assume alignment and word-size choices made by the parent driver. OF mode parsing maps textual modes to flags and must stay synchronized with CPM/QE backend support. If clock discovery fails, probe returns `-ENODEV` or property errors.

## Test Signals
Accessor behavior for 8/16/32-bit buffers and shifts, dummy TX, OF mode parsing for CPU/QE/CPM, clock fallback paths, and initialization of controller limits are useful tests.
