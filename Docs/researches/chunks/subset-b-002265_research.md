# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 14651-17088

## Purpose

This chunk is generated AMD DPCS 3.1.4 register-field metadata. It contains no executable C logic; it exports preprocessor constants that encode bit shifts and masks for display PHY controller and DPCS lane registers. Driver code pairs these `__SHIFT` and `_MASK` values with the companion DPCS offset header so AMDGPU display register helpers can pack, update, and decode individual MMIO fields safely.

The requested range is a mid-file slice of `dpcs_3_1_4_sh_mask.h`. It starts inside the `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P0S` register field group, covers a large CR0 lane/transceiver area, crosses an `addressBlock: dpcssys_cr1_rdpcstxcrind` marker, and ends inside the CR1 super-digital MPLLB divider override group. The chunk contains 2,438 lines, 2,143 `#define` entries, 1,068 `__SHIFT` macros, 1,098 `_MASK` macros, and 285 distinct register-comment groups. The imbalance between shift and mask counts is expected for this artificial chunk because it begins and ends inside register-field sequences.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, memory allocations, locks, or callable APIs in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the field bit position within a 16-bit DPCS register.
- `<REGISTER>__<FIELD>_MASK`: the field mask used for read-modify-write preservation, extraction, and value packing.

Major register families in this chunk:

- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_*`: TX p-state definitions for P0S/P1/P2, TX reference/clock/reset/serial/data enable bits, RX-detect and VBOOST permission, TX power-up timing, DCC bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT control.
- `DPCSSYS_CR0_LANEX_DIG_RX_PWRCTL_*`: RX p-state definitions for P0/P0S/P1/P2, RX AFE/clock/deserializer/CDR/VCO/digital-clock enables, RX power-up timing, and clock-delay setup.
- `DPCSSYS_CR0_LANEX_DIG_RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*`: RX VCO calibration control/status/timing fields, CDR calibration and override fields, CDR status, DPLL frequency, and upper/lower frequency bounds.
- `DPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration, thresholds, adaptation reset, ATT/VGA/CTLE/DFE status, even/odd DFE VDAC offsets, slicer controls, error slicer levels, DAC selector fields, and CR bank address/data.
- `DPCSSYS_CR0_LANEX_DIG_RX_STAT_*`: RX statistic/match controls, statistic counters 0-6, sample count, comparator clock control, match controls, stop controls, and data masks.
- `DPCSSYS_CR0_LANEX_DIG_MPHY_*` and `DPCSSYS_CR0_LANEX_DIG_ANA_*`: MPHY PWM/termination controls, digital-to-analog TX/RX override outputs, TX equalization and DCC override fields, RX AFE/CTLE/scope/slicer/IQ/calibration controls, analog status, RX termination, MPHY override, and signal-detect override fields.
- `DPCSSYS_CR0_LANEX_ANA_*`: low-level analog TX/RX register fields, many of which expose only reserved, no-connect, or high-byte masks in this generated slice.
- `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_*` and `PMA_XF_*`: raw-lane PCS/PMA crossbar override/input/output/status fields for TX and RX p-state, low-power detect, width, rate, MPLL selection/enables, reset/request/ack handshakes, loopback, async data, RX adaptation requests, VCO/reference load overrides, termination controls, phase-2 calibration, lane number, ATE override, and RX EQ override.
- `DPCSSYS_CR0_RAWLANEX_DIG_FSM_*`: FSM override control, memory address and status monitors, fast calibration/adaptation/power-up flags, common calibration status, CR lock, TX DCC flags/status, OCLA enables, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR0_RAWLANEX_DIG_IRQ_CTL_*`: reset/request/rate/p-state/adaptation/phase-2-calibration/loopback/DCC/TX IRQ status bits, clear bits, and IRQ mask registers.
- `DPCSSYS_CR0_RAWLANEX_DIG_TX_CTL_*` and `RX_CTL_*`: TX/RX FSM controls, TX clock control, TX DCC continuous status, OCLA controls, RX LOS mask, RX data-enable override, and continuous adaptation/off-cancellation status.
- `DPCSSYS_CR1_SUP_DIG_*`: beginning of the next CR1 address block, including refclock override fields and MPLLA/MPLLB divider and HDMI-clock override fields.

Several register names are only comments with no field macros in this exact range, especially some analog low-level placeholders such as `DPCSSYS_CR0_LANEX_ANA_RX_CLK_1`, `ANA_RX_CLK_2`, `ANA_RX_CDR_DES`, `ANA_RX_SLC_CTRL`, `ANA_RX_PWR_CTRL2`, and `ANA_RX_CAL1`. Those comments still indicate generated register map entries, but the visible bitfields are either absent, reserved elsewhere, or outside the chunk.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display PHY and link code:

1. DPCS 3.1.4 code includes this shift/mask header together with the matching offset header.
2. Register-list macros token-paste register and field names into generated tables or inline register-helper calls.
3. Driver paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and field-specific wrappers to manipulate TX/RX power states, lane width/rate, PLL selection, calibration, adaptation, IRQ masks, and diagnostic/status fields.
4. Hardware sequencing remains in the caller: the macros only describe bit layout and do not enforce reset ordering, PLL enable timing, p-state transitions, calibration waits, IRQ acknowledgement, or suspend/resume restoration.

The implied hardware control flow in this chunk centers on lane bring-up and maintenance: configure ref clocks and MPLL selection, set TX/RX p-state power bits and timing, enable or override PCS/PMA handshakes, run VCO/CDR/DPLL and RX adaptation calibration, poll status/done bits, manage IRQ masks and clears, and optionally use LBERT/OCLA/statistic/scope registers for diagnostics.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed DPCS hardware state:

- TX lane state for analog reference generation, VCM hold, clocks, reset, serial/data enablement, RX-detect, VBOOST, DCC compensation, clock alignment, beaconing, loopback, and LBERT pattern/error injection.
- RX lane state for AFE/clock/deserializer/CDR/VCO/digital-clock enablement, p-state selection, VCO calibration, CDR/DPLL tracking, adaptation, slicer levels, DFE offsets, signal detect, LOS/LFPS, and RX data-valid overrides.
- PCS/PMA crossbar state for reset/request/ack handshakes, lane width/rate/p-state/low-power detect, master MPLL states, async data, loopback, terminations, phase-2 calibration, and ATE overrides.
- Calibration and diagnostic state for FSM status, fast-calibration flags, common calibration done bits, RX statistic counters, comparator/match controls, OCLA enables, analog status, and TX/RX DCC status.
- IRQ state for RX/TX reset and request events, rate and p-state changes, adaptation request/disable, phase-2 calibration request/disable, lane loopback events, DCC on-demand events, clear strobes, and mask bits.
- CR1 super-digital state for reference clock source/range, bandgap and HDMI mode overrides, and MPLLA/MPLLB divider and HDMI clock override fields.

Persistence is hardware-defined. Configuration fields generally retain values until link retraining, modeset, lane power transition, PHY power-gating, suspend/resume, driver reset, or ASIC reset. Status, IRQ, clear, calibration-done, lock, self-clear, and monitor fields may be read-only, sticky, write-one-to-clear, transient, or valid only while the relevant PHY clocks and power domains are active. This generated header does not encode access semantics; consuming code and the hardware register specification must supply them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DPCS 3.1.4 register database and must remain synchronized with the companion offset header for the same hardware generation:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`
- Other chunks of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h`

The expected integration points are AMDGPU display PHY, link encoder, DPCS, DCN resource, and DMUB or link-service code that programs DPCS registers through generated register tables. The CR0 `LANEX` and `RAWLANEX` names indicate per-lane transceiver fields, while the CR1 `SUP_DIG` fields indicate shared/supervisor clock and PLL controls. Consumers must use these field constants with the corresponding register offsets, base indices, and silicon-specific sequencing tables.

This chunk is tightly coupled to display link behavior. Field mistakes can affect DisplayPort or HDMI link training, lane power state transitions, high-speed rate/width changes, PLL/MPLL selection, RX adaptation, low-power modes, loopback/ATE diagnostics, PHY interrupts, and suspend/resume restoration.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while touching the wrong hardware bit, preserving the wrong reserved bits, or corrupting an adjacent field during read-modify-write.
- The file is generated metadata. Manual edits risk divergence from AMD's register database, the matching offset header, firmware expectations, and silicon documentation.
- The chunk boundary is artificial. The first lines are only the tail of `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P0S`, and the final lines stop inside the CR1 supervisor PLL override area; adjacent chunks are required before making whole-register or whole-file claims.
- TX/RX power and p-state fields are sequencing-sensitive. Incorrect masks around analog clocks, reset, serial/data enablement, VBOOST, RX detect, VCO/CDR enables, or digital clocks can produce link-training failures, intermittent display loss, or power-state bugs that only appear during modeset, hotplug, low power, or resume.
- Calibration fields are side-effect-sensitive. VCO, CDR, DPLL, RX adaptation, DCC, RCAL, phase adjustment, and phase-2 calibration fields may involve start/done/ack semantics; confusing status with control bits can cause stuck calibration or invalid analog settings.
- IRQ clear and mask registers are easy to misuse. A wrong clear or mask field can create missed PHY events, stuck interrupts, interrupt storms, or stale rate/p-state/adaptation notifications.
- Repeated override and ATE patterns are copy-sensitive. Fields such as `*_OVRD_VAL`, `*_OVRD_EN`, PCS/PMA input/output, raw-lane and ATE variants look similar but have different direction and side effects.
- Reserved and no-connect fields are numerous in this range. Consumers should preserve reserved bits unless the hardware specification explicitly says otherwise; writing visible reserved masks as data can be harmful.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU display support for ASICs that consume DPCS 3.1.4. Missing or renamed macros should fail in generated register-table construction or field-helper use.
- Mechanically verify that fields in lines 14651-17088 have matching `__SHIFT` and `_MASK` definitions where both sides are inside the range, while allowing boundary exceptions at the start of `TX_PSTATE_P0S` and the end of the CR1 supervisor PLL groups.
- Diff this range against AMD's authoritative DPCS 3.1.4 register database and nearby DPCS versions where the PHY layout is expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across lane counts, link rates, hotplug, unplug/replug, modeset, link retraining, low-power entry/exit, and suspend/resume.
- Validate PHY calibration and adaptation by checking VCO/CDR/DPLL lock and done statuses, RX adaptation status fields, DCC/RCAL status, and absence of repeated retraining or timeout logs.
- Exercise IRQ paths for RX/TX reset/request, rate changes, p-state changes, adaptation request/disable, phase-2 calibration, loopback, and DCC events; verify clear bits do not leave stuck status.
- Use diagnostics where available: LBERT, OCLA, RX statistic counters, analog status/scope, loopback, and ATE override paths can reveal bitfield drift that normal display modes do not cover.
- Watch kernel logs and display diagnostics for AUX/link-training failures, blank displays, CRC or error-counter growth, hotplug storms, PHY timeout messages, stuck interrupts, audio/video loss after resume, and failures limited to specific rates or lane widths.

## Cross-Chunk Notes

Previous chunks own the opening portions of `dpcs_3_1_4_sh_mask.h`, including the beginning of the CR0 DPCS register namespace and the start of the `TX_PSTATE_P0S` field group. Later chunks continue the CR1 supervisor register block after `DPCSSYS_CR1_SUP_DIG_MPLLB_DIV_CLK_OVRD_IN` and cover the remaining DPCS 3.1.4 register-field namespace. The final per-file research document should merge all chunks before making complete claims about all DPCS 3.1.4 registers, all CR0/CR1 address blocks, or all lane and supervisor PHY controls.
