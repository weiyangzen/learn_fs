# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/edid.h

## Purpose
`edid.h` defines the public data model and entry points for GVT EDID/I2C emulation. It describes the emulated EDID block, the GMBUS transaction state machine visible to GVT, the AUX channel state needed for I2C-over-AUX, and the functions called by MMIO/display emulation code.

## Important APIs, Types, And Constants
`EDID_SIZE` is fixed at 128 bytes and `EDID_ADDR` is the standard 7-bit EDID I2C address `0x50`. `struct intel_vgpu_edid_data` stores a validity flag and one EDID block. `enum gmbus_cycle_type` mirrors the GMBUS cycle encodings used by GMBUS1. `enum gvt_gmbus_phase` keeps only phases visible through GMBUS MMIO: idle, data, and wait. `struct intel_vgpu_i2c_gmbus` stores total byte count, cycle type, and phase. `struct intel_vgpu_i2c_aux_ch` tracks I2C-over-AUX MOT state. `enum i2c_state` distinguishes unspecified, GMBUS, and AUX flows. `struct intel_vgpu_i2c_edid` combines all per-vGPU EDID read state.

The exported functions are `intel_vgpu_init_i2c_edid()`, `intel_gvt_i2c_handle_gmbus_read()`, `intel_gvt_i2c_handle_gmbus_write()`, and `intel_gvt_i2c_handle_aux_ch_write()`.

## Control Flow And State
This header encodes the invariant that GMBUS and AUX EDID sequences cannot interleave. Callers are expected to initialize or reset `intel_vgpu_i2c_edid` when a new transaction starts, when a stop is observed, or when the emulated display path changes. The active state records selected port, whether the guest has addressed EDID, whether EDID is available on that port, and how many bytes have been consumed.

## Dependencies And Integration Points
The header is included by `gvt.h`, which embeds `struct intel_vgpu_i2c_edid` in `struct intel_vgpu_display`. It is also consumed by `edid.c` and any MMIO dispatcher that forwards GMBUS/AUX accesses. It only includes Linux basic types and forward-declares `struct intel_vgpu`, keeping the interface light.

## Risks And Test Signals
The state machine is intentionally minimal and exposes only the hardware phases the emulation uses. Any future extension for multi-block EDID, DDC segment addressing, or richer AUX behavior would need new fields and stricter sequencing rules. Tests should confirm state reset clears port, target, availability, byte cursor, GMBUS metadata, and AUX MOT flags.
