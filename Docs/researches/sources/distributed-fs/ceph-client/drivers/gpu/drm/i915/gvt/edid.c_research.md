# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/edid.c

## Purpose
`edid.c` emulates the I2C paths a guest display driver uses to read monitor EDID data from an Intel GVT vGPU. It handles two transport styles: legacy GMBUS MMIO registers for non-DP ports and I2C-over-AUX transactions for DP ports. The file translates guest register writes into updates of `vgpu->display.i2c_edid`, returns bytes from the configured virtual port EDID block, and mirrors enough GMBUS/AUX status bits in vGPU virtual MMIO to make the guest driver believe hardware completed the transaction.

## Important APIs, Functions, And Types
The exported entry points are `intel_gvt_i2c_handle_gmbus_read()`, `intel_gvt_i2c_handle_gmbus_write()`, `intel_gvt_i2c_handle_aux_ch_write()`, and `intel_vgpu_init_i2c_edid()`. Internal helpers include `edid_get_byte()` for bounds-checked EDID byte consumption, platform pin decoders for BXT/CNP/default GMBUS0 layouts, `reset_gmbus_controller()`, and per-register emulators for GMBUS0 through GMBUS3. The implementation depends on the EDID state structs declared in `edid.h`, display port helpers such as `intel_vgpu_has_monitor_on_port()`, `intel_vgpu_port_is_dp()`, and virtual register access through `vgpu_vreg()`/`vgpu_vreg_t()`.

## Control Flow
For GMBUS, a guest first writes GMBUS0. `gmbus0_mmio_write()` stores the value, resets EDID state, decodes the selected pin to a GVT port, marks the state as `I2C_GMBUS`, and sets `edid_available` only if a monitor exists on a non-DP port. A later GMBUS1 write parses target address, byte count, index, and cycle type. EDID address `0x50` selects the target, index cycles set `current_edid_read`, stop cycles reset state, and data cycles move the GMBUS emulation to active/data phase. GMBUS3 reads then pack up to four EDID bytes into the data register and advance the current read cursor; the final read moves the emulation to wait or idle and reinitializes the high-level EDID state.

For AUX, `intel_gvt_i2c_handle_aux_ch_write()` only interprets writes to AUX control. It reads the AUX message from the following DATA register, decodes the target address and operation, synthesizes DONE plus reply size in AUX control, and places an ACK or one EDID byte in AUX data. Message length 3 is treated as start/restart/stop selection, while length 4 plus read opcode returns a byte. Non-control AUX data writes are simply mirrored into virtual MMIO.

## State And Persistence
State is entirely per-vGPU and transient: `state`, `port`, `target_selected`, `edid_available`, `current_edid_read`, GMBUS phase/cycle metadata, and AUX MOT flags live in `vgpu->display.i2c_edid`. EDID contents are stored on the selected virtual display port, not in this file. The emulation also persists protocol-visible status in virtual GMBUS/AUX MMIO registers. There is no on-disk persistence.

## Dependencies And Integration Points
This file integrates with the GVT MMIO dispatcher for GMBUS register reads/writes and with display register emulation for AUX writes. It depends on i915 display register definitions, DP AUX constants, platform checks (`IS_BROXTON`, `IS_COFFEELAKE`, `IS_COMETLAKE`), and GVT display configuration that supplies monitor presence and EDID blocks.

## Risks And Edge Cases
The logic intentionally supports only EDID reads. Unsupported target addresses are logged and ignored, GMBUS3 writes warn, and AUX write operations are mostly ignored. Protocol ordering matters: `edid_get_byte()` returns zero and logs if the guest reads before target selection, after the 128-byte block, or without available EDID. Port-pin mappings are platform-specific and stale mappings can break hotplug/EDID discovery. Partial or unusual guest I2C sequences may observe simplified status behavior because the implementation collapses hidden hardware phases.

## Test Signals
Useful validation includes guest boot/display probing on HDMI and DP virtual ports, EDID block reads of exactly 128 bytes, index-mode reads, stop/restart behavior, no-monitor reads producing error status, and DP AUX I2C-over-AUX reads returning ACK plus byte data. Kernel logs should be checked for `gvt_vgpu_err()` warnings about improper sequences, unsupported target addresses, or missing EDID.
