# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_combios.c

## Purpose

`radeon_combios.c` implements the legacy Radeon COMBIOS path for pre-AtomBIOS and compatibility hardware. It decodes legacy BIOS table offsets, builds DDC/I2C records, extracts PLL clocks, panel data, DAC/TMDS parameters, connector topology, power states, and thermal-controller hints, executes legacy ASIC/PLL/MMIO init scripts, and updates BIOS scratch registers so firmware and driver agree on display ownership and attachment state.

## Important APIs, Types, and Functions

- `combios_get_table_offset()` is the central COMBIOS table locator, resolving both absolute BIOS-header entries and relative offsets from misc, mobile, memory, and TMDS power tables.
- `radeon_combios_check_hardcoded_edid()` validates BIOS EDID blocks; `radeon_bios_get_hardcoded_edid()` returns duplicates for connector probing fallback.
- `combios_setup_i2c_bus()`, `radeon_combios_get_i2c_info_from_table()`, and `radeon_combios_i2c_init()` map legacy DDC IDs and ASIC-family GPIO quirks into Radeon I2C bus records.
- Clock/display data helpers include `radeon_combios_get_clock_info()`, `radeon_combios_get_primary_dac_info()`, `radeon_combios_get_tv_info()`, `radeon_combios_get_tv_dac_info()`, `radeon_combios_get_lvds_info()`, and TMDS/ext-TMDS helpers.
- Connector discovery is split between `radeon_get_legacy_connector_info_from_table()` for built-in platform tables and `radeon_get_legacy_connector_info_from_bios()` for packed BIOS connector records.
- `radeon_combios_get_power_modes()` creates simple default/battery power states, voltage GPIO metadata, PCIe lane hints, and optional thermal I2C clients.
- `radeon_combios_asic_init()` runs legacy ASIC/PLL/RAM init scripts through `combios_parse_mmio_table()`, `combios_parse_pll_table()`, `combios_parse_ram_reset_table()`, and `combios_write_ram_size()`.
- Scratch helpers maintain firmware-visible display status: `radeon_combios_initialize_bios_scratch_regs()`, `radeon_combios_output_lock()`, `radeon_combios_connected_scratch_regs()`, `radeon_combios_encoder_crtc_scratch_regs()`, and `radeon_combios_encoder_dpms_scratch_regs()`.

## Control Flow

Public helpers locate firmware tables with `combios_get_table_offset()` and decode fields through `RBIOS8/16/32`. I2C setup maps `DDC_*` values into register/mask pairs, applies family-specific remaps for ambiguous MONID/CRT2 lines, and creates or looks up Radeon I2C adapters. Clock and panel helpers populate `rdev->clock` or encoder-private LVDS/TMDS/DAC structures.

Connector discovery either selects a predefined platform connector table, including PowerMac/RN50/embedded cases, or walks BIOS connector entries. The BIOS path decodes connector type, DDC type, HPD, analog/digital device masks, dual-link hints, LVDS and TV supplemental tables, and PCI-ID quirks, then adds encoders/connectors and links them.

ASIC init is script-driven. The top-level init runs ASIC init 1, PLL init, ASIC init 2, optional non-IGP memory scripts, RAM reset, ASIC init 3/4, memory-size programming, and finally dynamic-clock programming unless a known RS4xx resume quirk skips it. Script interpreters perform direct MMIO/PLL writes, read-modify-write operations, delays, and polling loops.

## State and Persistence Behavior

The file persists decoded data into `rdev->i2c_bus[]`, `rdev->clock`, `rdev->mode_info`, encoder private data, `rdev->pm.power_state`, `rdev->pm.i2c_bus`, connector/encoder DRM objects, and BIOS scratch registers. Hardware programming through MMIO/PLL/I2C persists until reset, modeset, suspend/resume, or later display code changes it. Allocated DAC/LVDS/TMDS/power-state structures are handed to broader Radeon lifecycle code.

## Dependencies and Integration Points

This code depends on DRM EDID and mode structures, Radeon register/BIOS access macros, ASIC family predicates, Atom connector/device constants reused by legacy paths, Radeon I2C helpers, legacy encoder/connector constructors, kernel I2C client registration, and optional PowerPC Open Firmware machine matching.

## Risks and Edge Cases

- BIOS table offsets and sentinel-terminated scripts are mostly trusted and have limited ROM-length bounds checking.
- Board-specific PCI and platform quirks are fragile; missing or wrong quirks can produce phantom outputs or broken resume.
- ASIC init scripts write MMIO, PLL, memory-controller, and aperture locations directly; malformed firmware can hang or misprogram hardware.
- Connector fallback heuristics intentionally infer VGA/DVI/LVDS/TV outputs from partial BIOS data, which can expose nonexistent ports.
- Power-mode allocation failure paths leave cleanup to the broader driver lifecycle.
- External TMDS setup depends on correct I2C bus discovery and firmware script IDs; failures may silently leave a digital output unusable.

## Test Signals

Good coverage would include invalid/missing COMBIOS tables, EDID validation failure, DDC mapping by ASIC family, platform connector-table selection, BIOS connector parsing, dual-link detection, LVDS native-mode extraction, PowerPlay/thermal table parsing, ASIC script execution on known boards, RS4xx resume quirk skips, and BIOS scratch changes after connector status/DPMS/CRTC updates.
