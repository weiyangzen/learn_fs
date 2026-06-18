# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 42088-44705

## Purpose

This chunk is part of the generated AMDGPU DCN 1.0 register field shift/mask header. It contains no executable logic; it publishes preprocessor constants that describe packed bit fields in DCN 1.0 DCIO, ComboPHY common, ComboPHY transmitter, and ComboPHY PLL registers.

Each field is represented by the standard generated pair:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

The constants in this chunk are paired with register address definitions from `dcn_1_0_offset.h`. Consumers use both files through AMD display register helpers and structures, so the chunk is a hardware-layout contract for link encoder, PHY, PLL, clock-source, BIOS-table, and display resource code rather than a standalone software module.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or runtime APIs in this line range. The macro namespace is the API surface.

Major macro groups in this chunk are:

- Tail of `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED152` through `RESERVED159`: full-width `UNIPHY_MACRO_CNTL_RESERVED` masks for the end of UNIPHY0's reserved macro-control window.
- `DC_COMBOPHYCMREGS0_*`, `DC_COMBOPHYCMREGS1_*`, and `DC_COMBOPHYCMREGS2_*`: common ComboPHY register fields for PHY instances 0, 1, and 2. These include fuse-valid and fuse payload fields (`COMMON_FUSE1` through `COMMON_FUSE3`), nominal margin/de-emphasis defaults (`COMMON_MAR_DEEMPH_NOM`), lane power management (`COMMON_LANE_PWRMGMT`), transmitter common control (`COMMON_TXCNTRL`), lane resets (`COMMON_LANE_RESETS`), impedance/calibration override fields (`COMMON_ZCALCODE_CTRL`), and reserved display RFU registers.
- `DC_COMBOPHYTXREGS0_*`, `DC_COMBOPHYTXREGS1_*`, and the start of `DC_COMBOPHYTXREGS2_*`: per-lane transmitter command bus fields. For each lane, `CMD_BUS_TX_CONTROL_LANEn` exposes `tx_pwr`, `tx_pg_en`, and `tx_rdy`; `MARGIN_DEEMPH_LANEn` exposes `txmarg_sel`, `deemph_sel`, and `tx_margin_en`; `CMD_BUS_GLOBAL_FOR_TX_LANEn` exposes link and PCS controls such as `twosym_en`, `link_speed`, `gang_mode`, `max_linkrate`, `pcs_freq`, `pcs_clken`, `pcs_clkdone`, `pll1_always_on`, `rdclk_div2_en`, `tx_boost_adj`, `tx_boost_en`, and `tx_binary_ron_code_offset`. Each lane also has `TX_DISP_RFU0` through `TX_DISP_RFU12` full-width reserved fields.
- `DC_COMBOPHYPLLREGS0_*` and `DC_COMBOPHYPLLREGS1_*`: ComboPHY PLL tuning, calibration, observation, and wrapper fields. These define frequency-control words (`fcw*_frac` and `fcw*_int`), coarse/fine bandwidth and bias controls, calibration enable/delay/range/test fields, loop-control fields, voltage regulator configuration, observation outputs, DFT output, and wrapper power/reset/lock/status controls.
- `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159` and `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159`: full-width reserved macro-control windows for additional UNIPHY instances. These keep generated address/mask coverage complete even when most fields are not named at this level.

The range ends in the middle of `DC_COMBOPHYTXREGS2_CMD_BUS_GLOBAL_FOR_TX_LANE3`, after the `pll1_always_on` shift definition. Later chunks continue that register and the rest of the ComboPHY instance 2 transmitter/PLL definitions.

## Control Flow

This header chunk has no runtime control flow. It is a collection of `#define` statements.

Runtime control flow appears in consumers that:

1. Select a register address from `dcn_1_0_offset.h`, such as `mmDC_COMBOPHYCMREGS0_COMMON_FUSE1`, `mmDC_COMBOPHYTXREGS0_CMD_BUS_TX_CONTROL_LANE0`, `mmDC_COMBOPHYPLLREGS0_FREQ_CTRL0`, or `mmDCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0`.
2. Use a matching `*_MASK` and `*__SHIFT` macro from this header to extract or insert a field.
3. Read, modify, and write the MMIO register through AMDGPU/display register helper macros or through structures initialized in DC resource construction.

Sequencing-sensitive runtime operations represented by these fields include PHY lane power transitions, lane resets, link-rate and PCS clock programming, transmitter margin/de-emphasis setup, PLL frequency programming, PLL calibration, PLL reset/power transitions, and lock/status polling. The header does not encode required ordering, delays, access permissions, or read-only versus write-only behavior; those rules live in display, BIOS, firmware, and hardware programming code.

## State And Persistence Behavior

The file stores no software state and has no persistence behavior. It describes state located in hardware registers.

The represented hardware state includes eFuse-derived PHY calibration values, PHY lane power-gating controls, lane reset bits, transmitter power/readiness state, per-lane electrical margin and de-emphasis settings, link-speed and PCS clock controls, PLL frequency-control words, PLL bandwidth/bias/calibration controls, PLL lock and observation status, and large reserved UNIPHY and RFU register windows.

Persistence is hardware-defined. Some fields are stable configuration values until a later driver/firmware write, some are sampled fuse or status values, some may change as hardware calibration or PLL lock progresses, and reset/power-gating fields may be lost or reinitialized across display reset, ASIC reset, suspend/resume, runtime power transitions, or BIOS/firmware transmitter-control calls. The generated masks themselves do not document volatility or clear-on-read/write-one-to-clear behavior.

## Dependencies And Integration Points

Primary paired address dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

Direct DCN 1.0 include point:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c` includes both `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.

Important integration paths:

- `dcn10_resource.c` builds DCN 1.0 resource tables and maps `TRANSMITTER_UNIPHY_A` through `TRANSMITTER_UNIPHY_D` to PHY instances. These transmitter/PHY identities align with the generated UNIPHY and ComboPHY instance namespaces in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.*` handles DCN 1.0 link encoder behavior, including UNIPHY transmitter assignment, lane mapping, resets, and link enablement. It consumes the same generated register infrastructure even when higher-level macros hide individual field names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.h` defines DCN 1.0 clock-source register and mask lists. Those lists are initialized from the generated address and shift/mask headers in `dcn10_resource.c`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.c` provides BIOS transmitter and PHY programming calls for UNIPHY-backed outputs. The generated register fields here describe the MMIO-level state that BIOS/driver sequences must leave coherent.
- Display link code maps encoder IDs and transmitters through `TRANSMITTER_UNIPHY_*` values in files such as `display/dc/link/link_factory.c`, `display/dc/core/dc_resource.c`, and related DIO/HWSS paths.

Equivalent or near-equivalent definitions also appear in generated DCE 12.0 and later DCN/DPCS headers, showing that these PHY bit layouts are part of AMD's generated register database and evolve across ASIC generations.

Although the source tree is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It has no Ceph filesystem protocol behavior, no distributed filesystem data flow, and no persistent storage semantics.

## Risks And Edge Cases

The main risk is silent display hardware misprogramming. A bad mask or shift can compile cleanly while writing the wrong PHY, PLL, or lane-control bits.

High-risk areas include:

- ComboPHY PLL fields: wrong frequency-control word, bandwidth, bias, calibration, reset, or wrapper-control masks can prevent PLL lock, produce unstable pixel/link clocks, break modesets, or cause intermittent link training failures.
- Transmitter lane controls: incorrect `tx_pwr`, `tx_pg_en`, `tx_rdy`, link speed, PCS clock, gang-mode, boost, margin, or de-emphasis masks can leave lanes powered down, fail readiness polling, train at the wrong rate, or violate DP/HDMI electrical requirements.
- Lane reset and power-management fields: incorrect reset or power gating masks can wedge a PHY lane, race link enablement, or cause resume failures after display power transitions.
- Fuse and calibration fields: mis-decoding `COMMON_FUSE*` or `ZCALCODE_CTRL` can apply wrong termination, impedance, CDR, or calibration defaults. These bugs can be board- or cable-sensitive.
- Reserved/RFU registers: many fields are full-width placeholders. Treating them as generally writable is risky because reserved registers may have undocumented side effects; generated masks only describe bit positions, not safe programming policy.
- Chunk boundary risk: the assigned range starts after earlier UNIPHY0 reserved definitions and stops mid-register in ComboPHYTXREGS2. The merge lane must not interpret this chunk as a complete module boundary.

## Test Signals

Useful validation signals are mostly compile-time, register-database, and hardware-integration oriented:

- Build coverage for DCN 1.0 display paths that include `dcn_1_0_offset.h` and `dcn_1_0_sh_mask.h`.
- Static comparison of every `*_MASK` and `*__SHIFT` pair in this chunk against AMD's register database and the matching addresses in `dcn_1_0_offset.h`.
- Modeset and link-training tests on DCN 1.0 hardware for all supported UNIPHY transmitters and lane counts, including DP, eDP, HDMI, and any board-specific PHY routing.
- PLL programming tests that verify lock status, stable pixel clocks, clock-source selection, deep-color pixel-clock behavior, and repeated modeset changes.
- Suspend/resume, runtime power management, and hotplug cycles that exercise PHY power gating, lane reset, transmitter readiness, and BIOS/driver reinitialization ordering.
- Electrical/link margin validation, especially across different cables, link rates, de-emphasis/margin settings, and multi-lane configurations.
- Register readback or debug tooling that confirms writes affect only intended fields and that reserved/RFU registers are not touched by normal programming paths.

Regression symptoms from incorrect constants include no display after modeset, intermittent DP link training failure, HDMI/eDP output instability, missing or unstable pixel clock, PLL lock timeouts, lanes stuck in reset or power-down, display corruption at specific link rates, resume failures, and hardware status polling loops that never observe the expected ready or lock bit.

## Cross-Chunk Notes

Earlier chunks of `dcn_1_0_sh_mask.h` define the preceding DCN display, clocking, DIO, and UNIPHY0 fields. This chunk continues the DCIO/ComboPHY register map for PHY instances 0 through 2. Later chunks complete `DC_COMBOPHYTXREGS2_CMD_BUS_GLOBAL_FOR_TX_LANE3` and continue subsequent ComboPHY/UNIPHY instances and remaining DCN 1.0 register field definitions. The final per-file research document should treat the full header as one generated DCN 1.0 register-layout contract.
