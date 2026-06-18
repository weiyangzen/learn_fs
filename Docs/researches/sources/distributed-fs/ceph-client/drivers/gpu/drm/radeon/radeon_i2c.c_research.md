<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_i2c.c

## Purpose

`radeon_i2c.c` implements Radeon display I2C/DDC plumbing for legacy and AtomBIOS-era hardware. It probes EDID over DDC or DP AUX, exposes software bit-banged GPIO adapters, selects pre-DCE hardware I2C engines where supported, delegates newer DCE3 hardware I2C to AtomBIOS helpers, registers default buses from AtomBIOS/COMBIOS tables, provides small byte read/write helpers, and programs external DDC/clock-data router muxes on connector paths.

## Important APIs, Types, and Functions

- `radeon_ddc_probe(struct radeon_connector *, bool use_aux)`: selects any DDC router port, performs a two-message EDID read at `DDC_ADDR`, and accepts the bus only when the EDID header has at least six valid leading bytes.
- Bit-bang callbacks `pre_xfer`, `post_xfer`, `get_clock`, `get_data`, `set_clock`, and `set_data`: claim GPIO pins through mask registers, reset problematic legacy hardware I2C state, switch DCE3 pads to DDC mode, and expose pin direction/value operations to `i2c-algo-bit`.
- `radeon_get_i2c_prescale()`: computes legacy hardware-I2C prescale values from `rdev->pm.current_sclk` for R100-R5xx families.
- `r100_hw_i2c_xfer()` and `r500_hw_i2c_xfer()`: program legacy and Avivo hardware I2C controller registers, including address/data FIFO writes, GO/DONE polling, abort handling, pin selection, BIOS scratch busy marking, and 15-byte chunking on R5xx.
- `radeon_hw_i2c_xfer()` / `radeon_hw_i2c_func()`: Linux `i2c_algorithm` hooks that dispatch by ASIC family and advertise normal I2C plus SMBus emulation.
- `radeon_i2c_create()`: chooses a hardware, AtomBIOS-backed, or bit-banged adapter from `struct radeon_i2c_bus_rec`, initializes `struct radeon_i2c_chan`, and registers it with the I2C core.
- `radeon_i2c_init()`, `radeon_i2c_fini()`, `radeon_i2c_add()`, and `radeon_i2c_lookup()`: populate and query `rdev->i2c_bus[]`.
- `radeon_i2c_get_byte()` / `radeon_i2c_put_byte()`: convenience single-register I2C transactions used by router and encoder code.
- `radeon_router_select_ddc_port()` and `radeon_router_select_cd_port()`: program external mux/router control registers through a router I2C bus.

## Control Flow

DDC probing starts by switching any connector router to the desired DDC lane. It then reads the first EDID block bytes through either the connector's DP AUX DDC adapter or normal I2C adapter. A failed two-message transfer or weak EDID header returns `false`; successful probing returns `true`.

For bit-banged transfers, `pre_xfer` serializes the channel with `i2c->mutex`, works around R200-R400 hardware I2C reset issues by selecting a harmless DVI I2C pin under `dc_hw_i2c_mutex`, switches pads and GPIO mask registers to software ownership, clears output values, and sets both clock/data as inputs. The bit algorithm then calls `set_*` and `get_*`; `post_xfer` unclaims GPIO masks and unlocks the bus.

Hardware transfers hold both `dc_hw_i2c_mutex` and `pm.mutex`, because controller timing depends on stable SCLK. R100/R3xx/R4xx code computes prescale and selects the right DDC pin encoding before issuing per-byte transactions. R5xx Avivo code additionally clears GPIO ownership, claims the Avivo I2C arbitration register, saves/restores controller state, and splits reads/writes into controller FIFO chunks. Both paths poll GO/DONE bits with microsecond delays and abort on error before restoring scratch/state.

Adapter creation is policy-driven. Multimedia I2C is exposed only when forced hardware I2C is enabled. Older ASICs and R5xx use the local hardware algorithms when allowed; DCE3 hardware-capable buses use AtomBIOS I2C callbacks; all other buses fall back to GPIO bit-banging.

## State and Persistence Behavior

Persistent state lives in `rdev->i2c_bus[]`, each `radeon_i2c_chan`'s copied bus record, Linux `i2c_adapter` registration, and connector router metadata. Transfer state is transient but mutates hardware GPIO masks, I2C controller registers, DDC pin routing, Avivo arbitration, and `RADEON_BIOS_6_SCRATCH` busy flags. Locks protect channel-local GPIO use, global display-controller hardware I2C use, and PM clock stability.

`radeon_i2c_fini()` only nulls array entries in this snapshot. Adapter lifetime is mostly delegated to devm registration for the legacy hardware path or normal I2C registration for Atom/bit paths; any lifecycle changes must preserve I2C core unregister semantics.

## Dependencies and Integration Points

This file depends on Linux I2C, `i2c-algo-bit`, DRM EDID validation, Radeon register macros, AtomBIOS hardware I2C callbacks declared in `atom.h`, `struct radeon_i2c_bus_rec` and `struct radeon_i2c_chan` from `radeon_mode.h`, BIOS connector parsing (`radeon_atombios_i2c_init` / `radeon_combios_i2c_init`), DP AUX DDC, and connector hotplug/mode-detect code. It interacts with PM (`rdev->pm.current_sclk`, `pm.mutex`) and BIOS scratch state visible to firmware.

## Risks and Edge Cases

- Several ASIC families are marked `todo` for local hardware I2C and currently fall through with success-like `ret = 0` in `radeon_hw_i2c_xfer()` unless another case sets an error, so adapter selection must avoid those paths or callers may see misleading transfers.
- Hardware polling loops can exit after timeout without explicitly checking that `DONE` was observed; a loop that runs to its bound without error status can still continue to cleanup with `ret == num`.
- Prescale calculation depends on `current_sclk`; stale PM state or missing PM locking would corrupt bus timing.
- GPIO and controller register save/restore is chipset-specific and easy to regress during register macro changes.
- `radeon_i2c_fini()` does not explicitly unregister non-devm adapters in this file, so lifetime relies on external cleanup paths or device teardown.
- Router byte helpers log failures but do not propagate errors, so mux selection failure may surface only as later DDC failure.

## Test Signals

Useful validation includes EDID probing over bit-banged DDC, hardware I2C, AtomBIOS I2C, and DP AUX; hotplug detection on connectors with DDC routers; forced `radeon_hw_i2c=1` on supported and unsupported ASICs; lockdep coverage around PM/I2C/display locks; fault injection for NACK/GO timeout/arbitration failure; suspend/resume ensuring scratch busy bits and saved Avivo registers are restored; and regression tests for shared DDC mux systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_i2c.c -->
