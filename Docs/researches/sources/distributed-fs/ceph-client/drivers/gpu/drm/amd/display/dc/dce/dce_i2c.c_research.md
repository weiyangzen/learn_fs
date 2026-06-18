# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c.c

Purpose: provides the top-level DCE I2C dispatcher and OEM-I2C presence helper. It chooses hardware I2C when available and falls back to software GPIO bit-banging when the hardware engine is unavailable.

Important APIs and functions: `dce_i2c_oem_device_present()` checks BIOS firmware metadata for an OEM I2C object, fetches its I2C info through `dc_bios->funcs->get_i2c_info()`, and compares the slave address. `dce_i2c_submit_command()` validates inputs, attempts `acquire_i2c_hw_engine()`, submits through `dce_i2c_submit_command_hw()` on success, otherwise initializes a stack `struct dce_i2c_sw`, acquires the DDC in software mode, and submits through `dce_i2c_submit_command_sw()`.

Control flow: the dispatcher returns false on null DDC/command, uses the DDC's context/resource pool to find hardware engines, and only tries software acquisition after hardware acquisition fails. Hardware and software submission functions own release/close behavior after acquisition.

State and persistence: no persistent state is stored here. It creates a temporary software-engine struct and relies on lower layers to update hardware engine/DDC state and resource-pool flags.

Dependencies and integration: depends on `dce_i2c.h`, `dce_i2c_hw.h`, `dce_i2c_sw.h`, DC BIOS, resource pool, DDC service, and register/helper macros. It is the generic DC I2C entry point used by DDC/EDID and display-management flows.

Risks and test signals: risks are acquisition/release ownership mismatches between hardware and software paths, null `ddc->ctx` assumptions, and hardware fallback behavior when `pool->i2c_hw_buffer_in_use` is set. Test with hardware-supported DDC, hardware-busy fallback, invalid inputs, BIOS OEM I2C object present/missing, and repeated EDID reads after fallback.
