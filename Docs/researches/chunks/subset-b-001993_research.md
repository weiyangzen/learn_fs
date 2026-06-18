# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 156394-158822

## Chunk Scope

This chunk is a generated AMD DCN 3.2.0 register shift/mask header segment. It contains C preprocessor constants only: generated register grouping comments plus `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no C functions, structs, enums, global variables, locks, allocation paths, branches, loops, or direct MMIO operations in these lines.

The selected range has 2,429 source lines, 2,157 `#define` entries, and 270 generated register comments. It starts in the middle of `C20_PHY_LANE1_PIPE2_UPCSLANE_PIPE_LPC_PHY_C20_VDR_RECAL_SKIP_EN`, covers the end of one lane1/pipe2 C20 VDR group, then covers a large `addressBlock: c20_phy_cr3_rdpcspipecrind` region for CR3 supervisor/common PHY registers. It ends at the grouping comment for `C20_PHY_CR3_RAWCMN_DIG_AON_SRAM_IN`; the field macros for that final register are in the next chunk.

Although this file is under a mirrored `ceph-client` source tree, this content is AMDGPU display-driver ASIC metadata for DCN 3.2 hardware, not distributed filesystem code.

## Purpose

`dcn_3_2_0_sh_mask.h` publishes the field-level bit layout for DCN 3.2.0 registers. The matching offset header identifies register addresses; this header supplies bit positions and masks that AMD Display Core and DMUB register helpers use to pack values into hardware registers, preserve unrelated fields during read/modify/write updates, and decode status fields read from hardware.

At the hardware level, this chunk describes:

- The tail of lane1 pipe2 C20 VDR recalibration/deskew controls, including recalibration skip, line-to-line and clock deskew enable overrides, and global recal/deskew override enables.
- CR3 supervisor-digital identification, reference-clock override, HDMI mode/rate-related PLL controls, MPLLA/MPLLB divider, multiplier, bandwidth, VCO, fractional, and spread-spectrum fields.
- CR3 supervisor input, ASIC input, and override-output surfaces for PLLs, bandgap/reference clocks, firmware clock requests, level controls, TX termination offsets, RTUNE controls, calibration/status, power timing, analog crossover, and analog CREG payloads.
- CR3 RAWCMN common controls, clock gates, ATE ALU debug registers, firmware/static configuration status, async MPLL override, fractional update triggers, configuration versioning, CTLE offset settings, context-restore controls, context payload registers for supervisor/MPLLA/MPLLB, and always-on tune/SRAM/power-gate/supervisor/RTUNE status fields.

The macros do not encode access type, reset values, sequencing, or semantic enumerations. Those rules live in the hardware specification and in the DCN/DMUB/link code that consumes these constants.

## Important Macro Groups

The generated macro naming convention is the interface:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register position.
- `//<REGISTER>` comments define the register grouping used by generated tooling and by humans reviewing the header.
- Prefixes such as `C20_PHY_CR3_SUP_DIG_*` and `C20_PHY_CR3_RAWCMN_DIG_*` identify the CR3 C20 PHY address block and sub-block.

Important groups in this chunk:

- `C20_PHY_LANE1_PIPE2_UPCSLANE_PIPE_LPC_PHY_C20_VDR_*` finishes C20 VDR recalibration skip, deskew, and override controls for lane1/pipe2. These fields are value or enable bits for MPLLA/MPLLB/TX/RX recalibration and deskew behavior.
- `C20_PHY_CR3_SUP_DIG_IDCODE_*`, `REFCLK_OVRD_IN_*`, `MPLLA_DIV_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, and `HDMI_OVRD_IN` define ID and supervisor clock/PLL override input layouts.
- `C20_PHY_CR3_SUP_DIG_MPLLA_*` and `C20_PHY_CR3_SUP_DIG_MPLLB_*` define MPLL override, ASIC input, bandwidth, VCO, fractional, and spread-spectrum fields. The MPLLB family includes VCO override/status fields not mirrored exactly by MPLLA in this range.
- `C20_PHY_CR3_SUP_DIG_SUP_OVRD_*`, `SUP_OVRD_OUT`, `LVL_*`, `ASIC_IN_*`, and `ASIC_OUT_0` describe supervisor-level override inputs/outputs, request/ack handshakes, level controls, bandgap/reference clock controls, firmware clock request/ack bits, and status outputs.
- `C20_PHY_CR3_SUP_DIG_RTUNE_*` defines RTUNE configuration, status, set values, RX/TXDN/TXUP status values, termination-code payloads, and fast flag fields.
- `C20_PHY_CR3_SUP_DIG_CLK_RST_*`, `MPLLA_MPLL_PWR_CTL_*`, and `MPLLB_UPLL_PWR_CTL_*` define power-up/down timing, calibration control, PLL lock/status, power FSM fields, skip-calibration/tune values, and output timing for MPLLA/MPLLB.
- `C20_PHY_CR3_SUP_DIG_ANA_XF_*` defines the supervisor digital-to-analog crossover surface: analog status inputs/outputs, bandgap/reference/supervisor/MPLLA/MPLLB/PMIX/RTUNE override outputs, tune overrides, VREF controls, and analog CREG payload/override fields.
- `C20_PHY_CR3_RAWCMN_DIG_*` defines raw-common controls: common enable/reset/clock gate fields, ATE ALU address/data/flags/accumulator fields, MPLL input selectors, firmware power-up/config/status, MPLL async override, recalibration bank override, fractional update triggers, CTLE offsets, CREG access control, and context restore selection.
- `C20_PHY_CR3_RAWCMN_DIG_*_CNTX_CFG_*` defines saved or selectable context image payloads for supervisor, MPLLA, and MPLLB state. These are full-width or packed payload registers used by hardware/firmware restore flows.
- `C20_PHY_CR3_RAWCMN_DIG_AON_*` begins the always-on region: SRAM power-gate control, MPLLA/MPLLB tune banks, calibration bank selection, tune-done flags, tune payloads, in-recalibration flags, power-gate/supervisor overrides and status, PMA recalibration bank selection, common calibration status, RTUNE per-bank values, and the `SRAM_OVRD_IN` fields at the end of the range.

## Control Flow

There is no executable control flow in this header chunk. Runtime flow is supplied by AMDGPU display code and firmware-facing helpers that include the generated offset and shift/mask headers.

Typical use is table-driven:

1. DCN 3.2 source files include `dcn/dcn_3_2_0_offset.h` and `dcn/dcn_3_2_0_sh_mask.h`.
2. Register-list and field-list macros token-paste register and field names into generated symbols such as `C20_PHY_CR3_SUP_DIG_MPLLB_SSC_OVRD_IN_0__MPLLB_SSC_EN_MASK`.
3. Register helper code uses the resolved address, shift, and mask constants with MMIO or indirect PHY access paths to read, update, poll, or preserve fields.
4. Link, clock, DMUB, diagnostics, and low-power restore code decides when to program PLLs, issue recalibration or fractional-update requests, select context/tune banks, force overrides, poll status, and restore always-on context.

The source order is generated hardware-register order, not execution order. Most complete register groups list all shift definitions first and the corresponding mask definitions second.

## State And Persistence Behavior

This header stores no software state and persists nothing to disk. The represented state is hardware register state in DCN 3.2 C20 PHY CR3 and a small preceding lane1/pipe2 VDR tail.

Programmed state includes reference-clock selection, PLL divider/multiplier/bandwidth/VCO/SSC settings, HDMI-specific PLL mode fields, supervisor and ASIC input overrides, level controls, RTUNE set values, power-up/down timing, MPLL/UPLL power FSM configuration, analog override outputs, context-restore payloads, CTLE offsets, tune-bank payloads, SRAM power-gate and boot/bypass overrides, and recalibration-bank selections.

Volatile readback includes ID code/version values, supervisor ASIC outputs, RTUNE status, PLL lock and FSM state, clock/reset state, analog status inputs/outputs, firmware power-up/config/static status, common status, fractional update handshakes, tune-done flags, in-recalibration flags, common calibration status, RTUNE per-bank values, and supervisor power/clock acknowledgement bits.

Side-effect-sensitive fields include override-enable bits, reset/request bits, fractional update triggers, recalibration bank override enables, context restore request controls, calibration controls, power-gate overrides, SRAM external-load/boot bypass controls, and firmware clock/stop request or acknowledgement fields. The header gives numeric bit positions only; it does not identify read-only, sticky, self-clearing, write-one-to-clear, or firmware-owned fields.

## Dependencies And Integration Points

This chunk depends on exact consistency with the paired generated offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, and with neighboring chunks of this same shift/mask file. Offset macros locate registers; the macros in this chunk describe fields inside those registers.

Direct include sites for `dcn_3_2_0_sh_mask.h` in this tree include `amdgpu/gmc_v11_0.c`, `display/dmub/src/dmub_dcn32.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, `display/dc/gpio/dcn32/hw_translate_dcn32.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, and `display/dc/resource/dcn32/dcn32_resource.c`.

Important integration points:

- Display Core register helpers in the DC and DMUB layers consume `_SHIFT` and `_MASK` names through macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `FD_SHIFT`, `FD_MASK`, and `SF`.
- PHY/link bring-up and diagnostics are the likely semantic consumers for C20 PHY PLL, supervisor, RTUNE, analog override, context restore, and always-on SRAM/tune fields, even when handwritten code references them through generated tables rather than literal CR3 macro names.
- Firmware/DMUB coordination matters for the always-on and context-restore regions. Some fields appear to expose firmware power-up/config status, firmware clock request/acknowledge paths, context image payloads, tune-bank status, and SRAM boot/load behavior.
- The CR3 address block boundary at line 156425 and the chunk boundary at line 158822 must be preserved during merge-level research. This chunk begins mid-register and ends just before the `AON_SRAM_IN` field definitions.

## Risks And Maintenance Notes

- Numeric drift is the primary risk. A stale shift or mask can compile successfully while programming the wrong PHY bit, corrupting PLL setup, clock selection, calibration, power sequencing, context restore, SRAM boot behavior, or status decoding.
- The PLL and clock fields are high impact. Incorrect MPLLA/MPLLB divider, multiplier, VCO, bandwidth, SSC, HDMI, lock-status, or power-timing masks can cause link-training failures, unstable clocks, resume failures, or intermittent display blanking.
- Override value/enable pairs are common. Updating a value without the matching `*_OVRD_EN` bit may do nothing; setting an override enable unexpectedly can take control away from normal hardware or firmware state machines.
- Handshake and trigger fields require hardware sequencing outside this header. Fractional update, recalibration, context restore, firmware clock request/ack, tune-done, in-recalibration, SRAM load/bypass, and power-gate bits should be preserved or polled according to the hardware rules.
- Repeated MPLLA/MPLLB, supervisor/MPLL context, tune-bank, RTUNE bank, and analog CREG groups are structurally similar but not identical. Generator or caller mix-ups can produce valid C expressions with wrong hardware behavior.
- Boundary registers are partial. Lines 156394-156402 contain only the tail of `C20_PHY_LANE1_PIPE2_UPCSLANE_PIPE_LPC_PHY_C20_VDR_RECAL_SKIP_EN`; earlier shifts are in the previous chunk. Line 158822 is only the comment for `C20_PHY_CR3_RAWCMN_DIG_AON_SRAM_IN`; its fields are in the next chunk.

## Test Signals

Useful validation for this range combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU with DCN 3.2 display support enabled so all direct includers of `dcn_3_2_0_sh_mask.h` compile with the matching offset header.
- Run a generated-register consistency pass over lines 156394-158822: complete fields should have paired `__SHIFT` and `_MASK` definitions, masks should fit the apparent 8-bit or 16-bit PHY register width, and repeated MPLLA/MPLLB/context/tune-bank structures should match the authoritative register database.
- Diff this range against AMD's authoritative DCN 3.2.0/C20 PHY register specification or a known-good generated header, with focus on PLL, SSC, VCO, RTUNE, power FSM, analog override, context restore, and always-on SRAM fields.
- Exercise cold boot, hotplug, modeset, link retraining, high clock/deep-color modes, suspend/resume, low-power entry/exit, and multi-display cases while watching for PLL lock timeouts, firmware/DMUB register errors, PHY calibration failures, display blanking, flicker, and resume instability.
- Validate diagnostics and register dumps for ID/version fields, firmware/static/config status, MPLL/UPLL lock and FSM status, RTUNE values, tune-done/in-recalibration flags, context metadata, analog status fields, and SRAM boot/load/bypass status.
- If hardware test hooks are available, exercise forced override and recalibration paths cautiously: PLL fractional update, recalibration bank select, RTUNE set/status, analog CREG override, power-gate override, and SRAM external-load/boot-bypass behavior.

## Cross-Chunk Notes

This is chunk 65 of the large generated `dcn_3_2_0_sh_mask.h` file. The final per-file report should merge this with chunk 64 for the beginning of `C20_PHY_LANE1_PIPE2_UPCSLANE_PIPE_LPC_PHY_C20_VDR_RECAL_SKIP_EN`, and with chunk 66 for `C20_PHY_CR3_RAWCMN_DIG_AON_SRAM_IN` and the rest of the CR3 always-on SRAM/firmware/status fields. This document should remain chunk-scoped and should not be treated as the final source-file report.
