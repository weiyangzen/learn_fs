# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002288`: lines 1-2383, `Docs/researches/chunks/subset-b-002288_research.md`
- `subset-b-002289`: lines 2384-4766, `Docs/researches/chunks/subset-b-002289_research.md`
- `subset-b-002290`: lines 4767-7226, `Docs/researches/chunks/subset-b-002290_research.md`
- `subset-b-002291`: lines 7227-9584, `Docs/researches/chunks/subset-b-002291_research.md`
- `subset-b-002292`: lines 9585-11943, `Docs/researches/chunks/subset-b-002292_research.md`
- `subset-b-002293`: lines 11944-14320, `Docs/researches/chunks/subset-b-002293_research.md`
- `subset-b-002294`: lines 14321-16696, `Docs/researches/chunks/subset-b-002294_research.md`
- `subset-b-002295`: lines 16697-19122, `Docs/researches/chunks/subset-b-002295_research.md`
- `subset-b-002296`: lines 19123-21539, `Docs/researches/chunks/subset-b-002296_research.md`
- `subset-b-002297`: lines 21540-23895, `Docs/researches/chunks/subset-b-002297_research.md`
- `subset-b-002298`: lines 23896-26282, `Docs/researches/chunks/subset-b-002298_research.md`
- `subset-b-002299`: lines 26283-28640, `Docs/researches/chunks/subset-b-002299_research.md`
- `subset-b-002300`: lines 28641-31001, `Docs/researches/chunks/subset-b-002300_research.md`
- `subset-b-002301`: lines 31002-33365, `Docs/researches/chunks/subset-b-002301_research.md`
- `subset-b-002302`: lines 33366-35753, `Docs/researches/chunks/subset-b-002302_research.md`
- `subset-b-002303`: lines 35754-38156, `Docs/researches/chunks/subset-b-002303_research.md`
- `subset-b-002304`: lines 38157-40592, `Docs/researches/chunks/subset-b-002304_research.md`
- `subset-b-002305`: lines 40593-42955, `Docs/researches/chunks/subset-b-002305_research.md`
- `subset-b-002306`: lines 42956-45337, `Docs/researches/chunks/subset-b-002306_research.md`
- `subset-b-002307`: lines 45338-47685, `Docs/researches/chunks/subset-b-002307_research.md`
- `subset-b-002308`: lines 47686-50047, `Docs/researches/chunks/subset-b-002308_research.md`
- `subset-b-002309`: lines 50048-52421, `Docs/researches/chunks/subset-b-002309_research.md`
- `subset-b-002310`: lines 52422-54799, `Docs/researches/chunks/subset-b-002310_research.md`
- `subset-b-002311`: lines 54800-57195, `Docs/researches/chunks/subset-b-002311_research.md`
- `subset-b-002312`: lines 57196-59640, `Docs/researches/chunks/subset-b-002312_research.md`
- `subset-b-002313`: lines 59641-62003, `Docs/researches/chunks/subset-b-002313_research.md`
- `subset-b-002314`: lines 62004-64392, `Docs/researches/chunks/subset-b-002314_research.md`
- `subset-b-002315`: lines 64393-66750, `Docs/researches/chunks/subset-b-002315_research.md`
- `subset-b-002316`: lines 66751-69107, `Docs/researches/chunks/subset-b-002316_research.md`
- `subset-b-002317`: lines 69108-71473, `Docs/researches/chunks/subset-b-002317_research.md`
- `subset-b-002318`: lines 71474-73858, `Docs/researches/chunks/subset-b-002318_research.md`
- `subset-b-002319`: lines 73859-76242, `Docs/researches/chunks/subset-b-002319_research.md`
- `subset-b-002320`: lines 76243-78683, `Docs/researches/chunks/subset-b-002320_research.md`
- `subset-b-002321`: lines 78684-81059, `Docs/researches/chunks/subset-b-002321_research.md`
- `subset-b-002322`: lines 81060-83443, `Docs/researches/chunks/subset-b-002322_research.md`
- `subset-b-002323`: lines 83444-85815, `Docs/researches/chunks/subset-b-002323_research.md`
- `subset-b-002324`: lines 85816-88172, `Docs/researches/chunks/subset-b-002324_research.md`
- `subset-b-002325`: lines 88173-90528, `Docs/researches/chunks/subset-b-002325_research.md`
- `subset-b-002326`: lines 90529-92906, `Docs/researches/chunks/subset-b-002326_research.md`
- `subset-b-002327`: lines 92907-95285, `Docs/researches/chunks/subset-b-002327_research.md`
- `subset-b-002328`: lines 95286-97717, `Docs/researches/chunks/subset-b-002328_research.md`
- `subset-b-002329`: lines 97718-100127, `Docs/researches/chunks/subset-b-002329_research.md`
- `subset-b-002330`: lines 100128-102481, `Docs/researches/chunks/subset-b-002330_research.md`
- `subset-b-002331`: lines 102482-103385, `Docs/researches/chunks/subset-b-002331_research.md`

## Chunk Research

### subset-b-002288: lines 1-2383

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 1-2383

## Purpose

This chunk is the opening slice of AMD's generated DPCS 4.2.0 shift/mask register-field header. It contains no executable C code; it publishes preprocessor constants that describe bit positions and bit masks for DisplayPort control system (`DPCSSYS`), panel power sequencer (`PWRSEQ`), and DPCS transmitter (`RDPCSTX`) MMIO registers. AMDGPU display code pairs these macros with the matching `dpcs_4_2_0_offset.h` register offsets and register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and table-building macros such as `LE_SF`.

The range starts with the license and include guard, then covers CR address/data windows for `DPCSSYS_CR0` through `DPCSSYS_CR4`, complete panel power/backlight sequencer definitions for `PWRSEQ0` and `PWRSEQ1`, complete `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2` transmitter field definitions, and the beginning of `RDPCSTX3`. The requested slice has 2,160 `#define` lines: 1,080 `__SHIFT` macros and 1,079 `_MASK` macros. The one-field mismatch is an artificial chunk boundary: `RDPCSTX3_RDPCSTX_SPARE__RDPCSTX_SPARE__SHIFT` is line 2383, while its mask starts at line 2384 outside this chunk.

Although the path is under a `ceph-client` source tree, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, memory allocations, locks, or callbacks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset used to pack or extract a field.
- `<REGISTER>__<FIELD>_MASK`: field mask used for read-modify-write and readback isolation.

Major register groups in this chunk:

- `DPCSSYS_CR0` through `DPCSSYS_CR4`: 16-bit `RDPCS_TX_CR_ADDR` and `RDPCS_TX_CR_DATA` fields for CR register access windows.
- `PWRSEQ0` and `PWRSEQ1`: GPIO enable/control/mask/A/Y fields for `VARY_BL`, `DIGON`, and `BLON`; panel power sequencing enable, target state, sync/digon/blon override and polarity; state/done readback; power-up and power-down delays; reference dividers; PWM duty, enable, fractional mode, update timing, period, and group-lock fields; plus spare registers.
- `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2`: repeated transmitter blocks covering soft resets, FIFO lane enables/start/read delay, lane bit and byte packing order, interrupt status/clear/mask fields, CR address/data fields, SRAM power control, scratch/spare registers, CR-convert FIFO status, DMCU DP-alt blocking controls, and DP-alt driver-access arbitration.
- `RDPCSTX*_RDPCSTX_PHY_CNTL0` through `PHY_CNTL17`: PHY reset, reference range, CR mux, HDMI mode, SRAM init/bypass/status, VBOOST, power gating and stable bits, DP4/DP-alt status, loopback enables, per-lane TX reset/disable/clock-ready/data-enable/request/ack, termination/invert/equalization-bypass/hot-plug protection, low-power/rate/width/detect-RX request/result, pstate/MPLL enable, reference-clock request/enable, MPLLB fractional denominator/quotient/remainder, spread-spectrum peak/step/up-spread, multiplier/dividers, clock enables, calibration force, fractional and PMIX enable, VREG bypass, supervisor pre-HP, and generic PHY in/out buses.
- `RDPCSTX*_RDPCSTX_PHY_FUSE0` through `PHY_FUSE3`: fuse-derived lane EQ main/pre/post values and common analog tuning fields such as MPLLB V2I, VCO frequency, charge-pump integral/proportional controls, RX VREF, DCO finetune/range, TX VBOOST, and supervisor RX VCO VREF select.
- `RDPCSTX*_RDPCSTX_PHY_RX_LD_VAL`: RX reference lock-detect value, CDR VCO low-frequency bit, and VCO lock-detect value.
- `RDPCSTX*_RDPCSTX_DMCU_DPALT_PHY_CNTL3` and `PHY_CNTL6`: reserved DMCU/DP-alt mirrors for the per-lane reset/disable/clock/data/request/ack and pstate/MPLL/ref-clock/DP-alt fields.
- `RDPCSTX*_RDPCS_CNTL3`, `RDPCS_TX_PLL_UPDATE_ADDR_OVRRD`, and `RDPCS_TX_PLL_UPDATE_DATA_OVRRD`: lane byte-order selection and PLL update override address/data fields.
- `RDPCSTX3`: this chunk includes only the initial part of the fourth transmitter block, through `RDPCSTX_SPARE` shift at line 2383; `CNTL2` and later `RDPCSTX3` fields continue in the next chunk.

## Control Flow

This header has no runtime control flow. It participates in control flow only after inclusion by AMDGPU display code. In this tree, `dcn31_resource.c` includes both `dpcs/dpcs_4_2_0_offset.h` and this shift/mask header, making the macros available to DCN 3.1 resource and link-encoder tables.

The runtime pattern is:

1. Resource initialization selects the ASIC-specific offset and shift/mask headers.
2. Link encoder and panel control table macros token-paste register and field names into register-address and field-mask structures.
3. Display, backlight, link training, USB-C DP-alt-mode, hotplug, suspend/resume, and diagnostics paths use common register helpers to update or poll the DPCS, PWRSEQ, and RDPCSTX fields.
4. Hardware performs the actual sequencing: power rails, panel signals, PWM output, lane enable/reset/request/ack handshakes, PLL programming, SRAM power, and interrupt/status latching.

The macros do not encode ordering or side effects. Consumers must still follow the hardware sequence for panel power-up/down delays, PWM update locking, transmitter resets, FIFO start, reference-clock enabling, MPLL programming, lane request/ack transitions, DP-alt ownership, and SRAM power state changes.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in memory. It describes MMIO-backed hardware state:

- Panel and backlight state: power-sequencer enable/target, current `DIGON`/`SYNCEN`/`BLON` state, sequencer done/state readback, delay counters, reference dividers, PWM duty cycle, PWM period, fractional mode, enable, and group update lock/pending bits.
- GPIO state: output-enable, pull-up, receiver-enable, pad drive strength, mask, power-down disable, receive state, and A/Y values for panel-related GPIOs.
- Transmitter state: soft reset, FIFO enable/start, lane packing/byte order, interrupt and clear bits, CR register window state, scratch/spare values, and PLL update request/pending/override fields.
- PHY state: per-lane reset/disable/clock-ready/data-enable/request/ack, rate, width, pstate, termination, inversion, detect-RX, low-power disable, MPLL enable, loopback, DP-alt mode status, power gating/stability, SRAM initialization, reference-clock control, PLL fractional/SSC/divider programming, fuse-derived analog parameters, VREG bypass, generic buses, and RX lock-detect values.
- DMCU/DP-alt arbitration state: reserved mirror fields and driver-access allow/blocked indicators used when DP-alt hardware or firmware may control the PHY block.

Persistence is hardware-defined. Configuration fields may remain programmed until another modeset/link-training path changes them, the related power domain is gated, firmware takes ownership, or the GPU resets. Status, pending, done, ack, lock-detect, and interrupt fields can be read-only, sticky, write-one-to-clear, self-clearing, or valid only while clocks and power domains are active. This generated header does not label access type, reset value, or side-effect semantics.

## Dependencies And Integration Points

This file must match the generated DPCS 4.2.0 register database and `dpcs_4_2_0_offset.h`. A shift/mask macro is meaningful only when used with the corresponding register offset and the correct ASIC register base index.

Primary integration points are:

- DCN 3.1 resource initialization, which includes this header and the matching offset header.
- DIO and HPO link encoder code that builds per-transmitter `RDPCSTX` register tables and uses `RDPCSTX_PHY_CNTL*`, `RDPCS_TX_CR_ADDR`, and related fields for DisplayPort/HDMI PHY setup.
- Panel control code that reads, saves, restores, and updates `BL_PWM_CNTL`/`BL_PWM_CNTL2` style fields through generated masks for brightness control and backlight enable.
- USB-C/DP-alt-mode paths that inspect or program `RDPCS_PHY_DPALT_DISABLE`, `RDPCS_PHY_DPALT_DP4`, access-blocking, and DMCU DP-alt mirror fields.
- Interrupt, diagnostics, and bring-up flows that depend on FIFO error, register FIFO overflow, loopback, PLL update, scratch/spare, fuse, lock-detect, and generic PHY bus fields.

The repeated `RDPCSTX0`, `RDPCSTX1`, `RDPCSTX2`, and partial `RDPCSTX3` definitions are instance-specific. Their layouts are intentionally similar, but consumers should use the register table for the selected transmitter rather than substituting macro names by hand.

## Risks And Edge Cases

- These are untyped preprocessor constants. A bad shift or mask compiles cleanly but can write adjacent hardware bits, causing panel power sequencing errors, stuck backlight state, lane reset failures, PLL misprogramming, or DP-alt ownership problems.
- The file is generated metadata. Manual edits can diverge from AMD's authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- The register blocks are highly repetitive. A copy or generator error may affect only one transmitter instance or lane, so testing a single connector, lane count, or link rate is insufficient.
- The chunk boundary is incomplete at the end. The `RDPCSTX3_RDPCSTX_SPARE` mask and the rest of `RDPCSTX3` are outside this work item, so this chunk alone cannot make complete claims about transmitter 3.
- Panel power and PWM fields are sequencing-sensitive. Wrong delay, polarity, override, update-lock, or fractional duty fields can produce black screens, visible flicker, brightness jumps, or failure to restore backlight after suspend.
- Lane request/ack, reset, disable, clock-ready, data-enable, pstate, rate, width, and MPLL fields are tightly coupled. Updating them out of order can break link training or leave lanes powered but unusable.
- DP-alt and DMCU access-control bits can indicate ownership by firmware or another hardware agent. Ignoring blocked-access status or mirror/reserved fields can race platform firmware.
- Interrupt/status fields include clear and mask bits in the same register family. Confusing status masks with clear masks can drop diagnostics or leave error conditions latched.
- Fuse and analog tuning fields are hardware-sensitive. Incorrect EQ, VBOOST, VREF, DCO, charge-pump, SSC, or PLL divisor programming can pass low-rate tests but fail at high link rates, with marginal cables, or after thermal drift.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support for the DCN generation that includes `dpcs_4_2_0_sh_mask.h`; missing or renamed macros should fail in resource, link encoder, or panel control table initialization.
- Mechanically verify every visible `__SHIFT` has a matching `_MASK` in lines 1-2383, allowing the known boundary exception for `RDPCSTX3_RDPCSTX_SPARE`.
- Diff this chunk against AMD's generated DPCS 4.2.0 source and against adjacent DPCS/DCN register headers where transmitter layouts are expected to repeat.
- Exercise embedded-panel power sequencing and backlight control across boot, modeset, brightness changes, blank/unblank, suspend/resume, and hotplug-like panel resets; watch for PWM enable, duty, period, lock, and stored-register restore issues.
- Exercise DisplayPort and HDMI link training on transmitter instances 0, 1, and 2, and on the beginning of transmitter 3 once later chunks are reconciled. Include multiple lane counts, link rates, DP-alt/USB-C modes, HPD IRQ, MST if available, and suspend/resume.
- Stress PLL and PHY transitions: MPLLB fractional/SSC/divider programming, ref-clock request/enable, pstate changes, lane reset/disable/request/ack handshakes, SRAM power gating, and DP-alt ownership transitions.
- Check kernel logs and hardware diagnostics for AUX/link-training timeouts, CR/EQ failures, stuck waits on `ACK`, `CLK_RDY`, `PWR_STABLE`, or `PLL_UPDATE_PENDING`, FIFO overflow/error interrupts, blank panels after resume, brightness restore failures, and connector-specific failures isolated to one `RDPCSTX` instance.

## Cross-Chunk Notes

This is the first chunk of `dpcs_4_2_0_sh_mask.h`; later chunks continue `RDPCSTX3` and the remaining generated DPCS 4.2.0 register namespace. The final per-file research document should merge this with adjacent chunks before making complete statements about all transmitter instances, all DPCS address blocks, or the full header.

### subset-b-002289: lines 2384-4766

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 2384-4766

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display controller, DisplayPort/HDMI PHY, GPIO, AUX/DDC, hotplug, and UNIPHY register fields. It contains no executable C logic; its public surface is a large set of preprocessor constants that encode field bit positions (`__SHIFT`) and field masks (`_MASK`) for hardware MMIO register programming.

The requested range contains 2,161 `#define` entries over 2,383 source lines and 207 register comment markers. It starts at the tail of the `RDPCSTX3` block with the `RDPCSTX_SPARE` mask whose shift is in the previous chunk, covers the remaining `RDPCSTX3` PHY/DPALT field definitions, covers a full `addressBlock: dpcssys_dpcs0_rdpcstx4_dispdec` transmitter/PHY lane group, then crosses into shared DCIO, GPIO/AUX pad, and UNIPHY reserved-control blocks. It ends after `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED5`, so the rest of the UNIPHY2 reserved sequence is left to the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct register accesses in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used by AMD register helpers to isolate or update that field.

The major register-field families in this chunk are:

- `RDPCSTX3` tail fields: `RDPCSTX_CNTL2`, DMCU DPALT block/clock disable controls, `PHY_CNTL0` through `PHY_CNTL17`, PHY fuse/readback fields, DPALT reserved mirror fields, driver-access blocking controls, byte-order controls, and PLL update override fields.
- `RDPCSTX4` full transmitter/PHY block: soft resets, SRAM reset, lane bit/byte order, interrupt mask and status bits, TX FIFO enables/start delay/start, CR/non-DPALT register block enables, DPALT block status, clock gates/enables/readbacks for TX/SRAM/OCLA clocks, interrupt status/clear/mask fields, TX PLL update data and CR address/data windows, TX SRAM power fields, scratch/spare fields, PHY resets, PHY power gating, lane loopback, per-lane TX reset/disable/clock-ready/data-enable/request/ack handshakes, per-lane termination/invert/equalization-bypass/high-protection bits, lane rate/width/receive-detect fields, pstate/MPLL/ref-clock/DPALT controls, MPLLB fractional-N/SSC/divider/multiplier controls, fuse-derived equalization and analog trim fields, generic in/out buses, and lane byte-order controls.
- Shared DCIO block fields: generic A/B clock selection and enable, test/reference clock selectors, UNIPHY A-E link inversion and power-sequencer selection, UNIPHY A-E channel crossbar source selection, write-command delay, pinstrap status, intercept-state status for power sequencers and RDPCS transmitters, backlight PWM frame-start display selection, genlock/swaplock pad routing masks, and soft-reset controls for UNIPHY A-G, DSYNC A-G, and power sequencers.
- DCIO GPIO/AUX pad block fields: generic GPIO masks/output/input-enable/readback fields, DDC1-DDC5 and DDCVGA clock/data masks, pull-down/pad mode/polarity/hardware pull-down/drive strength fields, genlock/swaplock pad masks and readbacks, HPD1-HPD6 mask/readback/input-enable/schmitt/slew/spare/select fields, power-sequencer GPIO routing, pad strength controls, AUX wake and receiver select fields, generic TX12 enables, AUX/DDC/HPD slew/spike/current/resistor/bias/compensation controls, GPIO receiver and pullup enables, AUX termination/swap/hysteresis controls, AUX voltage/output-drive tuning, DDC I2C mode and 1.2V pad controls, and `AUXI2C_PAD_ALL_PWR_OK` status bits.
- UNIPHY reserved blocks: `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` and the first six `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*` registers, each exposing a full-width `UNIPHY_MACRO_CNTL_RESERVED` field.

The `RDPCSTX3` and `RDPCSTX4` layouts are intentionally repetitive. The fields name parallel DisplayPort transmitter instances, so nearby definitions should usually be identical except for the `RDPCSTX3`/`RDPCSTX4` prefix and address-block placement.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of register, shift, and mask tables:

1. `dcn31_resource.c` includes `dpcs_4_2_0_offset.h` and this matching `dpcs_4_2_0_sh_mask.h`.
2. DCN 3.1 display-resource macros such as `DPCS_DCN31_REG_LIST(id)`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)` token-paste register and field names into resource tables.
3. Runtime AMD display code uses those tables through register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. Actual sequencing for PHY reset, power gating, clock gating, PLL programming, lane enablement, DisplayPort alternate-mode access arbitration, AUX/DDC pad setup, HPD sensing, and UNIPHY reset is implemented in DC/link/PHY/resource code and hardware state machines outside this generated header.

The macros only describe where bits live. They do not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, latched, reserved, or sequencing-sensitive.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in DPCS and DCIO registers:

- Transmitter and PHY control state: soft reset, SRAM reset, lane FIFO enable/start, TX FIFO errors, lane byte and bit order, CR register access, non-DPALT register block access, DPALT disable/status handshakes, and scratch/spare values.
- Clock and power state: TX/SRAM/OCLA gate disables/enables/status, external/alternate PHY reference clocks, PHY reset/test-powerdown, PHY power-gating mode, PCS/PMA/analog power enables and stable readbacks, SRAM initialization/load/bypass status, lane pstate, lane MPLL enable, DPALT four-lane and disable state, reference-clock request/enable, and memory power-state controls.
- Lane training and signal state: lane reset/disable/clock-ready/data-enable/request/ack, termination control, lane inversion, EQ bypass, high-protection enable, lane low-power/rate/width, receive-detect request/result, loopback enables, MPLLB fractional-N/SSC/divider/multiplier state, fuse-derived TX equalization and analog trim fields, voltage regulator bypass bits, and generic PHY in/out buses.
- Shared DCIO routing state: UNIPHY link inversion, channel crossbar sources, power-sequencer selection, test/reference clock output selection, genlock/swaplock routing and masking, PWM frame-start selection, pinstrap status, intercept-state status, and broad UNIPHY/DSYNC/PWRSEQ soft resets.
- Pad and sideband I/O state: generic GPIO, DDC, DDCVGA, genlock, swaplock, HPD, backlight, AUX, I2C, receiver, pullup, pull-down, drive-strength, slew, spike-filter, termination, polarity, voltage tuning, and pad-power-good fields.
- Reserved UNIPHY macro-control state: full-width reserved fields for UNIPHY1 and the start of UNIPHY2, whose hardware meaning is intentionally not described by the generated names.

Persistence is hardware-defined. Configuration fields generally remain until display link reprogramming, modeset, hotplug handling, suspend/resume, power gating, GPU reset, or ASIC reset rewrites them. Status and handshake bits may be sampled, latched, self-clearing, clear-on-write, or valid only while the relevant PHY, clock, pad, or power domain is active. This header does not record those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching register addresses for the fields described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` directly includes both DPCS 4.2.0 generated headers and initializes DCN 3.1 resource tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the `DPCS_DCN31_*` register and mask/shift list macros consumed by the resource initialization.
- Display link encoder, PHY, AUX/DDC, hotplug, panel power, clock, and hardware-sequencing code consume the initialized tables indirectly when bringing up links, programming lane and PLL state, servicing hotplug/AUX/DDC paths, and controlling display-side pads.

Behaviorally, this chunk sits below higher-level display paths. It provides field locations for low-level operations such as enabling a transmitter lane, requesting PHY clock/power state changes, observing ACK/status bits, programming DP/HDMI clocking, configuring AUX/DDC/HPD electrical pads, resetting UNIPHY/DSYNC blocks, and decoding DCIO status.

## Risks And Edge Cases

- These constants are untyped preprocessor values. An incorrect shift or mask can compile cleanly while causing the driver to update the wrong field or corrupt adjacent reserved bits.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register source, the companion offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are artificial. Line 2384 contains only the `RDPCSTX3_RDPCSTX_SPARE` mask; its shift is in the previous chunk. Line 4766 stops inside the `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*` sequence; the remaining UNIPHY2 reserved registers are in the next chunk.
- `RDPCSTX3` and `RDPCSTX4` are copy-sensitive replicated transmitter blocks. A generator error in only one instance can break one physical link while other links appear healthy.
- PHY reset, lane request/ack, pstate/MPLL, clock gate, power gate, SRAM, receive-detect, and DPALT access-block fields are sequencing-sensitive. Bad masks can cause blank displays, failed link training, unstable clocks, missed ACKs, stuck DPALT access, high bit errors, or resume-only failures.
- Interrupt and clear fields in `RDPCSTX4_RDPCSTX_INTERRUPT_CONTROL` are side-effect-sensitive. Confusing status, clear, and mask bits can cause missed FIFO/DPALT events, repeated interrupts, or latent error status.
- GPIO/AUX/DDC/HPD pad fields affect physical sideband signaling. Incorrect masks can break hotplug detection, EDID/AUX transactions, DDC pullups, pad power validation, or board-specific polarity and drive-strength tuning.
- UNIPHY/DSYNC/PWRSEQ soft reset fields have broad blast radius. A bad field definition can reset or fail to reset a whole display PHY/sync/panel-power path.
- Reserved UNIPHY fields are full-width and poorly self-describing. Driver code should avoid depending on reserved semantics unless a platform-specific hardware sequence explicitly requires it.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support with DCN 3.1 enabled. Missing or renamed DPCS 4.2.0 macros should fail where `dcn31_resource.c` initializes register, shift, and mask tables.
- Mechanically verify that complete fields in this range have matching `__SHIFT` and `_MASK` definitions, while allowing the known boundary exceptions at the starting `RDPCSTX3_RDPCSTX_SPARE` mask and ending UNIPHY2 reserved sequence.
- Cross-check every complete register group in this chunk against `dpcs_4_2_0_offset.h` and AMD's source register database.
- Diff the replicated `RDPCSTX3` and `RDPCSTX4` field layouts where hardware expects the transmitter instances to match.
- Exercise DisplayPort and HDMI link bring-up on ports mapped to the affected RDPCS/UNIPHY instances. Watch for stable link training, correct lane request/ack transitions, no stuck FIFO or DPALT events, and expected clock/power status.
- Run hotplug, EDID/DDC, DisplayPort AUX, suspend/resume, modeset, stream disable/enable, and GPU reset tests to catch pad, HPD, pstate, clock, and reset persistence mistakes.
- Validate panel/backlight and genlock/swaplock paths on systems that expose those pads, especially frame-start selection, power-sequencer GPIO routing, and GSL pad masks.
- Use register dumps during failing links to confirm that PHY power, MPLL, lane status, interrupt, GPIO, AUX/DDC, HPD, and pad-power-good fields decode correctly.

## Cross-Chunk Notes

The previous chunk owns the start of the `RDPCSTX3` register group and the shift for `RDPCSTX3_RDPCSTX_SPARE`. This chunk owns the rest of `RDPCSTX3`, all visible `RDPCSTX4`, the shared DCIO/GPIO/AUX pad section, and the start of UNIPHY reserved fields. The next chunk should continue the `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*` sequence and should be reconciled before producing whole-file claims about all DPCS 4.2.0 UNIPHY reserved coverage.

### subset-b-002290: lines 4767-7226

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 4767-7226

## Scope

This chunk is part of the generated AMD DPCS 4.2.0 ASIC register shift/mask header. It contains preprocessor constants only: each register field is represented by a `...__SHIFT` bit offset and usually a matching `..._MASK` value. There are no C functions, structs, branches, allocations, locks, direct MMIO operations, or file-backed persistence mechanisms in this range.

The slice covers 2,460 source lines, 2,089 `#define` entries, and 362 register-comment blocks. It begins inside the `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*` run at reserved register 6, covers the full `DCIO_UNIPHY3` and `DCIO_UNIPHY4` reserved macro-control ranges, then enters the `dpcssys_cr0_rdpcstxcrind` indirect CR0 transmitter/PHY register namespace. It ends at the complete `DPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_CTL2` register, immediately before `DPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_STOP`.

## Purpose

The purpose of this chunk is to publish exact bitfield metadata for DPCS 4.2.0 display PHY, UNIPHY, supervisor, PLL, lane-0 TX, and lane-0 RX-statistics registers. Runtime AMDGPU display/link code combines these generated shift and mask names with companion register-address headers and register helper macros to program or inspect hardware without open-coded bit arithmetic.

Major covered areas:

- UNIPHY macro-control reserved windows for `DCIO_UNIPHY2` tail registers and all `DCIO_UNIPHY3`/`DCIO_UNIPHY4` reserved registers 0 through 57, each exposing a full 32-bit `UNIPHY_MACRO_CNTL_RESERVED` field.
- CR0 supervisor digital controls for ID code readback, reference clock overrides, MPLLA/MPLLB divider and HDMI clock overrides, PLL enable/divider/fractional-N/SSC/charge-pump controls, prescaler and level overrides, ASIC input mirrors, bandgap, RTUNE, and analog status/override output paths.
- CR0 supervisor analog controls for prescaler, RTUNE comparator, bandgap, MPLLA/MPLLB analog miscellaneous bits, override gates, analog test bus selectors, PLL control words, DLL/divider bypasses, and reserved analog control fields.
- MPLLA/MPLLB power-control and calibration fields, including power FSM status, DAC max-range, lock/stable/power-down timers, calibration override, analog DAC output, and SSC spread-type override.
- Lane 0 ASIC/TX interface fields for lane loopback, software override inputs, ASIC-owned input mirrors, TX request/ack handshakes, rate/width/P-state, reset, inversion, detect-RX, data enable, async drive, HDMI mode, MPLL selection, repeated-lane/master-lane clock-shift handoff, and TX output mirror fields.
- Lane 0 TX power-control fields for P0/P0S/P1/P2 per-state analog enables, resets, low-power detection, electrical-idle, reference-generation, termination, RX detection, async termination, power-up timing, DCC CR-bank/DAC access, clock alignment, and TX LBERT control.
- Lane 0 RX statistic fields for load/start values, data and pattern masks, A/B pattern match controls, statistic source/shift/timer/clock controls, sample counter completion, seven statistic counters, comparator clock timing, extended pattern masks, and sample-count disable/scope-delay controls.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit position inside the target DPCS register.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask consumed by register-helper read/modify/write and decode paths.
- Prefixes such as `DCIO_UNIPHY3_`, `DPCSSYS_CR0_SUP_DIG_`, `DPCSSYS_CR0_SUP_ANA_`, and `DPCSSYS_CR0_LANE0_` are part of the generated ABI between register metadata and display/PHY tables.

Important families in this chunk include:

- UNIPHY reserved windows: `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED6..57`, `DCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED0..57`, and `DCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED0..57` define full-register reserved masks. They preserve generated address/field coverage for silicon registers that are not given public semantic field names in this header.
- Supervisor PLL digital overrides: `DPCSSYS_CR0_SUP_DIG_REFCLK_OVRD_IN`, `MPLLA/MPLLB_DIV_CLK_OVRD_IN`, `MPLLA/MPLLB_HDMI_CLK_OVRD_IN`, `MPLLA/MPLLB_OVRD_IN_0..5`, `MPLLA/MPLLB_SSC_PEAK_*`, `MPLLA/MPLLB_SSC_STEPSIZE_*`, and charge-pump override registers define refclock source/range, PLL enable, divider, VCO/fractional-N, SSC, HDMI clocking, and CP settings.
- Supervisor handoff and status: `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `MPLLA/MPLLB_ASIC_IN_*`, clock ASIC input mirrors, `ASIC_IN`, level/bandgap/CP ASIC inputs, `ANA_STAT`, and `ANA_*_OVRD_OUT` fields describe the boundary between ASIC-owned PHY control and software override/readback paths.
- Supervisor analog tuning: `SUP_ANA_PRESCALER_CTRL`, `SUP_ANA_RTUNE_CTRL`, `SUP_ANA_BG1..3`, `SUP_ANA_MPLLA/MPLLB_MISC*`, `SUP_ANA_MPLLA/MPLLB_OVRD`, `SUP_ANA_MPLLA/MPLLB_ATB*`, `SUP_ANA_MPLLA/MPLLB_CTR*`, and reserved analog control registers expose bandgap/reference, RTUNE, PLL analog bias/filter/test, reset/calibration override, and test-bus measurement fields.
- MPLL power and calibration: `SUP_DIG_MPLLA/MPLLB_MPLL_PWR_CTL_*`, `MPLL_DAC_MAXRANGE`, `MPLL_TIMERS*`, `MPLL_CAL`, `MPLL_ANA_DAC_OUT`, and `SSC_GEN_SPREAD_TYPE` define PLL power FSM controls/status, lock and stable timing, calibration forcing, DAC readback, and spread-spectrum type override.
- Lane 0 ASIC/TX override and mirror fields: `LANE_OVRD_IN`, `TX_OVRD_IN_0..5`, `TX_OVRD_OUT`, `RX_OVRD_OUT_0`, `LANE_ASIC_IN`, `TX_ASIC_IN_0..2`, `TX_ASIC_OUT`, `RX_ASIC_OUT_0`, and `TX_OVRD_OUT_1` define software-forced and hardware-observed signals around TX lane control, RX detect, clock shifting, lane-master selection, and low-level handshakes.
- Lane 0 TX power/diagnostic fields: `TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0..5`, `DCC_CR_BANK_*`, `DCC_DAC_*`, `TX_CLK_ALIGN_TX_CTL_0`, and `TX_LBERT_CTL` define analog TX enable/reset sequencing, timing delays, DCC DAC access, clock alignment, and loopback error-rate test pattern control.
- Lane 0 RX statistic fields: `RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL0..5`, `STAT_CTL0..2`, `SMPL_CNT1`, `STAT_CNT_0..6`, and `CAL_COMP_CLK_CTL` define pattern-match setup, sample timing, statistic source selection, counter enables/readback, valid-loss control, and comparator timing.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. AMDGPU display/PHY code includes this generated shift/mask header with the matching DPCS 4.2.0 register offset/address header.
2. Register descriptor tables or register helper macros pair the address constants with the shift and mask constants from this file.
3. Masked read/modify/write helpers use the `_MASK` and `__SHIFT` definitions to update individual fields or decode status fields.
4. The actual control flow occurs in hardware: supervisor clock/PLL power-up, analog calibration, RTUNE, lane-0 TX power sequencing, DCC access, LBERT diagnostics, and RX-statistic collection.

The represented hardware flow is typically: choose ASIC-owned or software-override controls, configure refclock/MPLL/prescaler/level/bandgap settings, wait for PLL power/calibration/status signals, program lane TX P-state and power-up timing, optionally access DCC or enable LBERT, and poll RX statistic counters or ASIC mirror outputs to validate signal behavior.

## State and Persistence Behavior

The file itself has no mutable state. All state described by these macros lives in GPU/display PHY hardware registers.

The hardware state represented by this chunk includes:

- UNIPHY reserved register contents for instances 2, 3, and 4.
- Supervisor clock and PLL state: refclock enable/source/range, MPLLA/MPLLB enable/divider/VCO/fractional-N/SSC/CP settings, HDMI/div clocks, power FSM state, lock state, calibration state, DAC output, and spread-spectrum mode.
- Analog support state: prescaler, RTUNE comparator/configuration/results, bandgap/reference settings, PLL analog bias/filter/test controls, test-bus selectors, PMIX outputs, and analog override enables.
- Lane 0 TX state: request/ack, P-state, rate/width, reset, data enable, detect-RX, inversion, low-power detect, HDMI mode, async drive, MPLL selection, main/pre/post cursor values, per-P-state analog enables/resets, power-up delays, DCC DAC access, and lane-master clock-shift handoff.
- Lane 0 diagnostic/statistic state: LBERT mode/pattern/error injection, RX pattern masks, match selectors, statistic source and clock controls, sample-count completion, seven statistic counters, valid-loss control, and comparator clock timing.

Persistence is limited to hardware register lifetime. Values may need reprogramming after GPU reset, display engine reset, DPCS/PHY reset, power gating, suspend/resume, hotplug retraining, link-rate changes, or modeset-driven PHY reconfiguration. Driver policy and board/silicon tables remain the durable source of truth.

## Dependencies

This chunk depends on matching generated DPCS 4.2.0 register-address headers. Shift and mask constants alone do not identify where a register is located.

It also depends on:

- AMD display and PHY register-helper infrastructure that consumes generated `__SHIFT` and `_MASK` names for masked reads, writes, updates, and polling.
- The silicon register database or generator that emits this header and the companion offset headers.
- Link encoder, PHY bring-up, clock, power-management, diagnostics, and validation code that programs CR0 supervisor and lane-0 DPCS registers.
- Correct instance mapping between `DCIO_UNIPHY2/3/4`, `DPCSSYS_CR0_SUP_*`, and `DPCSSYS_CR0_LANE0_*` macro prefixes and their corresponding hardware address blocks.

Because this is generated silicon metadata, manual edits are risky unless synchronized with the register database, address headers, generated register tables, and all consumers that reference these exact names.

## Integration Points

Primary integration points are the macro names consumed by AMDGPU register tables and masked register helpers. A consumer naming a field such as `DPCSSYS_CR0_SUP_DIG_REFCLK_OVRD_IN__REF_CLK_EN`, `DPCSSYS_CR0_SUP_DIG_MPLLA_OVRD_IN_0__MPLLA_EN`, `DPCSSYS_CR0_LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0__TX_P0_ANA_CLK_EN`, or `DPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_CNT_0__STAT_CNT_0` relies on this header for the correct bit position and mask.

Integration surfaces include:

- Clock/PLL bring-up: refclock, MPLLA/MPLLB dividers, HDMI clock division, fractional-N, SSC, power FSM, lock timing, DAC, and calibration fields.
- Analog support and calibration: prescaler, bandgap, RTUNE, PLL analog controls, analog override outputs, PMIX fields, and test-bus measurement selectors.
- ASIC/software ownership handoff: `*_OVRD_IN`, `*_OVRD_OUT`, and `*_ASIC_IN/OUT` fields that let software override, observe, or debug hardware-owned PHY signals.
- Lane 0 transmit path: TX request/ack, rate/width/P-state, reset, detect-RX, HDMI mode, main/pre/post cursor, per-power-state analog enables, power-up timers, DCC DAC access, and clock alignment.
- Diagnostics and validation: TX LBERT controls, RX statistic pattern matchers, sample counters, statistic counters, valid-loss handling, comparator timing, and ASIC mirror registers.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent fields in compact 16-bit DPCS registers, causing PLL bring-up, calibration, TX power sequencing, or statistic collection failures.
- Reserved UNIPHY full-register masks are broad by design. If used carelessly, they can enable writes to undocumented hardware state that should remain generator- or firmware-controlled.
- Override fields are sensitive. A wrong mask can force software ownership of ASIC-controlled refclock, MPLL, bandgap, TX, RX, or lane-master signals and prevent hardware from completing normal training or calibration.
- PLL and timing fields are order and delay sensitive. Bad masks in MPLL power, lock, stable, power-down, or TX power-up timing registers can produce intermittent display bring-up failures rather than deterministic compile failures.
- Lane-prefix or address-block mistakes can compile cleanly while targeting the wrong UNIPHY instance or lane-0 register block, creating failures that only appear on certain connector, lane-count, or link-rate configurations.
- Status and clear fields can have side effects. Misdecoding RTUNE status, MPLL lock/calibration bits, DCC ack, RX statistic done bits, valid-loss clear/control, or LBERT trigger fields can hide real hardware failures or leave stale status latched.
- The chunk starts mid-family and ends at a boundary before the next RX statistic register. Per-file synthesis should reconcile the earlier `DCIO_UNIPHY2` reserved registers and the following `RX_STAT_STAT_STOP` fields from neighboring chunks.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DPCS 4.2.0 display/PHY code builds without missing `DCIO_UNIPHY*`, `DPCSSYS_CR0_SUP_*`, or `DPCSSYS_CR0_LANE0_*` shift/mask symbols.
- Generated-table sanity: each field is paired with the correct companion DPCS address constant and retains the expected repeated layout across MPLLA/MPLLB and UNIPHY instances.
- Display/link smoke tests: hotplug, modeset, lane-rate changes, link retraining, suspend/resume, GPU reset, and power-gating recovery on displays that exercise CR0 and lane-0 PHY paths.
- PHY bring-up checks: reference clock acknowledgement, MPLLA/MPLLB power FSM and lock status, calibration completion, RTUNE comparator/status readback, bandgap/reference state, and TX request/ack transitions.
- Lane TX checks: P0/P0S/P1/P2 sequencing, analog clock/data/refgen/termination enables, power-up timers, detect-RX, electrical-idle, DCC DAC ack/range/address behavior, and clock-alignment settings.
- Diagnostic checks: LBERT mode/error injection behavior, RX statistic match patterns, sample-count done bits, counter readbacks, valid-loss clear/control, comparator-clock timing, and ASIC input/output mirror consistency.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dpcs_4_2_0_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.

### subset-b-002291: lines 7227-9584

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 7227-9584

## Purpose

This chunk is a middle slice of AMD's generated DPCS 4.2.0 shift/mask register-field header. It contains no executable C logic; it publishes preprocessor constants for bit positions and masks in the DPCS control-register space used by AMDGPU Display Core. The matching address constants live in `dpcs_4_2_0_offset.h`, and both headers are included by `display/dc/resource/dcn31/dcn31_resource.c` for DCN 3.1 hardware resource construction.

The range covers 2,139 `#define` entries and 219 register comment groups. It starts inside `DPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_CTL2` at the `SCOPE_DLY_2` mask, continues through lane 0 digital/analog transmit override and status registers, then covers most of lane 1 digital ASIC, TX/RX power, CDR, adaptation, statistics, MPHY, digital-to-analog override, analog TX, and the start of analog RX clock registers. It ends after the first two `DPCSSYS_CR0_LANE1_ANA_RX_CLK_2` shift definitions; that register's remaining fields and masks are outside this chunk.

Although this repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, or callbacks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for packing, unpacking, or updating a register field.
- `<REGISTER>__<FIELD>_MASK`: mask used to isolate the field in a 16-bit-style DPCS register value represented as a C integer literal.

Major register families in this chunk are:

- `DPCSSYS_CR0_LANE0_DIG_RX_STAT_*`: tail of lane 0 receive-statistics control, including sample-count disable and `SC1_STOP`.
- `DPCSSYS_CR0_LANE0_DIG_ANA_TX_*`: lane 0 digital outputs into analog TX controls. Fields cover TX clock shift, data/refgen/VCM/word-clock/MPLL enables, reset, serial enable, data rate, div4, RX detect, override enable, termination-code override, EQ override, TX DCC DAC override, fast start, clock loopback, and AC JTAG enable.
- `DPCSSYS_CR0_LANE0_DIG_ANA_STATUS_0`: lane 0 analog status bits for TX clock-shift acknowledgement, RX detect results, loopback state, RX calibration/scope data, TX DCC calibration result, and EQ mux status.
- `DPCSSYS_CR0_LANE0_ANA_TX_*`: lane 0 direct analog TX control and diagnostics, including measurement override, power override, alternate bus/JTAG data, ATB measurement selectors, DCC DAC and control, termination code, clock override, miscellaneous peaking/slew/vreg/ring controls, and reserved registers.
- `DPCSSYS_CR0_LANE1_DIG_ASIC_*`: lane 1 ASIC-facing override and live signal registers. These expose lane-level reset, TX/RX power states, TX EQ and termination inputs, RX CDR/VCO, AFE/DFE/adaptation, slicer, signal-detect, MPHY, and OCLA-related fields.
- `DPCSSYS_CR0_LANE1_DIG_TX_PWRCTL_*`: lane 1 TX power-state configuration for P0/P0S/P1/P2, power-up timers, DCC CR bank access, DCC DAC control/range/selection/ack/address, TX clock alignment control, and TX LBERT controls.
- `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_*`, `DPCSSYS_CR0_LANE1_DIG_RX_VCOCAL_*`, `DPCSSYS_CR0_LANE1_DIG_RX_CDR_*`, and `DPCSSYS_CR0_LANE1_DIG_RX_DPLL_*`: lane 1 RX power-state, VCO calibration, CDR, DPLL frequency and frequency-bound controls/status.
- `DPCSSYS_CR0_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX adaptation configuration and status for ATT, VGA, CTLE, DFE taps, data/error VDAC offsets, slicer controls, reset, DAC control selection, and CR bank access.
- `DPCSSYS_CR0_LANE1_DIG_RX_STAT_*`: lane 1 receive pattern/statistics controls, sample counters, match/mask registers, statistics counters, calibration comparator clock control, and stop control.
- `DPCSSYS_CR0_LANE1_DIG_MPHY_*`: lane 1 MPHY low-speed PWM, termination, and analog PWM clock-stable count fields.
- `DPCSSYS_CR0_LANE1_DIG_ANA_*`: lane 1 digital override outputs to analog TX/RX, including TX EQ/termination/DCC/fast-start controls, RX control/power/VCO/calibration/DAC/AFE/scope/slicer/IQ/signal-change/status controls, RX termination-code override, MPHY override, and signal-detect override.
- `DPCSSYS_CR0_LANE1_ANA_TX_*`: lane 1 analog TX measurement, power, ATB, DCC, termination, clock, miscellaneous, and reserved registers.
- `DPCSSYS_CR0_LANE1_ANA_RX_CLK_1` and partial `DPCSSYS_CR0_LANE1_ANA_RX_CLK_2`: start of lane 1 analog RX clock controls such as CDR VCO startup, temperature compensation, CDR override, clock enable override, IQ phase-adjust shift, and RX loopback clock shift.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes the header and passes the constants into register-helper macros:

1. DCN 3.1 resource code includes `dpcs_4_2_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste register names into offset, shift, and mask table initializers.
3. DCN resource constructors wire those tables into display/link/PHY-related objects.
4. Runtime paths use register helpers such as read, write, update, get, and set operations; the helpers combine the offset constants with these field masks and shifts to touch individual hardware bits.

The macros do not define sequencing. Consumers must still order lane reset release, TX/RX power transitions, PLL/CDR/VCO programming, DCC/termination/EQ calibration, receive adaptation, statistic sampling, loopback or LBERT diagnostics, and suspend/resume restoration according to silicon requirements.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes DPCS hardware state in CR0 lane registers:

- TX state for lane 0 and lane 1: enable/reset/serial/data-rate controls, word/MPLL clocks, termination code, EQ pre/post/leg-pull settings, DCC DAC calibration controls, fast start, RX detect, and loopback/AC-JTAG paths.
- RX state for lane 1: power states and timers, VCO calibration controls/status, CDR/DPLL programming, adaptation configuration/status, AFE/DFE/slicer/DAC/IQ/scope controls, signal-detect and MPHY low-speed controls.
- Diagnostic state: LBERT enable/error controls, OCLA, ATB measurement selectors, statistics sample/match/count registers, calibration comparator clocking, and status bits for calibration, RX detect, scope, DCC, and analog acknowledgements.
- Override state: many fields explicitly select between ASIC-driven signals and software/debug override values. Incorrectly leaving override-enable bits set can decouple the PHY lane from normal display link training and power management.

Persistence is hardware-defined. Programmed control fields generally last until modeset/link reprogramming, lane power-down, power-gating, suspend/resume, GPU reset, or ASIC reset. Status, acknowledgement, calibration, statistic, and error fields may be read-only, sticky, self-clearing, write-one-to-clear, or only valid while the relevant DPCS clocks and power domains are active. This generated header does not encode those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DPCS 4.2.0 register database and especially with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides matching `ixDPCSSYS_*` register addresses for the field masks in this file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which directly includes both DPCS 4.2.0 headers.
- The AMD Display Core register-helper layer, which expects consistent register, shift, and mask naming when building register tables and performing read-modify-write operations.
- Neighboring DPCS generated headers such as `dpcs_4_2_2_*`, `dpcs_4_2_3_*`, and older `dpcs_3_1_4_*`, which indicate related ASIC generations and are useful comparison points when validating generated-field drift.

The most direct behavioral integration is display-link PHY handling: DisplayPort/USB-C style lane bring-up, lane power management, link training, RX/TX calibration, loopback and production diagnostics, and low-level PHY debug or characterization flows.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask compiles cleanly but can write the wrong DPCS bit, corrupt an adjacent field, or silently break link training, lane power, calibration, or diagnostics.
- The file is generated metadata. Manual edits risk divergence from AMD's register database, the matching offset header, firmware assumptions, and silicon documentation.
- The chunk boundary is artificial. It starts after the `DATA_DLY_SEL_2` mask for `LANE0_DIG_RX_STAT_STAT_CTL2`, so full pair accounting for that register requires the previous chunk. It ends before the remaining `LANE1_ANA_RX_CLK_2` shifts and all masks, so full pair accounting for that register requires the next chunk.
- Lane 0 and lane 1 register families are highly repetitive but not identical. Assuming lane 0 field names or semantics apply to lane 1 can miss lane-specific RX, MPHY, VCO, adaptation, or analog additions.
- Override-enable fields are high risk. Debug overrides for TX/RX power, CDR, VCO, EQ, termination, clock, loopback, DCC, and MPHY can leave the PHY in a state normal display code does not expect.
- Reserved and `NC*` fields are exposed as masks. Consumer code should avoid writing non-reset values to those bits unless directed by validated hardware sequences.
- Calibration and status fields are timing-sensitive. Polling before clocks or power are stable can produce false failures; clearing sticky/statistic fields with the wrong mask can lose diagnostic evidence.

## Test Signals

Useful validation is a mix of generated-header checks and hardware behavior:

- Build AMDGPU display support for DCN 3.1. Include or token-paste regressions should surface where `dcn31_resource.c` and register helpers consume DPCS 4.2.0 symbols.
- Mechanically verify that fields in this range have matching `__SHIFT` and `_MASK` definitions where the complete register lies within the range, while allowing the known boundary exceptions at `LANE0_DIG_RX_STAT_STAT_CTL2` and `LANE1_ANA_RX_CLK_2`.
- Compare this slice with the matching `dpcs_4_2_0_offset.h` address range from `ixDPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_CTL2` through `ixDPCSSYS_CR0_LANE1_ANA_RX_CLK_2`.
- Diff against adjacent generated DPCS versions when an ASIC stepping claims compatible lane-register layout.
- On hardware, exercise display link bring-up, retraining, hotplug, suspend/resume, GPU reset, low-power state entry/exit, high link rates, multiple lane counts, and USB-C/DP alternate-mode paths where DPCS lane programming is active.
- For diagnostics, run loopback or LBERT paths where available, inspect DCC/VCO/CDR/adaptation status convergence, confirm RX statistic counters and stop controls behave as expected, and watch kernel logs for link training timeouts, stuck power-state transitions, calibration failures, and resume-only display loss.

## Cross-Chunk Notes

This chunk is part of the larger `dpcs_4_2_0_sh_mask.h` generated header. Earlier chunks define the header prologue and prior DPCS/CR0 lane 0 RX-stat fields; later chunks continue lane 1 analog RX controls and the rest of the DPCS 4.2.0 field namespace. The final per-file research document should merge adjacent chunks before making whole-file claims about all DPCS registers or complete lane coverage.

### subset-b-002292: lines 9585-11943

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 9585-11943

## Scope And Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.0 register bitfield mask header. It contains C preprocessor constants for shift positions and bit masks, not executable code. The constants describe how the display PHY/DPCS register interface encodes lane-specific TX, RX, analog, calibration, adaptation, status, and test/debug fields.

The requested range starts inside the lane 1 analog RX clock group, then completes lane 1 analog RX control/measurement fields, covers almost all of lane 2's digital and analog PHY bitfield definitions, and ends at the beginning of lane 3 digital ASIC lane override fields. The dominant pattern is one `__SHIFT` macro and one `_MASK` macro for each hardware register field. Driver code elsewhere can combine these definitions with register address definitions and AMD's register access helpers to build read-modify-write values without hard-coding bit positions.

## Register Groups Covered

The line range contains 2,141 `#define` lines. Major source-aligned blocks are:

- Lane 1 analog RX tail: `DPCSSYS_CR0_LANE1_ANA_RX_CLK_2` through `DPCSSYS_CR0_LANE1_ANA_RX_RESERVED1` define IQ phase adjustment, loopback clock, CDR/deserializer controls, slicer controls, AFE/DFE/deserializer/loopback power overrides, signal-detect threshold/response, calibration mux selection, ATB/regulator measurement controls, and reserved low-byte fields.
- Lane 2 digital ASIC override and direct inputs/outputs: `DPCSSYS_CR0_LANE2_DIG_ASIC_*` defines software override versions and normal ASIC versions of lane loopback, TX request/pstate/rate/width/MPLL/data enable, cursor/equalization, detect-RX, inversion, low-power detect, reset, RX CDR/VCO load values, adaptation enables, termination, ACK/valid/status, OCLA, repeat/master-lane clock synchronization, and MPHY/PWM controls.
- Lane 2 TX power control: `DPCSSYS_CR0_LANE2_DIG_TX_PWRCTL_*` describes per-power-state TX analog/digital enable recipes for P0, P0S, P1, and P2 plus power-up timing fields and DCC DAC control registers.
- Lane 2 RX power, VCO, CDR, adaptation, and statistics: `DPCSSYS_CR0_LANE2_DIG_RX_*` includes RX pstate recipes, RX power-up timers, VCO calibration control/time/status, XAUI comma mask, LBERT control/error count, CDR/SSC/DPLL controls and status, adaptation configuration/status/reset, pattern matching/stat counters, and statistic stop controls.
- Lane 2 digital-to-analog override outputs and analog controls: `DPCSSYS_CR0_LANE2_DIG_ANA_*` and `DPCSSYS_CR0_LANE2_ANA_*` define the values driven from digital logic into analog TX/RX blocks, plus direct analog TX/RX register fields for termination, DCC, ATB, EQ, scope, IQ phase, slicer, VCO, calibration DAC, power, and status.
- Lane 3 boundary: the final lines start `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`, proving this chunk ends mid-register-group before the complete lane 3 block.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The public interface is a generated macro namespace:

- `DPCSSYS_CR0_LANE<n>_*__<field>__SHIFT` gives the low bit position for a field.
- `DPCSSYS_CR0_LANE<n>_*__<field>_MASK` gives the unshifted 32-bit mask literal, usually occupying the low 16 bits because these CR lane registers appear to expose 16-bit register payloads through a wider C type.
- `RESERVED_*`, `NC*`, and `RSVD_*` fields document non-functional or undocumented bit ranges and are still emitted as masks so generated tables preserve exact register layout.

The intended consumers are AMDGPU display/DPCS code paths that write memory-mapped or indirect control registers using kernel register helper macros such as field preparation, field get/set, or read-modify-write wrappers. The source path under `drivers/gpu/drm/amd/include/asic_reg/dpcs` indicates this header participates in ASIC-specific display register programming, not in Ceph filesystem logic despite the repository subtree prefix.

## Control Flow

This header has no runtime control flow. Hardware control flow is implied by the register group layout:

- Override registers pair a data field with an `*_OVRD_EN`, `*_OVRD`, or `EN` bit. Driver code must set the enable bit when it wants the software-provided value to replace the normal PHY/ASIC signal.
- Pstate registers encode predefined TX and RX power sequencing states. Higher-level link training, mode-set, suspend/resume, or hotplug paths can select pstate behavior indirectly by programming these fields.
- Time registers encode wait/settle counters such as `TX_REFGEN_EN_TIME`, `TX_VCM_HOLD_TIME`, `RX_AFE_EN_TIME`, `RX_CLK_EN_TIME`, and VCO startup/update/counter settle times. These constants let sequencing code pack timing parameters consistently with hardware layout.
- Status registers expose ACK, valid, detect-RX, calibration done/result, VCO counter/final frequency, adaptation code, and LBERT error count fields for polling or diagnostics.

Because the chunk spans repeated lane blocks, lane index is part of the contract. A caller using a lane 1 mask against a lane 2 address, or using the partial lane 3 definitions at the end without the continuation in the next chunk, would program or decode the wrong hardware field.

## State And Persistence Behavior

The file itself is compile-time-only and persists no runtime state. The state affected by consumers is hardware register state in the display PHY:

- TX/RX enable, reset, clock, data, pstate, loopback, polarity inversion, width, rate, MPLL selection, and low-power fields control live lane behavior.
- Analog override fields can force TX term codes, EQ/cursor values, RX AFE gain/attenuation/CTLE, slicer controls, IQ phase, calibration muxes, VCO tuning, and termination behavior.
- Calibration, adaptation, DPLL, CDR, and SSC fields influence hardware training algorithms and may affect link stability until overwritten or the PHY is reset.
- Status and counter fields are read-only or observation-oriented from the driver's perspective, but their interpretation depends on prior programming of enable, reset, timing, and pattern-match fields.

Persistence is at the hardware register level. Values can survive across parts of a mode-set or training sequence until a lane reset, block reset, power-gate transition, or subsequent register write changes them. The macros themselves impose no locking, ordering, polling, or reset semantics.

## Dependencies And Integration Points

This header depends on a matching register address header for `dpcs_4_2_0` and on the AMDGPU display stack's common register access machinery. It integrates with:

- DPCS/RDPCS display link programming for DisplayPort/HDMI/PHY bring-up.
- Lane training and equalization code that sets TX cursors, post/pre emphasis, rate, width, data enable, CDR, DPLL, and adaptation parameters.
- Power management paths that program TX/RX pstate recipes and power-up/down timing.
- Debug, manufacturing, and validation tools that use ATB, OCLA, LBERT, scope, DCC DAC, VCO, and statistic counter fields.
- ASIC register generation tooling. The highly regular naming and repeated lane layout indicate this file is generated from hardware register specifications; manual edits would be fragile.

The constants are tightly coupled to the DPCS 4.2.0 hardware revision. Reusing them for another ASIC revision requires confirming that the address map and bitfield layout are identical.

## Risks And Edge Cases

- This chunk starts and ends mid-logical sequence: lane 1 `ANA_RX_CLK_2` begins before line 9585, and lane 3 `DIG_ASIC_LANE_OVRD_IN` continues after line 11943. Any merged documentation must reconcile adjacent chunks to avoid treating partial groups as complete.
- Mask/shift mismatches in generated headers are high-impact. A one-bit error in pstate, reset, VCO, DPLL, or override-enable fields can produce display link bring-up failures, unstable clocks, or lanes stuck in reset/low power.
- Reserved and `NC` fields are exposed as masks. Driver code should preserve reserved bits during read-modify-write unless hardware documentation explicitly requires writing a value.
- Many fields are only meaningful when paired with an override enable or self-clear-disable bit. Writing the value field alone may have no effect; leaving override enables set after diagnostics may interfere with normal link training.
- Lane-specific duplication invites copy/paste mistakes. Lane 2 masks should be used with lane 2 register addresses; lane 1 and lane 3 names are not interchangeable even when bit layouts match.
- Timing fields are packed into small bit widths. Out-of-range software values must be clamped or validated before shifting, otherwise high bits can spill into adjacent fields if the caller does not mask properly.
- Status fields such as VCO calibration done, RX adaptation status, LBERT overflow, and detect-RX results may be transient. Polling code needs hardware-appropriate timeouts and reset/clear handling outside this header.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-generation, and hardware-oriented:

- Build tests that include `dpcs_4_2_0_sh_mask.h` from representative AMDGPU display translation units and catch macro spelling or duplicate-definition problems.
- Generated-header consistency checks that verify every `__SHIFT` field has the expected `_MASK`, masks are contiguous for multi-bit fields, masks match the documented shift and width, and repeated lane 1/lane 2 layouts agree where the hardware spec says they should.
- Register access unit tests or static checks around field packing helpers to ensure values are masked before shifting and reserved bits are preserved in read-modify-write paths.
- Hardware or emulator tests for lane 2 link bring-up, pstate transitions, hotplug detect, DisplayPort/HDMI training, suspend/resume, and lane reset sequences.
- Diagnostic tests for ATB/OCLA/LBERT/stat counters, including counter overflow (`OV14`), sample stop, pattern match/mask programming, and VCO calibration status polling.
- Regression signals in kernel logs and display tests: link training failures, blank screens after mode-set, unstable high-bandwidth modes, repeated PHY reset/retrain messages, or mismatched RX/TX ACK/status polling after changes to generated register headers.

### subset-b-002293: lines 11944-14320

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 11944-14320

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY/controller register fields. It contains no executable C logic; its public surface is a set of preprocessor constants that encode bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS hardware register fields.

The requested range contains 2,122 `#define` entries over 2,377 lines. It starts immediately after the `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` shift definitions, so the first lines are that register's masks. It then covers lane 3 ASIC/TX/RX power, analog TX, raw common PLL/control, raw lane PCS/PMA, FSM, IRQ, TX/RX control, and ATE override fields. The range ends at `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_ATE_TX_OVRD_IN_1`, with the next register `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_MASTER_MPLL_LOOP` beginning just after the requested chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the DPCS register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or update that field.

The main register-field families in this chunk are:

- Lane 3 ASIC interface and override fields: `DPCSSYS_CR0_LANE3_DIG_ASIC_*` describes TX/RX request, ACK, pstate, rate, width, MPLL select, data enable, reset, invert, low-power detect, receive-detect request/result, beacon, async drive/data, loopback, HDMI mode, MPHY mode, clock-ready, and cross-lane clock/sync handshakes.
- Lane 3 TX power and timing fields: `TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` carry analog refgen, VCM hold, clock, word clock, reset, serial enable, digital clock, data enable, receive-detect allowance, Vboost allowance, and DCC compensation bits. `TX_PWRUP_TIME_0-5` encode staged enable/reset/rxdet timing, skip controls, and fast receive-detect controls. The DCC CR bank and DCC DAC registers expose address/data, control/range/select, request/update, bin-hot, ACK, and DAC address fields.
- Lane 3 RX statistic and diagnostic fields: `RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL0-5`, `STAT_CTL0-2`, `SMPL_CNT1`, `STAT_CNT_0-6`, `CAL_COMP_CLK_CTL`, and `STAT_STOP` define sample-count start/stop, pattern masks/matches, data masks, counter enables, source selectors, clock controls, valid-loss clear/control, calibration comparison precharge/reference divider, and done bits.
- Lane 3 digital-to-analog TX override/readback fields: `DIG_ANA_TX_OVRD_OUT`, termination-code overrides, TX equalization override banks, DCC DAC override banks, `DIG_ANA_STATUS_0`, and `DIG_ANA_TX_OVRD_OUT_2` expose analog clock/data/refgen/reset/serial/MPLL enable controls, EQ leg pull enables/directions, pre/post/equalization mux controls, DCC calibration controls, RX detect readbacks, clock-shift ACK, loopback, ACJTAG, and fast-start controls.
- Lane 3 raw analog TX fields: `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1/2`, `ANA_TX_DCC_DAC`, `ANA_TX_DCC_CTRL1`, `ANA_TX_TERM_CODE`, `ANA_TX_TERM_CODE_CTRL`, `ANA_TX_OVRD_CLK`, `ANA_TX_MISC1-3`, and reserved registers describe analog test bus selection, forced ATB signals, alt-bus/JTAG/ring oscillator hooks, DCC DAC programming, termination-code programming and update/reset strobes, MPLL/word-clock/loopback overrides, Vref selection, peaking/slew/vreg controls, and reserved/NC bits.
- Raw common control and MPLL fields: `RAWCMN_DIG_CMN_CTL`, `MPLLA_*`, `MPLLB_*`, `CMN_CTL_1`, `MPLL_STATE_CTL`, `TX_CAL_CODE`, `SRAM_INIT_DONE`, `OCLA`, `SUP_ANA_OVRD`, ID-code registers, firmware ID registers, AON RTUNE values, AON SRAM/power-gate/supervisor/resistor/reference-range overrides, VREF stats, and MPLL power-down time fields. These govern common PHY reset, MPLLA/MPLLB divider/BW/SSC/fractional override inputs, HDMI mode override, RTUNE request, PWM clock selection, MPLL state timing, SRAM init completion, debug probe selection, analog supervisor overrides, calibration codes, and always-on common tuning state.
- Raw lane PCS transfer fields: `RAWLANE0_DIG_PCS_XF_TX_*` and `RX_*` describe TX/RX pstate, low-power detect, width, rate, MPLL select/enable, master MPLL states, reset/request/detect-rx overrides, Vboost/iboost/beacon overrides, PCS input/output ACKs, RX adaptation controls, RX data-enable override, RX LOS threshold, VCO/ref load values, equalization status, RX valid/clock controls, adaptation ACK/FOM, directed TX pre/main/post cursor feedback, lane number, ATE override inputs, RX EQ override values, TX/RX termination controls, and PH2 calibration signals.
- Raw lane FSM and IRQ fields: `RAWLANE0_DIG_FSM_*` covers FSM override, memory/status monitors, fast RX startup/adaptation/AFE/DFE/bypass/reflvl/IQ calibration enables and status, fast supervisor/TX common-mode/RX detect/RX power-up/VCO wait/VCO cal controls, common calibration status, continuous adaptation/calibration flags, CR lock, TX DCC flags/status, OCLA, TX EQ update, RCAL status, and RX IQ phase offset. `RAWLANE0_DIG_IRQ_CTL_*` covers RX/TX reset and request IRQs, RX rate/pstate/adaptation IRQs, clear registers, masks, lane transceiver-mode IRQs, PH2 calibration IRQs, loopback IRQs, and DCC on-demand IRQ.
- Raw lane PMA and TX/RX control fields: `PMA_XF_*` describes lane MPLLA/MPLLB enable overrides, supervisor state overrides, TX/RX PMA override outputs, PMA ACKs, lane RTUNE request/ACK, MPHY PWM/termination overrides, RX adaptation IQ phase adjustment, TX FSM/clock controls, TX DCC continuous status, TX/RX OCLA probes, RX FSM enable/rate-change behavior, LOS mask timing, RX data-enable override timing, and continuous off-cancel/adaptation status.
- ATE-specific PCS override fields at the end of the chunk: `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, and `PCS_XF_ATE_TX_OVRD_IN_1` mirror normal RX/TX rate/width/pstate/loopback/MPLL/beacon/Vboost/iboost/detect-rx/async-data controls for automated test or manufacturing/debug flows.

Most masks in this range are 16-bit style values ending in `L`, matching the DPCS indirect-register field width used by these lane, raw common, and raw lane blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 4.2 resource/display code includes the matching DPCS 4.2.0 offset header and this shift/mask header.
2. Register-list and shift/mask-list macros token-paste DPCS register and field names into tables used by AMD display resource, link encoder, PHY, AUX/link-training, clock-source, and hardware-sequencing code.
3. Runtime display code uses AMD register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` with those offset, shift, and mask tables.
4. Hardware and driver code outside this generated header perform the actual sequencing for lane power, PLL programming, link training, RX adaptation, DCC calibration, IRQ handling, and debug/statistic readback.

The macros in this chunk describe where bits live; they do not encode which fields are read-only, write-one-to-clear, self-clearing, latched, sequencing-sensitive, or clock-domain dependent.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR0 lane 3, raw common, and raw lane 0 DPCS registers:

- TX lane state: pstate programming, analog and digital clock enables, refgen/VCM/word-clock/reset/serial/data enable, receive-detect timing, Vboost and DCC compensation policy, PLL select/enable, beacon/async drive state, lane master/cross-lane sync, and TX equalization/termination values.
- RX lane state: request/reset/ACK handshakes, rate/width/pstate, RX valid/clock, low-power-detect, LOS thresholds, adaptation request/continuous/off-cancel controls, VCO/ref load values, equalization status and override values, IQ phase offset/adjustment, and RX data-enable override timing.
- Common PHY state: functional reset, MPLLA/MPLLB divider, bandwidth, SSC, fractional controls, init-calibration disables, RTUNE request and values, HDMI mode, PWM clocking, MPLL state timing/bank selection, SRAM init done, firmware and PCS ID readbacks, AON power-gate/supervisor/resistor/reference-range overrides, VREF stats, and MPLL power-down time.
- Diagnostic and test state: RX statistic match/mask/counter registers, sample counters, valid-loss controls, OCLA debug selectors, analog test bus selectors, alternate bus/JTAG hooks, DCC DAC debug controls, ATE override surfaces, PH2 calibration request/ACK, and directed TX coefficient feedback.
- Interrupt state: RX and TX reset/request/rate/pstate/adaptation/PH2/lane-mode/loopback/DCC IRQ status, clear, and mask fields.

Persistence is hardware-defined. Configuration fields generally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, IRQ, statistics, calibration, and handshake fields may be latched, clear-on-write, sampled, self-clearing, or valid only while the relevant lane/common clock and power domains are active. This generated header does not record those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_*` register offsets for the field names described here.
- AMD display DCN/DPCS resource code includes generated offset and shift/mask headers to initialize register, shift, and mask tables for the display engine version that owns DPCS 4.2.0.
- Link encoder, PHY, AUX/link-training, clock-source, and hardware-sequencing code consume those initialized tables indirectly when programming display PHY lanes, shared MPLL/reference-clock state, lane training, and debug or interrupt paths.
- Firmware and hardware state machines interact with the same register fields, especially for MPLL state, SRAM init, RX adaptation/calibration, DCC, RTUNE, IRQ latching, ATE, and PMA/PCS handshakes.

Behaviorally, this range sits below the user-facing display stack. It describes the low-level bit layout used when the driver enables or powers down TX/RX lanes, selects MPLLA/MPLLB clocking, configures HDMI/DisplayPort PHY behavior, runs receiver calibration/adaptation, handles lane-level interrupts, or reads low-level diagnostic counters.

## Risks And Edge Cases

- These constants are untyped preprocessor values. An incorrect shift or mask can compile cleanly while writing the wrong DPCS field, corrupting a reserved bit, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from the authoritative AMD register database, the matching offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are artificial. This slice starts with masks for `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`; the matching shifts are in the previous chunk. The next chunk continues with `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_MASTER_MPLL_LOOP` and later raw-lane fields.
- Lane 3 and raw lane 0 naming are both present in the same range. Consumers must pair these masks with the correct offset and register-list macro; assuming that all fields in the chunk belong to one lane numbering scheme would be wrong.
- Power, PLL, and calibration fields are sequencing-sensitive. Bad masks for pstate enables, MPLL dividers/BW/SSC/fractional controls, DCC DAC handshakes, VCO/ref load values, RTUNE, or RX adaptation controls can cause link-training failure, unstable clocks, blank displays, high error rates, or resume-only regressions.
- ACK, IRQ, clear, and mask fields are side-effect-sensitive. Confusing status, clear, and mask bits can produce missed lane events, repeated interrupts, stuck ACK waits, or failure to observe adaptation/rate/pstate changes.
- Raw PCS/PMA override and ATE fields can bypass normal state-machine control. Incorrect masks may force reset/request/data-enable/loopback/MPLL/termination behavior that is difficult to diagnose from higher-level display state.
- Analog and diagnostic fields are high-risk despite being debug-oriented. Wrong ATB, termination, DCC, equalization, Vref, or alt-bus masks can hide debug evidence or alter PHY electrical behavior.
- Repeated lane and PLL register groups are copy-sensitive. A generator or merge error can affect only one lane, one PLL bank, or one status block while nearby groups appear correct.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.0. Missing or renamed macros should fail where register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this range has an expected `__SHIFT`/`_MASK` pair, allowing the known boundary exception where `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` shifts are just before this chunk.
- Cross-check this slice against `dpcs_4_2_0_offset.h` so every complete register group in the chunk has a corresponding `ixDPCSSYS_*` offset.
- Diff against AMD's authoritative DPCS 4.2.0 register database and nearby generated variants such as `dpcs_4_0_0_sh_mask.h`, `dpcs_4_1_0_sh_mask.h`, or older DPCS headers where register layouts are expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available PHY lanes, rates, widths, and power states. Expected signals are stable link training, correct lane power transitions, correct MPLL selection, no false lane IRQs, and no stuck ACK/status bits.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in power, pstate, PLL, calibration, IRQ, and AON common fields.
- Validate high-bandwidth and clock-sensitive modes that stress MPLLA/MPLLB divider, bandwidth, SSC, fractional, HDMI-mode, and PWM clock controls. Watch for blank displays, PHY lock failures, retraining loops, display corruption, or audio/video timing instability.
- Use register dumps or PHY debug traces during failing links to confirm RX adaptation, VCO/ref load, equalization, DCC status, RTUNE, FSM status, IRQ clear/mask, and statistic counter fields decode correctly.
- Exercise diagnostic paths where available: OCLA, RX statistic match/count controls, analog test bus/readback fields, directed TX coefficient feedback, PH2 calibration, loopback controls, and ATE overrides.

## Cross-Chunk Notes

The previous chunk owns the `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` shift definitions and the preceding lane 2 analog RX tail. This chunk begins with that register's masks and then covers a large CR0 lane 3/raw-common/raw-lane section. The next chunk should begin with `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_MASTER_MPLL_LOOP` and continue the raw lane PCS RX override fields. The final per-file research document should reconcile these boundaries before making whole-file claims about all DPCS 4.2.0 register groups.

### subset-b-002294: lines 14321-16696

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 14321-16696

## Purpose

This chunk is generated AMD DPCS 4.2.0 register field metadata for DCN 3.1-era display link encoders. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS raw-lane registers. Runtime code combines these field constants with matching register offsets from `dpcs_4_2_0_offset.h` and AMD register helper macros to read, update, and program display PHY/link-encoder state.

The requested range covers 2,376 source lines and 2,113 `#define` lines. It begins at the tail of RAWLANE0 PCS ATE TX override fields, covers most RAWLANE1 and RAWLANE2 digital PCS/FSM/IRQ/PMA/TX/RX control field maps, and ends inside early RAWLANE3 PCS RX override fields. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct I/O operations in this chunk. The exposed interface is the macro namespace:

- `DPCSSYS_CR0_RAWLANE<n>_<block>_<register>__<field>__SHIFT`: bit offset for a field within a 16-bit DPCS register.
- `DPCSSYS_CR0_RAWLANE<n>_<block>_<register>__<field>_MASK`: mask for the same field.

Major register families in this slice:

- `DIG_PCS_XF_*`: PCS transmit/receive override and status fields for `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, master MPLL state, reset/request handshakes, detect-RX request/result, TX/RX data enables, async TX, beacon, serial/parallel loopback, `ACK`, `EN_CTL`, and RX-valid override. It also defines RX adaptation fields, CDR/VCO/ref load values, LOS thresholds, equalizer controls (`EQ_ATT_LVL`, `EQ_VGA*`, `EQ_CTLE_*`, `EQ_DFE_TAP1`), RX adaptation acknowledgements/FOM, TX precursor/main/post cursor direction fields, lane numbering, and ATE override fields.
- `DIG_FSM_*`: raw-lane finite-state-machine override and monitor fields, including FSM jump address/start/override/break controls, current state, command-ready and ALU/wait/mask status bits, fast calibration/adaptation flags, common-calibration status for MPLL/RCAL, DCC flags/status, OCLA enables, TX EQ update status, IQ phase offset, and CR register/memory lock bits.
- `DIG_IRQ_CTL_*`: interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation, lane transceiver mode, phase-2 calibration, lane RX-to-TX loopback, DCC on-demand, TX reset, and TX request.
- `DIG_PMA_XF_*`: PMA-side lane/MPLL/supervisor override fields, TX/RX request and reset overrides, beacon/async/clock-sync/data-enable overrides, lane loopback, RTUNE request/ack, MPHY PWM/async/termination controls, and RX adaptation phase-adjust output.
- `DIG_TX_CTL_*` and `DIG_RX_CTL_*`: lane-local TX/RX control knobs such as TX FSM wait/allow-RXDET fields, TX clock enable/select, async beacon wait time, DCC continuous status, OCLA/UPCS enables, RX FSM enable, rate-change-in-P1, LOS mask count, RX data-enable override count, internal reference tracking count, and continuous off-cancel/adaptation status.

The chunk is dominated by RAWLANE1 and RAWLANE2: each has 1,085 visible lines in the assigned slice. RAWLANE0 contributes only the end of a preceding block and small PCS ATE/RX/TX override groups; RAWLANE3 starts near the end and is incomplete in this chunk.

## Control Flow

This header has no runtime control flow. The effective runtime path is generated-macro expansion:

1. `dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and this `dpcs_4_2_0_sh_mask.h`.
2. DCN31 resource macros build link encoder register tables with `DPCS_DCN31_REG_LIST(id)`.
3. The same file initializes `le_shift` and `le_mask` with `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
4. DC link encoder code later uses those tables with AMD register helpers to compose read-modify-write operations for DPCS registers.

The macros themselves do not encode sequencing. Correct behavior depends on caller-side ordering for lane reset/request handshakes, power-state changes, MPLL selection/enabling, link training, RX detection, adaptation/calibration, interrupt clear/mask operations, and PMA/PCS override enablement.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes hardware-backed DPCS register fields. The represented hardware state includes:

- PCS/PMA control state for each raw lane: TX/RX request, reset, acknowledgement, power state, width, rate, MPLL selection, data enable, async/beacon mode, and loopback.
- RX adaptation and calibration state: AFE/DFE adaptation enablement, adaptation requests and continuous modes, off-cancel continuous mode, LOS/LFPS thresholding, VCO/reference load values, equalizer gains/taps, IQ phase offsets, and fast calibration bypass/status flags.
- FSM/debug state: FSM command and jump override, command-ready/status bits, CR locks, OCLA enables, DCC status, common-calibration init/done, and TX EQ update status.
- Interrupt state: sticky or latched status bits, write/clear bits, and masks for RX/TX events and lane-specific calibration or loopback events.
- PMA interface state: PMA lane/MPLL/supervisor overrides, TX/RX PMA data enables, PWM/MPHY controls, RTUNE, async drive controls, and RX adaptation phase-adjust mapping.

Retention and side effects are hardware-defined. Configuration fields usually persist until reprogrammed, lane power-gated, reset, or ASIC reset. Status, clear, IRQ, calibration, and handshake fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive; this header only names bit positions and masks, so consuming code must know the register semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides matching `ixDPCSSYS_CR0_RAWLANE...` register offsets.
- DCN31 resource and link-encoder code, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes this header and expands `DPCS_DCN31_REG_LIST`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
- Generic AMDGPU/DC register helper infrastructure such as `reg_helper.h`, which turns register tables plus shift/mask tables into typed-looking register operations.
- Adjacent generated DPCS/DCN register headers for related ASIC revisions (`dpcs_4_2_2`, `dpcs_4_2_3`, and `dcn_4_1_0`) whose repeated field maps show this is a generated hardware ABI, not hand-authored logic.

There were no direct C references to individual field macros in the quick source search outside generated headers; the normal integration path is token-pasted macro-list expansion into link encoder register, shift, and mask tables.

## Risks And Edge Cases

- Shift/mask drift is the central risk. A wrong constant compiles cleanly but can update the wrong DPCS bit, corrupting lane power state, link rate/width, reset/request handshakes, MPLL selection, or interrupt masking.
- The chunk has artificial boundaries. RAWLANE0 and RAWLANE3 are partial here; complete per-file conclusions require adjacent chunk reports.
- Repeated raw-lane blocks are copy-sensitive. RAWLANE1 and RAWLANE2 are structurally similar, but lane-number, offset, and instance-selection mistakes can fail only on specific physical links or multi-display configurations.
- Many fields are override-enable/value pairs. Setting an override value without the matching enable bit, or leaving an override enabled after training/test flows, can produce hard-to-debug link failures.
- IRQ fields are side-effect-sensitive. Confusing status, mask, and clear fields can create stuck interrupts, missed lane events, or repeated hotplug/link-training recovery.
- Calibration/adaptation fields interact with analog timing. Incorrect fast-calibration, DCC, VCO, RX EQ, LOS, or IQ phase masks can produce rate-specific or cable-specific failures rather than immediate build-time errors.
- Reserved masks are present throughout the chunk. Read-modify-write paths must preserve reserved bits unless the hardware programming guide says otherwise.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN31 support enabled; `dcn31_resource.c` should compile while expanding `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` against this header.
- Mechanically verify every visible field in this line range has a coherent `__SHIFT`/`_MASK` pair, and that masks match the advertised bit width and shift.
- Compare RAWLANE1 and RAWLANE2 field layouts in this chunk against each other and against `dpcs_4_2_0_offset.h` lane offsets; expected repeated blocks should remain aligned.
- Diff the generated fields against AMD's authoritative DPCS 4.2.0 register database or neighboring generated headers where hardware compatibility is expected.
- Exercise DisplayPort/HDMI link bring-up across all DCN31 link encoder instances, especially displays mapped to RAWLANE1 and RAWLANE2.
- Test link-rate and lane-width changes, suspend/resume, hotplug, RX detect, training failure/retry, low-power transitions, and MST or multi-monitor configurations.
- Use debug logging and hardware status reads to watch for stuck `ACK`, reset/request mismatches, DCC/adaptation failures, unexpected IRQ storms, LOS false positives, and link instability after modesets.

## Cross-Chunk Notes

Earlier chunks own the beginning of RAWLANE0 and RAWLANE1 register definitions before line 14321. Later chunks continue RAWLANE3 after line 16696 and likely cover the rest of its PCS/FSM/IRQ/PMA/TX/RX controls. The final merged per-file document should combine all chunks before making whole-file claims about complete raw-lane coverage or every DPCS 4.2.0 field family.

### subset-b-002295: lines 16697-19122

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 16697-19122

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It contains preprocessor constants only: no C functions, structs, enums, branches, allocation paths, locks, MMIO calls, or software-owned persistent state. Its public surface is the generated register-field macro namespace consumed by AMDGPU display and PHY register-table code.

The requested range is 2,426 lines. It contains 2,082 `#define` entries and 344 register-comment blocks; because some comment/register blocks are tiny and the chunk starts and ends mid-register, those counts do not imply 344 complete logical registers. The slice begins inside `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1`, after several shift definitions from the previous chunk, and ends inside `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0`, before that register's final mask lines and subsequent lane2 calibration registers.

This is AMD display/link PHY metadata despite the repository path containing `ceph-client`. It has no Ceph, filesystem, distributed-storage, network, or disk persistence behavior.

## Purpose

The purpose of this chunk is to publish bit positions and masks for DPCS CR0 RAW lane 3 and RAW always-on lane 0/1/2 registers in the DPCS 4.2.0 hardware block. Runtime code combines these generated constants with the companion `dpcs_4_2_0_offset.h` register-address definitions and AMDGPU register helpers to program or decode individual hardware fields without open-coded bit arithmetic.

Major covered hardware areas are:

- Tail of RAWLANE3 PCS RX override input 1, then RAWLANE3 PCS RX override/input/output/status fields for RX request/reset, link rate, width, pstate, low-power detect, CDR VCO low-frequency state, adaptation request/continuous/off-candidate controls, VCO/ref load values, equalizer settings, TX pre/main/post direction hints, lane number, ATE overrides, RX equalization delta, and RX/TX termination controls.
- RAWLANE3 FSM control/status and fast-sequence timing registers for RX startup calibration, adaptation, AFE/DFE calibration, bypass/ref-level/IQ calibration, supervisor and TX common-mode/RX-detect sequences, RX power-up, VCO wait/calibration, continuous adaptation/calibration, common calibration status, fast flags, CR locking, TX DCC flags/status, OCLA selection, TX EQ update flag, RCAL status, and RX IQ phase offset.
- RAWLANE3 IRQ control registers for RX reset/request/rate/pstate/adapt request/adapt disable events, corresponding clear registers, IRQ mask registers, lane transceiver-mode events, phase-2 calibration request/disable events, RX-to-TX serial loopback events, DCC on-demand interrupt, and TX reset/request events.
- RAWLANE3 PMA transfer fields for lane/supervisor/TX/RX override and real PMA inputs/outputs, lane RTUNE control, MPHY override/status, and RX adaptation output handoff.
- RAWLANE3 TX/RX control registers for TX FSM/clock control, DCC continuous status, OCLA/upstream OCLA selection, RX FSM control, RX loss-of-signal masking, RX data-enable override, off-candidate and adaptation continuous status.
- RAWLANE3 PCS ATE and master MPLL loop registers, plus late RX/TX override fields.
- RAWAONLANE0 and RAWAONLANE1 digital always-on lane fields for analog-front-end offsets, RX adaptation outputs, DFE offsets/reference levels, phase adjustment, MPLLA/MPLLB coarse tuning, power-up done, adaptation status, fast flags, slicer controls, common calibration status, adaptation control registers, MPLL disable, signal-detect filtering/calibration, RX override outputs, VREF/calibration code registers, RX DCC calibration code banks, TX DCC bank/data/continuous controls, MPLL bandgap control, signal-detect overrides/input, firmware configuration, transceiver mode, and TX/RX signal-detect/DCC configuration.
- Start of RAWAONLANE2, covering the same always-on adaptation, DFE, phase, MPLL, initialization, slicer, common calibration, adaptation-control, MPLL-disable, signal-detect, RX override, VREF/calibration, and the first RX DCC calibration code registers through `RX_DCC_CAL_QCM_CODE_0`.

## Important Macros And Field Families

There are no callable APIs or C data types in this range. The important API is the generated macro naming contract:

- `DPCSSYS_CR0_<REGISTER>__<FIELD>__SHIFT`: least-significant bit offset for a field.
- `DPCSSYS_CR0_<REGISTER>__<FIELD>_MASK`: already shifted mask for the same field.
- Instance prefixes such as `RAWLANE3` and `RAWAONLANE0/1/2` are part of the ABI between generated headers, offset headers, and register table macros.

Important macro families in this chunk include:

- `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_*`: PCS-facing lane 3 control and status for RX/TX request/reset handshakes, rate/width/pstate, AFE/DFE adaptation controls, equalizer/load values, acknowledge/status outputs, ATE override values, termination controls, and master MPLL loop selection.
- `DPCSSYS_CR0_RAWLANE3_DIG_FSM_*`: finite-state-machine timing, status, and debug fields. These include fast RX startup/adaptation/calibration phases, continuous calibration/adaptation flags, common calibration status, CR lock, TX DCC status, OCLA, and TX equalization update signaling.
- `DPCSSYS_CR0_RAWLANE3_DIG_IRQ_CTL_*`: interrupt latch, clear, and mask fields for lane 3 RX/TX state changes and calibration-related events.
- `DPCSSYS_CR0_RAWLANE3_DIG_PMA_XF_*`: digital-to-PMA and PMA-to-digital handoff fields for supervisor, lane, TX, RX, RTUNE, MPHY, and RX adaptation signals.
- `DPCSSYS_CR0_RAWLANE3_DIG_TX_CTL_*` and `DPCSSYS_CR0_RAWLANE3_DIG_RX_CTL_*`: compact control/status fields for TX/RX FSM behavior, clock/DCC status, OCLA selection, loss-of-signal masking, data-enable override, and continuous adaptation/off-candidate status.
- `DPCSSYS_CR0_RAWAONLANE[0-2]_DIG_AFE_*`, `RX_ADPT_*`, `DFE_*`, and `RX_SLICER_*`: always-on lane readback/control fields for receiver adaptation results, analog offsets, DFE references/taps, phase adjust, slicer controls, and figure-of-merit reporting.
- `DPCSSYS_CR0_RAWAONLANE[0-2]_DIG_MPLLA_*`, `MPLLB_*`, `MPLL_DISABLE`, `MPLL_BG_CTL`, and `LANE_CMNCAL_*`: MPLL coarse tuning, disable control, bandgap, and common calibration status fields.
- `DPCSSYS_CR0_RAWAONLANE[0-2]_DIG_FAST_FLAGS*`, `ADPT_CTL_*`, `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG`: fast calibration/adaptation flags and firmware-visible configuration knobs.
- `DPCSSYS_CR0_RAWAONLANE[0-2]_DIG_RX_SIGDET_*`, `SIGDET_OUT_*`, `RX_VREFGEN_EN`, `CAL_*`, and `RX_DCC_CAL_*`: signal-detect filtering/calibration, VREF generation, calibration code, and RX DCC calibration code fields.
- `DPCSSYS_CR0_RAWAONLANE[0-1]_DIG_TX_DCC_*`, `LANE_XCVR_MODE_*`, `RX_SIGDET_CONFIG`, and `TX_DCC_CONFIG`: TX DCC bank/data/continuous access, transceiver mode override/input, and lane signal-detect/DCC configuration fields. Lane2 begins the same family but continues in the next chunk.

Most masks are 16-bit CR-style masks (`0x0000FFFFL` or narrower bit ranges). Reserved fields are emitted explicitly; they are part of the generated description of the register layout but should not be treated as safe software write targets without an authoritative PHY sequence.

## Control Flow And Runtime Integration

This header has no runtime control flow. Runtime behavior is created by code that includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`, constructs register/field tables, and uses AMDGPU display register helpers to access the hardware.

Visible integration in this tree includes:

1. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and this shift/mask header.
2. That DCN 3.1 resource file expands DPCS register and mask/shift tables with macros such as `DPCS_DCN31_REG_LIST(id)`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
3. The companion offset header maps the same internal CR0 names to addresses in `dpcssys_cr0_rdpcstxcrind`; for example the RAWLANE3 PCS/FSM/IRQ families in this chunk correspond to `ixDPCSSYS_CR0_RAWLANE3_*` address definitions.
4. Higher-level AMD display code uses generic register helpers and link/PHY programming sequences to perform masked read/modify/write or polling operations using the generated address, mask, and shift metadata.

The represented hardware flow is typically: select ASIC-owned or software-override controls, sequence PCS/PMA RX/TX request and reset handshakes, start or monitor FSM calibration/adaptation phases, handle IRQ latches/clears, configure PMA/MPHY handoff values, and read always-on lane adaptation/calibration/status fields.

## State And Persistence Behavior

The file itself has no mutable state and persists nothing. All state described by these macros lives in DPCS hardware registers.

State represented by this chunk includes:

- RAWLANE3 PCS/PMA lane state: RX/TX request/reset, pstate/rate/width, adaptation request/ack/FOM, RX equalization/load values, CDR low-frequency state, TX pre/main/post direction, lane numbering, termination, and ATE override state.
- RAWLANE3 FSM state: fast startup/adaptation/calibration timing, continuous calibration/adaptation flags, common calibration and RCAL status, CR lock, TX DCC status, OCLA selection, and TX EQ update flags.
- RAWLANE3 IRQ state: interrupt request latches, clear bits, mask bits, lane transceiver mode events, phase-2 calibration events, loopback events, DCC on-demand events, and TX reset/request events.
- RAWAONLANE0/1/2 always-on lane state: analog offsets, RX adaptation values and done flags, DFE tap/reference values, phase adjustment, slicer controls, MPLL coarse tuning and disable state, initialization complete state, signal detect filtering/calibration, VREF/calibration codes, RX DCC calibration code readbacks, firmware configuration, transceiver mode, and TX DCC configuration where present in this slice.

Persistence is hardware-defined. Values generally survive only until the relevant lane, DPCS block, display engine, power domain, or GPU is reset or power-gated, and they may need to be restored or recalculated during modeset, hotplug retraining, suspend/resume, runtime power management, or ASIC reset. Status, clear, and handshake fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while related clocks and power are present; this generated header does not encode those access semantics.

## Dependencies

This chunk depends on the matching generated DPCS 4.2.0 offset header. Shift/mask constants alone do not identify MMIO or internal CR addresses.

Key dependencies are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides `reg*`, base-index, and `ixDPCSSYS_CR0_*` address definitions for the fields described here.
- AMDGPU display register-helper infrastructure, including token-paste macros and masked read/write/update helpers that consume generated `__SHIFT` and `_MASK` constants.
- DCN 3.1 display resource initialization, which includes this DPCS 4.2.0 generation and builds DPCS register and mask/shift lists for the hardware generation.
- Link encoder, PHY bring-up, link training, hotplug, power-management, suspend/resume, diagnostics, and firmware-facing code that programs or observes DPCS CR0 lane and always-on lane registers.
- The authoritative AMD silicon register database that generated this header and its companion offset header. Manual edits are risky unless synchronized with that source and every generated consumer table.

## Integration Points

Primary integration points are generated macro names used by register tables and masked field helpers. A consumer referencing a field such as `DPCSSYS_CR0_RAWLANE3_DIG_IRQ_CTL_IRQ_MASK__RX_REQ_IRQ_MASK_MASK` or `DPCSSYS_CR0_RAWAONLANE1_DIG_RX_ADPT_CTLE__RX_ADPT_CTLE_MASK` relies on this file for the exact bit geometry.

Integration surfaces include:

- Link training and lane bring-up: PCS RX/TX request/reset, pstate/rate/width, adaptation controls, termination controls, and PMA handoff fields.
- PHY calibration and adaptation: FSM fast-calibration flags/timers, continuous RX calibration/adaptation, RX AFE/DFE/CTLE/VGA values, phase adjustment, VREF/calibration codes, DCC code readbacks, and common calibration status.
- Interrupt handling and event tracking: RX/TX request/reset/rate/pstate/adaptation event latches, clears, and masks, plus lane transceiver-mode, phase-2 calibration, serial loopback, and DCC on-demand events.
- Diagnostics and observability: OCLA/upstream OCLA selection, FSM memory/status monitors, fast flags, TX DCC status, RX adaptation FOM, signal-detect status/configuration, and firmware configuration registers.
- Multi-lane mapping: RAWLANE3 and RAWAONLANE0/1/2 use repeated field layouts with lane-specific names. Address tables must keep these names aligned with the physical lane and always-on lane instances.

## Risks And Edge Cases

- Wrong shift/mask values can compile cleanly while writing the wrong bit in a PHY register, corrupting adjacent fields or decoding status incorrectly.
- The chunk starts inside `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1`; the first several `__SHIFT` definitions for that register are in the previous chunk, while this chunk contains later shifts and masks. Pairing checks must account for this boundary.
- The chunk ends inside `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0`; the next chunk owns the remaining mask lines and the following lane2 DCC calibration code registers.
- Override fields are sensitive because they can transfer ownership from normal ASIC/FSM control to software-forced values. Bad masks can hold reset/request/adaptation/termination signals in the wrong state.
- FSM and calibration fields are timing and sequencing dependent. Incorrect constants can cause link-training timeouts, unstable clocks, calibration loops, bad RCAL/DCC results, or resume-only failures.
- IRQ clear and mask fields may have side effects. Misidentifying a latch, clear, or mask bit can hide real events, create interrupt storms, or leave stale status latched.
- Always-on lane status fields are often used for debug, firmware calibration, or marginal-signal diagnosis. A field drift can look like a sink/cable/link-training problem rather than an obvious software regression.
- Repeated RAWAONLANE0/1/2 families are copy-error prone. Mixing lane instance prefixes can work on one lane topology and fail on another.
- Reserved masks are present throughout the generated file. Generic read-modify-write code should preserve reserved bits unless a silicon-authored sequence explicitly programs them.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Build AMDGPU display support with DCN 3.1/DPCS 4.2.0 enabled. Missing or renamed generated macros should fail in resource table construction or in code that token-pastes DPCS field names.
- Run mechanical consistency checks against AMD's authoritative DPCS 4.2.0 register database: complete fields should have matching `__SHIFT` and `_MASK` definitions with expected widths, while allowing the known start/end chunk-boundary exceptions.
- Compare this range with nearby generated DPCS versions, such as DPCS 4.2.2/4.2.3 or older 3.x layouts, only where the hardware team expects compatible register layouts. Do not assume cross-generation interchangeability.
- Exercise DisplayPort and HDMI hotplug, modeset, lane-count changes, link-rate changes, link retraining, suspend/resume, runtime power management, and GPU reset on hardware using DPCS 4.2.0.
- Watch link-training logs and display diagnostics for RX/TX request/reset timeouts, clock-not-ready, adaptation failures, IRQ storms, calibration timeout, DCC/RCAL failures, unstable link clocks, blank displays, or resume-only display loss.
- Validate high-bandwidth and marginal-signal scenarios that stress TX/RX termination, RX adaptation, CTLE/VGA/DFE values, signal-detect configuration, VREF/calibration codes, and DCC calibration readbacks.
- Use register dumps, debugfs, firmware traces, or vendor register-validation tooling where available to confirm that CR0 address/data accesses hit the intended RAWLANE3 and RAWAONLANE instances.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create a final per-file synthesis for `dpcs_4_2_0_sh_mask.h`; that merge belongs to the reconciliation lane after every chunk for this generated header is available.

### subset-b-002296: lines 19123-21539

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 19123-21539

## Scope

This chunk is a middle segment of the generated AMD DPCS 4.2.0 shift/mask header. It covers line 19123 through line 21539 and defines 2,101 preprocessor constants: 1,058 `__SHIFT` macros and 1,043 `_MASK` macros across 317 visible register groups. The uneven count is expected for this slice because the range ends inside `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0`; the remaining masks for that register continue after line 21539. The range starts cleanly at `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_ICM_CODE_0`.

The content is declarative only. It exports symbolic bitfield positions for memory-mapped DPCS CR0 lane/common/supervisor registers and contains no C functions, structs, enums, runtime storage, loops, or branches.

## Purpose

The header provides machine-generated bit shift and mask constants for AMDGPU display code that programs the DPCS 4.2.0 display PHY/register surface. Consumer code combines these macros with companion register-offset macros from `dpcs_4_2_0_offset.h` and AMD display register helpers to read, compose, update, and decode hardware register fields without embedding raw numeric bit positions in driver logic.

This specific chunk covers:

- The tail of CR0 always-on lane 2 calibration and control fields.
- A complete CR0 always-on lane 3 field surface for RX adaptation, DFE/AFE calibration, fast bring-up flags, overrides, signal-detect, DCC calibration, firmware configuration, and lane transceiver mode.
- A matching `RAWAONLANEX` generic lane template block with the same field families as lane 3.
- CR0 `SUPX` common/supervisor digital and analog fields for reference clock override, MPLLA/MPLLB override and ASIC inputs, SSC programming, charge-pump controls, bandgap, prescaler, RTUNE, PLL power-control state/timers/calibration, and analog PLL override outputs.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated macro namespace:

- `DPCSSYS_CR0_RAWAONLANE2_DIG_*`: remaining lane-2 RX DCC calibration codes, TX DCC bank address/data/control, MPLL bandgap control, signal-detect override/readback, firmware config, transceiver mode override/readback, RX signal-detect filter config, and TX DCC config.
- `DPCSSYS_CR0_RAWAONLANE3_DIG_*`: lane-3 AFE/DFE offsets, RX IQ/ATT/VGA/CTLE/DFE adaptation status, phase adjustment, MPLLA/MPLLB coarse tune, initial power-up done bits, fast calibration/adaptation flags, adaptive control windows, MPLL disable, common calibration status, TX/RX overrides, signal-detect calibration/status, DCC codes, firmware config, and lane mode fields.
- `DPCSSYS_CR0_RAWAONLANEX_DIG_*`: generic lane-X equivalents of the lane-3 definitions, useful where generated code wants a lane-agnostic register template.
- `DPCSSYS_CR0_SUPX_DIG_*`: supervisor digital identification, refclock override, MPLLA/MPLLB div/HDMI clock overrides, PLL override input sets, SSC peak/step-size fields, charge-pump overrides, supervisor/prescaler/lane-level overrides, ASIC input mirrors, PLL power-control status/timers/calibration, bandgap/ref clock power-up timing, RTUNE configuration/status/set values, and analog MPLL override output fields.
- `DPCSSYS_CR0_SUPX_ANA_*`: supervisor analog prescaler, RTUNE, bandgap, MPLLA/MPLLB miscellaneous/override/ATB/control/reserved fields.

Most registers expose a predictable pair pattern: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. Reserved fields are also generated, so consumers can preserve or explicitly mask reserved bits during read-modify-write sequences.

## Register Areas Covered

The lane-local part of the chunk describes RX adaptation and calibration state. Lane 3 and the lane-X template include AFE ATT/CTLE IDAC offsets, RX figure-of-merit and adaptation-done status, DFE summer/phase/data/bypass/error offset readbacks, DFE tap status, slicer controls, IQ phase adjustment, RX signal-detect thresholds and filters, LF/HF signal-detect tune codes, VREF generator enable/calibration, RX DCC calibration code families, and TX DCC bank access/configuration. Fast flags name the accelerated calibration steps that hardware or firmware can bypass or shorten, such as startup calibration, AFE/DFE calibration, reference-level calibration, IQ calibration, continuous adaptation, TX common-mode, RX detect, power-up, VCO wait, and VCO calibration.

The lane override groups expose control/readback bits for TX/RX mode selection, power-up and request handshakes, reset and rate changes, RX adaptation request/disable, serial loopback, PMA signal-detect enable and output, data-enable override, and lane transceiver mode. These are the fields most likely to be touched by low-level PHY bring-up, debug, validation, or firmware-assisted recovery paths.

The `SUPX` digital block defines common resources shared by lanes: refclock and bandgap overrides, HDMI mode, MPLLA/MPLLB div/HDMI clocks, PLL power and reset/calibration controls, SSC peak and step-size programming, charge-pump proportional/integral/gearshift controls, supervisor/prescaler/lane-level overrides, ASIC-facing mirrors, and readback/status fields. The MPLL power-control sub-blocks for MPLLA and MPLLB include override controls, finite-state-machine status, lane ownership/status bits, lock/readback bits, DAC range/input, lock and stable timing, gearshift/preset timing, PCLK enable/disable/powerdown timing, calibration override, analog DAC output, and SSC spread type.

The `SUPX` analog block mirrors the same common domain from the analog side: prescaler controls, RTUNE controls, bandgap controls and measurement switches, MPLLA/MPLLB misc/control/override/ATB fields, and reserved analog registers. These definitions are still plain masks, but their names indicate direct coupling to PLL, bias, termination, and measurement circuitry.

## Control Flow And State Behavior

This file has no local control flow. Runtime behavior emerges when AMD display code includes the generated header and uses the constants through register helper macros for direct MMIO or indexed CR register access.

The field names imply several hardware state machines and handshakes:

- Lane bring-up and recovery: `INIT_PWRUP_DONE`, `PH2_PWRUP_DONE`, `LANE_XCVR_MODE`, `MPLL_DISABLE`, RX/TX reset/request/rate/pstate/adapt bits, and RX/TX override enables participate in lane power and mode sequencing.
- RX adaptation: ATT/VGA/CTLE/DFE tap fields, adaptation figure-of-merit, adaptation-done status, DFE offset readbacks, slicer controls, and fast-adaptation flags expose the state of receive equalization and calibration.
- Signal detection and VREF/DCC calibration: LF/HF signal-detect thresholds and tune codes, signal-detect override/readback, RX VREF generator fields, RX DCC calibration codes, and TX DCC bank address/data/control fields support calibration workflows.
- Common PLL and clocking: refclock override, MPLLA/MPLLB clock enable, HDMI/div clocks, SSC peak/step-size, charge pump, PLL power-control status, lock/stable timers, PCLK timing, calibration override, and analog override outputs define the common clock domain that lanes depend on.
- RTUNE and bandgap: RTUNE config/status/set/stat fields plus bandgap/ref power-up timers describe shared analog calibration and power sequencing.

No software persistence is implemented here. Hardware register contents persist according to ASIC reset and power domains. Fields named `*_STAT`, `*_STATUS`, `*_OUT`, `*_ASIC_IN`, and `*_DONE` are readback/status-oriented by name, while `*_OVRD_IN`, `*_OVRD_EN`, `*_SET_VAL`, timer, calibration, and config fields are writable controls by name; this header does not encode those access permissions.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk is paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which supplies the `ix...` register addresses for the fields defined here.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes both `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`. That resource file builds DCN31 link encoder register, shift, and mask tables using `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`. The specific macros in this slice are not all surfaced through those high-level DCN31 lists, but they are part of the same generated DPCS 4.2.0 namespace available to display, PHY, diagnostics, and bring-up code.

Related integration points include:

- AMD DC link encoder and HPO DP link encoder code that programs DPCS/RDPCS PHY and clock resources.
- Register helper macros such as `LE_SF`, `SRI`, `SRI_IX`, and generated register-list macros that map shifts and masks into driver tables.
- DisplayPort/HDMI link training, low-level PHY programming, suspend/resume, hotplug recovery, DP Alt Mode coordination, and hardware validation flows that need lane or common PLL state.
- Firmware or debug paths that use CR access windows and override fields to inspect or force PHY state.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently target adjacent analog or PLL bits during read-modify-write operations.
- This slice contains repeated lane-specific and lane-template definitions. Copy-generation mistakes can affect only lane 2, lane 3, or the generic lane-X template, making failures lane-dependent and difficult to reproduce.
- The chunk mixes writable controls with status/readback fields by name. Consumers must rely on the hardware register specification and surrounding driver policy to avoid writing status-only, clear-on-read, or reserved bits.
- Override-enable patterns are common. Setting an override value without its matching enable bit, or leaving an enable bit asserted after recovery/debug work, can hold the PHY in a forced state across link training or resume.
- PLL, SSC, charge-pump, RTUNE, bandgap, and power-up timer masks affect shared analog resources. Incorrect writes can destabilize all lanes served by the common block, not just one link.
- Full-width or broad `data`, reserved, ASIC input, and analog-reserved masks provide little semantic validation in C. Values need to come from hardware tables or firmware-approved sequences, not arbitrary driver state.
- The range ends in the middle of `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0`; chunk-level validation must account for the remaining masks in the next chunk rather than reporting missing fields as source corruption.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU display code for DCN31 targets that include `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`.
- Static generation checks that every complete register in the full file has matching `__SHIFT` and `_MASK` definitions, with this chunk boundary allowing the partial `MPLLB_OVRD_OUT_0` mask list.
- Consistency checks between this header and the DPCS 4.2.0 register database, especially for repeated `RAWAONLANE3` and `RAWAONLANEX` groups.
- Grep/compile checks for renamed or missing DPCS fields consumed by DCN31 resource and link encoder register-table macros.
- Hardware tests on DPCS 4.2.0/DCN31-class ASICs: DP and HDMI link training, link-rate changes, lane power-state transitions, hotplug, suspend/resume, RX detect/signal-detect behavior, PLL lock, SSC programming, and recovery from failed link training.
- Register readback during bring-up to confirm `INIT_PWRUP_DONE`, adaptation done/FOM/tap values, signal-detect outputs, MPLL lock/status, RTUNE stat values, bandgap/ref power-up timing behavior, and override enable cleanup.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 19123-21539 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should cover the lower CR0, PWRSEQ, RDPCS, RAWLANE, RAWCMN, and beginning of lane-2 definitions. Later chunks should continue `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0` and the remaining DPCS 4.2.0 register groups. The final per-file merge should describe the whole file as a generated ASIC register bitfield map used by AMD display code, not as handwritten runtime logic.

### subset-b-002297: lines 21540-23895

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 21540-23895

## Scope

This chunk documents lines 21540-23895 of the generated AMD DPCS 4.2.0 shift/mask header. The slice contains 2,140 `#define` entries: 1,073 `__SHIFT` macros and 1,078 `_MASK` macros. The uneven count is expected because the requested range starts in the middle of `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0`, after its shift definitions and first mask, and ends in the middle of `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT`, after its first shift definitions and before its masks.

The file content is declarative only. It defines preprocessor constants for bit positions and masks in memory-mapped display PHY/control registers; it has no C functions, structs, runtime storage, branching, or local algorithms.

## Purpose

The header gives AMDGPU display code symbolic access to DPCS 4.2.0 register fields. Consumer code can combine companion offset macros with these shift/mask macros to build read-modify-write operations without hardcoding raw bit values.

This chunk covers CR0 common and lane-level DPCS/PHY surfaces:

- SUPX analog override/status fields for MPLLB clock enables, analog control, RTUNE, bandgap, reference regulator, and PMIX selection.
- `LANEX_DIG_ASIC_*` bridge-facing override/input/output fields for lane, TX, RX, EQ, CDR/VCO, link rate, lane width, power state, loopback, inversion, DETRX, beacon, async drive, and acknowledge/status signaling.
- TX and RX power-control state tables and timing registers for P0, P0S, P1, P2, power-up delays, DCC DAC, and low-bit-error-rate test controls.
- RX VCO calibration, CDR, DPLL, adaptation, slicer, CTLE/VGA/DFE status, statistic/match counters, and calibration clock controls.
- Digital-to-analog TX/RX override registers for TX EQ, cursor/term codes, DCC DAC, MPHY, RX AFE, RX VCO, RX scope/slicer, signal-detect, analog status, and term-code clocks.
- Analog lane TX/RX registers for measurement, power override, alternate bus, ATB measurement/force points, DCC, term-code control, clocks, misc controls, RX CDR/deserializer, squelch, calibration, regulator/reference, and reserved fields.
- Raw memory and raw lane PCS windows for ROM/RAM data, TX PCS input/override input, and the beginning of TX override output.

## Exported API Surface

There are no callable APIs or local types. The exported surface is the macro namespace used by AMD display code after including `dpcs_4_2_0_sh_mask.h`.

Important macro families in this range:

- `DPCSSYS_CR0_SUPX_DIG_ANA_*`: common analog and PLL-related masks for MPLLB enables/resets/calibration, RTUNE comparison, bandgap/reference regulator control, and MPLLA/MPLLB PMIX selection.
- `DPCSSYS_CR0_LANEX_DIG_ASIC_*`: lane interface fields that expose override values and corresponding override-enable bits for TX/RX request, power state, rate, width, data enable, MPLLB select, async drive, VBOOST, DETRX, termination, inversion, loopback, RX EQ, and CDR/VCO settings, plus ASIC input and output mirrors.
- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_*` and `DPCSSYS_CR0_LANEX_DIG_RX_PWRCTL_*`: TX/RX power-state programming fields, delay/count fields, DCC CR-bank address/data, DAC selection/range/control/ack, and power-up timing.
- `DPCSSYS_CR0_LANEX_DIG_RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, and `RX_ADPTCTL_*`: receive-side calibration and adaptation fields, including VCO calibration windows, CDR PI/deserializer controls, DPLL frequency bounds, adaptation loop controls, gain/DFE/CTLE status, DAC control selection, and CR-bank access.
- `DPCSSYS_CR0_LANEX_DIG_RX_STAT_*`: programmable RX statistic matcher/counter fields, masks, sample counts, stop control, and comparator clock control.
- `DPCSSYS_CR0_LANEX_DIG_ANA_*` and `DPCSSYS_CR0_LANEX_ANA_*`: digital control of analog TX/RX circuitry, ATB measurement selectors, signal detect, term-code generation, DCC, VCO, power, squelch, calibration muxes, regulator references, and reserved raw analog windows.
- `DPCSSYS_CR0_RAWMEM_*` and `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_*`: raw 16-bit ROM/RAM data fields and raw PCS TX override/input/status handoff fields.

## Control Flow And State Behavior

The chunk has no software control flow. Runtime behavior comes from consumers using the macros with register access helpers.

The field names imply several hardware state machines and handshakes:

- Link/lane bring-up uses request/ack, reset, rate, width, power state, low-power detect, data-enable, clock-ready, MPLL select/enable, and DETRX fields across the ASIC and raw PCS views.
- Override programming is explicit. Most override fields have a paired `*_OVRD_EN`, `*_OVR_EN`, or `ovrd_*` bit, so software must set both the desired value and its enable bit before hardware should consume it.
- TX output behavior is shaped by main/pre/post cursor fields, EQ tables, term-code controls, VBOOST/IBOOST, beacon enable, async data/drive, inverter controls, DCC DAC, and per-state power-control values.
- RX acquisition and adaptation depend on CDR/VCO calibration, DPLL bounds, adaptation reset/config fields, VGA/CTLE/DFE status, slicer controls, squelch/signal detect, and statistic counters.
- Analog measurement and debug paths are exposed through ATB selectors, force fields, scope controls, raw memory data windows, CR-bank address/data registers, and reserved analog buses.

No software persistence is implemented here. Hardware register contents persist according to the ASIC reset and power domains. Several fields expose hardware latches, counters, readback/status, reserved storage, or raw data windows, but this header does not define ownership or lifetime rules for those values.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. The macros are intended to be paired with generated DPCS 4.2.0 offset headers and AMDGPU/DC register helper macros that know how to apply a field mask and shift to a memory-mapped register.

Visible integration points include:

- AMDGPU DRM display resource code for DCN 3.1 generation hardware, which includes `dpcs/dpcs_4_2_0_sh_mask.h`.
- Display Core link encoder, PHY, clock, DisplayPort/HDMI, and low-level diagnostics paths under `drivers/gpu/drm/amd/display`.
- Companion generated offset headers that define addresses such as the `DPCSSYS_CR0_LANEX_*`, `RAWLANEX_*`, and `RAWMEM_*` registers.
- Firmware/PHY coordination paths that require request/ack and override-enable semantics rather than blind writes.
- Hardware validation tooling that compares generated register headers against the ASIC register database.

## Risks

- Generated-header drift is the central risk. A wrong shift or mask can make a read-modify-write touch the wrong PHY bit and produce link training, power, or calibration failures that compile cleanly.
- This slice is densely populated with paired value/enable fields. Programming an override value without the matching enable bit, or leaving an enable bit asserted after diagnostics, can pin hardware away from normal firmware/PHY control.
- Status and control fields sit close together. Examples include request/ack, calibration request/status, statistic counters, DCC DAC ack, analog status, and raw PCS input/output. Consumers need the hardware access semantics from the register spec.
- Reserved and raw windows (`RESERVED_*`, `NC*`, `RAWMEM_*`, raw analog buses) must not be treated as stable general-purpose storage unless the ASIC documentation says so.
- TX/RX power-state tables and timing masks are small packed fields. Invalid values can affect suspend/resume, hotplug, low-power transitions, or signal integrity without being detected by unit tests.
- The requested chunk boundaries split register blocks, so automated reconciliation must merge adjacent chunks before judging field completeness for `MPLLB_OVRD_OUT_0` and `RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT`.

## Test Signals

Useful validation is mostly build-time, generated-header, and hardware-integration oriented:

- Compile or preprocess AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`, especially DCN 3.1 resource/link paths.
- Run generated-register consistency checks against the DPCS 4.2.0 register source database, including paired `__SHIFT`/`_MASK` coverage across chunk boundaries.
- Static grep checks for consumers of `DPCSSYS_CR0_LANEX_DIG_ASIC_*`, `RX_VCOCAL`, `RX_ADPTCTL`, `RX_STAT`, `DIG_ANA`, `LANEX_ANA`, and `RAWLANEX_DIG_PCS_XF_TX_*` fields.
- Runtime display tests on matching ASICs: DP and HDMI link training, hotplug, suspend/resume, lane power-state changes, DETRX handling, RX adaptation/calibration, and PHY diagnostics.
- Register readback during bring-up should show expected transitions for request/ack, reset release, clock/data enable, MPLL selection, VCO calibration status, DPLL bounds, RX adaptation status, DCC ack, analog status, statistic counters, and raw PCS output fields.

## Chunk Notes For Merge

This document intentionally covers only lines 21540-23895 of `dpcs_4_2_0_sh_mask.h`. Adjacent chunks should provide the missing beginning of `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0` and the continuation of `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT`. The final per-file report should treat this file as a generated ASIC bitfield map, not handwritten driver logic.

### subset-b-002298: lines 23896-26282

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 23896-26282

## Scope And Purpose

This chunk is part of AMD's generated DPCS 4.2.0 register shift/mask header. It contains preprocessor constants for hardware bitfields, not executable driver logic. Consumers pair these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions with `dpcs_4_2_0_offset.h` register offsets and AMD display register helpers to access memory-mapped DisplayPort/PHY control registers on the relevant DCN 3.1-era ASICs.

The requested range contains 2,122 `#define` lines: 1,059 shift macros and 1,063 mask macros, plus 263 register/comment markers. The range starts inside `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT` after several earlier shift lines, and ends after the complete `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0` register. The next register, `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_1`, begins immediately after the chunk.

The substantive hardware covered here is the DPCS raw-lane control surface for CR0 and the beginning of the CR1 supervisor/lane register block:

- CR0 PCS/PMA lane cross-interface overrides, status, test/ATE controls, equalization, termination, loopback, RX/TX request/reset/data-enable, and lane-number fields.
- CR0 raw-lane FSM controls, fast-calibration/adaptation flags, lock/status monitors, on-chip logic analyzer selectors, and common-calibration status.
- CR0 raw-lane IRQ status, clear, and mask registers for RX/TX reset/request/rate/pstate/adaptation, phase calibration, transceiver mode, loopback, and DCC on-demand events.
- CR0 TX/RX control registers for lane FSM enablement, clocks, data-enable timing, loss-of-signal masking, continuous adaptation/offcan status, and UPCS observation.
- CR1 supervisor digital fields for ID code, reference clocks, MPLLA/MPLLB overrides, spread-spectrum configuration, fractional-N PLL programming, charge-pump controls, prescaler, RTUNE, power-up timing, and MPLL power-controller state.
- CR1 supervisor analog fields for bandgap, prescaler, RTUNE, MPLLA/MPLLB analog test/override/control, PMIX, voltage/reference levels, and analog status.
- The first CR1 lane0 ASIC override registers: lane loopback/enable/ACJTAG and the complete TX override input 0 surface for request, pstate, rate, width, MPLLB selection, and data enable.

## Important Constants And Register Areas

`DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_*` registers define the PCS side of the raw lane interface. The RX group covers rate, width, pstate, low-power detect, override enables, AFE/DFE adaptation enablement, RX-to-TX parallel loopback, RX data enable, reset/request overrides, loss-of-signal threshold, VCO/ref load override values, equalizer settings, adaptation acknowledgement/FOM readback, TX pre/main/post direction fields, and lane number. The range also includes ATE-specific RX/TX override registers with similar controls plus beacon, async, VBOOST, IBOOST, DETRX, master MPLL state, and loopback bits. The chunk starts with only the tail of `TX_OVRD_OUT`, so whole-register research for that register needs the previous chunk.

`DPCSSYS_CR0_RAWLANEX_DIG_FSM_*` registers expose low-level lane sequencer behavior. They include an override jump address and command/start/break controls, memory address and state monitors, fast path enables for startup, RX adaptation, AFE/DFE calibration, bypass/reference/IQ calibration, supervisor and TX common mode/RX detect, RX power-up/VCO wait/VCO calibration, continuous calibration/adaptation/data/phase/AFE paths, calibration status for MPLL/RCAL, register/memory lock bits, TX DCC flags/status, TX EQ update status, and OCLA selectors. These fields are diagnostic and sequencing-sensitive because they can alter or observe the PHY micro-sequencer directly.

`DPCSSYS_CR0_RAWLANEX_DIG_IRQ_CTL_*` registers define one-bit status, clear, and mask fields for lane events. Covered IRQs include RX reset/request/rate/pstate/adapt request/adapt disable, TX reset/request, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX serial loopback enable, and DCC on-demand. `IRQ_MASK` and `IRQ_MASK_2` pack enable/mask bits across related RX/TX interrupt sources; corresponding `*_IRQ_CLR` fields are likely write-one-to-clear style hardware controls and should be handled through established IRQ paths.

`DPCSSYS_CR0_RAWLANEX_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` registers bridge PCS control to PMA/MPHY and lane TX/RX controllers. They include MPLLA/MPLLB lane selection, supervisor state override/readback, TX/RX request/reset/beacon/async/data-enable overrides, serial/parallel loopback, RTUNE request/acknowledge, MPHY PWM/termination/async controls, RX IQ phase adjustment mapping, TX FSM timing and clock selection, DCC continuous status, RX FSM enable/rate-change policy, LOS mask counters, RX data-enable override counters, and adaptation/offcan continuous status.

The `addressBlock: dpcssys_cr1_rdpcstxcrind` marker introduces CR1 supervisor registers. `DPCSSYS_CR1_SUP_DIG_*` covers ID code, reference clock override, MPLLA/MPLLB div/HDMI clocks, PLL enable/divider/V2I/standby/frequency/calibration/fractional-N/clock-sync overrides, multiplier and fractional-N quotient/remainder/denominator fields, spread-spectrum peak/step-size fields, CP and gear-shift CP overrides, prescaler and DCO tuning, supervisor RTUNE handshake, PHY reset/reference clock/test controls, bandgap enable, and ASIC input readback mirrors.

`DPCSSYS_CR1_SUP_ANA_*` and `DPCSSYS_CR1_SUP_DIG_ANA_*` describe analog supervisor controls and readbacks. The fields cover prescaler analog test and vreg controls, RTUNE modes and values, bandgap trims and fast-start behavior, switch/power measurement selects, MPLLA/MPLLB analog override, ATB measurement selectors, charge-pump/filter/ring/VCO/lock/SPO/DLL controls, PMIX selection/enables, analog DAC readback, RTUNE comparator and reference clock detector status, and bandgap/async reset/reference vreg override outputs.

`DPCSSYS_CR1_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and the parallel MPLLB group define MPLL power-controller override/status/timing fields. They include override select, feedback and pixel clock enables, fast power-up/lock, DTB select, div10 enable, FSM state, active lane sides, output/fbclk/cal/reset/analog enables, lock status, DAC range/output, lock/stable/gearsift/preset/PCLK enable/disable/power-down timers, calibration override, and SSC spread type. MPLLA and MPLLB layouts are intentionally parallel and should remain consistent.

The chunk ends with `DPCSSYS_CR1_LANE0_DIG_ASIC_LANE_OVRD_IN` and `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`. These fields provide lane0 ASIC-side serial/parallel loopback, enable, RX ACJTAG enable, and TX request/pstate/rate/width/MPLLB/data-enable override controls. Later lane0 TX fields continue in the next chunk.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this source range. The public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position for packing or extracting a field.
- `REGISTER__FIELD_MASK` gives the already-positioned mask for that field.
- Register names encode the hardware block and instance, such as `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_RX_OVRD_IN`, `DPCSSYS_CR1_SUP_DIG_MPLLA_OVRD_IN_0`, or `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`.

The matching address constants live in `dpcs_4_2_0_offset.h`, for example the same CR0 raw-lane PCS/PMA/FSM/IRQ registers are listed around the `0xe000` indirect-register range and CR1 supervisor registers begin at small CR1-relative offsets. The shift/mask values are only meaningful with those matching offsets and this ASIC register database.

In-tree integration is visible in `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h` before including `reg_helper.h`. Higher-level DC code generally reaches these fields through AMD register helper macros and resource tables, not through standalone functions in this header.

Semantic enum values are not defined here. Values for lane rates, widths, pstate encodings, PLL dividers, spread-spectrum modes, RTUNE modes, IRQ mask polarity, and test/ATE selections must come from hardware documentation, generated enum data, or the caller code that owns the programming sequence.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when AMD display/PHY code writes or reads DPCS registers during link bring-up, lane training, PHY calibration, test/ATE flows, power management, interrupt handling, debug capture, or low-level diagnostics.

The implied CR0 lane-control flow starts with PCS/PMA request, reset, rate, width, pstate, MPLL selection, data enable, and loopback controls. RX-side setup can then configure adaptation enables, LOS thresholds, VCO/ref load values, equalization, termination, and data-enable timing. TX-side setup can select clocks, beacon/async behavior, DCC status, and TX request/reset/data-enable controls. Status and acknowledgement fields report whether hardware accepted the PCS/PMA handshakes.

The FSM and fast-calibration registers represent another control plane. They can bypass or accelerate the normal lane micro-sequencer for startup, RX adaptation, calibration, VCO wait/calibration, continuous adaptation, and supervisor/TX common-mode sequences. The `FSM_OVRD_CTL` jump/start/break fields are especially invasive because they can redirect or halt sequencer behavior.

IRQ control follows the usual status/clear/mask pattern. Hardware reports one-bit event status registers, software clears latched conditions through matching `*_IRQ_CLR` fields, and mask registers control which event sources are visible. The macros do not specify edge/level semantics or write-one-to-clear details; those are established by the interrupt service code and hardware spec.

The CR1 supervisor flow programs shared PHY resources: reference clock selection, MPLLA/MPLLB dividers and fractional-N values, spread-spectrum peak/step sizes, charge-pump settings, prescaler levels, RTUNE calibration values, bandgap and analog enablement, and MPLL power-controller timers. Status fields then expose FSM state, lock, clock enables, RTUNE results, and analog comparator/clock detector outcomes.

The lane0 fields at the end are the start of per-lane CR1 programming. They allow instance-specific ASIC-side lane override and TX state selection after the shared supervisor and MPLL resources are configured.

## State And Persistence

The file itself stores no mutable state. It defines how software reaches persistent hardware state in DPCS registers and PHY analog/digital control blocks.

Hardware state represented here includes lane RX/TX request/reset/data-enable bits, rate/width/pstate/LPD selections, loopback controls, adaptation and calibration enables, equalizer and termination settings, VCO/ref load values, IRQ latches/masks, FSM override state, OCLA capture enables, MPLLA/MPLLB configuration, spread-spectrum values, fractional-N PLL values, prescaler/RTUNE/bandgap state, analog test/measurement selects, MPLL power-controller timers, and lane0 TX override values.

Several fields are readback or status oriented rather than durable configuration: acknowledgement bits, calibration done/init bits, FSM state, command ready, ALU flags, DCC status, continuous adaptation/offcan status, RTUNE status, analog comparator and ref-clock detector results, MPLL lock, and active clock/output enables. Callers must distinguish these from writable override fields when building register update sequences.

State persistence is hardware-lifetime scoped. Register values may reset across PHY reset, GPU reset, suspend/resume, link disable, or power-gated PHY domains. PLL, RTUNE, bandgap, and analog fields are particularly sensitive to power transitions because they describe physical clocking and calibration state, not just software-visible configuration.

## Dependencies And Integration Points

This chunk depends on the matching generated register offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`. Cross-version DPCS headers such as `dpcs_4_2_2_*`, `dpcs_4_2_3_*`, or `dpcs_3_1_4_*` contain similar-looking names but must not be substituted without validating the ASIC register database and offsets.

Primary integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes the DPCS 4.2.0 offset and shift/mask headers for DCN 3.1 resource construction.
- The AMD display register helper layer included through `reg_helper.h`, which provides the expected bitfield update/read idioms around generated mask/shift data.
- Link encoder, PHY, HPD/link training, power-management, debug, and interrupt paths that program DPCS indirect registers using the generated offset and mask namespaces.
- Neighboring DPCS generated headers for other revisions, which are useful for structural comparison but not authoritative for this ASIC revision.

The API boundary is the generated register database. Handwritten arithmetic against these constants can work mechanically, but it bypasses the normal register helper patterns and increases the chance of using the wrong base, indirect address space, or field encoding.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong mask or shift compiles cleanly but can write the wrong physical field, causing failures such as link training instability, incorrect lane width/rate/pstate selection, stuck reset/request handshakes, broken RX adaptation, invalid equalization or termination, bad PLL programming, missed or uncleared interrupts, or PHY power/clock sequencing faults.

Chunk boundaries are incomplete. The range begins in the middle of `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT`, so whole-register validation for that register requires the previous chunk. The range ends cleanly after `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`, while the next lane0 TX override register begins after line 26282.

Many fields are sequencing-sensitive. PLL fractional-N, spread-spectrum, charge-pump, power-controller timer, RTUNE, bandgap, reset, clock-enable, calibration, and FSM override fields should be written only by code that owns the PHY bring-up or diagnostic sequence. Random read-modify-write operations can disturb active links.

Interrupt clear fields are side-effecting. `*_IRQ_CLR` bits should not be treated like ordinary persistent configuration, and mask polarity must be confirmed from the IRQ code or hardware spec before changing behavior.

Repeated MPLLA/MPLLB structures are a validation signal. The A and B PLL blocks should remain parallel for most override, ASIC input, analog, and power-controller fields. Any unexpected asymmetry between the two could be a generator issue or a real hardware distinction that needs confirmation.

The `L` suffix on masks, including high-bit masks elsewhere in the generated header, means consumers should keep using the driver's unsigned register helper types and avoid signed arithmetic assumptions around raw constants.

## Test And Validation Signals

Compile coverage should include DCN 3.1 display resource construction and any link/PHY code that includes `dpcs_4_2_0_sh_mask.h`. Missing or renamed macros are usually caught at build time; incorrect numeric values require generated-data comparison or hardware validation.

Useful static checks include comparing this range against the authoritative DPCS 4.2.0 register database, verifying each complete register has non-overlapping masks whose positions match their shift values, diffing MPLLA and MPLLB repeated groups for intentional symmetry, and comparing DPCS 4.2.0 against adjacent generated revisions only as a review aid.

Runtime signals include successful display link bring-up on DCN 3.1 hardware, stable lane training across supported rates and widths, correct suspend/resume and hotplug behavior, no stuck PHY reset/request/ack handshakes, stable RX adaptation and LOS handling, valid MPLL lock and RTUNE status, reliable interrupt delivery and clearing for RX/TX lane events, and absence of link flaps or display artifacts when PLL power management and clock gating are exercised.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002298_research.md`. Whole-file research for `dpcs_4_2_0_sh_mask.h` must merge adjacent chunks to complete the leading `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT` register and continue the CR1 lane0 TX override block after `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`.

### subset-b-002299: lines 26283-28640

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 26283-28640

## Scope

This chunk covers lines 26283-28640 of the generated AMD DPCS 4.2.0 shift/mask header. It is a declarative hardware-register field map, not executable driver logic. The range contains 2,138 exact field macros: 1,069 `__SHIFT` definitions and 1,069 `_MASK` definitions. The first line is the trailing mask for `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0__DATA_EN_OVRD_EN`; the matching register header comments and shifts begin just before this chunk boundary.

The range is centered on `DPCSSYS_CR1` lane-level PHY control. It completes much of lane 0 transmitter/receiver/analog coverage, then starts lane 1 and proceeds through TX, RX, adaptation, statistics, MPHY RX, and the beginning of analog TX definitions.

## Purpose

The header exports symbolic bit positions and masks for AMDGPU display code that programs DPCS 4.2.0 PHY registers. Consumers use these constants with the matching offset header and register helper macros to construct read-modify-write values without embedding literal bit numbers.

In this chunk, the hardware surfaces are:

- Lane 0 ASIC override and ASIC-observed TX/RX datapath fields.
- Lane 0 TX power-state, power-up timing, DCC DAC, TX clock-align, LBERT, RX statistic, and TX analog override/status controls.
- Lane 0 analog TX measurement, power override, alternate-test bus, DCC, termination, clock-override, misc, and reserved windows.
- Lane 1 lane/TX/RX ASIC override, ASIC input/output mirror, RX EQ/CDR/VCO input mirror, OCLA control, TX power-state/timing, RX power-state/timing, VCO calibration, CDR/DPLL, RX adaptation, RX statistics, MPHY RX PWM/termination, and the start of analog TX override/termination definitions.

## Exported API Surface

There are no callable APIs, structs, enums, functions, or local variables. The macro names are the public interface. Important macro families in this range include:

- `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_1` through `_IN_5`, `TX_OVRD_OUT`, `TX_OVRD_OUT_1`, and `RX_OVRD_OUT_0`: lane 0 digital override fields for TX request, pstate, rate, width, MPLLB select, data enable, Nyquist data, disable, beacon, TX main/pre/post cursor, async drive, vreg bypass, clock-ready, DETRX, invert, low-power detect, DC coupling, extended FIFO, MPHY mode, reset, repeater master-lane enable, and acknowledge/status readback.
- `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_ASIC_IN_*`, `TX_ASIC_OUT`, and `RX_ASIC_OUT_0`: non-override ASIC mirror fields for the same lane 0 TX/RX request, rate, pstate, data-enable, equalization cursor, async, vreg, ack, DETRX, valid, and adaptation status paths.
- `DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX power-state programming (`TX_PSTATE_P0`, `P0S`, `P1`, `P2`) plus power-up timing windows and DCC DAC access registers (`DCC_CR_BANK_ADDR`, `DCC_CR_BANK_DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, `DCC_DAC_ADDR`).
- `DPCSSYS_CR1_LANE0_DIG_RX_STAT_*`: lane 0 receiver statistic/pattern-match support, including load value, data mask, match control pairs for CR1A/CR1B patterns and masks, statistic source/shift selection, sample counter, seven statistic counters, calibration compare clock control, extra delay/sample-disable controls, and statistic stop.
- `DPCSSYS_CR1_LANE0_DIG_ANA_*` and `DPCSSYS_CR1_LANE0_ANA_TX_*`: lane 0 digital-to-analog TX override/status fields for clocks, reset, serial enable, data rate, divider, RX detect, termination code, EQ leg pull enables/directions, pre/post controls, DCC calibration override, fast start, measurement, power override, alternate bus/test bus routing, DCC DAC, misc controls, and reserved analog TX fields.
- `DPCSSYS_CR1_LANE1_DIG_ASIC_*`: lane 1 override and ASIC mirror surfaces. Unlike the lane 0 portion in this chunk, lane 1 includes both TX and RX override inputs, RX EQ override inputs, RX CDR/VCO mirror inputs, OCLA enable, and a richer RX datapath surface.
- `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, and `RX_ADPTCTL_*`: lane 1 receiver power-state/timing, VCO calibration controls/status, clock-data recovery control/status, DPLL frequency/bounds, and adaptive equalization configuration/status fields for ATT/VGA/CTLE/DFE/slicer/DAC control.
- `DPCSSYS_CR1_LANE1_DIG_RX_STAT_*` and `DPCSSYS_CR1_LANE1_DIG_MPHY_RX_*`: lane 1 statistic counters and low-speed MPHY RX PWM, termination, and PWM clock-stability controls.

## Control Flow And State Behavior

This file has no control flow. Runtime behavior is imposed by the AMDGPU display code and by hardware state machines behind these memory-mapped registers.

The field names imply these stateful protocols:

- TX override versus live ASIC input: `*_OVRD_IN_*` fields pair a desired control value with an `*_OVRD_EN` bit, while `*_ASIC_IN_*` and `*_ASIC_OUT*` expose the non-overridden or post-mux hardware values. Consumers must enable overrides deliberately and then verify outputs such as `TX_ACK`, `DETRX_RESULT`, `ACK`, `VALID`, or `ADAPT_STS`.
- Lane power sequencing: `PSTATE`, `TX_PSTATE_*`, `RX_PSTATE_*`, and `*_PWRUP_TIME_*` fields encode lane power modes and delays. These values affect suspend/resume, link bring-up, low-power entry/exit, and training recovery.
- Link-rate and width control: `RATE`, `WIDTH`, `MPLLB_SEL`, `DATA_EN`, `REQ`, `DISABLE`, `CLK_RDY`, and lane reset fields are the software-visible knobs and handshake bits for activating and deactivating a lane.
- Equalization and signal-shaping: `TX_MAIN_CURSOR`, `TX_PRE_CURSOR`, `TX_POST_CURSOR`, `TX_TERM_CODE`, `TX_ANA_CTRL_*`, DCC DAC, and DCC calibration fields configure electrical output behavior. Lane 1 RX adaptation fields cover ATT, VGA, CTLE, DFE taps, data/error VDAC offsets, slicer levels, adaptation reset, and DAC control selection.
- Receiver clock recovery and calibration: lane 1 `RX_VCOCAL`, `RX_CDR`, and `RX_DPLL` fields expose calibration controls, counters, resets, lock indicators, frequency measurements, and bounds.
- Diagnostics: LBERT controls, OCLA enable, statistic sample/counter registers, pattern-match controls, and MPHY RX low-speed controls are used for bring-up, validation, error isolation, and hardware debug.

No software persistence is implemented here. Hardware register values persist or reset according to the DPCS/PHY power domains, ASIC reset behavior, and firmware ownership rules. The numerous reserved, status, counter, and latch-like fields must be interpreted from the hardware specification rather than from this header alone.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. This file is normally included with the matching DPCS 4.2.0 offset header, which supplies register addresses, and with AMDGPU/DC register helper macros that combine `__SHIFT` and `_MASK` values.

Integration points are:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC link encoder, PHY bring-up, link training, DPCS access, and display diagnostics.
- DisplayPort/HDMI PHY programming paths that select rate, width, MPLL, data enable, DETRX, reset, polarity/invert, cursor values, and analog TX electrical parameters.
- RX-side calibration/adaptation paths for lane 1, including CDR, DPLL, VCO calibration, CTLE/VGA/DFE, slicer, and statistic counters.
- Hardware debug and manufacturing/validation flows that use LBERT, OCLA, pattern/stat counters, alternate test buses, DCC DAC programming, and analog measurement/override fields.
- Generated-register validation machinery. Field names and bit layouts should stay in lockstep with AMD's register database and nearby DPCS generation headers.

## Risks

- Generated-header drift is the main risk. A one-bit shift or mask error can silently write an adjacent control bit in a PHY register, with symptoms appearing only during link training, suspend/resume, or a specific lane/electrical mode.
- Override registers mix value fields and `*_OVRD_EN` bits. Setting the value without the enable bit may do nothing; setting the enable bit with an unintended value can force hardware away from normal ASIC or firmware control.
- Many fields are status/readback-only or handshake outputs (`ACK`, `VALID`, `ADAPT_STS`, `DPLL_LOCK`, statistic done bits, calibration results) adjacent to writable controls. Consumers need access-direction knowledge from the hardware spec.
- Lane 0 and lane 1 are similar but not identical in this chunk. Lane 1 includes RX override/adaptation/CDR/VCO surfaces that are not mirrored in the lane 0 portion here; copy/paste assumptions across lanes can compile while targeting the wrong fields.
- Electrical fields such as TX cursor, termination code, DCC DAC, EQ leg controls, RX adaptation taps, slicer levels, and VCO/DPLL settings can create link instability or out-of-spec signaling if programmed outside validated tables.
- Reserved masks are exposed as macros because the generator emits every field. Driver code should avoid writing reserved fields unless an ASIC-specific sequence explicitly requires it.

## Test Signals

Useful validation is mostly build-time, register-generation, and hardware-integration oriented:

- Preprocess or compile AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static checks that every exact `__SHIFT` in this chunk has a matching exact `_MASK`; this range has 1,069 of each.
- Diff the macros against AMD's authoritative DPCS 4.2.0 register database and the companion `dpcs_4_2_0_offset.h` register names.
- Compare lane 0 and lane 1 repeated groups where they are expected to match, while allowing known lane-specific RX/adaptation differences.
- Runtime display tests on DPCS 4.2.0 hardware: DP/HDMI link training at multiple rates and lane widths, hotplug, DETRX, suspend/resume, low-power transitions, lane reset/recovery, and error recovery.
- Electrical and diagnostic validation: TX cursor/termination programming, DCC calibration, RX CDR/DPLL lock, VCO calibration status, RX adaptation status, LBERT, OCLA capture, statistic counters, and MPHY RX low-speed mode.

## Chunk Notes For Merge

This document intentionally covers only lines 26283-28640. The preceding chunk owns the start of `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`; the next chunk continues `DPCSSYS_CR1_LANE1_DIG_ANA_TX_TERM_CODE_CLK_OVRD_OUT` and later analog TX fields. The per-file merge should describe the whole file as a generated DPCS 4.2.0 register bitfield map and preserve the lane/instance repetition rather than treating these macros as handwritten logic.

### subset-b-002300: lines 28641-31001

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 28641-31001

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It covers lines 28641-31001 and defines 2,137 preprocessor constants: 1,069 `__SHIFT` macros and 1,068 `_MASK` macros. The one-count mismatch is a chunk-boundary artifact: the range starts in the middle of `DPCSSYS_CR1_LANE1_DIG_ANA_TX_TERM_CODE_CLK_OVRD_OUT`, after its register comment but before all of its shifts and masks.

The content is declarative hardware metadata. It has no C functions, structs, enums, runtime storage, branches, loops, locks, memory allocation, or direct MMIO operations. Its public surface is the macro namespace that AMDGPU display code uses together with matching DPCS offset headers and register helper macros.

## Purpose

The header provides symbolic bitfield locations for ASIC display PHY registers. Each hardware field is exported as a shift and mask so driver code can encode, decode, and preserve fields during register read-modify-write sequences without embedding raw bit constants.

This range covers the tail of CR1 lane 1 analog/digital analog PHY definitions, then a large portion of CR1 lane 2. The lane 2 area starts at ASIC override and ASIC input/output registers, continues through TX/RX power-state and calibration controls, RX CDR/adaptation/statistics blocks, MPHY controls, and ends in the middle of lane 2 digital analog RX controls.

## Important APIs, Types, And Macros

There are no callable APIs or local types. The effective API is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask used for extraction, clearing, or insertion.

Important macro families in this chunk:

- `DPCSSYS_CR1_LANE1_DIG_ANA_*`: lane 1 digital-to-analog override/status fields for TX equalization, RX power/control/VCO, calibration DACs, AFE, scope, slicer, signal change clocks, term-code override, MPHY override, signal-detect override, and TX DCC DAC override.
- `DPCSSYS_CR1_LANE1_ANA_TX_*` and `DPCSSYS_CR1_LANE1_ANA_RX_*`: lane 1 analog register masks for TX power/measurement, alternative test bus, DCC DAC/control, termination code, override clocks, TX misc/reserved fields, RX clocks, CDR/deserializer, slicer control, RX power, squelch, calibration, analog test bus, and reserved RX fields.
- `DPCSSYS_CR1_LANE2_DIG_ASIC_*`: lane 2 PCS/ASIC boundary fields for lane override, TX/RX override inputs, ASIC inputs, ASIC outputs, RX EQ/VCO inputs, OCLA debug selection, and extra override registers.
- `DPCSSYS_CR1_LANE2_DIG_TX_PWRCTL_*`: lane 2 TX power-state tables for P0/P0S/P1/P2, TX power-up timing, DCC CR bank address/data access, DCC DAC control/range/selection/ack/address, TX clock alignment, and TX LBERT control.
- `DPCSSYS_CR1_LANE2_DIG_RX_PWRCTL_*`: lane 2 RX power-state tables for P0/P0S/P1/P2 and RX power-up timing.
- `DPCSSYS_CR1_LANE2_DIG_RX_VCOCAL_*`: RX VCO calibration control, timing, and status fields.
- `DPCSSYS_CR1_LANE2_DIG_RX_CDR_*` and `DPCSSYS_CR1_LANE2_DIG_RX_DPLL_*`: CDR control/status and DPLL frequency/bound registers.
- `DPCSSYS_CR1_LANE2_DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset, ATT/VGA/CTLE/DFE status, slicer and DAC selection, DFE data/error offset, and CR bank address/data fields.
- `DPCSSYS_CR1_LANE2_DIG_RX_STAT_*`: programmable RX status pattern/match/statistics controls, sample count, counters, stop control, and calibration comparator clock controls.
- `DPCSSYS_CR1_LANE2_DIG_MPHY_*`: MPHY PWM, low-speed termination, and analog PWM clock-stable count fields.
- `DPCSSYS_CR1_LANE2_DIG_ANA_*`: lane 2 digital analog TX/RX override fields, including TX term code, TX EQ, RX control/power/VCO/calibration/DAC/AFE/scope/slicer/IQ controls. The chunk ends after `DPCSSYS_CR1_LANE2_DIG_ANA_RX_ANA_IQ_SENSE_EN`; subsequent lane 2 analog fields continue in the next chunk.

## Register Areas Covered

The lane 1 section is primarily analog-facing. It exposes TX equalization override legs and pre/post controls, RX control and power override enables, CDR VCO overrides, calibration mux/DAC controls, AFE attenuation/gain/CTLE, eye-scope controls, slicer controls, IQ phase/sense controls, signal-change update clocks, analog status, RX/TX termination override fields, MPHY override fields, signal-detect override fields, TX DCC DAC controls, TX power/measurement registers, test bus routing, TX/RX clock controls, CDR/deserializer controls, RX power and squelch settings, calibration settings, and analog test-bus measurement selectors.

The lane 2 ASIC interface section maps override values and hardware readbacks around the PCS/PHY boundary. It includes TX reset/request/rate/width/pstate/data-enable controls, RX reset/request/rate/width/pstate/adaptation controls, low-power detect, loopback, term-code and equalization settings, VCO/CDR references, DETRX and ACK readbacks, and OCLA observability.

The lane 2 power-control sections define per-state TX and RX analog/digital enables, resets, serial/clock/data enables, RX adaptation/DFE flags, RX fast-start behavior, and timing counters. Separate DCC bank and DAC fields indicate indexed calibration or tuning access inside the lane.

The lane 2 RX calibration/adaptation/statistics sections expose VCO calibration start/range/mode/status, CDR and DPLL tuning, adaptation configuration weights and thresholds, completed adaptation codes for ATT/VGA/CTLE/DFE taps, slicer level fields, DAC control selectors, CR bank access, programmable match/stat counters, and stop/sample controls. These are diagnostic and tuning surfaces around RX link training and equalization.

The final lane 2 analog section mirrors part of the lane 1 digital analog block, beginning with TX override and term-code fields and running through RX IQ sense enable. It is a continuation point for the next chunk, which should cover the remaining lane 2 analog signal-change and status definitions.

## Control Flow

This header has no local control flow. Runtime behavior is supplied by AMDGPU display code that includes this header, combines these masks with register offsets, and performs register reads, writes, updates, polling, or interrupt/statistic handling.

Typical runtime flow implied by the field names is:

1. Select the ASIC generation and include the matching DPCS 4.2.0 offset and shift/mask headers.
2. Use register helper macros to compose field values from `__SHIFT` and `_MASK` constants.
3. Program lane TX/RX power-state tables, reset state, data enable, pstate, rate, width, and DCC/VCO/CDR settings during link bring-up or resume.
4. Poll ACK, status, stable, VCO calibration, adaptation done, CDR/DPLL, and statistic fields while training or diagnosing a link.
5. Use override-enable bits only for controlled debug, calibration, or hardware sequencing paths, then return hardware-owned fields to normal control.

The header does not encode sequencing requirements. Consumers must follow the DPCS hardware specification for reset ordering, clock enabling, pstate transitions, term-code clocks, self-clearing update clocks, CDR/VCO tuning, DCC calibration, RX adaptation, LBERT operation, and status counter clearing/stopping.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware register fields whose values live in ASIC register state.

- Override registers can hold software-forced TX/RX reset, request, pstate, rate, width, data enable, term-code, equalization, AFE, slicer, VCO, CDR, DCC, and MPHY values until reset, power-domain loss, or later writes.
- Status and ASIC output registers expose live or latched hardware observations such as ACKs, DETRX, CDR/VCO state, adaptation codes, calibration done bits, LBERT errors, statistic counters, and analog status fields.
- Power-state table fields persist the programmed behavior for P0/P0S/P1/P2 transitions and power-up timing, but this file does not define reset values or retention across suspend, GPU reset, or power gating.
- Self-clearing clock/update fields, clear/stop controls, and statistic counters require access semantics from the hardware spec; the mask header only describes bit positions.
- Reserved fields are named and masked so generated helpers can preserve or describe the full register layout. They should not be treated as general-purpose writable storage.

## Dependencies And Integration Points

The direct companion is the generated DPCS 4.2.0 offset header, expected to define matching `ixDPCSSYS_CR1_LANE*...` register addresses. This file is used through the C preprocessor and AMDGPU/DC register helper idioms that token-paste register and field names into shift/mask constants.

Integration points include:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC link encoder, PHY, link-training, power-management, and diagnostics code for DPCS 4.2.0 ASICs.
- DisplayPort, HDMI, USB-C/DP Alt Mode, and internal MPHY paths that need lane TX/RX reset, rate, width, pstate, data-enable, equalization, termination, and calibration controls.
- RX adaptation and link-training flows that consume ATT/VGA/CTLE/DFE, slicer, CDR, DPLL, VCO calibration, and signal-detect fields.
- Factory validation or debug flows that use LBERT, OCLA, analog test bus, scope, MPHY override, ATE-like overrides, and statistic counters.
- Generated sibling headers in DPCS/DCN trees. The same naming scheme appears in adjacent ASIC generations, so generation mismatch can compile if macro names overlap but still describe the wrong hardware layout.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while programming the wrong silicon bit.
- This chunk starts and ends mid-logical area. The previous chunk owns the beginning of lane 1 term-code clock override context, and the next chunk owns the rest of lane 2 digital analog RX definitions.
- The register surface mixes writable configuration, override enable bits, self-clearing clocks, read-only status, counters, stop/clear controls, and reserved fields. Treating all fields as ordinary writable configuration can leave overrides active, clear status unexpectedly, or corrupt reserved bits.
- Lane 1 and lane 2 blocks are structurally similar but not identical in this slice. Copying masks across lanes or assuming every lane has the same visible chunk coverage can hide generation or lane-index errors.
- Power-state, reset, clock, CDR/VCO, DCC, and adaptation fields are sequencing-sensitive. Updating them while the link is active can destabilize display output or break training.
- RX adaptation status values depend on analog behavior. Software-only checks cannot prove that masks match hardware semantics without hardware readback.
- Broad CR bank address/data and statistics controls can target internal indexed state. Consumers need value validation and must preserve bank/address sequencing.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generated-header, and hardware-integration oriented:

- Compile/preprocess AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`; missing or renamed macros should fail in register helper users.
- Mechanical checks that complete register groups have paired `__SHIFT` and `_MASK` definitions. For this exact slice, expect 1,069 shifts and 1,068 masks because of the partial first register.
- Diff against the authoritative AMD DPCS 4.2.0 register database and the matching `dpcs_4_2_0_offset.h` to confirm register/field names, masks, and bit positions.
- Cross-generation comparison against nearby generated DPCS/DCN headers only where the IP block is expected to be compatible, with care not to substitute another generation's values.
- Runtime link validation on DPCS 4.2.0 hardware: DP/HDMI link training, lane-count/rate changes, hotplug, suspend/resume, GPU reset recovery, low-power transitions, and DP Alt Mode attach/detach when applicable.
- Register readback during PHY bring-up to confirm TX/RX reset, request/ACK, pstate, rate, width, data enable, term code, VCO calibration, CDR/DPLL lock/tuning, DCC calibration, RX adaptation status, and statistic counters move through expected values.
- Diagnostic validation for LBERT, OCLA, analog test bus, RX scope/slicer controls, MPHY PWM/termination controls, and RX statistic match/counter paths, including cleanup checks that override-enable bits are returned to normal.

## Chunk Notes For Merge

This document intentionally covers only lines 28641-31001 of `dpcs_4_2_0_sh_mask.h`. The final per-file report should merge this with adjacent chunks to describe the whole generated DPCS 4.2.0 register bitfield map. For reconciliation, note that this chunk begins inside lane 1 term-code clock override definitions and ends immediately before `DPCSSYS_CR1_LANE2_DIG_ANA_RX_ANA_CAL_DAC_CTRL_EN`.

### subset-b-002301: lines 31002-33365

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 31002-33365

## Scope And Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It exports C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCSSYS CR1 lane, common, raw-lane PCS, and raw-lane FSM registers. It contains no executable C code, no structs, no runtime variables, no locking, and no direct MMIO operations.

The requested range contains 2,137 `#define` entries over 2,364 lines: 1,068 shift definitions and 1,069 mask definitions. It starts mid-register with the two mask definitions for `DPCSSYS_CR1_LANE2_DIG_ANA_RX_ANA_IQ_SENSE_EN`, because that register's shifts are just before line 31002. It ends mid-register after `DPCSSYS_CR1_RAWLANE0_DIG_FSM_FAST_SUP__FAST_SUP_MASK`; the matching reserved mask is on line 33366 and later `RAWLANE0_DIG_FSM_*` fast-state fields continue in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. Its purpose is to let display driver register helpers encode and decode DPCS register fields without open-coded bit constants.

## Important APIs, Types, And Macros

There are no callable APIs or local C types. The macro namespace is the API:

- `DPCSSYS_CR1_*__FIELD__SHIFT` gives the least-significant bit position of a field in a DPCS indirect register.
- `DPCSSYS_CR1_*__FIELD_MASK` gives the field mask used to isolate or update that field.
- Register comments such as `//DPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_TX_PSTATE_P0` group the following field constants by hardware register.

Major macro families in this slice:

- Tail of lane 2 analog controls: RX IQ sense/calibration clocks, AFE update, status readback, RX termination override, MPHY/signal-detect overrides, TX DCC DAC overrides, TX fast-start/loopback, analog TX measurement/power/ATB/DCC/termination/clock/misc fields, analog RX clock/CDR/slicer/power/squelch/calibration/ATB fields, and lane 2 reserved analog registers.
- Lane 3 digital ASIC interface controls: lane/TX/RX override input and output fields, lane state, TX pstate/rate/divider/MPLL selection, TX equalization and DCC calibration fields, RX detect and calibration status bits, and digital ASIC input/output mirrors.
- Lane 3 TX power-control and debug fields: TX `P0`, `P0S`, `P1`, `P2` power-state programming, power-up timing registers, DCC CR bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, LBERT controls, RX statistic match/mask/sample/count/stop registers, and calibration-comparison clock control.
- Lane 3 digital-to-analog and analog TX fields: TX term-code overrides, TX EQ override groups, analog status, DCC DAC override groups, fast-start and clock-loopback controls, analog TX measurement, power, ATB, DCC, term-code, clock, misc, and reserved fields.
- Raw common CR1 controls: common control, MPLLA/MPLLB override and bandwidth/SSC override inputs, lane FSM operation extension, MPLL state control, TX calibration code, SRAM init status, OCLA observability, supervisor analog override, PCS/FW ID codes, always-on RTUNE RX/TX pull-down/pull-up values for indexes 0 through 7, SRAM bitline config, power-gating override/status, supervisor override, VREF stats, reset override/status, reference-range override, and miscellaneous common configuration.
- Raw lane 0 PCS transfer fields: TX/RX PCS override inputs and outputs, pstate/rate/width/LPD/MPLL selection, TX and RX request/reset/data-enable/async/beacon/loopback controls, RX adaptation ACK and figure-of-merit, directed TX pre/main/post cursor requests, lane number, ATE override inputs, RX EQ override fields, TX/RX termination controls, RX valid/clock status, and RX phase-2 calibration handshakes.
- Opening raw lane 0 FSM fields: manual FSM override command/jump/break controls, memory-address monitor, status monitor, and fast flags for RX startup, RX adaptation, AFE/DFE/bypass/reference/IQ calibration, AFE/DFE adaptation, and supervisor fast support.

Reserved field masks are part of the generated layout description. They are not a signal that driver code should write reserved bits as programmable state.

## Control Flow

This header has no runtime control flow. The effective flow is supplied by AMD display code:

1. DCN 3.1 resource code includes `dpcs/dpcs_4_2_0_offset.h` and this matching `dpcs/dpcs_4_2_0_sh_mask.h`.
2. DPCS register-list and shift/mask-list macros, such as `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` / `DPCS_DCN31_MASK_SH_LIST(_MASK)`, token-paste register and field names into register tables.
3. AMD display register helpers use the paired offset, shift, and mask constants to build read, write, update, get, and poll operations.
4. Hardware side effects occur only at those call sites. This chunk only defines where fields live inside the DPCS 4.2.0 register map.

The macros do not encode sequencing rules. Consumers must still order power-state transitions, clock/MPLL programming, RX detection, TX/RX reset handshakes, lane training, calibration/adaptation, interrupt or status clearing, and firmware/shared-ownership transitions correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-backed state in DPCSSYS CR1 registers:

- Per-lane analog TX/RX state for termination, equalization, DCC, signal-detect, squelch, slicer, CDR/deserializer, calibration DACs, IQ phase/sense, clock enables, loopback, measurement, ATB routing, and power overrides.
- Lane 3 digital state for power-state definitions, lane state, pstate/rate/divider, MPLL selection, TX/RX request and reset signaling, RX detection, TX EQ/DCC controls, LBERT/debug controls, and RX statistic counters.
- Raw common state for shared MPLLA/MPLLB override values, spread-spectrum control, RTUNE calibration values, SRAM init and bitline configuration, common power-gating override/status, supervisor override, VREF stats, reset status, reference range, and firmware/PCS ID code readbacks.
- Raw lane 0 PCS state for TX/RX override values, PCS input/output mirrors, low-power detect, rate/width, pstate, data enable, async/beacon signaling, RX valid, loopback, RX adaptation/FOM, directed TX coefficient requests, termination controls, EQ overrides, ATE override values, and phase-2 calibration handshakes.
- Raw lane 0 FSM state for manual command override, current state/status monitoring, memory-address monitoring, and fast-calibration/adaptation control flags.

Persistence is hardware-defined. Configuration and override fields generally last until the hardware block is reprogrammed, power-gated, reset, or restored after suspend/resume. Status, ACK, monitor, statistic, and calibration fields can be volatile, latched, self-clearing, write-one-to-clear, or valid only while the relevant lane/common clock and power domains are active. This generated header does not classify those access semantics.

## Dependencies And Integration Points

The immediate generated-header dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides matching `ixDPCSSYS_CR1_*` offsets. For this range, the companion offset header maps examples such as `ixDPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_TX_PSTATE_P0` at `0x1320`, `ixDPCSSYS_CR1_RAWCMN_DIG_CMN_CTL` at `0x2000`, and `ixDPCSSYS_CR1_RAWLANE0_DIG_FSM_FAST_SUP` at `0x302c`.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes both DPCS 4.2.0 generated headers and initializes DCN 3.1 DPCS register, shift, and mask tables. The relevant table macros come from DC link-encoder headers such as `display/dc/dio/dcn31/dcn31_dio_link_encoder.h`.

Runtime integration is through AMDGPU Display Core link and PHY code. These fields sit below DisplayPort/HDMI link encoder setup, lane power management, clock and MPLL programming, link training, RX detection, calibration/adaptation, diagnostic/statistic readback, loopback/LBERT/OCLA use, suspend/resume restoration, and low-level hardware debugging.

## Risks And Edge Cases

- Generated metadata drift is the main risk. A wrong shift or mask can compile cleanly while programming the wrong hardware bit, truncating a field, corrupting an adjacent field, or clearing a reserved/status bit.
- The chunk is highly repetitive across lane 2, lane 3, raw common, and raw lane 0 namespaces. Copy-generation mistakes may affect only one lane, one pstate, or one override path and only show up under specific connector mappings or lane counts.
- Chunk boundaries are artificial. The range begins with masks whose shifts are in the previous chunk and ends before the reserved mask for `RAWLANE0_DIG_FSM_FAST_SUP`. Adjacent chunks are needed before making complete per-register or per-file claims.
- Override fields commonly use value/enable pairs. Enabling an override with a stale value can force unintended pstate, rate, MPLL, reset, loopback, data-enable, termination, EQ, calibration, or ATE behavior; setting only the value field may have no effect.
- Calibration and analog fields are sequencing-sensitive. Incorrect DCC, CDR, VCO, slicer, IQ, signal-detect, squelch, termination, or RTUNE masks can cause marginal link training, intermittent blanking, bad signal integrity, or resume-only failures.
- Status, ACK, statistic, monitor, and FSM fields are side-effect-sensitive. Treating readback or clear-style bits as ordinary read/write controls can hide failures, lose interrupts/status evidence, or make polling loops time out.
- Raw common MPLL and reference-control fields can affect shared clock resources rather than a single lane. Bad masks here can break multiple links or modes at once.
- Reserved masks exist for generated completeness. Read-modify-write users must preserve reserved fields unless hardware documentation explicitly says otherwise.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU Display Core with DCN 3.1 support. Missing or renamed DPCS 4.2.0 macros should fail where `dcn31_resource.c` populates register, shift, and mask tables.
- Mechanically verify field-pair consistency in lines 31002-33365, allowing the known boundary exceptions for `LANE2_DIG_ANA_RX_ANA_IQ_SENSE_EN` and `RAWLANE0_DIG_FSM_FAST_SUP`.
- Cross-check every complete register group in this chunk against `dpcs_4_2_0_offset.h` and AMD's generated DPCS 4.2.0 register database.
- Compare corresponding lane 2 and lane 3 analog/TX/RX groups, and compare raw lane 0 PCS/FSM layouts with neighboring generated DPCS/DCN versions where the IP layout is expected to match.
- Exercise DisplayPort and HDMI bring-up across link rates and lane counts, including hotplug, modeset, link retraining, suspend/resume, and GPU reset. Watch for link-training fallback, blank displays, unexpected lane pstate, clock/MPLL lock failures, or repeated retraining.
- Validate calibration and diagnostic paths with register dumps or PHY traces: RX statistic counters, LBERT/OCLA output, DCC status, RX adaptation ACK/FOM, PH2 calibration, FSM state/status, RTUNE values, SRAM init, and power-gating status should decode coherently.
- Stress override and ATE-only paths only in controlled lab or manufacturing-style tests, because these fields can bypass normal autonomous PHY sequencing.

## Cross-Chunk Notes

The previous chunk owns the shifts for `DPCSSYS_CR1_LANE2_DIG_ANA_RX_ANA_IQ_SENSE_EN`. The next chunk owns the reserved mask for `DPCSSYS_CR1_RAWLANE0_DIG_FSM_FAST_SUP` and continues later `RAWLANE0_DIG_FSM_*` fields such as fast TX common-mode/RX-detect and RX power-up/VCO timing. The final per-file research document should merge those boundaries and describe the whole `dpcs_4_2_0_sh_mask.h` file as generated DPCS 4.2.0 register metadata, not handwritten driver logic.

### subset-b-002302: lines 33366-35753

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 33366-35753

## Scope

This chunk covers a generated AMD DPCS 4.2.0 register shift/mask header section for `DPCSSYS_CR1_RAWLANE*` digital lane registers. The range starts inside RAWLANE0 FSM fast-calibration fields, covers the remainder of RAWLANE0, all visible RAWLANE1 PCS/FSM/IRQ/PMA/TX/RX control masks, and begins RAWLANE2 PCS/FSM/IRQ masks through `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK`.

## Purpose

The header provides preprocessor constants that describe bit positions and masks for memory-mapped DPCS hardware registers. Each register field is represented as two constants:

- `<register>__<field>__SHIFT`: the bit offset inside a 16-bit hardware register field window.
- `<register>__<field>_MASK`: the already-shifted mask used to isolate or update that field.

There are no functions, structs, or runtime algorithms in this chunk. Its purpose is to feed AMD display register accessor macros with stable field metadata matching the DPCS 4.2.0 register map.

## Covered Register Blocks

- RAWLANE0 FSM tail: fast TX/RX sequencing, common calibration status, continuous RX calibration/adaptation, DCC flags/status, FSM lock, OCLA debug enables, TX EQ update, RCAL status, and IQ phase offset.
- RAWLANE0 IRQ control: reset/request/rate/pstate/adaptation/phase-2-calibration/loopback/DCC/TX IRQ status, clear, and mask registers.
- RAWLANE0 PMA bridge: lane/MPLL override inputs and outputs, PMA supervisor state, TX/RX request and reset overrides, loopback enables, PMA data enables, retune request/ack, MPHY PWM/term controls, and RX adaptation IQ phase map override.
- RAWLANE0 TX/RX controls: TX FSM timing, RXDET gating by power state, TX clock control, DCC continuous status, RX FSM enable/rate-change behavior, LOS mask count, RX data enable override count, off-candidate/adaptation continuous status, and OCLA/UPCS debug controls.
- RAWLANE0 and RAWLANE1/2 PCS transfer blocks: TX/RX PCS inputs and outputs, override inputs, ATE override inputs, RX EQ/adaptation feedback, FOM, TX pre/main/post direction fields, lane number, reserved scratch registers, PH2 calibration handshakes, and TX/RX termination controls.
- RAWLANE1 complete visible lane block: PCS transfer registers, FSM override/status/fast-calibration registers, IRQ status/clear/mask registers, PMA bridge registers, TX/RX control registers, and ATE override copies.
- RAWLANE2 partial lane block: PCS transfer and EQ registers, FSM override/status/fast-calibration registers, and IRQ control through the first IRQ mask register. The chunk ends before the rest of RAWLANE2 IRQ/PMA/TX/RX definitions.

## Important Definitions

The most important macro families in this chunk are:

- `DPCSSYS_CR1_RAWLANE*_DIG_PCS_XF_*`: PCS-side transfer and override fields. These carry lane power state (`PSTATE`), low-power disable (`LPD`), lane `WIDTH`, link `RATE`, MPLL selection/enables, TX/RX request/reset handshakes, data enables, adaptation controls, RX equalization results, and ATE override controls.
- `DPCSSYS_CR1_RAWLANE*_DIG_FSM_*`: firmware/hardware FSM control and monitor fields. `FSM_FSM_OVRD_CTL` exposes jump address/start/override/break controls; `FSM_STATUS_MON` exposes state, command-ready, ALU, wait, and mask-disable status; `FAST_*` fields shortcut calibration/adaptation states.
- `DPCSSYS_CR1_RAWLANE*_DIG_IRQ_CTL_*`: lane-local interrupt status, clear, and mask bits for RX/TX reset/request/rate/pstate/adaptation, lane transceiver mode, RX phase-2 calibration, serial loopback, and DCC on-demand activity.
- `DPCSSYS_CR1_RAWLANE*_DIG_PMA_XF_*`: PMA-side bridge fields for MPLL state, TX/RX request/reset overrides, PMA data enables, loopback, RTUNE, MPHY PWM/async/termination controls, and IQ phase-adjust override.
- `DPCSSYS_CR1_RAWLANE*_DIG_TX_CTL_*` and `DPCSSYS_CR1_RAWLANE*_DIG_RX_CTL_*`: lane TX/RX control timing and debug fields, including TX MPLL-off wait time, RXDET permission per power state, TX clock select, async beacon wait, RX LOS masking, and continuous adaptation status.

Field widths vary from one-bit controls to multi-bit hardware values. Examples visible in the chunk include 2-bit or 3-bit `RATE`, `WIDTH`, `PSTATE`, term-control, and direction fields; 4-bit lane number/IQ/equalization fields; 5-bit or wider timing and state counters; 7-bit/13-bit reference/VCO load values; 8-bit adaptation FOM and DFE tap values; and 16-bit reserved registers.

## Control Flow

This header has no control flow on its own. Control flow is introduced by consumers that include the offset header and this shift/mask header, then use generated register descriptor tables and `REG_GET`, `REG_SET`, or `REG_UPDATE` style accessors to read or modify fields.

The nearby integration observed in `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`, then builds link encoder register tables with `DPCS_DCN31_REG_LIST(id)`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)`. That pattern means these macros are compile-time data for register table initialization rather than directly executed logic.

## State and Persistence Behavior

The constants are stateless at runtime, but they describe persistent hardware state in DPCS lane registers. Writes through these masks can affect:

- Lane power/link state transitions such as reset, request, pstate, width, and rate.
- MPLL enable/selection and common calibration status.
- RX/TX equalization, DCC calibration, RX adaptation, PH2 calibration, and VCO/reference load values.
- Interrupt masks and clear registers, which determine whether hardware events remain latched or visible.
- Debug and override state such as FSM override, ATE override, PMA/PCS override enables, OCLA controls, and loopback enables.

Reserved fields are explicitly masked. Consumers should preserve reserved bits unless hardware documentation says otherwise; many registers expose `RESERVED_*_MASK` values covering the unused high bits of a 16-bit register.

## Dependencies

- The corresponding address definitions live in the matching DPCS offset header, especially `dpcs_4_2_0_offset.h`.
- AMD display resource code maps offsets and masks into register structures through generated macros such as `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`.
- Low-level register access depends on the AMD display register helper layer that expands register/field names into offset, shift, and mask lookups.
- The definitions are ASIC/IP-version specific. Similar names appear in other generated DPCS/DCN headers, but mask widths and literal formatting may differ by IP version.

## Integration Points

- Link encoder resource initialization: the DPCS mask and shift tables are part of the per-link encoder register metadata used by DCN 3.1 resource setup.
- DisplayPort/PHY bring-up and link training: fields in PCS/PMA/FSM blocks correspond to lane request/reset, rate, width, MPLL, RX adaptation, and equalization handshakes that link training and PHY control paths rely on.
- Interrupt handling and diagnostics: IRQ status/clear/mask fields provide the bit layout for lane events such as RX/TX reset/request, rate changes, pstate changes, adaptation requests, PH2 calibration, loopback, and DCC on-demand.
- Hardware debug/test paths: ATE override, OCLA, FSM override, loopback, reserved scratch, and PMA/PCS override registers are likely used by diagnostics, validation, or firmware-assisted debug flows rather than normal display modes.

## Risks

- A wrong shift or mask silently writes the wrong hardware bit. In this domain that can break link bring-up, corrupt lane training, leave IRQs stuck, or alter analog PHY tuning.
- Lane definitions are repetitive but not interchangeable. RAWLANE0, RAWLANE1, and RAWLANE2 have mostly parallel fields, but chunk boundaries and per-lane offsets come from the offset header; copy/paste edits can misalign a lane with its address table.
- Multi-bit fields need value-range discipline. Callers must shift and mask values through the helper macros; writing raw values without masking can clobber neighboring reserved or enable bits.
- Override enable/value pairs are high risk. Many fields follow `<signal>_OVRD_VAL` plus `<signal>_OVRD_EN`; enabling an override with stale values can force reset/request/data/loopback/calibration behavior unexpectedly.
- IRQ clear bits are separate from status and mask bits. Confusing status, clear, and mask registers can either drop events or leave latched interrupts uncleared.
- The chunk ends mid-RAWLANE2 IRQ block, so whole-file reasoning must combine this with the next chunk before claiming complete RAWLANE2 coverage.

## Test Signals

- Compile coverage is the primary guard: any renamed or missing macro should fail consumers that build DPCS register lists or field tables.
- Register table smoke tests should verify that `dcn31_resource.c` still builds link encoder `le_shift` and `le_mask` tables with the DPCS shift/mask lists.
- Hardware or emulator validation should exercise link training across supported rates/widths and watch for failures in lane reset/request handshakes, RX adaptation, DCC calibration, and IRQ handling.
- Debug register readback can validate that `REG_UPDATE` on representative fields affects only the intended mask bits and preserves reserved bits.
- Regression signals include DisplayPort link training failures, PHY reset timeouts, unexpected RX/TX IRQ storms, DCC-on-demand interrupt issues, stuck PH2 calibration requests, and broken loopback/ATE diagnostics.

### subset-b-002303: lines 35754-38156

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 35754-38156

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header segment for CR1 raw lane and raw always-on lane registers. It covers lines 35754-38156 and defines 2,096 preprocessor constants: 1,050 `__SHIFT` macros and 1,046 `_MASK` macros across 307 register-comment groups. The count imbalance is expected for this slice because the range starts inside `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK` with two mask definitions whose shifts are in the previous chunk, and ends inside `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_OVRD_OUT_2` after several shifts and only the first masks.

The content is declarative only. It contains no C functions, structs, runtime branches, or local storage. Its public surface is the macro set used by AMDGPU display code to compose register field values for memory-mapped DPCS hardware.

## Purpose

The header provides symbolic bit positions and masks for DPCS CR1 raw-lane digital control registers. This chunk covers:

- The tail of raw lane 2 interrupt mask/status/clear definitions.
- Raw lane 2 PMA interface overrides, TX/RX control, ATE overrides, and PCS bridge fields.
- A broad raw lane 3 PCS, FSM, interrupt, PMA, TX control, RX control, and ATE register surface.
- Raw always-on lane 0 analog/adaptation/calibration registers.
- The beginning of raw always-on lane 1 analog/adaptation/calibration registers through the first masks of `RX_OVRD_OUT_2`.

The macros let consumer code write field-safe register programming logic without embedding magic constants for lane reset, request/ack handshakes, adaptation controls, PLL state, DCC calibration, signal detect, loopback, and lane diagnostics.

## Exported API Surface

There are no callable APIs or types. Every exported item is a C preprocessor constant following the generated naming pattern:

- `REGISTER__FIELD__SHIFT` gives the low bit for a register field.
- `REGISTER__FIELD_MASK` gives the bit mask for that field.

Important macro families in this chunk:

- `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_*`: lane 2 interrupt mask/status/clear fields for TX reset/request, RX phase-2 calibration request/disable, lane transceiver mode, RX-to-TX serial loopback, and DCC on-demand events.
- `DPCSSYS_CR1_RAWLANE2_DIG_PMA_XF_*`: lane 2 PMA cross-interface override and readback fields for MPLL enable/state, TX and RX request/reset, data-enable, async, beacon, loopback, RTUNE, MPHY PWM word/data/control, and RX adaptation handshake.
- `DPCSSYS_CR1_RAWLANE2_DIG_TX_CTL_*` and `RX_CTL_*`: lane 2 TX/RX FSM controls, clock controls, DCC continuous status, OCLA/UPCS observability, loss-of-signal masking, data-enable override, off-cancel, and adaptation continuous status.
- `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_*`: lane 2 PCS interface and ATE override fields for RX/TX valid/data/header/start/end/sync/standby/error/speed-change signaling, MPLL loop selection, RX power state, RX rate, and TX override inputs.
- `DPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_*`: lane 3 PCS interface fields, including TX/RX override inputs and outputs, PCS input/output readbacks, RX adaptation acknowledgements/FOM, directed TX pre/main/post values, lane number, reserved full fields, ATE overrides, EQ delta IQ, termination control, RX EQ overrides, and RX phase-2 calibration.
- `DPCSSYS_CR1_RAWLANE3_DIG_FSM_*`: lane 3 FSM override/status/monitor fields, fast calibration/adaptation triggers, common calibration status, TX DCC status/flags, OCLA, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR1_RAWLANE3_DIG_IRQ_CTL_*`: lane 3 IRQ status, clear, and mask fields matching the raw lane 2 interrupt family, plus reset return request.
- `DPCSSYS_CR1_RAWLANE3_DIG_PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and `PCS_XF_ATE_*`: lane 3 PMA/PCS/TX/RX controls parallel to the lane 2 definitions.
- `DPCSSYS_CR1_RAWAONLANE0_DIG_*`: always-on lane 0 analog calibration/adaptation fields for AFE/CTLE offsets, DFE references and offsets, phase adjustment, MPLL coarse tune, power-up/adaptation done status, fast flags, adaptation controls, LOS/sigdet controls, stats, RX overrides, signal-detect calibration, DCC calibration code banks, TX DCC bank access, firmware MM/adaptation/calibration configuration, transceiver mode, and TX DCC configuration.
- `DPCSSYS_CR1_RAWAONLANE1_DIG_*`: the same always-on lane pattern for lane 1 through `RX_OVRD_OUT_2`, ending mid-register at line 38156.

## Register Areas Covered

`RAWLANE2` in this chunk is mostly the second half of the lane's digital control surface. It starts with IRQ mask continuation and then defines PMA/PCS interface controls for forcing or reading lane-local TX/RX state. Fields model TX reset/request, RX reset/request, data enable, async enable, beacon enable, loopback controls, RTUNE request/ack, MPHY PWM interface values, RX adaptation acknowledgement, and PCS traffic/control signals. The TX/RX control registers expose lane-local FSM reset, bypass, clock enable, DCC status, loss-of-signal masking, and data-enable override behavior.

`RAWLANE3` is more complete in this slice. Its PCS interface groups expose both driver-side override values and PCS-side readback/status for TX and RX datapath signals. Its FSM groups expose calibration acceleration flags and status monitors for RX startup, AFE/DFE/bypass/reference-level/IQ calibration, continuous adaptation, common calibration, TX DCC, RCAL, and EQ updates. Its IRQ groups provide status, clear, and mask bits for reset, request, rate, pstate, adaptation, phase-2 calibration, loopback, DCC, TX reset, and TX request events. Its PMA/TX/RX/ATE groups mirror the lane 2 low-level control surface.

`RAWAONLANE0` and `RAWAONLANE1` describe analog and always-on lane sideband registers rather than the main PCS/PMA handshake surface. These fields cover adaptation results and controls, DFE tap/reference values, phase adjust mapping, MPLL coarse tuning, initial power-up status, fast calibration flags, TX/RX disable overrides, signal-detect filtering and calibration, RX squelch/termination/VREF overrides, DCC calibration code registers, firmware configuration windows, transceiver-mode override/readback, and TX DCC configuration.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior appears only when AMDGPU display code includes the header and passes these masks into register read/modify/write helpers.

The field names imply several hardware state machines and handshakes:

- TX/RX lane bring-up: reset, request, acknowledge, pstate, rate, data-enable, clock enable, and clock-ready fields coordinate PHY lane activation and shutdown.
- PCS/PMA boundary control: `PMA_XF` and `PCS_XF` fields expose override-enable/value pairs and readback inputs/outputs so low-level code can force or inspect lane-facing signals during training, diagnostics, and recovery.
- Interrupt processing: IRQ status bits have paired clear bits and mask registers for RX reset/request/rate/pstate/adaptation, phase-2 calibration, loopback, DCC on-demand, TX reset, and TX request events.
- Calibration and adaptation: FSM fast flags, AFE/DFE/IQ/reference-level fields, RX adaptation done/FOM/ack, DCC calibration code registers, signal-detect calibration, RTUNE, RCAL, and CMNCAL status fields represent lane-local analog calibration workflows.
- Diagnostic and test paths: ATE override fields, OCLA/UPCS observability fields, memory-address/status monitors, firmware configuration fields, and reserved/diagnostic fields expose manufacturing, validation, or firmware-controlled hooks.

No software persistence is implemented in this header. Hardware register values persist according to the ASIC's reset, power, and lane domains. Fields named `ADPT_CTL_*`, `FW_*_CONFIG`, DCC code banks, calibration code registers, reserved registers, and override values may latch state in hardware, but this chunk defines only bit layout, not policy for saving or restoring those values.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. The masks are intended to be included with companion generated DPCS 4.2.0 register address headers and used by AMDGPU/DC register helper macros that know how to read and write the corresponding MMIO addresses.

Integration points visible from the naming include:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, particularly DC link encoder, DPCS, PHY, lane training, and diagnostics paths.
- Companion `dpcs_4_2_0` address/offset headers that provide the register addresses matching these field definitions.
- DisplayPort/PHY link training and recovery code that controls TX/RX reset, request/ack, rate, pstate, data enable, and adaptation.
- Interrupt handlers or polling paths that consume the `DIG_IRQ_CTL_*` status, clear, and mask fields.
- Low-level bring-up, validation, and firmware interfaces using ATE overrides, OCLA/UPCS monitors, `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG`.
- Hardware calibration flows for MPLL, DCC, RX signal detect, RX VREF/squelch, RCAL/CMNCAL, AFE/DFE/IQ adaptation, and RTUNE.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently modify adjacent hardware bits in read-modify-write sequences.
- The range is lane-repetitive and partially sliced. Lane 2, lane 3, AON lane 0, and AON lane 1 definitions should remain structurally consistent except where the chunk begins or ends mid-register.
- Access semantics are not encoded in the macros. Status/readback fields, clear-on-write fields, override enables, and writable control values are adjacent and easy to misuse without the hardware register spec.
- Many controls are override/value pairs. Setting an override value without the corresponding enable, or leaving an enable asserted after diagnostics, can hold the PHY lane in an unintended state.
- Interrupt clear and mask fields have similar names to status fields. Consumers must distinguish status observation, write-to-clear, and mask programming.
- Calibration fields expose analog tuning surfaces. Invalid writes to DFE, DCC, signal-detect, VREF, termination, MPLL, or RTUNE controls can cause link training failures or lane instability that build tests will not catch.
- The final register group is incomplete in this chunk; merge/reconciliation should use the following chunk for the remaining `RAWAONLANE1_DIG_RX_OVRD_OUT_2` masks before evaluating per-register completeness.

## Test Signals

Useful validation signals are mostly compile-time, generated-data, and hardware-integration oriented:

- Preprocess or build AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static generated-header checks that each complete register group has matching `__SHIFT` and `_MASK` definitions; for this exact slice, expect 1,050 shifts and 1,046 masks because of the two partial boundaries.
- Diff this header against the authoritative DPCS 4.2.0 register database or generator output.
- Grep/compile consumer references for `DPCSSYS_CR1_RAWLANE2`, `DPCSSYS_CR1_RAWLANE3`, `DPCSSYS_CR1_RAWAONLANE0`, and `DPCSSYS_CR1_RAWAONLANE1` to catch renamed or missing fields.
- Hardware tests on ASICs using DPCS 4.2.0: DP link training, hotplug, lane disable/enable, rate and pstate transitions, suspend/resume, loopback diagnostics, RX adaptation, signal-detect behavior, DCC calibration, and interrupt clear/mask recovery.
- Register readback during bring-up to confirm reset/request/ack transitions, fast calibration status, CMNCAL/RCAL done bits, TX DCC status, RX adaptation done/FOM, lane transceiver mode, RX squelch/signal-detect status, and IRQ clear behavior.

## Chunk Notes For Merge

This document is source-tree aligned and intentionally covers only lines 35754-38156 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should include the first part of `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK`; the following chunk should finish `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_OVRD_OUT_2` and continue the raw AON lane 1 surface. The final per-file report should describe the whole file as generated ASIC register bitfield metadata, not handwritten driver logic.

### subset-b-002304: lines 38157-40592

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h - subset-b-002304

## Scope

This chunk covers lines 38157-40592 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h`. The range is a generated AMD DPCS 4.2.0 register field header segment containing 2,086 `#define` macros across 351 register comment blocks. It starts in the tail of the `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_OVRD_OUT_2` mask block, covers the remainder of RAWAON lane 1's late RX/DCC/firmware-control fields, full repeated RAWAON lane 2, lane 3, and lane X field layouts, then enters the CR1 SUPX common digital/analog PLL control area through the `DPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3` shift definitions.

## Purpose

The file is not executable logic. Its purpose is to publish the bit layout contract for DPCS 4.2.0 hardware registers to the AMD display driver. Each hardware field is represented by a `__SHIFT` macro and a matching `_MASK` macro, allowing driver code and register helper macros to construct, update, and decode packed register values without hard-coded bit positions.

This specific chunk describes two related areas:

- Per-lane RAWAON receiver/transmitter analog control and calibration fields for `DPCSSYS_CR1_RAWAONLANE*`.
- Shared `DPCSSYS_CR1_SUPX_*` digital and analog control fields for reference clocks, MPLLA/MPLLB programming, spread-spectrum clocking, prescaler, bandgap, RTUNE, and PLL analog controls.

The matching register-address side of this contract lives in `dpcs_4_2_0_offset.h`. For example, the covered chunk's offset companion maps `ixDPCSSYS_CR1_RAWAONLANE2_DIG_RX_ADPT_IQ` to `0x4202`, `ixDPCSSYS_CR1_RAWAONLANEX_DIG_TX_DCC_CONFIG` to `0x7051`, `ixDPCSSYS_CR1_SUPX_DIG_IDCODE_LO` to `0x8000`, and `ixDPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3` to `0x804e`.

## Important Macro Groups

### RAWAON Lane 1 Tail

The first lines complete the lane 1 `DIG_RX_OVRD_OUT_2` mask group, then cover late lane 1 controls:

- `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_OVRD_OUT_3` defines signal-detect low-frequency/high-frequency filter override values and enables.
- `DIG_RX_SIGDET_CAL`, `DIG_RX_SIGDET_HF_CODE`, and `DIG_RX_SIGDET_LF_CODE` define signal-detect calibration thresholds, enable bit, and 6-bit calibration tune codes.
- `DIG_RX_VREFGEN_EN`, `DIG_CAL_IOFF_CODE`, `DIG_CAL_ICONST_CODE`, and `DIG_CAL_VREFGEN_CODE` expose RX reference generator and calibration-code fields.
- `DIG_RX_DCC_CAL_*_CODE_{0,1}` expose 10-bit DCC calibration code fields for ICM, IDF, QCM, and QDF paths.
- `DIG_TX_DCC_BANK_ADDR`, `DIG_TX_DCC_BANK_DATA`, `DIG_TX_DCC_CONT`, and `DIG_TX_DCC_CONFIG` define TX DCC table access/control fields.
- `DIG_MPLL_BG_CTL`, `DIG_SIGDET_OUT_OVRD`, `DIG_SIGDET_OUT_IN`, `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, `DIG_FW_CALIB_CONFIG`, `DIG_LANE_XCVR_MODE_*`, and `DIG_RX_SIGDET_CONFIG` expose firmware, lane-mode, signal-detect, and MPLL-background control/status fields.

### RAWAON Lane 2, Lane 3, and Lane X

The chunk includes 82 register blocks each for `DPCSSYS_CR1_RAWAONLANE2_DIG_*`, `DPCSSYS_CR1_RAWAONLANE3_DIG_*`, and `DPCSSYS_CR1_RAWAONLANEX_DIG_*`. These are structurally repeated lane definitions. The covered fields include:

- Front-end offset and adaptation measurements: `AFE_ATT_IDAC_OFST`, `AFE_CTLE_IDAC_OFST`, `RX_ADPT_IQ`, `RX_ADAPT_FOM`, `RX_ADPT_ATT`, `RX_ADPT_VGA`, `RX_ADPT_CTLE`, `RX_ADPT_DFE_TAP1` through `RX_ADPT_DFE_TAP5`, and `RX_ADAPT_DONE`.
- DFE and slicer calibration fields: `DFE_*_VDAC_OFST`, `DFE_*_REF_LVL`, `RX_PHSADJ_LIN`, `RX_PHSADJ_MAP`, `RX_IQ_PHASE_ADJUST`, `RX_SLICER_CTRL_EVEN`, and `RX_SLICER_CTRL_ODD`.
- Power-up and MPLL status/control: `INIT_PWRUP_DONE`, `MPLLA_COARSE_TUNE`, `MPLLB_COARSE_TUNE`, `LANE_CMNCAL_MPLL_STATUS`, `MPLL_DISABLE`, `LANE_CMNCAL_RCAL_STATUS`, and `MPLL_BG_CTL`.
- Fast calibration flags: `FAST_FLAGS` and `FAST_FLAGS_2` contain many one-bit skip/fast-mode controls for RX adaptation, TX DCC calibration, RX DCC, VPHUD, VREF, signal detect, and continuous calibration paths.
- Manual override and observation fields: `TXRX_OVRD_IN`, `RX_LOS_MASK_CTL`, `RX_SIGDET_FILT_CTRL`, `STATS`, `RX_OVRD_OUT_1`, `RX_OVRD_OUT_2`, `RX_OVRD_OUT_3`, `SIGDET_OUT_OVRD`, and `SIGDET_OUT_IN`.
- Firmware-owned or firmware-visible controls: `ADPT_CTL_0` through `ADPT_CTL_7`, `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG`.

Lane X uses the same field model but the offset header places it at the `0x7000` lane-X indirect window rather than the lane 2/3 direct windows (`0x4200` and `0x4300`). This makes lane-X macros a generic or indexed lane access surface, while lane 2 and lane 3 are explicit lane instances.

### SUPX Digital Common Block

The `DPCSSYS_CR1_SUPX_DIG_*` section begins at `IDCODE_LO`/`IDCODE_HI` and then defines 60 register blocks for common digital control. Important groups include:

- Reference clock overrides: `REFCLK_OVRD_IN` has override value/enable pairs for digital, auxiliary, MPLL, HDMI, prescaler, and RX/TX reference-clock gating.
- MPLLA/MPLLB clock overrides: `MPLLA_DIV_CLK_OVRD_IN`, `MPLLA_HDMI_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, and `MPLLB_HDMI_CLK_OVRD_IN` define divider and enable override fields.
- MPLLA/MPLLB programming: `MPLLA_OVRD_IN_0` through `_5`, `MPLLB_OVRD_IN_0` through `_5`, SSC peak/stepsize registers, and CP/CP_GS override fields expose fractional PLL, spread-spectrum, PMIX, divider, clock-enable, output-enable, reset, calibration, feedback clock, gearshift, standby, and charge-pump parameters.
- SUP, prescaler, and level overrides: `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, and `LVL_OVRD_IN` define common power, bandgap, RTUNE, prescaler, and level override controls.
- ASIC input mirrors: `MPLLA_ASIC_IN_*`, `MPLLB_ASIC_IN_*`, `*_DIV_CLK_ASIC_IN`, `*_HDMI_CLK_ASIC_IN`, `ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, and `*_CP*_ASIC_IN` define the bit layout of values driven by ASIC-level logic into the SUPX/PLL block.

The SUPX fields are mainly low-level hardware programming hooks. Many have value/enable override pairs, so using the value bit without the corresponding enable bit is not sufficient to affect hardware behavior.

### SUPX Analog Block

The `DPCSSYS_CR1_SUPX_ANA_*` portion covers 15 analog register blocks in this chunk:

- `ANA_PRESCALER_CTRL` and `ANA_RTUNE_CTRL` expose prescaler, measurement, fast-start, RTUNE ATB, DAC, mode, and regulator feedback controls.
- `ANA_BG1`, `ANA_BG2`, `ANA_BG3`, and `ANA_SWITCH_PWR_MEAS` expose bandgap/reference selection, temperature/power measurement, analog test bus, and switch controls.
- `ANA_MPLLA_MISC1`, `ANA_MPLLA_MISC2`, and `ANA_MPLLA_OVRD` expose MPLLA analog override, calibration, reset, gearshift, boost, lock, feedback-clock, and enable controls.
- `ANA_MPLLA_ATB1` through `ANA_MPLLA_ATB3` expose analog-test-bus measurement selection fields.
- `ANA_MPLLA_CTR1`, `ANA_MPLLA_CTR2`, and the beginning of `ANA_MPLLA_CTR3` expose PLL charge-pump, VREF, register, SPO, and internal-capacitor control fields.

The requested line range ends after `DPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3__RESERVED_15_8__SHIFT`. The `_MASK` macros for `MPLLA_CTR3` are immediately outside this chunk at lines 40593-40596, so this chunk is boundary-split in the middle of a register block.

## APIs, Types, and Functions

There are no C functions, enums, structs, or runtime APIs in this chunk. The public interface is the macro namespace itself:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field's packed bit mask.
- Reserved-field masks such as `RESERVED_15_8_MASK` document the occupied but not semantically programmable parts of a 16-bit indirect register field layout.

The AMD display code consumes these definitions indirectly through table initialization and register helper macros. `dcn31_resource.c` includes both `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`, then builds `link_enc_regs`, `le_shift`, and `le_mask`. In the same resource file, `dcn31_link_encoder_create()` passes those tables into `dcn31_link_encoder_construct()`. The DPCS-specific table shape is declared in `display/dc/dio/dcn31/dcn31_dio_link_encoder.h` through `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(mask_sh)`.

This exact chunk's RAWAON and SUPX macros are not referenced by name in the display code searched under `drivers/gpu/drm/amd/display`. They are still part of the generated hardware register surface and may be used by bring-up, debug, firmware-directed sequences, or future code that accesses indirect CR registers via `RDPCS_TX_CR_ADDR`/`RDPCS_TX_CR_DATA`.

## Control Flow

The header itself has no control flow. The effective runtime flow around these definitions is:

1. A DCN31 resource file includes the generated offset and shift/mask headers for the ASIC generation.
2. Resource initialization creates static register, shift, and mask tables for link encoders.
3. Link encoder construction stores those tables in the encoder object.
4. Link encoder operations use register helper macros and the table entries to read, modify, and write hardware registers.
5. For indirect DPCS CR registers, software selects a CR address through the RDPCS CR address/data mechanism and uses these field masks/shifts to encode or decode the 16-bit payload.

The RAWAON/SUPX fields describe lane calibration and PLL state machines, but the sequencing of those machines is in hardware/firmware and in the link-encoder or PHY-control code outside this generated header.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The state they describe is hardware state:

- Lane adaptation and DFE values may represent live measured state, firmware-owned calibration state, or manually programmed override values.
- `*_DONE`, `*_STATUS`, `*_OUT_IN`, and `STATS` fields expose observable status bits.
- Override fields can persist in hardware registers until reset, power-gating, firmware reprogramming, or a driver write changes them.
- PLL, prescaler, RTUNE, and bandgap fields can affect link-clock stability and analog PHY behavior; wrong persistence across power transitions may lead to failed link training or unstable PHY output.

Because most masks are 16-bit-window masks with `0x0000FFFFL` or smaller values, callers must preserve reserved bits when doing read-modify-write sequences unless the hardware programming guide explicitly says otherwise.

## Dependencies and Integration Points

- `dpcs_4_2_0_offset.h` supplies the corresponding register offsets and indirect CR addresses.
- `dcn31_resource.c` is the direct integration point for this generated header in the DCN31 display stack.
- `dcn31_dio_link_encoder.h` defines the link encoder table macros that consume DPCS register/mask names for RDPCSTX-facing fields.
- `reg_helper.h` and AMD display register helper macros combine register offsets, masks, and shifts into typed register operations.
- The wider DPCS generated-header family (`dpcs_4_2_2_*`, `dpcs_4_2_3_*`, older `dpcs_3_*`) provides cross-generation layouts with similar naming. Those headers are useful for drift comparison, but mixing generations is risky because names may compile while bit layouts or offsets differ.

## Risks and Edge Cases

- Hardware contract drift is the main risk. A wrong mask, shift, or offset can silently program the wrong analog field.
- The chunk boundary splits `DPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3`: this document covers the shift macros, while the mask macros are in the following chunk. Any merge or reconciliation lane should join that register block before producing a final per-file report.
- Many fields are paired override value/enable bits. Tests or reviews should check both halves of any manual override sequence.
- RAWAON lane 2, lane 3, and lane X blocks are intentionally repetitive. Copy/paste or generation errors can produce a single-lane mismatch that is hard to notice in normal compilation.
- Several fields are analog calibration or PLL controls. Bad values can cause physical link failures, intermittent training errors, signal-detect false positives/negatives, clock instability, or display blanking.
- Reserved bits are explicitly defined. Blind writes of full 16-bit values can disturb reserved hardware state if firmware or hardware expects those bits preserved.

## Test Signals

Useful validation signals for changes touching this area include:

- Build coverage for DCN31 display code that includes `dpcs_4_2_0_sh_mask.h`, especially `dcn31_resource.c`.
- Compile-time failures from missing or renamed macros used by `DPCS_DCN31_MASK_SH_LIST`, `LINK_ENCODER_MASK_SH_LIST_DCN31`, or register helper initializers.
- Static comparison of each covered `__SHIFT`/`_MASK` pair: masks should line up with the documented shift and field width, and reserved masks should fill the unused bits in the 16-bit field window.
- Cross-check against `dpcs_4_2_0_offset.h` to ensure each register block in this chunk has an offset entry.
- Hardware or emulator smoke tests for DisplayPort/HDMI link training on DCN31 ASICs, including lane training, FEC readiness, PHY power transitions, DP Alt Mode, and PLL clock programming.
- Debug traces for signal detect, lane adaptation done bits, DCC calibration done/skip behavior, and MPLL lock/status when link bring-up fails.

### subset-b-002305: lines 40593-42955

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 40593-42955

## Scope

This chunk is a generated AMD DPCS 4.2.0 register shift/mask header segment. It covers line 40593 through line 42955 and defines 2,132 preprocessor constants: 1,065 `__SHIFT` macros and 1,067 `_MASK` macros.

The count mismatch is a chunk-boundary artifact. The range starts in the middle of `DPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3`, where four mask definitions are included but the matching shifts are immediately before line 40593. The range ends after the first two shift definitions for `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_1`; the remaining shifts and masks for that register follow after line 42955.

The content is declarative only. It exports bitfield positions and masks for DPCS CR1 SUPX and LANEX hardware registers; it contains no C functions, structs, runtime storage, or branching logic.

## Purpose

The header gives AMDGPU display code symbolic field definitions for programming DPCS 4.2.0 display PHY, PLL, lane, adaptation, power, calibration, statistics, and analog override registers. Consumer code includes these macros together with companion register-address headers to form read-modify-write operations against memory-mapped display hardware without open-coded bit positions.

In this range, the exported constants cover:

- SUPX analog MPLLA and MPLLB controls, overrides, ATB measurement fields, PLL tuning fields, and reserved windows.
- SUPX digital MPLL power-control, PLL lock/calibration/timer, spread-spectrum, bandgap/reference power-up, resistor tuning, and analog status/override fields.
- LANEX ASIC-facing lane, TX, RX, equalization, CDR/VCO, and override input/output fields.
- LANEX TX and RX power-state, power-up timing, DCC calibration, clock alignment, loopback/BERT, CDR, VCO calibration, DPLL, adaptation, and statistics fields.
- LANEX MPHY and analog TX/RX override fields for terminations, equalization, receiver front-end tuning, calibration DAC selection, slicer/scope control, status readback, and signal-detect controls.

## Exported API Surface

There are no callable APIs or local types. The public surface is the macro namespace used by AMD display code after including this generated ASIC register header.

Important macro families:

- `DPCSSYS_CR1_SUPX_ANA_MPLLA_*` and `DPCSSYS_CR1_SUPX_ANA_MPLLB_*`: analog PLL control and measurement fields. The chunk begins with `MPLLA_CTR3` masks, then covers `MPLLA_CTR4`, `MPLLA_CTR5`, `MPLLA_RESERVED1/2`, and the analogous MPLLB `MISC`, `OVRD`, `ATB`, `CTR`, and reserved registers.
- `DPCSSYS_CR1_SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR1_SUPX_DIG_MPLLB_MPLL_PWR_CTL_*`: digital PLL override, status, DAC max range, lock/power timers, calibration, and analog DAC output fields for the two MPLL blocks.
- `DPCSSYS_CR1_SUPX_DIG_CLK_RST_*` and `DPCSSYS_CR1_SUPX_DIG_RTUNE_*`: bandgap/reference power-up timing, reference voltage/power-up behavior, and RTUNE calibration configuration/status/set-value fields.
- `DPCSSYS_CR1_SUPX_DIG_ANA_*`: digital-to-analog override and status outputs for MPLLA, MPLLB, RTUNE, bandgap, and PMIX controls.
- `DPCSSYS_CR1_LANEX_DIG_ASIC_*`: ASIC-side per-lane TX/RX controls, overrides, equalization controls, VCO/CDR inputs, loopback/status outputs, and OCLA control.
- `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_*` and `DPCSSYS_CR1_LANEX_DIG_RX_PWRCTL_*`: transmit and receive power-state programming plus power-up timing registers.
- `DPCSSYS_CR1_LANEX_DIG_RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*`: receiver VCO calibration, CDR loop, and DPLL frequency/boundary fields.
- `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL_*`: receiver adaptation configuration, reset, status, DAC selection, CR-bank access, slicer, DFE, CTLE, VGA, and attenuator fields.
- `DPCSSYS_CR1_LANEX_DIG_RX_STAT_*`: match/statistic control, masks, counters, sample counters, stop control, and calibration compare clock control fields.
- `DPCSSYS_CR1_LANEX_DIG_ANA_*`: analog TX/RX override outputs, termination-code override and clock strobes, TX equalization override fields, RX control/power/VCO/calibration/AFE/scope/slicer/IQ/status/MPHY/signal-detect fields.

## Register Areas Covered

The SUPX analog area exposes two similar MPLL paths. `MPLLA` and `MPLLB` fields describe charge-pump, regulator, SPO, VINT capacitor, standby, calibration-lock, bypass, DLL/divider, ATB measurement, and override behavior. These names indicate low-level PLL tuning and diagnostic access rather than ordinary display policy.

The SUPX digital area manages MPLL power and calibration sequencing. It includes override enable/data bits, reference-clock enable, reset, calibration requests, lock/power timers, DAC range and output fields, spread-spectrum type, clock/reset power-up timing, RTUNE comparator/code fields, and analog-facing override outputs. This area is the bridge between driver-controlled digital sequencing and the analog MPLL/RTUNE/BG hardware.

The LANEX ASIC interface area maps the logical lane controls exchanged with the rest of the display engine. It defines lane reset, TX/RX reset and enable, width/rate, DETRX, PMA/PCS power state, loopback, equalization, clock-shift, data-enable, CDR/VCO inputs, and status outputs. The repeated `*_OVRD_IN`, `*_OVRD_OUT`, `*_ASIC_IN`, and `*_ASIC_OUT` naming shows that this block supports both normal ASIC-driven operation and explicit override paths.

The LANEX TX/RX datapath area covers state-machine programming for link bring-up and diagnostics. TX fields include P-state settings, power-up timers, duty-cycle-correction DAC bank/address/data/ack fields, clock alignment, and LBERT control. RX fields include P-state settings, power-up timers, VCO calibration control/status/time, LBERT control/error, CDR loop controls/status, DPLL frequency/bounds, and receiver adaptation controls/status.

The LANEX analog output area exposes direct analog override signals. TX fields control terminations, EQ main/post/pre cursors, EQ clock strobes, idle detect, lane power, clock shifting, and DCC. RX fields control AFE attenuation/VGA/CTLE, CDR/VCO frequency tuning, calibration muxes and DACs, slicer even/odd controls, IQ phase adjustment, scope capture, MPHY low-speed controls, status readback, RX termination override, and the beginning of signal-detect high-frequency threshold override fields.

## Control Flow And State Behavior

This file has no local control flow. Runtime behavior appears when AMDGPU display code uses these constants with register read/write helpers.

The field names imply several hardware state machines and handshakes:

- PLL bring-up and tuning use `MPLL_PWR_CTL_*` overrides, power/lock timers, reset/calibration controls, DAC outputs, spread-spectrum selection, and analog `CTR*` fields.
- Analog power and reference sequencing use bandgap and reference power-up timers plus status/override fields for BG, PMIX, VREG, and RTUNE.
- Link-lane activation uses per-lane TX/RX reset, enable, width, rate, PMA/PCS power-state, clock-ready, data-enable, DETRX, and loopback fields.
- Receiver clock recovery and adaptation use VCO calibration controls/status, CDR loop controls/status, DPLL frequency/bounds, adaptation configuration, DFE/CTLE/VGA/ATT status, DAC selection, and calibration compare clock controls.
- Diagnostics use LBERT controls/errors, RX statistic match/mask/control/counter registers, analog scope controls, ATB measurement selectors, and status readback fields.
- Self-clearing strobes are visible in fields such as RX DAC control enable, AFE update enable, IQ phase-adjust clock, RX termination clock, TX EQ clock, and VCO frequency tune clock; consumers must account for hardware-cleared bits and optional self-clear-disable fields.

No software persistence is implemented in this header. Hardware register contents persist only according to the ASIC reset and power domains. Fields named `RESERVED`, `STAT`, `STATUS`, `ACK`, `RESULT`, `COUNTER`, `SPARE`, `DAC`, and `*_CODE` may expose latches, counters, hardware readback, or programmable calibration values, but this chunk does not define policy for retaining or restoring them.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. These macros are intended to be included with generated DPCS 4.2.0 address headers and consumed by AMDGPU/DC register helper macros that combine a register offset, field shift, and field mask.

Integration points visible from the naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DPCS link encoder, PHY, clock, lane, and diagnostics code.
- DPCS 4.2.0 generated address headers that define the register offsets matching this shift/mask header.
- DisplayPort and HDMI PHY programming paths that set TX/RX lane width, rate, power state, terminations, equalization, PLL, and clock-recovery behavior.
- Link training and recovery paths that inspect RX CDR/VCO/adaptation status, lane acknowledgements, LBERT errors, and RX statistic counters.
- Suspend/resume and hotplug paths that reinitialize clocks, PLLs, analog power, lane P-states, and calibration values after power-domain transitions.
- Hardware validation and debug tools that use ATB, OCLA, LBERT, scope, statistic, CR-bank, and analog override fields.

## Risks

- Generated-header drift is the dominant risk. A wrong shift or mask can silently write adjacent analog or PHY control bits during read-modify-write operations.
- Many registers mix writable controls with readback/status bits. Examples include request/ack, enable/status, counter/result, calibration control/status, and interrupt-like statistic fields. Consumers need the hardware access semantics from the register database, not just these masks.
- The analog override families can bypass normal training or firmware-controlled behavior. Misusing `*_OVRD_*` fields can leave PLLs, RX front-end tuning, lane power states, or signal-detect thresholds in invalid states.
- Boundary slicing matters for reconciliation. `MPLLA_CTR3` is incomplete at the start of this chunk and `SIGDET_OVRD_OUT_1` is incomplete at the end, so per-file merge logic should combine adjacent chunks before checking per-register completeness.
- Repeated MPLLA/MPLLB and per-lane TX/RX field patterns are copy-generation sensitive. A single prefix, mask width, or shift error can affect only one PLL instance or one lane path and may not be caught by compile-only testing.
- Reserved masks are exposed beside active fields. Driver code should preserve reserved bits unless the hardware specification explicitly defines a value.
- Self-clearing strobe fields and self-clear-disable fields can produce timing-sensitive bugs if software assumes ordinary persistent bit storage.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Compile/preprocess AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static generated-register checks that compare this header against the DPCS 4.2.0 register database.
- Macro-pair checks for matching `__SHIFT` and `_MASK` definitions, allowing the expected boundary imbalance for this sliced range: four masks-only entries from `MPLLA_CTR3` at the start and two shifts-only entries from `SIGDET_OVRD_OUT_1` at the end.
- Grep/compile checks for consumers of `DPCSSYS_CR1_SUPX_ANA_MPLLA`, `DPCSSYS_CR1_SUPX_ANA_MPLLB`, `DPCSSYS_CR1_SUPX_DIG_MPLL`, `DPCSSYS_CR1_LANEX_DIG_ASIC`, `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL`, and `DPCSSYS_CR1_LANEX_DIG_ANA` macros.
- Runtime display tests on ASICs using DPCS 4.2.0: DP/HDMI link training, hotplug, suspend/resume, lane power-state transitions, PLL calibration/lock, RX VCO/CDR convergence, receiver adaptation convergence, and error-recovery paths.
- Diagnostic readback during bring-up for MPLL lock/status, RTUNE status, bandgap/reference power-up behavior, lane ACK/status fields, RX VCO calibration result, CDR status, DPLL bounds, adaptation status, LBERT errors, statistic counters, analog status, and self-clearing strobe behavior.

## Chunk Notes For Merge

This chunk is source-tree aligned and intentionally documents only lines 40593-42955 of `dpcs_4_2_0_sh_mask.h`. Adjacent chunks should supply the missing `MPLLA_CTR3` shifts before this range and the remaining `SIGDET_OVRD_OUT_1` definitions after this range. The later per-file merge should treat the whole file as a generated ASIC register bitfield map for AMD DPCS 4.2.0, not handwritten driver logic.

### subset-b-002306: lines 42956-45337

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 42956-45337

## Scope

This chunk covers lines 42956-45337 of the generated AMD DPCS 4.2.0 shift/mask header. It contains 2,131 `#define` entries: 1,065 `__SHIFT` macros and 1,086 `_MASK` macros, plus 249 register-block comments. The count imbalance is expected for this sliced range: it starts in the middle of `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_1`, so some masks appear for fields whose shift definitions are above line 42956, and it ends after only the first shift for `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`.

The content is declarative only. It defines preprocessor constants for bit positions and masks in DPCS/RDPCS transmitter CR registers. There are no C functions, structs, enums, local variables, branches, loops, or runtime allocations in this range.

## Purpose

The header gives AMDGPU display code symbolic bitfield locations for programming ASIC display PHY and controller registers. Consumer code combines the `__SHIFT` and `_MASK` constants with memory-mapped register read/modify/write helpers, avoiding hard-coded bit numbers in link, PHY, clock, calibration, interrupt, and diagnostics paths.

This chunk covers the latter part of the `DPCSSYS_CR1` lane/RAWLANEX CR surface and the beginning of the `DPCSSYS_CR2` support CR surface:

- CR1 lane analog TX/RX controls: signal detect, DCC DAC calibration, TX power/clock/termination, analog test bus, RX CDR/SLC/power/squelch/calibration, and measurement muxes.
- CR1 RAWLANEX PCS/PMA crossbar fields: TX/RX override inputs, PCS/PMA input/output status, adaptation status, equalization controls, lane numbering, ATE controls, MPHY override, and lane RTUNE controls.
- CR1 lane FSM, interrupt, TX control, and RX control fields: fast calibration/adaptation/status monitors, CR lock, DCC flags/status, OCLA controls, IRQ status/clear/mask fields, and TX/RX FSM override knobs.
- CR2 support digital fields after the `addressBlock: dpcssys_cr2_rdpcstxcrind` marker: IDCODE, refclock overrides, MPLLA/MPLLB clock and PLL programming overrides, SSC peak/stepsize fields, supervisor overrides, prescaler, level, ASIC input mirrors, bandgap, and charge-pump fields.
- CR2 support analog fields: prescaler, RTUNE, bandgap, switch-power measurement, MPLLA controls, and the first MPLLB analog controls through the opening of `MPLLB_ATB3`.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated macro namespace. Important families in this slice include:

- `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_*`: high-frequency and low-frequency signal-detect thresholds, filter enable, calibration tune, calibration enable, and per-field override-enable bits.
- `DPCSSYS_CR1_LANEX_DIG_ANA_TX_DCC_DAC_OVRD_OUT*` and `DPCSSYS_CR1_LANEX_ANA_TX_DCC_*`: TX duty-cycle-correction DAC range, comparator, control select, clock compensation, raw DAC register, and override gates.
- `DPCSSYS_CR1_LANEX_ANA_TX_*`: TX measurement override, power override, alternate bus, ATB measurement points, termination code/update/reset controls, MPLLA/MPLLB clock selection, LFPS/RXDET/boost/mode options, and reserved analog tuning registers.
- `DPCSSYS_CR1_LANEX_ANA_RX_*`: RX clock, CDR/deserializer, slicer control, RX power, squelch, calibration, ATB reference/measurement/force, and reserved RX analog fields.
- `DPCSSYS_CR1_RAWLANEX_DIG_PCS_XF_*`: PCS TX/RX override and PCS in/out fields, RX adaptation acknowledgement and figure-of-merit, transmitter pre/main/post cursor direction requests, lane number, ATE, RX equalization override, PH2 calibration, and TX/RX termination controls.
- `DPCSSYS_CR1_RAWLANEX_DIG_FSM_*`: FSM override control, memory address/status monitors, fast startup/adaptation/calibration phase controls, continuous calibration/adaptation states, flags, CR lock, TX DCC state, OCLA, CMNCAL status, and IQ phase offset.
- `DPCSSYS_CR1_RAWLANEX_DIG_IRQ_CTL_*`: RX/TX reset/request/rate/pstate/adaptation/PH2/loopback/DCC interrupt status, clear, and mask fields.
- `DPCSSYS_CR1_RAWLANEX_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*`: PMA lane/supervisor/TX/RX override fields, PMA input mirrors, RTUNE, MPHY, TX/RX FSM control, clock control, continuous status, loss-of-signal masking, data-enable override, and OCLA taps.
- `DPCSSYS_CR2_SUP_DIG_*`: CR2 support ID, refclock, MPLLA/MPLLB div/HDMI clock override, PLL override input groups, SSC peak/step-size fields, charge-pump override fields, supervisor/prescaler/level overrides, ASIC input mirrors, bandgap, and CP/CP_GS mirrors.
- `DPCSSYS_CR2_SUP_ANA_*`: CR2 prescaler and RTUNE analog controls, bandgap trims/overrides, power-measure switches, MPLLA/MPLLB misc and override controls, ATB measurement muxes, PLL control words, and reserved PLL/DLL bypass/tuning fields.

## Register Areas Covered

The CR1 lane analog area is centered on per-lane PHY bring-up and measurement. TX-side fields expose fast-start, loopback, AC JTAG, clock loopback, power gate enables, serial/data/refgen/clock enables, alternate bus routing, termination code programming, DCC calibration, MPLLA/MPLLB clock enable selection, LFPS behavior, RX detect override, vreg boost, and analog test-bus selectors. RX-side fields expose clock source/rate/divider selection, CDR/deserializer options, slicer control, RX power enables, squelch threshold/filter/calibration, reference controls, measurement muxes, forced analog test-bus values, and calibration-ready/status fields.

The CR1 RAWLANEX PCS/PMA area is a digital bridge between the PHY analog block and the PCS/PMA control plane. It defines override inputs, output mirrors, PCS input mirrors, RX adaptation controls, adaptation acknowledgements, figure-of-merit readback, TX pre/main/post cursor direction feedback, lane number programming/readback, equalization override fields, phase-2 calibration controls, ATE paths, and TX/RX termination controls. PMA fields mirror lane/supervisor/TX/RX control and status across override and ASIC-input style registers.

The CR1 FSM and IRQ area describes hardware state machines and event signaling. Fast calibration fields name startup, RX adaptation, AFE/DFE calibration, bypass calibration, reference-level calibration, IQ calibration, supervisor setup, TX common-mode, TX RXDET, RX power-up, VCO wait/calibration, and continuous calibration/adaptation/data/phase/AFE phases. Status fields include flags, lock state, TX DCC flags/status, CMNCAL MPLL/RCAL status, and RX IQ phase offset. IRQ fields are organized as status, clear, and mask registers for RX reset/request/rate/pstate/adaptation disable/request, lane transceiver mode, RX PH2 calibration request/disable, RX-to-TX serial loopback enable, DCC on-demand, and TX reset/request.

The CR2 support digital area begins a new address block. It covers shared/supervisory state rather than one CR1 lane: ID code, reference clock override, MPLLA/MPLLB divider and HDMI clock override, PLL override input bundles, SSC peak and step-size programming, charge-pump controls, supervisor override output, prescaler override, level override, and ASIC-input mirrors for MPLL, clocks, supervisor, level, bandgap, and charge-pump signals.

The CR2 support analog area exposes global support circuits: prescaler enable/division/source, RTUNE override/request/reference selection, bandgap trims and bypasses, switch-power measurement controls, and two parallel MPLL analog control surfaces. MPLLA is fully represented in this chunk from misc/override/ATB through control and reserved registers. MPLLB starts with misc, override, ATB1, ATB2, and the first `meas_iv_bias` shift of ATB3 before the chunk boundary.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior is created by AMDGPU display code that includes the header and writes the corresponding hardware registers.

The field names imply several hardware state machines and handshakes:

- PHY bring-up and clocking: enable/reset, reference-clock override, MPLLA/MPLLB clock enable, word-clock enable, prescaler, and clock input/status mirrors must be sequenced around link training and resume.
- TX analog calibration: DCC DAC range/control/select, DCC comparator, termination update/reset/code override, TX RXDET, LFPS, loopback, fast-start, and analog power bits influence transmitter electrical behavior.
- RX analog calibration and adaptation: signal-detect thresholds/filters/calibration, CDR/deserializer, slicer control, RX power, squelch, reference-level, IQ, AFE, DFE, and continuous adaptation fields reflect calibration phases and status.
- PCS/PMA override paths: many `OVRD_IN`, `OVRD_OUT`, `PCS_IN`, `PCS_OUT`, `PMA_IN`, and `ASIC_IN` groups separate software-forced values from hardware or firmware-generated values. Consumers must preserve the override-enable/value pairing.
- Interrupt handling: status/clear/mask triads expose latch-and-clear behavior for reset/request/rate/pstate/adaptation/PH2/loopback/DCC/TX events.
- PLL and support-circuit programming: CR2 MPLLA/MPLLB override, SSC, charge-pump, bandgap, RTUNE, and prescaler fields feed global link-clock generation and calibration.
- Diagnostics and factory paths: ATB, OCLA, ATE, JTAG, memory/status monitor, FOM, and raw reserved windows are intended for bring-up, validation, or low-level debug rather than normal high-level policy.

No software persistence is implemented here. Hardware register contents persist or reset according to ASIC power/reset domains. Fields named `RESERVED`, `SPARE`, `MEM_ADDR_MON`, status monitors, ATB selectors, and lock/status flags expose hardware storage or readback semantics, but this chunk does not define policy for saving/restoring them.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. These macros are normally paired with the generated DPCS 4.2.0 address/header files that define register offsets, and with AMDGPU/DC helper macros that compose field values from mask and shift constants.

Integration points visible from the naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC link encoder, DPCS/RDPCS PHY, DisplayPort, HDMI, clock, and PHY calibration paths.
- Register access helpers that use generated field names to perform read-modify-write operations against DPCS CR indirect registers.
- DisplayPort lane training and equalization code, reflected by TX pre/main/post cursor direction, RX EQ override, adaptation acknowledgement, FOM, RX rate/pstate, and per-lane PCS/PMA control fields.
- PHY analog bring-up and diagnostic code, reflected by ATB, ATE, OCLA, JTAG, DCC, RXDET, LFPS, RTUNE, bandgap, prescaler, and MPLL fields.
- Firmware or hardware state-machine coordination paths, reflected by `ASIC_IN`, `OVRD_IN`, `OVRD_OUT`, FSM status, IRQ mask/clear/status, and support-block override input/output fields.
- Generated register database tooling: this file should be treated as generated hardware metadata rather than a hand-authored algorithmic module.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently write adjacent hardware bits during read-modify-write sequences.
- This range has dense parallel namespaces: CR1 lane analog, CR1 RAWLANEX PCS/PMA/FSM/IRQ/TX/RX control, and CR2 support digital/analog. Prefix mistakes can cause code to use a field from the wrong instance or address block while still compiling.
- Many registers combine value fields with adjacent override-enable bits. Setting the value without the override enable, or leaving an override enable asserted accidentally, can produce hard-to-debug PHY behavior.
- Status, clear, and mask registers are adjacent in the IRQ namespace. Treating a clear bit like persistent state, or writing a status mirror as if it were control, can drop interrupts or leave stale latches.
- RX/TX analog controls, PLL charge-pump/SSC settings, bandgap, RTUNE, and reserved PLL/DLL fields can affect signal integrity and link stability. Consumer changes need hardware-spec validation, not just compile coverage.
- The chunk boundaries are partial. The beginning omits some `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_1` shifts, and the end omits most of `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`; merge tooling must combine adjacent chunks before deriving complete per-register counts.
- Full-width or reserved bit windows may be present in adjacent source regions. Consumers should preserve documented reset values and avoid treating reserved fields as general-purpose storage.

## Test Signals

Useful validation signals are build-time, generation-time, and hardware-integration oriented:

- Preprocess/compile AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static generated-header checks that every complete register block has matching `__SHIFT` and `_MASK` definitions and that masks correspond to width and shift. For this sliced chunk, the expected local count is 1,065 shifts and 1,086 masks because of partial boundaries.
- Diff or schema validation against the authoritative DPCS 4.2.0 register database, especially around CR1 RAWLANEX and CR2 support address-block boundaries.
- Grep/compile checks for consumers of `DPCSSYS_CR1_LANEX_ANA_TX`, `DPCSSYS_CR1_LANEX_ANA_RX`, `DPCSSYS_CR1_RAWLANEX_DIG_PCS_XF`, `DPCSSYS_CR1_RAWLANEX_DIG_FSM`, `DPCSSYS_CR1_RAWLANEX_DIG_IRQ_CTL`, `DPCSSYS_CR1_RAWLANEX_DIG_PMA_XF`, and `DPCSSYS_CR2_SUP_*` macros.
- Runtime display tests on ASICs using DPCS 4.2.0: DP and HDMI link training, hotplug, suspend/resume, link-rate changes, lane equalization/adaptation, RX/TX reset recovery, and interrupt clear/mask behavior.
- PHY bring-up readback for reset, clock enable/status, lane adaptation acknowledgement, FOM, CR lock, DCC status, CMNCAL MPLL/RCAL status, RX IQ phase offset, RTUNE, bandgap, prescaler, and MPLL override/status fields.
- Diagnostic coverage for ATB/OCLA/ATE paths when hardware validation or manufacturing flows depend on these fields.

## Chunk Notes For Merge

This document intentionally covers only lines 42956-45337 of `dpcs_4_2_0_sh_mask.h`. The previous chunk should provide the omitted start of `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_1`, and the following chunk should complete `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3` and subsequent CR2 support fields. The later per-file merge should describe this source as a generated ASIC bitfield map, not handwritten driver logic, and should preserve the distinction between CR1 per-lane/RAWLANEX controls and CR2 support-block controls.

### subset-b-002307: lines 45338-47685

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 45338-47685

## Scope And Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for Display Core Next display PHY/DPCS hardware. It is declarative metadata only: it defines C preprocessor constants for bit positions and bit masks, and contains no executable functions, structs, enums, variables, allocations, locks, or direct MMIO accesses.

The requested range contains 2,145 complete `#define` entries: 1,072 `__SHIFT` constants and 1,073 `_MASK` constants. The one extra mask is a chunk-boundary artifact: line 45338 begins inside `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`, after `meas_iv_bias__SHIFT` was emitted just before the requested range. The chunk then covers 203 register groups: 54 supervisor/common CR2 groups, 85 lane 0 groups, and 64 lane 1 groups. It ends inside the lane 1 RX VCO calibration status area at `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_0`; `RX_VCO_STAT_1` starts after this chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The exported interface is the generated macro naming convention consumed by AMD display register helper tables:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to isolate or update the field.
- `RESERVED_*`, `RSVD_*`, and similarly named fields preserve undocumented or reserved bit ranges so generated layouts stay aligned with the hardware register database.

Major macro families in this chunk are:

- CR2 supervisor analog MPLLB controls: `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`, `CTR1-5`, and `RESERVED1-2` describe MPLLB analog measurement, charge pump, regulator, Vref, standby, spoof/calibration-lock, bypass, DLL, divider, and reserved low-byte fields.
- CR2 supervisor digital MPLL power and SSC controls: paired `DPCSSYS_CR2_SUP_DIG_MPLLA_*` and `MPLLB_*` groups define MPLL override enables, feedback/PCLK enables, fast power-up/lock controls, divider selection, state readback, DAC range/input/output, lock/stable/gearswitch/PCLK timers, calibration override, and spread-spectrum generator spread-type override.
- Clock/reset and resistor tuning support: `CLK_RST_BG_PWRUP_TIME_*`, `CLK_RST_REF_PWRUP_TIME_0`, `CLK_RST_REF_VPHUD`, and `RTUNE_*` groups expose bandgap/reference timing, VPH/U/D reference bits, RTUNE request/force/set/readback values, calibration counters, and TX calibration code.
- Supervisor digital-to-analog override/readback groups: `SUP_DIG_ANA_MPLLA_OVRD_OUT_*`, `MPLLB_OVRD_OUT_*`, `RTUNE_OVRD_OUT`, `ANA_STAT`, `ANA_BG_OVRD_OUT`, and `PMIX_OVRD_OUT` describe override values and enable bits driven toward analog MPLL, RTUNE, bandgap, and PMIX circuits.
- Lane 0 digital ASIC interface: `DPCSSYS_CR2_LANE0_DIG_ASIC_*` defines software override and normal ASIC-facing TX signals such as request, pstate, rate, width, MPLL select, data enable, detect-RX, inversion, reset, clock-ready, low-power detect, beacon, async drive/data, and cross-lane shift handshakes, plus TX/RX output ACK/status fields.
- Lane 0 TX power, DCC, clock-align, LBERT, and RX statistics: `LANE0_DIG_TX_PWRCTL_*` gives pstate recipes, power-up timing, DCC CR-bank/DAC controls, and DAC ACK/address fields. `TX_CLK_ALIGN`, `TX_LBERT`, and `RX_STAT_*` cover clock alignment, loopback BERT control, match/mask programming, sample counters, statistic counters, calibration comparison clocking, stop, and done/status bits.
- Lane 0 digital/analog TX controls: `LANE0_DIG_ANA_TX_*` and `LANE0_ANA_TX_*` expose digital override values for analog TX clock/data/reset/refgen/serial/MPLL enables, termination-code overrides, TX equalization override banks, DCC DAC overrides, RX detect/status readbacks, analog measurement, power override, alternate bus/JTAG/test bus fields, DCC DAC programming, termination-code update/reset strobes, clock override, and miscellaneous analog TX tuning.
- Lane 1 digital ASIC interface: `DPCSSYS_CR2_LANE1_DIG_ASIC_*` repeats the lane 0 TX-side pattern and adds a larger RX-side surface in this range: RX request/pstate/rate/width, reset, CDR/VCO load values, adaptation enable/continuous adaptation, termination, low-power detect, RX valid, EQ override inputs, RX CDR/VCO ASIC inputs, OCLA, RX output readback, and cross-lane shift handshake fields.
- Lane 1 TX/RX power and VCO calibration: `LANE1_DIG_TX_PWRCTL_*` mirrors lane 0 TX pstate, power-up, and DCC controls. `LANE1_DIG_RX_PWRCTL_*` defines RX pstate recipes and RX power-up timing. `LANE1_DIG_RX_VCOCAL_*` covers RX VCO calibration fixed count/gain/bounce controls, reset/continuous-calibration overrides, DPLL calibration update gain, frequency tune start/step/skip controls, startup/update/counter timing, and the first RX VCO analog status register.

Most masks in this range are 16-bit-style values carried in 32-bit C literals ending in `L`, matching the DPCS CR register payload style used by these generated headers.

## Control Flow

This header has no local runtime control flow. The effective control flow is created by AMDGPU display code that includes this header with its companion offset header and uses register helpers to pack or unpack fields.

A typical consumer path is:

1. DCN 3.1 resource code includes `dpcs/dpcs_4_2_0_offset.h` and this `dpcs/dpcs_4_2_0_sh_mask.h` header.
2. Register-list and shift/mask-list macros token-paste generated register and field names into ASIC-specific tables.
3. Link encoder, PHY, hardware sequencer, clock, AUX/link-training, panel, or debug code calls helper macros such as register read, write, get, set, or update operations through those tables.
4. Hardware state machines, not this header, perform MPLL power sequencing, RTUNE calibration, lane pstate transitions, DCC updates, RX VCO calibration, RX adaptation, statistic counting, and ACK/status latching.

The field names imply sequencing dependencies: override value fields generally need paired override-enable bits, pstate recipes are selected by higher-level lane state changes, timing fields are interpreted by hardware counters, ACK/status fields are polled by driver code, and clear/mask/status fields require hardware-specific access semantics outside this generated file.

## State And Persistence Behavior

The file stores no software state and persists nothing itself. It names hardware-visible state in DPCS CR2 supervisor, lane 0, and lane 1 registers:

- Common clock/PLL state: MPLLA/MPLLB power override, feedback/PCLK/output enables, lock state, calibration state, DAC range/output, lock and stable timers, gearswing/preset timers, PCLK enable/disable/powerdown timers, spread-spectrum type override, bandgap/reference power timing, and analog PLL control bits.
- Tuning/calibration state: RTUNE request/force/calibration counters, RX/TX up/down set and status values, TX calibration code, MPLL calibration override, VCO calibration fixed-count and frequency-tune parameters, VCO calibration timing, and analog VCO readback signals.
- Lane TX state: pstate recipes for P0/P0S/P1/P2, analog/digital enables, refgen and clock enables, reset and serial-enable controls, data-enable and receive-detect allowance, DCC compensation policy, DCC DAC request/update/bin-hot/ACK, clock alignment, LBERT control, TX termination, equalization, DCC DAC, and miscellaneous analog tuning.
- Lane RX state: lane 1 RX request, reset, pstate, rate, width, termination, CDR/VCO load values, adaptation enable/continuous adaptation controls, EQ override values, RX valid/readback status, RX pstate recipes, RX power-up timers, and VCO status fields.
- Diagnostic and test state: analog test bus and alternate bus fields, OCLA selectors, RX statistic match/mask/sample/counter controls, calibration comparison clocking, loopback BERT control, DCC DAC diagnostics, directed TX coefficient/status readbacks, and cross-lane shift synchronization signals.

Persistence is hardware-defined. Configuration fields can remain until a modeset, link retraining pass, PHY/lane reset, power-gate transition, suspend/resume reinitialization, firmware action, or GPU reset rewrites them. Status, ACK, calibration, statistic, and diagnostic fields may be latched, sampled, clear-on-write, self-clearing, or only valid while the relevant clock and power domains are active. This generated header does not encode those semantics.

## Dependencies And Integration Points

This chunk is tightly coupled to the rest of the DPCS 4.2.0 generated register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_CR2_*` register offsets, including the same MPLL power-control groups at offsets such as `0x0061` onward and lane 1 RX VCO calibration groups around `0x1148` onward.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both the DPCS 4.2.0 offset and shift/mask headers when building DCN 3.1 resource definitions.
- AMD display `reg_helper.h`-style access macros and generated register tables consume these names indirectly; most runtime code will not mention every raw field name directly.
- Link encoder, PHY, clock-source, hardware sequencing, link-training, suspend/resume, and diagnostic paths depend on these masks to program lane power, clocking, PLL selection, MPLL calibration, RTUNE, DCC, RX VCO calibration, RX adaptation, and low-level lane status.
- Firmware and hardware state machines share ownership of some surfaces, especially override, calibration, clock-ready, request/ACK, cross-lane shift, OCLA/debug, and status fields. The header only describes bit layout, not ownership policy.

The constants are ASIC-version-specific. Nearby DPCS generations may have similarly named fields, but mixing this `dpcs_4_2_0_sh_mask.h` slice with another generation's offset table or hardware database can compile while programming the wrong register layout.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift or mask compiles cleanly but can write the wrong DPCS bit, corrupt reserved fields, or decode status incorrectly.
- Chunk boundaries are artificial. This slice starts after one `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3` shift and ends before `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_1`; whole-file research must reconcile adjacent chunks before treating those groups as complete.
- Repeated MPLLA/MPLLB and lane 0/lane 1 layouts are copy-sensitive. A generator error can affect one PLL bank, one lane, or one status register while nearby repeated groups appear correct.
- Override and normal ASIC-input fields often coexist. Writing a value without the matching override-enable bit may be ignored; leaving override bits set after diagnostics can bypass normal hardware sequencing.
- Power, clock, PLL, DCC, RTUNE, and VCO fields are sequencing-sensitive. Bad masks can produce blank displays, unstable link clocks, stuck resets, failed link training, RX adaptation failures, suspend/resume-only regressions, or high error rates.
- Status, ACK, clear, and mask fields can have side effects or transient validity. Confusing request, ACK, status, clear, and mask bits can cause missed events, stuck waits, repeated interrupts, or misleading diagnostics.
- Reserved fields are emitted as masks. Driver code should preserve reserved bits during read-modify-write unless the hardware specification explicitly requires a value.
- Timing fields are narrow packed bitfields. Consumers must mask or validate values before shifting so out-of-range values do not spill into adjacent controls.
- Analog/test/debug fields are not harmless metadata: ATB, alt-bus, termination, equalization, DCC, Vref, PMIX, RTUNE, and PLL controls can alter PHY electrical behavior or obscure useful debug evidence.

## Test Signals

Useful validation is a mix of generated-header checks and hardware behavior:

- Build AMDGPU display support for the DCN generation that includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`; missing, duplicate, or renamed macros should fail table initialization or preprocessor expansion.
- Mechanically verify that complete fields in this range have matching `__SHIFT` and `_MASK` definitions, allowing the expected boundary exception for `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3__meas_iv_bias`.
- Cross-check every complete `DPCSSYS_CR2_*` register group in this chunk against `dpcs_4_2_0_offset.h` and AMD's authoritative DPCS 4.2.0 register database.
- Diff repeated lane 0/lane 1 and MPLLA/MPLLB groups where the hardware spec expects identical layouts, while preserving intentional RX-only differences in the lane 1 section.
- Exercise DisplayPort and HDMI link bring-up, retraining, hotplug, stream disable/enable, high-bandwidth modes, and suspend/resume on hardware using DPCS 4.2.0. Watch for blank screens, clock lock failures, lane ACK timeout, RX adaptation failure, retraining loops, or DCC/VCO calibration failures.
- Inspect register dumps or PHY traces around MPLL lock/state, PCLK/output enable, RTUNE status, TX/RX pstate, DCC DAC ACK, RX statistic counters, RX VCO calibration status, lane clock-ready/data-enable, detect-RX, and cross-lane shift handshakes.
- Run diagnostics that use OCLA, LBERT, RX statistic match/count controls, analog test bus/readback, DCC DAC override, termination/equalization override, and RX VCO calibration readback to confirm masks decode expected bits.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`, including the `meas_iv_bias__SHIFT` line just before this range. This chunk covers the remainder of CR2 supervisor MPLLB/common control, lane 0 digital/analog TX and RX statistic surfaces, and the start of lane 1 digital TX/RX power and VCO calibration surfaces. The next chunk should continue with `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_1` and later lane 1 RX calibration/status definitions. The final per-file merge should treat this as one generated ASIC register map, not handwritten driver logic.

### subset-b-002308: lines 47686-50047

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 47686-50047

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for low-level display PHY lane registers. It contains preprocessor constants only; there is no executable C logic, no types, no storage, and no direct MMIO access in this range.

The line window covers 2,138 `#define` entries: 1,071 `__SHIFT` constants and 1,067 `_MASK` constants. It starts inside the lane 1 RX VCO calibration status area, covers the rest of the visible lane 1 digital RX, analog override, analog TX, and analog RX register-field metadata, then begins the lane 2 register-field metadata through the first masks of `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6`. The boundaries are artificial chunk boundaries: the previous chunk owns the beginning of lane 1 RX VCO calibration definitions, and the next chunk owns the remaining lane 2 adaptation masks and later lane 2 fields.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or includes in this range. The public contract is the generated register-field macro naming pattern:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field inside the register.

Major register families covered in this chunk:

- `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_*`: lane 1 RX VCO calibration status and control fields visible at the chunk start, including RX VCO FSM state, frequency/calibration resets, continuous calibration enable, calibration done, DPLL frequency reset, final VCO counter, too-fast/correct/up status, and related reserved ranges.
- `DPCSSYS_CR2_LANE1_DIG_RX_RX_ALIGN_XAUI_COMM_MASK` and `...LBERT_*`: receive alignment comma masking plus link BERT mode, sync, error count, and overflow status.
- `DPCSSYS_CR2_LANE1_DIG_RX_CDR_*`: lane 1 clock-data-recovery controls for phase detector enable/edge/polarity, PR mode, realign behavior, diagnostic bus selection, spread-spectrum on/off counters, DPLL gain override, phase/frequency update gains, CDR status, DPLL frequency, and upper/lower frequency bounds.
- `DPCSSYS_CR2_LANE1_DIG_RX_ADPTCTL_*`: lane 1 receiver adaptation configuration and status. This includes adaptation timing, start, clock division, CTLE pole override, TGG patterns, CTLE/VGA/ATT/DFE/eye/TGG enables, thresholds, adaptation step sizes, saturation thresholds, initial error levels, reset bits, ATT/VGA/CTLE/DFE status fields, DFE VDAC offsets, slicer controls, error slicer levels, DAC control mux selection, and CR-bank address/data access.
- `DPCSSYS_CR2_LANE1_DIG_RX_STAT_*`: lane 1 receive statistics and match/counter controls, including load values, data masks, match values, counter enable/invert/clear/edge/continuous mode fields, sample count, six statistic counters, calibration compare clock control, additional match controls, stat control extensions, and stop control.
- `DPCSSYS_CR2_LANE1_DIG_MPHY_RX_*`: MPHY receive PWM control, low-speed termination control, and analog PWM clock stable-count fields.
- `DPCSSYS_CR2_LANE1_DIG_ANA_*`: digital-side analog override outputs for TX, RX, VCO, calibration, DAC, AFE, slicer, IQ phase/sense, signal-change enables, analog status, MPHY overrides, signal-detect overrides, DCC DAC overrides, TX override measurement, TX power, alternate/test bus controls, TX DCC/termination/misc/reserved registers, RX clock/CDR/slicer/power/squelch/calibration/test-bus/reserved registers.
- `DPCSSYS_CR2_LANE2_DIG_ASIC_*`: start of lane 2 digital ASIC-facing lane/TX/RX override input/output and normal ASIC input/output fields, including RX equalization and CDR/VCO ASIC inputs, OCLA, and extra TX/RX override outputs.
- `DPCSSYS_CR2_LANE2_DIG_TX_PWRCTL_*`: lane 2 TX power-state programming, P0/P0S/P1/P2 state fields, TX power-up timers, DCC CR-bank address/data, DCC DAC control/range/selection/ack/address fields.
- `DPCSSYS_CR2_LANE2_DIG_TX_CLK_ALIGN_TX_CTL_0` and `...TX_LBERT_CTL`: lane 2 TX clock alignment and TX-side BERT mode/sync controls.
- `DPCSSYS_CR2_LANE2_DIG_RX_PWRCTL_*`: lane 2 RX power-state fields and RX power-up timing controls.
- `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_*`: lane 2 RX VCO calibration control, timing, and status fields, mirroring the lane 1 VCO calibration layout.
- `DPCSSYS_CR2_LANE2_DIG_RX_*` through `ADPTCTL_ADPT_CFG_6`: beginning of lane 2 receive alignment, LBERT, CDR, DPLL, and receiver adaptation config fields. The chunk stops after the `CTLE_MU` and `VGA_MU` masks for `ADPT_CFG_6`, so the complete register belongs partly to the next chunk.

## Control Flow

This header has no runtime control flow. Its role is compile-time register metadata:

1. `dcn31_resource.c` includes `dpcs_4_2_0_offset.h` and this matching `dpcs_4_2_0_sh_mask.h` for DCN 3.1 display resource construction.
2. Resource and link-encoder tables use macro expansion, for example `DPCS_DCN31_REG_LIST`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)`, to pair generated offsets with generated field positions and masks.
3. Runtime display code uses the resulting register tables through helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and related AMD display register helpers.
4. Hardware sequencing for VCO calibration, TX/RX power-state changes, CDR tuning, receiver adaptation, DFE/CTLE/VGA programming, statistics capture, and analog override access is implemented by driver or firmware code outside this generated header.

The constants in this chunk therefore enable control flow elsewhere but do not encode ordering, timing, read/write permissions, write-one-to-clear behavior, polling loops, or power/clock dependencies themselves.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names bitfields for hardware-visible state in CR2 lane registers:

- Lane 1 and lane 2 RX VCO calibration state, including FSM state, reset controls, calibration completion, VCO counter results, and too-fast/correct/up indications.
- CDR and DPLL configuration/status, including phase-detector behavior, spread-spectrum counters, update gains, DPLL frequency values, and frequency bounds.
- Receiver adaptation state for CTLE, VGA, attenuator, DFE taps, eye-height/eye-horizontal controls, TGG patterns, thresholds, step sizes, saturation behavior, reset controls, and live adaptation status/readback.
- RX statistics state for match masks/values, counter control, sample counts, statistic counters, and stop/clock controls.
- Analog lane override state for TX and RX power, equalization, termination, DAC, VCO, slicer, IQ, squelch, calibration, test bus, DCC, and signal-detect controls.
- Lane 2 TX/RX power-state programming and power-up timing state.

Actual persistence and side effects are hardware-defined. Some fields are configuration bits that remain until reset, power gating, suspend/resume, modeset reprogramming, or firmware intervention. Status and counter fields may be read-only, latched, self-clearing, write-one-to-clear, or meaningful only when the corresponding DPCS lane, PHY clocks, and power domains are active. This generated slice does not describe those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with the AMD DPCS 4.2.0 register database and companion generated offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` provides the matching register addresses/base indices for the field names in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes the 4.2.0 DPCS offset and shift/mask headers and builds DCN 3.1 link-encoder and DPCS register tables from them.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and related link-encoder code show the integration style for RDPCSTX/DPCS register arrays and shift/mask table population, even though this specific slice is CR2 lane-level metadata rather than the common RDPCSTX control fields.
- AMD display register helpers in `reg_helper.h` consume the shift/mask values indirectly through generated tables; a wrong mask can compile successfully but route MMIO updates to the wrong bit range.
- Neighboring chunks for the same file are required for whole-register and whole-lane interpretation. This chunk starts after part of lane 1 VCO calibration was already defined and ends before all lane 2 `ADPT_CFG_6` masks are present.

Behaviorally, these fields sit below connector/link policy code. They describe per-lane PHY calibration, receiver adaptation, analog test/override, power-state, and diagnostic controls that influence display link bring-up, training, signal integrity, power transitions, and debug capture.

## Risks And Edge Cases

- These constants are untyped preprocessor macros. A wrong shift or mask can build cleanly and only fail as a runtime hardware programming bug.
- The header is generated. Manual edits risk divergence from silicon register definitions, the matching offset header, firmware assumptions, and debug tooling.
- Chunk boundaries split semantic registers. `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_1` begins before this chunk, and `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6` continues after it; per-file synthesis must reconcile adjacent chunks before asserting complete register coverage.
- Lane repetition is copy-sensitive. Lane 1 and lane 2 definitions should be structurally aligned where the hardware lanes are symmetric; a generator drift can create port-, lane-, or link-width-specific failures.
- VCO, CDR, DPLL, and adaptation fields are sequencing-sensitive. Incorrect masks can cause calibration-done polling failures, unstable clock recovery, bad equalization, link-training failures, or marginal behavior that depends on rate, cable, sink, voltage, and temperature.
- Analog override and test-bus fields are dangerous if treated as ordinary controls. They can bypass normal firmware/hardware behavior, alter termination/equalization/power, or expose debug buses whose semantics may differ by stepping.
- Counter and status fields can have non-obvious clear/latch behavior. Using the correct bit location is necessary but not sufficient; runtime code must still follow hardware access rules outside this header.
- Reserved fields are present throughout the range. Software should not infer that reserved masks are safe to program just because they are generated.
- The file uses `L`-suffixed 16-bit-style masks inside 32-bit C constants. Consumers must preserve unsigned-width expectations used by AMD's register helpers.

## Test Signals

Useful validation is mostly generated-header consistency plus runtime display PHY behavior:

- Build AMDGPU display support for the DCN 3.1 configuration that includes `dcn31_resource.c`. Missing or renamed macros should surface as compile failures in the generated register table setup.
- Mechanically compare this line range against the authoritative DPCS 4.2.0 register-field database and confirm each complete field has the expected `__SHIFT`/`_MASK` pair, allowing for the known split at the chunk start and end.
- Cross-check all registers represented here against `dpcs_4_2_0_offset.h`, especially CR2 lane 1 and lane 2 offsets for VCOCAL, CDR, ADPTCTL, STAT, MPHY, ANA, ASIC, TX_PWRCTL, and RX_PWRCTL blocks.
- Run repetition checks between lane 1 and lane 2 for mirrored register families. Expected intentional differences should be limited to lane numbering and chunk-boundary incompleteness.
- Exercise DisplayPort and HDMI/PHY link bring-up across lane counts and link rates. Watch for calibration timeouts, CDR instability, link-training retries, lane-specific failures, and intermittent high-rate signal-integrity problems.
- Test power transitions, suspend/resume, hotplug link retraining, and modesets while monitoring TX/RX power-state and calibration status behavior.
- Use hardware register dumps or debug tooling to verify DPCS CR2 lane fields after link training and after power-state changes, comparing against firmware/hardware reference values.
- Exercise diagnostics that read RX statistics or use analog/test-bus controls only on supported platforms, checking for counter aliasing, stuck counters, and incorrect match masks.

## Cross-Chunk Notes

The previous chunk owns the beginning of lane 1 RX VCO calibration definitions, including fields immediately before `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_1`. This chunk then covers the rest of lane 1 receive, adaptation, statistics, and analog override metadata and starts lane 2 from ASIC override and TX/RX power/calibration metadata. The next chunk must finish `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6` and continue lane 2 adaptation/status definitions before a final per-file report can make whole-lane or whole-file claims.

### subset-b-002309: lines 50048-52421

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 50048-52421

## Scope

This chunk covers lines 50048-52421 of the generated AMD DPCS 4.2.0 shift/mask header. The range contains 2,132 `#define` constants across 243 register blocks: 1,065 `__SHIFT` macros and 1,067 `_MASK` macros. The two extra masks are expected for this sliced chunk because line 50048 starts in the middle of `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6`, where four `_MASK` definitions are present while their matching shifts were defined before the chunk boundary.

The content is declarative register metadata only. It defines bit positions and masks for DPCS CR2 lane 2, CR2 lane 3, and CR2 raw common registers. It contains no C functions, structs, enums, local storage, runtime branching, or software-owned persistence.

## Purpose

This header fragment provides symbolic bitfield definitions for AMDGPU display driver code that programs the DPCS 4.2.0 display PHY. Consumer code pairs these field macros with companion register-offset definitions and AMD display register helpers to build read-modify-write values without hard-coding literal bit positions.

The chunk is centered on three hardware surfaces:

- `DPCSSYS_CR2_LANE2_*`: lane 2 receive adaptation, RX statistics, MPHY/RX termination controls, digital analog override outputs, and lane 2 analog TX/RX control/status fields.
- `DPCSSYS_CR2_LANE3_*`: lane 3 ASIC-facing override/normal signal registers, TX power-control P-state and DCC controls, RX statistics, digital analog TX override/status fields, and analog TX controls.
- `DPCSSYS_CR2_RAWCMN_*`: CR2 common PHY reset, MPLLA/MPLLB override and spread-spectrum controls, common mode/RTUNE/HDMI/TX PWM clock overrides, MPLL state controls, calibration/status IDs, OCLA selection, support analog overrides, and always-on RTUNE readback values.

## Exported API Surface

There are no callable APIs or user-defined types. The public interface is the macro namespace itself. Each register field generally has:

- `REGISTER__FIELD__SHIFT`: starting bit for extracting or composing a field value.
- `REGISTER__FIELD_MASK`: bit mask for isolating the field in the corresponding memory-mapped register.

Important macro families in this range include:

- `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_*`: lane 2 RX adaptation configuration, reset, and status for ATT, VGA, CTLE boost/pole, DFE taps 1-5, DFE data/error VDAC offsets, even/odd slicer controls, error slicer level, adaptation reset, DAC control selection, and CR bank address/data windows.
- `DPCSSYS_CR2_LANE2_DIG_RX_STAT_*` and `DPCSSYS_CR2_LANE3_DIG_RX_STAT_*`: repeated RX statistics match/mask/control/counter blocks. These define pattern masks, pattern data, scope delay, symbol selectors, mask inversion, counter enables, saturation behavior, load values, sample counts, and statistic stop controls.
- `DPCSSYS_CR2_LANE2_DIG_ANA_*` and `DPCSSYS_CR2_LANE3_DIG_ANA_*`: digital-to-analog override/status surfaces for TX/RX controls, term-code overrides, EQ override outputs, RX VCO and power overrides, MPHY controls, signal-detect overrides, TX DCC DAC overrides, and analog status readbacks.
- `DPCSSYS_CR2_LANE2_ANA_TX_*`, `DPCSSYS_CR2_LANE2_ANA_RX_*`, and `DPCSSYS_CR2_LANE3_ANA_TX_*`: direct analog field maps for TX measurement, power override, alternate-bus controls, ATB measurement paths, DCC DAC/control, term code, override clocks, miscellaneous TX settings, and lane 2 RX clock/CDR/slicer/power/squelch/calibration/ATB/reserved fields.
- `DPCSSYS_CR2_LANE3_DIG_ASIC_*`: lane 3 ASIC-facing request/acknowledge, P-state, rate, width, MPLLB select, data-enable, main/pre/post cursor, HDMI mode, clock-ready, detect-RX, invert, low-power-detect, reset, loopback, AC JTAG, async-data, and override-enable fields.
- `DPCSSYS_CR2_LANE3_DIG_TX_PWRCTL_*`: lane 3 TX power-state programming for P0/P0S/P1/P2, TX power-up timing registers, DCC CR bank address/data, DCC DAC control/range/selection/ack/address, and TX clock alignment/LBERT controls.
- `DPCSSYS_CR2_RAWCMN_DIG_*`: common reset, MPLLA/MPLLB clock divider/bandwidth/SSC/frac-N overrides, lane FSM extension, initial calibration disable, RTUNE request override, HDMI mode override, TX PWM clock selection/enables, MPLL state/bank selection, TX calibration code, SRAM init done, OCLA probe selection, support analog overrides, PCS/FW ID code fields, and indexed AON common RTUNE RX/TXDN/TXUP readback fields.

## Register Areas Covered

The lane 2 RX adaptation block exposes the lower-level equalization and signal-sampling knobs that the display PHY uses during receive calibration. It covers VGA saturation thresholds/levels, DFE mu settings, initial error values, per-adaptation resets, live adaptation status codes, DFE tap status, even/odd data and error VDAC offsets, slicer controls, and adaptation reset. These fields are not algorithms by themselves; they are the bit contracts used by training, diagnostic, or low-level bring-up code to observe and influence the RX adaptation hardware.

The lane 2 and lane 3 RX statistic blocks provide programmable hardware counters and matchers. Register groups define data masks, pattern masks, pattern values, match control words, counter control, sample count, statistic counters 0-6, calibration comparison clock control, extra match controls, statistic control extensions, and stop bits. These are likely used for PHY diagnostics, calibration verification, and link-quality measurement rather than normal per-frame display traffic.

The lane 2 digital analog and analog RX/TX groups bridge digital control words to analog PHY behavior. They include TX/RX override output enables, transmitter term-code and EQ override controls, RX power/VCO/AFE/CTLE/scope/slicer/phase adjustment controls, analog status readback fields, MPHY override outputs, signal-detect overrides, TX DCC DAC overrides, direct analog TX power/ATB/DCC/term/misc controls, and direct lane 2 analog RX clock/CDR/slicer/power/squelch/calibration/ATB controls.

The lane 3 ASIC block describes the interface between higher-level ASIC link logic and the lane 3 PHY. It exposes both override input registers and normal ASIC input/output mirrors. The field pairs show a common pattern: value fields such as `REQ`, `PSTATE`, `RATE`, `WIDTH`, `DATA_EN`, `CLK_RDY`, `INVERT`, and `RESET` have adjacent `*_OVRD_EN` fields that gate whether the override value replaces the normal ASIC signal.

The lane 3 TX power-control block maps several power states and timing controls. P-state fields cover analog refgen, VCM hold, analog clock enable, power-down, high-Z, termination enable, DCC enable, output enable, serializer enable, divider controls, low-power DCC values, and reserved bits. Timing and DCC windows define power-up delays, DCC CR bank address/data access, DAC control/range/selection/ack/address, TX clock alignment, and LBERT controls.

The raw common block applies across the CR2 PHY rather than a single lane. It defines global PHY functional reset, MPLLA/MPLLB divider and bandwidth overrides, spread-spectrum and frac-N overrides, lane FSM extension, common override controls for MPLL initial calibration, RTUNE request, HDMI mode, TX PWM clock selection/enables, MPLL on/off state and bank selection, TX calibration code, SRAM init status, OCLA clock/probe selection, support analog overrides, firmware/PCS ID readbacks, and the beginning of indexed always-on RTUNE RX/TXDN/TXUP values.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior is created by driver code that uses these macros to access hardware registers.

The field names imply several hardware state machines and handshakes:

- RX adaptation sequencing: reset bits, status codes, `ASM1_DONE`/`ASM1_DON` flags, ATT/VGA/CTLE/DFE status fields, slicer levels, and VDAC offsets expose calibration progress and final tuned values.
- Statistics collection: load/start fields, sample counts, match masks/patterns, counter enables, saturation flags, stop controls, and statistic counters define a hardware measurement pipeline that must be configured, started, sampled, and stopped in a defined order by consumers.
- Lane request/ack and power state transitions: lane 3 `REQ`, `ACK`, `PSTATE`, `RATE`, `WIDTH`, `CLK_RDY`, `DATA_EN`, `DETECT_RX_REQ`, `DETRX_RESULT`, reset, disable, and power-state fields model PHY bring-up, link training, idle, and power-down transitions.
- Override gating: many fields have paired `*_OVRD_VAL`/`*_OVRD_EN` or value/`*_OVRD_EN` definitions. Software must enable override bits deliberately and usually restore hardware-owned control afterward.
- PLL/common clock control: MPLLA/MPLLB divider, bandwidth, SSC, frac-N, state, bank, and calibration-disable fields affect common clock generation shared by lanes.
- Analog measurement and calibration: ATB, DCC DAC, term code, RTUNE, VCO, support analog, OCLA, and TX calibration fields expose diagnostic and calibration state across analog and mixed-signal blocks.

No software persistence is implemented in this header. Hardware register contents persist or reset according to ASIC power, reset, and clock domains. Fields named `STATUS`, `ACK`, `DONE`, `VALID`, `ID_CODE`, `SRAM_INIT_DONE`, `RTUNE_*_VAL`, and statistic counters are readback/status-oriented; fields named `OVRD`, `RESET`, `PSTATE`, `DAC`, `TERM`, `DCC`, and `*_EN` are control-oriented. This distinction is semantic and must be enforced by consumer code and hardware documentation, not by the macros themselves.

## Dependencies And Integration Points

The only direct syntactic dependency is the C preprocessor. These definitions are meant to be included alongside DPCS 4.2.0 offset/address headers that provide the actual register locations. AMDGPU display code then uses common register helper macros to shift, mask, set, clear, or read the fields.

Integration points visible from naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DPCS link encoder, PHY, clock, link-training, and diagnostics code.
- Companion generated headers such as `dpcs_4_2_0_offset.h` or equivalent register-address maps for the same DPCS generation.
- DisplayPort and HDMI link paths, reflected by `RATE`, `WIDTH`, `PSTATE`, `HDMIMODE`, cursor/pre/post EQ, DETRX, data-enable, term-code, and MPLL fields.
- PHY diagnostics and validation paths that configure RX statistics, LBERT, OCLA, ATB, scope, slicer, DCC DAC, and RTUNE readbacks.
- Firmware or hardware-control paths that may own some lanes or common PLL state unless software explicitly enables override bits.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently write an adjacent hardware bit during a read-modify-write sequence, causing display link failures that may not be caught by compile tests.
- The chunk begins mid-register with masks for `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6`; naive per-chunk validators must account for the missing shifts being outside this range.
- Many lane 2 and lane 3 blocks are structurally similar but not identical. Copy-generation mistakes in lane prefixes, field widths, or mask values can affect only one lane and escape broad smoke tests.
- Override-enable fields are adjacent to override values. Accidentally setting an enable bit can seize a signal from normal hardware/firmware control; failing to set one can make a value write ineffective.
- Status/readback fields and writable control fields are intermixed. Consumers must not infer access direction from mask presence alone.
- Common MPLLA/MPLLB, RTUNE, reset, and HDMI/TX PWM clock fields can have cross-lane effects. A write intended for one lane's link mode can destabilize another lane if shared-resource ownership is misunderstood.
- Reserved fields have explicit masks throughout the chunk. Consumer code should preserve reserved bits unless the hardware specification explicitly requires a value.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Preprocess or compile AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Run generated-register consistency checks against the authoritative DPCS 4.2.0 register database and companion offset header.
- Verify this exact chunk has 1,065 shift macros and 1,067 mask macros, with the imbalance explained by the partial `ADPT_CFG_6` boundary.
- Check that every complete register block in the range has matching shift and mask entries for each field, including repeated `LANE2`, `LANE3`, `MPLLA`, `MPLLB`, and indexed RTUNE families.
- Compare compatible fields against nearby generated variants such as `dpcs_4_2_2_sh_mask.h` or `dpcs_4_2_3_sh_mask.h` where the hardware register database expects stable layouts.
- Runtime display tests on DPCS 4.2.0 ASICs: DP and HDMI link training, rate/width changes, suspend/resume, hotplug, lane power transitions, and multi-lane operation that exercises lane 2 and lane 3 independently.
- PHY diagnostic tests that read back RX adaptation status, DFE tap values, RX statistic counters, DETRX result, TX ack, SRAM init done, MPLL state, firmware ID, RTUNE values, and OCLA/ATB/DCC paths.
- Negative or recovery tests around override fields: enable an override only under controlled debug/bring-up code, restore normal ownership, and confirm no stale override remains across link reconfiguration.

## Chunk Notes For Merge

This document intentionally covers only lines 50048-52421 of `dpcs_4_2_0_sh_mask.h`. The later per-file merge should describe the full header as a generated DPCS 4.2.0 register bitfield map, not handwritten driver logic. Adjacent chunks are needed to cover the earlier part of lane 2 and the remaining raw common RTUNE fields after `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_RTUNE_TXDN_VAL_6`.

### subset-b-002310: lines 52422-54799

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 52422-54799

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header segment for the `DPCSSYS_CR2` register block. It covers 2,378 lines and defines 1,057 `__SHIFT` macros plus 1,095 `_MASK` macros. The unequal count is expected for this sliced range: it begins in the middle of common RTUNE definitions, so some masks or shifts for adjacent fields live outside the chunk boundary.

The content is declarative only. It contains no functions, structs, enums, runtime variables, loops, branches, or persistence logic. Its public surface is the set of C preprocessor constants that describe bit positions and masks for 16-bit DPCS internal registers.

## Purpose

The header gives AMDGPU display code symbolic access to DPCS 4.2.0 hardware register fields. Consumer code combines these constants with addresses from `dpcs_4_2_0_offset.h` and register helper macros to perform read-modify-write operations without hard-coding bit numbers.

This chunk specifically covers:

- The tail of common always-on RTUNE values for common RX/TX termination calibration.
- Common SRAM bring-up, power-gating, reset, supply, reference-range, VREF, and resonance override/status controls.
- Full lane 0 and lane 1 register-field maps for PCS crossbar (`PCS_XF`), lane FSM, IRQ control, PMA crossbar (`PMA_XF`), TX control, RX control, and ATE/test override windows.
- The beginning of lane 2 TX PCS/override field definitions through `DPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_TX_PCS_IN`.

## Exported API Surface

There are no callable APIs or local types. The exported interface is the generated macro namespace, where each register field has a `__SHIFT` constant and a `_MASK` constant.

Important macro families in this range:

- `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_RTUNE_*`: common RTUNE readback/value fields for RX, TXDN, and TXUP termination calibration slots 6 and 7.
- `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_SRAM_BL_CFG`: SRAM boot/load controls such as power-gate boot-load enable, ROM selection, bypass, and start.
- `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_PG_OVRD_*`, `SUP_OVRD_IN`, `RES_OVRD_IN`, and `RES_ASIC_IN_OUT`: common-domain power, reset, reference clock, MPLL force/ack, and request/ack override plumbing.
- `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_VREF_STATS`, `REF_RANGE_OVRD`, and `MISC_CONF_IN_1`: VREF calibration status, reference range override, and MPLL powerdown timing.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_PCS_XF_*`: lane-local PCS TX/RX request, reset, rate, width, pstate, low-power detect, MPLL selection, data enable, loopback, adaptation, equalization, phase calibration, termination, and ATE override fields.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_FSM_*`: lane FSM override/status, fast calibration/adaptation state monitor fields, common calibration status, flags, CR lock, TX DCC status, OCLA monitor controls, TX EQ update flag, and RX IQ phase offset.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_IRQ_CTL_*`: per-lane IRQ status, clear, mask, and reset-return request fields for RX reset/request/rate/pstate/adaptation, phase-2 calibration, loopback, DCC on-demand, TX reset, and TX request events.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_PMA_XF_*`: PMA-facing lane, supply, TX, RX, MPHY, RTUNE, and adaptation override/status fields.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_TX_CTL_*` and `RX_CTL_*`: lane-local TX/RX controller knobs and status, including TX FSM control, TX clock control, DCC continuous status, RX FSM control, RX LOS mask control, RX data-enable override, OFFCAN/adaptation continuous status, and UPCS/OCLA observability.
- `DPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_TX_*`: start of the lane 2 PCS TX override/input surface, continuing the same repeated lane pattern in later lines.

## Register Areas Covered

The common AON section exposes cross-lane support state: RTUNE calibration values, SRAM boot/load sequencing, PMA/PCS power stable overrides, power-gate reset/mode overrides, monitor input and analog isolation overrides, MPLLA/MPLLB force and acknowledgement overrides, reference clock enable override, VREF calibration done state, request/ack override routing, reference range override, and MPLL powerdown timing.

The lane 0 and lane 1 PCS crossbar sections are structurally parallel. TX fields cover reset, request, power state, low-power detect, data width/rate, MPLLB selection, MPLL enable, master MPLL state, DETRX request, VBOOST, IBOOST, beacon enable, serial loopback, TX data enable, TX async enable/data, acknowledgement, DETRX result, EN_CTL, and TX DWORD clock sync override. RX fields cover rate/width/pstate/LPD override, AFE/DFE adaptation enables, parallel loopback, RX data enable, LOS/LFPS and threshold overrides, adaptation/off-cancellation continuous mode, VCO/reference load overrides, RX PCS inputs, valid/ack outputs, adaptation acknowledgement, figure-of-merit, directed TX pre/main/post EQ values, lane number, RX EQ delta IQ, termination controls, RX EQ override controls, and phase-2 calibration request/ack.

The FSM sections encode diagnostics and state-machine observability rather than direct high-level software logic. They expose FSM override control, memory address and status monitors, fast RX startup/adaptation/calibration state bits, continuous calibration/adaptation state bits, common MPLL/RCAL status, RX VCO/ref/IQ calibration progression, generic flags, CR lock state, TX DCC flags/status, OCLA capture controls, TX EQ update flag, and RX IQ phase offset.

The IRQ sections define a consistent event model for each lane. Individual event registers and matching clear registers exist for RX reset, RX request, RX rate, RX pstate, RX adaptation request/disable, RX phase-2 calibration request/disable, lane loopback enable, TX reset, TX request, and lane transceiver mode. `IRQ_MASK` and `IRQ_MASK_2` fields gate those events, including DCC on-demand and TX reset/request mask bits.

The PMA and TX/RX controller sections bridge the digital PCS lane controls into analog/PHY-side status and override points. They include lane pstate/ack controls, supply power stable/enable fields, TX ack/data enable/DCC done flags, RX data/valid/adaptation done flags, RTUNE control, MPHY reference clock/DCC/reset/PLL calibration/sleep/termination fields, RX adaptation output override, TX FSM and clock controls, RX LOS and data-enable override controls, and OCLA/UPCS observability.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior is determined by the driver code that writes fields selected by these masks and by hardware state machines in the DPCS block.

The field names imply several hardware sequences:

- Common-domain bring-up: SRAM boot/load, PMA/PCS power stable indications, power-gate reset/mode, reference clock enable, MPLL force/ack, VREF calibration done, reference range, and MPLL powerdown timing are inputs to link initialization and low-power transitions.
- Per-lane TX/RX activation: TX/RX reset and request bits pair with acknowledgement/status fields; rate, width, pstate, LPD, MPLL select, MPLL enable, and data-enable fields describe the configured link state for each lane.
- Calibration and adaptation: RTUNE, RX AFE/DFE adaptation, OFFCAN continuous mode, VCO/ref load overrides, phase-2 calibration, TX DCC, IQ phase offset, FOM, and directed TX EQ fields expose calibration commands and readbacks.
- Interrupt lifecycle: event bits, clear bits, and mask bits describe a status-clear-mask pattern that consumers must handle with the correct register access semantics.
- Test and debug access: ATE override, OCLA, UPCS_OCLA, FSM memory/status monitor, and MPHY override windows allow manufacturing, validation, or deep debug code to force or observe low-level PHY behavior.

No software state is persisted here. Hardware register contents persist or reset according to ASIC power domains, resets, and firmware/hardware sequencing. Reserved fields are explicitly named in the macros and should be preserved by consumers during read-modify-write operations.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is the DPCS 4.2.0 register database that generated this file and its companion `dpcs_4_2_0_offset.h` address map.

Within this source tree, `dpcs_4_2_0_sh_mask.h` is included by `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` together with `dpcs_4_2_0_offset.h`. That ties this generated register contract to the DCN 3.1 resource implementation for Yellow Carp-class display hardware. The matching offset range maps the common registers around `0x203c`-`0x2040`, lane 0 around `0x3000`-`0x30c8`, lane 1 around `0x3100` and later, and lane 2 starting at the next repeated lane window.

Integration points visible from the names include AMD DC link encoder and PHY programming, DisplayPort/HDMI link training, per-lane PMA/PCS control, DPCS interrupt handling, suspend/resume and power-gating flows, firmware or manufacturing ATE paths, and debug/diagnostic paths that inspect FSM, OCLA, calibration, and IRQ state.

## Risks

- Generated-header drift is the main risk. A wrong bit shift or mask can silently change adjacent hardware fields during register updates.
- The lane 0 and lane 1 blocks are highly repetitive. A copy-generation error in only one lane can create asymmetric display-link failures that are hard to reproduce.
- This chunk starts and ends inside larger logical register groups. Merge/reconciliation must avoid assuming the partial RTUNE and lane 2 groups are complete in this chunk alone.
- Many registers mix override enable bits with override value bits. Setting a value bit without its enable bit, or leaving an enable bit asserted after debug/test use, can force hardware away from normal state-machine control.
- IRQ status, clear, and mask fields share very similar names. Consumer code must respect write-one-to-clear or mask polarity semantics from the hardware spec; the mask header alone does not encode those access rules.
- Reserved masks cover large bit ranges. Drivers should preserve reserved bits and avoid treating full-width or reserved fields as safe scratch space.
- Debug/ATE/OCLA/MPHY override fields can interfere with normal link training, power management, and calibration if used outside controlled bring-up or diagnostics.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile/preprocess AMDGPU DCN 3.1 code that includes `dpcs_4_2_0_sh_mask.h` through `dcn31_resource.c`.
- Static checks that every complete register group has matching `__SHIFT` and `_MASK` definitions; for this sliced chunk, expect 1,057 shifts and 1,095 masks because the line range crosses group boundaries.
- Consistency checks against `dpcs_4_2_0_offset.h` so every register-family prefix in this chunk has a corresponding `ix...` address define.
- Generated-register comparison against adjacent DPCS versions (`dpcs_4_2_2`, `dpcs_4_2_3`, or `dcn_4_1_0` copies) to catch accidental field-width or mask-format changes.
- Runtime display tests on hardware using DPCS 4.2.0: DP and HDMI link training, lane-count/rate changes, hotplug, suspend/resume, low-power entry/exit, RX/TX calibration, DCC/adaptation flows, loopback/debug paths if available, and IRQ clear/mask handling.
- Register readback during bring-up should show expected transitions for power stable, SRAM load, reset/request acknowledgements, VREF calibration done, adaptation acknowledgements, phase-2 calibration request/ack, TX DCC status, FSM flags, and IRQ status/clear behavior.

## Chunk Notes For Merge

This document intentionally covers only lines 52422-54799 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should cover the preceding common AON RTUNE fields, and later chunks should continue lane 2 and subsequent register blocks. The final merged per-file report should describe the whole file as a generated ASIC bitfield map for DPCS 4.2.0 rather than handwritten driver logic, with `dcn31_resource.c` and the matching offset header as the primary in-tree integration anchors.

### subset-b-002311: lines 54800-57195

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 54800-57195

## Scope

This chunk is part of the generated AMD DPCS 4.2.0 register shift/mask header. It contains 2,100 `#define` entries for bit positions and bit masks, covering the end of `DPCSSYS_CR2_RAWLANE2`, the full matching `DPCSSYS_CR2_RAWLANE3` digital lane block, and the beginning of `DPCSSYS_CR2_RAWAONLANE0`. The file is declarative: it exports preprocessor constants only and has no C functions, structs, runtime branches, allocation, or persistent software data.

## Purpose

The constants describe 16-bit register fields used by AMD display PHY/DPCS programming code for lane-level DisplayPort/PHY control. Each register field has a `__SHIFT` constant for positioning and a `_MASK` constant for read-modify-write operations. The chunk is mostly lane-scoped control and status metadata:

- `RAWLANE2` tail: PCS/PMA crossbar override inputs and outputs, RX/TX request/ack fields, ATE overrides, FSM monitor and fast-calibration fields, IRQ status/clear/mask fields, lane TX/RX controller flags, OCLA debug hooks, and late PCS TX override bits.
- `RAWLANE3`: the same PCS, FSM, IRQ, PMA, TX_CTL, RX_CTL, and ATE register groups repeated for lane 3.
- `RAWAONLANE0` start: always-on lane calibration/readback definitions for AFE/DFE offsets, adapted equalizer values, phase adjustment, MPLL coarse tune and disable, power-up done status, calibration fast flags, common calibration status, and TX/RX disable overrides.

## Important API Surface

The exported API is the macro namespace. Important families in this chunk include:

- PCS TX/RX interface macros such as `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN__PSTATE_MASK`, `...__RATE_MASK`, `...__MPLL_EN_MASK`, `...__RESET_OVRD_EN_MASK`, `...__REQ_OVRD_EN_MASK`, and the corresponding RX fields for `ADAPT_AFE_EN`, `ADAPT_DFE_EN`, `RX_DATA_EN_OVRD_*`, CDR VCO/ref load values, EQ gains, and acknowledge bits.
- ATE and loopback/test macros such as `DPCSSYS_CR2_RAWLANE{2,3}_DIG_PCS_XF_ATE_OVRD_IN`, `ATE_RX_OVRD_IN*`, `ATE_TX_OVRD_IN*`, `MASTER_MPLL_LOOP`, serial loopback enable overrides, TX data/asynchronous data overrides, and RX EQ delta IQ controls.
- FSM/fast-calibration macros such as `DPCSSYS_CR2_RAWLANE{2,3}_DIG_FSM_FAST_RX_STARTUP_CAL`, `FAST_RX_ADAPT`, `FAST_RX_AFE_CAL`, `FAST_RX_DFE_CAL`, `FAST_RX_CONT_*`, `FAST_FLAGS`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `CMNCAL_MPLL_STATUS`, `CMNCAL_RCAL_STATUS`, `CR_LOCK`, and `OCLA`.
- Interrupt macros for per-lane RX/TX request, reset, rate, pstate, adaptation, phase-2 calibration, lane mode, loopback, and DCC-on-demand events, including individual IRQ status bits, clear bits, and `IRQ_MASK` / `IRQ_MASK_2` fields.
- PMA interface macros for lane/supervisor override routing, TX/RX PMA fields, MPHY fields, RTUNE controls, and RX adaptation override values.
- `RAWAONLANE0` calibration/status macros for AFE and DFE IDAC/VDAC offsets, even/odd ref levels, adapted ATT/VGA/CTLE/DFE tap values, RX slicer controls, `FAST_FLAGS`, `FAST_FLAGS_2`, MPLL coarse tune/disable, common calibration done/init status, and generic `ADPT_CTL_0` through `ADPT_CTL_7` full-word fields.

The paired offset definitions live in `dpcs_4_2_0_offset.h`; this header supplies only bit layout. Consumers normally combine an `ix...` offset macro with a `...__FIELD_MASK` and `...__FIELD__SHIFT` macro through AMD display register helper code.

## Control Flow

There is no executable control flow in this chunk. The implied hardware flow is encoded by register naming:

1. Software selects a lane and register offset from the DPCS offset header.
2. It reads or writes hardware register words through AMD display register helpers.
3. Field values are shifted by `__SHIFT` and masked by `_MASK`.
4. Override enable bits, request bits, reset bits, and IRQ clear bits affect hardware state machines in the PCS/PMA/lane-controller blocks.
5. Status and acknowledge fields report the hardware result, for example request `ACK`, RX adaptation acknowledge/FOM, calibration done bits, CR lock, TX DCC status, and OCLA monitor fields.

For `RAWLANE2` and `RAWLANE3`, the chunk preserves a regular repeated lane layout, which lets higher-level code use lane-indexed offset tables while the field definitions stay lane-specific. The `RAWAONLANE0` section is not a repeat of the raw lane PCS block; it starts the always-on calibration/status register set that can be shared by or adjacent to PHY lane bring-up logic.

## State And Persistence

The header itself has no software state and persists nothing. Its constants address hardware-backed state:

- Override registers can force TX/RX power, reset, request, rate, width, pstate, MPLL selection, PLL state, data enable, loopback, PMA signal-detect, and calibration paths.
- Status registers expose transient PHY state, including acknowledgements, signal/adaptation figure-of-merit, calibration phases, common calibration completion, clock/data recovery indicators, and debug monitor values.
- IRQ clear masks are write-sensitive hardware controls; using a wrong mask can clear the wrong event or fail to clear an asserted one.
- Reserved masks document unused or reserved bit ranges. Callers should preserve these bits on read-modify-write unless the hardware programming guide explicitly says otherwise.

Any durable effect comes from writes to the display PHY registers during link setup, training, test mode, power management, or recovery, not from this header.

## Dependencies And Integration Points

This header depends only on C preprocessing and its include guard. In this tree, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`, wiring these constants into the DCN 3.1 resource implementation alongside DCN, NBIO, and MMHUB register headers.

Integration points are expected to include AMD display register helper macros from `reg_helper.h` and resource/link encoder initialization code that builds register tables. The constants are ASIC-version-specific: DPCS 4.2.0 bit layouts must remain synchronized with the matching offset header and the generated DCN/DPCS register tables used for Yellow Carp/DCN31-era display resources.

## Risks

- Bit drift between `dpcs_4_2_0_offset.h`, this shift/mask header, and silicon documentation can silently misprogram PHY registers.
- The lane 2 and lane 3 blocks are highly repetitive; copy-generation mistakes can leave one lane with a shifted mask or a missing override that is hard to spot in review.
- Many controls are low-level PHY override or calibration knobs. Incorrect writes can break link training, leave lanes stuck in reset, disable data, mask interrupts, bypass required calibrations, or force test/ATE behavior in normal operation.
- Reserved masks are numerous in this range. Code that writes full register literals instead of read-modify-write field updates risks changing reserved bits.
- `RAWAONLANE0` contains always-on calibration and MPLL controls; errors here can affect broader PHY bring-up behavior beyond a single high-level display connector flow.

## Test Signals

Useful validation signals are compile-time and hardware-facing:

- Kernel/display build coverage should include `dcn31_resource.c` so these macro names compile with the matching offset header and register helper usage.
- Static checks can verify each register field has coherent shift/mask pairs and that masks do not overlap except for documented reserved ranges.
- Generated-header regression checks should compare lane 2 and lane 3 repeated register groups for expected structural equivalence while allowing lane-number-specific prefixes.
- Hardware or emulator tests should exercise DisplayPort link bring-up, link retraining, power state changes, lane reset/request handshakes, RX adaptation, DCC/RTUNE calibration, interrupt clear/mask handling, and debug/OCLA monitor reads.
- Failure signatures include link training timeouts, missing RX/TX request acknowledgements, stuck calibration-done bits, unexpected IRQ storms or lost IRQs, and lane-specific failures that reproduce only on raw lane 2 or raw lane 3.

### subset-b-002312: lines 57196-59640

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 57196-59640

## Scope And Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.0 shift/mask header. It contains C preprocessor constants for hardware register bitfield packing and extraction, not executable code. The range belongs to the `DPCSSYS_CR2` register namespace and describes the always-on lane (`RAWAONLANE`) digital register fields for CR2 plus the start of the CR2 supervisor/common (`SUPX`) digital PLL and reference-clock fields.

The chunk starts in the tail of `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_LOS_MASK_CTL`, completes the remainder of lane 0's always-on RX/signal-detect block, repeats a full always-on register layout for lanes 1, 2, 3, and the lane-template-like `LANEX` namespace, then enters the common `DPCSSYS_CR2_SUPX_DIG_*` definitions. It provides 2,073 `#define` lines under 372 register-comment headings. The naming pattern is the generated public contract: each bitfield has a `__SHIFT` macro giving the low bit and a matching `_MASK` macro giving the encoded field mask.

## Register Groups Covered

- `DPCSSYS_CR2_RAWAONLANE0_DIG_*` tail: the range begins after the first two `RX_LOS_MASK_CTL` shift macros, so only the `RX_LOS_MASK_CNT_MASK` and reserved mask for that register are present in this chunk. It then covers lane 0 signal-detect filtering, statistics, RX PMA override outputs, RX signal-detect calibration/code fields, VREF generator enable, current/VREF calibration codes, RX DCC calibration code captures, TX DCC bank access, MPLL bandgap state delay control, signal-detect output override/input observation, firmware configuration words, lane transceiver-mode override/input, RX signal-detect filter counters, and TX DCC configuration.
- `DPCSSYS_CR2_RAWAONLANE1_DIG_*`, `RAWAONLANE2`, and `RAWAONLANE3`: each lane has a full repeated always-on set beginning with analog/RX adaptation telemetry and offsets, then DFE and slicer values, MPLLA/MPLLB coarse tuning, power-up-done status, adaptation outputs for ATT/VGA/CTLE/DFE taps, fast flag status banks, common calibration status, TX/RX disable overrides, loss-of-signal and signal-detect controls, RX PMA override outputs, signal-detect calibration, DCC calibration, firmware configuration, lane transceiver-mode fields, and TX DCC configuration.
- `DPCSSYS_CR2_RAWAONLANEX_DIG_*`: mirrors the same lane-local always-on layout using an `X` lane namespace. This usually acts as a generated generic or broadcast/template form alongside explicit lane numbers; consumers still need the matching address definitions to know whether this maps to an actual indirect lane selector, broadcast alias, or generated documentation alias.
- `DPCSSYS_CR2_SUPX_DIG_*` start: covers supervisor ID code low/high words, reference clock override fields, MPLLA/MPLLB divided clock and HDMI clock override fields, MPLLA main override words, MPLLA multiplier, MPLLA spread-spectrum enable/update controls, and the first MPLLA SSC peak word. The next chunk continues the SUPX PLL, ASIC-input, and analog supervisor register family.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this chunk. The interface is the macro namespace consumed by AMDGPU register programming code:

- `DPCSSYS_CR2_RAWAONLANE<n>_DIG_<REG>__<FIELD>__SHIFT` gives the field's starting bit.
- `DPCSSYS_CR2_RAWAONLANE<n>_DIG_<REG>__<FIELD>_MASK` gives the mask for that field.
- `DPCSSYS_CR2_RAWAONLANEX_DIG_*` repeats the same shape for the generated lane-X alias/template.
- `DPCSSYS_CR2_SUPX_DIG_*` covers common CR2 supervisor fields shared by lanes, especially reference clock and MPLL control.
- `RESERVED_*` fields preserve the hardware register layout and must normally be left unchanged by read-modify-write code.

The header is intended to be used with the matching DPCS 4.2.0 register address header and AMDGPU display register access helpers. In typical usage, higher-level display/PHY code prepares a value by masking and shifting field values, writes it through an MMIO or indirect DPCS access path, or reads a register and decodes status with the corresponding mask and shift.

## Control Flow

This header has no runtime control flow. The implied hardware sequencing is visible in the field families:

- Override fields pair `*_OVRD_VAL` data with `*_OVRD_EN` enable bits. For RX PMA square wave/signal detect, VREF, termination, lane transceiver mode, TX/RX disable, and SUPX clock/PLL controls, the value field alone is not enough; software must intentionally assert the enable bit to take control away from normal hardware/ASIC signals.
- Status and observation fields such as `RX_VREFGEN_MASTER`, `RX_PMA_SQ_OUT`, `PH2_PWRUP_DONE`, `ADAPT_DONE`, `FAST_FLAGS`, `LANE_CMNCAL_*_STATUS`, and `SIGDET_OUT_IN` are intended for polling or diagnostics after hardware training, power sequencing, or calibration has been triggered elsewhere.
- Calibration code fields expose hardware-produced or firmware-provided values for signal detect, VREF/current generation, RX DCC I/Q common-mode and data-filter codes, and MPLL coarse tune. These are data surfaces for training/bring-up code, not algorithms themselves.
- The SUPX fields establish common reference-clock and PLL behavior before per-lane transmit/receive operation depends on those clocks. The chunk includes override controls for reference clock enable/source/range, bandgap, HDMI mode, divided clocks, HDMI clock dividers, MPLLA enable/divider/multiplier/fractional-N/spread-spectrum fields, and the first spread-spectrum peak register.

Because the range is generated and repetitive, lane identity is part of the control contract. A lane 2 mask may have the same numeric value as a lane 3 mask, but code should still use the macro matching the register address being accessed so static review and generated-address coupling remain correct.

## State And Persistence Behavior

The file itself persists no runtime state. It contributes compile-time constants. State affected by consumers is hardware register state in the CR2 display PHY/DPCS block:

- Lane-local RX adaptation and calibration state includes ATT/VGA/CTLE/DFE tap values, DFE even/odd data/error/bypass offsets, IQ phase adjustment, slicer controls, common calibration status, RX signal-detect thresholds/codes, LOS mask counters, and DCC calibration code fields.
- Lane control state includes TX/RX disable override bits, RX PMA square-wave/signal-detect/VREF/termination override fields, lane transceiver mode override, and TX DCC bank/configuration controls.
- Firmware-facing state appears in `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG`, which expose 16-bit configuration or split adaptation/calibration fields for microcode or firmware-mediated PHY procedures.
- SUPX common state includes reference clock selection and range, bandgap enable, HDMI mode, MPLLA/MPLLB divided and HDMI clock overrides, MPLLA enable/standby/divider/multiplier/fractional-N/spread-spectrum controls, and SSC peak data.

Persistence is governed by hardware, not this header. Programmed register values can survive across portions of a mode-set, link training attempt, hotplug handling path, or suspend/resume sequence until overwritten, reset, or power-gated. Status fields may be transient or latched depending on the hardware register definition outside this header.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DPCS 4.2.0 register set:

- Matching register address definitions are required; this `_sh_mask` header only describes bit positions and masks.
- AMDGPU display code supplies the register read/write helpers, field packing helpers, locking, sequencing, polling, and timeout behavior.
- Link training and PHY bring-up code integrates with the lane always-on registers for RX adaptation results, DFE/CTLE/VGA state, signal detect, LOS masking, DCC calibration, lane mode selection, and TX/RX disable control.
- Power management and reset paths depend on the `INIT_PWRUP_DONE`, common calibration status, MPLL disable/state-delay, and SUPX reference-clock/PLL fields.
- Firmware or diagnostics paths may use the `FW_*` config registers, `FAST_FLAGS`, DCC bank address/data/control registers, signal-detect override/input registers, and ID code registers.
- The file is generated from ASIC register specifications. Manual edits risk diverging from the DPCS 4.2.0 hardware layout and should be validated against the generator/spec source.

Although this repository path starts with `sources/distributed-fs/ceph-client`, the file itself is an imported Linux AMDGPU display header. It has no direct Ceph filesystem integration.

## Risks And Edge Cases

- The chunk starts mid-register and ends mid-SUPX family. `RAWAONLANE0_DIG_RX_LOS_MASK_CTL` is incomplete at the beginning, and `DPCSSYS_CR2_SUPX_DIG_MPLLA_SSC_PEAK_1` is followed by more SUPX PLL fields in the next chunk. Merge-stage documentation should reconcile those boundaries.
- Reserved masks are emitted as named constants. Driver code should preserve reserved bits unless the hardware specification requires a particular write value.
- Override fields are easy to misuse. Leaving `*_OVRD_EN` asserted after debug or validation can pin RX termination, signal detect, TX/RX disable, PLL clocking, or lane mode away from normal hardware control.
- The repeated lane layout invites copy/paste mistakes. Numeric masks are often identical across `RAWAONLANE1`, `2`, `3`, and `X`, but the macro prefix must match the addressed register.
- Many fields are narrow but safety-critical. Unmasked values can spill into adjacent fields if callers shift raw values without applying `_MASK`; this is especially risky for thresholds, filter counters, DCC calibration codes, MPLL multipliers/dividers, fractional-N controls, and SSC fields.
- Status fields can be stale or timing-dependent. Polling `ADAPT_DONE`, calibration status, `PH2_PWRUP_DONE`, signal-detect inputs, or fast flags needs timeouts and reset/clear sequencing outside this header.
- The `LANEX` namespace requires caution. Without the matching address-map context, it should not be assumed to be interchangeable with a numbered lane address.

## Test Signals

Useful validation for this chunk is mostly compile-time, generated-header, and hardware-oriented:

- Build AMDGPU display translation units that include `dpcs_4_2_0_sh_mask.h` to catch macro spelling, duplicate definition, and include-guard issues.
- Generator consistency checks should verify every non-reserved field has matching `__SHIFT` and `_MASK` definitions, masks are contiguous where expected, and mask positions agree with shift/width metadata.
- Cross-lane checks should compare `RAWAONLANE1`, `RAWAONLANE2`, `RAWAONLANE3`, and `RAWAONLANEX` for expected repeated layouts while allowing lane-number namespace differences.
- Static checks around field packing should confirm caller values are masked before shifting and read-modify-write paths preserve reserved bits.
- Hardware regression coverage should include CR2 display link bring-up, hotplug, DisplayPort/HDMI training, high-bandwidth modes, suspend/resume, lane reset/retrain paths, and PLL/reference-clock transitions.
- Diagnostic validation should exercise RX signal-detect filtering and overrides, LOS mask timing, DCC bank access, RX DCC calibration code reads, adaptation/fast-flag observation, firmware config fields, and SUPX MPLLA/MPLLB override behavior.
- Runtime warning signals include blank displays after mode-set, link training failures, unstable high-rate links, repeated PHY retraining, stuck adaptation/calibration polling, incorrect signal-detect/LOS reporting, and HDMI/DP clocking problems after changes to these generated masks.

### subset-b-002313: lines 59641-62003

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 59641-62003

## Scope

This chunk covers `dpcs_4_2_0_sh_mask.h` lines 59641-62003, a generated AMD DPCS 4.2.0 register shift/mask header fragment. The range is entirely preprocessor metadata: `#define` constants for register field bit shifts and masks, grouped under `//DPCSSYS_CR2_*` register comments. It contains 223 register-comment groups and about 2,140 macro definitions, split roughly evenly between `__SHIFT` and `_MASK` constants. There are no C functions, structs, enums, storage objects, or executable control flow in this slice.

## Purpose

The fragment supplies symbolic bitfield definitions for Display Core PHY/SerDes programming in the AMDGPU DRM driver. Callers use the constants to pack or extract hardware register fields without hard-coding bit positions. The visible register groups describe two main hardware areas:

- `DPCSSYS_CR2_SUPX_*`: supervisor/global DisplayPort/HDMI PHY controls, including MPLLA/MPLLB PLL override inputs, PLL analog controls, power-control timers/status, spread-spectrum clocking, RTUNE, bandgap/reference power-up, and analog override outputs.
- `DPCSSYS_CR2_LANEX_*`: per-lane PHY controls and status, including lane ASIC override/input/output fields, TX and RX power states and timing, TX DCC DAC access, TX clock alignment and LBERT, RX VCO calibration, RX CDR/DPLL, and RX adaptation/equalization status.

The header is normally paired with address-definition headers for the same ASIC block. Address macros identify a register; this file's `__SHIFT` and `_MASK` macros define how to encode individual fields within that register.

## Important APIs, Types, and Macros

There are no callable APIs or data types. The exported interface is a large set of C preprocessor constants whose naming convention is the contract:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for `FIELD`.
- `REGISTER__FIELD_MASK` gives the masked field value in register position.
- Register comments such as `//DPCSSYS_CR2_SUPX_DIG_MPLLB_OVRD_IN_0` separate field groups and match the prefix used by the following macros.

Key macro families in this chunk:

- MPLLA/MPLLB digital override and SSC fields: `DPCSSYS_CR2_SUPX_DIG_MPLLA_*` and `DPCSSYS_CR2_SUPX_DIG_MPLLB_*` define enable, divider, multiplier, standby, calibration, fractional-N quotient/remainder/denominator, charge-pump, gear-shift, spread-spectrum peak/step-size, and clock-output fields. The B-side family mirrors the A-side family for dual PLL resources.
- Supervisor digital fields: `DPCSSYS_CR2_SUPX_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `ASIC_IN`, `LVL_ASIC_IN`, and `BANDGAP_ASIC_IN` describe prescaler, RTUNE request/acknowledge, bandgap, reference clock, voltage boost/reference, and ASIC-facing global control/status.
- Analog supervisor fields: `DPCSSYS_CR2_SUPX_ANA_*` includes prescaler, RTUNE, bandgap, ATB measurement, MPLLA/MPLLB analog override, miscellaneous PLL controls, PLL control registers, and reserved/vendor-specific knobs.
- MPLL power-control fields: `DPCSSYS_CR2_SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR2_SUPX_DIG_MPLLB_MPLL_PWR_CTL_*` expose state-machine override, status, timers, calibration, DAC range, analog DAC output, and SSC spread-type fields.
- Analog override outputs: `DPCSSYS_CR2_SUPX_DIG_ANA_MPLLA_OVRD_OUT_*`, `MPLLB_OVRD_OUT_*`, `ANA_RTUNE_OVRD_OUT`, `ANA_BG_OVRD_OUT`, and `ANA_MPLL{A,B}_PMIX_OVRD_OUT` define fields that drive or override analog enable/reset/calibration, charge pump, PMIX, RTUNE, bandgap, and reference regulator behavior.
- Lane ASIC override/input/output fields: `DPCSSYS_CR2_LANEX_DIG_ASIC_*` defines per-lane TX/RX requests, rate, width, pstate, data enable, loopback, inversion, reset, CDR/SSC/alignment, equalizer controls, RX/TX acknowledge/status, and ASIC-facing input/output mirrors.
- TX lane power and diagnostics: `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_*`, `TX_CLK_ALIGN_TX_CTL_0`, and `TX_LBERT_CTL` define TX P-state enable/reset/data/RX-detect bits, power-up timing fields, DCC CR-bank/DAC access fields, FIFO bypass/2UI shift controls, and LBERT pattern/error-trigger controls.
- RX lane power, calibration, and adaptation: `DPCSSYS_CR2_LANEX_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, `RX_LBERT_*`, and `RX_ADPTCTL_*` define RX P-state power bits, power-up timing, VCO calibration controls/status, CDR coefficients/status, DPLL frequency bounds, adaptation configuration, reset, and CTLE/VGA/ATT/DFE tap status.

## Control Flow

This chunk has no runtime branch, loop, or call flow. Runtime behavior is created by other AMDGPU code that includes this header and performs read/modify/write operations, usually in a pattern equivalent to:

1. Read a DPCS register through the driver's MMIO/register-access helpers.
2. Clear a field with `~FIELD_MASK`.
3. Shift a desired value by `FIELD__SHIFT`.
4. Mask it with `FIELD_MASK`.
5. Write the updated register value back, or test a status field after masking and shifting.

Several register families imply hardware state-machine sequencing even though the header does not implement it. For example, `REQ`/`ACK`, `OVRD_EN`, `*_PSTATE_*`, `*_PWRUP_TIME_*`, `*_CAL_*`, `RTUNE_*`, and `ASM1_DONE` fields are intended to be used by link bring-up, power transition, PLL calibration, receiver adaptation, and diagnostics flows elsewhere in the driver.

## State and Persistence Behavior

The macros are compile-time constants and do not persist state. The state they name is hardware-resident:

- PLL state: MPLLA/MPLLB enable, reset, standby, fractional-N values, charge-pump settings, DAC/calibration outputs, and spread-spectrum parameters are latched in PHY registers.
- Supervisor/reference state: bandgap, prescaler, reference clock, RTUNE, and analog override controls affect common PHY resources shared across lanes.
- Per-lane TX/RX state: lane request, power state, rate, width, TX cursor values, RX CDR/VCO/adaptation settings, DCC DAC selection, and status bits live in per-lane DPCS registers.
- Diagnostic state: LBERT, OCLA, ATB measurement, DPLL frequency, and adaptation status fields expose transient hardware measurement or test state.

Persistence across suspend/resume, hotplug, link retraining, or GPU reset is not handled in this header. Any required save/restore or reprogramming must be implemented by the display/PHY code that consumes these constants.

## Dependencies

The fragment depends only on the C preprocessor and inclusion by driver source. Its semantic dependencies are external:

- Register address headers for DPCS 4.2.0 provide register offsets that pair with these field definitions.
- AMDGPU display code and DC/DM PHY programming paths provide register read/write helpers, link-rate policy, DP/HDMI mode selection, PLL programming formulas, and sequencing.
- Hardware documentation or generated register databases define the authoritative bit layouts. The repetitive shape and `_sh_mask.h` suffix indicate this file is generated rather than manually authored.

Because it is a header-only constant table, include order matters only insofar as consumers need both address macros and field macros visible before using them.

## Integration Points

Likely integration points are display link bring-up, PHY tuning, power management, and diagnostics inside the AMDGPU DRM driver:

- DP/HDMI clock programming code uses the MPLLA/MPLLB multiplier, fractional-N, divider, SSC, PMIX, and output-enable fields when selecting and enabling PHY clocks.
- Link training and mode-setting paths use per-lane TX/RX override, rate, width, cursor, CDR, VCO, and equalization/adaptation fields.
- Runtime power management and reset paths use `*_PSTATE_*`, `*_PWRUP_TIME_*`, `MPLL_PWR_CTL_*`, bandgap/reference power-up, and reset/standby fields.
- Debug, validation, and factory-test paths may use LBERT, OCLA, ATB, DCC DAC, RTUNE status, DPLL frequency, and adaptation-status masks.

The `LANEX` naming indicates the same macros are intended to be applied to lane-indexed register instances. Consumers must combine these field definitions with the correct lane-specific register address.

## Risks and Edge Cases

- Bitfield drift is high impact. If a shift or mask differs from the actual DPCS 4.2.0 hardware database, consumers can corrupt adjacent fields such as reset, override-enable, clock-enable, or calibration controls.
- Reserved fields are explicitly represented. Callers should preserve them in read/modify/write sequences unless hardware documentation says otherwise; writing mask-derived values blindly across a whole register can alter reserved bits.
- Many fields are paired with override-enable bits. Setting the data bit without the corresponding `*_OVRD_EN` bit may have no effect; setting override-enable without a coherent value can force the PHY into a bad link/power state.
- A-side and B-side PLL families are highly similar. Copy/paste errors between `MPLLA` and `MPLLB` consumers can select the wrong PLL or clock output.
- Per-lane `LANEX` fields must be used with the correct lane instance. Applying a lane mask to the wrong lane register can disturb another link lane or fail link training.
- Multiword fields are split across registers in several places, such as SSC peak/step-size and TX/RX timing values. Consumers must assemble high and low parts consistently.
- Status fields such as ACK, calibration done, VCO status, DPLL frequency, and adaptation done are transient hardware signals. Polling code must account for timeouts and reset/hotplug races.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Compile coverage: all include paths using DPCS 4.2.0 masks build without undefined macro references.
- Static consistency checks: every `__SHIFT` has a matching `_MASK` for the same register field, mask widths match the documented field width, and A/B PLL families remain symmetric where intended.
- Register write review: read/modify/write call sites preserve reserved bits and pair value fields with their override-enable bits.
- Hardware/link tests: DP and HDMI modes at multiple link rates train successfully, including lane-width changes, PLL A/B selection, SSC on/off, suspend/resume, hotplug, and GPU reset.
- Power tests: TX/RX P-state transitions, PLL power-up/down, bandgap/reference power sequencing, and RTUNE sequences complete without timeout.
- Diagnostic tests: LBERT/OCLA/ATB/DCC DAC paths can enable, report expected status, and return hardware to normal operation.

## Unresolved Cross-Chunk References

This range starts in the middle of the MPLLA SSC definitions; `DPCSSYS_CR2_SUPX_DIG_MPLLA_SSC_PEAK_1` begins before line 59641. It also ends in the middle of `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS`, with the remaining masks likely following after line 62003. The merged per-file report should reconcile this chunk with adjacent chunks to describe the complete DPCS 4.2.0 mask header and verify boundary register groups are complete.

### subset-b-002314: lines 62004-64392

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 62004-64392

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY register fields. It contains no executable C logic; its public surface is a dense set of preprocessor constants that encode bit positions (`__SHIFT`) and field masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,119 `#define` entries across 2,389 lines and describes 268 register groups. It starts in the middle of `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS`: lines 62004-62006 provide masks whose shift definitions are in the previous chunk. It then covers CR2 lane-X RX adaptation/status, RX statistic counters, MPHY controls, digital analog TX/RX override/status registers, raw analog TX/RX registers, raw memory placeholders, raw lane PCS/PMA/FSM/IRQ/TX/RX control registers, and ATE PCS override registers. Near the end it switches address blocks to `dpcssys_cr3_rdpcstxcrind` and begins CR3 supervisor/reference-clock/MPLLA/MPLLB override fields. The range ends inside `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`: only the first two masks are in this chunk, with the remaining masks in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The exported interface follows the generated register-field convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, compose, or update the field.

The main register-field families in this chunk are:

- CR2 RX adaptation status and controls: `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS` through `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_CR_BANK_DATA` expose DFE tap adaptation status, adaptation-done flags, even/odd DFE data and error VDAC offsets, slicer controls, error slicer levels, adaptation reset, DAC control selects, and CR bank address/data access.
- CR2 RX statistic collection: `DPCSSYS_CR2_LANEX_DIG_RX_STAT_*` defines sample load/start, data masks, pattern match controls, statistic/correlation source selectors, counter enables, clocking and pause controls, valid-loss clear/control, sample and statistic counters, calibration comparison clock control, extended match controls, statistic control, and stop behavior.
- CR2 MPHY and digital analog override/status surfaces: `DPCSSYS_CR2_LANEX_DIG_MPHY_RX_*`, `DIG_ANA_TX_*`, `DIG_ANA_RX_*`, `DIG_ANA_STATUS_*`, `DIG_ANA_MPHY_*`, `DIG_ANA_SIGDET_*`, and `DIG_ANA_TX_DCC_*` cover MPHY PWM and low-speed termination, TX analog enable/clock/reset/serial/data override outputs, TX termination and EQ override banks, RX CTLE/VCO/power/slicer/scope/DAC/calibration controls, signal-detect overrides, term-code clocks, DCC DAC overrides, and status bits such as PLL lock, receive detect, clock ACK, calibration outputs, and RX signal-detect state.
- CR2 raw analog lane registers: `DPCSSYS_CR2_LANEX_ANA_TX_*` and `DPCSSYS_CR2_LANEX_ANA_RX_*` describe analog TX power, measurement overrides, alternate/test buses, ATB controls, DCC DAC and control fields, termination code programming, override clocking, miscellaneous slew/vreg/peaking/reserved controls, RX clocks, CDR/deserializer, slicer controls, RX power, squelch, calibration, ATB measurement/reference selection, and reserved analog fields.
- CR2 raw memory and raw lane PCS transfer fields: `DPCSSYS_CR2_RAWMEM_DIG_ROM_CMN0_B0_R0`, `RAM_CMN0_B0_R0`, and `DPCSSYS_CR2_RAWLANEX_DIG_PCS_XF_*` describe raw ROM/RAM words plus PCS TX/RX override inputs, PCS inputs/outputs, RX adaptation controls and acknowledgements, figure-of-merit reporting, directed TX pre/main/post cursor feedback, lane number, ATE overrides, RX EQ delta/IQ controls, TX/RX termination control overrides, and PH2 calibration.
- CR2 raw lane FSM and fast-flow controls: `DPCSSYS_CR2_RAWLANEX_DIG_FSM_*` includes FSM override, memory/status monitors, fast RX startup/adapt/AFE/DFE/bypass/reference-level/IQ calibration controls, fast supervisor/TX common-mode/RX detect/RX power-up/VCO wait/VCO calibration controls, common MPLL and RCAL status, continuous adaptation/calibration flags, CR lock, TX DCC flags/status, TX EQ update flags, OCLA selection, and RX IQ phase offset.
- CR2 raw lane IRQ controls: `DPCSSYS_CR2_RAWLANEX_DIG_IRQ_CTL_*` defines RX/TX reset and request IRQ status, RX rate/pstate/adaptation IRQs, clear registers, IRQ masks, lane transceiver-mode interrupts, PH2 calibration request/disable IRQs, serial loopback IRQs, and DCC on-demand IRQ status.
- CR2 raw lane PMA, TX control, RX control, and ATE fields: `DPCSSYS_CR2_RAWLANEX_DIG_PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and late `PCS_XF_ATE_*` registers expose PMA lane and supervisor override signals, TX/RX PMA handshakes, lane RTUNE, MPHY override paths, RX adaptation override output, TX FSM and clock controls, DCC continuous status, TX/RX OCLA probes, RX FSM/rate-change controls, LOS mask timing, RX data-enable override timing, off-cancel and adaptation continuous status, and ATE RX/TX override banks for manufacturing or debug flows.
- CR3 supervisor and MPLL fields: after `// addressBlock: dpcssys_cr3_rdpcstxcrind`, the chunk defines CR3 supervisor ID code, reference-clock override, MPLLA/MPLLB divider and HDMI clock overrides, MPLLA/MPLLB main override inputs, multiplier controls, SSC controls, SSC peak/stepsize high and low words, fractional numerator/remainder/denominator words, charge-pump overrides, gain-scheduled charge-pump overrides, and the beginning of supervisor override input fields for prescaler, RTUNE, TX calibration, and alternate low-power reference-clock selection.

Most field masks are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these lane, raw-lane, raw-analog, supervisor, and MPLL blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. AMD display code for the matching DCN/DPCS generation includes the DPCS 4.2.0 offset header and this shift/mask header.
2. Register-list, shift-list, and mask-list setup code token-pastes generated register and field names into tables used by hardware sequencing, link encoder, PHY, AUX/link-training, clock-source, diagnostic, and interrupt paths.
3. Runtime driver code uses helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` against those tables.
4. The real sequencing for PLL programming, lane power, RX adaptation, RX statistic capture, DCC/RTUNE calibration, IRQ handling, PMA/PCS handshakes, test overrides, and debug readback lives outside this generated header.

The macros only describe bit layout. They do not encode access type, ordering constraints, reset values, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, clock-domain restrictions, or power-domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR2 lane-X and CR3 supervisor DPCS registers:

- RX adaptation state includes DFE tap status, adaptation done bits, slicer controls, even/odd data and error offsets, adaptation reset, DAC selection, CR bank address/data, CTLE/VGA/attenuation-adjacent status from the previous boundary, and RX calibration/scope/phase/signal-detect controls.
- RX statistic state includes loaded sample counts, pattern masks and matches, statistic/correlation source selectors, sample and statistic counters, done bits, counter enable bits, pause/clock controls, valid-loss handling, calibration-comparison clock controls, and stop controls.
- TX/RX analog lane state includes TX/RX power, clocks, reset, termination codes, EQ/peaking/slew/vreg controls, DCC DAC values, RX clock/CDR/deserializer/slicer settings, squelch and calibration values, ATB/test-bus selection, signal-detect status, PLL lock/readback, receive-detect readback, and reserved analog latches.
- Raw PCS/PMA state includes TX/RX pstate, rate, width, MPLL select/enable, reset/request/data-enable/loopback/beacon/async signals, RX adaptation request/disable/ACK/FOM, directed TX coefficient feedback, termination-control overrides, PH2 calibration, PMA supervisor and lane handshakes, lane RTUNE, MPHY PWM/termination, and RX adaptation override outputs.
- FSM and IRQ state includes lane state-machine override and monitor fields, fast-path calibration/adaptation enables and status, continuous adaptation/calibration flags, CR lock, TX DCC flags/status, TX EQ update flag, RX IQ phase offset, RX/TX reset/request/rate/pstate/adaptation/PH2/lane-mode/loopback/DCC IRQ status, clear, and mask fields.
- CR3 supervisor state includes ID-code readback, reference-clock override, MPLLA/MPLLB clock divider and HDMI divider override selection, PLL enable/divider/VCO/standby/calibration/fractional/clock-sync overrides, SSC enable and spread parameters, fractional PLL quotient/remainder/denominator words, charge-pump values, gain-scheduled charge-pump override enables, and the leading supervisor RTUNE/TX calibration/reference-clock override bits.

Persistence is hardware-defined. Configuration fields usually remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, IRQ, statistic, calibration, and handshake fields may be latched, sampled, clear-on-write, self-clearing, or valid only while the relevant lane/common clock and power domains are active. This generated header does not define those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_*` offsets. In the companion offset header, this chunk's CR2 groups map across offsets such as `0x9070` for `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS`, `0x9080` for `RX_STAT_LD_VAL_1`, `0x90a0` for digital analog TX overrides, `0x90e0` for raw analog TX, `0xe000` for raw lane PCS transfer registers, `0xe020` for raw lane FSM registers, `0xe040` for raw lane IRQ registers, `0xe060` for raw lane PMA transfer registers, and `0xe0c0` for ATE PCS override registers.
- The same offset header marks the transition to `addressBlock: dpcssys_cr3_rdpcstxcrind`, where CR3 supervisor registers begin at offsets `0x0000` through the MPLLA/MPLLB and supervisor override region covered here.
- AMD display DCN/DPCS resource code consumes these generated constants through version-specific register, shift, and mask tables rather than by open-coding bit values.
- Link training, PHY bring-up, clock-source programming, display mode set, hotplug, suspend/resume, diagnostics, and interrupt code interact with the hardware fields described here through the register helpers and generated tables.
- Firmware/hardware state machines also interact with the same fields, especially for RX adaptation, DCC calibration, RTUNE, PMA/PCS handshakes, fast calibration/adaptation flows, IRQ latching, and MPLL/SSC/fractional PLL setup.

Behaviorally, this range is below the user-facing display stack. It defines the bit layout used when the driver or firmware powers and configures CR2 lane-X PHY components, programs CR3 supervisor/MPLL state, handles raw lane PCS/PMA handshakes, clears or masks low-level lane interrupts, and reads or controls diagnostics.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. The first register in this range, `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS`, is split: its `__SHIFT` lines are immediately before line 62004. The last register, `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`, is also split: most of its masks follow line 64392.
- The range crosses an address-block boundary from CR2 lane/raw-lane fields into CR3 supervisor fields. Consumers must pair these macros with the correct offset block and register table; treating all names as one lane-local block would be wrong.
- RX adaptation and statistic fields are sequencing-sensitive. Incorrect masks around DFE taps, slicers, VDAC offsets, adaptation reset, pattern masks, sample counters, source selectors, valid-loss handling, or stop controls can cause link-training failures, poor equalization, misleading diagnostics, or stuck polling loops.
- Analog TX/RX fields can affect electrical behavior. Wrong masks for termination, EQ, DCC, VCO, CDR, slicer, power, signal-detect, ATB, or calibration fields may produce blank displays, unstable links, compliance failures, or debug traces that do not match hardware state.
- Raw PCS/PMA override and ATE fields can bypass normal state-machine behavior. Misprogramming reset/request/data-enable/loopback/MPLL/termination/RTUNE/PH2 fields can leave a lane in a state that higher-level display code cannot easily reason about.
- IRQ status, clear, and mask registers are easy to confuse because many field names repeat across status, clear, and mask groups. Wrong masks can drop events, leave stale status latched, or cause repeated interrupts.
- CR3 MPLLA/MPLLB fields control clocks. Bad masks for dividers, HDMI dividers, VCO frequency, SSC, fractional PLL words, charge-pump overrides, calibration force, standby, or clock-sync override can cause clock instability, link retraining loops, black screens, or mode-specific regressions.
- Repeated A/B PLL and TX/RX register patterns are copy-sensitive. A generator or merge error can affect only MPLLA, only MPLLB, only RX, only TX, or only a single lane while nearby fields look correct.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.0. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this range has the expected `__SHIFT` and `_MASK` pair, allowing the known boundary exceptions for `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS` at the start and `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN` at the end.
- Cross-check every complete register group in this chunk against `dpcs_4_2_0_offset.h`, including the CR2-to-CR3 address-block transition.
- Diff against AMD's source register database and nearby generated variants such as DPCS 3.1.4, 4.0.x, or DCN integrated shift/mask headers where hardware layout is expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, power states, and PHY lanes. Expected signals are stable link training, correct RX adaptation completion, correct MPLL selection, no stuck ACK/status bits, and no unexpected lane IRQs.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in adaptation, statistic, analog, PMA/PCS, IRQ, and CR3 supervisor/MPLL fields.
- Validate high-bandwidth and clock-sensitive modes that stress MPLLA/MPLLB divider, HDMI divider, SSC, fractional PLL, charge pump, reference-clock, and clock-sync controls. Watch for black screens, PHY lock failures, retraining loops, display corruption, audio/video timing instability, or rate-specific failures.
- Use register dumps or PHY debug traces during failing links to confirm DFE tap status, VDAC offsets, slicer levels, RX statistic counters, DCC status, VCO/CDR state, RTUNE handshakes, FSM status, IRQ clear/mask bits, and MPLL/SSC fields decode correctly.
- Exercise diagnostic paths where available: OCLA, RX statistic match/count controls, analog test bus/readback fields, directed TX coefficient feedback, PH2 calibration, loopback controls, ATE overrides, and MPHY low-speed controls.

## Cross-Chunk Notes

The previous chunk owns the `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS` shift definitions and earlier RX adaptation setup/status fields. This chunk begins with that register's masks, then covers a large CR2 lane-X/raw-lane section and the beginning of the CR3 supervisor/MPLL address block. The next chunk should finish `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN` masks and continue CR3 supervisor/prescaler/output/MPLL power-control fields. The final per-file research document should reconcile these boundaries before making whole-file claims about all DPCS 4.2.0 register groups.

### subset-b-002315: lines 64393-66750

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 64393-66750

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY/controller registers. It contains no executable C logic; its public surface is a set of preprocessor constants that encode bit positions (`__SHIFT`) and masks (`_MASK`) for individual fields in DPCS hardware registers.

The requested range contains 2,146 `#define` entries over 2,358 source lines. It starts in the middle of `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`, with the register's shift definitions immediately before the chunk and its masks at the top of this range. It then covers CR3 supervisor digital and analog PLL/bandgap/RTUNE controls, CR3 lane 0 ASIC/TX/RX power, statistics, analog TX and DCC fields, and the beginning of CR3 lane 1 ASIC override/input fields. It ends at `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2`, with `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_OUT` beginning just after the requested range.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the DPCS register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, compose, or update that field.

The main register-field families in this chunk are:

- CR3 supervisor override inputs and outputs: `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, and `LVL_OVRD_IN` describe prescaler overrides, RTUNE request/ACK overrides, TX calibration code override, reference alternate-clock low-power selection, MPLLA/MPLLB and bandgap state overrides, RX VREF controls, TX Vboost level, and supervisor RX VCO VREF selection.
- CR3 supervisor MPLLA/MPLLB ASIC inputs: `MPLLA_ASIC_IN_0-6` and `MPLLB_ASIC_IN_0-6` provide enable, div5 clock, TX clock divider, V2I, standby, VCO frequency, calibration force, fractional-N enable, multipliers, spread-spectrum enable/up-spread/peak/step-size, PMIX, word-div2, config-update, and clock-sync fields for both common PLL banks.
- Divided and HDMI clock inputs: `MPLLA_DIV_CLK_ASIC_IN`, `MPLLA_HDMI_CLK_ASIC_IN`, `MPLLB_DIV_CLK_ASIC_IN`, and `MPLLB_HDMI_CLK_ASIC_IN` describe divided-clock enable/multiplier and HDMI pixel/clock divider fields.
- Common supervisor digital/level/bandgap and charge-pump controls: `SUP_DIG_ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, `MPLLA_CP_ASIC_IN`, `MPLLA_CP_GS_ASIC_IN`, `MPLLB_CP_ASIC_IN`, and `MPLLB_CP_GS_ASIC_IN` cover VREF, TX Vboost, RX VCO VREF, bandgap enables, RTUNE calibration/current modes, isolated bandgap/reference controls, and PLL charge-pump proportional/integral settings.
- Supervisor analog controls: `SUP_ANA_PRESCALER_CTRL`, `RTUNE_CTRL`, `BG1/BG2/BG3`, `SWITCH_PWR_MEAS`, and paired `SUP_ANA_MPLLA_*`/`SUP_ANA_MPLLB_*` registers cover prescaler output clock enables, RTUNE range/mode/enable, bandgap voltage/current/offset selections, reference-clock selection, analog test bus selectors, PLL bias/current/CTUNE/loop-filter/lock/window/reserved fields, and PLL analog override surfaces.
- MPLL power, timing, calibration, and SSC controls: paired `SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `SUP_DIG_MPLLB_MPLL_PWR_CTL_*` registers define MPLL power/clock-calibration requests, lock and power-good status, DAC range, lock/sleep/reset/stable timers, calibration thresholds/timers, analog DAC readback, and SSC generator spread type.
- Supervisor clock/reset and RTUNE state: `CLK_RST_BG_PWRUP_TIME_*`, `CLK_RST_REF_PWRUP_TIME_0`, `CLK_RST_REF_VPHUD`, `RTUNE_CONFIG`, `RTUNE_STAT`, `RTUNE_*_SET_VAL`, `RTUNE_*_STAT`, `RTUNE_CONFIG_CNT*`, and `RTUNE_TX_CAL_CODE` encode bandgap/reference power-up timers, RTUNE request/ack/state/status, RX/TX up/down set values and measured status, counter thresholds, and TX calibration code.
- Digital-to-analog supervisor readback and override outputs: `ANA_MPLLA_OVRD_OUT_*`, `ANA_MPLLB_OVRD_OUT_*`, `ANA_RTUNE_OVRD_OUT`, `ANA_STAT`, `ANA_BG_OVRD_OUT`, and `ANA_MPLLA/MPLLB_PMIX_OVRD_OUT` expose PLL override outputs, RTUNE override outputs, PLL lock/status readbacks, bandgap override outputs, and PMIX override values.
- CR3 lane 0 ASIC lane/TX/RX interface fields: `LANE0_DIG_ASIC_*` includes lane loopback, TX/RX override inputs and outputs, reset, invert, data enable, request/ACK, low-power detect, pstate, rate, width, MPLLB select, receive-detect request/result, disable, beacon, main/pre/post cursor, async data/drive, Vreg driver bypass, RX adaptation/equalization values, RX ref/VCO load values, CDR/align/clock-shift, termination, and TX/RX ASIC input/output fields.
- CR3 lane 0 TX power and DCC controls: `LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0-5`, and `DCC_*` define per-power-state analog refgen, VCM hold, clock, word clock, reset, serial, digital clock, data enable, receive-detect, Vboost, DCC compensation, staged power-up timing, fast RX detect controls, and DCC CR/DAC address/data/control/range/select/ACK fields.
- CR3 lane 0 RX statistics and diagnostics: `LANE0_DIG_RX_STAT_*` describes RX load values, data masks, match controls, statistic count controls, sample count, statistic counters, calibration comparison clock controls, valid-loss controls, and statistic stop/done bits.
- CR3 lane 0 analog TX and DCC surfaces: `LANE0_DIG_ANA_TX_*` and `LANE0_ANA_TX_*` provide digital-to-analog override outputs, termination-code overrides, TX EQ override banks, DCC DAC override banks, analog status, measurement overrides, power overrides, alternate bus and ATB selectors, DCC DAC/control programming, termination-code programming/update/reset, clock override, TX miscellaneous controls, and reserved analog TX fields.
- CR3 lane 1 ASIC fields at the end of the chunk: `LANE1_DIG_ASIC_LANE_OVRD_IN`, `TX_OVRD_IN_0-4`, `TX_OVRD_OUT`, `RX_OVRD_IN_0-5`, `RX_OVRD_EQ_IN_*`, `RX_OVRD_OUT_0`, `LANE_ASIC_IN`, and `TX_ASIC_IN_0-2` mirror the lane-level loopback, TX/RX override, pstate/rate/width, request/ACK, receive-detect, async, equalization, termination, and TX cursor controls seen for lane 0. The following lane 1 TX output and RX ASIC input groups are outside this chunk.

Most values are 16-bit-style masks ending in `L`, matching the DPCS indirect-register field width used by these supervisor and lane blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN/DPCS display code includes the matching DPCS 4.2.0 offset header and this shift/mask header.
2. Register-list and shift/mask-list macros token-paste DPCS register and field names into tables for the ASIC generation that owns this register block.
3. Runtime AMD display code uses register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` with those offset, shift, and mask tables.
4. Hardware sequencing code outside this generated header performs the actual ordering for PLL programming, bandgap/reference startup, RTUNE, lane power-up/down, TX/RX handshakes, receive detect, RX adaptation, DCC calibration, diagnostics, and debug overrides.

The macros in this range describe bit layout only. They do not encode access type, reset value, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, latching, clock-domain crossings, or required sequencing.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 supervisor and lane registers:

- Common supervisor state: prescaler/DCO/reference-clock selection, alternate reference low-power selection, RTUNE request/ACK/status and set values, TX calibration code, RX VREF, TX Vboost, supervisor RX VCO VREF, bandgap state, reference power-up timing, and always-on tuning/status fields.
- PLL state: MPLLA/MPLLB enables, dividers, VCO frequency, standby, calibration force, fractional-N, multiplier, SSC peak/step-size/spread type, PMIX, word-div2, charge-pump proportional/integral values, DAC ranges/readbacks, power-good, lock, sleep, reset, stable timers, and analog override/readback fields.
- Lane 0 TX state: request/ACK, pstate, rate, width, MPLLB select, reset, invert, data enable, low-power detect, disable, receive-detect request/result, beacon, async drive/data, pre/main/post cursor values, Vreg bypass, per-pstate power enables, staged power-up timers, DCC compensation, DCC DAC programming, analog TX termination/equalization/clock/refgen/serial controls, and analog test bus selections.
- Lane 0 RX state: request/ACK, data enable, pstate, rate, width, low-power detect, inversion, reset, CDR tracking, CDR SSC, align, clock shift, termination mode, RX ref/VCO load values, adaptation AFE/DFE controls, equalization override values, async/squelch readbacks, and statistic match/mask/count/calibration controls.
- Lane 1 partial state: lane loopback, TX/RX override and ASIC input fields through `TX_ASIC_IN_2`, including request/data-enable/pstate/rate/width, reset/invert/disable, receive-detect, beacon, async, termination, adaptation, equalization, and TX pre/post cursor values.
- Diagnostic and manufacturing state: analog test bus fields, reserved analog hooks, RX statistic counters, DCC CR/DAC controls, PLL analog override outputs, bandgap and RTUNE override outputs, and lane loopback controls.

Persistence is hardware-defined. Configuration fields generally remain until modeset or link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, statistic, calibration, and diagnostic fields may be sampled, latched, read-only, write-one-to-clear, self-clearing, or valid only while the relevant supervisor, PLL, or lane clock/power domain is active. This generated header does not describe those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and companion offset definitions:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_*` offsets for the fields described by this shift/mask header.
- AMD display resource and hardware-sequencing code includes generated offset and shift/mask headers to initialize register, shift, and mask tables for the relevant DCN/DPCS generation.
- Link encoder, PHY, clock-source, AUX/link-training, power-management, and diagnostics code consume those tables indirectly when programming common PLLs, reference clocks, lane power, DisplayPort/HDMI link behavior, RX adaptation, DCC, RTUNE, and analog debug paths.
- Firmware and hardware state machines interact with the same registers, especially for MPLL lock/power state, bandgap/reference startup, RTUNE, DCC calibration, RX adaptation, receive-detect, and lane request/ACK handshakes.

Behaviorally, this chunk sits below the user-facing display stack. It provides the bit definitions used when the driver brings up CR3 common resources, selects and programs MPLLA/MPLLB clocking, powers TX/RX lanes, trains or retrains links, enters low-power PHY states, reads diagnostic counters, or forces overrides for hardware validation.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while writing the wrong DPCS bit, corrupting a reserved bit, or decoding a hardware status field incorrectly.
- The file is generated metadata. Manual edits risk divergence from the authoritative AMD register database, the matching offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are artificial. This slice starts with masks for `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`; the matching shift definitions are immediately before line 64393. It ends after `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2`; the following lane 1 TX output and RX ASIC input fields are in the next chunk.
- Supervisor and lane naming is dense and repetitive. A generator or merge error can affect only one PLL bank, one lane, or one override/status pairing while nearby groups appear correct.
- PLL, bandgap, reference-clock, and RTUNE fields are sequencing-sensitive. Bad masks for enables, standby, dividers, SSC, fractional-N, charge pump, power-up timers, RTUNE requests, or calibration codes can cause PLL lock failure, unstable PHY clocks, link-training failure, blank displays, high error rates, or suspend/resume-only regressions.
- Lane power and handshake fields are also sequencing-sensitive. Confusing request, ACK, reset, data-enable, low-power, pstate, rate, width, MPLL select, receive-detect, or disable bits can lead to stuck handshakes, false receive-detect results, lane bring-up failures, or incorrect power state transitions.
- Analog override and debug fields can bypass normal hardware control. Incorrect DCC DAC, termination, equalization, Vboost, VREF, bandgap, ATB, PMIX, or PLL analog masks may alter electrical behavior or hide the debug evidence needed to diagnose link problems.
- Reserved fields are explicitly named in many registers. Register update helpers must preserve reserved bits according to hardware requirements; broad writes built from incorrect masks could unintentionally toggle reserved silicon behavior.
- Status and counter fields need access-semantics knowledge outside this header. RX statistic counters, calibration status, PLL lock/power-good status, RTUNE status, and DCC ACK/readback fields may be stale or invalid if read while the associated domain is off or transitioning.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.0. Missing or renamed macros should fail where register, shift, and mask tables are initialized.
- Mechanically verify that complete fields in this range have expected `__SHIFT`/`_MASK` pairs, allowing the known start boundary where `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN` shifts are before this chunk.
- Cross-check this range against `dpcs_4_2_0_offset.h` so each complete `DPCSSYS_CR3_SUP_*`, `DPCSSYS_CR3_LANE0_*`, and partial `DPCSSYS_CR3_LANE1_*` register group has a matching offset.
- Diff the chunk against AMD's authoritative DPCS 4.2.0 register database and nearby generated DPCS variants where the CR3 supervisor and lane layouts are expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, and lane power states. Expected signals are stable PLL lock, correct MPLL selection, clean lane request/ACK transitions, successful receive-detect, and no repeated retraining caused by bad pstate/rate/width or calibration fields.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, runtime power management, and GPU reset paths to catch persistence or reinitialization mistakes in supervisor, PLL, RTUNE, lane power, DCC, and analog override fields.
- Validate clock-sensitive modes that stress MPLLA/MPLLB divider, SSC, fractional-N, HDMI divider, reference-clock, and bandgap timing controls. Watch for blank displays, PHY lock failures, audio/video timing instability, symbol errors, or clock recovery issues.
- Use register dumps or PHY debug traces during failing links to confirm RTUNE, MPLL lock/power, bandgap/reference startup, DCC ACK/readback, RX adaptation/equalization, RX statistic counters, and lane TX/RX handshake fields decode correctly.
- Exercise diagnostic paths where available: RX statistic match/count controls, analog test bus selections, DCC DAC controls, termination and EQ override readbacks, async/loopback controls, and PLL/bandgap/RTUNE analog override outputs.

## Cross-Chunk Notes

The previous chunk owns the `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN` shift definitions and earlier CR3 supervisor charge-pump override fields. This chunk begins with that register's masks, then covers a large CR3 supervisor and lane 0 section plus the beginning of CR3 lane 1 ASIC definitions. The next chunk should begin with `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_OUT` and continue lane 1 TX/RX ASIC fields. The final per-file research document should reconcile these boundaries before making whole-file claims about CR3 register coverage.

### subset-b-002316: lines 66751-69107

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 66751-69107

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY/controller registers. It contains no executable C logic; its public surface is preprocessor constants that encode DPCS register field bit positions (`__SHIFT`) and bit masks (`_MASK`).

The requested range contains 2,141 `#define` entries across 217 register groups. It starts at the mask tail for `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2`, covers most of the CR3 lane 1 digital ASIC, TX/RX power, RX calibration/adaptation/statistic, digital-to-analog, and analog TX/RX field masks, then begins the corresponding CR3 lane 2 digital ASIC field sequence. The range ends in the `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` shift definitions; that register's masks continue in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the DPCS register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, compose, or update that field.

Most complete register groups in this range are 16-bit DPCS register fields. The slice has one artificial boundary at the start, where `TX_PRE_CURSOR` and shift definitions for `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2` are in the previous chunk and this chunk only owns `TX_POST_CURSOR_MASK` plus the reserved high-nibble mask. It has another boundary at the end, where `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` shifts start here and the masks continue after line 69107.

The main register-field families are:

- Lane 1 ASIC TX/RX interface fields: `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_OUT`, `RX_ASIC_IN_0/1`, `RX_EQ_ASIC_IN_0/1`, `RX_CDR_VCO_ASIC_IN_0/1`, and `RX_ASIC_OUT_0` describe request/ACK, TX acknowledge, receive-detect result, reset, invert, data enable, low-power detect, pstate, rate, width, AFE/DFE adaptation enables, CDR tracking and SSC, RX termination, alignment, EQ attenuation/VGA/CTLE/DFE taps, VCO/ref load values, RX valid, and adaptation status.
- Lane 1 digital override and observation fields: `RX_OVRD_IN_6`, `TX_OVRD_IN_5`, `TX_OVRD_OUT_1`, and `DIG_ASIC_OCLA` expose RX PWM clock/enable and termination overrides, master/other-lane clock and shift handshakes, lane-master overrides, DWORD clock sync overrides, repeated output override fields, and OCLA RX DWORD probe controls.
- Lane 1 TX power-control fields: `DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` encode analog refgen, VCM hold, analog/digital/word clocks, analog reset, serial enable, data enable, receive-detect permission, DCC compensation enable, and Vboost allowance per TX power state. `TX_PWRUP_TIME_0-5` provide staged TX bring-up timing for refgen, VCM, clocks, reset, serial/data enable, RX detect, DCC compensation, skip controls, and fast RX-detect timing.
- Lane 1 TX DCC controls: `DCC_CR_BANK_ADDR`, `DCC_CR_BANK_DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, and `DCC_DAC_ADDR` describe indirect calibration-bank addressing, DCC DAC request/update controls, range, selection, bin-hot fields, ACK, and DAC address selection.
- Lane 1 RX power, VCO calibration, CDR, DPLL, adaptation, and statistics: `DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1/P2`, `RX_PWRUP_TIME_1-3`, `RX_VCOCAL_RX_VCO_CAL_CTRL_0-2`, `RX_VCO_CAL_TIME_0-1`, `RX_VCO_STAT_0-2`, `RX_CDR_CDR_CTL_0-4`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, `RX_DPLL_FREQ_BOUND_0/1`, `RX_ADPTCTL_ADPT_CFG_0-9`, `RST_ADPT_CFG`, `ATT/VGA/CTLE/DFE_*_STATUS`, slicer and VDAC-offset registers, `ADPT_RESET`, DAC-control select registers, CR-bank address/data, and `RX_STAT_*` registers cover RX pstate programming, clock/data/reset/slicer/adaptation enable, VCO startup/calibration timing and status, CDR bypass/tracking/rate controls, digital PLL frequency and bounds, adaptation algorithm timing/gains/modes, adaptation status readback, statistic pattern match/mask/counter controls, sample counters, valid-loss controls, and stat stop/done flags.
- Lane 1 MPHY and digital-to-analog bridge fields: `DIG_MPHY_RX_PWM_CTL`, `DIG_MPHY_RX_TERM_LS_CTL`, `DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT`, `DIG_ANA_TX_OVRD_OUT*`, TX termination-code and EQ override outputs, `DIG_ANA_RX_CTL_OVRD_OUT`, `DIG_ANA_RX_PWR_OVRD_OUT`, `DIG_ANA_RX_VCO_OVRD_OUT_0-2`, `DIG_ANA_RX_CAL`, RX DAC-control fields, RX AFE attenuation/VGA/CTLE fields, RX scope/slicer/IQ/cal-DAC/signals-change controls, `DIG_ANA_STATUS_0/1`, RX termination-code overrides, MPHY overrides, signal-detect overrides, and TX DCC DAC override outputs map digital control signals to analog PHY inputs or expose analog status.
- Lane 1 analog TX/RX fields: `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1/2`, `ANA_TX_DCC_DAC`, `ANA_TX_DCC_CTRL1`, `ANA_TX_TERM_CODE`, `ANA_TX_TERM_CODE_CTRL`, `ANA_TX_OVRD_CLK`, `ANA_TX_MISC1-3`, reserved TX registers, `ANA_RX_CLK_1/2`, `ANA_RX_CDR_DES`, `ANA_RX_SLC_CTRL`, `ANA_RX_PWR_CTRL1/2`, `ANA_RX_SQ`, `ANA_RX_CAL1/2`, `ANA_RX_ATB_*`, and `ANA_RX_RESERVED1` define analog test bus selection, TX power/clock/measurement overrides, termination/DCC controls, Vref/slew/peaking/vreg and misc analog controls, RX CDR/VCO clock controls, slicer controls, RX power settings, squelch/signal-detect tuning, calibration values, and analog-test measurement forcing.
- Lane 2 digital ASIC bring-up sequence: the chunk begins `DPCSSYS_CR3_LANE2_DIG_ASIC_LANE_OVRD_IN`, TX override input/output groups, RX override input/EQ/output groups, lane ASIC input, TX ASIC input/output, RX ASIC input/EQ/VCO/output, RX override input 6, TX override input 5, TX override output 1, OCLA, and the first `TX_PSTATE_P0` shift definitions. These largely mirror the lane 1 digital ASIC field names, giving lane 2 its own request, pstate, rate, width, MPLL select, data enable, reset, serial, detect-RX, beacon, async TX, loopback, HDMI/MPHY mode, RX/TX handshakes, EQ, termination, VCO/ref-load, and OCLA field constants.

## Control Flow

This header has no runtime control flow. Its role is compile-time register metadata:

1. DCN 3.1 resource code includes `dpcs_4_2_0_offset.h` and this `dpcs_4_2_0_sh_mask.h` header.
2. Register-list and shift/mask-list macros expand token-pasted DPCS names into typed register, shift, and mask tables.
3. Runtime AMD display code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` through those tables.
4. Actual sequencing for PHY lane power, link training, CDR/VCO calibration, DCC, RX adaptation, statistics, and diagnostics is implemented in display resource, link encoder, PHY, AUX/link-training, and hardware-sequencing code outside this generated file.

The constants here describe where bits live. They do not encode access direction, write-one-to-clear behavior, self-clearing behavior, clock-domain requirements, calibration ordering, or timeout rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 DPCS lane registers:

- TX state: pstate-specific analog and digital enable bits, refgen/VCM/word-clock/reset/serial/data controls, receive-detect enable and timing, Vboost/DCC policy, TX pre/post cursor masks, termination-code and EQ override fields, DCC DAC request/update/range/selection/ACK, beacon and async-drive/data controls, loopback, lane-master and cross-lane shift/clock synchronization.
- RX state: reset, inversion, data enable, request, low-power detect, pstate/rate/width, adaptation AFE/DFE enable, CDR tracking/SSC/alignment, termination controls, EQ attenuation/VGA/CTLE/DFE taps, CDR/VCO/ref load values, RX valid/ACK/adaptation status, slicer/VDAC controls, squelch/signal-detect and IQ phase controls.
- Calibration and adaptation state: VCO calibration control/timing/status, CDR control/status, DPLL frequency/bounds, adaptation algorithm configuration, reset and status readbacks for attenuation, VGA, CTLE, DFE taps, and DAC-control selection.
- Diagnostic state: RX statistic match/data mask controls, statistic sample and count registers, valid-loss controls, OCLA enable/data controls, analog test bus and measurement-selection fields, scope/slicer debug fields, MPHY PWM/termination controls, and status/readback bits.
- Lane duplication: line 68624 starts CR3 lane 2 digital ASIC fields. These are separate hardware lane states even when field layouts mirror lane 1.

Persistence is hardware-defined. Configuration fields generally remain until reprogrammed by modeset/link-training code, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization. ACK, status, IRQ-like, statistic, calibration, and handshake fields may be latched, sampled, clear-on-write, self-clearing, or only valid while the relevant lane power and clock domains are active. This generated header does not record those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_*` offsets for the register groups described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both the DPCS 4.2.0 offset and shift/mask headers and uses generated list macros such as `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` to populate link-encoder/AUX-related register tables.
- AMD display register helpers consume the populated offset/shift/mask tables when programming display PHY lanes, link encoders, AUX/DPCS access paths, HPO/DP link encoder paths, and low-level hardware sequencing.
- Firmware and hardware state machines interact with the same register fields for power-state transitions, CDR/VCO calibration, DCC compensation, receiver adaptation, analog override/debug paths, and lane handshakes.

Behaviorally, this chunk sits below the user-facing display stack. Bad constants here are observed as PHY/link failures, incorrect register dumps, broken debug paths, or lane-specific regressions rather than as normal C control-flow bugs.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while writing the wrong DPCS field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from the authoritative AMD register database, the companion offset header, silicon documentation, and firmware assumptions.
- Chunk boundaries split two register groups. `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2` is only partially represented at the start, and `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` is only partially represented at the end. Whole-register claims need reconciliation with adjacent chunks.
- Lane 1 and lane 2 fields are similar but not interchangeable. Copying a mask into the wrong lane's register-table entry can produce a lane-local failure that may only appear on particular connectors, link widths, or routing configurations.
- Power and clock fields are sequencing-sensitive. Incorrect pstate, refgen, VCM, analog/digital clock, reset, serial/data enable, DCC, VCO, CDR, or DPLL masks can cause blank displays, link-training failure, CDR unlock, unstable clocks, high bit error rates, or suspend/resume-only failures.
- Adaptation and analog override fields are electrically sensitive. Bad attenuation, VGA, CTLE, DFE, slicer, squelch, signal-detect, termination, TX EQ, Vref, or DCC masks can degrade signal integrity while the software path appears to have completed normally.
- ACK/status/readback fields are side-effect-sensitive. Confusing input override, output override, ACK, valid, statistic, or calibration-status fields can lead to stuck waits, false success, false timeout, or misleading debug captures.
- Reserved and `NC` fields are present throughout the analog blocks. Incorrect masks that overlap reserved bits may have undocumented effects on specific ASIC revisions.
- Repeated generated lane/register families are copy-sensitive. A generator or merge error can affect only one pstate, one lane, one DFE tap, one calibration field, or one status counter while nearby groups remain correct.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build the AMDGPU display code path that includes `dcn31_resource.c`. Missing or renamed DPCS macros should fail where DPCS register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this slice has a matching `__SHIFT`/`_MASK` pair, allowing the known boundary exceptions for `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2` and `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0`.
- Cross-check every complete `DPCSSYS_CR3_LANE1_*` and `DPCSSYS_CR3_LANE2_*` register group in this range against `dpcs_4_2_0_offset.h` for a corresponding `ixDPCSSYS_*` offset.
- Diff the generated field layout against AMD's authoritative DPCS 4.2.0 register source and nearby generated variants such as `dpcs_4_2_2_sh_mask.h` or `dpcs_4_2_3_sh_mask.h` where layouts are expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available CR3 lane mappings, rates, widths, and power states. Expected signals are stable link training, correct pstate transitions, no stuck ACK/status bits, and no unexpected retraining.
- Run hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence and reinitialization mistakes in lane power, TX/RX reset, CDR/VCO calibration, DCC, and adaptation fields.
- Use register dumps or PHY debug traces during known-good and failing links to confirm TX/RX pstate, DCC, CDR/VCO, DPLL, adaptation, EQ, statistic, and analog override fields decode as expected.
- If available, exercise diagnostic paths for OCLA, RX statistic counters, analog test bus/readback, DCC DAC debug controls, MPHY PWM/termination controls, and loopback/ATE-style overrides.

## Cross-Chunk Notes

The previous chunk owns most of `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2`; this chunk begins with its final masks. The next chunk should continue `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` masks and then proceed through the rest of the lane 2 power/adaptation/analog sequence. The final per-file research document should reconcile these artificial chunk boundaries before making whole-file claims about all DPCS 4.2.0 register groups.

### subset-b-002317: lines 69108-71473

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 69108-71473

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header segment for CR3 lane register fields. It contains only C preprocessor constants: `__SHIFT` macros identify field bit positions and `_MASK` macros identify the corresponding bit masks. The covered range starts inside `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` mask definitions, continues through most lane 2 digital/analog PHY field definitions, and then enters lane 3 through ASIC/TX power/RX statistics/TX analog override definitions. It has no executable code, types, storage objects, or functions.

## Purpose

The header gives register-field metadata for low-level AMD display PHY programming. Driver code combines these masks and shifts with the matching address definitions from `dpcs_4_2_0_offset.h` to update 16-bit DPCS CR registers without hard-coding bit positions. In this range, the fields describe:

- Lane 2 TX power-state controls, TX power-up timing, DCC DAC controls, TX clock alignment, TX/RX LBERT, RX power-state controls, RX VCO calibration, CDR/DPLL controls, RX adaptation controls/status, RX statistic counters, MPHY controls, digital analog override/status signals, and lane 2 analog TX/RX registers.
- Lane 3 ASIC override/input/output fields, TX power-state and timing controls, TX DCC DAC controls, TX clock alignment, TX LBERT, RX statistic counters, and the beginning of TX analog override/equalization fields.

## Important APIs, Types, And Macros

There are no APIs or types in this chunk. The important interface is the generated macro convention:

- `DPCSSYS_CR3_LANE*_...__FIELD__SHIFT`: bit offset for `FIELD`.
- `DPCSSYS_CR3_LANE*_...__FIELD_MASK`: mask for the same field after shifting.
- Register comments such as `//DPCSSYS_CR3_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_0` delimit field groups and correspond to `ix...` address macros in the companion offset header.

Notable lane 2 groups include:

- `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`: per-power-state TX enables for refgen, VCM hold, analog/digital clocks, reset, serial, data, RX detect allowance, VBOOST allowance, and DCC compensation calibration.
- `DIG_TX_PWRCTL_TX_PWRUP_TIME_0..5`: power sequencing delays for refgen, clock enable, VCM hold, VBOOST disable, RX detect, reset, and serial enable.
- `DIG_TX_PWRCTL_DCC_*`: CR bank address/data, DCC DAC control/range/selection/ack/address.
- `DIG_RX_PWRCTL_RX_PSTATE_*` and `DIG_RX_PWRCTL_RX_PWRUP_TIME_*`: RX analog enable, clock/AFE controls, DFE/adaptation enable, CDR tracking, and RX startup timing.
- `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`: VCO calibration, CDR configuration/status, and DPLL frequency/bounds.
- `DIG_RX_ADPTCTL_*`: adaptation configuration and tap/status reporting for ATT, VGA, CTLE, DFE taps, slicer levels, DAC selections, and CR bank access.
- `DIG_RX_STAT_*`: pattern match, sample count, statistic counter, clock, valid-loss, and stop controls.
- `DIG_ANA_*` and `ANA_*`: digital-to-analog override outputs/status plus raw analog TX/RX controls such as term code, equalization, RX clock/CDR, slicer, power, squelch, calibration, ATB measurement, and reserved analog registers.

Notable lane 3 groups include:

- `DIG_ASIC_*`: lane loopback, TX request/PSTATE/rate/width/data and training override controls, ASIC input/output status, RX output status, and handshake/control override fields.
- `DIG_TX_PWRCTL_*`: lane 3 equivalents of the TX power-state, timing, DCC, clock-align, and LBERT controls.
- `DIG_RX_STAT_*`: lane 3 statistic pattern/counter/clock/stop definitions.
- `DIG_ANA_TX_*`: lane 3 TX analog override output, term-code, DCC, and equalization fields; this chunk ends while this family is still in progress.

## Control Flow

This file contributes no runtime control flow. At compile time it lets C code build register values with operations of the form "clear bits using `_MASK`, insert shifted field value using `__SHIFT`, then write to the hardware register address." Runtime sequencing is implemented by display/PHY code outside this header. The implied control paths are hardware sequences such as TX/RX power state transitions, RX VCO/CDR calibration, adaptation, statistics collection, LBERT test setup, and analog override programming.

## State And Persistence

The macros are stateless compile-time constants. The state they describe lives in DPCS hardware registers, not in this header. Register values are volatile hardware state and can be reset by GPU reset, display engine reset, power-gating, suspend/resume, link disable, or PHY reinitialization. Reserved field masks are included so callers can preserve or explicitly avoid touching undocumented bits during read-modify-write sequences.

## Dependencies

This header depends on the ASIC register generation pipeline staying synchronized with AMD hardware specifications. It is normally used with:

- `dpcs_4_2_0_offset.h` for register addresses such as lane 2 offsets around `0x1220` and lane 3 offsets around `0x1320`.
- AMD DRM display/DC code that performs MMIO or indexed DPCS CR register access.
- Common register helper macros in the AMD GPU driver that combine mask/shift constants for read-modify-write operations.

The chunk is independent of Ceph logic despite living under the repository's imported Linux source tree.

## Integration Points

These definitions integrate with display link bring-up, link training, DisplayPort/PHY diagnostic paths, and board/ASIC-specific tuning code. The TX power and analog equalization fields affect transmitter startup and signal quality. RX VCO, CDR, DPLL, adaptation, slicer, and statistic fields affect receiver lock and margining. The LBERT and RX statistic fields are integration points for PHY validation and debug. Lane-specific prefixes are important: lane 2 and lane 3 macros are structurally similar but map to different physical-lane register addresses.

## Risks

- The range begins after the `__SHIFT` definitions for `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0`; adjacent chunk data is needed for a complete per-register summary.
- The range ends in the middle of lane 3 TX analog override definitions, so the following chunk must complete that register family.
- Copy/paste or generation errors in masks/shifts would cause silent hardware misprogramming; the compiler cannot validate that a field mask matches the actual register layout.
- Writing reserved bits or failing to preserve them can destabilize analog PHY behavior.
- Lane 2 and lane 3 names are highly repetitive; using the wrong lane macro with the wrong offset can program a different physical lane.
- Power-state, reset, VCO/CDR, DCC, and analog override fields are timing-sensitive and can cause link training failures, display blanking, or intermittent high-rate link instability if programmed out of sequence.

## Test Signals

Useful validation signals for changes touching this generated header or consumers of these fields include:

- Kernel build coverage for AMDGPU display code with this header included.
- Static checks that every `__SHIFT` field has a matching `_MASK` field and that masks fit the expected 16-bit DPCS CR register width unless the register is known wider.
- Display bring-up on ASICs using DPCS 4.2.0, including boot display, hotplug, suspend/resume, modesets, and GPU reset recovery.
- Link-training coverage across lane counts and rates, especially configurations using CR3 lane 2 or lane 3.
- DP/HDMI stress tests, high-bandwidth modes, multi-monitor configurations, and retraining after HPD events.
- Debug/validation paths that exercise LBERT, RX statistic counters, CDR/VCO calibration status, DCC DAC selection/acknowledgement, and analog override/status readback.

### subset-b-002318: lines 71474-73858

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 71474-73858

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It contains preprocessor constants only: no callable functions, structs, enums, storage objects, allocation, or executable control flow. The exported contract is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace, where each macro describes one field position or already-shifted mask for a 16-bit DPCS/PHY control register.

The requested range covers 2,385 source lines and 2,113 `#define` entries: 1,055 shift macros, 1,078 mask macros, and many reserved-bit definitions. It begins inside the tail of the `DPCSSYS_CR3_LANE3_DIG_ANA_TX_EQ_OVRD_OUT_2`/TX equalization override family, completes the lane 3 analog TX status, DCC, override, test, termination, and miscellaneous groups, then covers `DPCSSYS_CR3_RAWCMN` common PHY controls. It then covers essentially all visible `DPCSSYS_CR3_RAWLANE0` PCS/FSM/IRQ/PMA/TX/RX/control fields and starts the matching `DPCSSYS_CR3_RAWLANE1` PCS/FSM/IRQ fields through `RX_ADAPT_DIS_IRQ`, ending at the comment for `RX_RESET_IRQ_CLR`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this header is AMD display/link PHY register metadata. It has no Ceph, distributed filesystem, network-storage, or persistent-disk behavior.

## Purpose

The purpose of this header range is to provide ASIC-specific bit geometry for DCN 3.1 DPCS 4.2.0 CR3 lane, common, raw-lane, FSM, IRQ, and PMA registers. Runtime display code includes this header with the matching `dpcs_4_2_0_offset.h` file so generated register tables can map logical link-encoder fields onto exact DPCS hardware layout.

The covered hardware areas are:

- Lane 3 analog TX tail: TX equalization override outputs for pre/post cursor values and leg-pull direction, analog status readback, TX DCC DAC override output, extra fast-start/loopback/ACJTAG override bits, analog TX measurement, power override, alternate bus, ATB measurement selection, DCC DAC/control, TX termination code and clock controls, override clock, miscellaneous clock/loopback/power-save bits, and reserved analog TX registers.
- CR3 raw-common controls: common PHY functional reset; `MPLLA`/`MPLLB` word-divide, TX-clock-divider, div8/div10, bandwidth, spread-spectrum, and fractional-N overrides; lane-FSM extension; common control for PLL init-cal disable, rtune, HDMI mode, and TX PWM clock; MPLL state timing and bank selection; TX calibration code; SRAM init status; OCLA/debug; supervisor analog overrides; PCS/FW ID-code readbacks; AON retune values for RX/TXDN/TXUP entries 0-7; SRAM block configuration; power-gate, supervisor, resistance, VREF, reference-range, and power-down timing controls.
- CR3 raw-lane0 PCS transfer and test controls: TX/RX PCS override inputs, PCS input mirrors, override outputs, ACK/readback outputs, RX adaptation ACK/FOM and TX pre/main/post direction hints, lane number, reserved scratch registers, ATE RX/TX override inputs, RX EQ delta-IQ controls, TX/RX termination controls, RX EQ override inputs, RX phase-2 calibration, and master MPLL loop controls.
- CR3 raw-lane0 FSM and IRQ controls: FSM override, memory-address/status monitors, fast-path timing flags for RX startup/adaptation/calibration/power/VCO/SUP and TX common-mode/RX-detect paths, continuous calibration/adaptation flags, CR register/memory locks, TX DCC flags/status, OCLA controls, TX EQ update flag, common calibration status, RX IQ phase offset, and IRQ status/clear/mask bits for RX reset/request/rate/pstate/adaptation, lane mode, PH2 calibration, RX-to-TX loopback, DCC on-demand, and TX reset/request.
- CR3 raw-lane0 PMA, TX, and RX control surfaces: PMA lane/supervisor/TX/RX transfer overrides and readbacks, lane rtune request/ack, MPHY override inputs/outputs, RX adaptation output, TX FSM and clock controls, TX DCC continuous status, TX/RX OCLA controls, RX LOS mask, RX data-enable override, off-canonical/adaptation continuous status, and repeated ATE PCS controls.
- CR3 raw-lane1 opening: a second raw-lane PCS/FSM/IRQ pattern mirroring raw-lane0 for TX/RX PCS transfer, RX adaptation, TX equalization direction hints, lane number, ATE and RX EQ controls, RX PH2 calibration, FSM fast flags/status, DCC status, OCLA, TX EQ update, RCAL/MPLL status, RX IQ phase offset, and the first RX IRQ status bits.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important interface is the generated macro naming pattern:

- `*_SHIFT` gives a field's least-significant bit position.
- `*_MASK` gives the field mask in final register position.
- Register names encode DPCS CR instance, lane/raw-lane, block, and register, such as `DPCSSYS_CR3_LANE3_ANA_TX_DCC_CTRL1`, `DPCSSYS_CR3_RAWCMN_DIG_MPLLA_OVRD_IN`, `DPCSSYS_CR3_RAWLANE0_DIG_PCS_XF_RX_OVRD_IN`, and `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_FLAGS`.

The lane 3 analog TX fields define low-level transmitter override and readback controls. Important families include `TX_ANA_CTRL_PRE`, `TX_ANA_CTRL_POST`, `TX_ANA_CTRL_EQ_MUX_SEL`, `TX_ANA_CTRL_LEG_PULL_DIR_*`, `TX_ANA_DCC_CAL_*`, `TX_ANA_FAST_START`, `TX_CLK_LB_EN`, measurement/ATB selectors, power override enables, TX DCC DAC controls, termination code fields, loopback, self-clear clock controls, and TX power-save/miscellaneous bits.

The raw-common `MPLLA`/`MPLLB` fields expose parallel PLL control paths. Each PLL has word-divide, TX clock divisor, div8/div10 enable, bandwidth override, SSC range/clock/enables, and fractional-N control. Common support fields include functional reset, PLL init-cal-disable overrides, rtune request, HDMI-mode and TX PWM controls, MPLL state/off/force-on timing, bank selection, supervisor analog overrides, SRAM init/readback, OCLA probe controls, ID-code readbacks, retune values, power-gate/isolation controls, supervisor force/ref-clock controls, VREF status, resistance request/ack controls, and reference-range override.

The raw-lane PCS transfer fields form the digital boundary between PCS, PMA, lane supervisor, and link logic. TX-side fields include `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, master MPLL state, reset/request/detect-RX, VBOOST/IBOOST, beacon, data enable, async enable/data, serial loopback, ACK, detect-RX result, and TX dword-clock sync override. RX-side fields include `RATE`, `WIDTH`, `PSTATE`, low-power detect, reset/request, CDR VCO/ref load values, adaptation AFE/DFE enable, adaptation request/continuous/off-canonical controls, RX data enable, RX valid, RX LOS thresholds, EQ attenuation/VGA/CTLE/DFE readbacks, adaptation ACK/FOM, and TX pre/main/post direction outputs.

The raw-lane FSM fields provide firmware or microcontroller state-machine observability and fast-path controls. They include FSM override enables, program counter, RAM readiness, memory address/status monitors, one-bit fast timing or skip flags for startup and continuous RX calibration/adaptation steps, TX DCC flags/status, common MPLL/RCAL init/done status, CR register/memory locks, OCLA bank enable bits, TX EQ update flag, and RX IQ phase offset.

The IRQ control fields define lane event plumbing. This chunk includes status, clear, and mask families for reset, request, rate, pstate, adaptation request/disable, lane transceiver mode, RX PH2 calibration request/disable, RX-to-TX serial loopback enable, DCC on-demand, TX reset, and TX request. For raw-lane1 the chunk reaches only the first RX IRQ status bits; the clear and mask families continue after the requested range.

The PMA and control fields at the end of raw-lane0 expose PMA transfer boundaries and lane-local control. They include lane MPLL enables, supervisor state, TX/RX request/reset override paths, data enable, loopback, ACK/readback inputs, rtune control, MPHY PWM/term/async/clock-selection controls, RX adaptation output, TX FSM/clock/DCC continuous status, RX LOS masking, RX data enable override, off-canonical/adaptation continuous status, and OCLA debug enables.

## Control Flow

This header range has no local control flow. Runtime behavior is created by consumers that include `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`, construct register/field tables, and then use AMD display register helpers to perform MMIO or CR-indirect reads and writes.

A typical DCN 3.1 path is:

1. `display/dc/resource/dcn31/dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`.
2. Resource construction initializes `le_shift` and `le_mask` with `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
3. Link encoder and HPO DP link encoder code use those tables through register helper operations such as `REG_GET`, `REG_SET`, and `REG_UPDATE` variants.
4. Higher-level display code sequences PHY reset, PLL setup, TX/RX lane enable, DisplayPort/HDMI mode transitions, lane training, equalization, power-state transitions, IRQ handling, debug capture, hotplug recovery, suspend/resume, and GPU reset recovery.

The header itself does not encode ordering, delays, polling loops, field writability, lane ownership, or policy. Those rules live in display resource, link encoder, HPO DP, GPIO, IRQ, clock manager, hardware sequencer, and firmware-facing code that consumes the generated tables.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware register state whose lifetime is controlled by DPCS/PHY programming, link training, modesets, hotplug handling, DP/HDMI mode changes, runtime power management, suspend/resume, and GPU reset.

State represented by this chunk includes:

- Lane 3 analog TX state for equalization, leg-pull direction, termination, DCC DAC/control, clock/loopback/fast-start, ATB/measurement selection, power override, and analog TX status.
- Common PHY state for reset, PLL dividers, bandwidth/SSC/fractional-N controls, init calibration disable, rtune, HDMI/PWM mode, MPLL state timing, SRAM init, supervisor analog overrides, retune values, power-gate/isolation, VREF, resistance handshakes, and reference range.
- Raw-lane PCS state for TX/RX reset/request/ack handshakes, rate/width/pstate/LPD, MPLL selection, data/async enable, VBOOST/IBOOST, detect-RX, loopback, RX valid, RX adaptation request/ack/FOM, equalization readbacks, and direction hints used during training.
- Raw-lane FSM and IRQ state for fast/skip flags, continuous calibration/adaptation state, DCC and common calibration status, CR locks, debug bank enables, IRQ status/clear/mask values, TX EQ update state, and RX IQ phase offset.
- Raw-lane PMA/control state for PMA supervisor/TX/RX transfer overrides, rtune, MPHY PWM/term/async controls, TX/RX clock and FSM state, LOS masking, data-enable override, and OCLA/debug capture.

Many fields are status-like readbacks, including ACK bits, calibration done/status bits, FOM values, EQ readbacks, SRAM init done, ID codes, retune values, VREF stats, IRQ status bits, FSM status monitors, CR lock bits, and PMA/PCS mirrors. Other fields are writable controls that can immediately change live PHY behavior or arm clear/pulse-style paths. Fields named `*_REQ`, `*_ACK`, `*_CLR`, `*_OVRD_EN`, `*_UPDATE_FLAG`, `*_SELF_CLEAR_DISABLE`, `*_CLK`, or `*_START` are especially sequencing-sensitive.

Bad values can persist until the lane, common PHY, DPCS block, display link, or whole GPU is reset or reprogrammed. Some state is reconstructed during modeset, hotplug recovery, link training, suspend/resume, and runtime PM, but this generated header has no restore logic; it only defines the bit layout those paths rely on.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides matching generated register offsets. These masks are only correct when paired with the DPCS 4.2.0 offset header and DCN 3.1 resource layout.

Visible integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which directly includes both DPCS 4.2.0 generated headers and builds `le_shift`/`le_mask` tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`, which defines `DPCS_DCN31_MASK_SH_LIST` and the logical DPCS field set token-pasted against `__SHIFT` and `_MASK`.
- DCN link encoder and HPO DP link encoder code that consumes generated shift/mask tables through AMD display register helpers for DPCS PHY and link-encoder control.
- GPIO, IRQ, clock-manager, and resource code for nearby AMD display generations, which follow the same generated offset/shift-mask pairing pattern.

The generated namespace is cross-generation in shape but not interchangeable. Nearby DPCS headers such as `dpcs_4_2_2_sh_mask.h`, `dpcs_4_2_3_sh_mask.h`, and older `dpcs_3_*_sh_mask.h` contain similar register families, but field availability, field widths, and exact masks may differ. Consumers must bind the correct offset and mask pair for the target ASIC.

## Risks And Edge Cases

The main risk is silent PHY misprogramming. Shift and mask constants compile cleanly even when wrong, but a bad value can update a neighboring field, truncate a multi-bit control, miss a clear/pulse bit, decode a status bit incorrectly, or force the wrong lane/PLL state.

Chunk-boundary risk is present. The first in-scope lines are already inside the lane 3 TX equalization override family; the preceding chunk owns earlier `TX_EQ_OVRD_OUT_2` context and the first lane 3 TX-EQ fields. The final line is only the comment for `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_RX_RESET_IRQ_CLR`; its shift/mask definitions and the rest of raw-lane1 IRQ/PMA/control fields continue in the next chunk. The final per-file report should merge adjacent chunks before making complete claims about those boundary registers.

Lane and instance pairing are critical. This range mixes `CR3_LANE3`, `CR3_RAWCMN`, `CR3_RAWLANE0`, and `CR3_RAWLANE1` names. A valid macro copied to the wrong lane instance or paired with a mismatched offset can produce failures that look like link-training, clocking, or signal-integrity bugs.

PLL and common-clock fields are high risk. `MPLLA`/`MPLLB` dividers, bandwidth controls, spread-spectrum fields, fractional-N values, PLL state timing, HDMI mode, TX PWM clock controls, and reference-range overrides affect symbol clocks and link stability. Wrong masks can cause no-link, intermittent training failure, jitter, or mode-specific display loss.

Analog and equalization fields are calibration-sensitive. TX pre/post, leg-pull direction, termination, DCC DAC/control, VBOOST/IBOOST, RX LOS thresholds, RX EQ readbacks, CDR VCO/ref load values, adaptation controls, and signal-detect behavior can produce subtle failures at high link rates, with specific cables, docks, boards, alt-mode paths, or lane mappings.

Handshake and power-state fields are sequencing-sensitive. TX/RX request/reset/ack, pstate/rate/width, data-enable, async enable/data, detect-RX, adaptation request/ack, PMA ACK, rtune, loopback, and supervisor state must be changed in hardware-defined order. The masks do not express waits, ownership, read-only/write-one-to-clear behavior, self-clearing semantics, or required restore order.

IRQ and debug fields can mislead diagnostics. Incorrect status, clear, or mask constants may hide lane events, clear the wrong interrupt, leave an interrupt stuck, or make OCLA/FSM/DCC/debug readbacks appear plausible but wrong.

Reserved fields appear frequently. Generic full-register writes must preserve reserved bits unless the hardware database explicitly requires otherwise. Many registers are 16-bit views with dense reserved regions, so read-modify-write discipline matters.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile DCN 3.1 AMDGPU Display Core resource, link encoder, HPO DP, GPIO, IRQ, and clock/resource code with DPCS 4.2.0 headers enabled, ensuring all generated symbols used by `DPCS_DCN31_MASK_SH_LIST` resolve.
- Run generated-register consistency checks: every logical field has a matching offset/header pair, each `*_MASK` matches the intended `*_SHIFT` and width, and no field list references a missing or wrong-generation macro.
- Diff against AMD's authoritative DPCS 4.2.0 register database and nearby DPCS 4.2.2/4.2.3 headers, with expected generation differences reviewed instead of normalized away.
- Exercise DP/HDMI link bring-up across lane counts, link rates, MST/HPO paths, USB-C/DP alt-mode, dock paths, hotplug/unplug, suspend/resume, runtime PM, and GPU reset.
- Validate PLL and common-clock paths for MPLLA/MPLLB selection, dividers, SSC/fractional-N, bandwidth override, HDMI/PWM modes, reference-range, SRAM init, power-gating, and supervisor force/ack behavior.
- Test TX/RX lane handshakes for reset/request/ack, pstate/rate/width transitions, data/async enable, detect-RX, VBOOST/IBOOST, loopback, RX valid, adaptation request/ack/FOM, PMA ACK, and rtune.
- Run signal-integrity and link-training tests that stress TX EQ pre/post, termination, DCC DAC, RX LOS thresholds, RX EQ/CTLE/DFE values, VCO/ref load controls, continuous adaptation, and IQ phase offset at high rates.
- Trigger IRQ/debug events for reset/request/rate/pstate/adaptation, PH2 calibration, loopback, DCC on-demand, and TX reset/request; verify status, mask, and clear behavior plus FSM/OCLA readbacks.
- Validate recovery from interrupted or failed link-training sequences through hotplug recovery, modeset, suspend/resume, runtime power cycling, and GPU reset.

Regression symptoms from bad constants include blank display output, intermittent DP training failures, reduced maximum link rate, HDMI mode failures, USB-C/DP alt-mode instability, dock-specific failures, flicker at high rates, stuck reset/request/ack bits, missing or storming interrupts, failed suspend/resume recovery, incorrect PHY debug counters, and failures isolated to DCN 3.1 ASICs using DPCS 4.2.0.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dpcs_4_2_0_sh_mask.h`. The previous chunk is required for the beginning of lane 3 analog TX equalization override context before line 71474. The next chunk is required for the raw-lane1 IRQ clear/mask continuation and later raw-lane1 PMA/TX/RX/control definitions after line 73858. The merge/reconciliation lane should treat this document as the CR3 lane 3 analog TX tail, raw-common, raw-lane0 PCS/FSM/IRQ/PMA/control, and raw-lane1 opening portion of the full DPCS 4.2.0 shift/mask contract.

### subset-b-002319: lines 73859-76242

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 73859-76242

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for low-level display PHY register fields. It contains no executable C logic; its interface is a dense set of preprocessor constants used by AMDGPU display code to pack and decode bitfields in DPCS registers.

The requested range contains 2,107 `#define` entries: 1,055 `__SHIFT` macros and 1,052 `_MASK` macros. The mismatch is expected from the chunk boundaries. The range starts in the middle of `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_RX_RESET_IRQ_CLR`, so the register comment and some adjacent context are just before the chunk. It ends in the middle of `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT`, with the final masks and subsequent RAWLANE3 PMA/TX/RX control registers continuing in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file belongs to `drivers/gpu/drm/amd/include/asic_reg/dpcs` and describes AMD display hardware, not Ceph or distributed filesystem behavior.

## Register Groups Covered

The line range spans CR3 raw-lane register layouts:

- RAWLANE1 tail: IRQ clear/status/mask fields for RX/TX reset/request, RX rate, pstate, adaptation request/disable, lane transceiver mode, PH2 calibration, lane RX-to-TX serial loopback, and DCC on-demand IRQs; PMA transfer and override registers for MPLLA/MPLLB lane enable, supervisor state, TX/RX request/reset/data-enable overrides, TX beacon/async/clock-sync controls, loopback controls, PMA ACKs, lane RTUNE, MPHY PWM/termination controls, RX adaptation IQ phase adjustment, TX/RX control/status/OCLA fields, ATE PCS override fields, master MPLL loop, and additional ATE/RX override surfaces.
- RAWLANE2 main body: PCS transfer registers for TX and RX pstate/rate/width/MPLL/reset/request/detect-rx/data-enable/loopback/adaptation/equalization/termination/PH2 calibration; FSM status and fast-control fields for startup calibration, RX adaptation, AFE/DFE/bypass/reference-level/IQ calibration, supervisor and TX common-mode steps, RX detect/power-up/VCO wait/VCO cal, continuous calibration/adaptation flags, CR lock, TX DCC flags, OCLA, TX EQ update, RCAL status, and RX IQ phase offset; complete RAWLANE2 IRQ, PMA transfer, TX control, RX control, and ATE override groups.
- RAWLANE3 beginning through PMA RX override: PCS transfer, RX adaptation feedback, lane number/reserved fields, ATE override, RX equalization delta/IQ and termination controls, PH2 calibration, FSM monitor/fast-control/status fields, complete IRQ status/clear/mask groups, PMA lane/supervisor/TX override groups, TX PMA ACK, and the beginning of PMA RX request/reset/loopback/data-enable override fields.

Most fields are 16-bit register payload fields represented as `long`-suffixed mask literals such as `0x0000FFFEL`. The repeated RAWLANE2 and RAWLANE3 layouts are intentionally similar, but the lane number in the macro name remains part of the contract.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO calls in this chunk. The exported API is the generated macro naming convention:

- `DPCSSYS_CR3_RAWLANE<n>_<BLOCK>__<FIELD>__SHIFT` gives the least-significant bit position for a hardware field.
- `DPCSSYS_CR3_RAWLANE<n>_<BLOCK>__<FIELD>_MASK` gives the bit mask for isolating or updating that field.
- `RESERVED_*`, `RSVD_*`, and similar fields preserve exact hardware layout for reserved bit ranges; they are metadata, not permission to write arbitrary values into reserved bits.

Important field families include:

- IRQ control: status, write-clear, and mask bits for RX reset/request/rate/pstate/adaptation, TX reset/request, transceiver-mode changes, PH2 calibration events, RX-to-TX loopback, and DCC on-demand events.
- PCS transfer: TX/RX override inputs and outputs for request, reset, pstate, rate, width, low-power detect, detect-rx request/result, Vboost/Iboost, beacon, async data/drive, lane loopback, MPLL select/enable/state, data enable, RX valid/clock, LOS threshold, VCO/ref-load values, RX equalization status, adaptation controls, directed TX pre/main/post feedback, and lane numbering.
- FSM and calibration: enable/status bits for fast RX startup, adaptation, AFE/DFE/bypass/reference-level/IQ calibration, continuous adaptation/data/phase/AFE calibration, VCO wait/calibration, RX power-up, TX common-mode, RX detect, common MPLL/RCAL status, TX DCC flags/status, CR lock, and RX IQ phase offset.
- PMA transfer: lane MPLLA/MPLLB enable overrides, supervisor MPLL state overrides, TX/RX request and reset overrides, TX beacon/async/clock-sync/data-enable controls, serial/parallel loopback controls, PMA ACK readbacks, RTUNE request/ACK, MPHY PWM/termination overrides, and RX IQ phase adjustment map override.
- TX/RX control and debug: TX FSM wait/allow-rxdet controls, TX clock divider and duty-cycle-continuation status, RX FSM/rate-change controls, RX LOS mask/data-enable override timing, off-cancel/adaptation continuous status, and OCLA/UPCS debug probe enables.
- ATE and validation: ATE RX/TX override inputs, master MPLL loop controls, additional RX override outputs, equalization overrides, and PH2 calibration request/ACK fields used by manufacturing, validation, or deep PHY debug flows.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of register field tables and read-modify-write helpers:

1. AMD display code includes the DPCS 4.2.0 offset header plus this shift/mask header.
2. Register-list and shift/mask-list macros token-paste register and field names into ASIC-specific tables.
3. Runtime code uses AMDGPU display register helpers, such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, or `REG_UPDATE`, to program or poll the corresponding hardware fields.
4. Hardware, firmware, and display driver sequencing code outside this header perform the real operations: PHY reset, lane power sequencing, link training, RX adaptation, PLL selection, IRQ handling, test/debug collection, and suspend/resume reinitialization.

The macros describe where bits live. They do not encode access direction, write-one-to-clear behavior, self-clearing bits, latch semantics, polling timeouts, clock-domain requirements, or safe programming order.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. The fields name hardware-visible state in DPCS CR3 raw-lane registers:

- Live lane state includes TX/RX request, reset, pstate, rate, width, MPLL selection/enables, low-power detect, detect-rx, beacon, async data, loopback, data enable, RX valid, clock controls, and lane-number reporting.
- Calibration and adaptation state includes RX startup/AFE/DFE/IQ/reference-level calibration, VCO wait/calibration, continuous adaptation/data/phase/AFE calibration, RX equalization values, IQ phase offset/adjustment maps, PH2 calibration, RCAL and common MPLL status, and TX DCC status.
- Interrupt state includes latched status, clear strobes, and mask bits for lane request/reset/rate/pstate/adaptation/PH2/loopback/DCC events.
- Debug and validation state includes OCLA/UPCS selections, ATE override inputs, directed TX coefficient feedback, RX adaptation ACK/FOM, RTUNE, MPHY PWM/termination overrides, and PMA/PCS ACK handshakes.

Persistence is hardware-defined. Configuration and override fields generally persist until rewritten by a modeset, link-training step, PHY reset, power-gate transition, suspend/resume path, GPU reset, or ASIC reinitialization. Status, IRQ, ACK, calibration, and statistic-like fields may be transient, latched, clear-on-write, self-clearing, or valid only when the relevant lane/common power and clock domains are active.

## Dependencies And Integration Points

This generated header is tightly coupled to AMD's DPCS 4.2.0 register database and companion address definitions:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_CR3_RAWLANE*` register offsets, such as RAWLANE1 offsets around `0x3140`, RAWLANE2 around `0x3240`, and RAWLANE3 around `0x3340`.
- AMD display DCN/DPCS resource code consumes these macros through generated register, shift, and mask tables for the ASIC generation that owns DPCS 4.2.0.
- Link encoder, PHY, clock-source, AUX/link-training, hotplug, modeset, power-management, and hardware-sequencing code indirectly depends on these constants when programming DPCS lanes.
- Firmware and hardware state machines interact with the same register bits for lane handshakes, PMA/PCS transfers, RX adaptation, PLL/MPLL state, DCC, RTUNE, PH2 calibration, and IRQ latching.

The chunk is low-level hardware metadata. Its user-visible impact appears indirectly as display link stability, correct power transitions, reliable hotplug/modeset behavior, and useful PHY debug telemetry.

## Risks And Edge Cases

- Incorrect masks or shifts compile cleanly but can program the wrong hardware bit, corrupt a reserved field, miss a status bit, or clear/mask the wrong interrupt.
- This is generated metadata. Manual edits can diverge from the authoritative AMD register database, companion offset headers, firmware assumptions, and silicon documentation.
- The chunk starts and ends mid-register-group. The previous chunk owns the `RAWLANE1_DIG_IRQ_CTL_RX_RESET_IRQ_CLR` comment and earlier fields; the next chunk owns the remaining `RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT` masks and subsequent PMA/TX/RX control groups.
- RAWLANE1, RAWLANE2, and RAWLANE3 macros are not interchangeable even when field layouts match. Using a lane 2 mask with a lane 3 offset, or vice versa, may silently target the wrong hardware lane.
- IRQ status, clear, and mask registers are side-effect-sensitive. Confusing status bits with clear strobes or mask bits can produce repeated interrupts, missed lane events, stuck waits, or failure to observe link-training transitions.
- Override fields are sequencing-sensitive. Leaving PMA/PCS/ATE override enables asserted can bypass normal state-machine control of request/reset/data-enable/MPLL/loopback/termination behavior.
- Power, PLL, calibration, and adaptation fields affect link integrity. One-bit mistakes in VCO, RX adaptation, DCC, RTUNE, PH2 calibration, pstate, or MPLL-related fields can cause blank displays, unstable high-rate links, repeated retraining, resume-only failures, or difficult-to-debug PHY lock problems.
- Reserved masks are emitted for layout completeness. Driver writes should preserve reserved bits unless hardware documentation explicitly requires a value.

## Test Signals

Useful validation for this chunk combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.0. Missing or renamed macros should fail where register, shift, and mask tables are initialized.
- Mechanically verify that each complete field has a matching `__SHIFT` and `_MASK`, allowing the known boundary exceptions at the start and end of this chunk.
- Cross-check every complete register group in this range against `dpcs_4_2_0_offset.h` and against AMD's authoritative DPCS 4.2.0 register source.
- Compare repeated RAWLANE2 and RAWLANE3 field layouts where hardware expects them to match, while preserving lane-specific macro names and offsets.
- Exercise DisplayPort and HDMI link bring-up across available lanes, rates, widths, and power states. Good signals are stable link training, correct lane power transitions, expected MPLL selection, no stuck ACK/status bits, and no false or missing lane IRQs.
- Run hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence and reinitialization problems around IRQ, pstate, PMA/PCS override, calibration, and adaptation fields.
- Use register dumps or PHY debug traces on failures to confirm IRQ clear/mask, RX adaptation ACK/FOM, TX directed coefficient feedback, VCO/ref-load, DCC status, RTUNE, FSM status, PH2 calibration, and OCLA/UPCS fields decode as expected.
- Exercise manufacturing/debug paths where available, including ATE overrides, PMA loopback, RX/TX termination controls, RX EQ overrides, master MPLL loop controls, and OCLA probes.

## Cross-Chunk Notes

The previous chunk should provide the beginning of RAWLANE1 IRQ clear definitions, including the comment and earlier fields for `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_RX_RESET_IRQ_CLR`. This chunk then covers the RAWLANE1 tail, the complete RAWLANE2 PCS/FSM/IRQ/PMA/control/ATE span, and RAWLANE3 through the beginning of PMA RX override output. The next chunk should resume with the remaining `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT` masks and continue RAWLANE3 PMA, TX control, RX control, and later groups. The final per-file report should reconcile these boundaries before making whole-file completeness claims.

### subset-b-002320: lines 76243-78683

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 76243-78683

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for DCN 3.1 display PHY register fields. It contains no executable C code. Its public surface is preprocessor metadata that tells AMDGPU display code where individual bitfields live inside DPCS control/status registers.

The requested range contains 2,074 `#define` entries: 1,036 `__SHIFT` constants and 1,038 `_MASK` constants. It starts inside the tail of `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT`, covers the remaining CR3 raw-lane-3 PMA/TX/RX/PCS control fields, then covers repeated CR3 always-on lane calibration/status fields for lanes 0 through 3. It ends inside the beginning of `DPCSSYS_CR3_RAWAONLANEX_DIG_DFE_DATA_EVEN_LOW_VDAC_OFST`, so both the first and last registers are split by chunk boundaries.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller register metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or direct MMIO operations in this range. The API contract is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask of that field within its hardware register.

The main macro families in this chunk are:

- `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_*`: PMA interface fields for lane 3, including RX/TX request, reset, data-enable and loopback override bits; PMA ack and retune request/ack bits; MPHY override controls for RX PWM clocks/data, async enable, PWM enable, clock select, and RX termination; and RX adaptation phase-map override controls.
- `DPCSSYS_CR3_RAWLANE3_DIG_TX_CTL_*`: lane-3 TX state-machine and clock controls, including MPLL-off wait time, RX-detect allowance in P states, TX clock enable/select, async beacon wait time, TX DCC continuous status, OCLA enable, and UPCS data/clock observation enables.
- `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_*`: lane-3 RX state-machine controls and status bits, including RX control FSM enable, P1 rate-change allowance, loss-of-signal mask counter, RX data-enable override counters, off-cancel/adaptation continuous status, and RX UPCS OCLA gating.
- `DPCSSYS_CR3_RAWLANE3_DIG_PCS_XF_ATE_*` and related PCS transfer fields: ATE/test override inputs for RX and TX rate, width, pstate, LPD, MPLL selection/enables, master MPLL override, async TX enable, TX presets, TX/RX termination, TX/RX load-value overrides, CTLE boost, and PI-related override controls.
- `DPCSSYS_CR3_RAWAONLANE0_DIG_*` through `DPCSSYS_CR3_RAWAONLANE3_DIG_*`: four repeated always-on lane blocks. Each block defines analog calibration, adaptation, status, override, signal-detect, DCC, firmware configuration, and lane transceiver-mode fields.
- `DPCSSYS_CR3_RAWAONLANEX_DIG_*`: shared or lane-X always-on field definitions beginning near the end of the chunk. The range includes AFE/DFE offset and RX phase/adaptation fields and stops before the register is complete.

The always-on lane block is the largest surface in this range. Each concrete lane instance includes masks/shifts for AFE attenuation and CTLE IDAC offsets; RX IQ adaptation and FOM; DFE summer, phase, data, bypass, and error VDAC offsets; even/odd reference levels; linear and mapped phase-adjust values; MPLLA/MPLLB coarse tune; initial power-up done; RX ATT/VGA/CTLE/DFE tap adaptation values; RX adaptation done; fast flags; slicer controls; MPLL/RCAL common-calibration status; adaptation control words; MPLL disable; TX/RX override inputs; LOS and signal-detect filters; stats; RX override output groups; signal-detect calibration/code registers; VREF generator enable; calibration code registers; RX DCC calibration code registers; TX DCC bank address/data/control; MPLL bandgap timing; firmware MM/adaptation/calibration config; lane transceiver-mode override/readback; RX signal-detect config; and TX DCC config.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to AMDGPU's register access layer:

1. `dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and this matching `dpcs/dpcs_4_2_0_sh_mask.h`.
2. Resource and link-encoder table macros use token-pasting helpers such as `REG`, `SRI`, `SRI_IX`, `LE_SF`, and related shift/mask list macros to combine register offsets from the offset header with field positions from this header.
3. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use those tables to access hardware registers.

The macros in this chunk do not decide sequencing. PHY reset, request/ack handshakes, retuning, RX adaptation, TX/RX clock selection, ATE override use, signal-detect filtering, and DCC/calibration programming are controlled by display driver code, firmware, and silicon behavior outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state and control fields:

- Lane-3 PMA/PCS/TX/RX override and handshake state, including request/reset/data-enable overrides, loopback controls, RX/TX PMA ack, retune request/ack, RX termination overrides, async and PWM controls, TX clock controls, RX/TX state-machine controls, and test/ATE override values.
- Per-lane always-on PHY state for lane calibration and adaptation, including analog offsets, DFE references, RX phase adjustment, MPLL coarse tune, RX adaptation completion/status, fast startup flags, common calibration status, adaptation control storage, LOS/signal-detect behavior, and DCC calibration data.
- Firmware and microcode-facing configuration fields such as firmware MM/adaptation/calibration words, lane transceiver-mode override/readback, TX DCC bank access, and signal-detect tuning.

Persistence and side effects are hardware-defined. Configuration bits may survive until display modeset, PHY power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, ack, done, calibration, and signal-detect fields may be read-only, latched, self-clearing, or valid only while the relevant DPCS lane and always-on power island are powered and clocked. This file only supplies bit locations; it does not encode access direction or lifetime semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies the matching register offsets. For this range, lane-3 PMA/TX/RX/PCS offsets include `ixDPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_PMA_IN` through `ixDPCSSYS_CR3_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN_2`, and always-on lane offsets run in repeated `0x4000`, `0x4100`, `0x4200`, and `0x4300` bands for lanes 0-3.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` directly includes this header and builds DCN 3.1 register shift/mask tables. In particular, link-encoder masks combine `LINK_ENCODER_MASK_SH_LIST_DCN31` with `DPCS_DCN31_MASK_SH_LIST`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` and inherited DCN2/DCN3 link-encoder field-list patterns are the style of consumers that rely on DPCS register macros for link PHY programming, even when many shared field lists use canonical RDPCSTX names rather than the raw-lane names in this exact slice.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and `.c` consume DPCS/RDPCS-style offset and mask tables for high-performance DP link encoder register access.
- Adjacent generated headers for DPCS 4.2.2, DPCS 4.2.3, and DCN 4.1.0 expose closely related field names, which are useful for generator consistency comparisons but are not substitutes for this ASIC-specific file.

Behaviorally, these fields sit under display link bring-up, PHY lane power/control, link training, signal detection, runtime retuning, debug/test overrides, and calibration telemetry for DPCS CR3.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly and corrupt only one hardware bitfield at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, `dpcs_4_2_0_offset.h`, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are only the ending masks for `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT`, and the final line is only the first shift definition for `DPCSSYS_CR3_RAWAONLANEX_DIG_DFE_DATA_EVEN_LOW_VDAC_OFST`.
- Lane and instance repetition is copy-sensitive. The `RAWAONLANE0` through `RAWAONLANE3` blocks should be structurally aligned where hardware intends; a generator drift can affect only one physical lane or only CR3.
- Request/ack and done bits are sequencing-sensitive. Bad definitions for PMA ack, retune ack, adaptation done, power-up done, calibration status, or common-calibration state can cause timeouts, false readiness, or link bring-up hangs.
- Override-enable fields can force the PHY away from normal hardware/firmware control. Incorrect masks for RX/TX request, reset, data-enable, loopback, PLL, async, termination, or phase overrides can break link training, cause blank displays, or leave lanes stuck after suspend/resume.
- Signal-detect, LOS mask, VREF, DFE, CTLE, VGA, ATT, RX phase, and DCC fields affect analog behavior. Errors may show up only with specific lane rates, cables, sinks, boards, voltage/temperature corners, or marginal signal integrity.
- The `data`/`DATA` field spelling varies across generated ASIC headers. Consumers that token-paste exact field names must use the names from the included ASIC generation, not names from nearby DPCS/DCN versions.
- Reserved bits are widely represented. Driver code should avoid treating reserved masks as available controls unless the hardware programming guide or firmware handoff explicitly requires it.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build DCN 3.1 AMDGPU display support. Missing or renamed macros should surface in `dcn31_resource.c`, DPCS link-encoder mask/shift tables, and HPO DP link encoder users.
- Mechanically compare this range against the authoritative DPCS 4.2.0 register-field database and ensure every complete register field has a consistent `__SHIFT`/`_MASK` pair, allowing the split first and last registers.
- Cross-check the shift/mask register names against `dpcs_4_2_0_offset.h` so every lane-3 PMA/TX/RX/PCS and always-on lane register has a matching offset.
- Run repetition checks across `DPCSSYS_CR3_RAWAONLANE0` through `DPCSSYS_CR3_RAWAONLANE3` to catch unintended field drift while allowing intentional lane-specific offsets.
- Compare related DPCS 4.2.2/4.2.3 and DCN 4.1.0 generated headers for expected naming, mask-width, and reserved-field differences.
- Exercise DP/HDMI link bring-up across all lanes and link rates exposed by CR3 hardware. Watch for request/ack timeouts, RX adaptation failures, retune failures, stuck data-enable/reset bits, and unstable signal detect.
- Test hotplug, modeset, blank/unblank, suspend/resume, and GPU reset paths on systems using this ASIC generation, with attention to lane power-up done, adaptation done, common-calibration status, and restoration of override controls.
- Use hardware register dumps around failed link training to verify TX/RX clock selection, PMA/PCS overrides, RX adaptation values, DFE/CTLE/VGA/ATT values, signal-detect filters, and DCC calibration fields decode as expected with these masks.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT` and earlier CR3 raw-lane-3 PMA fields. This chunk continues through lane-3 PMA/TX/RX/PCS transfer fields and the full repeated always-on lane 0-3 blocks, then starts the shared `RAWAONLANEX` block. The next chunk should complete `DPCSSYS_CR3_RAWAONLANEX_DIG_DFE_DATA_EVEN_LOW_VDAC_OFST` and the remaining shared lane-X always-on definitions. The final per-file research document should reconcile those boundaries before making whole-register or whole-file claims.

### subset-b-002321: lines 78684-81059

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 78684-81059

## Purpose

This chunk is generated AMD DPCS 4.2.0 register field metadata for the `DPCSSYS_CR3` display PHY/control-register space. It contains no executable C logic; it exports preprocessor constants that describe bit positions and bit masks for 245 hardware register blocks in one oversized header. The chunk has 2,132 `#define` entries: 1,066 `__SHIFT` constants and 1,066 matching `_MASK` constants.

The visible register groups cover three related CR3 hardware regions:

- `DPCSSYS_CR3_RAWAONLANEX_*`: raw always-on lane digital fields for RX DFE/adaptation, signal detection, calibration, TX/RX disable overrides, firmware calibration/adaptation configuration, lane transceiver mode, and TX/RX DCC controls.
- `DPCSSYS_CR3_SUPX_*`: supervisor/common PHY fields for ID codes, refclock/bandgap controls, MPLLA/MPLLB dividers, HDMI clocking, spread-spectrum clocking, fractional-N PLL values, charge-pump values, ASIC input mirrors, analog bandgap/prescaler/RTUNE controls, MPLL power-control status/timers/calibration, RTUNE status/config counters, and analog override outputs.
- `DPCSSYS_CR3_LANEX_*`: lane-level digital/ASIC TX and RX override/mirror fields, loopback, AC JTAG, TX request/pstate/rate/width/data-enable/drive controls, RX CDR/VCO/equalizer/termination controls, lane-master and repeat/shift handshakes, OCLA gates, and TX power-state programming for P0, P0s, P1, and the beginning of P2.

The source tree path is under a local `ceph-client` mirror, but this file is AMDGPU display-driver hardware metadata rather than distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, local includes, allocations, or locks in this chunk. The API surface is the generated macro namespace:

- `DPCSSYS_CR3_<register>__<field>__SHIFT`: the bit offset of a field within a DPCS register.
- `DPCSSYS_CR3_<register>__<field>_MASK`: the bit mask for the same field.

Every field visible in this range has both a shift and a mask definition. The largest complete register block in the chunk is `DPCSSYS_CR3_RAWAONLANEX_DIG_FAST_FLAGS`, with 16 fields and 32 generated macro lines. Common field shapes include single-bit enable/value pairs, multi-bit numeric fields such as DFE tap values, PLL multipliers, fractional-N values, RTUNE values, TX main/pre/post cursors, RX VCO load values, pstate/rate/width selectors, and many `RESERVED_*` masks that protect unused upper bits.

Important macro families in this slice include:

- DFE, RX adaptation, and fast-calibration controls: `DIG_DFE_*_VDAC_OFST`, `DIG_RX_ADPT_*`, `DIG_RX_ADAPT_DONE`, `DIG_FAST_FLAGS`, and `DIG_FAST_FLAGS_2`.
- Signal detection and RX analog controls: `DIG_RX_LOS_MASK_CTL`, `DIG_RX_SIGDET_*`, `DIG_RX_OVRD_OUT_*`, `DIG_SIGDET_OUT_*`, and `DIG_RX_VREFGEN_EN`.
- Calibration and DCC fields: `DIG_CAL_*`, `DIG_RX_DCC_CAL_*`, `DIG_TX_DCC_*`, `DIG_MPLL_BG_CTL`, `DIG_LANE_CMNCAL_*_STATUS`, and `DIG_MPLL_DISABLE`.
- Firmware and lane-mode fields: `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, `DIG_FW_CALIB_CONFIG`, `DIG_LANE_XCVR_MODE_*`, and `DIG_TXRX_OVRD_IN`.
- Supervisor PLL/refclock fields: `SUPX_DIG_REFCLK_OVRD_IN`, `SUPX_DIG_MPLLA_*`, `SUPX_DIG_MPLLB_*`, `SUPX_DIG_ASIC_IN`, `SUPX_DIG_LVL_ASIC_IN`, charge-pump fields, SSC peak/stepsize fields, and HDMI/divider clock fields.
- Analog supervisor fields: `SUPX_ANA_PRESCALER_CTRL`, `SUPX_ANA_RTUNE_CTRL`, `SUPX_ANA_BG*`, `SUPX_ANA_MPLLA_*`, `SUPX_ANA_MPLLB_*`, plus digital analog override outputs such as `SUPX_DIG_ANA_MPLLA_OVRD_OUT_*`, `SUPX_DIG_ANA_MPLLB_OVRD_OUT_*`, `SUPX_DIG_ANA_RTUNE_OVRD_OUT`, and `SUPX_DIG_ANA_BG_OVRD_OUT`.
- Lane TX/RX fields: `LANEX_DIG_ASIC_LANE_*`, `LANEX_DIG_ASIC_TX_*`, `LANEX_DIG_ASIC_RX_*`, `LANEX_DIG_ASIC_RX_EQ_*`, `LANEX_DIG_ASIC_RX_CDR_VCO_*`, and `LANEX_DIG_TX_PWRCTL_TX_PSTATE_*`.

## Control Flow

This chunk has no runtime control flow. The runtime sequence is supplied by AMD display code that includes the matching offset and mask headers and then token-pastes register and field names into register helper tables.

The observed integration path for this specific header is `display/dc/resource/dcn31/dcn31_resource.c`, which includes both `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`. That file materializes `DPCS_DCN31_REG_LIST(id)` into link encoder register tables and appends `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` / `DPCS_DCN31_MASK_SH_LIST(_MASK)` to the link encoder shift and mask tables. The helper pattern in display code then feeds `REG_GET`, `REG_SET`, `REG_UPDATE`, and related macros with register offsets from the offset header and field metadata from this mask header.

The constants in this chunk do not encode hardware sequencing. Consumers still must order refclock, bandgap, PLL, RTUNE, TX/RX power state, lane width/rate, DFE/adaptation, signal detection, and calibration programming according to the link encoder and PHY initialization flows.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state. The represented state is broad:

- RX equalization/adaptation state, including DFE tap values, CTLE/VGA/ATT adaptation results, slicer controls, bypass/error values, RX IQ phase adjustment, RX adaptation-done flags, and fast-start/continuous calibration flags.
- Calibration and signal-detection state, including LOS mask counters, HF/LF signal-detect filters and thresholds, signal-detect override inputs/outputs, DCC calibration codes, TX DCC bank address/data/continuous enable, RTUNE set/status/config counters, and supervisor analog compare/status bits.
- Clocking and PLL state for MPLLA/MPLLB, including coarse tune, disable flags, divider/HDMI clock controls, PLL enable/standby/reset/calibration bits, fractional-N quotient/remainder/denominator fields, SSC peak/stepsize fields, charge-pump proportional/integral fields, power-control status, timers, DAC max range, and spread type.
- Analog supervisor state, including bandgap selections, prescaler and RTUNE analog controls, MPLL analog miscellaneous/control/test/ATB fields, analog override outputs, PMIX controls, and bandgap/reset/ref-vreg override outputs.
- Lane TX/RX state, including loopback/ACJTAG controls, TX request/pstate/rate/width/data-enable/disable/beacon/cursor/HDMI mode/DC-coupling/reset fields, RX request/data/pstate/rate/width/CDR/SSC/align/termination/PWM/equalizer fields, lane master/repeater shift handshakes, and TX P0/P0s/P1/P2 power-state enable/reset/data/RX-detect/VBOOST/DCC-cal bits.

Persistence is entirely hardware-defined. Some fields are configuration bits that likely retain values until modeset, power gating, suspend/resume, or reset; others are status, mirror, calibration-result, override-enable, or self-clearing/handshake bits. The header does not identify access direction or side effects, so any read/modify/write behavior must be inferred from hardware programming guides and consuming driver code.

## Dependencies And Integration Points

This chunk depends on consistency with adjacent generated AMD register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies the matching `ixDPCSSYS_CR3_*` register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` macros that select DPCS fields for link encoder register structs.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes this file and builds the concrete DCN 3.1 link encoder register, shift, and mask tables.
- The display register helper layer consumes the resulting tables through token-pasted field names and helper macros such as `FD`, `FN`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

The chunk is part of a generated family. Searches show equivalent register names in related `dpcs_4_2_2`, `dpcs_4_2_3`, and broader `dcn_4_1_0` mask headers, sometimes with different masks or reserved layouts. That makes ASIC-version pairing important: the 4.2.0 offset and shift/mask headers should be used together, not mixed with another revision.

## Risks And Edge Cases

- Bitfield drift is the central risk. These are untyped preprocessor constants, so a wrong shift/mask can compile cleanly while corrupting adjacent fields or programming the wrong hardware behavior.
- Offset/mask version mismatches are dangerous. The register offsets live in `dpcs_4_2_0_offset.h`, while this chunk only supplies field layout; mixing revisions can silently target valid offsets with invalid bit layouts.
- Many fields affect live PHY behavior: PLL enable/reset/calibration, refclock/bandgap control, RTUNE, TX/RX pstate/rate/width, TX drive cursors, RX CDR/VCO/equalizer settings, signal detect, loopback, and lane master/shift handshakes. Incorrect values can cause link-training failures, blank display, intermittent hotplug, poor signal margin, audio/video instability over HDMI/DP, or resume failures.
- Override fields commonly have value and enable bits. Setting an override value without the matching enable, or leaving an enable asserted after calibration/debug use, can create mode-specific or board-specific failures.
- Reserved masks are present throughout the chunk. Read/modify/write helpers should preserve reserved bits unless the hardware programming sequence explicitly requires otherwise.
- The chunk boundaries are artificial. The first lines continue the tail of `DPCSSYS_CR3_RAWAONLANEX_DIG_DFE_DATA_EVEN_LOW_VDAC_OFST` from the previous chunk, and the final line stops at the `TX_P2_ANA_DCC_COMP_CAL_EN_MASK` field before the trailing reserved mask for `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P2`.

## Test Signals

Because this file is generated metadata, direct unit tests are unlikely. Useful validation signals are compile-time and hardware-path oriented:

- Build coverage for AMDGPU display configurations that include DCN 3.1 resources; missing or renamed macros should fail when `dcn31_resource.c` expands the DPCS register and mask lists.
- Static consistency checks can verify each visible `__SHIFT` macro has a matching `_MASK` macro and that the selected field names match the register/mask list declarations in `dcn31_dio_link_encoder.h`.
- ASIC-version checks should ensure `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h` are paired in include sites.
- Runtime display smoke tests should cover DP and HDMI link bring-up, link training across lane counts and rates, hotplug/EDID, suspend/resume, MST where applicable, and modes that exercise TX power states P0/P0s/P1/P2.
- Hardware debug signals include DPCS register dumps before and after link training, PLL lock/calibration status, RTUNE status, signal-detect outputs, RX adaptation done/status, and comparison against known-good register dumps for the same ASIC revision.

### subset-b-002322: lines 81060-83443

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 81060-83443

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It covers lines 81060-83443 and defines 2,118 preprocessor constants: 1,064 `__SHIFT` macros and 1,054 `_MASK` macros. The mismatch is expected for this exact slice because it starts with the final mask of `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P2` and ends inside the shift half of `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`, before that register's masks.

The content is declarative hardware metadata. There are no C functions, structs, enums, branches, loops, allocation paths, locks, direct MMIO accesses, or local software state. The public surface is the macro namespace consumed by AMDGPU/DC register helpers together with the matching DPCS offset header.

## Purpose

The header provides symbolic bit positions for DPCS 4.2.0 display PHY registers. Each hardware field is represented by a shift and a mask so callers can compose, update, and decode register values without hard-coding raw bit constants.

This range covers the late CR3 lane transceiver block. It begins at lane-X TX power sequencing, then covers CR3 lane-X RX power sequencing, RX VCO calibration, RX CDR/DPLL/adaptation/statistics, MPHY controls, digital analog TX/RX overrides, analog TX/RX controls and test-bus fields, raw memory placeholders, raw PCS lane interface fields, raw lane FSM status/fast-path controls, raw lane IRQ status/clear/mask registers, and ends in raw PMA TX override output fields.

## Important APIs, Types, And Macros

There are no callable APIs or local data types. The effective API is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset.
- `<REGISTER>__<FIELD>_MASK`: field mask for extraction, clearing, or insertion.

Important macro families in this chunk:

- `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_*`: TX P2 reserved tail, TX power-up timing, DCC CR-bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT control.
- `DPCSSYS_CR3_LANEX_DIG_RX_PWRCTL_*`: RX P0/P0S/P1/P2 power-state tables and RX power-up timing. Fields describe AFE, clock regulator, clock, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clock, equalization, adaptation, and DFE enables.
- `DPCSSYS_CR3_LANEX_DIG_RX_VCOCAL_*`: RX VCO calibration control, timing, calibration interval/sequence settings, and status fields such as calibration done, low-frequency indication, VCO code, reference code, and thermometer-like state.
- `DPCSSYS_CR3_LANEX_DIG_RX_CDR_*` and `DPCSSYS_CR3_LANEX_DIG_RX_DPLL_*`: CDR tuning/status and DPLL frequency/bounds fields.
- `DPCSSYS_CR3_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset, ATT/VGA/CTLE/DFE tap status, slicer controls, DFE data/error offsets, error slicer level, DAC control selectors, and CR bank address/data.
- `DPCSSYS_CR3_LANEX_DIG_RX_STAT_*`: programmable RX status/match/statistics controls, data masks, load values, sample count, multiple statistic counters, comparator clock control, and stop control.
- `DPCSSYS_CR3_LANEX_DIG_MPHY_*`: MPHY RX PWM, low-speed termination, and analog PWM clock-stable count fields.
- `DPCSSYS_CR3_LANEX_DIG_ANA_*`: digital override and readback-facing analog fields for TX/RX power/control, term code, TX equalization, RX VCO, calibration, DAC, AFE ATT/VGA/CTLE, RX scope, slicer, IQ phase/sense, signal-change clocks, analog status, MPHY override, signal detect, and TX DCC DAC.
- `DPCSSYS_CR3_LANEX_ANA_TX_*` and `DPCSSYS_CR3_LANEX_ANA_RX_*`: direct analog TX/RX register field maps for power override, measurement/test buses, DCC DAC, termination code, override clocks, TX misc/reserved fields, RX clocks, CDR/deserializer, slicer, power, squelch, calibration, analog test buses, and reserved RX fields.
- `DPCSSYS_CR3_RAWMEM_*`: raw ROM/RAM common memory field placeholders.
- `DPCSSYS_CR3_RAWLANEX_DIG_PCS_XF_*`: raw PCS interface override/input/output fields for TX, RX, ATE, adaptation ack/FOM, equalization requests, lane number, termination control, and phase-2 calibration.
- `DPCSSYS_CR3_RAWLANEX_DIG_FSM_*`: raw finite-state-machine override/status, memory monitor, fast RX/TX calibration/adaptation step controls, flags, common calibration status, DCC status, OCLA, TX EQ update, RCAL status, and IQ phase offset fields.
- `DPCSSYS_CR3_RAWLANEX_DIG_IRQ_CTL_*`: raw lane IRQ status, clear, reset-return request, IRQ masks, and second TX IRQ mask register for RX/TX reset/request/rate/pstate/adaptation, lane mode, phase-2 calibration, loopback, and DCC on-demand events.
- `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_*`: raw PMA interface override and PMA input fields for lane MPLL A/B enables, supervisor MPLL state, and the beginning of TX override output values/enables.

## Register Areas Covered

The `LANEX_DIG_TX_PWRCTL` region describes lane-X TX sequencing rather than a single immediate register write. Timing fields cover refgen enable, TX clock enable, VCM hold, VBOOST disable, RX detect, reset, serial enable, fast RX detect, and skip bits. DCC bank/DAC fields indicate indexed access and handshake around TX DCC calibration or compensation.

The `LANEX_DIG_RX_PWRCTL`, `RX_VCOCAL`, `RX_CDR`, `RX_DPLL`, and `RX_ADPTCTL` regions define the core RX bring-up and training controls. The power-state tables identify which analog/digital subblocks are enabled for each state. VCO calibration and CDR/DPLL fields expose lock/tracking configuration and readback. Adaptation fields carry the programmable knobs and observed results for ATT, VGA, CTLE, DFE taps, slicers, DAC selectors, and reset behavior.

The `RX_STAT` region is a diagnostic counter/match engine. It can load compare values, mask received data, select match/stat modes, count samples, expose several counter registers, gate comparator clocks, and stop statistic collection. This makes it a validation/debug surface rather than normal display-mode state alone.

The digital analog and direct analog regions bridge software-visible DPCS logic to analog PHY behavior. They include override enables and values for TX/RX resets, clocks, term codes, equalization, VCO/CDR signals, calibration DACs, signal detect, MPHY, and test-bus measurement fields. The paired status fields are readback surfaces for analog state and calibration observations.

The raw PCS/FSM/IRQ/PMA regions expose lower-level hardware interfaces beneath the higher-level lane-X register map. They are useful for debug, manufacturing validation, OCLA observation, fast calibration sequencing, interrupt handling, and PMA boundary override/readback. The range ends before the masks for `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`, so the next chunk owns the remainder of that register.

## Control Flow

This header has no local control flow. Runtime control flow is implied by how AMDGPU display code uses generated offset and shift/mask headers:

1. Select DCN 3.1 resource code, which includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`.
2. Pair `ixDPCSSYS_CR3_*` offsets from the offset header with these `DPCSSYS_CR3_*__SHIFT` and `_MASK` constants.
3. Use register helper macros and DC link/PHY code to compose read-modify-write values, program power-state/timing/adaptation tables, read live status, poll calibration/ack bits, or clear/mask IRQs.
4. Let hardware execute the real TX/RX power, reset, calibration, adaptation, FSM, and interrupt behavior.

The header does not encode ordering. Callers must follow the hardware sequencing rules for reset, clock enable, pstate changes, CDR/VCO calibration, DCC DAC handshakes, adaptation reset, statistics clear/stop, IRQ clear, and PMA/PCS overrides.

## State And Persistence Behavior

No software state is stored here. The macros describe fields whose values live in hardware registers.

- Power-state and timing fields persist programmed TX/RX lane behavior until later writes, reset, or power-domain loss.
- Override fields can force analog, PCS, FSM, PMA, TX, RX, loopback, term-code, data-enable, reset, request, calibration, and signal-detect behavior while their corresponding override-enable bits remain set.
- Status, IRQ, counter, ACK, FOM, VCO, CDR, DPLL, adaptation, analog, and FSM fields expose live or latched hardware state.
- Clear, stop, update-clock, request, and handshake fields may have side effects or self-clearing semantics defined by the hardware specification, not by this generated header.
- Reserved fields are part of the register layout but should be preserved and not used as software-owned storage.

The file does not define reset values, retention across suspend/resume, or which fields are read-only/write-only. Those properties must come from the ASIC register database and consumer code.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which defines matching `ixDPCSSYS_CR3_*` register offsets. For this slice, the offset range runs from the CR3 lane-X TX power-control registers around `0x9024` through raw lane PMA/PCS/FSM/IRQ/PMA registers around `0xe000+`.

The observed in-tree include point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes both `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`. That resource file uses AMD DC register helper conventions that token-paste register and field names into offset, shift, and mask constants.

Likely consumers are AMDGPU DC link encoder, PHY, link-training, display power, diagnostics, and interrupt paths for DCN 3.1 ASICs using DPCS 4.2.0. The same generated naming scheme appears in sibling DPCS/DCN ASIC headers, so the exact ASIC generation matters even when names look structurally similar.

## Risks And Edge Cases

- Generated-header drift is high impact: an incorrect mask or shift can compile successfully while writing the wrong silicon bit.
- This chunk begins and ends mid-register. The previous chunk owns most of `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P2`; the next chunk owns the rest of `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`.
- The register surface mixes writable configuration, read-only status, latched IRQ status, write-to-clear bits, stop/update controls, counters, override enables, and reserved fields. Treating all fields as ordinary writable configuration can clear status, leave forced overrides active, or corrupt reserved bits.
- TX/RX power, reset, clock, VCO, CDR, DPLL, DCC, adaptation, and PMA/PCS override fields are sequencing-sensitive. Writes at the wrong link-training or display-active phase can cause link loss, failed training, flicker, or hardware hangs.
- CR bank address/data fields imply indexed internal state. Callers need strict address/data ordering and should avoid concurrent or interleaved bank access without the relevant hardware locking/serialization.
- The raw lane/FSM/IRQ/PMA regions expose low-level debug and validation controls. They are powerful enough to bypass normal hardware ownership and should be restored to non-override operation after use.
- Reserved masks are present for completeness but do not make reserved bits safe to write. Consumers should preserve existing reserved values unless the hardware spec explicitly says otherwise.

## Test Signals

Useful validation signals for this chunk are build-time, generated-header, and hardware-integration oriented:

- Compile/preprocess DCN 3.1 AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`; missing or renamed fields should fail in register helper users.
- Mechanical checks that all complete register groups have paired `__SHIFT` and `_MASK` definitions. For this exact slice, expect 2,118 defines, 1,064 shifts, and 1,054 masks because of the partial start/end registers.
- Diff this header against the authoritative AMD DPCS 4.2.0 register database and the matching `dpcs_4_2_0_offset.h`.
- Cross-check sibling DPCS 4.2.x/DCN headers only where the IP block is expected to be compatible; similar names do not prove identical bit layout.
- Runtime validation on DPCS 4.2.0/DCN 3.1 hardware: DP/HDMI link training, link-rate and lane-count changes, hotplug, suspend/resume, GPU reset recovery, low-power transitions, and DP Alt Mode attach/detach where applicable.
- Register readback during link bring-up should show expected movement through TX/RX request/ack, reset, pstate, power-up timing, VCO calibration, CDR/DPLL tuning, DCC calibration, RX adaptation, and FSM fast-path status.
- IRQ tests should exercise RX/TX reset/request/rate/pstate/adaptation, lane mode, phase-2 calibration, loopback, and DCC on-demand status/mask/clear behavior.
- Diagnostic tests should cover LBERT, OCLA, RX statistic counters, analog test bus, MPHY controls, signal detect overrides, PMA/PCS overrides, and cleanup that returns override-enable bits to hardware ownership.

## Chunk Notes For Merge

This document intentionally covers only lines 81060-83443 of `dpcs_4_2_0_sh_mask.h`. The final per-file report should merge it with adjacent chunks for the full generated DPCS 4.2.0 field map. Reconciliation should note that this chunk begins with the last mask of `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P2` and ends after `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT__TX_DWORD_CLK_SYNC_OVRD_VAL__SHIFT`, before the remaining shifts and masks for that PMA TX override register.

### subset-b-002323: lines 83444-85815

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 83444-85815

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY and lane-control register fields. It contains no executable logic; its exported surface is preprocessor metadata that maps hardware register fields to bit positions (`__SHIFT`) and bit masks (`_MASK`) for AMDGPU display register helpers.

The requested range contains 2,136 `#define` entries over 2,372 source lines and 234 register comment markers. It begins inside `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`, after several of that register's shift definitions have already appeared in the previous chunk, and then covers the rest of the CR3 raw-lane PMA/PCS, TX/RX control, ATE override, and MPLL-loop definitions. It then enters `addressBlock: dpcssys_cr4_rdpcstxcrind`, covering CR4 supervisor, MPLL, bandgap, RTUNE, ASIC interface, lane0 TX power/DCC, RX statistics, and lane0 analog TX equalization/status fields through `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0`.

Although the source path is under a local `ceph-client` tree, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The only public interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for extracting or updating that field.

The main register-field families in this chunk are:

- CR3 raw-lane PMA cross-interface controls: TX/RX override values and enable bits, PMA request/reset/data-enable handshakes, PMA ACK inputs, lane TX-to-RX and RX-to-TX loopback enables, RTUNE request/ACK, MPHY PWM/term/async overrides, RX adaptation phase-map override, and PMA data/clock enable controls.
- CR3 raw-lane TX/RX control: TX FSM timing and receive-detect permission in P-states, TX clock enables/selectors, DCC continuous-status enables, OCLA observation controls, RX FSM enable/rate-change controls, loss-of-signal mask counters, RX data-enable override counters, off-cancel/adaptation continuous-status flags, and UPCS OCLA data/clock gates.
- CR3 PCS/ATE override controls: RX/TX rate, width, pstate, reset, beacon, async, data-enable, DETRX, VBOOST, IBOOST, loopback, LOS/LFPS threshold, adaptation/off-cancel continuous control, VCO/ref load overrides, RX-valid override, master MPLLA/MPLLB loop enables, and TX/RX override fields used for automated test or forced-lane operation.
- CR4 supervisor digital controls: ID-code registers, reference clock and MPLLA/MPLLB divided/HDMI clock override inputs, MPLLA/MPLLB fractional-N, SSC, divider, multiplier, enable, reset, prescaler, charge-pump, gain-switch, level, ASIC-input, bandgap, and supervisor override/output fields.
- CR4 supervisor analog controls: prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB miscellaneous, override, ATB, control, and reserved analog fields, plus digital MPLL power-control status, timers, calibration, DAC range/output, SSC spread type, clock/reset power-up timers, RTUNE configuration/status/set/stat/code fields, and analog override/status outputs.
- CR4 lane0 ASIC interface and TX power controls: lane/TX/RX ASIC override inputs/outputs, lane ASIC status, TX pstate definitions for P0/P0s/P1/P2, TX power-up timers, DCC CR bank address/data, DCC DAC control/range/select/ACK/address, TX clock alignment, and LBERT control.
- CR4 lane0 RX statistics controls: load/data masks, pattern match and mask registers, statistic control enables, sample counters, statistic counters 0-6, calibration comparison clock control, second match-register set, statistic-stop control, valid-loss clearing, pause/clock enable, data-delay, and sample-done indicators.
- CR4 lane0 analog TX controls and status: analog TX clock/data/refgen/VCM/word-clock/MPLL/reset/serial/rate/RX-detect override bits, TX termination code and drive-source override, termination clock self-clear control, TX equalization load/leg-pull/mux/pre/post/direction fields, and status bits for clock-shift ACK, RXDET results, loopback, RX calibration, scope data, TX DCC calibration, and EQ mux readback.

Most fields are 16-bit register slices with paired shift and mask definitions. Some fields span multiple registers by suffix, such as `MPLLA_FRACN_QUOT_31_16`/`15_0`, `MPLLA_SSC_PEAK_31_16`/`15_0`, and TX equalization leg-pull fields split across `_0` through `_5`.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to the AMDGPU display stack:

1. DPCS 4.2.0 register address metadata comes from the companion `dpcs_4_2_0_offset.h` file.
2. This file supplies matching field shifts and masks for those registers.
3. DCN resource and link-encoder code token-pastes register, shift, and mask names into register tables.
4. Runtime display code uses those tables through AMD register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
5. Hardware sequencing for PHY reset, clock selection, PLL programming, pstate changes, lane power, AUX/ATE forcing, RX adaptation, statistics collection, and analog calibration lives outside this generated header.

The macro names describe field location only. They do not encode access semantics such as read-only status, write-one-to-clear behavior, self-clearing bits, sticky bits, reserved-bit policy, or required ordering between writes.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on its own. It names hardware-visible state in CR3 and CR4 DPCS/PHY registers:

- CR3 PMA/PCS override state includes forced request/reset/data-enable values, override-enable bits, TX/RX loopback state, PMA/RTUNE ACK status, MPHY PWM and termination control, RX phase-map adaptation override, rate/width/pstate forcing, DETRX/VBOOST/IBOOST forcing, LOS/LFPS/adaptation controls, VCO/ref load overrides, and RX-valid forcing.
- CR3 TX/RX control state includes FSM enable/timing bits, TX clock enable/source selection, RXDET permission by power state, DCC/off-cancel/adaptation continuous-status enables, RX LOS masking, and OCLA/UPCS observation gates.
- CR4 supervisor state includes MPLLA/MPLLB clocking, SSC, fractional-N, dividers, multipliers, enable/reset/power state, charge-pump/gain-switch tuning, bandgap and prescaler controls, RTUNE set/stat/calibration state, and power-up/timing thresholds.
- CR4 lane0 state includes ASIC override/in/out buses, TX pstate and power-up timing, DCC CR bank access, DAC tuning and ACK state, TX clock alignment, LBERT control, RX statistic match/counter/sample state, and analog TX override/equalization/termination/status readbacks.

Persistence is hardware-defined. Configuration fields generally remain until link reprogramming, modeset, suspend/resume, power-gating, GPU reset, ASIC reset, or explicit driver reinitialization changes them. Status and handshake fields may be transient, latched, clear-on-write, self-clearing, sampled only under an active clock domain, or invalid while PHY power is gated. The header itself does not distinguish these cases.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` provides matching `ix...` register offsets for the shift/mask names in this file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes the DPCS 4.2.0 offset and shift/mask headers when initializing DCN 3.1 display resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines DPCS/DCN31 register-list and mask/shift-list macros that consume these generated names.
- Low-level display link, PHY, PLL, lane-training, hotplug/AUX/DDC, diagnostics, and hardware-sequencing code consumes the initialized tables indirectly.

The fields in this chunk sit below the higher-level display pipeline. They provide locations for operations such as forcing or observing lane handshakes, programming MPLL and SSC parameters, controlling PHY power and clocking, running RTUNE and DCC calibration, collecting RX statistics, applying TX equalization/termination settings, and reading analog TX/RX status.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly while causing the driver to update the wrong field or corrupt adjacent reserved bits.
- The chunk starts mid-register: the first visible lines are late shift definitions for `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`; earlier shifts and the register comment are in the preceding chunk. Whole-register analysis must reconcile both chunks.
- CR3 and CR4 raw-lane/register-bank layouts are highly repetitive. Copy/generator errors can affect only one lane, PLL, or transmitter path, producing port-specific failures that are hard to reproduce.
- PLL, SSC, divider, multiplier, charge-pump, gain-switch, bandgap, power-up timer, RTUNE, DCC, and analog equalization fields are timing- and silicon-sensitive. Incorrect field definitions can cause link-training failures, unstable clocks, blank displays, excessive bit errors, bad resume behavior, or calibration timeouts.
- Override-enable and override-value pairs must be handled carefully. Setting a value bit without the corresponding enable bit, or enabling an override with a stale value, can force unexpected PHY state.
- Status, ACK, IRQ-like, statistic-done, and calibration-result fields may be read-only, latched, or dependent on active power/clock domains. Treating them like ordinary writable configuration fields can hide real hardware state or clear diagnostics.
- RX statistic and LBERT fields are diagnostic/test-oriented. Incorrect masks can make hardware validation appear to pass or fail incorrectly even when link operation is otherwise unchanged.
- Reserved fields are numerous. Generic register writes must preserve reserved bits unless hardware documentation explicitly requires programming them.
- Manual edits to this generated header risk divergence from AMD's authoritative register source, the offset header, firmware assumptions, and silicon documentation.

## Test Signals

Useful validation should combine generated-header checks and hardware behavior:

- Build AMDGPU display support with DCN 3.1 enabled. Missing or renamed macros should fail where DPCS 4.2.0 register, shift, and mask tables are assembled.
- Mechanically verify that complete fields in this range have paired `__SHIFT` and `_MASK` definitions, allowing for the known starting boundary where `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT` begins before line 83444.
- Cross-check the register names in this chunk against `dpcs_4_2_0_offset.h` and AMD's source register database.
- Diff CR3/CR4 replicated lane and PLL field layouts against neighboring generated DPCS/DCN headers where the hardware specification expects matching fields.
- Exercise DisplayPort and HDMI link bring-up on ports mapped to the affected DPCS/UNIPHY instances. Watch for stable link training, correct PLL lock behavior, expected lane request/ACK transitions, and no recurring RX/TX calibration failures.
- Run modeset, stream disable/enable, hotplug, suspend/resume, GPU reset, and power-gating tests to catch stale pstate, clock, reset, MPLL, and analog override state.
- Use register dumps during failures to confirm that PMA/PCS overrides, MPLLA/MPLLB settings, RTUNE/DCC status, TX pstate timers, RX statistics, and analog TX status fields decode as expected.
- On validation hardware, run RX statistic/LBERT/ATE paths when available to verify that diagnostic counters, pattern matches, sample-done bits, and forced override paths use the intended field positions.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`, including the register marker and the first shift definitions. This chunk owns the remaining masks for that register, the rest of the visible CR3 raw-lane PMA/PCS/TX/RX/ATE block, and the CR4 supervisor plus lane0 control/status section through the complete `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0` register. The next chunk begins at `DPCSSYS_CR4_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT`, so whole-file reconciliation should connect this document with adjacent chunks before making final claims about complete CR3/CR4 lane coverage.

### subset-b-002324: lines 85816-88172

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 85816-88172

## Scope

This chunk covers lines 85816-88172 of the generated AMD DPCS 4.2.0 shift/mask header. It contains 2,141 preprocessor definitions and register-block comments for DPCSSYS CR4 lane metadata. The range begins with the tail masks for `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0`, continues through lane 0 analog TX registers, and then covers a large lane 1 surface: digital ASIC override/actual fields, TX/RX power control, RX VCO/CDR/adaptation/statistical monitor controls, MPHY and analog TX/RX override/status fields, and the beginning marker for `DPCSSYS_CR4_LANE1_ANA_RX_ATB_REGREF`.

This file is declarative generated data. It exports constants only; it has no functions, structs, loops, allocations, locking, or direct MMIO access.

## Purpose

The purpose of this chunk is to describe bit positions and masks for low-level DPCS/PHY lane registers used by AMD display code. Each field is represented by a `__SHIFT` macro and a `_MASK` macro. Consumers combine these field constants with offsets from the matching `dpcs_4_2_0_offset.h` header and register helper macros to perform read-modify-write operations against 16-bit CR-space registers.

The main hardware concerns represented here are:

- Lane 0 analog TX diagnostics and override fields after the preceding lane 0 status block.
- Lane 1 digital ASIC override inputs and outputs for TX, RX, loopback, reset, request/acknowledge, rate, width, power state, equalization, CDR/VCO load values, MPHY/PWM mode, and cross-lane/master-lane clock handshakes.
- Lane 1 TX power-state sequencing for P0, P0S, P1, and P2, including reference generator, VCM hold, analog/digital clocks, reset, serial/data enable, receiver detection, VBOOST, and DCC compensation calibration.
- Lane 1 RX power-state sequencing, VCO calibration, CDR/DPLL controls, adaptation configuration/status, RX statistical pattern matching/counters, MPHY low-speed controls, analog TX/RX override controls, analog status, and analog RX calibration/power/signal-detect controls.

## Important API Surface

There are no callable APIs or local types. The exported API is the macro namespace for this line range.

Important lane 0 macro families in this chunk include:

- `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0` tail masks for TX clock-shift acknowledgement, RX detect results, loopback, RX analog calibration/scope data, TX DCC calibration result, and TX EQ mux status. The corresponding shifts started in the prior chunk.
- `DPCSSYS_CR4_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT*` for TX analog DCC calibration range, comparator enable, control value, control select, clock compensation, and override-enable gates.
- `DPCSSYS_CR4_LANE0_DIG_ANA_TX_OVRD_OUT_2` and `DPCSSYS_CR4_LANE0_ANA_TX_*` for TX fast start, clock loopback, AC JTAG enable, measurement ATB paths, TX power override, alternate bus/JTAG routing, DCC DAC values, termination code controls, clock overrides, VREF/DCC-range controls, peaking/slew/inversion settings, and reserved analog TX fields.

Important lane 1 digital ASIC macro families include:

- `DPCSSYS_CR4_LANE1_DIG_ASIC_LANE_OVRD_IN` and `...LANE_ASIC_IN` for TX-to-RX serial loopback, RX-to-TX parallel loopback, lane override enable, and RX AC JTAG.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_TX_OVRD_IN_0` through `_5` and `...TX_ASIC_IN_0` through `_2` for TX request, power state, rate, width, MPLL selection, data enable, main/pre/post cursor values, asynchronous drive/data, reset, clock ready, invert, LPD, HDMI/MPHY/DC-coupled modes, FIFO mode, receiver-detect request, and master-lane clock/repeater synchronization fields.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_TX_OVRD_OUT*` and `...TX_ASIC_OUT` for TX acknowledge, detect-RX result, repeater enable, digital clock enable/state, shift control, and shift-ack status.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_RX_OVRD_IN_0` through `_6` and `...RX_ASIC_IN_*` for RX request/data enable/pstate/rate/width, VCO/ref load values, CDR track and SSC enable, alignment, clock shift, disable, LPD, inversion, AFE/DFE adaptation, termination enable/ACDC, reset, PWM clock selection, LS/LCC termination, and PWM enable overrides.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_RX_OVRD_EQ_IN_*` and `...RX_EQ_ASIC_IN_*` for ATT, AFE gain, CTLE boost, DFE tap1/tap2, and EQ override enable.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_RX_OVRD_OUT_0` and `...RX_ASIC_OUT_0` for RX acknowledge, valid/adaptation status, async data, and weak-keeper outputs.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_OCLA` for RX DWORD OCLA clock/data enable.

Important lane 1 TX/RX control macro families include:

- `DPCSSYS_CR4_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0`, `_P0S`, `_P1`, and `_P2` for per-power-state TX analog and digital enable/reset sequencing. P2 adds `TX_P2_ALLOW_VBOOST`.
- `DPCSSYS_CR4_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_0` through `_5` for TX refgen/clock timing, VCM hold timing, VBOOST disable timing, RX-detect timing, reset timing, serial-enable timing, skip/fast flags, and DTB selection.
- `DPCSSYS_CR4_LANE1_DIG_TX_PWRCTL_DCC_*` for DCC CR bank address/data and DCC DAC control/range/select/ack/address handshakes.
- `DPCSSYS_CR4_LANE1_DIG_TX_CLK_ALIGN_TX_CTL_0` and `...TX_LBERT_CTL` for TX UI-shift alignment, FIFO bypass, and lane BERT pattern/error injection control.
- `DPCSSYS_CR4_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, `_P0S`, `_P1`, and `_P2` for RX AFE, clock regulator, analog clock, deserializer, CDR, VCO reset/calibration/continuous-calibration, and digital clock enable states.
- `DPCSSYS_CR4_LANE1_DIG_RX_VCOCAL_*` for RX VCO calibration control, frequency-tune calibration, startup/update/counter timing, final counter status, VCO direction/correctness flags, and calibration-done state.
- `DPCSSYS_CR4_LANE1_DIG_RX_CDR_*`, `...RX_DPLL_FREQ`, and `...RX_DPLL_FREQ_BOUND_*` for phase detector controls, SSC on/off counters, DPLL gain overrides, PHUG/FRUG status, frequency value, and upper/lower frequency bounds.
- `DPCSSYS_CR4_LANE1_DIG_RX_ADPTCTL_*` for RX adaptation algorithm timing, enable masks, CTLE/VGA/ATT/DFE thresholds and mu values, reset controls, adapted code status for ATT/VGA/CTLE/DFE taps 1-5, slicer and DAC offset controls, DAC-control selects, and CR bank address/data access.
- `DPCSSYS_CR4_LANE1_DIG_RX_STAT_*` for RX pattern load/mask/match controls, statistic control, sample count, statistic counters 0-6, calibration comparator clock control, and statistic stop.
- `DPCSSYS_CR4_LANE1_DIG_MPHY_RX_*` for PWM polarity/data polarity, low-speed termination LCC count, and analog PWM clock stable count.

Important lane 1 analog macro families include:

- `DPCSSYS_CR4_LANE1_DIG_ANA_TX_OVRD_OUT` and `...TX_TERM_CODE*` for TX analog clock/data/refgen/VCM/word-clock/MPLL/reset/serial/rate/rx-detect overrides, TX termination code, driver source, and self-clearing termination-clock behavior.
- `DPCSSYS_CR4_LANE1_DIG_ANA_TX_EQ_OVRD_OUT_0` through `_5` for TX EQ load clock, leg pull enables/directions, EQ mux selection, pre-cursor and post-cursor values, and EQ override enable.
- `DPCSSYS_CR4_LANE1_DIG_ANA_RX_CTL_OVRD_OUT`, `...RX_PWR_OVRD_OUT`, and `...RX_VCO_OVRD_OUT_*` for RX analog data rate, word/div4 clocks, DFE/adaptation enable, loopback clock, AFE/clock/CDR/deserializer power, fast start, CDR VCO enable/startup, frequency tuning, counter enable/clock/power-down, low-frequency mode, and self-clearing frequency-tune clock.
- `DPCSSYS_CR4_LANE1_DIG_ANA_RX_CAL`, `...DAC_CTRL*`, `...AFE_ATT_VGA`, `...AFE_CTLE`, `...SCOPE`, `...SLICER_CTRL`, `...IQ_*`, and update-clock registers for RX calibration muxes, DAC controls, AFE gain/attenuation/CTLE, scope capture, slicer control, IQ phase/sense, and self-clearing analog-update strobes.
- `DPCSSYS_CR4_LANE1_DIG_ANA_STATUS_0` and `_1` for analog result/status readback, including RX detect, loopback, RX calibration/scope, TX DCC calibration result, TX EQ mux, and RX VCO counter.
- `DPCSSYS_CR4_LANE1_DIG_ANA_RX_TERM_CODE*`, `...MPHY_OVRD_OUT`, `...SIGDET_OVRD_OUT_*`, `...TX_DCC_DAC_OVRD_OUT*`, and `...TX_OVRD_OUT_2` for RX termination code, MPHY squelch/PWM overrides, signal-detect voltage/reference/comparator/mux controls, TX DCC overrides, and TX fast-start/loopback/AC-JTAG.
- `DPCSSYS_CR4_LANE1_ANA_TX_*` for the analog-side TX measurement, power, alternate bus, ATB, DCC DAC/control, termination code/control, clock, VREF/DCC range, peaking/slew/inversion, and reserved fields.
- `DPCSSYS_CR4_LANE1_ANA_RX_CLK_*`, `...RX_CDR_DES`, `...RX_SLC_CTRL`, `...RX_PWR_CTRL*`, `...RX_SQ`, and `...RX_CAL*` for analog-side RX CDR/startup/clock, IQ phase, loopback clock, word-clock/phase-detector, slicer, AFE/DFE/deserializer/loopback/fast-start power overrides, squelch response/threshold, and calibration mux/DFE tap enable controls.

The final line in scope is the comment for `DPCSSYS_CR4_LANE1_ANA_RX_ATB_REGREF`; its field definitions are outside this chunk and belong to the next chunk.

## Control Flow

There is no executable control flow in this header range. The implied use flow is:

1. AMD display code selects a DPCS CR4 lane 0 or lane 1 register offset from `dpcs_4_2_0_offset.h`.
2. A register helper reads or writes the CR-space register through the display resource/link path.
3. Callers isolate or set a field by applying the `_MASK` and `__SHIFT` constants from this header.
4. Override-enable fields gate whether software-provided values replace hardware state-machine values.
5. Hardware returns status through acknowledge, result, calibration, counter, DPLL/CDR, VCO, adaptation, and statistic fields.

The naming indicates several hardware handshakes: TX/RX request and acknowledge, DCC DAC request and acknowledge, analog self-clearing update clocks, VCO calibration done/correct/up signals, adaptation ASM1 done bits, statistic sample-count done bits, and cross-lane master/other-lane clock shift acknowledgements.

## State And Persistence

The header stores no software state and persists nothing. The defined constants describe hardware-backed state and control fields:

- Override registers can force TX/RX reset, request, power state, rate, width, data enable, clock enable, loopback, termination, VCO/CDR tuning, EQ/cursor values, DCC calibration, signal detect, MPHY/PWM, and analog calibration paths.
- Power-control registers encode the desired analog/digital enable state for TX and RX power states and timing registers encode hardware sequencing delays.
- Status registers expose transient hardware results such as RX/TX acknowledgements, RX detect, CDR/VCO state, VCO calibration result, DPLL bounds, adapted equalizer codes, statistic counters, and analog calibration/scope outputs.
- Self-clearing control bits and update clocks are stateful at the hardware register level. Misusing their masks can trigger repeated updates or prevent intended updates.
- Reserved and `NC*` masks occupy many upper-bit regions. Correct consumers should preserve those bits unless the silicon programming guide explicitly defines a full-register write.

Durable effects are limited to hardware programming during display link bring-up, retraining, power management, diagnostics, lab/ATE modes, and recovery. The C preprocessor constants themselves do not allocate memory or retain runtime values.

## Dependencies And Integration Points

This header depends only on the C preprocessor and the larger include guard of `dpcs_4_2_0_sh_mask.h`. Its field constants are useful only with the matching DPCS 4.2.0 offset header.

In this source tree, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`. That is the visible in-tree integration point tying this generated register contract to DCN 3.1 display resource setup. Runtime access is expected to go through AMD display register helper infrastructure rather than through this header directly.

The constants are ASIC-version-specific and must remain synchronized with:

- `dpcs_4_2_0_offset.h`, which provides the register addresses.
- AMD's generated register database or silicon programming reference for DPCS 4.2.0.
- Adjacent generated DPCS headers for related versions where the driver expects compatible lane layouts.
- Link/PHY code that configures DisplayPort, embedded PHY, MPHY, low-speed/PWM modes, DCC calibration, CDR/VCO calibration, and RX adaptation.

## Risks

- A single incorrect mask or shift can silently misprogram PHY control fields. The highest-risk fields in this chunk are reset, power enable, clock enable, VCO/CDR tuning, TX EQ/cursor, termination, DCC calibration, adaptation, and self-clearing update strobes.
- The lane 1 register set is highly repetitive and mirrors patterns from other lanes and DPCS versions. Generated-data drift can create lane-specific failures that compile cleanly.
- Many fields are override gates paired with values. Setting a value without the matching override-enable bit, or leaving an override enabled after diagnostics, can cause hard-to-debug link training and power-state behavior.
- Reserved/NC bits are widespread. Full-register writes that do not preserve reserved bits risk changing undocumented hardware behavior.
- Some fields represent diagnostic or lab features such as OCLA, LBERT, ATB, JTAG, ATE-style measurement, scope, and loopback. Accidental use in normal display paths can alter signal integrity or hide real link failures.
- Timing fields for TX power-up and RX VCO/CDR/adaptation are hardware-sequencing sensitive. Incorrect values can lead to intermittent bring-up failures rather than deterministic build-time errors.
- This chunk begins and ends at generated-file boundaries: the first five lane 0 status masks depend on prior-chunk shift definitions, and the final `ANA_RX_ATB_REGREF` heading lacks its fields until the next chunk. The merge lane must reconcile these boundaries before making complete whole-register claims.

## Test Signals

Useful validation signals include:

- Build or preprocess AMDGPU DCN 3.1 display code that includes `dpcs_4_2_0_sh_mask.h`, especially `dcn31_resource.c`, to catch missing or renamed macros.
- Generated-header consistency checks that verify every non-boundary field has both a `__SHIFT` and `_MASK`, masks match their shifts and widths, and masks within a register do not overlap except where reserved/NC fields intentionally cover unused regions.
- Diff checks against AMD's authoritative DPCS 4.2.0 register data and against sibling generated headers for expected lane-to-lane structural equivalence.
- Hardware or emulator tests for DisplayPort link bring-up, link retraining, TX/RX power-state transitions, receiver-detect, lane reset/request handshakes, CDR/VCO calibration, DPLL frequency bounds, RX adaptation, DCC calibration, termination, MPHY/PWM low-speed behavior, loopback/LBERT diagnostics, and statistic counter reads.
- Failure signatures to watch for include lane 1-only link training timeouts, missing TX/RX ACK/VALID status, stuck VCO calibration done/correct/up flags, unstable DPLL/CDR lock, bad adapted CTLE/VGA/DFE codes, RX statistic counters not completing, unexpected signal-detect behavior, and display failures that appear only after power-state transitions.

## Chunk Boundaries

This document intentionally covers only lines 85816-88172 of `dpcs_4_2_0_sh_mask.h`. The previous chunk is needed for the beginning of `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0`; the next chunk is needed for `DPCSSYS_CR4_LANE1_ANA_RX_ATB_REGREF` fields and the remaining CR4 lane definitions. The final per-file research document should merge all chunks before presenting complete DPCS 4.2.0 register coverage.

### subset-b-002325: lines 88173-90528

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 88173-90528

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask register header fragment. It contains 2,356 lines of preprocessor constants defining bit shifts and masks for DPCS CR4 lane register fields. The chunk starts in the middle of the lane 1 analog RX ATB register block, covers the bulk of lane 2 digital and analog PHY field definitions, and ends in the beginning of lane 3 digital TX override definitions.

The file is not executable code. Its purpose is to provide the bitfield ABI used by low-level display PHY programming code together with the corresponding `dpcs_4_2_0_offset.h` `ixDPCSSYS_...` register offsets. Consumers write or read hardware registers by combining an offset macro with these `__SHIFT` and `_MASK` macros.

## Purpose

The macros describe control and status surfaces for a DisplayPort/PHY lane:

- ASIC-facing lane override and normal input/output fields for TX and RX.
- TX and RX power-state templates and power-up timing.
- TX DCC/DAC calibration control.
- TX clock alignment and loopback/BERT controls.
- RX VCO calibration, DPLL/CDR, DFE/CTLE/VGA adaptation, statistics/scope counters, and loopback/BERT controls.
- Digital-to-analog override outputs for TX/RX analog controls, term codes, equalization, signal detect, MPHY behavior, and analog status.
- Analog TX and RX low-level controls for clocks, power, calibration, ATB measurement, slicers, term codes, and reserved or not-connected fields.

Most definitions are 16-bit hardware fields stored in `0x0000....L` masks. The register naming convention encodes the block hierarchy: `DPCSSYS_CR4_LANE<N>_<DIG|ANA>_<subblock>_<register>__<field>_{SHIFT|MASK}`.

## Important API Surface

This chunk exposes macros, not functions or C types. The important API is the naming/bitfield contract:

- `...__<field>__SHIFT` gives the least-significant bit for a field.
- `...__<field>_MASK` gives the field mask after shifting.
- `RESERVED_*`, `NC*`, and `RSVD_*` fields identify bits that should generally be preserved or avoided unless the hardware programming guide requires otherwise.
- Paired `*_OVRD_EN` fields gate adjacent override values. Writes to override values without asserting the matching enable bit may have no effect; writes with the enable set can bypass automatic PHY control.

Primary register groups in this chunk:

- Boundary lane 1 analog RX ATB: `DPCSSYS_CR4_LANE1_ANA_RX_ATB_REGREF`, `ATB_MEAS1..4`, `ATB_FRC`, and `ANA_RX_RESERVED1`.
- Lane 2 ASIC interface: `DIG_ASIC_LANE_OVRD_IN`, `DIG_ASIC_TX_OVRD_IN_0..5`, `DIG_ASIC_TX_OVRD_OUT(_1)`, `DIG_ASIC_RX_OVRD_IN_0..6`, `DIG_ASIC_RX_OVRD_EQ_IN_0..1`, `DIG_ASIC_RX_OVRD_OUT_0`, `DIG_ASIC_*_ASIC_IN/OUT`, and `DIG_ASIC_OCLA`.
- Lane 2 TX power/control: `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0..5`, `DCC_*`, `DIG_TX_CLK_ALIGN_TX_CTL_0`, and `DIG_TX_LBERT_CTL`.
- Lane 2 RX power/calibration/control: `DIG_RX_PWRCTL_RX_PSTATE_*`, `RX_PWRUP_TIME_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, `RX_LBERT_*`, `RX_ADPTCTL_*`, and `RX_STAT_*`.
- Lane 2 digital-to-analog override/status: `DIG_ANA_TX_*`, `DIG_ANA_RX_*`, `DIG_ANA_SIGDET_*`, `DIG_ANA_MPHY_*`, and `DIG_ANA_STATUS_*`.
- Lane 2 direct analog controls: `ANA_TX_*` and `ANA_RX_*`.
- Boundary lane 3 digital TX override: `DPCSSYS_CR4_LANE3_DIG_ASIC_LANE_OVRD_IN` and `DIG_ASIC_TX_OVRD_IN_0..4` through the `RESET_OVRD_EN_MASK` line.

## Control Flow and Data Flow

There is no runtime control flow in this header. The effective hardware programming flow implied by the macros is:

1. Select an indirect DPCS CR register using an `ixDPCSSYS_CR4_LANE...` offset from the matching offset header.
2. Read the current 16-bit/32-bit register value when preserving reserved or unrelated fields is required.
3. Clear target bits with `_MASK`, place new field values using `__SHIFT`, and write the merged value.
4. For manual PHY programming, assert the relevant `*_OVRD_EN` or `ovrd_*` bit after setting the value field.
5. Poll status fields such as `ACK`, `VALID`, `ASM1_DONE`, `RX_VCO_CAL_DONE`, `SMPL_CNT1_DONE`, `TX_ANA_*_ACK`, or error counters to confirm hardware state.

Several groups encode multi-step flows:

- TX/RX pstate macros describe which analog and digital enables are active in power states `P0`, `P0S`, `P1`, and `P2`. Timing registers then specify waits for refgen, VCM hold, vboost disable, reset, serial enable, RX AFE/vreg/clock/CDR/deserializer, and fast-start paths.
- RX VCO calibration fields control resets, continuous calibration enable, frequency-tune start/step behavior, wait times, and status fields reporting FSM state, calibration done, DPLL reset, final counter value, and direction/correctness.
- RX adaptation fields configure AFE/DFE/CTLE/VGA enablement, thresholds, step sizes, saturation behavior, reset controls, slicer levels, DAC selections, and readback status codes.
- RX statistics/scope fields configure pattern matching, masks, sample counts, counter enables, data delay, clocking, pauses, stop/start, and counter results.
- ATB and scope fields route internal analog measurements for lab/debug visibility.

## State and Persistence

The state represented by these macros is hardware register state, not kernel-owned persistent data:

- Values persist in the PHY register file until reset, power transition, firmware/driver reprogramming, or hardware self-clear behavior changes them.
- Many fields are direct power/clock/reset enables. A bad write can immediately affect lane link state.
- Some controls are explicitly self-clearing or can disable self-clear behavior, including `DAC_CTRL_SELF_CLEAR_DISABLE`, `PHASE_ADJUST_SELF_CLEAR_DISABLE`, `AFE_UPDATE_SELF_CLEAR_DISABLE`, `RX_SCOPE_SELF_CLEAR_DISABLE`, and term/frequency tune clock self-clear disable fields.
- Status and counters such as LBERT error count, RX stat counters, VCO status, analog status, and adaptation status are volatile hardware observations.
- Reserved and NC fields are part of the ABI shape but should not be treated as stable software state.

## Dependencies and Integration Points

This chunk depends on the rest of the generated AMD register headers:

- `dpcs_4_2_0_offset.h` supplies the matching `ixDPCSSYS_CR4_LANE2_...` offsets for the register names defined here.
- Other DPCS 4.2.x mask/offset headers carry nearly identical lane/register surfaces for related ASIC revisions.
- AMD display code normally reaches these registers through DC/DM register access helpers and generated include layering rather than by including this chunk in isolation.

Integration-sensitive areas:

- Lane numbering is embedded in every macro. Lane 2 definitions must be paired with lane 2 offsets; lane 1 and lane 3 fragments in this chunk are boundary spillover and should not be merged into lane 2 programming tables by accident.
- The register surface is duplicated by lane, so generated consistency across lanes matters. Manual edits can silently break one lane while leaving others correct.
- Power sequencing fields interact with link training and PHY bring-up/tear-down code. These are not ordinary software config flags.
- Debug/test controls such as BERT, OCLA, ATB, scope, loopback, and MPHY overrides may conflict with normal display link operation if left enabled.

## Risks

- Incorrect masks or shifts can corrupt adjacent fields, including reserved bits, because callers depend on these constants for read-modify-write operations.
- Setting override enables can bypass hardware state machines for TX/RX clocks, data enable, CDR, VCO, equalization, term codes, signal detect, and analog power. This can cause link loss, unstable training, or bad signal quality.
- Power-state and timing values are highly hardware-specific. Applying lane 2 or DPCS 4.2.0 definitions to a different lane/revision without matching offsets can program the wrong register.
- Self-clearing control bits are easy to mishandle in polling code. A test may pass if the bit clears quickly but fail if software later disables self-clear or assumes the bit remains set.
- Status counters and adaptation readbacks are volatile. Tests must tolerate hardware timing and should not expect deterministic values without a controlled link/test pattern.
- The chunk boundaries split register groups: lane 1 `ANA_RX_ATB_REGREF` lacks its comment header in this slice, and lane 3 `DIG_ASIC_TX_OVRD_IN_4` is incomplete beyond the final mask present here. Merge tooling must rely on line ranges and adjacent chunks for full-file context.

## Test Signals

Useful validation signals for code using these definitions:

- Build-time: headers compile cleanly, no duplicate macro warnings in the intended include order, and generated offset/mask names match exactly.
- Static consistency: for each field, `MASK >> SHIFT` should fit the documented field width and should not overlap unrelated fields except reserved ranges.
- Register-pair consistency: every lane 2 mask register in this chunk should have a matching `ixDPCSSYS_CR4_LANE2_...` offset in `dpcs_4_2_0_offset.h`.
- Lane consistency: corresponding lane 1/lane 2/lane 3 groups should preserve identical field layouts where the hardware is lane-replicated.
- Runtime hardware smoke tests: link bring-up, link training, display modeset, suspend/resume, hotplug, and power-state transitions should not regress.
- PHY/debug tests: LBERT mode/sync/error count, OCLA clock/data enable, RX stat sample counters, VCO calibration done/status, adaptation `ASM1_DONE` statuses, and analog status readbacks are direct indicators that these bit definitions still map to hardware as expected.

## Summary

This chunk is a generated hardware ABI map for DPCS CR4 lane PHY registers, dominated by lane 2. It has no functions or data structures, but it is critical because all low-level display PHY register programming depends on these exact bit positions. The highest-risk surfaces are override enables, power-state templates, VCO/CDR calibration, RX adaptation, and volatile debug/status counters.

### subset-b-002326: lines 90529-92906

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 90529-92906

## Scope

This chunk covers lines 90529-92906 of the generated AMD DPCS 4.2.0 shift/mask header. It contains 2,121 `#define` entries: 1,061 `__SHIFT` macros and 1,060 `_MASK` macros.

The count imbalance is a chunk-boundary artifact. The range starts with the final mask for `DPCSSYS_CR4_LANE3_DIG_ASIC_TX_OVRD_IN_4`, whose shift and earlier masks are immediately above line 90529. The range ends inside `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN`, after `MSTR_MPLL_OVRD_EN_MASK`; the remaining masks for `TX_ASYNC_EN_OVR_VAL` and `TX_ASYNC_EN_OVR_EN` follow below line 92906.

The content is declarative only. It defines preprocessor constants for register bit positions and masks. There are no C functions, structs, enums, branches, loops, allocations, locks, or local runtime state in this range.

## Purpose

The header gives AMDGPU display code symbolic field definitions for DPCS 4.2.0 CR4 display PHY and controller registers. Consumer code combines these `__SHIFT` and `_MASK` constants with generated register-address headers and AMDGPU/DC register helpers to compose read-modify-write operations against memory-mapped or indirect ASIC registers.

This slice covers three major CR4 areas:

- The tail of CR4 lane 3 controls, including ASIC TX/RX override mirrors, lane ASIC inputs, TX/RX ASIC status, TX power-state sequencing, DCC DAC controls, TX clock alignment, loopback/BERT, RX statistic matching/counters, digital-to-analog TX override outputs, and lane 3 analog TX controls.
- CR4 raw common controls, including MPLLA/MPLLB override and spread-spectrum fields, common control/status, SRAM/ID/OCLA, always-on RTUNE values for multiple lanes, power-gate/supervisor/resource overrides, VREF status, and miscellaneous common configuration.
- CR4 raw lane 0 and the beginning of raw lane 1, including PCS TX/RX override and PCS in/out mirrors, RX adaptation and equalization, FSM fast-calibration/status registers, IRQ status/clear/mask fields, PMA crossbar fields, TX/RX control registers, ATE paths, and the first raw lane 1 TX override register.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated macro namespace. Important families in this chunk include:

- `DPCSSYS_CR4_LANE3_DIG_ASIC_*`: ASIC-facing lane, TX, and RX fields for TX acknowledgement, DETRX result/request, RX ACK/VALID/adaptation status, loopback, clock-ready, reset, invert, data-enable, request, low-power detect, P-state, rate, width, MPLLB selection, beacon, async TX, vreg bypass, pre/main/post cursor values, and multi-lane clock/shift/master-lane override signals.
- `DPCSSYS_CR4_LANE3_DIG_TX_PWRCTL_*`: TX power-state definitions for P0/P0s/P1/P2, power-up timing windows, and DCC CR-bank/DAC programming fields. These fields name analog reference generation, VCM hold, analog/word clock enables, reset, serial enable, digital clock enable, data enable, RX detect allowance, DCC compensation calibration, and per-phase timeouts.
- `DPCSSYS_CR4_LANE3_DIG_RX_STAT_*`: receiver statistic load, data mask, match controls, statistic controls, sample count, status counters, calibration compare clock control, and stop control fields.
- `DPCSSYS_CR4_LANE3_DIG_ANA_*` and `DPCSSYS_CR4_LANE3_ANA_TX_*`: digital override outputs and analog TX controls for TX request/reset/invert/low-power, rate/width/P-state, clocks, TX async, main/pre/post cursor, vboost/iboost, termination code, equalization, DCC DAC, power measurement, alternate bus, analog test bus, power override, termination update/reset, HDMI/MPHY/DC-coupled modes, and reserved analog tuning windows.
- `DPCSSYS_CR4_RAWCMN_DIG_*`: common digital controls for MPLLA/MPLLB power and overrides, PLL bandwidth and SSC programming, lane FSM extended operation, common control bits, MPLL state, TX calibration code, SRAM init done, OCLA, supervisor analog override, raw PCS and firmware ID codes, AON common RTUNE readbacks, SRAM bitline config, power-gate/resource/supervisor override inputs and outputs, VREF status, reference range override, and miscellaneous common configuration.
- `DPCSSYS_CR4_RAWLANE0_DIG_PCS_XF_*`: raw lane 0 PCS crossbar fields for TX/RX overrides, PCS in/out mirrors, RX adaptation acknowledgement and figure-of-merit, TX pre/main/post cursor direction, lane number, reserved windows, ATE override, RX equalization and phase-2 calibration controls, TX/RX termination control, and additional ATE TX/RX override registers.
- `DPCSSYS_CR4_RAWLANE0_DIG_FSM_*`: lane 0 FSM override, memory/status monitors, fast RX startup/adaptation/AFE/DFE/bypass/reference-level/IQ calibration controls, supervisor and TX fast-state controls, common-calibration status, continuous calibration/adaptation states, flags, CR lock, TX DCC flags/status, OCLA, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANE0_DIG_IRQ_CTL_*`: status, clear, and mask fields for RX reset/request/rate/P-state/adaptation request/adaptation disable, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX serial loopback enable, DCC on-demand, and TX reset/request interrupts.
- `DPCSSYS_CR4_RAWLANE0_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*`: PMA lane/supervisor/TX/RX override and input/output mirrors, lane RTUNE, MPHY override, RX adaptation override, TX/RX FSM controls, TX clock and DCC continuous status, loss-of-signal masking, RX data-enable override, off-cancel/adaptation continuous status, and OCLA taps.
- `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN_*`: the opening raw lane 1 TX override fields for P-state, LPD, width, rate, MPLLB select, MPLL enable, override enable, master MPLLA/MPLLB state, and master MPLL override enable.

## Register Areas Covered

The lane 3 ASIC and TX power-control area is the per-lane interface between display link logic and the DPCS PHY. It exposes both normal ASIC inputs/outputs and explicit override outputs. The field names separate value bits from adjacent override-enable bits, especially around TX ACK, DETRX, RX ACK/adaptation status, clock-ready, reset, low-power detect, master-lane coordination, and clock-shift handshakes. The TX P-state registers describe the electrical enable set for each power state, while the power-up timing registers provide timeout/count fields for analog reference, VCM, clocks, reset, serial/data enable, RX detect, and DCC calibration stages.

The lane 3 RX statistic and analog TX area is a diagnostic and calibration surface. Statistic registers define match masks, compare controls, counters, stop behavior, and calibration compare clock selection. Analog TX override and analog TX registers expose termination, equalization cursor, DCC DAC, clocking, analog test-bus, measurement, and miscellaneous mode bits. These are low-level PHY knobs rather than high-level display policy.

The raw common area manages CR4 shared DPCS state. MPLLA and MPLLB override groups include reference-clock enables, reset/calibration requests, fractional feedback dividers, multiplier ranges, HDMI clock controls, SSC peak and step-size fields, and bandwidth override values. AON common fields expose RTUNE values per lane, SRAM bitline setup, power-gate and supervisor overrides, resource ASIC input/output mirrors, VREF status, reference range, and miscellaneous common configuration. ID and firmware-code registers identify the raw PCS/firmware view.

The raw lane 0 PCS/PMA area is the digital bridge around the lane PHY. PCS fields cover TX/RX value overrides, PCS input mirrors, output/status mirrors, adaptation controls, figure-of-merit readback, cursor direction feedback, lane numbering, equalization override, phase-2 calibration, ATE override, and TX/RX termination controls. PMA fields mirror lane, supervisor, TX, RX, MPHY, RTUNE, and adaptation status across override and ASIC-input style registers.

The raw lane 0 FSM and IRQ area describes hardware sequencing and event signaling. FSM fields name fast calibration/adaptation phases, continuous calibration states, lock/status flags, TX DCC state, CMNCAL MPLL/RCAL status, and RX IQ phase offset. IRQ fields are organized as status/clear/mask groups, so the same event families appear repeatedly with different write semantics.

The raw lane 1 material is only the beginning of a repeated lane pattern. It starts the `PCS_XF_TX_OVRD_IN` register and should be merged with the following chunk before drawing complete conclusions about raw lane 1.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior is created by driver code that includes this header and writes the corresponding hardware registers.

The field names imply several hardware state machines and handshakes:

- TX/RX lane bring-up uses reset, clock-ready, request/acknowledge, data-enable, low-power detect, P-state, rate, width, MPLL select/enable, RX detect request/result, beacon, and async-data controls.
- TX power sequencing uses the P0/P0s/P1/P2 power-state bit sets and the TX power-up timing registers to coordinate analog reference generation, VCM hold, analog/word/digital clocks, reset release, serial enable, data enable, RX detect, and DCC compensation.
- Common PLL programming uses MPLLA/MPLLB override inputs, bandwidth values, SSC peak/step-size fields, MPLL state controls, and master MPLL override state bits visible in lane-level registers.
- Calibration and adaptation use RX adaptation acknowledgement/status, FOM, RX EQ overrides, PH2 calibration controls, fast FSM phase fields, continuous adaptation/calibration status, CMNCAL MPLL/RCAL status, CR lock, TX DCC flags/status, RX IQ phase offset, and RTUNE readbacks.
- Interrupt behavior is latch-like and split across status, clear, and mask registers for RX/TX reset/request/rate/P-state/adaptation/PH2/loopback/DCC events. Consumers must use the correct status, clear, or mask macro family.
- Diagnostic and validation flows use LBERT, OCLA, ATE, ATB, SRAM init/status, memory monitor, statistic counters, analog measurement, firmware ID, raw PCS ID, and reserved/tuning windows.

No software persistence is implemented here. Hardware register contents persist or reset according to ASIC power, reset, and clock domains. Fields named `STATUS`, `ACK`, `RESULT`, `CNT`, `FOM`, `LOCK`, `FLAGS`, `CODE`, `ID`, `RTUNE`, `VREF`, `ASIC_IN`, `PMA_IN`, and `PCS_IN` indicate hardware readback or latched state, but this chunk does not define save/restore policy.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. These macros are intended to be included with generated DPCS 4.2.0 register address headers and AMDGPU/DC helper macros that derive field values from shift and mask constants.

Integration points visible from the naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DPCS/RDPCS PHY, Display Core, link encoder, clock, DisplayPort, HDMI, and PHY diagnostics paths.
- Generated ASIC register offset headers for DPCS 4.2.0 CR4 registers. This file supplies field shifts and masks, not register addresses.
- DisplayPort and HDMI link training and recovery paths that control lane width/rate/P-state, TX EQ pre/main/post cursors, RX adaptation, FOM, RX/TX reset, RX detect, beacon, and PLL selection.
- Suspend/resume and hotplug paths that reinitialize common PLL, power-gate, supervisor, RTUNE, bandgap/VREF, lane power, and analog TX state after power-domain transitions.
- Hardware validation, manufacturing, and bring-up tooling that uses OCLA, ATE, ATB, LBERT, statistic counters, FSM monitors, firmware/raw ID codes, SRAM init, and analog measurement fields.
- Firmware or hardware state-machine coordination paths, reflected by `ASIC_IN`, `ASIC_OUT`, `OVRD_IN`, `OVRD_OUT`, `PCS_IN`, `PCS_OUT`, `PMA_IN`, and `PMA_OUT` naming.

## Risks

- Generated-header drift is the main risk. A wrong mask or shift can silently write adjacent PHY or PLL bits during read-modify-write operations.
- This chunk mixes CR4 lane 3, CR4 raw common, raw lane 0, and the beginning of raw lane 1. Prefix mistakes can compile cleanly while targeting the wrong lane or common block.
- Many registers pair a value bitfield with an override-enable bitfield. Setting only the value, or leaving override-enable asserted after diagnostics, can force PHY behavior away from normal ASIC or FSM control.
- IRQ status, clear, and mask registers have similar names but different semantics. Using a clear macro as persistent state, or writing a status mirror as a control value, can lose interrupts or leave stale event latches.
- Analog TX, PLL, SSC, RTUNE, VREF, DCC DAC, termination, boost, and cursor fields affect signal integrity. Changes need hardware-spec validation and link testing, not only compile coverage.
- Reserved and spare masks are exposed beside active fields. Driver code should preserve reserved bits unless the hardware specification explicitly documents a write value.
- Chunk boundaries are partial. `DPCSSYS_CR4_LANE3_DIG_ASIC_TX_OVRD_IN_4` is missing its shifts and earlier masks here, and `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN` is missing its final two masks. Merge tooling must combine adjacent chunks before doing per-register completeness checks.
- Repeated per-lane and MPLLA/MPLLB patterns are copy-generation sensitive. A single instance-specific field error may only affect one lane, one PLL path, or one diagnostic mode.

## Test Signals

Useful validation signals are build-time, generation-time, and hardware-integration oriented:

- Preprocess/compile AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static generated-header checks against the authoritative DPCS 4.2.0 register database, especially around the lane 3 to raw common to raw lane 0 address-region transitions.
- Macro-pair checks that each complete register block has matching `__SHIFT` and `_MASK` definitions and that masks correspond to field width and shift. For this sliced chunk, the expected local count is 1,061 shifts and 1,060 masks because of partial boundaries.
- Grep/compile checks for consumers of `DPCSSYS_CR4_LANE3_DIG_ASIC`, `DPCSSYS_CR4_LANE3_DIG_TX_PWRCTL`, `DPCSSYS_CR4_LANE3_DIG_RX_STAT`, `DPCSSYS_CR4_LANE3_DIG_ANA`, `DPCSSYS_CR4_LANE3_ANA_TX`, `DPCSSYS_CR4_RAWCMN_DIG`, `DPCSSYS_CR4_RAWLANE0_DIG_PCS_XF`, `DPCSSYS_CR4_RAWLANE0_DIG_FSM`, `DPCSSYS_CR4_RAWLANE0_DIG_IRQ_CTL`, and `DPCSSYS_CR4_RAWLANE0_DIG_PMA_XF` macros.
- Runtime display tests on ASICs using DPCS 4.2.0: DP and HDMI link training, hotplug, suspend/resume, link-rate changes, lane-count changes, RX/TX reset recovery, PLL lock/recalibration, RX adaptation convergence, and interrupt clear/mask behavior.
- PHY bring-up readback for TX ACK, DETRX result, RX ACK/VALID/adaptation status, P-state/rate/width, TX power-state timing, DCC DAC acknowledgement, RX statistic counters, MPLL state, SRAM init done, RTUNE values, VREF status, FOM, CR lock, TX DCC status, CMNCAL status, RX IQ phase offset, and lane IRQ status/clear/mask behavior.
- Diagnostic coverage for OCLA, ATE, ATB, LBERT, statistic match/counter, analog measurement, firmware/raw ID, FSM monitor, and reserved/tuning register paths when hardware validation or manufacturing flows depend on them.

## Chunk Notes For Merge

This document intentionally covers only lines 90529-92906 of `dpcs_4_2_0_sh_mask.h`. The previous chunk should complete `DPCSSYS_CR4_LANE3_DIG_ASIC_TX_OVRD_IN_4` before this range, and the following chunk should complete `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN` and continue the raw lane 1 repeated register families. The later per-file merge should describe this source as a generated ASIC bitfield map for AMD DPCS 4.2.0, not handwritten driver logic, and should preserve the distinction between CR4 lane 3, raw common, raw lane 0, and raw lane 1 surfaces.

### subset-b-002327: lines 92907-95285

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 92907-95285

## Scope

This chunk covers 2,379 lines from the generated AMD DPCS 4.2.0 shift/mask header. The chunk starts in the final mask entries for `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN` and then contains complete register-field macro groups from `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN_1` through the heading for `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_RX_ADAPT_FOM`. The matching offset header and other chunks define the register addresses; this file supplies the field positions and masks used by register helper code.

## Purpose

The source is a hardware register description header for the AMD display DPCS block, specifically CR4 rawlane digital PCS/PMA/FSM/IRQ/TX/RX control fields for DPCS 4.2.0. It exports preprocessor constants named as:

- `<register>__<field>__SHIFT`
- `<register>__<field>_MASK`

These constants let C code form and extract fields from 16-bit-style register payloads without hard-coding bit positions. The chunk is mostly lane-local register vocabulary for rawlane 1 and rawlane 2, then begins the same PCS TX/RX vocabulary for rawlane 3.

## Important API Surface

There are no functions, structs, enums, or runtime objects in this chunk. Its API is entirely macro constants. Important macro families include:

- `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_*`: lane 1 PCS transfer/interface controls for TX override input, TX PCS input/output, RX override input, RX PCS input/output, RX adaptation status, loopback direction, lane number, ATE overrides, RX equalization override, TX/RX termination, and RX phase-2 calibration.
- `DPCSSYS_CR4_RAWLANE1_DIG_FSM_*`: lane 1 FSM controls and monitors, including `FSM_OVRD_CTL`, `MEM_ADDR_MON`, `STATUS_MON`, fast RX/TX calibration/adaptation flags, common calibration MPLL/RCAL status, CR lock bits, OCLA hooks, TX DCC state, TX EQ update flag, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANE1_DIG_IRQ_CTL_*`: lane 1 IRQ status, clear, and mask definitions for RX reset/request/rate/pstate/adaptation/phase-2-calibration events, lane mode and loopback events, DCC on-demand IRQ, and TX reset/request IRQs.
- `DPCSSYS_CR4_RAWLANE1_DIG_PMA_XF_*`: lane 1 PCS-to-PMA interface fields for lane/supervisor override, TX/RX PMA handshakes, RTUNE, MPHY override, and RX adaptation output override.
- `DPCSSYS_CR4_RAWLANE1_DIG_TX_CTL_*` and `DPCSSYS_CR4_RAWLANE1_DIG_RX_CTL_*`: lane 1 local control/status bits for TX FSM, TX clock selection, TX DCC continuous status, OCLA, RX FSM, LOS mask count, RX data-enable override count, and continuous adaptation/off-cancellation status.
- `DPCSSYS_CR4_RAWLANE2_DIG_*`: the same broad PCS, FSM, IRQ, PMA, TX control, RX control, and ATE register families repeated for rawlane 2.
- `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_*`: the beginning of rawlane 3 PCS TX/RX handshaking and override definitions through `RX_ADAPT_ACK`; the `RX_ADAPT_FOM` heading appears at the end boundary but its field macros are outside this chunk.

Field names carry the hardware contract. Examples:

- TX override fields expose `RESET_OVRD_VAL/EN`, `REQ_OVRD_VAL/EN`, `DETRX_REQ_OVRD_VAL/EN`, `VBOOST_EN_OVRD_VAL/EN`, `IBOOST_LVL_OVRD_VAL/EN`, and beacon/async-data enable fields.
- RX override fields expose link rate/width/pstate/low-power data, adaptation enables, loopback override, RX data enable override, reset/request override, LOS threshold override, adaptation request/continuous/off-cancellation control, VCO load/low-frequency override, and reference-load override.
- RX PCS input status fields expose request, rate, width, pstate, CDR low-frequency state, adaptation request/continuous/off-cancellation, reset, reference/VCO load values, and EQ state such as attenuation level, VGA gains, CTLE boost/pole, and DFE tap 1.
- IRQ clear registers use one-bit `*_IRQ_CLR` fields; mask registers use `*_IRQ_MSK` fields. The value semantics are implemented by hardware and callers, not by this header.

## Control Flow

There is no executable control flow. The generated header is consumed at C preprocessing and compilation time. Runtime register control flow in the display driver is external:

1. A driver file includes `dpcs_4_2_0_offset.h` for addresses and `dpcs_4_2_0_sh_mask.h` for field encodings.
2. Register helper macros or inline functions combine a register address with one or more `*_MASK` and `*__SHIFT` constants.
3. Hardware accessors read, update, or write the corresponding DPCS MMIO/register-space value.

Within this chunk, the only ordering dependency is textual: each comment heading identifies a register, then its field shifts are listed, followed by matching masks. Some chunk boundaries are partial; line 92907 continues the preceding `RAWLANE1_DIG_PCS_XF_TX_OVRD_IN` register, and line 95285 only introduces the next `RAWLANE3_DIG_PCS_XF_RX_ADAPT_FOM` register.

## State and Persistence Behavior

The header itself has no memory, persistence, locking, allocation, or side effects. It is persistent source data for register definitions. The state represented by these macros lives in hardware registers:

- PCS TX/RX request, reset, ACK, rate, width, pstate, loopback, and data-enable state.
- PMA/PCS handshake state, MPLL lane/supervisor state, and RTUNE acknowledgements.
- FSM monitor state such as command-ready, state index, wait count, ALU flags, memory address, and calibration flags.
- Sticky or latched IRQ status/clear/mask bits, depending on the underlying register behavior.
- RX adaptation measurements and calibration outputs such as FOM, EQ settings, IQ phase offset, VCO/ref load, and phase-2 calibration fields.

Any persistence, latching, clear-on-write behavior, or sequencing requirements are hardware-defined and must be enforced by the driver code that reads/writes these registers. The masks should not be treated as proof that a reserved field can be written safely.

## Dependencies

Direct dependencies are preprocessor-level:

- Include guard `_dpcs_4_2_0_SH_MASK_HEADER` is defined earlier in the same file.
- The matching address definitions are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both `dpcs_4_2_0_offset.h` and this `dpcs_4_2_0_sh_mask.h`, then includes `reg_helper.h`, which is the normal AMD display register-helper layer.
- Neighboring generated DPCS versions, such as `dpcs_4_2_2_sh_mask.h` and `dpcs_4_2_3_sh_mask.h`, contain comparable definitions and are useful compatibility references, but they are distinct ASIC/IP register contracts.

This chunk does not include other headers and does not depend on C library, kernel APIs, or Ceph-specific code despite being located under the larger `ceph-client` source mirror.

## Integration Points

The main integration point is the AMD DCN 3.1 display resource stack. `dcn31_resource.c` includes this header for DPCS 4.2.0 register field constants. Downstream code can use these constants with generated register lists and helper macros to:

- Program lane TX/RX PCS and PMA override behavior during link bring-up, power transitions, retraining, or diagnostics.
- Observe and clear lane IRQs for RX/TX request/reset/rate/pstate/adaptation events.
- Configure or inspect fast calibration/adaptation paths for RX AFE/DFE/VCO/ref-level/IQ and TX DCC/supervisor calibration.
- Gate observability/debug paths such as OCLA and FSM monitor registers.
- Support automated test equipment paths through `ATE_*` override registers.

The specific rawlane macros in this chunk were only found in the generated headers during text search, not in direct C references elsewhere in the mirrored tree. That suggests they are part of a broad generated register surface where many fields are available to common helper code, debugging, or future ASIC-specific paths even if not explicitly used in the checked-in C sources.

## Risks and Edge Cases

- Register-field drift is the primary risk. If these generated masks do not match the DPCS 4.2.0 hardware spec or matching offset header, callers can silently write the wrong bits.
- Chunk boundaries are partial. Research or merge logic must not infer that line 92907 starts a complete register definition or that line 95285 contains the complete `RX_ADAPT_FOM` register.
- Many masks cover reserved fields, for example `RESERVED_15_*`. These are useful for generated completeness and readback decoding, but production code should avoid writing nonzero reserved bits unless the hardware spec requires it.
- Lane copy/paste errors are hard to detect manually because rawlane 1, rawlane 2, and rawlane 3 definitions are structurally repetitive. A lane prefix mismatch would compile cleanly but target the wrong register field family.
- All masks in this 4.2.0 chunk use 32-bit-looking `0x0000....L` constants for 16-bit fields. Neighboring DPCS versions may use shorter hex formatting for equivalent values; formatting differences should not be mistaken for semantic differences, but width/sign assumptions in helper macros should still be checked.
- Hardware side effects are not visible here. Fields named `*_CLR`, `*_OVRD_EN`, `RESET`, `REQ`, `ACK`, or calibration/adaptation bits may require strict sequencing, polling, debounce, or clear semantics in runtime code.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver integration signals:

- Build coverage for AMD display code that includes `dcn31_resource.c` and this generated header.
- Static checks that every `*_MASK` has a corresponding `*__SHIFT` for non-heading fields in the same register group, except at chunk boundaries where the complete group may be outside this file slice.
- Generated-header consistency checks against `dpcs_4_2_0_offset.h`: every register prefix used here should have a matching address definition in the offset header for the same IP version.
- Cross-version diff checks against `dpcs_4_2_2_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` to identify intended versus accidental field layout changes.
- Runtime display link tests on DCN 3.1/DPCS 4.2.0 hardware: link training, hotplug, rate changes, low-power transitions, RX adaptation, IRQ handling, and recovery from reset/request transitions.
- Debug readback tests that decode register values using these masks and confirm lane-specific fields behave independently across rawlane 1, rawlane 2, and rawlane 3.

## Open Questions for Merge Lane

- The final per-file synthesis should connect this chunk to neighboring chunks that define rawlane 0, the start of rawlane 1, the remainder of rawlane 3, and later rawlanes/register blocks.
- The merge lane should verify whether `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_RX_ADAPT_FOM` is completed in the next chunk and avoid treating this boundary heading as a complete register group.
- If the repository contains generated register metadata outside the C headers, the merged report can compare this source against that generator output to assess whether the header is hand-edited or fully generated.

### subset-b-002328: lines 95286-97717

# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 95286-97717

## Scope

This chunk covers lines 95286-97717 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h`. It is a generated AMD DPCS 4.2.0 register bitfield header slice, not executable logic. The range contains 2,078 `#define` macros: 1,039 `__SHIFT` definitions and 1,039 matching `_MASK` definitions. Register blocks are separated by `//DPCSSYS_...` comments; 354 block comments appear in this range.

## Purpose

The chunk provides C preprocessor constants used by AMD GPU display/PHY driver code to compose, mask, and decode 16-bit DPCS CR4 register fields. The constants map hardware register field names to bit positions and masks for:

- `DPCSSYS_CR4_RAWLANE3_DIG_*`: raw lane 3 digital PCS, FSM, IRQ, PMA, TX, and RX control/status fields.
- `DPCSSYS_CR4_RAWAONLANE0_DIG_*`, `RAWAONLANE1`, and `RAWAONLANE2`: repeated always-on lane register fields for analog adaptation, DFE, signal-detect, DCC, MPLL, firmware config, and transceiver mode.
- The chunk ends at the comment for `DPCSSYS_CR4_RAWAONLANE3_DIG_AFE_ATT_IDAC_OFST`; the actual lane 3 always-on field macros are outside this chunk.

The header lets other code avoid hard-coded bit positions when programming DPCS hardware through MMIO/register-access helpers. It preserves the hardware register naming scheme, so integration code can use generated symbolic masks while still matching the ASIC register specification.

## Important Macros and Register Areas

There are no functions, structs, enums, or types in this slice. The API surface is the macro namespace itself:

- `...__FIELD__SHIFT` macros define the least-significant bit position of a field.
- `...__FIELD_MASK` macros define the field mask in the 16-bit register word, generally with an `L` suffix.
- `...__RESERVED_*` macros document reserved bit positions and masks. These are useful for validation and generated completeness, but driver writes should avoid setting reserved bits unless required by hardware documentation.

Key raw lane 3 groups:

- PCS transfer/control fields: `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, `RX_TXPOST_DIR`, `LANE_NUMBER`, reserved registers, ATE override input, RX equalization overrides, termination control, RX phase-2 calibration, and lane data/clock override fields.
- FSM fields: override controls such as `FSM_JMP_ADDR`, `FSM_JMP_EN`, `FSM_CMD_START`, `FSM_OVRD_EN`, `FSM_BREAK`; monitor fields such as `MEM_ADDR`, `STATE`, `CMD_RDY`, `ALU_OVFLW`, `WAIT_CNT_EQ0`; fast calibration/adaptation flags including startup, AFE/DFE, bypass, reference-level, IQ, supervisor, TX common-mode, RX detect, VCO wait/calibration, continuous calibration/adaptation, DCC, VPHUD, and VREF status.
- IRQ fields: reset/request/rate/pstate/adaptation IRQ status and clear bits, `IRQ_MASK` and `IRQ_MASK_2`, lane transceiver mode IRQs, RX phase-2 calibration request/disable IRQs, loopback enable IRQs, DCC on-demand IRQ, and TX reset/request IRQs.
- PMA/PCS bridge fields: lane MPLL enable/state overrides, TX/RX request/reset/data-enable overrides, serial and parallel loopback overrides, RTUNE request/ack, MPHY PWM/async/termination controls, and RX adapt phase-adjust map override.
- TX/RX control fields: TX FSM wait and RX detection permissions by power state, TX clock enable/source and beacon wait, TX/RX OCLA fields, RX control FSM enable/rate-change behavior, LOS mask count, RX data-enable override counters, and continuous off-cancellation/adaptation status.
- ATE PCS override fields: RX rate/width/pstate/LPD and loopback overrides, TX pstate/LPD/width/rate/MPLL/async controls, detector RX request, vboost, iboost, beacon, serial loopback, master MPLL loop, and RX/TX override outputs.

Key always-on lane groups for lanes 0-2:

- Adaptation readback/calibration: `AFE_ATT_IDAC_OFST`, `AFE_CTLE_IDAC_OFST`, `RX_ADPT_IQ`, `RX_ADAPT_FOM`, DFE summer/phase/ref-level/data/bypass/error offsets, `RX_IQ_PHASE_ADJUST`, `RX_ADPT_ATT`, `RX_ADPT_VGA`, `RX_ADPT_CTLE`, and DFE taps 1-5.
- Lane calibration/status: MPLLA/MPLLB coarse tune, init power-up done, RX adaptation done, fast flags, common calibration MPLL/RCAL status, and MPLL disable bits.
- Signal-detect and analog RX controls: LOS mask control, signal-detect filter control, stats, RX override outputs for SQ threshold/response/weakkeep/polarity/enable, vrefgen, SQ output, term ACDC/term enable, LF/HF signal-detect enables, signal-detect calibration thresholds, HF/LF tune codes, and VREF pull-up.
- DCC and firmware configuration: RX DCC calibration ICM/IDF/QCM/QDF code registers for two banks, TX DCC bank address/data/control, MPLL background control, firmware MM/adaptation/calibration config, lane transceiver mode override/input, RX signal-detect config, and TX DCC config.

## Control Flow

This chunk has no runtime control flow. Control behavior is indirect: compiled driver code includes this header, selects a register from the companion offset header, then uses these masks/shifts to read-modify-write hardware fields or decode hardware status.

Typical use is expected to be:

1. Read a 16-bit or wider DPCS register through the AMD display register access layer.
2. Isolate a field with `value & FIELD_MASK`.
3. Shift it down with `FIELD__SHIFT` for interpretation, or shift a new value up and combine it with `FIELD_MASK` for writes.
4. Preserve unrelated and reserved bits during read-modify-write operations.

The raw lane 3 definitions expose active controls that affect link training, PMA handshakes, resets, clocks, calibration, loopback, IRQ masking/clearing, and override paths. The always-on lane definitions expose mostly analog calibration, readback, and static control fields replicated per lane.

## State and Persistence Behavior

The macros are compile-time constants and maintain no software state. The state they describe lives in hardware registers:

- Status/readback fields represent volatile hardware state, such as FSM state, IRQ status, calibration done/init flags, ACK bits, signal-detect outputs, DCC codes, and adaptation results.
- Control/override fields persist in hardware register state until changed by the driver, reset by hardware, or affected by power/domain reset behavior.
- Many fields are paired as override value plus override enable bits. Safe use requires programming both consistently; setting an override value without its enable bit, or leaving enable asserted after testing, can hold the PHY in a forced state.
- IRQ clear fields are likely write-one or write-trigger style integration points; callers must use the matching clear mask rather than treating clear registers as ordinary persistent storage.

Because this is a register-mask header, persistence semantics depend on the underlying ASIC register block, not on C storage in this file.

## Dependencies and Integration Points

This header depends only on the C preprocessor. Practical integration depends on surrounding AMDGPU display code:

- Companion generated register offset/address headers for DPCS 4.2.0 provide the actual register addresses. This file provides only shifts and masks.
- AMD display register helpers and macros consume `_MASK`/`__SHIFT` pairs when forming field writes and reads.
- DisplayPort/PHY/link-training paths may use lane PCS/PMA fields for reset sequencing, RX/TX request handshakes, adaptation, equalization, termination, rate/width/pstate selection, loopback, signal detect, and DCC calibration.
- Debug, bring-up, and manufacturing/ATE paths may use the numerous `ATE_*`, `OVRD_*`, `OCLA`, and FSM override fields.

The naming convention is the main contract. Any generated-name drift would break call sites that reference exact macro names.

## Risks and Edge Cases

- Reserved bit handling: the chunk defines reserved masks, but callers should not write reserved fields unless an ASIC sequence explicitly requires it. Read-modify-write helpers should preserve reserved bits.
- Field width correctness is critical. Examples include multi-bit fields for rates, widths, pstate, DFE/adaptation values, DCC calibration codes, RX signal-detect counters, and TX clock select. Incorrect masks can silently corrupt adjacent controls.
- Override controls can destabilize the PHY if left enabled after diagnostics or ATE paths. Value/enable bit pairs are common and should be reviewed together.
- IRQ status and clear definitions are easy to mix up because names differ only by `_CLR` or `_MSK`. Using a clear mask in a status read or masking the wrong interrupt could hide link events.
- This chunk starts mid-register (`RX_ADAPT_FOM`) and ends at the next lane's first comment. Whole-file research/merge must account for adjacent chunks to reconstruct complete lane coverage.
- Lane replication creates copy/paste risk. Lanes 0-2 always-on blocks are structurally parallel; differences should be treated as generated hardware-spec differences, not manually normalized without checking the source generator/spec.

## Test and Validation Signals

Useful validation for this chunk is mostly static and integration-oriented:

- Build coverage: any malformed macro or duplicate conflicting definition should surface through kernel/driver compilation units that include this header.
- Generated-pair checks: every `__SHIFT` in this range has a matching `_MASK` definition count-wise; this chunk has 1,039 of each.
- Mask/shift consistency checks: for non-reserved fields, verify masks line up with the declared shift and expected field width from the ASIC spec.
- Register smoke tests on supported hardware: link training, lane power transitions, RX/TX reset/request handshakes, interrupt status/clear behavior, calibration completion, and DCC/signal-detect readbacks should work when code uses these constants.
- Debugfs or tracing that reads DPCS fields can confirm that decoded values remain plausible for lane number, FSM state, IRQ status, adaptation done flags, and calibration codes.

## Chunk Notes for Merge Lane

This is a partial view of `dpcs_4_2_0_sh_mask.h`. The later merge lane should combine this with neighboring chunks to describe the full generated header. For this chunk specifically, the major source-tree-aligned signal is that it documents DPCS CR4 lane 3 raw digital control/status fields and most of always-on lane 0-2 digital analog/calibration field masks.

### subset-b-002329: lines 97718-100127

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 97718-100127

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask register-field map. It contains no executable logic; it defines C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for 16-bit DPCS register fields. Driver code combines these definitions with the matching DPCS offset header to read, write, or update individual hardware fields safely.

The covered range has three main areas:

- The tail of the `DPCSSYS_CR4_RAWAONLANE3_*` namespace for always-on raw lane 3 receiver adaptation, DFE, signal-detect, DCC, and firmware/configuration fields.
- A parallel `DPCSSYS_CR4_RAWAONLANEX_*` namespace that repeats the same raw always-on lane register schema for an indexed/generic lane-X view.
- The start and most of the `DPCSSYS_CR4_SUPX_*` supervisor/common PHY namespace, including reference clock overrides, MPLLA/MPLLB control, spread-spectrum clocking, bandgap/reference analog controls, RTUNE calibration, PLL power-control state/timers, and analog override/status outputs. The final lines begin the `DPCSSYS_CR4_LANEX_*` lane-X ASIC override namespace.

## Important Definitions

The file section is entirely `#define` constants. There are no functions, structs, enums, or exported symbols beyond macro names. The important API surface is the naming contract:

- `<register>__<field>__SHIFT` gives the right-shift amount for a field.
- `<register>__<field>_MASK` gives the register-word mask for that field.
- Most registers are 16-bit logical fields with masks bounded by `0x0000FFFFL`; reserved regions are explicitly named `RESERVED_*`.

Lane 3 and lane-X raw always-on receiver definitions cover:

- AFE/DFE calibration values such as `DIG_AFE_*_IDAC_OFST`, `DIG_DFE_*_VDAC_OFST`, even/odd reference levels, bypass/error offsets, and DFE tap adaptation values.
- RX adaptation and status fields such as `DIG_RX_ADPT_ATT`, `DIG_RX_ADPT_VGA`, `DIG_RX_ADPT_CTLE`, `DIG_RX_ADPT_DFE_TAP1` through `TAP5`, `DIG_RX_ADAPT_DONE`, and `DIG_RX_ADAPT_FOM`.
- Phase and IQ controls such as `DIG_RX_PHSADJ_LIN`, `DIG_RX_PHSADJ_MAP`, `DIG_RX_IQ_PHASE_ADJUST`, and `DIG_RX_ADPT_IQ`.
- Fast-path bring-up flags in `DIG_FAST_FLAGS` and `DIG_FAST_FLAGS_2`, including startup/adapt/calibration bypass controls and VCO/power-up shortcuts.
- Signal-detect and LOS handling in `DIG_RX_LOS_MASK_CTL`, `DIG_RX_SIGDET_FILT_CTRL`, `DIG_RX_SIGDET_CAL`, `DIG_RX_SIGDET_*_CODE`, `DIG_SIGDET_OUT_OVRD`, and `DIG_SIGDET_OUT_IN`.
- Override outputs for receiver PMA/squelch/termination/vref/signal-detect paths in `DIG_RX_OVRD_OUT_1`, `DIG_RX_OVRD_OUT_2`, and `DIG_RX_OVRD_OUT_3`.
- DCC and calibration storage fields such as `DIG_RX_DCC_CAL_*_CODE_[0|1]`, `DIG_TX_DCC_BANK_ADDR`, `DIG_TX_DCC_BANK_DATA`, `DIG_TX_DCC_CONT`, and `DIG_TX_DCC_CONFIG`.
- Firmware and mode plumbing through `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, `DIG_FW_CALIB_CONFIG`, `DIG_LANE_XCVR_MODE_OVRD_IN`, and `DIG_LANE_XCVR_MODE_IN`.

The supervisor/common `SUPX` definitions cover:

- Identification and input override registers: `DIG_IDCODE_LO`, `DIG_IDCODE_HI`, `DIG_REFCLK_OVRD_IN`, `DIG_SUP_OVRD_IN`, `DIG_PRESCALER_OVRD_IN`, `DIG_SUP_OVRD_OUT`, `DIG_LVL_OVRD_IN`, and ASIC input mirrors.
- MPLLA/MPLLB digital controls: divider/HDMI clock overrides, `MPLLA/MPLLB_OVRD_IN_0..5`, SSC peak/step-size fields, fractional-N quotient/remainder/denominator fields, charge-pump override fields, and corresponding ASIC input fields.
- Analog support controls: prescaler, RTUNE control, bandgap/reference selection, power-measure switch, PLL misc/override/ATB/control/reserved fields for both MPLLA and MPLLB.
- MPLL power-control fields: override, state, DAC max range, lock/stable timers, gearshift/preset timers, PCLK stable and power-down timings, calibration override, analog DAC output, and SSC spread type for both MPLLA and MPLLB.
- Clock/reset and RTUNE sequencing: bandgap and reference power-up timers, VPHUD reference controls, RTUNE enable/fast mode, set/stat values for RX/TX pull-up/down tuning, RTUNE counter timings, and TX calibration code.
- Analog override/status outputs: MPLLA/MPLLB clock/output/reset/calibration override outputs, RTUNE analog override output, analog status, bandgap override output, and PMIX override outputs.

The final register group in scope starts `DPCSSYS_CR4_LANEX_DIG_ASIC_LANE_OVRD_IN` and `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0`, indicating the next chunk continues generic lane-X ASIC lane/TX override fields.

## Control Flow

There is no control flow in this header. Runtime control flow is external:

1. AMDGPU display/DCN code includes the generated DPCS offset header and this shift/mask header.
2. Register helper code calculates the target MMIO address from the offset macro.
3. The helper uses these shift/mask macros to assemble, mask, extract, or update individual bitfields.
4. Hardware state machines in the DPCS/PHY block interpret those fields to control lane adaptation, signal detection, PLL bring-up, bandgap/reference power, and RTUNE calibration.

Because this is a generated register contract, correctness depends on exact field names, shifts, and masks matching the ASIC register database. The header itself does not enforce sequencing, valid values, polling intervals, or reserved-bit preservation.

## State And Persistence

The macros are compile-time constants only. They do not allocate memory or persist software state.

The state they describe is hardware-resident:

- RAWAON lane registers reflect or control per-lane always-on receiver/DFE/adaptation state.
- SUPX registers reflect or control common PHY supervisor state, including reference clocks, bandgap/reference generation, MPLL A/B configuration, PLL lock/power FSM status, and RTUNE calibration state.
- Many fields are override-enable/value pairs. Persistent hardware behavior depends on whether firmware or driver code leaves override bits asserted across link training, suspend/resume, hotplug, or power-gating transitions.
- Reserved masks mark bit ranges that should be preserved during read-modify-write operations unless the ASIC programming guide explicitly says otherwise.

## Dependencies

Primary dependencies are structural rather than call-based:

- `dpcs_4_2_0_offset.h` supplies the register addresses that pair with these field definitions.
- AMDGPU display code includes this header through DCN 3.1 resource setup, notably Yellow Carp/DCN 3.1-era DPCS register support.
- Register access helpers elsewhere in `drivers/gpu/drm/amd/display` depend on the generated mask/shift naming convention to build register-field descriptors.
- The definitions depend on AMD's internal ASIC register database. Hand edits are risky because downstream code expects generated names and exact bit positions.

## Integration Points

This chunk is most relevant to code paths that configure or inspect:

- Display link PHY lane receiver bring-up and adaptation on CR4 RAWAON lane 3 or generic lane-X paths.
- Signal-detect, loss-of-signal masking/filtering, PMA squelch, termination, VREF generation, and DCC calibration.
- MPLLA/MPLLB common PLL setup for DisplayPort/HDMI link clocks, including fractional-N and SSC programming.
- Bandgap/reference and RTUNE calibration used by the PHY before stable link operation.
- Debug or diagnostic paths that read PLL FSM state, lock bits, RTUNE status, DFE tap values, adaptation done bits, or analog status fields.

The lane-specific `LANE3` names and generic `LANEX` names must remain aligned with their corresponding offset ranges. A mismatch between lane 3 offsets and lane-X field masks would compile cleanly but program the wrong hardware bits.

## Risks

- A single incorrect shift or mask can silently corrupt adjacent fields in a hardware register, especially where multiple control bits share one 16-bit word.
- Override-enable/value pairs are easy to misuse: setting a value without the enable bit has no effect, while leaving an enable bit set can bypass firmware or hardware-managed sequencing.
- Reserved-bit masks show many high-bit regions. Runtime writes that do not preserve reserved bits can cause undocumented behavior on real hardware.
- PLL and reference-clock fields are high impact. Wrong MPLLA/MPLLB divider, fractional-N, SSC, power-control, or timer fields can prevent link clock lock or destabilize display output.
- Fast flags and calibration bypass fields can reduce bring-up latency but may hide required calibration time, causing marginal links or intermittent failures.
- This header is generated. Manual fixes in only this file can drift from the matching offset header, other ASIC revisions, or regenerated upstream files.

## Test Signals

Useful validation signals for changes touching this range:

- Preprocess or build AMDGPU/DCN code that includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`; macro-only errors surface at compile time.
- Diff regenerated output against AMD's authoritative DPCS 4.2.0 register database and neighboring ASIC variants to catch accidental field drift.
- On hardware, verify link training and modesets across DP/HDMI paths that exercise MPLLA/MPLLB and raw lane receiver adaptation.
- Confirm PLL lock/status fields (`MPLL_LOCK`, FSM state, output/FB/PCLK enables), RTUNE stat/set fields, and RX adaptation done/FOM/tap values through existing display debug tooling where available.
- Exercise suspend/resume, hotplug, and fast link reconfiguration paths to ensure override and fast calibration bits do not leave stale hardware state.
- Check read-modify-write call sites for reserved-bit preservation when using masks from this range.

## Chunk Boundary Notes

This document covers only lines 97718-100127 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should cover the preceding lane 3 RAWAON definitions before `DIG_AFE_CTLE_IDAC_OFST`; later chunks should continue from `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0` through the rest of the generic lane-X register definitions. The final per-file report should merge all chunks before making complete statements about the whole DPCS 4.2.0 register namespace.

### subset-b-002330: lines 100128-102481

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 100128-102481

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header segment for the `DPCSSYS_CR4` register block. It covers 2,354 lines and defines 2,141 preprocessor constants: 1,072 `__SHIFT` macros and 1,069 `_MASK` macros. The slight mismatch is expected for this sliced range because it starts inside `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0` and ends inside `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN`.

The content is declarative only. It contains no functions, structs, enums, branches, loops, runtime variables, allocation, locking, or persistence code. Its public surface is a large set of C preprocessor constants that describe bit positions and bit masks for 16-bit internal DPCS registers.

## Purpose

The header gives AMDGPU display code symbolic names for DPCS 4.2.0 hardware register fields. Driver code can combine these `*_SHIFT` and `*_MASK` constants with companion register addresses from `dpcs_4_2_0_offset.h` and AMD register access helpers to build read-modify-write operations without hard-coding field locations.

This chunk specifically covers the CR4 lane-template area beginning after the lane override register, including ASIC-facing TX/RX override and input/output fields, TX/RX power control, TX DCC controls, TX clock alignment, RX VCO/CDR/adaptation/status controls, MPHY controls, analog override/status windows, analog TX/RX register fields, two raw memory identifiers, and the beginning of the `RAWLANEX_DIG_PCS_XF` TX/RX crossbar register family.

## Exported API Surface

There are no callable APIs or local types. The exported interface is the generated macro namespace. Most complete fields appear as a pair:

- `DPCSSYS_CR4_*__FIELD__SHIFT` gives the bit offset.
- `DPCSSYS_CR4_*__FIELD_MASK` gives the field mask, usually within a 16-bit register value.

Important macro families in this range:

- `DPCSSYS_CR4_LANEX_DIG_ASIC_*`: ASIC-facing lane, TX, RX, RX EQ, RX CDR/VCO, output, OCLA, and override fields. These expose request, acknowledgement, reset, rate, width, power state, data enable, loopback, beacon, DETRX, clock-ready, low-power detect, CDR tracking, RX alignment, RX VCO/ref load, RX EQ, TX pre/main/post cursor, async drive, VBOOST/IBOOST, and debug output fields.
- `DPCSSYS_CR4_LANEX_DIG_TX_PWRCTL_*`: TX power-state fields for P0, P0S, P1, and P2, TX power-up timing fields, DCC CR-bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment control, and TX LBERT control.
- `DPCSSYS_CR4_LANEX_DIG_RX_PWRCTL_*`: RX power-state and power-up timing fields for P0/P0S/P1/P2 and power sequencing.
- `DPCSSYS_CR4_LANEX_DIG_RX_VCOCAL_*`: RX VCO calibration control, timing, and status fields, including calibration request, clock/data selectors, FSM status, reference and VCO load values, low-frequency indication, and done/busy-style status.
- `DPCSSYS_CR4_LANEX_DIG_RX_CDR_*` and `RX_DPLL_*`: RX CDR control/status and DPLL frequency/bounds fields for lock tracking, SSC/filter configuration, frequency readback, and lock-related diagnostics.
- `DPCSSYS_CR4_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset, ATT/VGA/CTLE/DFE tap status, data/error slicer offsets, slicer controls, DAC select controls, and CR-bank access fields.
- `DPCSSYS_CR4_LANEX_DIG_RX_STAT_*`: RX statistic/match machinery, including data masks, match controls, statistic controls, sample count, statistic counters, calibration comparator clock control, match extensions, and stop control.
- `DPCSSYS_CR4_LANEX_DIG_MPHY_*`: MPHY RX PWM, low-speed termination, and analog PWM clock stable count fields.
- `DPCSSYS_CR4_LANEX_DIG_ANA_*`: digital views of analog TX/RX override outputs and controls, including TX termination code, TX EQ, RX control/power/VCO, RX calibration/DAC/AFE/CTLE/scope/slicer/IQ phase, analog status, MPHY override, signal detect, and TX DCC DAC override fields.
- `DPCSSYS_CR4_LANEX_ANA_*`: analog TX/RX register fields for TX override measurement, power override, alt bus, ATB, DCC DAC/control, termination code, override clock, miscellaneous TX registers, RX clock/CDR/deserializer/slicer/power/squelch/calibration/ATB/force/reserved registers.
- `DPCSSYS_CR4_RAWMEM_DIG_ROM_CMN0_B0_R0` and `DPCSSYS_CR4_RAWMEM_DIG_RAM_CMN0_B0_R0`: raw memory bitfield definitions for ROM and RAM access words.
- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_*`: beginning of raw lane PCS crossbar TX/RX override and input/output fields, covering TX reset/request/DETRX/VBOOST/IBOOST/beacon, TX pstate/LPD/width/rate/MPLL selection, TX acknowledgement and DETRX result, RX rate/width/pstate/LPD/adaptation/data enable/loopback/LOS threshold, RX VCO/ref load overrides, and the start of RX PCS input fields.

## Register Areas Covered

The ASIC override group maps values crossing between the ASIC control side and the lane digital/analog PHY. It provides paired value and override-enable bits for many controls, plus readback fields for acknowledgement and status. TX fields cover request, power state, link rate/width, MPLL B selection, data enable, main/pre/post cursor, async drive, HDMI mode, clock ready, detect-RX, inversion, low-power detect, DC coupling, extended FIFO, MPHY mode, reset, VBOOST, IBOOST, beacon, and TX enable/ack state. RX fields cover request, data enable, power state, link rate/width, RX reference/VCO load values, CDR VCO low-frequency state, CDR tracking and SSC, alignment, clock shift, disable, low-power detect, reset, RX DC coupling, RX LOS/LFPS thresholds, RX data/clock valid, RX EQ adaptation and force state, VCO/ref IQ calibration values, and RX output status.

The TX power-control group defines per-state parameters and wake-up timing. It includes coefficients and completion counters for TX P-states, explicit power-up timing slots, and DCC DAC programming fields. These are the bit definitions a driver or hardware bring-up path would use to tune TX low-power transitions, DCC calibration, and test modes.

The RX power, VCO, CDR, DPLL, and adaptation groups define the receive-side bring-up and calibration contract. They include RX P-state values, power-up timing, VCO calibration requests and status readbacks, CDR tracking/filter/frequency controls, DPLL frequency bounds, adaptation configuration registers, adaptation reset, equalizer/DFE tap status, slicer offsets, DAC control selection, and CR-bank indirection fields.

The RX statistic group exposes hardware match/count infrastructure. It defines masks, match controls, statistic controls, sample count, multiple statistic counter segments, calibration comparator clock control, additional match controls, and stop control. This is primarily diagnostic or validation-oriented rather than normal link-policy logic.

The analog/MPHY groups provide a digital register description for lower-level analog controls and observability. They include TX and RX analog override outputs, TX termination and EQ controls, RX analog power/VCO/calibration/DAC/AFE/CTLE/scope/slicer/IQ controls, analog status, MPHY override, signal-detect override, analog test bus controls, DCC controls, RX clock/CDR/deserializer/squelch/power/calibration, and reserved analog registers.

The raw memory and raw PCS crossbar section begins a lower-level view of the CR4 lane interface. The raw PCS TX/RX groups mirror many of the ASIC-facing concepts using explicit override-value and override-enable fields, plus PCS input/output status. This chunk ends before the RX PCS input group is complete.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior comes from the AMDGPU display driver code that selects these masks and from the DPCS hardware state machines that consume or expose the underlying register bits.

The field names imply these hardware state patterns:

- TX/RX request and acknowledgement handshakes: `REQ`, `RESET`, `ACK`, `TX_ACK`, `RX_ACK`, `EN_*`, and `*_OVRD_EN` fields describe state-machine requests, forced values, and observed completions.
- Link mode and power transitions: `PSTATE`, `RATE`, `WIDTH`, `LPD`, `DATA_EN`, `MPLLB_SEL`, `MPLL_EN`, TX/RX P-state registers, and power-up timing fields are the low-level representation of link rate/lane configuration and low-power entry/exit.
- Calibration and adaptation: VCO/ref load values, CDR controls, DPLL frequency fields, RX AFE/DFE adaptation controls, CTLE/VGA/DFE status, slicer offsets, TX DCC DAC controls, TX EQ cursor fields, and IQ phase fields expose calibration commands and readbacks.
- Debug, test, and manufacturing paths: OCLA, LBERT, RX statistic counters, ATB, scope, MPHY, analog override, raw memory, and CR-bank fields provide observability or forced settings that can bypass normal hardware sequencing.
- Interrupt-like status is not directly represented as a full IRQ block in this chunk, but status/ack/clear-style fields exist in several controller and calibration groups. The header does not encode access semantics such as write-one-to-clear; consumers must rely on the hardware spec and register helper conventions.

No software state is persisted here. Hardware register contents persist only according to ASIC reset, power-domain, firmware, and display-engine sequencing. Reserved fields are explicitly represented by masks and should be preserved by read-modify-write users.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is the DPCS 4.2.0 register database that generated this file and the companion `dpcs_4_2_0_offset.h` address map.

Within this source tree, `dpcs_4_2_0_sh_mask.h` is included by `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` together with `dpcs_4_2_0_offset.h`. The offset header maps the `DPCSSYS_CR4_LANEX_DIG_ASIC_*` window starting at internal addresses around `0x9000`, the TX power-control area around `0x9020`, RX power/VCO/CDR/adaptation/stat areas around `0x9040` through `0x9090`, analog lane areas after that, and the raw PCS crossbar fields in the CR4 raw-lane namespace.

Integration points visible from the names include AMD DC link encoder and PHY programming, DisplayPort/HDMI link training, lane rate/width changes, power-management and suspend/resume flows, TX/RX calibration, receiver equalization, DCC and VCO calibration, factory/ATE paths, debug capture through OCLA/LBERT/stat counters, and low-level PHY diagnostics using analog and raw crossbar registers.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently target an adjacent hardware field during a register update.
- The chunk contains many override value bits adjacent to override enable bits. Setting a value without its enable bit has no intended effect; leaving an enable bit asserted after debug or test use can force hardware away from normal state-machine control.
- Several fields are calibration-sensitive: CDR, DPLL, VCO, DCC, TX EQ, RX adaptation, CTLE/VGA/DFE, slicer, and IQ phase values can destabilize link training or signal integrity if stale or misprogrammed.
- Reserved masks cover large bit ranges. Drivers should preserve reserved bits and avoid treating them as writable scratch space.
- The `LANEX` and `RAWLANEX` naming means this is a lane-template namespace, not a single obvious physical lane from the name alone. Consumers need the companion offset/addressing scheme to select the correct instance.
- The range starts and ends inside logical register groups. Merge/reconciliation should not assume `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0` or `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN` are fully described by this chunk alone.
- Many diagnostic and analog override fields are powerful enough to interfere with normal display operation, hotplug handling, and power sequencing if used outside controlled bring-up or validation paths.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile/preprocess AMDGPU DCN 3.1 code that includes `dpcs_4_2_0_sh_mask.h` through `dcn31_resource.c`.
- Static checks that every complete register group has matching `__SHIFT` and `_MASK` definitions; for this sliced chunk, expect 1,072 shifts and 1,069 masks because the line range crosses group boundaries.
- Consistency checks against `dpcs_4_2_0_offset.h` so every complete register-family prefix in this chunk has a corresponding `ixDPCSSYS_CR4_*` address define.
- Generated-register comparison against adjacent DPCS versions or regenerated headers to catch accidental field-width, reserved-bit, suffix, or mask-format changes.
- Runtime display tests on hardware using DPCS 4.2.0: DisplayPort and HDMI link training, lane-count/rate changes, hotplug, suspend/resume, low-power entry/exit, TX/RX request-ack transitions, TX/RX calibration, DCC, VCO/CDR/DPLL behavior, RX adaptation/equalization, and link recovery.
- Debug/validation readbacks should show plausible transitions for TX/RX P-state programming, power-up timing, reset/request acknowledgements, VCO calibration status, CDR lock/frequency status, adaptation status, DFE/CTLE/VGA status, TX DCC acknowledgement, statistic counters, OCLA/LBERT signals, and raw PCS crossbar acknowledgements.

## Chunk Notes For Merge

This document intentionally covers only lines 100128-102481 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should include the CR4 supervisor/supply and the beginning of `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0`; later chunks should complete `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN` and continue the raw lane register families. The final merged per-file report should describe the whole file as a generated ASIC bitfield map for DPCS 4.2.0 rather than handwritten driver logic, with `dcn31_resource.c` and the matching offset header as primary in-tree integration anchors.

### subset-b-002331: lines 102482-103385

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 102482-103385

## Purpose

This chunk is the final slice of AMD's generated DPCS 4.2.0 shift/mask header. It contains no executable C logic; it exports preprocessor constants that describe bit positions and masks for DPCS/RDPCS hardware registers used by AMDGPU display link-encoder code. Runtime code pairs these constants with offsets from `dpcs_4_2_0_offset.h` so register helpers can pack, update, or extract individual MMIO fields safely.

The requested range covers 785 `#define` lines across 115 register comment blocks: 391 `__SHIFT` macros and 414 `_MASK` macros. The extra masks are caused by the artificial chunk boundary, which starts at the tail of `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN` masks after that register's shifts appeared in the previous chunk. This range then covers RX PCS input/status fields, ATE and override controls, RX equalization and calibration controls, DPCS micro-FSM controls and monitors, interrupt status/mask/clear fields, PMA crossbar override fields, TX/RX control registers, and the final header guard `#endif`.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or runtime APIs in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a DPCS register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or preserving that field during read-modify-write operations.

Major macro families in this range:

- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN*`: RX request/rate/width/P-state/low-power/reset state, reference load value, VCO load value, AFE/DFE adaptation enables, CTLE/VGA/attenuation/equalizer tap fields, and continuous adaptation/off-cancellation controls.
- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_OVRD_OUT*`, `RX_PCS_OUT`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, and `RX_TX{PRE,MAIN,POST}_DIR`: RX acknowledge, RX clock/valid override output, adaptation acknowledge, figure-of-merit, and transmitter coefficient direction feedback fields.
- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_ATE_*` and related override inputs: automated-test or manufacturing override paths for RX/TX reset/request/data enable, adaptation AFE/DFE enable, rate, width, P-state, low-power detect, loopback, async data, beacon, VBoost, IBoost, master MPLL state, VCO/ref load values, LOS/LFPS threshold, and continuous adaptation/off-cancellation selection.
- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_EQ_*`, `TXRX_TERM_CTRL*`, and `RX_PH2_CAL`: RX equalization override values for AFE gain, attenuation, DFE tap, CTLE boost/pole, delta IQ, TX/RX termination control, and phase-2 calibration request/acknowledge bits.
- `DPCSSYS_CR4_RAWLANEX_DIG_FSM_*`: micro-FSM override control, current memory address, status bits, fast calibration/adaptation bypass controls, common calibration status, fast flag aggregation, CR register/memory locks, TX DCC flags/status, OCLA debug enables, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANEX_DIG_IRQ_CTL_*`: RX/TX reset/request/rate/P-state/adaptation/phase-calibration/loopback/DCC interrupt status bits, clear bits, and interrupt masks.
- `DPCSSYS_CR4_RAWLANEX_DIG_PMA_XF_*`: PMA crossbar override inputs/outputs for MPLLA/MPLLB lane enable, supervisor state, TX/RX request/reset/data-enable/asynchronous/loopback controls, PMA acknowledge inputs, lane retune request/acknowledge, MPHY PWM/async/term controls, and RX IQ phase adjust override.
- `DPCSSYS_CR4_RAWLANEX_DIG_TX_CTL_*` and `RX_CTL_*`: TX FSM timing and RX detect allowance by power state, TX clock selection and async beacon wait, DCC continuous status, OCLA visibility, RX control FSM enable, LOS mask count, RX data enable override timing, and RX adaptation/off-cancellation continuous status.

All fields in this slice are 16-bit-style masks within `0x0000FFFFL`, even though the macro values are expressed as long constants. Reserved fields are explicitly named and masked; consumers should preserve them unless hardware documentation says otherwise.

## Control Flow

This header has no runtime control flow. It supplies constants to code that performs the actual sequencing:

1. DCN 3.1-family resource code includes `dpcs_4_2_0_offset.h` and this shift/mask header.
2. Register-list macros such as `DPCS_DCN31_REG_LIST(id)` select DPCS/RDPCS register offsets for each link encoder instance.
3. `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` populate the link encoder shift and mask tables.
4. Runtime link-encoder code uses AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` against those tables while bringing up, training, disabling, or debugging links.

The macros do not encode ordering requirements. Consumers must still sequence PLL and clock enablement, power-state transitions, reset/request handshakes, RX/TX data enablement, calibration/adaptation, DCC, loopback, interrupt clear/mask operations, and suspend/resume restore in the correct hardware order.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state in the DPCS lane/PCS/PMA interface:

- Link lane state for RX/TX request, reset, acknowledge, rate, width, P-state, low-power detect, clock/data enable, RX valid, lane number, and lane loopback.
- Analog and calibration state for VCO/ref load values, CTLE/VGA/DFE/equalizer settings, IQ phase offset, RX phase-2 calibration, RX adaptation acknowledge/FOM, TX coefficient direction feedback, TX/RX termination, DCC, RCAL, and common MPLL calibration.
- Override state for ATE/manufacturing paths and software-forced PMA/PCS values, including paired value/enable bits throughout the RX, TX, PMA, MPHY, MPLL, and continuous adaptation controls.
- Micro-FSM state for override execution, jump address, command start, break, current memory address, command-ready flag, ALU flags, wait count, CR locks, fast calibration/adaptation flags, and OCLA debug visibility.
- Interrupt state for RX and TX events, interrupt masks, and explicit clear fields.

Persistence is hardware-defined. Configuration and override fields can remain programmed until modeset, link retraining, power gating, suspend/resume, driver reset, or ASIC reset. Status, acknowledge, interrupt, calibration, clear, and monitor fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while related clocks and power domains are active. This generated header does not distinguish those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DPCS 4.2.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides the matching MMIO offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`, which defines `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`.
- DCN 3.1-family resource files that instantiate link encoder register, shift, and mask tables using the DPCS macros, including `dcn31_resource.c`, `dcn314_resource.c`, `dcn315_resource.c`, and `dcn316_resource.c`.

In the inspected tree, `dcn31_resource.c` directly includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`, then initializes `link_enc_regs`, `le_shift`, and `le_mask` with `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(...)`. Later DCN resource files either reuse the same mask-list pattern or comment it out for hardware generations that moved away from this DPCS table shape.

The behavioral integration is display link management: DP/HDMI/USB-C alternate-mode PHY control, lane power and clock control, PLL state, transmitter and receiver data paths, calibration/adaptation, loopback/test paths, and DPCS debug/interrupt handling.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while programming the wrong MMIO bit, corrupting an adjacent field, failing to preserve reserved bits, or silently breaking only one lane state.
- The range is chunk-boundary sensitive. It starts with the last masks for `RX_PCS_IN` while the matching shifts are in the previous chunk, so whole-register consistency checks must merge adjacent chunks.
- Override registers are high risk because many fields use paired value/enable bits. Setting an override value without the enable bit, or leaving an enable bit asserted after test/debug use, can pin RX/TX reset, request, data enable, loopback, MPLL, LOS, or adaptation state.
- Calibration and adaptation fields are timing-sensitive. Incorrect VCO/ref load, CTLE/VGA/DFE, IQ phase, DCC, RCAL, or continuous adaptation controls can cause link training failures, marginal signal integrity, resume-only failures, or rate-specific instability.
- Interrupt and clear fields are side-effect-sensitive. Confusing status, mask, and clear bits can cause missed RX/TX state changes, stuck DCC or loopback interrupts, or interrupt storms.
- PMA/PCS crossbar fields bridge digital control into analog PHY behavior. Wrong PMA override, MPHY PWM/async, MPLL state, retune, or lane enable fields can break DP Alt Mode, USB-C muxing, low-power transitions, or multi-lane link bring-up.
- The header does not encode read-only, write-one-to-clear, sticky, or self-clearing semantics. Any tooling that blindly writes every mask in the range would be unsafe.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support with DCN 3.1, DCN 3.1.4, DCN 3.1.5, and DCN 3.1.6 resource paths enabled. Missing or renamed DPCS shift/mask macros should fail in link encoder table construction.
- Mechanically verify that every field in lines 102482-103385 has the expected `__SHIFT`/`_MASK` pair, allowing the known artificial-boundary exception for `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN` masks whose shifts are immediately before this range.
- Diff this chunk against AMD's authoritative DPCS 4.2.0 register database and against nearby generated DPCS/RDPCS headers where compatible field layouts are expected.
- Exercise real DCN 3.1-family hardware across DP and HDMI link bring-up, link retraining, hotplug, suspend/resume, lane-count and link-rate changes, USB-C/DP Alt Mode if available, and low-power state transitions.
- Validate calibration/adaptation paths by checking stable links at high data rates, no repeated training fallback, no clock/data-enable timeouts, and no signal-integrity regressions after resume or mode changes.
- Test interrupt behavior by forcing RX/TX reset/request transitions, adaptation requests, phase calibration, loopback enablement, and DCC on-demand events where supported, then checking that status, mask, and clear handling does not leave stale or storming interrupts.
- Use debug/OCLA and FSM monitor fields to confirm expected FSM state progression, command-ready behavior, calibration completion, and absence of CR lock or ALU/wait-count anomalies.
- Watch kernel logs and display diagnostics for AUX/link-training timeouts, blank display after modeset, high-rate-only failures, DP Alt Mode failures, stuck low-power state, repeated hotplug events, or resume-only display loss.

## Cross-Chunk Notes

Previous chunks cover the beginning of the `DPCSSYS_CR4_RAWLANEX` DPCS namespace and the missing `RX_PCS_IN` shifts for the first masks in this range. This chunk reaches the physical end of `dpcs_4_2_0_sh_mask.h`; there is no later chunk for this file after line 103385. The final per-file research document should merge this tail with earlier chunks before making complete claims about all DPCS 4.2.0 register fields.
