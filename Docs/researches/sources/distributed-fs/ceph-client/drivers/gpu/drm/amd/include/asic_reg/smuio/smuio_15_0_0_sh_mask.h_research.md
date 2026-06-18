# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_0_sh_mask.h

## Purpose

`smuio_15_0_0_sh_mask.h` is the generated SMUIO 15.0.0 field-layout companion to `smuio_15_0_0_offset.h`. It defines shifts and masks for misc, reset, TSC, and software timer registers. It is declarative register ABI data only; there are no C functions, local variables, structs, function pointers, or executable statements.

The local AMDGPU integration point is `amdgpu/smuio_v15_0_0.c`, which includes this header with the offset file. That C file currently uses only the TSC count offsets directly, but this mask header provides the field definitions needed by any SMUIO 15.0.0 code using `REG_GET_FIELD` and `REG_SET_FIELD`.

## Important APIs, types, and macro families

The misc block defines `SMUIO_MCM_CONFIG`, `IP_DISCOVERY_VERSION`, scratch registers 0 through 7, and `IO_SMUIO_PINSTRAP`. In this generation, `SMUIO_MCM_CONFIG` exposes `DIE_ID`, `PKG_TYPE`, `SOCKET_ID`, `CONSOLE_K`, `CONSOLE_A`, and `PKG_SUBTYPE`. Notably, `PKG_TYPE` occupies mask `0x0000003c`, `SOCKET_ID` is a single bit at mask `0x00000100`, and `PKG_SUBTYPE` is at bit 18. These layouts differ from older generated files and must be paired with 15.0.0 consumers.

The pinstrap register defines audio port connection and audio strap fields. Scratch registers and IP discovery are full-width values. The scratch registers form a simple 8-word MMIO scratchpad surface that firmware and driver paths may use depending on platform policy.

The reset block defines `SMUIO_GFX_MISC_CNTL` with `SMU_GFX_cold_vs_gfxoff` and `PWR_GFXOFF_STATUS` fields. The status field spans mask `0x00000006`, so consumers should decode it as a small value rather than a single Boolean unless a specific bit is intended.

The TSC block defines the same timebase register fields as neighboring SMUIO generations: pre/post PWROK reference-clock gap cycles, 24-bit upper and 32-bit lower golden TSC increment halves, 24-bit upper and 32-bit lower count halves, SOC golden TSC shadow halves, and a one-bit SOC gap power-good field.

The software timer block defines `PWR_VIRT_RESET_REQ`, display timer 1 and 2 control/debug/elapsed-control registers, global timer control, and `PWR_IH_CONTROL`. Control registers expose a 25-bit interrupt count plus enable, disable, mask, status-ack, type, and mode bits. Debug registers expose running, status, interrupt, and run-value fields. The elapsed-control registers expose a 25-bit elapsed-time count and comparison-enable bit. `PWR_IH_CONTROL` defines max credit, display timer trigger masks, display timer 2 trigger masks, and clock-gate enable.

## Control flow

The header itself has no control flow. Consumer control flow comes from MMIO read/modify/write and polling logic. For example, a timer handler can read a control/debug register, use these masks to test status, acknowledge with the `DISP_TIMER_INT_STAT_AK` field, and configure the next count. A reset path can set the VF or PF FLR request bits in `PWR_VIRT_RESET_REQ`. A platform-identification path can read `SMUIO_MCM_CONFIG` and branch on die, package, socket, console, or subtype fields.

## State and persistence behavior

This file describes persistent and live hardware register state. `SMUIO_MCM_CONFIG`, pinstrap, and IP discovery are identity/configuration state. Scratch registers can persist driver/firmware scratch values across portions of initialization until reset or overwrite. `SMUIO_GFX_MISC_CNTL` exposes GFXOFF-related state. TSC registers are live counters and increment configuration. Timer registers hold programmed interrupt counts, elapsed counts, modes, masks, status, acknowledge state, and trigger routing. `PWR_VIRT_RESET_REQ` carries reset request bits that may be consumed asynchronously by hardware or firmware.

The file cannot encode whether fields are read-only, write-one-to-clear, sticky, or reserved. Because timer and reset registers are side-effect sensitive, callers must use the documented SMUIO programming sequence, not just raw mask manipulation. For TSC reads, consumers must avoid torn high/low reads; the local `smuio_v15_0_0_get_gpu_clock_counter()` implements the usual high-low-high sequence.

## Dependencies and integration points

The header depends on the generated offset map for SMUIO 15.0.0 and the AMDGPU register helper macros that concatenate register and field names inside `REG_GET_FIELD` and `REG_SET_FIELD`. It integrates with ASIC-specific SMUIO callback setup, power-management and GFXOFF code, reset/virtualization flows that request PF/VF FLR, display/power timer interrupt routing, and platform topology discovery.

It is important that code using `SMUIO_MCM_CONFIG` field names be generation-aware. Other local SMUIO files expose topology or package fields differently, and `smuio_v15_0_8.c` expects a `TOPOLOGY_ID` field in its own matching mask file. This 15.0.0 mask file does not define that field.

## Risks

The largest risk is generation mismatch. A caller built against this file but using 15.0.8 or 14.0.2 offsets could write timer elapsed-control fields into a different register or decode package/socket bits incorrectly. Conversely, code copied from `smuio_v15_0_8.c` that expects `SMUIO_MCM_CONFIG__TOPOLOGY_ID` would not compile with this header and should not be papered over with hard-coded masks unless the hardware spec confirms them.

Timer registers have many adjacent one-bit controls near the high end of the word. Off-by-one shifts can enable instead of disable, mask instead of acknowledge, or configure interrupt type/mode incorrectly. `PWR_VIRT_RESET_REQ` divides VF and PF FLR bits across a broad mask and bit 31; wrong writes here can request resets for the wrong function. `PWR_IH_CONTROL` clock gating and trigger masks affect interrupt delivery, so reserved-bit writes may cause lost or spurious power/display timer events.

## Test signals

Compile tests should cover all 15.0.0 SMUIO consumers and any code using `REG_GET_FIELD(data, SMUIO_MCM_CONFIG, ...)` with this header. Runtime tests should verify monotonic TSC reads, correct `SMUIO_MCM_CONFIG` decode for die/package/socket/subtype, and expected GFXOFF status decoding. Timer validation should program display timer counts and elapsed comparisons, observe interrupt/debug status, acknowledge status, and verify `PWR_IH_CONTROL` routing.

Reset validation should exercise PF/VF FLR paths on hardware or simulation that exposes `PWR_VIRT_RESET_REQ`. Generated-header validation should compare every shift and mask against the SMUIO 15.0.0 register database and should specifically check fields whose positions differ from 14.0.2 or 15.0.8.
