<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx.h

## Purpose
`mxl5xx.h` is the public board-facing header for the MaxLinear MxL5xx satellite tuner-demodulator driver. It defines the attach configuration that board drivers pass to the demodulator and provides a Kconfig-gated attach stub.

## Important APIs, Types, And Functions
`struct mxl5xx_cfg` carries the chip I2C address, device type, crystal capacitance, crystal clock, TS clock, optional firmware pointer/length, and optional `fw_read()` callback with private data. `mxl5xx_attach()` accepts an I2C adapter, config, demod id, tuner id, and an out-parameter for the driver's `set_input()` callback, returning a `struct dvb_frontend *` when `CONFIG_DVB_MXL5XX` is reachable. The disabled inline implementation logs a warning and returns `NULL`.

## Control Flow
The header has no runtime flow beyond the disabled-driver stub. At runtime `mxl5xx.c` consumes every field in `mxl5xx_cfg`: address/type for shared-chip matching and SKU setup, clock/cap for crystal programming, TS clock for MPEG output rate, firmware fields for loading, and `fw_read()` when firmware is not embedded.

## State And Persistence
The header defines no storage. It describes board-supplied immutable setup data and firmware access. Any returned frontend state is allocated and owned by `mxl5xx.c`.

## Dependencies And Integration Points
It includes Linux types, I2C declarations, and DVB frontend declarations. Board drivers integrate with the demod by including this header and holding the returned frontend and `fn_set_input` callback.

## Risks
The `type`, `clk`, `cap`, and `ts_clk` values are hardware-contract inputs; wrong values can make probe fail or produce invalid clock/TS output. Firmware pointer lifetime must cover attach-time download. The fallback stub uses `pr_warn()`, so users can detect builds where the driver was not enabled.

## Test Signals
Compile tests with `CONFIG_DVB_MXL5XX=y/m/n`, board attach tests with embedded and callback firmware, and validation that the returned `set_input` callback is non-NULL only on successful attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx.h -->
