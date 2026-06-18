# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 219523-221994

## Scope

This chunk covers generated shift and mask macros for DCN 3.2 C20 PHY CR4 register fields. The range is entirely preprocessor data: 2,089 `#define` entries, all either `__SHIFT` or `_MASK` constants, with no C functions, structs, enums, or executable control flow. It starts inside the CR4 RAWLANEX TX firmware crossbar override block and ends in the RAWLANEAONX RX DFE tap-offset/adaptation bank-0 block; the next chunk continues the RAWLANEAONX RX bank definitions.

## Purpose

The file as a whole is the ASIC register field mask companion for `dcn_3_2_0_offset.h`. This chunk contributes the bit-level layout for a specific PHY lane/register instance (`C20_PHY_CR4`) used by AMD DCN 3.2 display hardware. Consumers include DCN 3.2 display, GPIO, IRQ, resource, clock-manager, DMUB, and amdgpu code that include `dcn/dcn_3_2_0_sh_mask.h` and use these symbols through AMD register helper macros.

The covered registers describe:

- `RAWLANEX_DIG_TX_*`: TX firmware crossbar, IRQ, control, PMA interface, PCS/RX interface, and PHY finite-state-machine controls.
- `RAWLANEX_DIG_RX_*`: RX PCS, RX firmware crossbar, IRQ, margining, adaptation, CDR, phase adjust, PMA interface, and FSM controls.
- `RAWLANEAONX_DIG_TX_*`: always-on TX firmware state, SRAM recovery, CCA timing, startup/continuous algorithm skips, high-performance protection, lane transceiver mode, DCC calibration banks, and calibration-done indicators.
- `RAWLANEAONX_DIG_RX_*`: always-on RX startup and continuous calibration controls, fast flags, analog front-end offsets, DCC/IQ calibration banks, adaptation result banks, and DFE tap-offset fields.

## Important APIs, Types, and Macros

There are no callable APIs or declared types in this range. The exported interface is the naming contract of register bitfield macros:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for the field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register value.
- The register identifiers are grouped by comments such as `//C20_PHY_CR4_RAWLANEX_DIG_RX_IRQ_CTL_IRQ_MASK`, which act as generated register headings.

Important macro families in this chunk include:

- Firmware crossbar handshakes: `*_DIG_TX_FW_XF_*` and `*_DIG_RX_FW_XF_*` expose reset/request/ack, power state, low-power detect, rate, width, clock enable, PLL/master-state, DFE bypass, adaptation request, adaptation FOM, and TX pre/main/post direction fields.
- Interrupt controls: `*_IRQ_CTL_IRQ_MASK`, `*_IRQ_CTL_IRQ_EN_FLAGS`, individual IRQ status fields, and matching `*_IRQ_CLR` fields cover TX rate/reset/request, RX request/rate/pstate/adapt/reset, term control, lane mode, parallel loopback, and RX margining interrupts.
- TX/RX control fields: `*_CTL_FSM_CTL`, `*_CTL_CLK_CTL`, `*_TERM_CODE`, `*_RATE_IRQ_ACK`, `*_FW_PWRUP_DONE`, `*_ADAPT_*`, `*_PPM_DRIFT`, `*_CDR_DET_STATUS`, `*_PMA_MISC_CTL`, `*_PHSADJ_*`, `*_MARGIN_*`, and IQ read/write fields.
- PHY FSM and debug controls: `*_DIG_FSM_*` includes FSM override/jump, breakpoint, memory address/status monitors, firmware scratch registers, CR lock, fast-path enable bits, and many skip bits for startup/rate/continuous calibration stages.
- Always-on calibration state: `RAWLANEAONX_DIG_TX_*` and `RAWLANEAONX_DIG_RX_*` include SRAM recovery registers, DCC control range and full/half-rate bank values, bank select fields, calibration-done bits, RX IQ calibration controls, and adaptation-result fields for ATT/VGA/CTLE/DFE taps.

Field widths are encoded by paired masks. Examples in this chunk include single-bit enables and done flags (`0x0001L`), two-bit mode/bank fields (`0x0003L`), 4-bit DCC range fields (`0x000FL`), 8-bit CM/DIFF halves (`0x00FFL`/`0xFF00L`), 13-bit DFE tap adaptation fields (`0x1FFFL`), and full 16-bit counter/address fields (`0xFFFFL`).

## Control Flow

This chunk has no runtime control flow. It is a generated register description consumed at compile time by macro expansion. Runtime behavior emerges only when driver code reads or writes the hardware registers using these masks and shifts through AMD register access helpers.

The implicit hardware flows represented by the fields are:

- Firmware/PHY handshakes use request, reset, ack, and override-enable fields to control or observe crossbar-mediated TX/RX state.
- IRQ programming uses mask, enable, status, and clear registers. The software pattern is expected to mask or enable selected IRQ sources, read latched status bits, then write the matching clear bit.
- Calibration/margining uses control, skip, bank-select, code, valid, and done bits. Software or firmware selects banks/rates, triggers or bypasses algorithm stages, reads result fields, and checks done/valid flags.
- Adaptation reporting stores RX equalization state in banked ATT, VGA, CTLE, DFE, IQ, and reference-error fields that later diagnostics or tuning logic can inspect.

## State and Persistence

The macros are stateless compile-time constants. The state they describe lives in DCN 3.2 C20 PHY hardware registers:

- IRQ status and clear fields represent transient latched hardware events.
- Firmware scratch, memory breakpoint, SRAM recovery, and FSM status fields expose mutable firmware or microcontroller state.
- Calibration and adaptation bank fields persist in hardware registers until reset, recalibration, firmware update, or explicit programming changes them.
- Reserved masks are present because the generated header mirrors the complete hardware field map; driver code should preserve reserved bits during read-modify-write sequences.

No kernel memory, file storage, or user-visible persistence is implemented in this header chunk.

## Dependencies and Integration Points

This header depends only on the C preprocessor and the companion DCN register-offset definitions. The top of the file declares the guard `_dcn_3_2_0_SH_MASK_HEADER`; the chunk itself is included inside that guarded header body.

Known integration points in the tree include direct inclusion of `dcn/dcn_3_2_0_sh_mask.h` from:

- `drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

The exact CR4 PHY symbols in this range are register-map exports. They may be referenced indirectly by generated register tables, register helper macros, debug tooling, firmware-facing code, or by future hardware enablement patches even when no local C file references a particular field name today.

## Risks

- Incorrect masks or shifts can silently corrupt MMIO read-modify-write behavior. For PHY control registers, that can affect display link training, PLL/DCC calibration, RX equalization, IRQ handling, or low-power state transitions.
- Reserved-bit writes are risky. The presence of `RESERVED_*_MASK` fields is useful for documentation, but normal driver code should avoid intentionally setting reserved bits and should preserve existing register values where required.
- The CR index is part of the ABI-like generated name. Accidentally substituting CR0-CR3 macros for CR4, or RAWLANEX macros for RAWLANEAONX macros, would address a different PHY lane/register block or power-domain view.
- Many fields are hardware/firmware coordination points (`*_OVRD_EN`, `REQ`, `ACK`, `CAL_DONE`, `*_VLD`). Race-prone polling or clear-before-read ordering bugs would not be caught by the header itself.
- Because this file is generated and very large, manual edits are high risk. Regeneration from the authoritative ASIC register specification is safer than hand-maintaining individual constants.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware-oriented:

- Kernel or module build coverage for DCN 3.2 AMDGPU display code verifies that the macro names remain available and syntactically valid.
- Static checks can confirm every field has a matching shift/mask pair and that masks align with shifts and declared widths.
- Register helper/unit tests, where available, should exercise field extraction and update macros against representative masks such as one-bit IRQ flags, two-bit mode fields, split 8-bit CM/DIFF fields, and 16-bit address/counter fields.
- Hardware smoke tests should cover DCN 3.2 display bring-up, hotplug/HPD handling, link training, mode set, suspend/resume, and interrupt handling.
- PHY-specific diagnostics should watch for successful TX/RX calibration done flags, RX adaptation valid fields, absence of stuck IRQ status bits, and stable margining/FOM readings.

## Chunk Boundary Notes

The chunk begins after earlier TX PCS context and TX firmware override definitions, so the first local block is `C20_PHY_CR4_RAWLANEX_DIG_TX_FW_XF_OVRD_IN_2`. It ends at `C20_PHY_CR4_RAWLANEAONX_DIG_RX_DFE_EOH_TAP1_OFST_BANK_0`; the immediately following source lines continue with more RAWLANEAONX RX DFE/adaptation bank fields. The final per-file research document should merge this with adjacent chunks to describe the full `dcn_3_2_0_sh_mask.h` register-map surface.
