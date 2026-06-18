# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9611uxc.c

## Purpose

This file implements the Lontium LT9611UXC MIPI DSI to HDMI bridge. Compared with `lontium-lt9611.c`, more behavior is delegated to firmware; the driver mainly provides DSI attachment, fixed-mode validation, timing writes, HPD/EDID handling, HDMI audio notifications, and firmware update/readback through sysfs.

## Important APIs, Types, And Functions

`struct lt9611uxc` stores bridge state, regmap, `ocm_lock`, waitqueue/work item, DSI nodes/devices, GPIOs, regulators, HPD/EDID flags, HDMI connection state, and firmware version. `lt9611uxc_lock()` and `lt9611uxc_unlock()` stop/restart the on-chip MCU around register access by writing `0x80ee`.

The fixed mode table is `lt9611uxc_modes[]`; validation is `lt9611uxc_bridge_mode_valid()`. HDMI paths include detect, EDID wait/read, `hpd_notify`, and no-op audio prepare/shutdown. Firmware paths include `lt9611uxc_firmware_update()`, page read/write helpers, sysfs `lt9611uxc_firmware`, and automatic update when firmware version reads as zero.

## Control Flow

Probe validates I2C, allocates the bridge, initializes mutex/regmap, parses mandatory DSI0, optional DSI1, and output bridge, gets GPIOs/regulators, asserts optional 5V, powers and resets the chip, reads chip revision and firmware version, optionally updates firmware and retries version detection, initializes waitqueue/work, requests IRQ, sets bridge ops including HPD only for firmware version >= 0x40, adds the bridge, and attaches DSI devices.

IRQ handling locks the MCU, reads interrupt and HPD status, clears interrupt status, wakes EDID waiters on EDID-ready events, updates `hdmi_connected` and schedules HPD work on connect changes, then unlocks. EDID reads wait up to 500 ms for `edid_read`, then read one of two 128-byte blocks from internal memory. Mode set locks, writes timing registers, and unlocks.

Firmware update requests `lt9611uxc_fw.bin`, locks MCU, erases flash twice with long waits, writes 32-byte pages, reads back the image, compares it, unlocks, resets, and releases firmware.

## State And Persistence

`hdmi_connected` and `edid_read` are shared across IRQ, waitqueue, workqueue, detect, and EDID paths and are protected by `ocm_lock` when touching registers or shared connection state. Firmware writes persist in flash. `fw_version` is cached for sysfs display. DSI endpoint node references persist until remove. The driver does not perform detailed power state transitions on atomic enable/disable; firmware appears to manage most HDMI state.

## Dependencies And Integration Points

Dependencies include I2C/regmap, firmware loader, mutex/waitqueue/workqueue, IRQ, GPIO, regulators, OF graph, MIPI DSI, DRM bridge/EDID helpers, and HDMI audio notification helpers. It exposes `MODULE_FIRMWARE("lt9611uxc_fw.bin")` and a sysfs firmware attribute.

## Risks And Edge Cases

The firmware readback comparison appears inverted: `!memcmp(readbuf, fw->data, fw->size)` logs failure even when buffers match. EDID is only two blocks and depends on an interrupt-driven ready flag; stale `edid_read` state may affect later reads. HPD support depends on firmware version. Register access must consistently use MCU lock/unlock, and firmware update holds the MCU stopped for long erase/write periods. Mode support is a fixed whitelist. DSI lanes are fixed to 4.

## Test Signals

Test firmware version zero update path, manual sysfs update, readback comparison, HPD-supported and non-HPD firmware versions, EDID wait timeout and success, two-block EDID reads, fixed-mode whitelist rejection, DSI0-only and dual-DSI DTs, IRQ/workqueue teardown, HDMI audio plugged notifications, and regulator/GPIO/IRQ failure paths.
