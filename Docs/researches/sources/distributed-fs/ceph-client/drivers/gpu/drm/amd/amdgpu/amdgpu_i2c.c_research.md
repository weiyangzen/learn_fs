# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_i2c.c

## Purpose
`amdgpu_i2c.c` implements AMDGPU display I2C/DDC bus creation and routing for legacy AtomBIOS paths. It supports hardware AtomBIOS I2C when enabled, software bit-banging over GPIO/DDC registers, bus lookup, bus initialization/finalization, and external DDC/clock-data router mux selection.

## Important APIs, types, and functions
Exported functions are `amdgpu_i2c_create()`, `amdgpu_i2c_init()`, `amdgpu_i2c_fini()`, `amdgpu_i2c_lookup()`, `amdgpu_i2c_router_select_ddc_port()`, and `amdgpu_i2c_router_select_cd_port()`. Internal bit-bang callbacks include `amdgpu_i2c_pre_xfer()`, `amdgpu_i2c_post_xfer()`, `amdgpu_i2c_get_clock()`, `amdgpu_i2c_get_data()`, `amdgpu_i2c_set_clock()`, and `amdgpu_i2c_set_data()`.

## Control flow
`amdgpu_i2c_create()` rejects MM I2C buses if hardware I2C is disabled, allocates an `amdgpu_i2c_chan`, copies the AtomBIOS bus record, initializes the adapter and mutex, and either registers a hardware AtomBIOS algorithm adapter or a software `i2c-algo-bit` adapter. Bit-bang transfer setup locks the channel, switches pads into DDC mode, clears output values, sets pins to input, and masks GPIO pins for software control. Post-transfer unsets the masks and unlocks. Router selection reads and writes mux control registers over the selected router bus to choose DDC or clock/data paths.

## State and persistence behavior
State is held in allocated `amdgpu_i2c_chan` objects and `adev->i2c_bus[]`. Register changes configure GPIO/DDC pins and mux chips at runtime. `amdgpu_i2c_fini()` clears stored bus pointers; devm-managed adapters are removed with the DRM device lifecycle. There is no persistence.

## Dependencies and integration points
The file depends on Linux I2C core and bit-bang APIs, DRM EDID/display paths, AtomBIOS I2C helpers, AMDGPU register access macros, connector router metadata, and module parameters controlling hardware I2C. It feeds display connector probing and EDID/DDC access for non-DC or legacy paths.

## Risks and edge cases
GPIO register programming must leave pads unmasked after transfers. Hardware I2C availability depends on AtomBIOS records and module parameters. Router I2C failures are silently ignored by mux selection. `amdgpu_i2c_destroy()` is declared in the header but not implemented in this file, so ownership is likely devm/device-lifecycle based elsewhere. Bus finalization only nulls array entries.

## Test signals
EDID reads on bit-bang and hardware buses, module parameter combinations, Polaris OEM I2C init, router mux selection for DDC and clock/data, concurrent transfers on one bus, transfer timeout behavior, and device removal/reprobe are relevant tests.
