# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-reg.c

Purpose: Register-controlled I2C mux driver. It writes channel values to an MMIO register, with platform data or DT configuration, 1/2/4-byte register sizes, endian selection, optional posted-write readback, and optional idle-state deselection.

Important APIs/types/functions: `struct regmux` wraps `i2c_mux_reg_platform_data`. `i2c_mux_reg_set()` performs endian-aware `iowrite8/16/32` and optional readback. `i2c_mux_reg_select()` and `i2c_mux_reg_deselect()` are mux callbacks. `i2c_mux_reg_probe_dt()` parses `i2c-parent`, child `reg` channel values, endian flags, `write-only`, `idle-state`, and resources. Probe maps resources and adds adapters.

Control flow: Probe fills platform data from board data or DT, gets the parent adapter, maps the register if needed, validates register size, allocates the mux core, sets deselect when idle is configured, and adds one adapter per configured value. Select writes the child channel ID; deselect writes idle only when configured.

State and persistence: Software state is static configuration: parent adapter id, channel values, base numbering, mapped register, register size, endian flag, write-only flag, and idle value. Hardware state is the selected register value. No last-value cache exists.

Dependencies/integration: OF address parsing, `of_find_i2c_adapter_by_node()`, platform data ABI, devm MMIO mapping, platform driver core, and I2C mux framework.

Risks: Child `reg` parsing does not check read errors. Default endianness follows build target if no DT endian flag exists. Readback flush is skipped for write-only hardware. Unsupported register size fails probe.

Test signals: Verify 8/16/32-bit writes, little/big endian behavior, posted-write readback, write-only mode, idle-state deselect, parent probe deferral, bad resource size, and adapter-add rollback.
