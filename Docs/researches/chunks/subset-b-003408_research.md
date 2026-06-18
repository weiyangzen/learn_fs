# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_0_1_sh_mask.h lines 4535-5462

## Scope

This chunk covers the final portion of the SMU 7.0.1 generated shift/mask header. It starts in the middle of `CG_FREQ_TRAN_VOTING_0` graphics/RLC throttling vote fields and runs through the end of the include guard. The covered content is entirely C preprocessor register-field metadata: each hardware field is represented as a `_MASK` macro, a `__SHIFT` macro, or both. There are no functions, structs, storage objects, allocation paths, locks, or executable branches in this range.

The register families in this chunk are:

- `CG_FREQ_TRAN_VOTING_0` through `CG_FREQ_TRAN_VOTING_7` frequency-transition throttling vote enables.
- PLL, static-screen, display-gap, ACPI, SCLK deep-sleep, LCLK deep-sleep, ULV, and SCLK minimum-divider controls.
- `TARGET_AND_CURRENT_PROFILE_INDEX_1` current/target voltage and PCIe profile index fields.
- LCAC threshold/override controls for SX0, MC0 through MC3, and CPL.
- ROM indirect access, ROM clocking/timing, ROM page mirror, ROM indexed/software command/data, ROM busy/done status, and the 64 full-width `ROM_SW_DATA_n` payload registers.
- Current power-gating status bits for VCE and UVD, plus `SMC_SYSCON_MISC_CNTL` prefetcher enable.

## Purpose

The purpose of this section is to define the bit-level ABI used by AMDGPU SMU/clock/power-management code when it reads or writes SMU 7.0.1 registers. The sibling SMU offset header supplies register addresses. This header supplies the field masks and bit positions required to compose register values, extract status fields, and preserve unrelated bits during read/modify/write updates.

Consumers typically use these macros through AMDGPU register helpers and bitfield helpers, for example `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, `RREG32_SMC`, or ASIC-specific register access wrappers. The macros are not meaningful by themselves; their correctness depends on exact alignment with the ASIC register specification and the corresponding offset/default headers.

## Important Macro Families

### Frequency Transition Voting

Lines 4535-4982 are dominated by `CG_FREQ_TRAN_VOTING_*` field pairs. `CG_FREQ_TRAN_VOTING_0` is already in progress at the start of the chunk and contributes the tail fields for `GRBM_10` through `GRBM_15` and `RLC`. `CG_FREQ_TRAN_VOTING_1` through `CG_FREQ_TRAN_VOTING_7` then repeat a regular layout.

Each full voting register exposes one-bit enable fields for blocks that can participate in frequency throttling or frequency transition votes:

- BIF, HDP, ROM, IH semaphore, PDMA, DRM, IDCT, ACP, SDMA, UVD, VCE, DC/AZ, SAM, and AVP.
- `GRBM_0` through `GRBM_15`, mapping per-GRBM graphics busy/throttling participants.
- RLC at bit 30.

The repeated layout makes these fields especially likely to be used by generic tables or initialization sequences that program all voting slots consistently. A wrong mask in this family can leave a hardware client unable to vote for throttling, or can allow an unintended client to stall a clock/frequency transition.

### Clock and Display Power Parameters

`PLL_TEST_CNTL` at lines 4983-4992 provides test source/reference select fields, reference/test count fields, and a test reset bit. This is diagnostic/control-plane register metadata rather than a normal runtime data path.

`CG_STATIC_SCREEN_PARAMETER` and `CG_DISPLAY_GAP_CNTL`/`CG_DISPLAY_GAP_CNTL2` at lines 4993-5008 define the thresholds and timing used by display-aware clock-gating logic. The static-screen fields encode a threshold and unit; display-gap fields encode display gap selection, vertical blanking interval timer count/unit, memory-change display gap behavior, timer disable, and a full-width prediction register.

`CG_ACPI_CNTL` at lines 5009-5012 defines SCLK ACPI divisor and SCLK-change skip control. These fields integrate SMU clock behavior with platform power-management states.

### SCLK Deep Sleep Controls

`SCLK_DEEP_SLEEP_CNTL` at lines 5013-5050 describes the main system-clock deep-sleep register. It includes:

- Divider, ramp disable, and hysteresis fields.
- Mask bits for activity or permission signals such as SCLK running, self-refresh, NBP-state allowance, BIF busy, UVD busy, MC SRBM busy, MC allow, SMU busy, MBUS2 active, VCE busy, and AZ busy.
- Fast-exit and entry-mode fields.
- `ENABLE_DS` at bit 31.

`SCLK_DEEP_SLEEP_CNTL2` at lines 5051-5082 extends the busy-mask set with RLC, HDP, ROM, IH semaphore, PDMA, IDCT, SDMA, DC/AZ, ACP stutter permission, UVD/VCE/SAM clock-gating status, RLC GFXCLK-off, shallow divider, and in/out cushion fields.

`SCLK_DEEP_SLEEP_CNTL3` at lines 5083-5114 maps `GRBM_0` through `GRBM_15` SMU busy-mask bits. This pairs with the graphics throttling vote fields earlier in the chunk and lets firmware/driver policy decide which graphics blocks block SCLK deep-sleep entry.

`SCLK_DEEP_SLEEP_MISC_CNTL` at lines 5115-5124 adds DPM and OCP divider controls, including OCP enable and deep/shallow sleep divider IDs. `SCLK_MIN_DIV` at lines 5201-5204 defines fractional and integer minimum SCLK divider fields.

### LCLK Deep Sleep Controls

`LCLK_DEEP_SLEEP_CNTL` at lines 5125-5134 mirrors the basic deep-sleep shape for link clock: divider ID, ramp disable, hysteresis, reserved bits, and `ENABLE_DS`.

`LCLK_DEEP_SLEEP_CNTL2` at lines 5135-5180 contains link/PCIe-oriented masks and wake state fields. It covers RFE, BIF LCLK busy, L1/L2 IMU idle signals, SCLK running, SMU busy, multiple PCIe LCLK idle lines, inbound/outbound wake and wake-ack signals, DMA activity, RLC GFXCLK-off, and reserved high bits. These fields are part of the condition set that gates LCLK deep-sleep entry and exit.

### Profile, ULV, and LCAC Controls

`TARGET_AND_CURRENT_PROFILE_INDEX_1` at lines 5181-5196 packs current and target indices for VDDCI, MVDD, VDDC, and PCIe profile levels. Each index is a 4-bit nibble. Driver or firmware code can use this register to observe transition state between current and requested power/voltage/PCIe profiles.

`CG_ULV_PARAMETER` at lines 5197-5200 defines the Ultra Low Voltage threshold and its unit. This is clock-gating/power-management policy input rather than persistent software state.

The `LCAC_*` registers at lines 5205-5276 define threshold controls and full-width override select/value registers for SX0, memory-controller channels MC0 through MC3, and CPL. Each `*_CNTL` register uses a consistent field layout:

- enable bit at bit 0,
- threshold at bits 16:1,
- block ID at bits 21:17,
- signal ID at bits 29:22.

The override select/value registers are 32-bit wide fields. These definitions are likely used by low-current/activity counter or clock/activity classification logic where a selected block/signal pair is compared against a threshold, with optional override behavior.

### ROM and SMC Indirect Access

Lines 5277-5456 describe ROM-side control and data registers:

- `ROM_SMC_IND_INDEX` and `ROM_SMC_IND_DATA` provide full-width indirect SMU/ROM address/data fields.
- `ROM_CNTL` controls SCK overwrite, ROM clock gating, chip-select setup/hold timing, and SCK prescalers for reference and crystal clocks.
- `PAGE_MIRROR_CNTL` controls page mirror base address, invalidation, enable, and usage.
- `ROM_STATUS` exposes the `ROM_BUSY` bit.
- `CGTT_ROM_CLK_CTRL0` provides ROM clock-gating on-delay, off-hysteresis, and soft override bits.
- `ROM_INDEX`, `ROM_DATA`, and `ROM_START` expose indexed ROM access fields.
- `ROM_SW_CNTL`, `ROM_SW_STATUS`, and `ROM_SW_COMMAND` define software-command sizing, return-data enable, done status, instruction, and address fields.
- `ROM_SW_DATA_1` through `ROM_SW_DATA_64` are full-width payload/result words.

These macros support command-style ROM access paths. The implicit control flow lives in consumers: program command/data/control fields, start or issue the transaction, poll `ROM_BUSY` or `ROM_SW_DONE`, then read data payload registers. This header only provides the field encodings for those steps.

### Tail Status Bits

At lines 5457-5460, `CURRENT_PG_STATUS` exposes VCE and UVD power-gating status masks. Unlike most fields in this chunk, these two masks do not include companion shift macros in the covered range. `SMC_SYSCON_MISC_CNTL__pre_fetcher_en` then defines a single prefetcher enable bit and shift before the header closes at line 5462.

## APIs, Types, and Functions

This chunk defines no callable APIs, C types, inline helpers, enums, or data structures. The exported interface is the macro namespace itself. The naming convention is the API contract:

- `<REGISTER>__<FIELD>_MASK` gives the bit mask for a field.
- `<REGISTER>__<FIELD>__SHIFT` gives the field shift.
- Full-width data fields use mask `0xffffffff` and shift `0x0`.

The macros are intended to be included by AMDGPU/SMU C code that knows the target ASIC generation. They must not be interpreted independently of the matching register-offset header and the register access domain for the target block.

## Control Flow

There is no direct control flow in the header. The hardware workflows implied by the fields are:

- Frequency transition setup: enable or disable per-block throttling votes in `CG_FREQ_TRAN_VOTING_*` registers.
- Deep-sleep policy setup: program dividers, hysteresis, enable bits, and busy-mask bits for SCLK and LCLK deep sleep, then hardware/SMU logic uses live block activity to enter or exit low-power states.
- Profile tracking: read current/target profile nibbles to observe voltage and PCIe power-state transitions.
- ROM access: program index/command/data registers, wait for busy/done status, and read back payload words.

All sequencing, synchronization, timeout handling, and read/modify/write preservation must be implemented by the caller.

## State and Persistence Behavior

The macros describe memory-mapped hardware register state. Any persistence is hardware/firmware persistence, not software persistence. Writes to these fields change volatile ASIC state and may be reset by GPU reset, suspend/resume, power-gating transitions, firmware reinitialization, or driver reprogramming.

Several fields affect persistent behavior while the GPU is powered:

- `CG_FREQ_TRAN_VOTING_*` fields influence which blocks can block or request throttled frequency transitions.
- SCLK/LCLK deep-sleep enable, divider, hysteresis, and mask fields affect low-power entry/exit behavior until reprogrammed.
- ROM timing and command fields affect active ROM transactions and clocking.
- LCAC threshold/override fields change activity/threshold classification for selected blocks/signals.

Because these are shared hardware registers, callers must preserve unrelated bits and account for firmware ownership. Blind writes can corrupt adjacent fields in the same register.

## Dependencies and Integration Points

Primary dependencies are:

- Matching SMU 7.0.1 register offset/default headers in the same AMDGPU ASIC register tree.
- AMDGPU register access helpers for SMU, MMIO, and indexed/indirect register spaces.
- SMU firmware/power-management code that owns clock-gating, dynamic power management, deep sleep, ULV, profile transition, and ROM access policy.
- Display, UVD, VCE, SDMA, ACP, BIF/PCIe, RLC, GRBM, and memory-controller blocks whose busy, idle, or vote signals are named by the masks.

Integration is low-level and hardware-facing. Higher layers should not depend on literal mask values; they should use these macros through the normal AMDGPU field helpers so ASIC-specific layout stays localized to generated register headers.

## Risks and Edge Cases

- Generated-header drift: if this mask header and the corresponding offset/default headers come from different register database revisions, callers can write correct-looking bitfields to the wrong addresses or wrong bit positions.
- Read/modify/write hazards: many registers pack unrelated controls into one word. Updating one field without preserving the others can disable deep sleep, alter ROM timing, or change vote eligibility for unrelated hardware blocks.
- Reserved bits: `LCLK_DEEP_SLEEP_CNTL` and `LCLK_DEEP_SLEEP_CNTL2` expose reserved masks. Software should avoid using reserved ranges as writable policy fields unless the ASIC programming guide requires a specific value.
- Busy-mask polarity mistakes: fields named `*_BUSY_MASK_MASK` or `*_IDLE_MASK_MASK` are easy to misread. Enabling a mask generally changes whether that signal participates in low-power gating decisions; it is not the same as reporting the live busy/idle state.
- ROM command timeout risk: consumers using `ROM_BUSY` or `ROM_SW_DONE` need bounded polling. A bad command size, address, timing value, or clock-gating override can leave firmware/software waiting on hardware status.
- Repeated register layouts: `CG_FREQ_TRAN_VOTING_1` through `_7`, `SCLK_DEEP_SLEEP_CNTL3`, `LCAC_*`, and `ROM_SW_DATA_1` through `_64` are repetitive. Copy/paste or generation errors can be subtle and should be checked mechanically.
- Tail masks without shifts: `CURRENT_PG_STATUS__VCE_PG_STATUS_MASK` and `CURRENT_PG_STATUS__UVD_PG_STATUS_MASK` appear without companion shift macros in this chunk. Callers that expect every field to have both forms need to handle these status bits explicitly or confirm the shift definitions elsewhere.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for AMDGPU configurations that include SMU 7.0.1 headers, catching missing macro names or malformed generated definitions.
- Static checks that each non-status bitfield used by driver code has the expected `_MASK`/`__SHIFT` pair and that `REG_SET_FIELD`/`REG_GET_FIELD` invocations reference the right register namespace.
- Hardware smoke tests around clock/power management: DPM transitions, SCLK/LCLK deep-sleep entry/exit, suspend/resume, display idle/static-screen behavior, and ACPI power-state changes.
- Media and graphics workload tests while deep-sleep/vote fields are active, especially UVD, VCE, SDMA, RLC, and GRBM activity, to catch incorrect busy-mask or vote programming.
- ROM access tests with bounded polling for `ROM_BUSY`/`ROM_SW_DONE`, including readback of indexed/software data paths.
- Register readback or debugfs-style dumps, where available, to confirm programmed masks preserve adjacent fields and reserved bits.
