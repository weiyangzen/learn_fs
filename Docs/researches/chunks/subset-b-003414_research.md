# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_sh_mask.h lines 4455-4866

## Scope

This chunk is the tail of the generated SMU 7.1.1 shift/mask header. It covers the final display power timer fields, VDDGFX idle-detection fields, LCAC memory/controller counter fields, ROM and ROM software-command register fields, current power-gating status masks, and the closing `SMU_7_1_1_SH_MASK_H` include guard.

The file is not executable driver logic. It is a hardware register metadata header: each `*_MASK` constant identifies writable or readable bits in a 32-bit SMU register, and each matching `*__SHIFT` constant gives the low bit for that field. The sibling address header `smu_7_1_1_d.h` supplies the corresponding `ix*` and `mm*` register addresses.

## Purpose

The chunk lets AMDGPU and PowerPlay code program SMU 7.1.1 registers without hard-coding bit positions at every call site. It documents several hardware blocks:

- `PWR_DISP_TIMER_5_CONTROL` through `PWR_DISP_TIMER_15_CONTROL`, plus `PWR_DISP_TIMER_CONTROL2`, for display-related interrupt timer setup and status.
- `VDDGFX_IDLE_PARAMETER`, `VDDGFX_IDLE_CONTROL`, and `VDDGFX_IDLE_EXIT`, for graphics-voltage idle thresholding, detection, SMC idle-state visibility, forced exit, and BIF exit requests.
- `LCAC_MC0..MC3_*` and `LCAC_CPL_*`, for load/current activity counter controls and override registers.
- `ROM_SMC_IND_INDEX/DATA`, `ROM_CNTL`, `PAGE_MIRROR_CNTL`, `ROM_STATUS`, `CGTT_ROM_CLK_CTRL0`, `ROM_INDEX`, `ROM_DATA`, `ROM_START`, `ROM_SW_CNTL`, `ROM_SW_STATUS`, `ROM_SW_COMMAND`, and `ROM_SW_DATA_1..64`, for SMU-side ROM access, SPI timing/control, page mirroring, and bulk software-command payloads.
- `CURRENT_PG_STATUS__VCE_PG_STATUS_MASK` and `CURRENT_PG_STATUS__UVD_PG_STATUS_MASK`, for checking whether video encode/decode engines are power-gated before touching their clock-gating registers.

## Important Symbols

The display timer controls repeat the same layout for timers 6 through 15, with this chunk also completing timer 5:

- `DISP_TIMER_INT_COUNT` uses bits 0-24 where present.
- `DISP_TIMER_INT_ENABLE` is bit 25.
- `DISP_TIMER_INT_RUNNING` is bit 26.
- `DISP_TIMER_INT_MASK` as a field/control bit appears at bit 27, while the generated macro names include both `..._INT_MASK_MASK` and `..._INT_MASK__SHIFT`.
- `DISP_TIMER_INT_STAT`, `DISP_TIMER_INT_STAT_AK`, and `DISP_TIMER_INT` occupy bits 28, 29, and 30.
- `PWR_DISP_TIMER_CONTROL2__DISP_TIMER_PULSE_WIDTH_MASK` is a 10-bit pulse-width field at bits 0-9.

The VDDGFX idle group defines a 16-bit threshold, a 4-bit threshold unit, an enable bit, a detection bit, a forced-exit bit, an SMC state bit, and `VDDGFX_IDLE_EXIT__BIF_EXIT_REQ_MASK`.

Each LCAC control register has the same shape: enable at bit 0, threshold in bits 1-16, block id in bits 17-21, and signal id in bits 22-29. Each `OVR_SEL` and `OVR_VAL` register is a full 32-bit field.

The ROM group includes:

- Full-width indirect index/data fields for `ROM_SMC_IND_INDEX` and `ROM_SMC_IND_DATA`.
- `ROM_CNTL` fields for SCK overwrite, clock gating, chip-select setup/hold timing, and SCK prescale values for refclk and crystal clock.
- `PAGE_MIRROR_CNTL` fields for base address, invalidate, enable, and usage.
- `ROM_STATUS__ROM_BUSY_MASK`, ROM clock-gating delay/hysteresis/override fields, 24-bit `ROM_INDEX` and `ROM_START`, and full-width `ROM_DATA`.
- `ROM_SW_CNTL` data size, command size, and return-data enable; `ROM_SW_STATUS__ROM_SW_DONE_MASK`; `ROM_SW_COMMAND` instruction and 24-bit address fields; and 64 full-width `ROM_SW_DATA_N` payload registers.

## APIs, Types, and Functions

This chunk defines no C functions, structs, enums, or runtime APIs. Its API surface is the set of preprocessor constants exported to AMDGPU code that includes the generated ASIC register headers.

The symbols are normally paired with address definitions from `smu_7_1_1_d.h`. For example, the address header maps `ixPWR_DISP_TIMER_5_CONTROL` through `ixPWR_DISP_TIMER_15_CONTROL`, `ixVDDGFX_IDLE_*`, `ixLCAC_*`, `ixROM_CNTL`, `ixROM_SW_*`, and `ixCURRENT_PG_STATUS` to SMU indirect register addresses. Runtime code then uses helpers such as `RREG32_SMC`, `WREG32_SMC`, `cgs_read_ind_register`, or `cgs_write_ind_register` to access those registers.

These constants are hardware ABI definitions. A value change is not a local refactor; it changes how the driver encodes or decodes hardware state.

## Control Flow

The header itself has no control flow beyond the include guard. Runtime flow appears in consumers:

1. Display or power-management code can compose display timer control words using count, enable, mask, acknowledge, status, and pulse-width fields.
2. SMU power-management code can set VDDGFX idle thresholds and enable/force idle exit behavior, then observe detect/state bits.
3. LCAC initialization code writes MC and CPL control registers, often first with low enable/threshold values, then after a short delay with block/signal selector bits set.
4. BIOS/ROM read paths save `ROM_CNTL`, enable or override ROM signaling, read BIOS contents, and restore the saved control value.
5. Video IP clock-gating query paths read `ixCURRENT_PG_STATUS` or an APU variant and skip UVD/VCE clock-gating register reads while the corresponding engine is power-gated.
6. ROM software-command flows would fill `ROM_SW_CNTL`, `ROM_SW_COMMAND`, and `ROM_SW_DATA_1..64`, then poll `ROM_SW_STATUS__ROM_SW_DONE_MASK`; this chunk supplies the field layout even though the sampled local call sites mostly use the simpler `ROM_CNTL` path.

Concrete local examples include `cik_read_disabled_bios()` and `vi_read_disabled_bios()`, which read `ixROM_CNTL`, set `ROM_CNTL__SCK_OVERWRITE_MASK` while calling `amdgpu_read_bios()`, and restore the original value afterward. `smu7_hwmgr.c` programs `ixLCAC_MC0_CNTL`, `ixLCAC_MC1_CNTL`, and `ixLCAC_CPL_CNTL` through SMC indirect writes. `uvd_v6_0_get_clockgating_state()` and `vce_v3_0_get_clockgating_state()` test the UVD/VCE masks before reading video clock-gating registers.

## State and Persistence

All state represented here lives in hardware registers or in ROM command payload latches, not in this header:

- Display timer count, enable, mask, running, interrupt, status, and acknowledge bits persist in SMU timer control registers while the device remains powered and initialized.
- VDDGFX idle threshold and unit fields configure idle-detection policy. Detect/state/exit bits are live hardware state that can change as graphics and bus activity changes.
- LCAC control registers persist the selected monitored block/signal, threshold, and enable state; override select/value registers force or mask measurement inputs until cleared.
- ROM control fields persist SPI/ROM access timing and clocking policy. BIOS-read code that changes `ROM_CNTL` must restore it because the register affects subsequent ROM transactions.
- ROM software-command data registers are command-buffer-like hardware state. `ROM_SW_DATA_1..64` are full-width payload slots, while `ROM_SW_STATUS__ROM_SW_DONE_MASK` is transient completion state.
- Current power-gating status bits are live status flags for media blocks. They are read to avoid touching register spaces that may be inaccessible or invalid while a block is power-gated.

The header contains no persistence, locking, or synchronization. Consumers must provide ordering, mutual exclusion, and restore logic around hardware register writes.

## Dependencies and Integration Points

Primary dependencies:

- `drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_d.h` for matching register addresses, including `ixPWR_DISP_TIMER_*`, `ixVDDGFX_IDLE_*`, `ixLCAC_*`, `ixROM_*`, and `ixCURRENT_PG_STATUS`.
- AMDGPU SMC indirect register access helpers such as `RREG32_SMC` and `WREG32_SMC`, and PowerPlay CGS indirect access helpers.
- Common register field helper conventions in AMDGPU, where masks and shifts are combined through `REG_SET_FIELD`-style code or direct bitwise operations.
- Power-management, BIOS-loading, display-timer, and media IP clock-gating code that needs SMU 7.1.1-specific bit layouts.

The LCAC symbols integrate with PowerPlay/hwmgr current-activity setup. The ROM symbols integrate with early device bring-up and disabled-BIOS reads on CIK/VI-class paths. The `CURRENT_PG_STATUS` masks integrate with UVD and VCE clock-gating reporting so those IP blocks are not queried while powered down.

## Risks and Edge Cases

- The generated names around `DISP_TIMER_INT_MASK` are easy to misread: `PWR_DISP_TIMER_N_CONTROL__DISP_TIMER_INT_MASK_MASK` is the field mask for a field named `DISP_TIMER_INT_MASK`, while `PWR_DISP_TIMER_N_CONTROL__DISP_TIMER_INT_MASK` is a separate interrupt bit at bit 30. Direct readers must distinguish the field name from the `_MASK` suffix convention.
- Timer 5 is incomplete in this chunk because its count field appears in the previous chunk; timers 6-15 are complete here. Reconciliation must merge adjacent chunks for a full per-file view.
- `PWR_DISP_TIMER_14_CONTROL` and `PWR_DISP_TIMER_15_CONTROL` have addresses far from the timer 2-13 sequence in `smu_7_1_1_d.h`; code must use the address macros rather than assuming contiguous timer addresses.
- Narrow fields must be shifted and masked, not ORed with raw values. Examples include 25-bit timer counts, 10-bit pulse width, 16-bit VDDGFX thresholds, 4-bit threshold units, 5-bit LCAC block ids, 8-bit LCAC signal ids, 24-bit ROM addresses, and 2-bit ROM command sizes.
- ROM code often saves and restores `ROM_CNTL`. Any early return between setting `ROM_CNTL__SCK_OVERWRITE_MASK` and restoring the original value can leave ROM clocking or SPI behavior altered.
- `ROM_STATUS__ROM_BUSY_MASK` and `ROM_SW_STATUS__ROM_SW_DONE_MASK` are polling signals. Consumers need timeouts to avoid boot or resume hangs if hardware never transitions.
- `PAGE_MIRROR_CNTL` includes invalidate and enable bits near the base/usage fields. Accidental writes that preserve neither old state nor intended invalidation ordering can stale or disable the mirror mapping.
- Full-width `ROM_SW_DATA_N` fields do not validate command length. The software-command flow must keep `DATA_SIZE` consistent with the number of data registers populated.
- Power-gating status bits protect access to UVD/VCE clock-gating registers. Ignoring them risks register reads while the engine is power-gated, which can return invalid values or trigger access problems depending on platform state.
- These headers are generated from hardware descriptions; hand edits can diverge from firmware/ASIC documentation and silently corrupt register programming.

## Test Signals

Useful validation signals for code that consumes this chunk:

- Compile coverage for SMU 7.1.1 builds should catch renamed or missing symbols in CIK/VI, PowerPlay, UVD, and VCE paths.
- BIOS-read tests on disabled-ROM configurations should show `ROM_CNTL` saved, `ROM_CNTL__SCK_OVERWRITE_MASK` set during the read, and the original value restored on exit.
- Hardware traces or debug reads should confirm LCAC writes to `ixLCAC_MC0_CNTL`, `ixLCAC_MC1_CNTL`, and `ixLCAC_CPL_CNTL` set enable, threshold, block, and signal bits exactly as intended.
- Display/power tests should confirm display timer interrupts transition through enable/running/status/ack states without spurious unmasked interrupts.
- VDDGFX idle tests should observe threshold/unit programming, idle-detect transitions, SMC idle-state reporting, and forced-exit behavior under graphics load and idle conditions.
- UVD/VCE clock-gating debug output should report that state cannot be read while the corresponding `CURRENT_PG_STATUS` bit says the engine is power-gated, and should resume normal reporting after power-up.
- ROM software-command tests, if present on this ASIC path, should verify command-size/data-size encoding, `ROM_SW_DONE` polling with timeout coverage, and correct use of the 64 payload registers.
