# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 14317-16696

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask register-field slice. It contains no executable C logic; it publishes preprocessor constants that describe bit offsets and masks for DPCS CR0 raw-lane digital registers used by AMDGPU display link-encoder code. The companion `dpcs_4_2_2_offset.h` file supplies the matching MMIO/indexed-register addresses, while this header supplies the field geometry needed by register helpers and macro-generated shift/mask tables.

The requested range covers 2,111 `#define` entries: 1,058 `__SHIFT` macros and 1,053 `_MASK` macros. It starts in the tail of `RAWLANE0`, contains the full register-field map for `RAWLANE1`, and continues through most of the early `RAWLANE2` map. The chunk boundary is artificial: it stops after the first two masks for `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_TX_OVRD_IN_2`, with the remaining masks for that register immediately after line 16696.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or callable APIs in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset of a DPCS register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, or update that field.

The covered register groups are all under `DPCSSYS_CR0_RAWLANE<n>_DIG_*`:

- `RAWLANE0` tail: TX control, RX control, ATE RX/TX override inputs, master MPLL loop enables, VCO/reference load override fields, RX-valid override output, and late TX override input bits.
- `RAWLANE1` complete lane slice: PCS transmit and receive override/input/output registers; RX equalization, adaptation, figure-of-merit, lane number, TX pre/main/post cursor direction registers; FSM override/status/fast-step monitor registers; IRQ request/status/clear/mask registers; PMA override/input registers; TX/RX control registers; and ATE override registers.
- `RAWLANE2` early lane slice: the same PCS, FSM, IRQ, PMA, TX/RX control, and ATE register pattern through the first two masks of `PCS_XF_TX_OVRD_IN_2`.

Important field families in this chunk include:

- Link operating-state fields such as `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, and master MPLL state/override enables.
- TX/RX request, reset, data-enable, async-data, beacon, RX detect, RX valid, and serial/parallel loopback override value/enable pairs.
- RX adaptation and calibration controls/status: `ADAPT_REQ`, `ADAPT_ACK`, `ADAPT_DONE`, `ADAPT_FOM`, IQ/AFE/DFE/reflvl calibration fast-step bits, continuous calibration/adaptation fields, and PH2 calibration.
- Equalization and termination controls: TX pre/main/post direction fields, RX EQ delta/IQ override fields, TX/RX termination control override fields, and PMA lane/termination/tune controls.
- IRQ state and acknowledgement fields for RX/TX reset/request/rate/pstate/adapt transitions, lane transceiver mode, PH2 calibration, loopback changes, DCC on-demand, and mask registers.
- Observability/test hooks, including `OCLA`, `UPCS_OCLA`, `FSM_*_MON`, reserved monitor slots, ATE override registers, and PMA/MPHY override inputs/outputs.

Most fields are 16-bit register layouts represented with 32-bit-looking mask literals in this version (`0x0000....L`). Reserved fields are also emitted as macros, so consumers must avoid treating their presence as permission to write undocumented bits.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMD display code that includes generated offset and shift/mask headers, builds register tables, and uses those tables through register helper macros.

The typical path is:

1. ASIC-specific resource or link-encoder code includes the matching DPCS offset and shift/mask headers.
2. Register-list macros select concrete `ixDPCSSYS_CR0_RAWLANE...` offsets from `dpcs_4_2_2_offset.h`.
3. Field-list macros use token-pasting helpers such as `LE_SF(<reg>, <field>, __SHIFT)` and `LE_SF(<reg>, <field>, _MASK)` to initialize `struct dcn10_link_enc_shift` and `struct dcn10_link_enc_mask` instances.
4. Link encoder and PHY programming paths use `REG_GET`, `REG_SET`, `REG_UPDATE`, indexed register reads/writes, or equivalent helpers to update individual fields without hard-coding bit positions.

The chunk itself does not encode programming order. Sequencing for resets, PLL enablement, rate/width changes, lane power states, RX adaptation, IRQ acknowledgement, loopback/test overrides, and PMA controls is determined by the display link-encoder implementation and the hardware programming guide.

## State And Persistence Behavior

This file stores no software state and persists nothing on its own. It describes hardware state in the DPCS CR0 raw-lane register space:

- Lane configuration state for link rate, lane width, power state, low-power detect, MPLL selection/enables, and RX/TX data/clock enables.
- TX and RX finite-state-machine state, including fast calibration/adaptation step bits, status monitors, CR lock, DCC flags/status, and lane reset/request handshakes.
- Interrupt state and control bits for lane events, with separate status, clear, and mask registers.
- PHY-facing PMA and PCS state for lane overrides, PMA inputs/outputs, RX valid, RX adaptation, equalization, TX cursor direction, termination, VCO/reference load overrides, and loopback controls.
- Test/debug state for ATE overrides, OCLA/UPCS OCLA, MPHY overrides, and reserved monitor registers.

Persistence is hardware-defined. Configuration fields generally last until the driver reprograms the link, disables or power-gates the PHY, performs suspend/resume restore, resets the display engine, or resets the ASIC. Status, IRQ, acknowledgement, calibration, and monitor bits may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant clock and power domains are active. The generated macros do not identify access type or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DPCS 4.2.2 register database and especially with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which defines the matching `ixDPCSSYS_CR0_RAWLANE...` register addresses. For example, the offset file maps `RAWLANE0` TX/RX/ATE registers around `0x3080`-`0x30c8`, `RAWLANE1` around `0x3100`-`0x31c8`, and `RAWLANE2` around `0x3200` onward, matching the lane repetition visible in this shift/mask chunk.

Display integration is through AMDGPU display link-encoder register tables:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.h` defines `DPCS_DCN2_MASK_SH_LIST(mask_sh)`, which expands field constants into link-encoder shift/mask tables through `LE_SF(...)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c` initializes `le_shift` with `DPCS_DCN2_MASK_SH_LIST(__SHIFT)` and `le_mask` with `DPCS_DCN2_MASK_SH_LIST(_MASK)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.h` extends the DPCS field list with CR0 `RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_2` and `RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_3` VCO/reference load override fields, which are present in this chunk.
- Later DCN resource files use similar DPCS mask/shift table patterns, so generated-field correctness affects link bring-up, PHY control, debug override plumbing, and power-management behavior across ASIC variants that consume this register family.

The most direct behavioral integration from this chunk is display PHY and DisplayPort/HDMI link-lane control: link training, lane rate/width programming, MPLL gating, lane reset/request handshakes, RX adaptation/calibration, lane IRQ handling, and diagnostic/ATE paths.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bit, corrupting a neighboring field, missing a status bit, or clearing an interrupt incorrectly.
- The file is generated metadata. Manual edits risk divergence from the offset header, AMD's authoritative register database, firmware expectations, and silicon documentation.
- Lane definitions are repetitive but not risk-free. A generator or copy/paste error can affect only `RAWLANE1` or `RAWLANE2`, so one working lane does not prove the others are correct.
- The chunk boundary cuts through `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_TX_OVRD_IN_2`: shifts and two masks are inside this range, while the remaining masks are in the next chunk. Consumers and merged research must consider the full register definition across chunk boundaries.
- Reserved field masks are emitted. Code should preserve reserved bits unless the hardware specification explicitly says otherwise.
- Override registers often pair a value bit with an enable bit. Setting only the value or only the enable can leave hardware in normal mode, force stale values, or wedge debug/test paths.
- IRQ/status/clear registers are side-effect-sensitive. Confusing status fields with clear fields, or mask fields with enable fields, can cause missed HPD/link events, interrupt storms, or stuck lane state.
- PMA/PCS calibration and MPLL controls are timing-sensitive. Incorrect field geometry or sequencing can cause link-training failures, unstable high-rate links, silent black screens, or suspend/resume-only regressions.
- Some masks use the wider `0x0000....L` literal style compared with older DPCS headers that use shorter 16-bit masks. Mechanical comparisons across ASIC revisions should normalize values before flagging differences.

## Test Signals

Useful validation is mostly compile-time plus hardware/link behavior:

- Build AMDGPU display code for ASIC configurations that include DPCS 4.2.2 headers. Missing, renamed, or malformed macros should fail in link-encoder/resource table initializers that token-paste register and field names.
- Run a generated-header consistency check that verifies every `__SHIFT` has the expected `_MASK` within the full file, while allowing this chunk's artificial split for `RAWLANE2_DIG_PCS_XF_TX_OVRD_IN_2`.
- Compare `dpcs_4_2_2_sh_mask.h` against `dpcs_4_2_2_offset.h` and adjacent generated revisions (`dpcs_4_2_0`, `dpcs_4_2_3`) for lane-stride consistency and intended field-layout changes.
- Exercise display link bring-up at multiple DisplayPort rates and lane counts, including retraining, hotplug, suspend/resume, and modeset transitions.
- Validate lane-specific behavior on one-, two-, and four-lane configurations so `RAWLANE1` and `RAWLANE2` paths are actually programmed, not just `RAWLANE0`.
- Check diagnostics for IRQ clear/mask behavior, RX adaptation completion, link-training status, DCC status, and PMA/PCS debug outputs when hardware and debug tooling expose them.
- For changes to override/test fields, use targeted ATE or debug-mode tests; normal desktop display tests may never touch those bits.
