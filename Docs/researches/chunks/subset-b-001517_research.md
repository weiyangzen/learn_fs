# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h lines 15236-17567

## Purpose

This chunk is the tail of the generated AMD DCE 11.0 shift/mask header. It defines the bitfield masks and shifts used to compose and decode display-controller MMIO register values for the final DCE register groups in the file, then closes the `DCE_11_0_SH_MASK_H` include guard.

The covered range spans several hardware blocks:

- `DISP_INTERRUPT_STATUS_CONTINUE3` through `DISP_INTERRUPT_STATUS_CONTINUE10`, which extend the display interrupt-status chain for later CRTC/DIG/AUX/HPD/perfmon events.
- DCO memory-power, clock-gating, soft-reset, stereo-sync, debug, and power-management fields.
- DC I2C and Generic I2C/DDC control, status, transaction, speed, setup, interrupt, pin, and EDID-detection fields.
- `BLNDV_*` virtual blender controls and `CRTCV_*` virtual CRTC timing, status, trigger, stereo, CRC, test-pattern, update-lock, vertical-interrupt, and GSL synchronization fields.
- `XDMA_*` display cross-DMA master/slave, tiling, interrupt, power, debug, performance, cache, surface-address, urgent/stall, nack, and read-latency fields.

The file does not implement behavior directly. Its purpose is to keep register field layout in one generated source of truth so AMDGPU display code can avoid hard-coded bit constants at call sites.

## Important APIs, Types, And Functions

There are no C functions, structs, or runtime types in this chunk. The exported interface is preprocessor constants following the generated AMD register-header convention:

- `REGISTER__FIELD_MASK` gives the packed bit mask for a field in a 32-bit register value.
- `REGISTER__FIELD__SHIFT` gives the right-shift amount for that same field.

Important macro families include:

- `DISP_INTERRUPT_STATUS_CONTINUE*__*`: status bits for chained display interrupts, including mode-change, blender underflow, line-buffer vline/vblank, CRTC snapshot/trigger/vsync/vertical interrupts, DisplayPort fast-training and stream-disable events for DIGE/DIGF/DIGG/DIGLPA/DIGLPB, HPD/AUX events, GTC sync lock/error events, BUFMGR interrupts, DCCG/DCI/DCO/DCFE/WB perfmon counter interrupts, and continuation bits linking status registers 4 through 10.
- `DCO_MEM_PWR_STATUS*`, `DCO_MEM_PWR_CTRL*`, `DCO_CLK_CNTL*`, `DCO_SOFT_RESET`, `DIG_SOFT_RESET*`: DCO memory power-state and force/disable controls, clock gate-disable bits for display, AFMT, TMDS, DIG, and low-power DIG clocks, plus reset bits for DCO, DIG front/back ends, audio, formatter, MVP, ABM, DVO, and DP debug blocks.
- `DPDBG_*`, `DCO_POWER_MANAGEMENT_CNTL`, `DCO_TEST_DEBUG_*`: DisplayPort debug, DCO power-management, and indexed debug-data fields.
- `DC_I2C_*`: the main display I2C/DDC engine fields, including transaction start/stop/read-write/count descriptors, DDC1-DDC6 and DDCVGA status/setup/speed fields, software and hardware completion interrupts, EDID detection control, arbitration between software and DMCU/hardware users, indexed data FIFO access, and read-request interrupt acknowledgment/masking.
- `GENERIC_I2C_*`: a second generic I2C engine with go/reset/enable, completion and DDC read-request interrupts, status/error bits, speed/setup/transaction/data fields, and pin selection/debug controls.
- `BLNDV_*`: virtual blender gain, blend mode, stereo mode, alpha mode, feedthrough, update lock/status, underflow interrupt, debug, and test-debug fields.
- `CRTCV_*`: virtual CRTC timing registers for totals, blanking, syncs, VBI, vertical total min/max control, nominal-vsync and vertical-update interrupts, trigger A/B controls, force-count/force-vsync controls, stereo and AV sync, master enable, blank/interlace/field status, pixel readback, counters, snapshot, double buffering, test patterns, CRC windows/data, static-screen detection, GSL synchronization, color constants, vertical interrupt windows, and debug access.
- `XDMA_*`: XDMA MC/PCIe client config, local tiling, interrupts, clock/memory power, BIF/status/error, RBBMIF timeout, power-gating mailbox/status, always-on debug, master and slave enable/reset/status, surface addresses and dimensions, local/remote/cache base addresses, urgent/stall tuning, nack clearing, GSL checks, cache and pipe control, performance measurement, latency accounting, and slave channel/remote GPU address fields.
- `#endif /* DCE_11_0_SH_MASK_H */`: closes the header guard opened at the top of the file.

The matching register-address constants live in `dce_11_0_d.h` as `mmDCO_MEM_PWR_CTRL`, `mmDC_I2C_CONTROL`, the `mmCRTCV_*` sequence, and the corresponding `mmXDMA_*` entries. This chunk provides field layout; the companion `_d.h` header provides register offsets.

## Control Flow

This header has no executable control flow. Its operational flow is compile-time expansion:

1. A DCE 11.0 display implementation includes the generated register offset and shift/mask headers.
2. The implementation chooses an MMIO register offset from `dce_11_0_d.h`.
3. It clears, inserts, or extracts a field using the `*_MASK` and `*__SHIFT` constants from this header.
4. The composed value is passed to an AMDGPU register access helper, or a read value is decoded into driver state.

The chunk also describes implicit hardware control sequences. For I2C/DDC, callers typically program speed/setup and transaction fields, write data/index fields, assert `*_GO`, then poll or handle done/status/error bits. For CRTC and blender changes, callers can use update-lock and double-buffer fields so timing-sensitive changes land during a safe update point. For XDMA, callers configure memory clients, tiling, surface addresses, dimensions, cache/pipe state, urgent levels, and enable/reset bits before observing active/flush/flip/status fields.

## State And Persistence Behavior

The macros store no software state. Hardware state changes only when other driver code uses these definitions to read or write DCE registers.

Stateful hardware surfaces represented here include:

- Interrupt status, mask, type, clear, and acknowledge bits. Some fields are latched until an explicit clear or ACK bit is written.
- DCO and XDMA clock-gating, memory-power, power-gating, and reset controls. These persist in the display block until reprogrammed or reset.
- DC I2C and Generic I2C transaction state, including pending requests, done bits, abort/timeout/NACK status, hardware DDC request ownership, EDID-detection counters, and indexed data FIFO contents.
- CRTC timing registers, counters, trigger occurrence bits, stereo/3D state, CRC configuration/data, static-screen status, vertical interrupt positions, and update-lock/double-buffer state.
- XDMA master/slave state such as enable/reset, surface addresses, pitches, cache settings, active/flush/flip-pending flags, urgent/stall controls, nack tags, latency counters, and performance measurement counters.

Because this is a generated bit-layout header, persistence correctness depends on synchronization with the ASIC register database. A stale field definition compiles cleanly but can cause a caller to corrupt adjacent hardware fields.

## Dependencies

The chunk depends on the surrounding AMDGPU generated register ecosystem:

- The file-level license and `DCE_11_0_SH_MASK_H` include guard defined earlier in `dce_11_0_sh_mask.h`.
- Register-address definitions in `drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h`.
- AMDGPU display register helper conventions that pair `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` constants with read/modify/write helpers.
- DCE 11.0 hardware semantics for display interrupts, DCO power and clocks, I2C/DDC engines, virtual CRTC/blender pipelines, and XDMA.
- Higher-level display code responsible for choosing legal timing, I2C, power, reset, and DMA values before writing registers.

There are no direct Linux kernel library dependencies in this chunk beyond the C preprocessor.

## Integration Points

These definitions integrate with DCE 11.0 display bring-up, modeset, interrupt handling, hotplug/DDC, diagnostics, and low-level register programming.

Important integration paths are:

- Display interrupt dispatch can decode continuation status bits to route CRTC, HPD, AUX, DisplayPort, perfmon, GTC sync, BUFMGR, and XDMA events.
- DCO power-management code can gate or ungate clocks, force memory states, assert resets, and inspect power status when enabling or suspending display blocks.
- I2C/DDC code can program DDC bus timing, select DDC instances, issue multi-transaction transfers, read EDID-detection state, and handle read-request or done interrupts.
- CRTC programming code can set virtual timing, sync, blanking, total-min/max, trigger, stereo, CRC, test-pattern, color, and update-lock fields during modeset and validation.
- XDMA code can configure cross-GPU/display DMA surfaces, memory client attributes, local tiling, cache, master/slave channels, urgent watermarks, and performance diagnostics.
- The final `#endif` makes this chunk structurally important to every translation unit including `dce_11_0_sh_mask.h`; a truncation here breaks the generated header globally.

## Risks And Edge Cases

- Incorrect masks or shifts silently target the wrong hardware bits. This is especially risky for packed control registers such as `DCO_CLK_CNTL*`, `CRTCV_INTERRUPT_CONTROL`, `DC_I2C_READ_REQUEST_INTERRUPT`, and `XDMA_MSTR_PIPE_CNTL`.
- Several fields use high bits, including `0x80000000` masks. Callers must compose values using unsigned 32-bit operations to avoid sign-extension or overflow bugs.
- Fields with names ending in `_MASK_MASK` represent a hardware field whose name includes `MASK`, not a duplicate typo. Callers and scripts should not normalize these away.
- Interrupt fields often split occurrence/status, mask, type, ack, and clear bits. Writing a clear or ACK bit when trying to set a mask can lose events.
- DCO clock-gate and reset fields can disable clocks or reset active display sub-blocks. Ordering with modeset, audio, DisplayPort, and I2C activity matters.
- I2C/DDC fields include arbitration with DMCU/hardware users and status reset/abort controls. Misusing ownership or abort bits can hang EDID or AUX/DDC flows.
- CRTC timing fields commonly use 14-bit coordinate/count fields. Values must be range-checked by higher-level timing code before shifting into these masks.
- Update-lock and double-buffer fields can leave pending changes unapplied if locks are not released, or can tear timing changes if bypassed at the wrong time.
- XDMA surface address, pitch, tiling, VMID/privilege, urgent, nack-clear, and cache invalidation fields affect memory access. Bad values can produce display corruption, bus errors, or hard-to-debug cross-GPU transfer failures.
- This chunk starts in the middle of the `DISP_INTERRUPT_STATUS_CONTINUE3` register family and is the last chunk of the file. Per-file reconciliation should combine it with previous chunks for a complete interrupt-map view.

## Test Signals

Useful validation signals are mostly build-time, static, and hardware integration checks:

- Kernel or driver builds including `dce_11_0_sh_mask.h` should pass without unterminated include-guard, duplicate macro, or missing macro errors.
- Generated-header validation should compare this chunk against the DCE 11.0 register database and the companion `dce_11_0_d.h` offsets.
- Static checks can verify each `REGISTER__FIELD_MASK` has a matching `REGISTER__FIELD__SHIFT`, that masks do not overlap unexpectedly within a register, and that continuation interrupt bits progress consistently.
- Register read/modify/write unit tests or bring-up diagnostics should confirm that setting one field changes only its masked bits.
- Display hotplug and EDID tests should exercise `DC_I2C_*`, `GENERIC_I2C_*`, DDC read-request interrupts, NACK/timeout handling, and EDID-detection status.
- Modeset and vblank/vertical-interrupt tests should exercise `CRTCV_*` timing, update-lock, vertical interrupt, snapshot, trigger, and vsync status paths.
- CRC and test-pattern validation should observe stable `CRTCV_CRC*` data and expected test output when corresponding fields are programmed.
- Power-management tests should suspend/resume display while checking DCO memory/clock/reset state and ensuring no lost HPD/AUX/CRTC interrupts.
- XDMA diagnostics should validate master/slave enable, address, pitch, tiling, cache invalidate, urgent interrupt, nack-clear, latency, and performance-measurement behavior on ASICs that use these registers.
