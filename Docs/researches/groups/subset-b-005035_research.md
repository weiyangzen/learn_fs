# Research Report: subset-b-005035

This grouped report covers Qualcomm QMP PHY PCS and QSERDES register-offset headers under `sources/distributed-fs/ceph-client/drivers/phy/qualcomm`. Each section preserves the source path for reconciliation into the required source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v8.h

Purpose: Defines the QMP v8 USB PCS register offsets for USB-specific power-state, LFPS, receiver-detect, RX equalization training, and test-control programming. It is a narrow address-map header, not an implementation file.

Important APIs/types/functions: Exports `QPHY_V8_PCS_USB_*` macros, including `POWER_STATE_CONFIG1..4`, `AUTONOMOUS_MODE_*`, `LFPS_*`, `RXEQTRAINING_*`, `RCVR_DTCT_*`, and `TEST_CONTROL`. There are no functions or types.

Control flow: No executable control flow exists. Runtime flow is indirect through QMP USB/combo init arrays that use these macros in `QMP_PHY_INIT_CFG` entries before the generic QMP PHY start and status polling sequence.

State and persistence: The header has no mutable state. Values written through these offsets persist in USB PCS hardware until reset, power collapse, or a later reconfiguration.

Dependencies and integration points: Included by `phy-qcom-qmp-usb.c` and `phy-qcom-qmp-combo.c`; used with common QMP register write helpers.

Risks: Wrong offsets can silently program LFPS or power-state registers incorrectly, causing USB3 link training, U1/U2/U3 transitions, or receiver detect failures.

Test signals: Build coverage for v8 USB PHY tables, probe on matching Qualcomm platforms, USB3 link-up, suspend/resume, LFPS wake, and link-training stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v2.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v2.h

Purpose: Provides the legacy QMP v2 PCS register map shared by early USB and PCIe PHY configurations. It covers reset/start, power state, lock detect, FLL, LFPS, signal-detect, wake-delay, and status offsets.

Important APIs/types/functions: Exports `QPHY_V2_PCS_*` macros such as `SW_RESET`, `POWER_DOWN_CONTROL`, `START_CONTROL`, `LOCK_DETECT_CONFIG*`, `FLL_*`, `USB_PCS_STATUS`, and `PCI_PCS_STATUS`. No functions or data structures are defined.

Control flow: No code executes here. The common QMP header includes it, and protocol drivers reference the constants from static init tables consumed by the QMP PHY initialization sequence.

State and persistence: The macros identify hardware registers; runtime state is only created when the driver writes or polls those addresses. Hardware settings persist until the PHY is reset or powered down.

Dependencies and integration points: Pulled into `phy-qcom-qmp.h`, then used by QMP USB/PCIe-era SoC tables.

Risks: v2 has USB and PCIe status offsets in the same PCS map, so using the wrong protocol-specific status macro can break readiness detection.

Test signals: Compile use of v2 tables, successful probe, PLL/PCS lock polling, USB/PCIe link establishment, and low-power wake timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v3.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v3.h

Purpose: Defines the full QMP v3 PCS offset map for USB/PCIe style PHYs. It expands v2 with TX amplitude/de-emphasis groups, receiver-detect timing, LFPS timers, equalization training, BIST/PRBS, debug/status, oscillator-detect, and refgen request controls.

Important APIs/types/functions: Exports `QPHY_V3_PCS_*` macros for reset/start, TX magnitude and deemphasis levels, power states, lock detect, FLL, autonomous mode, signal detect, test/BIST, revision IDs, debug buses, wake delays, and `REFGEN_REQ_CONFIG*`. No functions or types exist.

Control flow: None locally. Static QMP init arrays write selected offsets, then the generic QMP power-on path polls PCS status and lock bits.

State and persistence: All state is hardware-resident. Writes to these offsets configure signal quality, timing, test, and low-power behavior until reset or another table write.

Dependencies and integration points: Included through `phy-qcom-qmp.h`; consumed by protocol-specific QMP PHY drivers and their SoC configuration tables.

Risks: The dense map mixes operational and diagnostic registers. Confusing status/debug offsets with writable configuration offsets can cause non-obvious link-training failures.

Test signals: Build for v3 users, PCS lock/status polling, link-up across supported rates, LFPS or electrical-idle behavior, and BIST/debug register sanity checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v4.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v4.h

Purpose: Supplies the QMP v4 USB/PCIe PCS register map. Compared with v3, the layout starts with revision/status and debug registers, then covers power control, in/out signal muxing, FLL, lock detect, test/BIST, Gen1/2 and Gen3/2 TX settings, receiver detect, alignment, RX idle, DCC, and equalization.

Important APIs/types/functions: Exports `QPHY_V4_PCS_*` macros, including `PCS_STATUS*`, `POWER_DOWN_CONTROL`, `START_CONTROL`, `INSIG_*`, `OUTSIG_*`, `LOCK_DETECT_CONFIG*`, `G12S1_*`, `G3S2_*`, `RX_SIGDET_*`, `ALIGN_DETECT_CONFIG*`, and `EQ_CONFIG*`. No functions or types.

Control flow: No direct flow. QMP init tables select offsets appropriate for each SoC and the shared PHY code applies them during bring-up.

State and persistence: Register writes program PCS link timing and equalization state in hardware until PHY reset or reinitialization.

Dependencies and integration points: Included by `phy-qcom-qmp.h` for common QMP users.

Risks: v4 changed offsets relative to older maps; reusing v3 constants or choosing v4_20 deltas incorrectly can program the wrong PCS fields.

Test signals: Compile coverage, probe, status polling, PCIe/USB link training, receiver-detect, equalization, suspend/resume, and debug status reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v4_20.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v4_20.h

Purpose: Captures the small PCS offset differences for QMP v4.20 hardware, mainly signal-detect and equalization registers whose addresses differ from base v4.

Important APIs/types/functions: Exports `QPHY_V4_20_PCS_RX_SIGDET_LVL`, `QPHY_V4_20_PCS_EQ_CONFIG2`, `QPHY_V4_20_PCS_EQ_CONFIG4`, and `QPHY_V4_20_PCS_EQ_CONFIG5`. There are no functions or types.

Control flow: No direct flow. SoC-specific init tables choose these macros instead of the base v4 names when the PCS layout is v4.20.

State and persistence: Only identifies hardware offsets. Programmed values persist in PCS equalization and signal-detect logic until reset or rewrite.

Dependencies and integration points: Included through `phy-qcom-qmp.h` and paired with v4/v4.20 QMP configuration tables.

Risks: Because this is a delta header, missing a v4.20-specific constant may lead developers to accidentally use a base v4 offset that writes the wrong register.

Test signals: Build of v4.20 users, link training on affected SoCs, receiver-detect threshold behavior, and stable equalization at target rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v4_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v5.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v5.h

Purpose: Defines the reduced QMP v5 PCS offset set needed by USB/PCIe PHY tables. It keeps common reset/start, status, lock detect, refgen request, signal detect, receiver detect, rate slew, alignment, TX/RX config, and equalization registers.

Important APIs/types/functions: Exports `QPHY_V5_PCS_*` macros such as `SW_RESET`, `PCS_STATUS1`, `POWER_DOWN_CONTROL`, `START_CONTROL`, `LOCK_DETECT_CONFIG*`, `REFGEN_REQ_CONFIG1`, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, `RX_CONFIG`, `PCS_TX_RX_CONFIG`, and `EQ_CONFIG*`. No code is defined.

Control flow: No local control flow. QMP init arrays write these offsets during PHY initialization before common start and status polling.

State and persistence: Hardware-only state; the header contains immutable numeric constants.

Dependencies and integration points: Included by `phy-qcom-qmp.h`, and used with USB/PCIe QMP configuration tables.

Risks: `CDR_RESET_TIME` and `RX_CONFIG` share offset `0x1b0` under different semantic names, so table authors must choose the name matching the protocol block meaning.

Test signals: Build, probe, PCS lock, RX detect, alignment, equalization, and link-up on v5 PHY platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v5_20.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v5_20.h

Purpose: Provides QMP v5.20 PCS offset overrides for signal mux, lock-detect, TX pre-gain, signal-detect, alignment, and equalization fields.

Important APIs/types/functions: Exports `QPHY_V5_20_PCS_*` macros for `INSIG_SW_CTRL7`, `INSIG_MX_CTRL7`, lock-detect config, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, `ALIGN_DETECT_CONFIG*`, and `EQ_CONFIG*`. It has no functions or structures.

Control flow: None. The macros are used by version-specific init tables and then applied by common QMP register-write flow.

State and persistence: Contains no state. Programmed values affect PCS muxing, lock detection, signal thresholds, alignment, and equalization until the PHY is reset or retuned.

Dependencies and integration points: Included from `phy-qcom-qmp.h`; paired with v5.20 SoC tables in QMP protocol drivers.

Risks: Small offset shifts are easy to miss during SoC enablement. Incorrect align/equalization offsets can pass compilation but fail only as marginal high-speed links.

Test signals: Version-specific platform probe, PCS lock, link-up at all supported rates, eye/equalization stability, and suspend/resume recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v5_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6-n4.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6-n4.h

Purpose: Defines the QMP v6 N4 PCS register subset for USB/PCIe-style PHYs. The map covers reset, status, power/start, power-state config, lock detect, refgen request, signal detect, receiver detect, rate slew, RX config, alignment, TX/RX config, and equalization.

Important APIs/types/functions: Exports `QPHY_V6_N4_PCS_*` constants, including `POWER_STATE_CONFIG1`, `LOCK_DETECT_CONFIG1..6`, `RX_SIGDET_LVL`, `RCVR_DTCT_DLY_P1U2_*`, `RX_CONFIG`, `ALIGN_DETECT_CONFIG*`, and `EQ_CONFIG*`. No functions or types.

Control flow: No executable logic. SoC tables reference these constants and the shared QMP driver writes them during initialization.

State and persistence: Immutable offsets only. Hardware state persists after register writes until reset or reconfiguration.

Dependencies and integration points: Included by `phy-qcom-qmp.h` for common QMP SoC configuration code.

Risks: N4 has its own namespace despite similarity to v6. Mixing `QPHY_V6_N4_*` and base `QPHY_V6_*` constants can target wrong offsets on newer nodes.

Test signals: Build for N4 users, probe, power-state behavior, PCS lock, signal detect, and stable USB/PCIe link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6-n4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6.h

Purpose: Supplies the base QMP v6 PCS offset subset for USB/PCIe PHY initialization. It mirrors the compact v5-style map with updated v6 naming.

Important APIs/types/functions: Exports `QPHY_V6_PCS_*` macros for reset, `PCS_STATUS1`, power control, start, lock-detect configs, refgen request, `G12S1_TXDEEMPH_M6DB`, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, receiver detect, rate slew, `RX_CONFIG`, align detect, `PCS_TX_RX_CONFIG`, and equalization configs.

Control flow: No code executes. Constants are consumed by static PHY tables and written by common QMP initialization helpers.

State and persistence: No in-memory state. Register values written through these offsets configure PCS state until reset/powerdown.

Dependencies and integration points: Included from `phy-qcom-qmp.h`; used by common USB/PCIe QMP platform descriptors.

Risks: Base v6, v6.20, v6.30, and v6 N4 are close but not interchangeable. Offset mistakes are hardware-visible and often appear as link-training timeouts.

Test signals: Build, probe, PCS status polling, Gen/rate-specific link-up, equalization, receiver detect, and low-power transition tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6_20.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6_20.h

Purpose: Provides QMP v6.20 PCS offset overrides for selected TX de-emphasis, pre-gain, signal-detect, electrical-idle delay, TX/RX config, and equalization registers.

Important APIs/types/functions: Exports `QPHY_V6_20_PCS_G12S1_TXDEEMPH_M6DB`, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, `COM_ELECIDLE_DLY_SEL`, `TX_RX_CONFIG1`, `TX_RX_CONFIG2`, `EQ_CONFIG4`, and `EQ_CONFIG5`. No functions or types.

Control flow: None. These constants are chosen by v6.20-specific init tables and applied by the common QMP register writer.

State and persistence: Immutable address definitions only; programmed values persist in PCS hardware until reset/rewrite.

Dependencies and integration points: Included in `phy-qcom-qmp.h` and directly included by `phy-qcom-qmp-pcie.c` for v6.20 PCIe tables.

Risks: This delta header does not restate base v6 offsets, so SoC table authors must combine the right base and variant constants deliberately.

Test signals: v6.20 platform build/probe, PCIe or USB link training, electrical-idle behavior, de-emphasis tuning, and equalization margin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6_30.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6_30.h

Purpose: Defines the small QMP v6.30 PCS delta used where selected de-emphasis, signal-detect, electrical-idle, TX/RX config, and equalization registers shifted from base v6.

Important APIs/types/functions: Exports `QPHY_V6_30_PCS_G12S1_TXDEEMPH_M6DB`, `RX_SIGDET_LVL`, `COM_ELECIDLE_DLY_SEL`, `TX_RX_CONFIG1`, `TX_RX_CONFIG2`, `EQ_CONFIG1`, `EQ_CONFIG4`, and `EQ_CONFIG5`. It defines no code.

Control flow: No local control flow. PCIe and common QMP tables refer to these offsets and the shared init path writes them.

State and persistence: No state in the header. Values written to these offsets persist in PCS link-training hardware until reset or reprogramming.

Dependencies and integration points: Included by `phy-qcom-qmp-pcie.c`; used with v6.30 PCIe PCS tables and common QMP helpers.

Risks: The naming overlaps with PCIe-specific v6.30 PCS headers, so developers must keep common PCS and protocol-specific PCS offsets distinct.

Test signals: Build for v6.30 users, PCIe link training, equalization across supported generations, electrical-idle transitions, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6_30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v7.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v7.h

Purpose: Supplies the QMP v7 PCS common offset subset. It covers reset/start, status, power control, lock detect, refgen, TX de-emphasis/pre-gain, signal detect, receiver detect, RX config, align detect, TX/RX config, and equalization.

Important APIs/types/functions: Exports `QPHY_V7_PCS_*` macros such as `SW_RESET`, `PCS_STATUS1`, `LOCK_DETECT_CONFIG*`, `REFGEN_REQ_CONFIG1`, `G12S1_TXDEEMPH_M6DB`, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, `RX_CONFIG`, `PCS_TX_RX_CONFIG`, and `EQ_CONFIG*`. No functions or structs.

Control flow: None directly. QMP init tables consume these offsets, and common QMP PHY code performs writes and later status polling.

State and persistence: The header is stateless; hardware retains programmed PCS settings until reset/reinitialization.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and used by newer protocol-specific QMP tables.

Risks: v7 continues the compact map trend but has version-specific offsets. Copying v6 or v8 table entries without checking the namespace can misprogram the PCS.

Test signals: Compile, platform probe, lock/status polling, high-speed link training, equalization stability, and power-management cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v8.h

Purpose: Defines base QMP v8 PCS offsets for common USB/PCIe-style PHY setup. The map includes reset/start, status, power control, lock detect, refgen, signal detect, RX config, alignment, TX/RX config, and equalization.

Important APIs/types/functions: Exports `QPHY_V8_PCS_*` macros, including `SW_RESET`, `PCS_STATUS1`, `POWER_DOWN_CONTROL`, `START_CONTROL`, `LOCK_DETECT_CONFIG*`, `REFGEN_REQ_CONFIG1`, `RX_SIGDET_LVL`, `RX_CONFIG`, `ALIGN_DETECT_CONFIG*`, `TX_RX_CONFIG*`, and `EQ_CONFIG*`. No executable APIs exist.

Control flow: None. Consumers use these offsets in static initialization tables, which the generic QMP path applies before enabling the PHY and polling readiness.

State and persistence: The file stores only constants; register values persist in the PCS block until reset or table rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used alongside v8 QSERDES COM/TXRX/LALB headers and protocol-specific PCS headers.

Risks: v8 has additional specialized headers for USB, PCIe, AON, and LALB blocks. Using the base PCS offset for a protocol-specific PCS register can target the wrong block.

Test signals: Build, probe, PCS status readiness, USB/PCIe link-up, equalization, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v8_50.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v8_50.h

Purpose: Provides a minimal QMP v8.50 PCS delta for changed status and power-down offsets.

Important APIs/types/functions: Exports `QPHY_V8_50_PCS_PCS_STATUS1`, `QPHY_V8_50_PCS_POWER_DOWN_CONTROL`, and the include guard. No functions, types, or runtime data are present.

Control flow: No code executes. Variant-specific QMP configuration tables use these names when v8.50 layout differs from base v8.

State and persistence: Stateless address constants. Hardware status is read and power-down control is written through these offsets by common QMP code.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v8.50 SoC descriptors.

Risks: The tiny surface makes accidental fallback to base v8 constants likely. Incorrect status offset can make the driver poll a stale or unrelated register, while a wrong power-down offset can prevent PHY enable.

Test signals: Compile of v8.50 tables, probe, power-on/off sequencing, PCS status polling, and link-up on matching silicon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v8_50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v2.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v2.h

Purpose: Defines the QSERDES v2 common/PLL register offsets used by QMP PHY PLL programming. It covers SSC, clock dividers, charge pump, PLL R/C controls, lock compare, divider fractional values, VCO tune, bias/clock enables, reset state machine, and mode-specific PLL fields.

Important APIs/types/functions: Exports `QSERDES_V2_COM_*` macros such as `SSC_*`, `CLK_EP_DIV*`, `CP_CTRL*`, `PLL_RCTRL*`, `PLL_CCTRL*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `HSCLK_SEL`, `VCO_TUNE*`, `PLL_IVCO`, and `CORECLK_DIV_MODE1`. No functions or types.

Control flow: None. Static QMP init tables write these offsets before the common driver enables PLLs and waits for lock.

State and persistence: No software state. PLL configuration persists in common QSERDES hardware while the PHY remains powered.

Dependencies and integration points: Included by `phy-qcom-qmp.h` for legacy QMP USB/PCIe/UFS users.

Risks: PLL offsets directly affect frequency synthesis. A wrong mode or fractional divider offset can create clock lock failures or unstable links.

Test signals: Build, PLL lock, generated reference rate correctness, link-up, SSC behavior, and resume after power collapse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v3.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v3.h

Purpose: Provides the QSERDES v3 common block register map for PLL, SSC, clocking, reset, calibration, and common-mode controls.

Important APIs/types/functions: Exports `QSERDES_V3_COM_*` macros for mode 0/1 PLL programming, `SSC_*`, `CP_CTRL*`, `PLL_RCTRL*`, `PLL_CCTRL*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `HSCLK_SEL`, `INTEGLOOP_*`, `VCO_TUNE*`, `BG_TIMER`, `CLK_ENABLE1`, `SYS_CLK_CTRL`, `PLL_IVCO`, `RESETSM_*`, and `CMN_VREG_SEL`. It defines no functions.

Control flow: None in the header. QMP init arrays use these offsets, followed by generic PLL enable and lock polling in protocol drivers.

State and persistence: Hardware state is created only by writes to the common QSERDES block and persists until reset/powerdown.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; feeds QMP USB/PCIe/UFS and related SoC tables.

Risks: v3 register names are similar to v2/v4 but offsets differ. Table copy errors can break PLL lock or program the wrong VCO mode.

Test signals: Compile, PLL lock, link-up at expected rate, SSC enablement, and power-management recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v4.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v4.h

Purpose: Defines QSERDES v4 common block offsets for PLL/SSC setup, common clocks, lock comparison, VCO calibration/tuning, reset sequencing, and additional control fields.

Important APIs/types/functions: Exports `QSERDES_V4_COM_*` macros, including mode-specific `SSC_STEP_SIZE*`, `CP_CTRL*`, `PLL_RCTRL*`, `PLL_CCTRL*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `INTEGLOOP_*`, `VCO_TUNE*`, `CLK_SELECT`, `PLL_ANALOG`, `SW_RESET`, `CORE_CLK_EN`, `CMN_CONFIG_*`, and `BIN_VCOCAL_HSCLK_SEL`. No executable code.

Control flow: None. The eDP and common QMP drivers include this map and write selected constants through initialization tables.

State and persistence: Constants only. Programmed PLL and common-clock state persists in QSERDES hardware until power/reset.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and `phy-qcom-edp.c`; used by QMP protocol init tables.

Risks: Common-block PLL configuration is foundational. Wrong lock compare or VCO tune offsets can produce intermittent lock or rate-specific failures.

Test signals: Build, PLL lock polling, eDP/USB/PCIe/UFS link-up where applicable, clock-rate validation, and resume retest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v5.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v5.h

Purpose: Supplies the QSERDES v5 common register map for newer QMP PHY PLL and clock programming, including additional mode, miscellaneous, and reserved fields.

Important APIs/types/functions: Exports `QSERDES_V5_COM_*` macros for SSC, clock dividers, charge pump, PLL R/C controls, core-clock dividers, lock compare, dec/div-frac programming, high-speed clock select, integration loop, VCO tune, bias/clock enables, reset state machine, common config, VCO DC level, and `RESERVED_1`. No functions or structs.

Control flow: None locally. Init arrays write these offsets before the common driver starts the PHY and checks lock/readiness.

State and persistence: The header is stateless; hardware PLL/common state persists while powered.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and `phy-qcom-sgmii-eth.c`; used by QMP USB/PCIe/UFS/SGMII-related tables.

Risks: v5 is reused across protocols. A value appropriate for one protocol/rate can be invalid for another even though the macro name compiles.

Test signals: Build, PLL lock, protocol link-up, SGMII/USB/PCIe/UFS rate-specific validation, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v6.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v6.h

Purpose: Defines QSERDES v6 common block offsets for PLL mode programming, SSC, clocking, lock compare, divider programming, VCO tune, reset, common config, adaptive PLL controls, and readiness status.

Important APIs/types/functions: Exports `QSERDES_V6_COM_*` macros, including `SSC_STEP_SIZE*`, `CP_CTRL_MODE*`, `PLL_RCTRL_MODE*`, `PLL_CCTRL_MODE*`, `CORECLK_DIV_MODE*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `HSCLK_SEL_1`, `BG_TIMER`, `PLL_IVCO`, `LOCK_CMP_EN`, `VCO_TUNE_MAP`, `CORE_CLK_EN`, `CMN_MODE`, `PLL_CCTRL_ADAPTIVE_MODE1`, and status fields. No functions.

Control flow: None in this file. QMP PCIe/eDP/common tables program the common block, then generic code waits for PLL/common readiness.

State and persistence: Immutable offset definitions. Writes persist in QSERDES common hardware until reset/powerdown.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and `phy-qcom-edp.c`; heavily used by `phy-qcom-qmp-pcie.c`.

Risks: Adaptive PLL and mode-specific controls are rate-sensitive. Offset mistakes may only appear at higher link generations.

Test signals: Build, PLL lock, C-ready status, PCIe/eDP link training, rate switching, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v7.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v7.h

Purpose: Provides the QSERDES v7 common/PLL offset map for high-speed QMP PHYs. It keeps mode-specific PLL fields while adding v7 common-mode, clock, and ready-status definitions.

Important APIs/types/functions: Exports `QSERDES_V7_COM_*` macros for SSC, clock dividers, charge pump, PLL R/C, core clock, lock compare, divider programming, high-speed clock selection, integration loop, VCO tune, clock enables, reset state machine, common config/mode, VCO DC control, and `C_READY_STATUS`. No runtime code.

Control flow: None. Static QMP init tables write selected offsets and the shared initialization flow later polls lock/ready status.

State and persistence: Header constants only; hardware PLL/common state persists until PHY reset or power collapse.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and used by v7 protocol descriptors.

Risks: v7 is close to v8 but not identical. Copying v8 PLL table entries without checking offsets can misconfigure clock synthesis.

Test signals: Build, PLL lock, C-ready polling, high-rate link-up, SSC behavior, and resume/reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v8.h

Purpose: Defines QSERDES v8 common/PLL offsets for newest QMP PCIe/common PHY initialization. It covers mode 0/1 PLL parameters, SSC, clocking, VCO tuning, common config, miscellaneous PLL ECO fields, and ready status.

Important APIs/types/functions: Exports `QSERDES_V8_COM_*` macros such as `SSC_STEP_SIZE*`, `CP_CTRL_MODE*`, `PLL_RCTRL_MODE*`, `PLL_CCTRL_MODE*`, `CORECLK_DIV_MODE*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `HSCLK_SEL_1`, `BG_TIMER`, `PLL_IVCO`, `LOCK_CMP_EN`, `VCO_TUNE_MAP`, `CMN_MISC_1`, `PLL_SPARE_FOR_ECO`, and `C_READY_STATUS`. No code.

Control flow: None locally. `phy-qcom-qmp-pcie.c` and common QMP tables write these offsets during PLL setup.

State and persistence: No software state; programmed PLL/common hardware settings persist while powered.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and directly by `phy-qcom-qmp-pcie.c`.

Risks: v8 introduces ECO/misc fields and high-generation PCIe rate programming. Wrong offsets can cause PLL lock failures or marginal Gen4/Gen5 behavior.

Test signals: Build, PLL lock and C-ready status, PCIe link generation negotiation, clock stability, and power-management retest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com.h

Purpose: Provides the original/base QSERDES common register map used by early QMP PHY drivers. It defines PLL, SSC, clock, lock, reset, VCO, SAR, debug, and reserved common-block offsets.

Important APIs/types/functions: Exports `QSERDES_COM_*` macros for `SSC_*`, `CLK_EP_DIV`, `CP_CTRL`, `PLL_RCTRL`, `PLL_CCTRL`, `LOCK_CMP*`, `DEC_START`, `DIV_FRAC_START*`, `HSCLK_SEL`, `VCO_TUNE*`, `SYS_CLK_CTRL`, `PLL_IVCO`, `RESETSM_*`, `LOCK_CMP_EN`, `SAR`, `DEBUG_BUS*`, `CMN_RSVD*`, and many related controls. No functions or structs.

Control flow: None. Included by the umbrella QMP header and used in static init tables executed by protocol drivers.

State and persistence: Stateless constants. Hardware common/PLL state is persistent only after register writes and until reset/powerdown.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used by legacy QMP USB/PCIe/UFS configurations.

Risks: This base namespace lacks a version suffix. New table authors must not assume it applies to newer QSERDES versions.

Test signals: Compile for legacy users, PLL lock, protocol link-up, SSC/clock behavior, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-dp-com-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-dp-com-v8.h

Purpose: Defines DisplayPort-specific QSERDES v8 common block offsets for eDP/DP PHY initialization. It contains PLL/SSC/clock fields specialized for the DP common block.

Important APIs/types/functions: Exports `DP_QSERDES_V8_COM_*` macros for mode-specific SSC step size, clock divider, charge pump, PLL R/C, lock compare, dec/div-frac starts, high-speed clock selection, integration loop, VCO tune, common clock enables, reset, config/mode, VCO DC control, additional misc, and `C_READY_STATUS`. No functions.

Control flow: No direct flow. `phy-qcom-edp.c` uses these constants in DP/eDP initialization arrays before common DP PHY enable and status checks.

State and persistence: No in-memory state. DP QSERDES common hardware retains programmed PLL values until reset or reinitialization.

Dependencies and integration points: Included by `phy-qcom-edp.c`; complements shared QMP/eDP PHY code and DP link-rate programming.

Risks: DP common offsets are namespaced separately from generic v8 COM. Mixing them can break DisplayPort PLL programming even if macro shapes look similar.

Test signals: Build, eDP/DP PHY probe, PLL C-ready, link training at supported DP rates, display enable/disable, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-dp-com-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-lalb-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-lalb-v8.h

Purpose: Provides a large QSERDES v8 LALB register map for a combined lane analog/lane-B style block. It spans BIST/PRBS, reset, TX0/TX1 drive and emphasis, restrim, interface select, per-rate RX mode settings, DCC, CDR/VCO/KVCO/KP calibration, IVCM/IDAC/signal detect, receiver/equalizer, CTLE/VGA/VTH/DFE, IQ tune, BLW/IVTH, extensive status/debug, and digital backup registers.

Important APIs/types/functions: Exports about 630 `QSERDES_V8_LALB_*` macros. The map includes paired TX0/TX1 controls, rate0-rate4 RX/CDR fields, calibration controls, readback/status registers, and backup/RO buses. No functions or types are defined.

Control flow: No code executes. The umbrella QMP header exposes the constants to v8 tables; common QMP write helpers perform actual register programming.

State and persistence: The header is immutable. Runtime state is entirely in lane hardware and calibration/readback registers after table writes or hardware calibration.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; intended for newest v8 PHY descriptors that need LALB offsets beyond generic TX/RX maps.

Risks: This is a high-risk map because it is dense, rate-indexed, and contains many similarly named control/status registers. Offset drift can corrupt calibration or debug readbacks without compiler errors.

Test signals: Build of v8 LALB users, lane bring-up, BIST/PRBS when available, high-rate link training, calibration status reads, equalizer margin, and suspend/resume reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-lalb-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-ln-shrd-v5.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-ln-shrd-v5.h

Purpose: Defines the minimal QSERDES v5 lane-shared RX PI controls needed by some QMP configurations.

Important APIs/types/functions: Exports `QSERDES_v5_LN_SHRD_UCDR_PI_CTRL1` and `QSERDES_v5_LN_SHRD_UCDR_PI_CTRL2`. There are no functions, structures, or data objects.

Control flow: None. Init tables write these lane-shared offsets through normal QMP register write helpers when a PHY layout exposes UCDR PI controls in a shared lane block.

State and persistence: Stateless address definitions. Hardware CDR/PI settings persist until reset or reconfiguration.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used with QMP v5/v6 generation lane-shared descriptors.

Risks: The macro prefix uses lowercase `v5`, unlike most QSERDES headers. Renaming for style would break consumers unless all tables are updated.

Test signals: Build, lane initialization on matching SoCs, clock-data recovery stability, and link-up across supported rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-ln-shrd-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-ln-shrd-v6.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-ln-shrd-v6.h

Purpose: Supplies QSERDES v6 lane-shared offsets for UCDR, RX mode, DFE/CTLE, PI, and summer calibration controls.

Important APIs/types/functions: Exports `QSERDES_V6_LN_SHRD_*` macros, including `UCDR_PI_CTRL1/2`, `RXCLK_DIV2_CTRL`, `RX_Q_EN_RATES`, `DFE_DAC_ENABLE1/2`, `RX_MODE_RATE*`, `RX_Q_PI_INTRINSIC_BIAS_RATE*`, `RX_MARG_VERTICAL_CODE`, `PI_CTRL*`, `QPI_CTRL*`, and `RX_SUMMER_CAL_SPD_MODE`. No code exists.

Control flow: No local flow. QMP init arrays write these shared-lane registers while per-lane TX/RX maps handle lane-specific programming.

State and persistence: Constants only; programmed lane-shared CDR/equalizer state persists in hardware until reset/rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; complements v6 TX/RX headers.

Risks: Shared-lane fields can affect multiple lanes. Wrong values or offsets may break multi-lane behavior even when each per-lane table is correct.

Test signals: Build, multi-lane link training, CDR stability, equalizer convergence, lane margin, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-ln-shrd-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-pll.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-pll.h

Purpose: Defines a QSERDES PLL-specific register map used where PLL offsets are separated from the broader COM namespace. It covers SSC, clock dividers, charge pump, PLL controls, lock compare, divider fractional starts, VCO tune, bias/clock, reset, and core clock fields.

Important APIs/types/functions: Exports `QSERDES_PLL_*` macros such as `SSC_STEP_SIZE*`, `CLK_EP_DIV`, `CP_CTRL`, `PLL_RCTRL`, `PLL_CCTRL`, `LOCK_CMP*`, `DEC_START`, `DIV_FRAC_START*`, `HSCLK_SEL`, `VCO_TUNE*`, `PLL_IVCO`, `RESETSM_CNTRL*`, `LOCK_CMP_EN`, and `CORECLK_DIV_MODE1`. No functions or types.

Control flow: None. Included by the QMP umbrella header for tables that address PLL fields through a PLL block rather than COM.

State and persistence: Stateless constants; runtime PLL state is hardware-resident.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used by QMP configuration tables and common PHY register helpers.

Risks: It overlaps semantically with COM headers. Selecting PLL-vs-COM namespaces incorrectly can write valid-looking values to invalid offsets.

Test signals: Build, PLL lock, rate generation, link-up, and suspend/resume re-lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-pcie-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-pcie-v8.h

Purpose: Defines PCIe-specific QSERDES v8 TX/RX offsets. It targets PCIe lane controls for resistance codes, lane modes, driver emphasis, band selection, rate-specific adaptation, UCDR gains, signal detect, RX band/termination, RX mode tables, EOM, auxiliary data, threshold calibration, and GM calibration.

Important APIs/types/functions: Exports `QSERDES_V8_PCIE_TX_*` and `QSERDES_V8_PCIE_RX_*` macros. No functions or types are defined.

Control flow: None locally. `phy-qcom-qmp-pcie.c` uses these constants in PCIe Gen-rate initialization arrays that the common QMP code writes during PHY bring-up.

State and persistence: Header constants only. Programmed TX/RX lane state persists in QSERDES hardware until reset, powerdown, or rate-specific reprogramming.

Dependencies and integration points: Directly included by `phy-qcom-qmp-pcie.c`; paired with `phy-qcom-qmp-qserdes-com-v8.h` and v8 PCIe PCS headers.

Risks: PCIe Gen4/Gen5 tuning is sensitive. Wrong rate-specific RX mode or UCDR offset may only fail at higher negotiated speeds or under marginal signal conditions.

Test signals: Build, PCIe link training across supported generations, receiver detection, equalization, EOM/margin checks, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-pcie-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-ufs-v6.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-ufs-v6.h

Purpose: Provides UFS-specific QSERDES v6 TX/RX offsets for MPHY/UFS lane initialization. It includes TX driver/emphasis, lane mode, interface select, UCDR/PI, RX mode, signal detect, calibration, DFE, GM, QPI, and DLL tuning fields.

Important APIs/types/functions: Exports `QSERDES_UFS_V6_TX_*` and `QSERDES_UFS_V6_RX_*` macros. Notable groups are `TX_LANE_MODE_*`, `TX_INTERFACE_SELECT`, `RX_UCDR_*`, `RX_MODE_RATE_*`, `RX_SIGDET_*`, `RX_DFE_*`, `RX_Q_PI_INTRINSIC_BIAS_RATE32`, and `RX_DLL0_FTUNE_CTRL`. No functions.

Control flow: No local flow. `phy-qcom-qmp-ufs.c` uses these constants in UFS PHY init sequences before link startup.

State and persistence: Stateless offsets; hardware settings persist until UFS PHY reset/power mode change.

Dependencies and integration points: Included by `phy-qcom-qmp-ufs.c`; paired with UFS PCS headers and common QMP helpers.

Risks: UFS power modes and gears depend on precise RX/TX tuning. Wrong offsets can cause boot storage link failures.

Test signals: Build, UFS host probe, gear negotiation, HS mode entry, link startup, hibern8/resume, and storage I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-ufs-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-ufs-v7.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-ufs-v7.h

Purpose: Defines UFS-specific QSERDES v7 TX/RX offsets for newer UFS PHY lanes. The map covers TX drive/emphasis, band and interface selection, lane modes, UCDR gains, RX calibration, signal detection, mode-rate tables, DFE, QPI bias, PI controls, backup, and signal-detect calibration.

Important APIs/types/functions: Exports `QSERDES_UFS_V7_TX_*` and `QSERDES_UFS_V7_RX_*` macros. It has no functions or data types.

Control flow: No code here. `phy-qcom-qmp-ufs.c` references the macros in static register tables applied during UFS PHY initialization and power mode setup.

State and persistence: Only immutable offsets. UFS lane hardware retains written values until reset or mode switch reprogramming.

Dependencies and integration points: Included by the UFS QMP driver and paired with UFS PCS v6 headers where SoC tables require it.

Risks: UFS v7 has separate names from generic v7 TX/RX. Mixing generic and UFS-specific maps can cause subtle high-speed mode failures.

Test signals: Build, UFS link startup, HS gear changes, hibern8 enter/exit, storage stress I/O, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-ufs-v7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v2.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v2.h

Purpose: Provides the QSERDES v2 TX/RX lane offset subset used by versioned QMP PHY tables. It includes TX clock buffer, emphasis/drive, reset, lane mode, receiver detect, and RX UCDR/equalization/signal-detect/mode fields.

Important APIs/types/functions: Exports `QSERDES_V2_TX_*` and `QSERDES_V2_RX_*` macros, including `TX_EMP_POST1_LVL`, `TX_DRV_LVL`, `RESET_TSYNC_EN`, `LANE_MODE`, `RCV_DETECT_LVL*`, `RX_UCDR_*`, `RX_EQU_ADAPTOR_CNTRL*`, `RX_SIGDET_*`, and `RX_MODE_00/01`. No functions.

Control flow: No direct control flow. Static init tables write TX/RX registers through common QMP helpers after common PLL setup.

State and persistence: Stateless constants. Lane state persists in QSERDES hardware until reset/reconfiguration.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and used by legacy QMP protocol tables.

Risks: TX and RX offsets share one header but target different base regions. Consumers must use the right base address when applying each table.

Test signals: Compile, lane bring-up, signal detect, equalization, link-up, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v3.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v3.h

Purpose: Defines QSERDES v3 TX/RX lane offsets. It is a compact map for TX emphasis/drive/lane controls and RX UCDR, signal-detect, equalizer, and mode-rate programming.

Important APIs/types/functions: Exports `QSERDES_V3_TX_*` and `QSERDES_V3_RX_*` macros, including TX drive/emphasis and lane mode plus RX `UCDR_*`, `RX_EQU_ADAPTOR_CNTRL*`, `SIGDET_*`, and mode registers. No functions or structures.

Control flow: No local flow. QMP init tables consume these constants and shared QMP code performs writes during lane setup.

State and persistence: No software state; hardware lane settings persist until reset or later table writes.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used by v3-generation USB/PCIe/UFS descriptors.

Risks: The v3 map resembles v2 but should not be treated as identical. Incorrect namespace selection can break signal detect or equalization while still compiling cleanly.

Test signals: Build, probe, PLL plus lane startup, signal detect, link training, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v4.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v4.h

Purpose: Supplies a full QSERDES v4 TX/RX lane register map. TX coverage includes BIST, clock buffer, common controls, drive/emphasis, reset, band/interface, resistance, lane mode, PRBS, receiver detect, PWM, VMODE, analog observation, and status. RX coverage includes UCDR gains, auxiliary/JTAG, IDAC, equalizer/adaptor, signal detect, CDR, interface, jitter/SSC, PWM, PI, data/status readbacks, and error counters.

Important APIs/types/functions: Exports roughly 220 `QSERDES_V4_TX_*` and `QSERDES_V4_RX_*` macros. No functions or C types are defined.

Control flow: None. Version-specific QMP tables program selected TX/RX offsets through common register-write helpers.

State and persistence: Header constants only; programmed lane tuning, calibration, and diagnostic state live in hardware.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v4 COM and PCS maps.

Risks: The file mixes writable controls and readback/status offsets. Accidentally writing a status offset or reading a control as status can hide bugs until hardware testing.

Test signals: Build, lane startup, BIST/PRBS if used, equalization, signal detect, error counters, link-up, and power-cycle recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v4_20.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v4_20.h

Purpose: Defines QSERDES v4.20 TX/RX lane delta offsets, mainly TX drive/lane controls and RX UCDR, calibration, adaptation, signal detect, mode, DFE, PI, and margining controls.

Important APIs/types/functions: Exports `QSERDES_V4_20_TX_*` and `QSERDES_V4_20_RX_*` macros, including `TX_EMP_POST1_LVL`, `TX_DRV_LVL`, `LANE_MODE_*`, `RX_UCDR_*`, `RX_IVCM_*`, `DFE_*`, `RX_EQ_OFFSET_ADAPTOR_CNTRL1`, `SIGDET_*`, `RX_MODE_00_*`, `Q_PI_INTRINSIC_BIAS_RATE32`, and margin coarse controls. No functions.

Control flow: None. Used by v4.20-specific init tables through the standard QMP table write path.

State and persistence: Stateless offset map; hardware lane state persists after writes.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; complements v4.20 PCS deltas and v4 COM maps.

Risks: Delta headers omit many base registers. Consumers must combine base and variant constants carefully.

Test signals: Build, platform probe, link training, RX margining, DFE/equalization behavior, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v4_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5.h

Purpose: Provides the QSERDES v5 TX/RX lane register map. It covers TX BIST, drive/emphasis, reset, band/interface, resistance, lane modes, PRBS, receiver detect, status/debug, and PWM; RX UCDR, auxiliary/JTAG, IDAC, IVCM, DFE, equalization, VGA/VTH/GM calibration, signal detect, CDR/interface, jitter/SSC, mode tables, margining, QPI/PI, data readbacks, and backup/status registers.

Important APIs/types/functions: Exports more than 200 `QSERDES_V5_TX_*` and `QSERDES_V5_RX_*` macros. There are no C functions or structures.

Control flow: None. QMP protocol tables reference the offsets and shared helpers write them during lane initialization.

State and persistence: Only numeric constants. Lane tuning and calibration state is in hardware until reset/reprogramming.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and `phy-qcom-sgmii-eth.c`; paired with v5 COM/PCS maps.

Risks: Broad protocol reuse means a macro can be valid but inappropriate for a given PHY mode. Care is needed around margining and backup/status fields.

Test signals: Build, lane bring-up, link training, SGMII/USB/PCIe/UFS protocol tests where applicable, margin/error status, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5_20.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5_20.h

Purpose: Defines QSERDES v5.20 TX/RX lane offsets for a trimmed newer layout. It includes TX drive/lane controls and RX CDR, IVCM, DFE, adaptation, VGA/GM, signal detect, post-calibration, QPI bias, mode-rate, and backup controls.

Important APIs/types/functions: Exports `QSERDES_V5_20_TX_*` and `QSERDES_V5_20_RX_*` macros. Key groups include `TX_EMP_POST1_LVL`, `TX_DRV_LVL`, `LANE_MODE_*`, `RX_UCDR_*`, `RX_IVCM_*`, `DFE_*`, `RX_TX_ADPT_CTRL`, `VGA_CAL_*`, `SIGDET_ENABLES`, `RX_MODE_RATE*`, `Q_PI_INTRINSIC_BIAS_RATE32`, and `RX_BKUP_CTRL1`. No functions.

Control flow: None. Consumers use the constants in static init tables applied by QMP helpers.

State and persistence: Stateless address map; hardware state persists after writes.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used with v5.20 PCS and v5 COM-family tables.

Risks: Versioned RX mode offsets are dense and rate-specific; a single wrong offset can break one speed while lower speeds still pass.

Test signals: Build, link training across rates, equalization, CDR lock, signal-detect, backup behavior, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5_5nm.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5_5nm.h

Purpose: Supplies a large QSERDES v5 5nm TX/RX lane map. TX covers BIST, drive/emphasis, reset, lane mode, receiver detect, PRBS, VMODE, PI/QEC, band/interface, debug and backup. RX covers rate-indexed UCDR fastlock/gain, IDAC/IVCM, DFE, adaptation, VGA/VTH/GM, equalizer, signal detect, CDR, jitter/SSC, RX modes, DCC, margining, QPI/PI, readbacks, and calibration status.

Important APIs/types/functions: Exports about 315 `QSERDES_V5_5NM_TX_*` and `QSERDES_V5_5NM_RX_*` macros. No functions or types.

Control flow: None locally. QMP tables select these offsets for 5nm PHY layouts and common helpers apply the writes.

State and persistence: The header is immutable. Runtime lane/calibration/margin state lives in hardware until reset or retuning.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v5/v5.20 common and PCS descriptors as SoC tables require.

Risks: This map has many rate-indexed and status registers. Copy/paste or base-version mixups can produce failures isolated to specific gears/generations or diagnostics.

Test signals: Build, high-speed link training at each supported rate, RX margining, DCC/calibration status, error counters, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5_5nm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6.h

Purpose: Defines the QSERDES v6 TX/RX lane offset set, named in the guard as USB v6 but used as a generic v6 lane map. It covers TX clock/drive/lane mode/band/interface and RX UCDR, calibration, DFE, adaptation, VGA/GM, signal detect, RX modes, DFE timer, DCC, VTH, and signal-detect calibration.

Important APIs/types/functions: Exports `QSERDES_V6_TX_*` and `QSERDES_V6_RX_*` macros such as `TX_CLKBUF_ENABLE`, `TX_EMP_POST1_LVL`, `TX_DRV_LVL`, `LANE_MODE_*`, `RX_UCDR_*`, `RX_IVCM_*`, `RX_DFE_*`, `RX_MODE_00_*`, and `RX_SIGDET_CAL_TRIM`. No functions.

Control flow: None. Static QMP tables apply these offsets through common register writers.

State and persistence: Stateless constants; hardware lane settings persist until reset/rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v6 COM/PCS maps.

Risks: Include guard naming says `TXRX_USB_V6`, which can obscure generic use. Namespace clarity matters when adding protocol-specific v6 variants.

Test signals: Build, lane startup, CDR lock, signal detect, equalization, high-speed link-up, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6_20.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6_20.h

Purpose: Provides QSERDES v6.20 PCIe TX/RX lane offsets. It covers TX drive/emphasis, lane modes, and RX UCDR rate gains, IVCM, DFE, adaptation, VGA/GM, signal detect, phpre, post-calibration, QPI bias, rate2/rate3 mode tables, and backup control.

Important APIs/types/functions: Exports `QSERDES_V6_20_TX_*` and `QSERDES_V6_20_RX_*` macros. No functions or types are defined.

Control flow: None. PCIe-oriented QMP init arrays write these offsets as part of lane setup after common PLL programming.

State and persistence: Constants only; hardware lane configuration persists until reset or rate reprogramming.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used with v6.20 PCS/PCIe tables.

Risks: The include guard identifies it as PCIe v6.20, so using it for non-PCIe modes should be deliberate and backed by hardware documentation.

Test signals: Build, PCIe link training by generation, CDR/equalization stability, receiver detection, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6_n4.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6_n4.h

Purpose: Defines QSERDES v6 N4 TX/RX lane offsets for newer N4 PHY layouts. It includes TX drive/emphasis, resistance, bias/high-Z/polarity, lane mode, band/interface, VMODE, and RX UCDR, IVCM, DFE, VGA/GM, signal detect, QPI, DFE DAC, mode tables, summer calibration, and backup control.

Important APIs/types/functions: Exports `QSERDES_V6_N4_TX_*` and `QSERDES_V6_N4_RX_*` macros. No functions or structures.

Control flow: No local flow. QMP init tables write these offsets using the common PHY register abstraction.

State and persistence: The header is stateless; writes affect persistent lane hardware state until reset/rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v6 N4 PCS maps and v6 common block definitions.

Risks: N4-specific RX mode offsets are not interchangeable with base v6/v6.20. Mistakes may only show up under one lane rate or signal condition.

Test signals: Build, N4 platform probe, link training at all supported rates, CDR/signal detect, equalization, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6_n4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v7.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v7.h

Purpose: Provides QSERDES v7 TX/RX lane offsets. It covers TX clock/reset/pre-stall, band/interface, resistance, lane modes, receiver detect, driver emphasis, VMODE and PI QEC; RX UCDR, auxiliary data, adaptation thresholds, VGA/GM, equalizer, IDAC timing, signal detect, RX mode tables, DFE, DCC, VTH, and signal-detect calibration.

Important APIs/types/functions: Exports `QSERDES_V7_TX_*` and `QSERDES_V7_RX_*` macros. No functions or C types.

Control flow: None. QMP tables program selected v7 lane offsets after common PLL setup.

State and persistence: No software state; lane configuration and calibration state persist in hardware until reset or retuning.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v7 COM/PCS maps.

Risks: v7 and v8 maps are similar but not identical. Using v8 macros or assumptions in v7 tables can corrupt lane tuning.

Test signals: Build, lane startup, signal-detect, CDR lock, equalization, rate-specific link training, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v8.h

Purpose: Defines the base QSERDES v8 TX/RX lane offsets for non-PCIe-specialized v8 tables. It includes TX drive/emphasis, resistance, bias, high-Z, polarity, lane modes, receiver-detect level, and PI QEC; RX UCDR, auxiliary data, VGA/GM/equalizer, signal detect, RX mode tables, DFE, DCC, VTH, and signal-detect calibration.

Important APIs/types/functions: Exports `QSERDES_V8_TX_*` and `QSERDES_V8_RX_*` macros. No functions, structs, or global data.

Control flow: None locally. The umbrella QMP header exposes these constants to SoC tables, and common QMP code writes them during lane initialization.

State and persistence: Stateless offsets; hardware lane state persists until reset/rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v8 COM, PCS, USB, PCIe, and LALB maps depending on platform.

Risks: PCIe v8 has its own TXRX header with extra rate fields. Using this base map for PCIe-specific tables can omit or misaddress required tuning.

Test signals: Build, lane bring-up, CDR/signal detect, equalization, high-speed link-up, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx.h

Purpose: Provides the original/base QSERDES TX and RX lane register maps for QMP v2-era PHYs. TX covers BIST, clock/common controls, drive/emphasis, reset, band/interface, resistance, debug, lane mode, receiver detect, PRBS, PWM, VMODE, and status. RX covers UCDR, auxiliary/JTAG, termination, IDAC, equalizer, signal detect, CDR, interface, jitter/SSC, PWM, PI, data/readback, calibration status, and error counters.

Important APIs/types/functions: Exports `QSERDES_TX_*` and `QSERDES_RX_*` macros, roughly 193 offsets total. It defines no functions or C types.

Control flow: No direct flow. The umbrella QMP header includes it and static init tables use these constants with TX/RX base addresses.

State and persistence: Stateless constants. Runtime lane state exists only in hardware after writes.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used by legacy QMP protocol drivers and tables.

Risks: This unversioned namespace is easy to misuse for later QSERDES revisions. TX and RX sections also require correct base selection by the caller.

Test signals: Compile, lane initialization, signal detect, equalizer convergence, BIST/error counters where used, link-up, and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx.h -->
