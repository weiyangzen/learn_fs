# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002253`: lines 1-2376, `Docs/researches/chunks/subset-b-002253_research.md`
- `subset-b-002254`: lines 2377-3574, `Docs/researches/chunks/subset-b-002254_research.md`

## Chunk Research

### subset-b-002253: lines 1-2376

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_0_sh_mask.h lines 1-2376

## Scope

This chunk covers lines 1-2376 of the AMDGPU generated register field header `dpcs_3_0_0_sh_mask.h`. The full header has 3574 lines; this chunk starts at the SPDX/header guard and runs through the beginning of the `RDPCSTX3_RDPCSTX_DMCU_DPALT_PHY_CNTL6`/`RDPCSTX3_RDPCSTX_DPALT_CONTROL_REG` area. The remaining CR3 completion and transmitter instances 4 and 5 are outside this chunk and must be handled by later chunk merge work.

## Purpose

The file is a generated C preprocessor interface for DPCS 3.0.0 display PHY / DisplayPort transmitter register bitfields in the AMD DRM driver. It does not define functions or data structures. Instead, it exports `#define` constants naming bit offsets (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped GPU display registers.

This chunk describes the first four DPCS transmitter slices: complete DPCSTX/RDPCSTX field definitions for instances 0, 1, and 2, the CR0/CR1/CR2 address/data aperture fields, and most of instance 3 through its reserved DMCU DPALT PHY fields. Consumers combine these macros with register addresses from companion `*_offset.h` headers and with AMDGPU register helpers to read, update, and poll hardware state.

## Exported Interface Pattern

Every exported item is a macro. Naming follows:

- `<BLOCK>_<REGISTER>__<FIELD>__SHIFT`: the bit position where the field begins.
- `<BLOCK>_<REGISTER>__<FIELD>_MASK`: the already-shifted mask for the field.

Examples from this chunk include:

- `DPCSTX0_DPCSTX_TX_CLOCK_CNTL__DPCS_SYMCLK_EN__SHIFT` and `_MASK` for symbol-clock enable.
- `DPCSTX0_DPCSTX_TX_CNTL__DPCS_TX_PLL_UPDATE_REQ__SHIFT` and `_MASK` for requesting a PLL update.
- `RDPCSTX0_RDPCSTX_CNTL__RDPCS_TX_FIFO_LANE0_EN__SHIFT` and `_MASK` for lane FIFO enables.
- `RDPCSTX0_RDPCSTX_PHY_CNTL6__RDPCS_PHY_DPALT_DISABLE__SHIFT` and `_MASK` for DP alternate-mode disable control.
- `DPCSSYS_CR0_DPCSSYS_CR_ADDR__RDPCS_TX_CR_ADDR__SHIFT` and `_MASK` for the CR bus address window.

There are no inline helpers to shift values into fields. Callers must use the AMDGPU display register macros/helpers that expect mask/shift pairs, or must manually shift and mask values consistently.

## Register Block Coverage

The chunk is organized by generated `addressBlock` comments:

- `dpcssys_dpcs0_dpcstx0_dispdec` lines 12-75: DPCSTX0 TX clock, TX control, CBUS control, interrupt control, PLL update address/data, and debug config.
- `dpcssys_dpcs0_rdpcstx0_dispdec` lines 77-598: RDPCSTX0 wrapper/control, clocking, interrupts, PLL update data, TX CR address/data, SRAM control, scratch/spare, CR FIFO status, DMCU DPALT block control, PHY controls 0-14, PHY fuses, RX load values, reserved DMCU DPALT PHY mirrors, and DPALT driver-access control.
- `dpcssys_dpcssys_cr0_dispdec` lines 600-606: CR0 address/data aperture fields.
- `dpcssys_dpcs0_dpcstx1_dispdec` lines 609-670: DPCSTX1 fields with the same TX-clock/TX-control/CBUS/interrupt/PLL shape as DPCSTX0, minus the debug config visible on DPCSTX0 in this chunk.
- `dpcssys_dpcs0_rdpcstx1_dispdec` lines 672-1193: RDPCSTX1 mirror of the RDPCSTX0 schema.
- `dpcssys_dpcssys_cr1_dispdec` lines 1195-1201: CR1 address/data aperture fields.
- `dpcssys_dpcs0_dpcstx2_dispdec` lines 1204-1265: DPCSTX2 TX-facing fields.
- `dpcssys_dpcs0_rdpcstx2_dispdec` lines 1267-1788: RDPCSTX2 mirror of the RDPCSTX0 schema.
- `dpcssys_dpcssys_cr2_dispdec` lines 1790-1796: CR2 address/data aperture fields.
- `dpcssys_dpcs0_dpcstx3_dispdec` lines 1799-1860: DPCSTX3 TX-facing fields.
- `dpcssys_dpcs0_rdpcstx3_dispdec` lines 1862-2376: RDPCSTX3 starts and continues through PHY CNTL14, PHY FUSE0-3, RX load value, DMCU DPALT PHY CNTL3, and most of DMCU DPALT PHY CNTL6. The associated DPALT control register starts immediately after the chunk boundary.

## Functional Areas

### TX Clock and FIFO Control

The `DPCSTXn_DPCSTX_TX_CLOCK_CNTL` fields expose symbol clock gating, enable, and clock-on status bits. `DPCSTXn_DPCSTX_TX_CNTL` covers PLL update request/pending, data swap/order inversion, FIFO enable/start, FIFO read-start delay, and TX soft reset. The RDPCSTX side repeats FIFO controls at the lane level with `RDPCS_TX_FIFO_LANE0_EN` through `LANE3_EN`, aggregate FIFO enable/start, data mode selection, and FIFO read-start delay.

These fields are likely used during link bring-up, link-rate changes, encoder enable/disable, and recovery after FIFO errors. The `_MASK` constants are already aligned to the register bit positions, so multi-bit fields such as FIFO delay must be shifted by the corresponding `__SHIFT` before being ORed into the register value.

### CBUS and CR Access

`DPCSTXn_DPCSTX_CBUS_CNTL` controls CBUS write command delay and CBUS soft reset. RDPCSTX exposes `RDPCS_TX_CR_ADDR` and `RDPCS_TX_CR_DATA`, while the `DPCSSYS_CRn_DPCSSYS_CR_ADDR/DATA` blocks provide a system-level CR aperture with 16-bit address and 16-bit data masks.

The control flow implied by these macros is address/data register programming: set an address field, write or read data, and poll status if required by companion code. This header does not enforce ordering, barriers, or polling delays.

### Interrupt and Error Reporting

The DPCSTX interrupt controls provide register FIFO overflow, register error clear, TX lane FIFO error bits for lanes 0-3, TX error clear, FIFO error mask bits, and an interrupt mask. RDPCSTX interrupt controls add DPALT disable-toggle and 4-lane-toggle status, clear, and mask bits.

These fields are status and control bits in hardware registers. Clear bits such as `DPCS_REG_ERROR_CLR`, `DPCS_TX_ERROR_CLR`, `RDPCS_DPALT_DISABLE_TOGGLE_CLR`, and `RDPCS_DPALT_4LANE_TOGGLE_CLR` are especially sensitive: writes likely acknowledge latched hardware conditions, so callers must preserve unrelated status/mask fields when doing read-modify-write operations.

### PHY Reset, Power, Lane, and Loopback Control

`RDPCSTXn_RDPCSTX_PHY_CNTL0` exposes PHY reset, TCA reset/APB reset, test powerdown, debug test bus output, HDMI mode enable, reference range, TX boost level, retune request/acknowledge, CR mux/parallel select, reference clock detection, SRAM initialization/load status, and SRAM bypass.

`PHY_CNTL1` covers PHY power-gating mode, PCS/PMA/analog power enables and stable indicators, plus DP power-gate reset. `PHY_CNTL2` contains DP4 power-on reset and per-lane loopback controls for RX-to-TX parallel and TX-to-RX serial loopbacks. `PHY_CNTL3` defines repeated per-lane reset, disable, clock-ready, data-enable, request, and acknowledge fields for DP TX lanes 0-3.

These fields imply hardware state machines with request/acknowledge and enable/stable handshakes. The header only supplies bit positions; correctness depends on higher-level driver code polling the corresponding acknowledge/stable bits with timeouts.

### Lane Electrical Settings and Link Rate

`PHY_CNTL4` exports per-lane termination control, inversion, EQ calculation bypass, and HP protection enable fields. `PHY_CNTL5` exports per-lane low-power detect, rate, width, detect-RX request, and detect-RX result fields. `PHY_CNTL6` exports per-lane power state and MPLL enable fields, plus DPALT DP4, DPALT disable/acknowledge, DP reference clock enable, and reference clock request.

These fields are key integration points for DisplayPort link training and mode set code. The risk surface is high because many fields are compact multi-bit values repeated in byte-like lane groups. A wrong shift or lane prefix can silently program the wrong lane.

### MPLL and Spread-Spectrum Controls

`PHY_CNTL7` through `PHY_CNTL14` define DP MPLLB fractional-N denominator/quotient/remainder, spread-spectrum peak and step size, up-spread control, DP MPLLB multiplier, HDMI MPLLB divider fields, DP reference-clock MPLLB divider, HDMI pixel-clock divider, MPLLB div5/word-div2/TX clock divider/state/SSC enable, divider multiplier, divider clock enable, force enable, init calibration disable, calibration force, fractional-N enable, and PMIX enable.

These macros are frequency programming primitives. They are likely paired with calculated PLL parameters in display link-rate setup code. Test coverage must focus on known-good modes/link rates because the header itself cannot detect invalid clock programming combinations.

### Fuse, SRAM, Scratch, Spare, and Reserved DPALT Mirrors

Each RDPCSTX instance includes PHY fuse fields for per-lane equalization defaults (`EQ_MAIN`, `EQ_PRE`, `EQ_POST`) and PLL/DCO tuning fields such as `MPLLB_V2I`, `MPLLB_FREQ_VCO`, `MPLLB_CP_INT`, `MPLLB_CP_PROP`, `DCO_FINETUNE`, and `DCO_RANGE`. SRAM fields include memory power disable/force/state and SRAM initialization/load status. Scratch/spare fields are full 32-bit masks and should not be assigned semantics beyond what consuming driver code documents.

The `RDPCSTXn_RDPCSTX_DMCU_DPALT_PHY_CNTL3` and `CNTL6` macros duplicate many PHY CNTL3/CNTL6 fields with `_RESERVED` suffixes. They appear to describe DMCU-reserved DP alternate-mode ownership or shadowing. The adjacent DPALT control register exposes driver access allow/block fields for instances 0-2 in this chunk and begins for instance 3 after line 2376.

## Control Flow and State Behavior

This header has no executable control flow, allocations, locks, or persistence. Its behavior is compile-time textual substitution. Runtime state lives entirely in GPU hardware registers accessed by other AMDGPU display code.

The important control-flow implications for consumers are:

- Clock and reset sequencing must use enable/request bits and then poll matching `*_CLOCK_ON`, `*_ACK`, `*_STABLE`, `*_INIT_DONE`, or `*_RESULT` fields.
- PLL update sequences use request/pending and address/data fields; writes must preserve unrelated bits and respect hardware update ordering.
- Interrupt/error handling must clear only intended latched bits and update masks without discarding status.
- DPALT ownership uses allow/block and reserved DMCU fields, so driver-side writes may need coordination with firmware or display microcontroller ownership rules.

No state is persisted in memory by this header. The only persistent effect from its consumers is hardware register mutation.

## Dependencies and Integration Points

Direct dependencies are minimal: the file uses only the C preprocessor and an include guard. It is expected to be included by AMDGPU display code together with companion generated register offset headers under `drivers/gpu/drm/amd/include/asic_reg/dpcs/` and common register access helpers/macros in the AMD DRM stack.

Likely integration points include:

- DCN display core resource and link encoder code that configures DisplayPort PHY slices.
- Link training and mode-set paths that program lane rate, width, power, MPLL, and EQ fields.
- Hotplug, DP alternate-mode, and firmware/DMCU coordination paths that use DPALT fields.
- Interrupt or diagnostics code that reads FIFO error, toggle, scratch, spare, fuse, and status fields.
- Register generation/update tooling that regenerates `*_sh_mask.h` files from ASIC register specifications.

The header guard `_dpcs_3_0_0_SH_MASK_HEADER` prevents duplicate definitions inside a translation unit.

## Risks and Edge Cases

- Manual edits are risky because this is generated hardware ABI data. A one-bit shift or mask error can break display output, link training, power management, or interrupt handling.
- Macro names encode both instance and field. Copy/paste between `DPCSTXn`, `RDPCSTXn`, and `DPCSSYS_CRn` can compile while targeting the wrong register slice.
- Multi-bit fields require correct masking and shifting by callers. The masks are pre-shifted; raw field values must not be ORed directly unless already shifted.
- Several fields are status or acknowledge bits, not writable controls. Misusing masks without checking access semantics can write to read-only/status fields or clear latched events.
- The chunk boundary cuts through the RDPCSTX3 DPALT area. Any whole-file report must reconcile the continuation after line 2376 before claiming complete instance-3 coverage.
- `_MASK_MASK` macro names such as `DPCS_REG_FIFO_ERROR_MASK_MASK` are generated from fields whose names include `MASK`; they are awkward but intentional and should not be simplified by hand.
- Full-width `0xFFFFFFFFL` masks for scratch/spare and PLL update data should be treated as raw register payloads; blindly preserving or exposing them can leak undefined/reserved bits into future writes.

## Test Signals

Because this file is preprocessor data, useful validation is indirect:

- Build coverage for AMDGPU/DC display code that includes `dpcs_3_0_0_sh_mask.h`; duplicate names, missing definitions, or syntax issues fail at compile time.
- Register macro generator diff checks against the authoritative ASIC register database; field names, shifts, and masks should be regenerated rather than hand-maintained.
- Display smoke tests on DPCS 3.0.0 hardware: boot with AMDGPU, enable/disable monitors on all relevant transmitters, run DP link training at multiple link rates/lane counts, suspend/resume, hotplug, and DP alternate-mode paths.
- Runtime diagnostics around FIFO errors, PLL update pending bits, clock-on/stable polling, and DPALT toggles can reveal mismatched masks or wrong register instance use.
- Static checks can verify every `__SHIFT` has a corresponding `_MASK` in each repeated transmitter instance and that repeated instance schemas remain aligned unless hardware generation data intentionally differs.

## Open Cross-Chunk References

The full file continues after this chunk with `DPCSSYS_CR3`, DPCSTX4/RDPCSTX4, CR4, and DPCSTX5/RDPCSTX5 content. For the final merged source-file research, confirm whether instances 4 and 5 exactly mirror the schema here and whether DPCSTX0's `DPCSTX_DEBUG_CONFIG` uniqueness is intentional across all instances.

### subset-b-002254: lines 2377-3574

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_0_sh_mask.h lines 2377-3574

## Scope

This chunk is the tail of the generated AMD DPCS 3.0.0 register shift/mask header. It covers line 2377 through the final `#endif` at line 3574, defining 1,094 preprocessor constants: 547 `__SHIFT` values and 547 matching `_MASK` values. The content is declarative only; it exposes bitfield locations for DPCS/RDPCS register programming and contains no executable functions, data structures, storage, or branching logic.

The chunk completes the `RDPCSTX3_RDPCSTX_DPALT_CONTROL_REG` field definitions started before the chunk, then defines complete repeated register-field surfaces for CR bridge instances 3 and 4, DPCSTX transmitter instances 4 and 5, and RDPCSTX transmitter/PHY instances 4 and 5.

## Purpose

The header gives AMD display driver code stable symbolic names for extracting, composing, and updating memory-mapped display PHY/control registers. Each field has a left-shift value and a 32-bit or 16-bit mask so call sites can use common register helpers to set fields without embedding raw bit positions. In this chunk, the exported constants describe DisplayPort/HDMI transmitter lanes, FIFO control, clock gating, PLL update payloads, PHY power state, lane request/ack handshakes, spread-spectrum PLL parameters, fuse-derived calibration fields, DP Alt Mode ownership controls, and DMCU-reserved views of selected DPALT PHY state.

## Exported API Surface

There are no C functions or types. The public API is a set of `#define` constants consumed by other AMDGPU display code after including this generated ASIC register header.

Important macro families:

- `DPCSSYS_CR3_DPCSSYS_CR_ADDR` / `DPCSSYS_CR3_DPCSSYS_CR_DATA` and `DPCSSYS_CR4_DPCSSYS_CR_ADDR` / `DPCSSYS_CR4_DPCSSYS_CR_DATA`: 16-bit CR address/data fields for RDPCS transmitter CR access paths.
- `DPCSTX4_DPCSTX_*` and `DPCSTX5_DPCSTX_*`: DPCS transmitter-side clock, control, CBUS, interrupt, PLL update address, and PLL update data fields.
- `RDPCSTX4_RDPCSTX_*` and `RDPCSTX5_RDPCSTX_*`: RDPCS transmitter control, clocks, interrupts, SRAM control, scratch/spare, FIFO state, DMCU DPALT blocks, PHY control registers, fuse fields, RX load values, and DPALT access-control fields.
- A carry-over `RDPCSTX3_RDPCSTX_DPALT_CONTROL_REG` group: DPALT driver-access and blocked-status fields for transmitter instance 3.

The instance 4 and instance 5 blocks are intentionally parallel. Most `RDPCSTX4_*` definitions have a same-shaped `RDPCSTX5_*` counterpart with identical shifts and masks, allowing higher-level code to choose a register instance while preserving field semantics.

## Register Areas Covered

The DPCS TX blocks (`DPCSTX4_DPCSTX_*` and `DPCSTX5_DPCSTX_*`) define:

- Symbol clock gate/enable/status bits in `DPCSTX_TX_CLOCK_CNTL`.
- PLL update request and pending bits, 10-bit/18-bit data swap/order controls, FIFO enable/start, FIFO read-start delay, and TX soft reset in `DPCSTX_TX_CNTL`.
- CBUS write delay and CBUS soft reset in `DPCSTX_CBUS_CNTL`.
- Register FIFO overflow/error clear/mask, per-lane TX FIFO errors, TX error clear, and global interrupt mask in `DPCSTX_INTERRUPT_CNTL`.
- PLL update address and 32-bit update data payload fields.

The RDPCS TX control blocks (`RDPCSTX4_RDPCSTX_*` and `RDPCSTX5_RDPCSTX_*`) define:

- CBUS, SRAM, lane FIFO, aggregate FIFO, data mode, FIFO start delay, DPALT block status, CR/non-DPALT register block enables, and TX soft reset in `RDPCSTX_CNTL`.
- External reference clock enable, per-lane TX clock enables, aggregate TX clock gate/enable/status, SRAM clock gate/enable/status, and SRAM clock bypass in `RDPCSTX_CLOCK_CNTL`.
- Register FIFO overflow, DPALT disable and four-lane toggle interrupts, per-lane FIFO errors, clear bits, and interrupt masks in `RDPCSTX_INTERRUPT_CONTROL`.
- One-bit RDPCS PLL update data, 16-bit CR address/data, SRAM memory power disable/force/state fields, full-width scratch and spare registers, and CR convert FIFO empty/full status.
- DMCU DPALT disable/block controls, including forced TX clock disable and spare bits.

The RDPCS PHY blocks define:

- Reset, test powerdown, HDMI mode, reference range, VBOOST level, RTUNE request/ack, CR mux selection, reference clock detection, SRAM init/load status, and SRAM bypass in `PHY_CNTL0`.
- Power-gating and stability bits for PCS, PMA, analog power, and DP power-gate reset in `PHY_CNTL1`.
- DP4 power-on-reset plus per-lane RX-to-TX parallel and TX-to-RX serial loopback bits in `PHY_CNTL2`.
- Per-lane DP TX reset, disable, clock ready, data enable, request, and acknowledge handshake fields in `PHY_CNTL3`.
- Per-lane termination control, inversion, EQ calculation bypass, and high-performance protection in `PHY_CNTL4`.
- Per-lane low-power detect, rate, width, DETRX request, and DETRX result in `PHY_CNTL5`.
- Per-lane power state and MPLL enable plus DPALT DP4, DPALT disable/ack, DP reference clock enable/request in `PHY_CNTL6`.
- MPLLB fractional denominator/quotient/remainder, SSC peak/step/up-spread, multiplier/dividers, MPLLB state, SSC enable, force enable, calibration force, FRACN enable, and PMIX enable across `PHY_CNTL7` through `PHY_CNTL14`.
- Fuse fields for per-lane EQ main/pre/post settings and PLL/DCO calibration (`PHY_FUSE0` through `PHY_FUSE3`), plus RX reference/VCO load values.
- DMCU-reserved DPALT mirrors of selected `PHY_CNTL3` and `PHY_CNTL6` bits, named with `_RESERVED`.
- DPALT access control (`ALLOW_DRIVER_ACCESS`, `DRIVER_ACCESS_BLOCKED`, and spare bits).

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior emerges in consumer code that reads or writes hardware registers using these masks. The constants imply several state-machine surfaces that consumers must sequence correctly:

- Reset and power state transitions: soft reset, PHY reset, power-gating enables, stable status bits, and SRAM init/load done fields are expected to be toggled or polled by display bring-up and link-management code.
- Clock control: gate-disable, enable, and clock-on bits expose both requested and observed state for TX, symbol, external reference, and SRAM clocks.
- FIFO bring-up and error handling: lane FIFO enables, aggregate FIFO enable/start, read-start delay, FIFO empty/full status, overflow bits, clear bits, and interrupt masks support data-path activation and diagnostics.
- PLL programming: update request/pending plus update address/data and MPLLB fractional/SSC/divider fields support staged link-rate programming.
- PHY lane handshake: per-lane reset/disable/clock-ready/data-enable/request/ack bits encode hardware negotiation between display control logic and PHY lanes.
- DP Alt Mode ownership: driver access, blocked status, DPALT disable/toggle, DMCU-reserved fields, and register block enables model contention between the host driver, DMCU, and DPALT control paths.

No persistence is implemented in software. Hardware register values persist according to device power/reset domains. The `SCRATCH` and `SPARE` masks expose full-width register storage that may be used by firmware/driver conventions elsewhere, but this chunk does not define those conventions.

## Dependencies And Integration Points

This file depends only on C preprocessing. It is normally included alongside companion generated headers that define register addresses and possibly enum/value constants. The mask names are designed for AMD display register helper idioms such as read-modify-write macros that take a register, field mask, and shift value.

Integration points visible from the names:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DCE/DPCS code that configures display PHY lanes and link clocks.
- Generated ASIC register address headers for `dpcs_3_0_0`, which provide the register offsets corresponding to these field masks.
- DisplayPort, HDMI, USB-C/DP Alt Mode, and DMCU firmware coordination paths, as reflected by `DPALT`, `HDMIMODE`, `DMCU`, `MPLLB`, and per-lane DP PHY field names.
- Interrupt handling paths that inspect FIFO errors, DPALT toggles, and register FIFO overflow, then write clear bits and masks.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask silently corrupts unrelated hardware bits during read-modify-write operations, especially where fields are adjacent per-lane slices.
- Instance copy/paste errors are high-impact because instance 4 and instance 5 are large parallel blocks. A single mismatched `RDPCSTX4`/`RDPCSTX5` field can route programming to the wrong register instance or use the wrong mask.
- Some fields combine command and status semantics in adjacent bits, such as request/pending, enable/clock-on, request/ack, stable status, clear bits, and interrupt masks. Consumers must not assume every defined field is writable.
- DPALT and DMCU-reserved fields imply shared ownership. Writing driver access or reserved mirror controls without checking ownership can conflict with firmware or Type-C/DP Alt Mode state.
- Full-width `SCRATCH`, `SPARE`, and PLL update data masks allow arbitrary 32-bit writes. Call sites need hardware-specific value validation before composing register data.
- The final `#endif` is in this chunk, so malformed edits here can break inclusion of the entire generated header.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration oriented:

- C preprocessing/compilation of AMDGPU display code that includes `dpcs_3_0_0_sh_mask.h`.
- Static checks that every field in the chunk has exactly one `__SHIFT` macro and one matching `_MASK` macro; this chunk currently has 547 of each.
- Generated-register consistency checks comparing this header against the source register database for DPCS 3.0.0.
- Grep or compile checks for `DPCSTX4`, `DPCSTX5`, `RDPCSTX4`, and `RDPCSTX5` consumers to catch renamed or missing macros.
- Runtime display tests on ASICs using DPCS 3.0.0: link training, hotplug, DP Alt Mode attach/detach, HDMI mode, suspend/resume, display clock changes, and interrupt/error recovery.
- Register readback during bring-up to confirm reset, clock-on, stable, FIFO, PLL pending, lane ack, DPALT blocked, and SRAM init/load status fields match expected hardware transitions.

## Chunk Notes For Merge

This chunk is self-contained for transmitter instances 4 and 5 and closes the header. Earlier chunks are expected to define address constants and the same register families for lower-numbered instances. The final merged per-file report should describe this file as a generated bitfield map rather than handwritten driver logic, and should call out the repeated per-instance pattern across all DPCS/RDPCS transmitters.
