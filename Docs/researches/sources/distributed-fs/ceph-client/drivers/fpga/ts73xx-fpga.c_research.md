<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/ts73xx-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/ts73xx-fpga.c

## Purpose
`ts73xx-fpga.c` is an FPGA manager driver for the Altera Cyclone II FPGA on Technologic Systems TS-73xx boards. It bit-pushes configuration bytes through two MMIO registers and exposes the sequence through the Linux FPGA manager framework.

## Important APIs, types, and functions
`struct ts73xx_fpga_priv` stores the mapped register base and device pointer. Manager callbacks are `ts73xx_fpga_write_init()`, `ts73xx_fpga_write()`, and `ts73xx_fpga_write_complete()` in `ts73xx_fpga_ops`. Probe uses `devm_platform_ioremap_resource()` and `devm_fpga_mgr_register()`. Register bits include `TS73XX_FPGA_RESET`, `TS73XX_FPGA_WRITE_DONE`, `TS73XX_FPGA_CONFIG_LOAD`, and `TS73XX_FPGA_LOAD_OK`.

## Control flow
Probe maps the platform MMIO resource and registers an FPGA manager named `TS-73xx FPGA Manager`. Programming starts by dropping and reasserting reset with documented microsecond delays. The write callback polls the config register until the hardware is ready for each byte, then writes one byte to the data register. Completion toggles `CONFIG_LOAD`, waits, reads the status register, and returns `-ETIMEDOUT` if the load-ok bit is not set.

## State and persistence behavior
The driver keeps only the MMIO mapping and device pointer in managed memory. Programming state lives in board registers and the FPGA manager state machine; there is no persistent software state across unload or reboot.

## Dependencies and integration points
It depends on platform devices, MMIO helpers, `readb_poll_timeout()`, delay helpers, and the FPGA manager API. It integrates as a platform driver named `ts73xx-fpga-mgr`; board files or device tree/platform setup must provide the register resource.

## Risks and edge cases
The byte-at-a-time write path is sensitive to polling timeout, hardware-ready polarity, and register spacing. There is no explicit `.state` callback, partial-reconfiguration handling, firmware validation, or recovery beyond returning errors. Completion checks only `LOAD_OK`, so intermediate protocol failures may surface as timeout.

## Test signals
Build coverage, platform probe with a valid resource, successful manager registration, programming a known-good bitstream, timeout injection on `WRITE_DONE`, and `LOAD_OK` failure handling are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/ts73xx-fpga.c -->
