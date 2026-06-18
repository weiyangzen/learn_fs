# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 56734-59163

## Purpose

This chunk is generated AMD DCN 3.2 register field metadata. It contains no executable C code; it publishes preprocessor constants that describe bit positions and bit masks for a slice of the DCN 3.2 `C20_PHY_CR0` PHY/register namespace. Consumers pair these `*_SHIFT` and `*_MASK` macros with register offsets from `dcn_3_2_0_offset.h` to build typed-ish register helper tables for `REG_GET`, `REG_SET`, `REG_UPDATE`, DMUB register access, and related AMDGPU display code.

The requested range starts in the middle of `C20_PHY_CR0_SUP_DIG_MPLLA_OVRD_IN_0`, covers many complete supervisor/common PHY register groups, and stops at the comment for `C20_PHY_CR0_LANE0_DIG_ASIC_LANE_OVRD_IN` before that lane register's fields. The range contains 2,154 `#define` lines under 276 register comments. Although the repository path is under a local `ceph-client` source mirror, this header is AMDGPU display hardware metadata and has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset of a field within the register.
- `<REGISTER>__<FIELD>_MASK`: bit mask of that field within the same register.
- `RESERVED_*` fields: generated masks/shifts for reserved bit ranges; these are useful for consistency checks but should not be treated as writable feature fields unless hardware documentation explicitly says so.

Major register families in this slice:

- `C20_PHY_CR0_SUP_DIG_MPLLA_*` and `C20_PHY_CR0_SUP_DIG_MPLLB_*`: MPLL A/B enable, reference dividers, word/TX clock dividers, multipliers, bandwidth thresholds, VCO charge-pump/proportional controls, fractional/SSC controls, divisor clock inputs, calibration, tune, power FSM timing, and status.
- `C20_PHY_CR0_SUP_DIG_SUP_*`, `ASIC_IN/OUT`, and `LVL_*`: supervisor override/input/output paths for resets, power, reference and internal clocks, lane activity, PLL selection, bandgap/reference supplies, test clocks, PMA/PCS power state, and misc override enables.
- `C20_PHY_CR0_SUP_DIG_RTUNE_*`: RTUNE configuration, status, set values, observed RX/TX termination values, termination codes, and fast flags.
- `C20_PHY_CR0_SUP_DIG_CLK_RST_*`: bandgap and reference clock reset/power-up timing and status.
- `C20_PHY_CR0_SUP_DIG_ANA_XF_*` and `*_ANA_CREG*`: analog cross-fabric status/override outputs and analog control-register bit definitions for supervisor, MPLLA, and MPLLB analog blocks.
- `C20_PHY_CR0_RAWCMN_DIG_*`: raw common digital control/status, clock gating, MPLL configuration/input, ATE ALU test access, firmware power-up/config status, async/recal controls, config master version, CTLE offset configuration, context restore requests, context selection overrides, supervisor/MPLL context configuration, and always-on SRAM/MPLL/RTUNE control/status.
- `C20_PHY_CR0_RAWCMN_DIG_AON_*`: always-on SRAM power gating, MPLL tune banks and tune-done flags, recalibration bank selection, power-gating and supervisor overrides, common calibration statuses, RTUNE captured values for banks 0 through 7, SRAM boot/load/init controls, firmware/raw version fields, APB timeout configuration, supervisor clock/power status, metadata location, and SRAM recovery address fields.

Representative fields include PLL enable override value/enable pairs, `REF_CLK_*_DIV`, `MPLL*_MULTIPLIER`, SSC step/peak/fractional numerator-denominator-remainder fields, `RTUNE_*` calibration fields, `FW_PWRUP_DONE`, `SRAM_INIT_DONE`, `APB_TIMEOUT_VAL`, `PMA_PWR_STABLE`, `PCS_PWR_STABLE`, firmware stop request/ack override fields, and SRAM/metadata address fields.

## Control Flow

This header has no runtime control flow. It participates in compile-time macro expansion:

1. DCN 3.2 code includes `dcn_3_2_0_offset.h` and this `dcn_3_2_0_sh_mask.h` file.
2. Register table macros paste register and field names into the generated symbols. For DMUB, `FD_SHIFT(reg, field)` expands to `reg__field__SHIFT`, and `FD_MASK(reg, field)` expands to `reg__field_MASK`.
3. Resource, IRQ, clock manager, GPIO, and DMUB code store offsets, masks, and shifts in per-block register structures.
4. Runtime register helpers use those structures to shift, mask, read, update, and poll hardware registers during display initialization, link/PHY programming, power transitions, firmware bring-up, and debug/status collection.

The macros do not encode sequencing. Consumers still own PLL programming order, firmware/SRAM loading handshakes, calibration and recalibration timing, APB timeout behavior, power-gating transitions, and any write-one-to-clear or sticky status handling.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed DCN 3.2 PHY state. The represented hardware state includes:

- MPLL A/B configuration, spread-spectrum/fractional settings, VCO/tuning values, calibration controls, power FSM timers, and PLL status.
- Supervisor clock/reset/power inputs and outputs, including PMA/PCS power enable/stable signals, clock selection/enables, firmware stop request/ack overrides, and test clock controls.
- RTUNE calibration state, termination setpoints, captured RX/TX termination values, and banked always-on RTUNE readings.
- SRAM and firmware boot state, including SRAM load/bypass/init flags, firmware/raw version words, metadata location, and SRAM recovery address fields.
- Always-on and raw-common context restore, context selection, tune-bank selection, recalibration, APB timeout, clock-gate, ATE/debug, and analog cross-fabric state.

Persistence is hardware-defined. Some configuration registers can retain values until a modeset, link reconfiguration, power gating, firmware reset, suspend/resume, or ASIC reset. Status/calibration/version fields can be read-only, latched, sticky, self-clearing, or valid only after a specific PHY firmware or power-state transition. This generated header does not mark access direction or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which provides the matching register offsets.
- AMD's generated DCN 3.2 register database, since the constants are hardware ABI rather than driver-owned values.
- Register helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Direct include sites for the DCN 3.2 offset and mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`

The broader integration point is PHY bring-up and link operation. The fields in this chunk correspond to low-level PHY PLL, calibration, RTUNE, power, SRAM, APB, analog override, and firmware status surfaces that are likely programmed directly by display firmware/BIOS/DMUB paths or used by kernel-side DCN register tables when a field appears in a local register-list macro.

## Risks And Edge Cases

- Bitfield drift is the main risk. A wrong shift or mask compiles cleanly but causes the driver or firmware-access layer to update the wrong hardware bits.
- The file is generated and untyped. Nothing prevents code from using a reserved mask, applying a field to the wrong register, or using a value wider than the field unless helper code validates it.
- PLL and clock fields are timing-sensitive. Bad MPLL divider, multiplier, VCO, SSC, bandwidth, or tune constants can lead to link-training failures, unstable pixel/link clocks, blank displays, or failures only at specific DP/HDMI rates.
- Override-enable pairs are easy to misuse. Setting an override value without the corresponding override enable, or leaving an override enabled after calibration, can mask firmware/hardware state-machine control.
- SRAM, firmware, and APB fields affect initialization plumbing. Incorrect SRAM load/bypass/init, firmware stop/ack, metadata address, recovery address, or timeout fields can break PHY firmware boot, recovery, or low-power resume.
- RTUNE and analog cross-fabric fields affect signal integrity. Errors may appear as marginal links, intermittent hotplug/link training failures, CRC errors, or problems only on certain boards, cables, lanes, or temperatures.
- The chunk boundaries are artificial. The first lines omit the beginning of `C20_PHY_CR0_SUP_DIG_MPLLA_OVRD_IN_0`, and the final line is only the next lane-register comment; adjacent chunks are needed for complete file-level coverage.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.2 support enabled; missing or renamed field macros should fail in DCN 3.2 resource, IRQ, clock, GPIO, DMUB, and any PHY-related register-table code that references them.
- Mechanically verify that every non-reserved field in this line range has coherent `__SHIFT` and `_MASK` definitions, and that masks align with their shifts and apparent field widths.
- Diff this range against AMD's authoritative DCN 3.2 register database and related generated headers, especially `dpcs_4_2_3_sh_mask.h`, where the same `C20_PHY_CR0` field names appear.
- Exercise DP and HDMI modes across low and high link/pixel rates, with spread-spectrum/fractional PLL cases where available, and watch for link-training failures, clock instability, blanking, underflow, or visual corruption.
- Test suspend/resume, display hotplug, panel power transitions, firmware/DMUB PHY initialization, and PHY power down/up paths; failures here would implicate the SRAM, firmware status, APB, supervisor, and always-on fields.
- Monitor kernel logs and display diagnostics for AUX/link errors, PLL lock/calibration timeouts, PHY firmware init timeouts, RTUNE/calibration failures, APB timeouts, stuck firmware stop acknowledgements, and resume regressions.

## Cross-Chunk Notes

Earlier lines own the start of the MPLLA override register and preceding supervisor PHY definitions. Later lines continue with lane-level `C20_PHY_CR0_LANE0_DIG_*` masks and the remaining DCN 3.2 field namespace. The final per-file research document should merge adjacent chunks before making complete claims about all C20 PHY, lane, or DCN 3.2 mask coverage.
