# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt8713sx.c

## Purpose

This file implements a Lontium LT8713SX DRM bridge driver. Display-side bridge behavior is intentionally simple: it attaches a downstream bridge found from DT port 1 and advertises a DisplayPort connector type. Most file complexity is a sysfs-triggered firmware updater for the bridge's internal flash, including firmware loading, CRC preparation, SRAM staging, flash erase/write, and post-write CRC checks.

## Important APIs, Types, And Functions

`struct lt8713sx` stores the DRM bridge, next bridge, 16-bit paged regmap, `ocm_lock`, reset and enable GPIOs, firmware pointers/buffer, main CRC, bank CRC values, and bank count. `lt8713sx_regmap_config` exposes a 0x0000-0xffff logical register space through page register `0xff` and disables caching.

Firmware functions include `lt8713sx_prepare_firmware_data()`, `lt8713sx_firmware_update()`, `lt8713sx_firmware_upgrade()`, `lt8713sx_block_erase()`, `lt8713sx_write_data()`, `lt8713sx_load_main_fw_to_sram()`, `lt8713sx_load_bank_fw_to_sram()`, and result check helpers. The sysfs attribute is `lt8713sx_firmware` via `DEVICE_ATTR_WO()`. Bridge integration is `lt8713sx_bridge_attach()`.

## Control Flow

Probe validates I2C, allocates the bridge, initializes `ocm_lock` and regmap, finds the downstream panel/bridge on port 1, acquires reset/optional enable GPIOs, enables `vdd` then `vcc`, resets the chip, registers the bridge, and populates the CRC8 table.

Writing the sysfs attribute calls `lt8713sx_firmware_update()`: take `ocm_lock`, stop/enable host I2C access to the on-chip MCU, request `lt8713sx_fw.bin`, allocate a 256 KiB padded buffer, copy main firmware and bank firmware, append/compute CRCs, configure flash parameters, erase eight 32 KiB blocks, write 256-byte pages through SRAM to flash, validate main and bank CRCs by loading flash regions back to SRAM, disable I2C access, reset on success, and release firmware/buffer.

## State And Persistence

Firmware bytes are transient in `fw_buffer`, but successful writes persist in the chip's flash. `ocm_lock` serializes all register accesses that require stopping the on-chip MCU. Regmap has no cache, which is appropriate for firmware command/status registers. Regulators and GPIO state are device-managed; the optional enable GPIO is acquired high and not otherwise toggled after probe.

## Dependencies And Integration Points

The driver depends on I2C, firmware loading, CRC8, regmap, mutex guards, GPIO, regulators, DRM bridge, and OF graph bridge lookup. It exposes `MODULE_FIRMWARE("lt8713sx_fw.bin")`. The display pipeline depends on a downstream bridge/panel; no mode callbacks, EDID, HPD, or bus-format negotiation are implemented locally.

## Risks And Edge Cases

Firmware preparation assumes a main area of 64 KiB and bank granularity of 12 KiB. There is a potential boundary risk because `bank_crc_value` has 17 entries but firmware size checks allow nearly 256 KiB. Many low-level `regmap_write()` calls are unchecked, so flash operation failures may be detected only by CRC logging, and CRC mismatch helpers do not convert mismatch into a failing return. `lt8713sx_block_erase()` stops polling after a fixed count but does not report timeout. Sysfs update is a privileged destructive operation that can leave flash partially rewritten after power loss or I2C errors.

## Test Signals

Validate build coverage, DT probe, regulator/GPIO failures, bridge chaining, sysfs firmware update success/failure paths, missing/oversized firmware, flash busy timeout behavior, CRC mismatch handling, reset after update, repeated sysfs updates, and display operation before/after firmware update.
