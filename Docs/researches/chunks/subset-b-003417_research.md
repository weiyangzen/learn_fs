# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_2_sh_mask.h lines 4518-5838

## Scope

This chunk covers the final 1,321 lines of the generated AMDGPU SMU 7.1.2 shift/mask register header. The range starts in the middle of the `THM_TMON1_RDIL5_DATA` field definitions and continues through thermal monitor, power-management, clock-voting, deep-sleep, display gap, VDDGFX idle, LCAC, ROM, and current power-gating status register fields. It ends at the file include guard close.

This header chunk defines preprocessor constants only. There are no C functions, structs, global variables, heap allocations, locks, loops, or executable control flow in the covered range. Its behavior is compile-time: it supplies bit masks and field shifts used by AMDGPU/PowerPlay code when reading, composing, and updating SMU 7.1.2 hardware register values.

## Purpose

`smu_7_1_2_sh_mask.h` is the bit-layout companion for the SMU 7.1.2 register-address header `smu_7_1_2_d.h`. The covered chunk gives consumers the field encodings for 32-bit registers accessed through SMU indirect or SMC register paths. The generated convention is:

- `<REGISTER>__<FIELD>_MASK` isolates the field bits in the 32-bit register value.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.

Driver code combines these definitions with register helpers such as `RREG32_SMC`, `WREG32_SMC`, `WREG32_P`, `PHM_SET_FIELD`, `PHM_WRITE_INDIRECT_FIELD`, `cgs_read_ind_register`, and `cgs_write_ind_register`. The header keeps low-level register programming code from hard-coding bit positions for SMU 7.1.2 ASICs, especially Tonga-era SMU7 paths.

## Important Macro Families

### Thermal Monitor Data and Status

The first part of the chunk completes repeated thermal monitor data layouts:

- `THM_TMON1_RDIL5_DATA` through `THM_TMON1_RDIL15_DATA`.
- `THM_TMON1_RDIR0_DATA` through `THM_TMON1_RDIR15_DATA`.
- `THM_TMON0_INT_DATA` and `THM_TMON1_INT_DATA`.
- `THM_TMON0_DEBUG`, `THM_TMON1_DEBUG`, `THM_TMON0_STATUS`, and `THM_TMON1_STATUS`.

The `*_DATA` registers use the same field shape: `Z` at bits 0..10, `VALID` at bit 11, and `TEMP` at bits 12..23. The one boundary artifact is that this chunk starts after the `THM_TMON1_RDIL5_DATA__Z_MASK` line, so only the `Z__SHIFT`, `VALID`, and `TEMP` definitions for RDIL5 appear here. `DEBUG_RDI` and `DEBUG_Z` expose selected thermal diode/debug readings. `CURRENT_RDI` and `MEAS_DONE` expose thermal measurement progress.

These masks are read-oriented telemetry definitions. They let software validate whether a sensor sample is fresh before interpreting the raw temperature and diode output fields.

### Global, CNB, and SCLK Power Management

The power-management control registers include:

- `GENERAL_PWRMGT`: global and static power management enable bits, thermal protection disable/type, SMIO index, ACPI D2/D3 low-voltage controls, voltage power management enable, GPU counter clock/off/interface-off state, ACPI D3 VID, dynamic spread-spectrum enable, and reserved/spare fields.
- `CNB_PWRMGT_CNTL`: GNB slow mode, forced northbridge power-state selection, DPM enable, and spare bits.
- `SCLK_PWRMGT_CNTL`: SCLK power management off, reset controls for busy/SCLK counters, dynamic light sleep, automatic pulse skip, light-sleep counter, and dynamic PM enable.
- `TARGET_AND_CURRENT_PROFILE_INDEX`: target/current DPM state and target/current MCLK, SCLK, and LCLK index fields.
- `TARGET_AND_CURRENT_PROFILE_INDEX_1`: target/current VDDCI, MVDD, VDDC, and PCIe index fields.

These fields are core state-machine inputs and observability points for dynamic power management. For example, PowerPlay code clears or asserts `SCLK_PWRMGT_CNTL` reset fields before programming the eight `CG_FREQ_TRAN_VOTING_*` registers, and legacy DPM paths use `GENERAL_PWRMGT` bits to enable global power management, thermal protection, voltage management, and spread spectrum.

### PCC, Clock Voting, and PLL Test Fields

`PWR_PCC_CONTROL` and `PWR_PCC_GPIO_SELECT` describe a power/current-control polarity bit and full-width GPIO selection field.

`CG_FREQ_TRAN_VOTING_0` through `CG_FREQ_TRAN_VOTING_7` are a repeated family of frequency-transition voting-client bitmaps. Each register exposes enable bits for clients such as `BIF`, `HDP`, `ROM`, `IH_SEM`, `PDMA`, `DRM`, `IDCT`, `ACP`, `SDMA`, `UVD`, `VCE`, `DC_AZ`, `SAM`, `AVP`, `GRBM_0` through `GRBM_15`, and `RLC`. SMU7 PowerPlay writes all eight voting registers in sequence from `data->voting_rights_clients[i]` and clears them when disabling DPM.

`PLL_TEST_CNTL` supplies test-source, reference-source, reference-count, test-reset, and test-count fields. It is diagnostic/test infrastructure for PLL or clock validation rather than ordinary runtime policy.

### Display Gap, ACPI, Static Screen, and ULV Parameters

Display and low-power timing fields include:

- `CG_STATIC_SCREEN_PARAMETER`: static-screen threshold and threshold unit.
- `CG_DISPLAY_GAP_CNTL`: display gap selection, vertical blank interval timer count/unit, memory-change display-gap policy, and VBI timer disable.
- `CG_DISPLAY_GAP_CNTL2`: full-width VBI prediction.
- `CG_ACPI_CNTL`: SCLK ACPI divider and SCLK-change skip.
- `CG_ULV_PARAMETER`: ultra-low-voltage threshold and threshold unit.
- `SCLK_MIN_DIV`: fractional and integer minimum SCLK divider fields.

These fields connect display timing, ACPI low-power behavior, static-screen detection, and ULV entry thresholds to the SMU's dynamic clocking decisions. Existing SMU7 code uses `PHM_SET_FIELD` with `CG_DISPLAY_GAP_CNTL` fields when programming display gap behavior around vertical blanking.

### SCLK and LCLK Deep Sleep

The deep-sleep section maps the policy and gating signals used to enter lower-clock states:

- `SCLK_DEEP_SLEEP_CNTL`: divider ID, ramp disable, hysteresis, many busy/allow masks, fast-exit request, entry mode, and `ENABLE_DS`.
- `SCLK_DEEP_SLEEP_CNTL2`: additional busy masks for RLC, HDP, ROM, IH semaphore, PDMA, IDCT, SDMA, DC/AZ, ACP, UVD, VCE, SAM, RLC graphics-clock-off, plus shallow divider and in/out cushion fields.
- `SCLK_DEEP_SLEEP_CNTL3`: GRBM0 through GRBM15 busy masks.
- `SCLK_DEEP_SLEEP_MISC_CNTL`: DPM and OCP divider IDs plus OCP enable.
- `LCLK_DEEP_SLEEP_CNTL`: LCLK divider ID, ramp disable, hysteresis, reserved bits, and `ENABLE_DS`.
- `LCLK_DEEP_SLEEP_CNTL2`: LCLK idle/busy/wake/DMA masks for RFE, BIF, L1/L2 IMU paths, PCIe idle signals, ORB idle, inbound/outbound wake and wake-ack, DMA active, RLC graphics-clock-off, and reserved bits.

The naming pattern has repeated `*_MASK_MASK` symbols for fields whose logical hardware field name already ends in `MASK`. Consumers must use the exact generated identifier, for example `SCLK_DEEP_SLEEP_CNTL__SMU_BUSY_MASK_MASK` for the bit mask and `SCLK_DEEP_SLEEP_CNTL__SMU_BUSY_MASK__SHIFT` for the shift.

Deep-sleep fields are high-risk because they gate SCLK or LCLK based on multiple client busy signals. An incorrect bit position can allow entry while a block is active, prevent sleep entirely, or break wake timing.

### Clock Stretching, Display Timers, and VDDGFX Idle

Clock-stretching fields are split across:

- `PWR_CKS_ENABLE`: stretch enable, master reset, and static enable.
- `PWR_CKS_CNTL`: bypass, PCC enable, temperature compensation, stretch amount, skip-phase bypass, sample size, FSM wait cycles, low-frequency use, coarse-step suppression, LDO reference selection, debug select, and LDO ready-count value.

Display timer fields are duplicated for `PWR_DISP_TIMER_CONTROL`/`DEBUG` and `PWR_DISP_TIMER2_CONTROL`/`DEBUG`, with count, enable/disable, interrupt mask, interrupt status acknowledge, interrupt type/mode, running/stat/int debug bits, and run-value fields. `PWR_DISP_TIMER_CONTROL2` adds display timer pulse width.

VDDGFX idle fields include:

- `VDDGFX_IDLE_PARAMETER`: threshold and threshold unit.
- `VDDGFX_IDLE_CONTROL`: idle enable, detect, forced idle exit, and SMC idle-state observation.
- `VDDGFX_IDLE_EXIT`: BIF exit request.

These fields participate in voltage/clock-reduction mechanisms. They are typically programmed by firmware or PowerPlay policy code and then observed through status bits.

### LCAC Measurement/Override Controls

The LCAC family contains four memory-controller channels and one CPL channel:

- `LCAC_MC0_CNTL` through `LCAC_MC3_CNTL`.
- `LCAC_MC0_OVR_SEL`/`OVR_VAL` through `LCAC_MC3_OVR_SEL`/`OVR_VAL`.
- `LCAC_CPL_CNTL`, `LCAC_CPL_OVR_SEL`, and `LCAC_CPL_OVR_VAL`.

Each `*_CNTL` register has enable, threshold, block ID, and signal ID fields. Override select and override value registers are full-width fields. These definitions support leakage/current/activity counter or calibration-related programming where the SMU selects monitored hardware signals and optionally forces override values.

### ROM, Page Mirror, and SMC Indirect Access

The ROM portion covers several register-access paths:

- `ROM_SMC_IND_INDEX` and `ROM_SMC_IND_DATA`: full-width indirect address/data fields for ROM SMC access.
- `ROM_CNTL`: SCK overwrite, ROM clock gating enable, chip-select setup/hold timings, and reference/crystal SCK prescalers.
- `PAGE_MIRROR_CNTL`: page mirror base address, invalidate, enable, and usage fields.
- `ROM_STATUS`: ROM busy.
- `CGTT_ROM_CLK_CTRL0`: ROM clock gating on delay, off hysteresis, and two soft override bits.
- `ROM_INDEX`, `ROM_DATA`, and `ROM_START`: indexed ROM address/data/start fields.
- `ROM_SW_CNTL`, `ROM_SW_STATUS`, and `ROM_SW_COMMAND`: software-command data size, command size, return-data enable, done status, instruction, and address fields.
- `ROM_SW_DATA_1` through `ROM_SW_DATA_64`: 64 full-width data payload registers.

These fields are the chunk's largest late section. They describe both direct/indexed ROM accesses and a software-command mailbox with up to 64 data words. Correct polling of `ROM_STATUS__ROM_BUSY_MASK` or `ROM_SW_STATUS__ROM_SW_DONE_MASK` is necessary when the driver or firmware path performs ROM transactions.

### Current Power-Gating Status

The chunk ends with two status masks:

- `CURRENT_PG_STATUS__VCE_PG_STATUS_MASK` at bit 1.
- `CURRENT_PG_STATUS__UVD_PG_STATUS_MASK` at bit 2.

These are directly used by media IP code. `vce_v3_0_get_clockgating_state()` reads `ixCURRENT_PG_STATUS` or `ixCURRENT_PG_STATUS_APU` and avoids reading VCE clock-gating registers while VCE is powergated. `uvd_v5_0_get_clockgating_state()` similarly checks `CURRENT_PG_STATUS__UVD_PG_STATUS_MASK` before reading UVD clock-gating state.

## Control Flow and State Behavior

This header has no runtime control flow. The effective control flow lives in driver code that includes the header and performs read-modify-write, poll, and status-check sequences against hardware registers.

The hardware state represented by this chunk falls into several categories:

- Configuration state that persists in SMU registers until reset or explicit reprogramming, such as global power-management enables, DPM state indices, voting-client bitmaps, deep-sleep dividers/masks, display gap timers, clock-stretching controls, LCAC thresholds, ROM timing, and page mirror controls.
- Status and telemetry state, such as thermal sample validity/temperature, thermal measurement done, target/current profile indices, VDDGFX idle detect/state, ROM busy/done, and current VCE/UVD power-gating status.
- Command or handshake state, such as reset counter bits, display timer interrupt enable/disable/status acknowledge, forced VDDGFX idle exit, BIF idle exit request, page mirror invalidate, ROM software commands, and ROM data payloads.
- Debug or diagnostic state, such as thermal monitor debug fields, PLL test fields, display timer debug fields, ROM clock soft overrides, and LCAC override select/value registers.

Because these are hardware registers, persistence is device-local rather than file-local. The header does not store state, enforce ordering, or encode access semantics such as write-one-to-clear, sticky status, required delays, or polling timeouts. Those rules must be supplied by the ASIC documentation and by the surrounding SMU/PowerPlay code.

## Dependencies and Integration Points

This chunk depends on AMDGPU's generated register-header layout:

- `smu_7_1_2_d.h` supplies register addresses such as `ixCG_FREQ_TRAN_VOTING_0`, `ixCG_DISPLAY_GAP_CNTL`, and `ixCURRENT_PG_STATUS`.
- Other generated SMU 7.1.2 headers, when present, supply default/reset values.
- Register helper macros consume the `__SHIFT` and `_MASK` definitions to avoid hard-coded field math.

Observed source-tree include points for this specific header include:

- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_baco.c`.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.c`.
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/tonga_smumgr.c`.
- `drivers/gpu/drm/amd/amdgpu/vce_v3_0.c`.
- `drivers/gpu/drm/amd/amdgpu/uvd_v5_0.c`.

Representative integration paths include:

- SMU7/Tonga PowerPlay initialization and DPM enable/disable, especially programming `CG_FREQ_TRAN_VOTING_0` through `_7` and `SCLK_PWRMGT_CNTL` reset bits.
- Display power tuning, especially `CG_DISPLAY_GAP_CNTL` fields used with vertical blank timing.
- BACO and SMU manager code that relies on SMU 7.1.2 register addresses and field masks for low-power transitions.
- UVD and VCE clock-gating status reporting, which checks `CURRENT_PG_STATUS` before accessing media block registers.
- Legacy DPM code sharing similarly named SMU masks across adjacent SMU7 generations for `GENERAL_PWRMGT` fields.
- ROM access or firmware/BIOS data paths that may use ROM index/data, software command, busy, and data payload fields.

## Risks

- Chunk-boundary risk: the range starts after `THM_TMON1_RDIL5_DATA__Z_MASK`, so a consumer reading only this chunk would see `RDIL5_DATA__Z__SHIFT` without its matching mask. The full file provides the missing pair just before the requested range.
- Generated-name risk: fields with hardware names ending in `MASK` produce identifiers such as `SCLK_DEEP_SLEEP_CNTL__BIF_BUSY_MASK_MASK`. Manual edits or ad hoc scripts can easily collapse the duplicated `MASK` and break builds.
- Register-generation drift: SMU 7.1.2 is close to other SMU 7.x headers, but masks are ASIC-specific. Reusing constants from `smu_7_0_0`, `smu_7_1_3`, or newer `smuio_*` headers can silently target the wrong bit.
- Power-management risk: incorrect `GENERAL_PWRMGT`, `CNB_PWRMGT_CNTL`, `SCLK_PWRMGT_CNTL`, DPM profile index, or voting-client masks can prevent DPM from enabling, leave thermal protection disabled, or cause unsafe transitions.
- Deep-sleep risk: wrong SCLK/LCLK busy-mask or wake-mask positions can either block deep sleep permanently or permit clock reduction while hardware clients are active.
- Media power-gating risk: wrong `CURRENT_PG_STATUS` masks can make UVD/VCE code read registers while an engine is powergated, producing invalid state, bus faults, or misleading clock-gating reports.
- ROM access risk: incorrect command-size, data-size, address, busy, done, or payload masks can corrupt ROM transactions or cause timeout loops.
- Reserved/spare bit risk: several registers expose spare or reserved fields. Driver writes must preserve unrelated bits with read-modify-write helpers unless hardware documentation explicitly allows overwriting them.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/driver integration checks:

- Compile coverage for include users: `tonga_smumgr.c`, `smu7_baco.c`, `tonga_baco.c`, `vce_v3_0.c`, and `uvd_v5_0.c` should build without missing-mask or duplicate-name errors.
- Static checks can verify that each generated field pair has a mask and shift, except for known chunk-boundary partials such as `THM_TMON1_RDIL5_DATA__Z_MASK` being outside this range and the final `CURRENT_PG_STATUS` masks not having shift definitions in this file tail.
- DPM bring-up logs should show successful SMU7/Tonga initialization, voting-client programming, and DPM enable/disable without SMU timeouts.
- Power-management tests should exercise SCLK deep sleep, display gap behavior, static-screen/ULV entry, VDDGFX idle entry/exit, and thermal protection under load.
- Media tests should query UVD/VCE clock-gating state while the engines are both powered and powergated, confirming that `CURRENT_PG_STATUS` prevents invalid register reads.
- Suspend/resume and BACO tests should confirm that power-management and ROM/SMU state is restored or reprogrammed correctly after low-power transitions.
- ROM access tests should validate busy/done polling and payload sizes for any firmware/BIOS data paths using `ROM_SW_*` fields.
- Hardware register dumps compared against AMD reference values are the strongest signal for generated-header correctness, because ordinary unit tests cannot prove ASIC bit positions.
