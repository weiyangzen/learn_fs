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
