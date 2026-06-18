# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nxp-ptn3460.c

## Purpose

This file implements the NXP PTN3460 eDP-to-LVDS bridge. It controls powerdown/reset GPIOs, selects one of the chip's EDID emulation entries, reads EDID over I2C, optionally creates an LVDS connector, and attaches a downstream panel bridge.

## Important APIs, Types, And Functions

`struct ptn3460_bridge` contains a connector, I2C client, DRM bridge, panel bridge, powerdown/reset GPIOs, selected EDID emulation index, and an `enabled` flag. Low-level accessors are `ptn3460_read_bytes()` and `ptn3460_write_byte()`. `ptn3460_select_edid()` loads the selected EDID into SRAM and enables emulation. Bridge callbacks are `ptn3460_pre_enable()`, `ptn3460_disable()`, `ptn3460_bridge_attach()`, and `ptn3460_edid_read()`.

## Control Flow

Probe wraps the downstream bridge from DT port 0 endpoint 0, acquires powerdown and reset GPIOs, reads the required `edid-emulation` property, sets bridge EDID op/type/of_node, adds the bridge, and stores client data. Pre-enable powers the chip, pulses reset, waits 90 ms to avoid false HPD, selects EDID, and marks enabled. Disable marks disabled, asserts reset high, and powers down. EDID read temporarily powers the bridge if needed, reads one 128-byte EDID block from address 0, allocates a DRM EDID object, and powers off again if it was originally off.

## State And Persistence

`enabled` tracks whether GPIO power sequencing has completed. The selected EDID emulation persists in chip registers/SRAM while powered. The driver does not manage regulators; board power is represented through GPIOs. Connector state exists only if the driver creates a connector during attach.

## Dependencies And Integration Points

Dependencies include I2C master send/receive, GPIO, OF properties, DRM bridge/connector/EDID helpers, and `devm_drm_of_get_bridge()` for the downstream panel. It integrates as an LVDS connector/bridge in the DRM chain.

## Risks And Edge Cases

Only a single EDID block is read; extension blocks are not supported. The `edid-emulation` property is not range-checked against chip-supported entries. `gpiod_set_value()` is used rather than cansleep variants, so GPIO provider context matters. Attach registers a connector manually when not connectorless and triggers an HPD helper event. Power sequencing delays are fixed from datasheet assumptions.

## Test Signals

Test EDID emulation indices, missing property, GPIO failures, connectorless and connector-owning attach, EDID read while off/on, false HPD timing, remove after connector registration, and I2C transfer errors.
