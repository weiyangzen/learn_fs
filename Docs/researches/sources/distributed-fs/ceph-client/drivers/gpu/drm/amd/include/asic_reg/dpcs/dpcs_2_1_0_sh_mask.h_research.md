# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_1_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002250`: lines 1-2383, `Docs/researches/chunks/subset-b-002250_research.md`
- `subset-b-002251`: lines 2384-3430, `Docs/researches/chunks/subset-b-002251_research.md`

## Chunk Research

### subset-b-002250: lines 1-2383

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_1_0_sh_mask.h lines 1-2383

## Purpose

This chunk is generated AMD DPCS 2.1.0 register-field metadata. It contains no executable C logic; it exports preprocessor constants that describe bit positions and masks for DisplayPort transmitter and retimer/DP-alt-mode PCS register fields. AMDGPU Display Core pairs this header with `dpcs_2_1_0_offset.h` and register-helper tables so link-encoder code can pack, extract, and update individual MMIO fields.

The range covers the license/header guard and the generated `__SHIFT`/`_MASK` definitions for DPCS instances 0 through 2, plus the start of instance 3. It includes 2,161 `#define` lines: 1,089 shift macros and 1,071 mask macros across 11 address blocks and 167 register comments. The shift/mask count is intentionally unbalanced at this chunk boundary because line 2383 stops inside `RDPCSTX3_RDPCSTX_PHY_CNTL3`; the remaining masks for that register and the rest of instance 3 continue in the next chunk. Although this path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or direct MMIO accesses in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for encoding or decoding a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, clearing, or writing that field.

Major register families in this chunk:

- `DPCSTX0_*`, `DPCSTX1_*`, `DPCSTX2_*`, and `DPCSTX3_*`: front-end DPCS transmitter controls for symbol-clock gating/enabling/status, TX PLL update request/pending flow, data swap/order inversion, TX FIFO enable/start/read-start delay, soft reset, CBUS write-command delay/reset, interrupt status/clear/masks, PLL update address/data, and debug mux/test-index controls.
- `RDPCSTX0_*`, `RDPCSTX1_*`, `RDPCSTX2_*`, and partial `RDPCSTX3_*`: retimer/display PCS controls for CBUS/SRAM/TX resets, lane FIFO enables, DP-alt-mode block status, CR/non-DP-alt register blocking, symbol/SRAM/OCLA clock controls, interrupt status/ack/masks, PLL update data, CR indirect address/data windows, TX SRAM power controls, scratch/spare registers, CR-convert FIFO status, DMCU DP-alt disable blocking, and debug selectors/counters.
- `RDPCSTX*_RDPCSTX_PHY_CNTL0` through `PHY_CNTL17`: PHY reset, TCA/APB reset, test powerdown, HDMI mode, reference-range/clock-detect, RTUNE request/ack, SRAM init/load/bypass status, power-gating enables and stable bits, loopback controls, per-lane reset/disable/clock-ready/data-enable/request/ack handshakes, termination/invert/high-pass/equalization bypass fields, lane rate/width/LPD/detect-RX fields, P-state and MPLL enables, DP-alt DP4/disable/ack fields, DP reference-clock enable/request, MPLL fractional/SSC/multiplier/divider controls, generic PHY buses, and debug/OCLA source selection.
- `RDPCSTX*_RDPCSTX_PHY_FUSE0` through `PHY_FUSE3` and `PHY_RX_LD_VAL`: fuse-derived equalization, MPLL charge-pump/VCO/DCO, voltage boost, RX VREF, and RX load-value fields that link-encoder code can read when choosing PHY programming values.
- `RDPCSTX*_RDPCSTX_DMCU_DPALT_PHY_CNTL3` and `PHY_CNTL6`: reserved DMCU/firmware-owned mirror fields for DP-alt PHY handshakes and power/state control.
- `RDPCSTX*_RDPCSTX_DPALT_CONTROL_REG`: driver versus DP-alt ownership controls, including allow-driver-access, driver-access-blocked status, and spare bits.
- `DPCSSYS_CR0_DPCSSYS_CR_ADDR/DATA`, `DPCSSYS_CR1_*`, and `DPCSSYS_CR2_*`: CR indirect address/data windows paired with the RDPCS CR access registers for instances 0 through 2.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 2.1 resource setup includes `dpcs_2_1_0_offset.h` and this shift/mask header.
2. Link-encoder register-list macros bind instance-specific MMIO offsets with these field masks and shifts using token-pasting helpers such as `LE_SF`, `SR`, and `SRI`.
3. Runtime link-encoder paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to program the DPCS/RDPCS registers for DisplayPort, HDMI/FRL-related PHY controls, USB-C DP-alt-mode ownership, link training, PHY power, and diagnostics.
4. The numeric values in this chunk determine which bits are touched when the driver enables lanes/FIFOs/clocks, polls PHY ready/ack bits, configures MPLL/SSC/rate/width/equalization fields, acknowledges interrupt/error conditions, or hands access between driver and DMCU/firmware.

The macros do not encode required programming order. Consumers must still observe hardware sequencing for soft resets, clock enable/status polling, SRAM and memory-power transitions, TX FIFO start timing, PLL update request/pending completion, PHY lane request/ack handshakes, DP-alt disable/ack flow, indirect CR accesses, interrupt clearing, and fuse/status reads.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. It describes hardware-backed DPCS state:

- Transmitter state includes symbol clocks, FIFO enable/start/read delay, data lane ordering, soft reset, PLL-update mailbox address/data, CBUS reset/delay, interrupt status, and debug mux state.
- RDPCS state includes per-lane FIFO enables, DP-alt blocking, CR register blocking, SRAM and OCLA clocks, low-level CR address/data access, memory power state, scratch/spare values, and debug counter/source selections.
- PHY state includes power-gating status, resets, per-lane disable/ready/data-enable/request/ack handshakes, per-lane electrical settings, rate/width/P-state, MPLL and SSC programming, reference-clock state, HDMI mode, loopback controls, fuse-derived trim values, and generic debug bus values.
- DP-alt and firmware ownership state includes DMCU reserved mirrors, DP-alt disable/block/ack fields, driver access grant/block status, and DP4 mode indication.

Lifetime and access semantics are hardware-defined. Configuration fields generally persist until rewritten, modeset/link reconfiguration, PHY power transition, suspend/resume, GPU reset, or driver reinitialization. Status, pending, ack, ready, interrupt, error, and clear fields may be read-only, sticky, self-clearing, write-one-to-clear, or only valid while the associated clocks and power domains are active. This generated header does not express those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 2.1.0 register database and the companion offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_1_0_offset.h`, which supplies the matching `mm...` register offsets and base-index selectors.

Observed integration points in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c` includes both `dpcs_2_1_0_offset.h` and this header when constructing DCN 2.1 display resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.h` builds DCN 2.1 link-encoder shift/mask lists from fields in this chunk, including PHY fuse fields, DP-alt disable/block controls, PHY voltage/pre-emphasis controls, DP4 mode, and per-lane equalization fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.c` reads and updates `RDPCSTX_PHY_CNTL6` fields such as `RDPCS_PHY_DPALT_DISABLE`, `RDPCS_PHY_DPALT_DISABLE_ACK`, and `RDPCS_PHY_DP_REF_CLK_EN` during DP-alt-mode and reference-clock handling.
- Shared DIO/link-encoder definitions under `display/dc/dio/dcn10`, `display/dc/dio/dcn20`, and related DCN generations consume the same logical RDPCS/DPCSTX field names for lane ready, lane disable, termination, rate/width, MPLL, FIFO, and clock programming. The DCN 2.1 resource path binds those generic lists to this ASIC-specific generated metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h` contains related symbolic enum values for DPCS/RDPCS fields such as TX FIFO lane enable, symbol-clock controls, and TX FIFO error masking. Those enums document field value intent, while this header provides the bit placement.

The repeated instance layout is an integration contract. Generic instance-indexed code assumes that fields for `DPCSTX0/1/2/3` and `RDPCSTX0/1/2/3` have consistent layouts where the hardware schema expects them, while the offset header maps each instance to the correct MMIO address range.

## Risks And Edge Cases

- These are untyped preprocessor constants. A bad shift or mask can compile cleanly while reading or writing the wrong hardware bits.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the matching offset header, firmware ownership expectations, and silicon documentation.
- The chunk boundary is inside `RDPCSTX3_RDPCSTX_PHY_CNTL3`. Complete reasoning about instance 3 PHY handshakes requires the next chunk for the remaining TX2/TX3 masks and later RDPCSTX3 register families.
- Transmitter clock, reset, FIFO, and PLL-update fields are sequencing-sensitive. Incorrect masks can leave the symbol clock gated, start FIFOs at the wrong time, miss PLL-update completion, or corrupt data ordering.
- Interrupt status, clear, and mask fields have similar names across DPCSTX and RDPCSTX blocks. Confusing status bits with clear or mask bits can lose FIFO/error events or leave stale interrupts asserted.
- DP-alt-mode ownership fields cross driver and DMCU/firmware boundaries. Incorrect `ALLOW_DRIVER_ACCESS`, block, disable, or ack masks can race firmware, block valid driver access, or let the driver program PHY state while DP-alt mode owns the block.
- Per-lane PHY request/ack/ready/data-enable/reset/disable fields are packed repeatedly by lane. Off-by-one lane masks can train the wrong lane, leave a lane powered down, or report link readiness incorrectly.
- PHY electrical and PLL fields affect user-visible link stability. Bad equalization, termination, rate, width, MPLL, SSC, fractional divider, or reference-clock masks can cause link training failures, flicker, blank displays, HDMI/DP mode failures, or marginal behavior only at high link rates.
- Fuse and calibration fields should generally be treated as hardware-provided trim/status. Misinterpreting them as writable configuration, or reading them while power/clock domains are inactive, can produce invalid PHY programming decisions.
- Repeated instance layouts are copy-sensitive. Testing only DPCSTX0/RDPCSTX0 may miss an instance-specific typo in DPCSTX1/2/3 or RDPCSTX1/2/3.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 2.1 display behavior:

- Build AMDGPU Display Core with DCN 2.1 enabled. Missing or renamed macros should fail in `dcn21_resource.c`, `dcn21_link_encoder.h`, `dcn21_link_encoder.c`, and shared DIO/link-encoder register-table construction.
- Mechanically compare this slice against the authoritative DPCS 2.1.0 register-field database and `dpcs_2_1_0_offset.h`. Every field in a complete register should have a matching shift/mask pair, with the expected exception that this chunk ends mid-register at `RDPCSTX3_RDPCSTX_PHY_CNTL3`.
- Verify repeated instance consistency for DPCSTX/RDPCSTX 0-2 and the covered portion of instance 3 where the hardware schema expects identical field layouts.
- Exercise DisplayPort link training across all exposed DCN 2.1 transmitters, including 1/2/4-lane modes, multiple link rates, lane disable/enable transitions, clock gating, FIFO programming, and unplug/replug during training.
- Exercise USB-C DP-alt-mode transitions where supported: DP4 mode detection, DP-alt disable/ack polling, DMCU block handoff, driver-access allow/block status, and suspend/resume while in alt mode.
- Test PHY power and reset transitions, including SRAM init/load, power-gating stable bits, reference-clock enable/disable, RTUNE request/ack, MPLL enable/disable, and high-rate SSC/fractional-divider programming.
- Validate HDMI/FRL or HDMI-mode paths that share DPCS/RDPCS PHY controls, especially data swap/order inversion, MPLL divider settings, and voltage/equalization trims.
- Induce or monitor FIFO and register-access error paths and check that interrupt status, clear, and mask fields behave as expected without stuck interrupts or lost events.
- Use debug and scratch/status registers only as diagnostics; expected high-signal failures are link-training errors, AUX/link logs indicating DP-alt ownership problems, display blanking or flicker, PHY timeout polling, FIFO error interrupts, and resume-only failures.

## Cross-Chunk Notes

This chunk owns the beginning of `dpcs_2_1_0_sh_mask.h` through line 2383. It includes complete DPCSTX/RDPCSTX/DPCSSYS_CR metadata for instances 0, 1, and 2, plus complete DPCSTX3 TX-side metadata and RDPCSTX3 metadata through the first masks of `RDPCSTX3_RDPCSTX_PHY_CNTL3`. The next chunk must cover the rest of `RDPCSTX3_RDPCSTX_PHY_CNTL3`, later RDPCSTX3 PHY/fuse/DP-alt/debug fields, any remaining instances or trailer guard, and should reconcile the intentionally incomplete shift/mask pairing at this boundary.

### subset-b-002251: lines 2384-3430

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_1_0_sh_mask.h lines 2384-3430

## Scope And Purpose

This chunk is the tail of AMD DCN 2.1 DPCS shift/mask definitions. The file is a generated-style hardware register header: it does not implement runtime logic, allocate state, or call functions. Instead, it defines preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DisplayPort/HDMI DPCS transmitter register fields. These constants are consumed by AMD Display Core register helper macros to construct per-ASIC register tables and to drive `REG_GET`/`REG_UPDATE` style field access.

The selected lines begin in the middle of `RDPCSTX3_RDPCSTX_PHY_CNTL3`, covering masks for TX lane 1 through lane 3 reset/disable/clock-ready/data-enable/request/ack fields. The chunk then completes the `RDPCSTX3` PHY control, fuse, DP-alt, generic-bus, debug, and CR access definitions before defining the full `DPCSTX4` and `RDPCSTX4` register field set and final `DPCSSYS_CR4` address/data fields. It ends with the header guard close.

## Important Definitions

The definitions fall into repeated register families:

- `RDPCSTX3_RDPCSTX_PHY_CNTL3` through `PHY_CNTL17`: per-lane DP PHY control for transmitter instance 3, including lane reset/disable handshakes, term control, invert flags, rate/width, low-power detect, pstate/MPLL enable, DP-alt mode, ref-clock request/enables, MPLL fractional/SSC/divider programming, voltage-regulator bypass, generic input/output buses, and debug source selection.
- `RDPCSTX3_RDPCSTX_PHY_FUSE0` through `PHY_FUSE3`: fuse-derived calibration fields for lane equalization, MPLL charge-pump/current properties, RX reference voltage, DCO tuning/range, TX voltage boost, and supplemental RX VCO reference selection.
- `RDPCSTX3_RDPCSTX_DMCU_DPALT_PHY_CNTL3` and `PHY_CNTL6`: reserved DMCU DP-alt mirrors for the lane reset/disable/clock/data/request/ack and pstate/MPLL/ref-clock fields.
- `RDPCSTX3_RDPCSTX_DPALT_CONTROL_REG`: driver/DMCU access arbitration fields, notably allow-driver-access, driver-access-blocked, and spare control bits.
- `DPCSSYS_CR3_DPCSSYS_CR_ADDR` and `DPCSSYS_CR3_DPCSSYS_CR_DATA`: 16-bit indirect control-register address/data fields for CR instance 3.
- `DPCSTX4_DPCSTX_*`: direct DPCS transmitter instance 4 masks for symbol clock, TX control, CBUS control, interrupt status/masks/clears, PLL update address/data, and debug selection.
- `RDPCSTX4_RDPCSTX_*`: read/display-side DPCS transmitter instance 4 masks for reset, SRAM/FIFO enable, clocking, interrupts, PLL update, CR address/data, SRAM control, scratch/spare, DP-alt block state, debug, PHY controls, fuses, and DP-alt control.
- `DPCSSYS_CR4_DPCSSYS_CR_ADDR` and `DPCSSYS_CR4_DPCSSYS_CR_DATA`: 16-bit indirect control-register address/data fields for CR instance 4.

No C types or functions are declared here. The effective API is the naming convention used by register-table macros. For a field named by a higher-level macro such as `LE_SF(RDPCSTX0_RDPCSTX_PHY_CNTL6, RDPCS_PHY_DPALT_DISABLE, _MASK)`, the preprocessor resolves a concrete constant like `RDPCSTX0_RDPCSTX_PHY_CNTL6__RDPCS_PHY_DPALT_DISABLE_MASK`. The same pattern applies across instances, so the instance-specific `RDPCSTX3` and `RDPCSTX4` constants in this chunk must stay structurally aligned with earlier `RDPCSTX0`-`RDPCSTX2` definitions.

## Control Flow And Runtime Use

This header has no direct control flow. Runtime behavior is introduced when the AMD display resource code includes it with the matching `dpcs_2_1_0_offset.h` header. In DCN 2.1, `dcn21_resource.c` includes both headers and builds `link_enc_regs`, `le_shift`, and `le_mask` tables. `DPCS_DCN21_REG_LIST(id)` maps each link encoder instance to the correct register offsets, while `DPCS_DCN21_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN21_MASK_SH_LIST(_MASK)` materialize the field positions and masks into the link encoder register helper structures.

The field selection comes from link encoder headers. `dcn20_link_encoder.h` names the common DPCS fields for lane readiness, data enable, termination, MPLL programming, FIFO enable, clocks, lane disable/request/ack/reset, and DP-alt mode. `dcn21_link_encoder.h` extends that set with DCN 2.1-specific fuse and regulator fields such as `RDPCS_PHY_TX_VBOOST_LVL`, `RDPCS_PHY_DP_MPLLB_CP_PROP_GS`, `RDPCS_PHY_RX_VREF_CTRL`, `RDPCS_PHY_DP_MPLLB_CP_INT_GS`, `RDPCS_PHY_SUP_PRE_HP`, and per-lane `RDPCS_PHY_DP_TX*_VREGDRV_BYP`.

At runtime, those tables are used by register helper operations in link encoder code. For example, the DCN 2.1 PHY acquisition path reads `RDPCS_PHY_DPALT_DISABLE`, updates `RDPCS_PHY_DPALT_DISABLE_ACK`, and toggles `RDPCS_PHY_DP_REF_CLK_EN` through `RDPCSTX_PHY_CNTL6`. The masks in this chunk provide the same bit layout for transmitter instances 3 and 4 when those encoder instances are selected.

## State And Persistence Behavior

The constants here describe persistent hardware register state, but they do not store software state themselves. The underlying state lives in MMIO or indirect CR/SRAM hardware registers. Writes made through `REG_UPDATE` persist in the display engine until hardware reset, power gating, mode set sequencing, firmware/DMCU ownership changes, or another driver write changes them.

Several fields are handshake or status-like rather than pure configuration:

- Lane fields in `PHY_CNTL3` pair control bits (`RESET`, `DISABLE`, `DATA_EN`, `REQ`) with hardware-visible status/handshake bits (`CLK_RDY`, `ACK`).
- DP-alt fields in `PHY_CNTL6` and `DMCU_DPALT_*` coordinate Type-C/DP-alt ownership with firmware or DMCU paths, including disable, disable-ack, DP4 mode, ref-clock enable, and ref-clock request.
- Interrupt control fields expose sticky status bits and clear/mask controls for FIFO, register FIFO, and DP-alt toggle events.
- Fuse fields expose calibration values that are expected to match silicon-programmed defaults and should generally be treated as hardware-provided tuning inputs.

Because this is a mask header, persistence risks arise from incorrect bit definitions: an incorrect mask can make unrelated bits sticky, clear the wrong interrupt, misprogram PLL state, or break the DP-alt ownership handshake.

## Dependencies And Integration Points

This chunk depends on the matching offset header for register addresses and on the AMD DC register helper conventions that combine register offsets, shifts, and masks. The primary source-tree integration points are:

- `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes `dpcs_2_1_0_offset.h` and this mask header and initializes DCN 2.1 link encoder register, shift, and mask tables.
- `drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.h`, which defines the DCN 2.1 DPCS mask/shift field list used to populate those tables.
- `drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.h`, which defines the common DPCS field list inherited by DCN 2.1.
- `drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.c`, where runtime PHY acquire/release paths read and update fields such as `RDPCS_PHY_DPALT_DISABLE`, `RDPCS_PHY_DPALT_DISABLE_ACK`, and `RDPCS_PHY_DP_REF_CLK_EN`.

The instance-4 definitions are important because DCN 2.1 resource construction declares five link encoder register sets, mapping `id` values 0 through 4. Any missing or malformed `DPCSTX4`/`RDPCSTX4` field definition can therefore break compilation or silently misconfigure the fifth transmitter.

## Risks And Edge Cases

The main risk is structural drift between instances. The register helper field lists often name fields using instance-0 symbols, then instantiate offsets per encoder. For this pattern to stay correct, `RDPCSTX3` and `RDPCSTX4` masks must mirror the same bit layout as the earlier instances for every shared field. A one-bit difference in lane reset, request/ack, rate/width, or MPLL programming could affect only specific physical connectors and be difficult to isolate.

PLL and spread-spectrum fields are high risk: `MPLLB_FRACN_DEN`, `MPLLB_FRACN_QUOT`, `MPLLB_SSC_PEAK`, `MPLLB_SSC_STEPSIZE`, `MPLLB_MULTIPLIER`, `MPLLB_TX_CLK_DIV`, `MPLLB_STATE`, `MPLLB_FRACN_EN`, and related divider fields control link clock synthesis. Incorrect masks can produce unstable DP link training, wrong pixel clocks, or failures at high link rates.

DP-alt ownership fields are another high-risk area. `RDPCS_PHY_DPALT_DISABLE`, `RDPCS_PHY_DPALT_DISABLE_ACK`, `RDPCS_PHY_DPALT_DP4`, `RDPCS_ALLOW_DRIVER_ACCESS`, and `RDPCS_DRIVER_ACCESS_BLOCKED` coordinate driver access with firmware/DMCU and USB-C alternate mode. Incorrect masks may cause the driver to access PHY registers while blocked or fail to acknowledge ownership transitions.

Generated-header naming is also fragile. Consumer macros depend on exact token concatenation. Renaming a field, changing `_MASK`/`__SHIFT` suffixes, or defining a field only for some instances will surface as compile failures when a selected `LE_SF` expands, or as missing coverage for a physical transmitter if the field is never instantiated.

## Test Signals

The first signal is build coverage for DCN 2.1 display support. Compiling the AMD display driver with `dcn21_resource.c` exercises the token-concatenation contract between register lists and this header. Missing constants for `DPCSTX4`, `RDPCSTX4`, or `DPCSSYS_CR4` should fail at compile time once the relevant register list is expanded.

Runtime signals are hardware/display oriented:

- DP link training and mode-set success across all physical transmitter instances, especially the fifth instance that uses the `*4` definitions.
- USB-C DP-alt acquire/release behavior, including correct `DPALT_DISABLE` and `DPALT_DISABLE_ACK` transitions and ref-clock enable/disable sequencing.
- Stable high-rate DP modes that depend on correct MPLL fractional, spread-spectrum, divider, and pstate fields.
- Absence of FIFO, register FIFO, and DP-alt toggle interrupt storms, and correct clear/mask behavior after display hotplug or mode changes.
- Correct lane enable, clock-ready, data-enable, request, and ack behavior for one-, two-, and four-lane link configurations.

There are no local unit tests for this header alone. The meaningful validation comes from compile-time macro expansion, AMD display driver bring-up, connector hotplug/mode-set tests, DP link-training logs, and hardware register readback when debugging specific PHY or DP-alt failures.
