# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/reg.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004932`: lines 1-7053, `Docs/researches/chunks/subset-b-004932_research.md`
- `subset-b-004933`: lines 7054-10717, `Docs/researches/chunks/subset-b-004933_research.md`

## Chunk Research

### subset-b-004932: lines 1-7053

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/reg.h lines 1-7053

## Scope And Purpose

This chunk covers the first 7,053 lines of `drivers/net/wireless/realtek/rtw89/reg.h`, the central register map header for Realtek `rtw89` wireless devices. It contains C preprocessor definitions only: MMIO register addresses, bit positions, bit masks, literal field values, aggregate interrupt-mask presets, and address aliases for AX-generation chips and the beginning of BE-generation chips.

The header is the shared hardware contract consumed by the PCI/USB/SDIO host-interface code, MAC initialization, firmware download, power management, security engine setup, TX/RX packet-buffer management, debug dumps, Bluetooth/LTE coexistence, and chip-specific bring-up files such as `rtw8851b.c`, `rtw8852b.c`, `rtw8852c.c`, `rtw8922a.c`, and `rtw8922d.c`. No functions or types are declared in this chunk, but the macros define the symbolic API used by the rest of the driver to perform register reads, writes, polling, and bitfield updates.

This chunk ends at the early BE CMAC/PTCL definitions around `R_BE_AGG_BK_0`; later BE RX/RMAC and remaining register families continue in subsequent chunks of the same source file.

## Register Naming And Macro Conventions

The file follows a compact hardware naming scheme:

- `R_AX_*` and `R_BE_*` are register offsets for Wi-Fi 6/AX-era and Wi-Fi 7/BE-era hardware blocks.
- `B_AX_*` and `B_BE_*` are single-bit flags or multi-bit `GENMASK()` field masks for those registers.
- `_C1` suffixes identify the second CMAC/band address window. AX often maps CMAC0 at `0xC000` and CMAC1 at `0xE000`; BE in this chunk maps CMAC0 at `0x10000` and CMAC1 at `0x14000`.
- `_V1`, `_V01`, and similar suffixes capture chip-revision layout changes where a register address is stable but field positions, interrupt sets, or enable masks differ.
- Aggregate masks such as `B_AX_HOST_DISP_IMR_SET`, `B_AX_WDE_IMR_CLR_V1`, `B_BE_DISP_HOST_IMR_SET_V1`, and `B_BE_CMAC_FUNC_EN_SET` are policy presets used by initialization and SER/error-handling paths.
- Literal constants such as `AX_WMAC_RFMOD_80M`, `BE_WMAC_RFMOD_320M`, `MAC_AX_HCI_SEL_PCIE_USB`, `SW_LPS_OPTION`, `TRXCFG_MPDU_PROC_ACT_FRWD`, and `CSI_RRSC_BMAP` encode values written into masked fields.

The macros depend on the Linux kernel `BIT()`, `GENMASK()`, and occasionally `u32_encode_bits()` helpers through transitive kernel headers. Consumers typically call local register helpers such as `rtw89_read32()`, `rtw89_write32()`, `rtw89_write32_set()`, `rtw89_write32_clr()`, `rtw89_write32_mask()`, and `rtw89_mac_reg_by_idx()`.

## AX System, Power, EFUSE, GPIO, And Firmware Control

The opening AX section defines low-address system registers used before the MAC is fully running:

- Power/isolation and reset: `R_AX_SYS_ISO_CTRL`, `R_AX_SYS_FUNC_EN`, `R_AX_SYS_PW_CTRL`, `R_AX_SYS_CLK_CTRL`, `R_AX_SYS_SWR_CTRL1`, `R_AX_AFE_LDO_CTRL`, and related bits such as `B_AX_EN_WLON`, `B_AX_APFN_ONMAC`, `B_AX_APFM_OFFMAC`, `B_AX_APFM_SWLPS`, `B_AX_RDY_SYSPWR`, `B_AX_SOP_EDSWR`, and `B_AX_XTAL_OFF_A_DIE`.
- EFUSE/OTP access: `R_AX_EFUSE_CTRL`, `R_AX_EFUSE_CTRL_1`, and `R_AX_EFUSE_CTRL_1_V1` define mode, ready, address, data, burst/test, and error fields.
- GPIO and pinmux: `R_AX_GPIO_MUXCFG`, `R_AX_GPIO_EXT_CTRL`, `R_AX_GPIO*_FUNC_SEL`, LED/EESK/EECS pull-down controls, and Bluetooth-mode pin options.
- HCI/platform state: `R_AX_SYS_SDIO_CTRL`, `R_AX_HCI_OPT_CTRL`, `R_AX_HCI_BG_CTRL`, `R_AX_HCI_LDO_CTRL`, `R_AX_PLATFORM_ENABLE`, `R_AX_SYS_STATUS1`, and HCI-selection constants.
- Firmware and mailbox registers: `R_AX_WCPU_FW_CTRL`, `R_AX_H2CREG_DATA*`, `R_AX_C2HREG_DATA*`, `R_AX_H2CREG_CTRL`, `R_AX_C2HREG_CTRL`, `R_AX_RPWM`, `R_AX_CPWM`, halt H2C/C2H registers, and boot/debug status fields.

These symbols are used by MAC power sequencing and firmware download paths. Call sites in `mac.c` and chip files poll `R_AX_SYS_PW_CTRL` for `B_AX_RDY_SYSPWR`, set `B_AX_EN_WLON` and `B_AX_APFN_ONMAC` during power-on, clear firmware download bits in `R_AX_WCPU_FW_CTRL`, and use H2C/C2H register windows for mailbox-style firmware communication.

## AX Host Interface, DMA, LTR, And Page Accounting

AX HCI/DMA definitions cover PCI/USB/SDIO transport setup and DMA state:

- HAXI setup and stop/busy state: `R_AX_HAXI_INIT_CFG1`, `R_AX_HAXI_DMA_STOP1`, `R_AX_HAXI_DMA_BUSY1`, `R_AX_HAXI_DMA_STOP2`, `R_AX_HAXI_DMA_BUSY2`, and `R_AX_HAXI_DMA_BUSY3`.
- USB variants: `R_AX_USB_ENDPOINT_*`, `R_AX_USB_HOST_REQUEST_2`, `R_AX_USB3_MAC_NPI_CONFIG_INTF_0`, `R_AX_USB_WLAN0_1`, plus `_V1` forms at the `0x50xx` window.
- PCIe/LTR control: `R_AX_LTR_DEC_CTRL`, `R_AX_LTR_LATENCY_IDX*`, `R_AX_LTR_CTRL_0`, `R_AX_LTR_CTRL_1`, `R_AX_LTR_IDLE_LATENCY`, and `R_AX_LTR_ACTIVE_LATENCY`.
- HCI flow control/page accounting: `R_AX_HCI_FC_CTRL`, channel page controls and page-info registers for access categories, channels 8-12, public page pools, and WP pools.
- HCI DMA enable: `R_AX_HCI_FUNC_EN` with `B_AX_HCI_TXDMA_EN` and `B_AX_HCI_RXDMA_EN`.

The page-control macros integrate with DLE quota setup in `mac.c`, where the driver writes WDE and PLE packet-buffer sizes and reads page usage/available counters for diagnostics. The LTR constants are consumed by PCI power-management logic to program latency tolerance behavior.

## AX DMAC, Dispatcher, WDE/PLE, CPUIO, And Error Masks

The AX DMAC block begins at `R_AX_DMAC_FUNC_EN` and `R_AX_DMAC_CLK_EN`, which gate major data-path modules including MAC, DMAC, MPDU processor, WDE/PLE, TX packet control, STA scheduler, packet-in, dispatcher, BB reports, and security. Chip-specific power-on routines set these bits after system power is ready.

Large portions of this chunk define error interrupt masks and status bits for:

- Top-level DMAC: `R_AX_DMAC_ERR_IMR` and `R_AX_DMAC_ERR_ISR`.
- Host/CPU/other dispatcher paths: `R_AX_HOST_DISPATCHER_ERR_IMR`, `R_AX_CPU_DISPATCHER_ERR_IMR`, `R_AX_OTHER_DISPATCHER_ERR_IMR`, and dispatcher debug select registers.
- WDE and PLE packet-buffer engines: `R_AX_WDE_PKTBUF_CFG`, `R_AX_WDE_ERR_IMR`, `R_AX_WDE_ERR_ISR`, WDE quotas, WDE initialization status, DFI debug, `R_AX_PLE_PKTBUF_CFG`, PLE debug/error/status registers, and PLE quotas 0-11.
- WDRLS, BBRPT, CPUIO, packet-in, MPDU TX/RX, TX packet control preload/error registers, and queue operation registers.

The aggregate `*_IMR_CLR` and `*_IMR_SET` masks are especially important because they encode which hardware anomalies should be cleared and which should be unmasked. Versioned variants show that interrupt layouts changed across chips; using the wrong aggregate mask can either hide a real hardware fault or enable a bit that has another meaning on a different revision.

## AX MPDU, Security, Scheduler, TX/RX, And CMAC

The chunk defines AX MPDU processing and security hardware:

- MPDU forwarding and processing: `R_AX_MPDU_PROC`, `R_AX_ACTION_FWD0`, `R_AX_ACTION_FWD1`, `R_AX_TF_FWD`, `R_AX_HW_RPT_FWD`, `R_AX_CUT_AMSDU_CTRL`, and WOW control.
- Security engine: `R_AX_SEC_ENG_CTRL`, `R_AX_SEC_MPDU_PROC`, CAM access/data registers, debug counters, hang flags, encryption/decryption enable bits, and debug controls.
- STA scheduler: scheduler pause registers, scheduler error interrupt/status, search/report hang bits, and MACID pause maps.
- CMAC enable and clocks: `R_AX_CMAC_FUNC_EN`, `R_AX_CMAC_FUNC_EN_C1`, `R_AX_CK_EN`, `R_AX_CK_EN_C1`, plus TX/RX/PHY interface/submodule enables.

Security and CMAC definitions are used directly in `mac.c` and debugfs. The driver enables `B_AX_SEC_TX_ENC` and `B_AX_SEC_RX_DEC` for hardware crypto, toggles BMC/UC/MC/BC management/data handling, and reads the same registers when diagnosing SER or security hang conditions. CMAC registers are addressed per band through either explicit `_C1` constants or `rtw89_mac_reg_by_idx()`.

## AX Scheduler, Beacon Ports, TRX Protocol, RX Filters, Power, And Coexistence

The AX CMAC/PTCL portion maps per-band MAC behavior:

- Scheduler/CCA/EDCA: pre-backoff, SIFS timeout, CCA enable/control, contention TX enable, MU-EDCA parameters, scheduler debug, and scheduler error bits.
- Per-port beacon and TSF state: `R_AX_PORT_CFG_P0` through `P4`, TBTT prohibit/setup, beacon area, early interrupt timing, beacon spacing, forced beacon TX, beacon error counters/flags, DTIM, TBTT shift, TSF low/high, drop-all, MBSSID controls, and P0MB/HGQ windows.
- Protocol/TMAC/RMAC: `R_AX_PTCL_COMMON_SETTING_0`, AMPDU limits, TX rate checks, protocol report handling, BSS color, PTCL interrupt/status/debug, DLE/RX/TX error masks, TCR, TX FIFO debug, response control, NAV control, trigger-test user info, TRXPTCL error indication, beamformer/beamformee response controls, and CSI report settings.
- RX filtering and address matching: `R_AX_RCR`, `R_AX_RX_FLTR_OPT`, `R_AX_CTRL_FLTR`, `R_AX_MGNT_FLTR`, `R_AX_DATA_FLTR`, address CAM, BA CAM, PPDU status, spatial-reuse RX control, BSSID source control, CSI reporting, RMAC error masks, and PLCP/debug monitor.
- TX power tables and path composition: power-by-rate, power-limit, RU-limit, MACID-limit, path combination registers, TSSI, band-edge config, and TX power interrupt/status.
- Coexistence: `R_AX_BTC_CFG`, RTK/CSR mode, BT counters, grant software control/status, TDMA mode, BT coexistence mask/break tables, LTE control and LTE software config registers.

These definitions connect to high-level driver flows: beacon/TSF setup for virtual interfaces, RX filter programming for normal/promiscuous modes, rate/power programming from regulatory and PHY data, beamforming and CSI control, and coexistence policy from `coex.c`. The `DEFAULT_AX_RX_FLTR` macro is notable because it embeds a default receive policy using several bit definitions and `u32_encode_bits()`.

## BE System And Power Definitions In This Chunk

Starting around line 3,798, the chunk switches to BE-generation register definitions. The low-address BE system block mirrors AX concepts but expands them for Wi-Fi 7 devices:

- Power/isolation: `R_BE_SYS_ISO_CTRL`, `R_BE_SYS_PW_CTRL`, `R_BE_SYS_CLK_CTRL`, `R_BE_SYS_WL_EFUSE_CTRL`, `R_BE_SYS_PAGE_CLK_GATED`, `R_BE_AFE_LDO_CTRL`, `R_BE_AFE_CTRL1`, `R_BE_FEN_RST_ENABLE`, `R_BE_PLATFORM_ENABLE`, `R_BE_WLLPS_CTRL`, and `R_BE_WLRESUME_CTRL`.
- EFUSE/GPIO/HCI: `R_BE_EFUSE_CTRL`, `R_BE_EFUSE_CTRL_1_V1`, `R_BE_EFUSE_CTRL_2_V1`, `R_BE_GPIO_MUXCFG`, `R_BE_GPIO_EXT_CTRL`, `R_BE_WL_BT_PWR_CTRL`, `R_BE_SYS_SDIO_CTRL`, `R_BE_HCI_OPT_CTRL`, and `R_BE_SYS_CHIPINFO`.
- Firmware and interrupt/mailbox state: BE scoreboard registers, halt H2C/C2H, FWS/HIMR/HISR interrupt status/masks, `R_BE_WCPU_FW_CTRL`, boot reason, LDM/UDM counters, WCPU/DCPU platform controls, H2C/C2H register data/control windows, and `R_BE_HCI_FUNC_EN`.
- Watchdogs and PCIe power: multiple watchdog registers/timers (`R_BE_WLAN_WDT`, `R_BE_AXIDMA_WDT`, `R_BE_AON_WDT`, `R_BE_WDT_AR/AW/W/B/R`, etc.) and BE LTR decision/latency controls.

These symbols are used by BE-specific files such as `mac_be.c`, `pci_be.c`, `rtw8922a.c`, and `rtw8922d.c`. For example, BE power-up sequences manipulate `R_BE_SYS_PW_CTRL`, firmware download paths update `R_BE_WCPU_FW_CTRL` and optionally `R_BE_DCPU_PLATFORM_ENABLE`, PCI code programs BE watchdog and LTR registers, and chip info tables point H2C/C2H transport fields at the BE mailbox registers.

## BE DMAC, Dispatcher, Packet Buffers, Security, MLO, HAXI, And Early CMAC

The BE DMAC section keeps the AX structure but adds newer blocks:

- DMAC function/clock gates: `R_BE_DMAC_FUNC_EN`, `R_BE_DMAC_CLK_EN`, including MLO, PLRLS, P-AXIDMA, DLE data-CPUIO, and LTR-control bits in addition to the AX-style modules.
- SER and IDCT diagnostics: SER L1 debug counters, firmware-triggered IDCT registers, top-level DMAC error masks/status, and expanded dispatcher ISR/IMR blocks.
- Dispatcher and RX stop/fwd controls: BE-specific `R_BE_DISP_ERROR_ISR*`, `R_BE_DISP_*_IMR`, `R_BE_RX_STOP`, and `R_BE_DISP_FWD_WLAN_0`.
- WDE/PLE packet buffers: BE packet-buffer config, buffer-manager control, expanded WDE/PLE error masks, quota registers up to PLE quota 13, and debug function interface.
- CPUIO and release paths: WD/PL buffer request/status/CPU queue operations, CPUIO error masks, WDRLS, BB report, LA, CH info, packet-in, MPDU, forwarding, WOW, RX header transform, and security-engine definitions.
- BE extensions: MLO init/error IDCT registers, PLRLS, SS/interrupt status, HAXI init/stop/IDCT, HCI flow control and page accounting, LTPC, CMAC share function enable, coexistence/grant controls, and power MACID base ranges.
- Early BE CMAC/PTCL: `R_BE_CMAC_FUNC_EN`, `R_BE_CK_EN`, `R_BE_WMAC_RFMOD`, GID position registers, sub-band and RRSR registers, CMAC error/firmware-trigger IDCT, SER L0 counters, port-0 TSF/beacon controls, EDCA/CCA/TX enable, and the start of aggregation-backoff controls.

The chunk shows BE support is not just a renaming of AX registers. Addresses move to larger windows, 320 MHz bandwidth appears via `BE_WMAC_RFMOD_320M`, MLO/PLRLS and DCPU controls appear, watchdog coverage broadens, and many aggregate masks use raw revision constants for newer interrupt layouts.

## Control Flow And State Model

This header has no executable control flow. Its effective control flow is imposed by callers that sequence reads/writes against these macros:

- Power-on code clears suspend/off bits, enables WLON/ONMAC, polls ready bits, then enables DMAC/CMAC/HCI blocks.
- Firmware paths set/clear firmware download, path-ready, and host-exist bits, then exchange H2C/C2H data through register mailbox windows.
- Packet-buffer setup reads WDE/PLE configuration, updates page size/start boundaries/free-page totals, programs quota registers, and waits for initialization-ready bits.
- Error/SER paths read top-level DMAC/CMAC indicators, then inspect submodule ISR registers and apply version-appropriate IMR clear/set masks.
- Per-band operations derive CMAC1 register offsets from `_C1` constants or `rtw89_mac_reg_by_idx()`.

Hardware state persists in device registers across normal driver calls and may survive until reset, power state transitions, or firmware/SER recovery. Some registers represent sticky interrupt or error status; others are control latches, one-shot triggers, or live counters. The header itself stores no software state, but incorrect masks can leave hardware in an inconsistent persistent state.

## Dependencies And Integration Points

Important dependencies and users visible from this chunk include:

- Kernel bitfield helpers: `BIT()`, `GENMASK()`, and `u32_encode_bits()`.
- rtw89 register access helpers in MAC/HCI code: `rtw89_read*`, `rtw89_write*`, set/clear/mask helpers, polling helpers, and per-band register-index helpers.
- Chip-specific bring-up files: AX chips use `R_AX_*` power, DMAC, CMAC, coexistence, and antenna-table constants; BE chips use `R_BE_*` power, firmware, DMAC, HCI, watchdog, LTR, and CMAC constants.
- `mac.c` and `mac_be.c`: core MAC power state, firmware download, packet-buffer quota setup, security engine enablement, RX filter control, CSI/beamforming, coexistence setup, and SER diagnostics.
- `pci.c` and `pci_be.c`: PCI power, LTR, watchdog, and HCI/DMA behavior.
- `coex.c`: Bluetooth/LTE coexistence register selection and grant/status control.
- `debug.c`: debugfs register dumps and controlled debug toggles for CMAC/TMAC/security and power tables.
- `phy.c`: TX power table base/max macros for power-by-rate, power-limit, and RU-limit programming.

## Risks And Edge Cases

- Register layout versioning is dense. Many macros share names with `_V1` or `_V01` variants, and some addresses overlap intentionally for different views. A consumer must pick the variant tied to the chip descriptor, not just the nearest name.
- Aggregate interrupt masks encode hardware policy. Changing a single constituent bit can alter SER behavior, hide hangs, or enable noisy/unsupported interrupts.
- AX and BE namespaces are similar but not interchangeable. BE adds larger address windows, DCPU, MLO, PLRLS, expanded watchdogs, 320 MHz fields, and different interrupt-mask constants.
- Per-band `_C1` offsets are easy to misuse. Directly adding offsets or using a CMAC0 register against CMAC1 can corrupt another band's state.
- Some macros define literal default values for hardware tables and path combinations. These values are opaque hardware contracts and are hard to validate by inspection.
- Duplicate or repeated bit macro names appear in version-specific sections. Include-order or redefinition warnings are not expected in this header as written, but future edits should avoid accidental semantic redefinition.
- Several status registers are sticky or clear-on-write style in hardware. Using a mask intended for IMR as an ISR value, or vice versa, can leave stale error state or clear useful diagnostics.

## Test And Validation Signals

There are no unit tests in this header. Useful validation is indirect:

- Build coverage catches missing macros, typoed names, invalid bit helpers, and duplicate definitions that trigger compiler warnings.
- Device bring-up tests should verify AX and BE chips can power on, download firmware, enable HCI/DMAC/CMAC, and exchange H2C/C2H messages.
- Suspend/resume and low-power tests exercise `R_*_SYS_PW_CTRL`, LPS/resume, LTR, watchdog, and HCI power bits.
- TX/RX traffic tests exercise packet-buffer quota programming, HCI flow control, RX filters, security engine enablement, and CMAC/PTCL/TMAC/RMAC configuration.
- SER/error-injection or fault diagnostics should confirm aggregate IMR/ISR masks route faults to the expected handler without interrupt storms.
- Multi-band tests should validate `_C1` CMAC paths, beacon/TSF per-port behavior, and per-band RX/TX controls.
- Coexistence tests should monitor BTC/LTE grant controls and counters under Wi-Fi plus Bluetooth/LTE activity.
- Debugfs and register-dump paths provide sanity checks that address ranges and table base/max aliases match actual hardware maps.

### subset-b-004933: lines 7054-10717

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/reg.h lines 7054-10717

## Scope

This chunk is the tail of the Realtek rtw89 register definition header. It is not executable code; it defines MMIO/register addresses and bit masks used by the Wi-Fi 7/BE MAC, BB wrapper, PHY, RF calibration, TX power, coexistence, and watchdog paths. Most definitions use the local `R_*` register-address convention and `B_*` bit/field-mask convention built on Linux `BIT()` and `GENMASK()`.

The range covers two broad address spaces:

- BE CMAC/WMAC and TX-power wrapper registers around `0x10800` through `0x168e4`, with C1/second-MAC aliases such as `R_BE_TB_PPDU_CTRL_C1`.
- PHY/RF/BB calibration registers from low PHY offsets through BE4 high-address aliases, ending with WiFi CPU local-domain watchdog registers `R_AX_WDT_CTRL` and `R_AX_WDT_STATUS`.

## Purpose

The definitions provide the symbolic contract between the rtw89 driver and Realtek BE hardware. They let driver code:

- initialize protocol timing, response rates, NAV behavior, RX filters, BA/CSI response memory, and BE trigger/response behavior;
- mask, enable, and dump protocol/RX/TX/PHY-interface/TX-power error interrupts;
- program BE TX power by rate, power limits, RU limits, offsets, force controls, FTM controls, and BT coexistence power hooks;
- operate PHY channel/bandwidth, EDCCA/NHM/IFS measurement, CFO compensation, BSS coloring, RF path selection, baseband gain, and packet-detection knobs;
- run RFK calibration flows including IQK, DPK, DACK, ADDCK, DRCK, TSSI, PA bias, and coefficient/LUT operations;
- access BE4/RTL8922D-specific duplicated register maps and WiFi CPU watchdog state.

## Important Register Groups

### BE PTCL/TMAC/RX DMA and Error Registers

The first block defines BE protocol control and data-path registers:

- `R_BE_TB_PPDU_CTRL`, `R_BE_AMPDU_AGG_LIMIT`, `R_BE_AGG_LEN_HT_0`, `R_BE_SPECIAL_TX_SETTING`, `R_BE_SIFS_SETTING`, `R_BE_TXRATE_CHK`, and `R_BE_TXCNT` configure trigger-based PPDU behavior, AMPDU limits, special TX modes, SIFS/CTS-to-self timing, TX rate validation, and TX counters.
- `R_BE_PTCL_PRELD_CTRL`, `R_BE_BT_PLT`, `R_BE_PTCL_BSS_COLOR_0/1`, `R_BE_PTCL_FSM_MON`, and `R_BE_PTCL_TX_CTN_SEL` configure preloading queues, BT packet-lifetime grants, BSS color fields, protocol FSM timeout thresholds, and TX-contender/busy status.
- `R_BE_PTCL_IMR_2`, `R_BE_PTCL_IMR0/1`, and `R_BE_PTCL_ISR0/1` define protocol interrupt masks/status. Composite masks such as `B_BE_PTCL_IMR0_CLR`, `B_BE_PTCL_IMR0_SET`, `B_BE_PTCL_IMR1_CLR`, and `B_BE_PTCL_IMR1_SET` are consumed by chip error-mask tables.
- `R_BE_RX_ERROR_FLAG`, `R_BE_RX_ERROR_FLAG_IMR`, `R_BE_TX_ERROR_FLAG`, `R_BE_TX_ERROR_FLAG_IMR`, plus `_1` variants define DMA/RU/FSM/zero-length error reporting for RX resource units 0-15 and TX resource units 0-15. The `_V1` masks distinguish later chip revisions.
- `R_BE_WMTX_*`, `R_BE_TRXPTCL_RESP_*`, `R_BE_MAC_LOOPBACK`, `R_BE_CLIENT_OM_CTRL`, `R_BE_WMAC_NAV_CTL`, `R_BE_RXTRIG_TEST_USER_2`, `R_BE_TRXPTCL_ERROR_INDICA_MASK`, `R_BE_TRXPTCL_ERROR_INDICA`, `R_BE_PHYINFO_ERR_IMR_V1`, and `R_BE_PHYINFO_ERR_ISR` back WMAC response, loopback, NAV, trigger-test, and error-indication flows.

Integration examples:

- `mac_be.c` uses `R_BE_TB_PPDU_CTRL` in `tmac_init_be()` to clear `B_BE_QOSNULL_UPD_MUEDCA_EN`.
- `mac_be.c` uses `R_BE_SPECIAL_TX_SETTING`, `R_BE_WMAC_NAV_CTL`, and `R_BE_TRXPTCL_RESP_0` in `nav_ctrl_init_be()` to configure NAV behavior and force MBA duration.
- `mac_be.c` uses `R_BE_SIFS_SETTING`, `R_BE_PTCL_FSM_MON`, and `R_BE_AMPDU_AGG_LIMIT` in protocol initialization.
- `mac_be.c` polls `R_BE_PTCL_TX_CTN_SEL` and `B_BE_PTCL_BUSY` in the BE TX-idle path.
- `rtw8922a.c` and `rtw8922d.c` build chip-specific IMR tables from the `*_IMR_*_CLR/SET` macros.
- `mac_be.c` dumps `R_BE_PTCL_IMR*`, `R_BE_PTCL_ISR*`, `R_BE_RX_ERROR_FLAG*`, `R_BE_TX_ERROR_FLAG*`, and `R_BE_TRXPTCL_ERROR_INDICA*` when CMAC error indicators fire.

### Response, CSI, RX Filter, and CAM Registers

This range defines the WMAC response-format matrix:

- `R_BE_BFMEE_RESP_OPTION`, `R_BE_TRXPTCL_RESP_CSI_CTRL_0/1`, `R_BE_TRXPTCL_RESP_CSI_RRSC`, and `R_BE_TRXPTCL_RESP_CSI_RATE` drive BFee/CSI response setup.
- `R_BE_WMAC_ACK_BA_RESP_*`, `R_BE_WMAC_RX_RTS_RESP_*`, `R_BE_WMAC_RX_MURTS_RESP_*`, and `R_BE_WMAC_OTHERS_RESP_*` encode ACK/BA/RTS/MU-RTS/other response behavior for legacy, HE, and EHT puncturing modes.
- `R_BE_RCR`, `R_BE_PLCP_HDR_FLTR`, `R_BE_RXGCK_CTRL`, `R_BE_RX_FLTR_OPT`, `R_BE_CTRL_FLTR`, `R_BE_MGNT_FLTR`, `R_BE_DATA_FLTR`, `R_BE_ADDR_CAM_CTRL`, `R_BE_RESPBA_CAM_CTRL`, `R_BE_PPDU_STAT`, `R_BE_RX_SR_CTRL`, `R_BE_BSSID_SRC_CTRL`, `R_BE_CSIRPT_OPTION`, `R_BE_BSR_UPD_CTRL`, and `R_BE_DRV_INFO_OPTION` define RX filtering, CAM addressing, PPDU status, spatial reuse, BSSID source, CSI report, and driver-info options.
- `R_BE_RESP_CSI_RESERVED_PAGE` stores the reserved packet-id/page count used for CSI response buffers.
- `R_BE_RESP_IMR1`, `R_BE_RESP_IMR`, `R_BE_RX_ERR_ISR`, `R_BE_RX_ERR_IMR`, and `R_BE_RX_PLCP_EXT_OPTION_1/2` define response/RX error masks and PLCP option bits.

Integration examples:

- `mac_be.c` initializes response rates and response RRSR fields in `trxptcl_init_be()`, using `R_BE_TRXPTCL_RESP_0/1` and the chip `rrsr_cfgs`.
- `mac_be.c` resets the BA CAM through `R_BE_RESPBA_CAM_CTRL` and polls `B_BE_BACAM_RST_MASK`.
- `mac_be.c` programs `R_BE_RCR`, `R_BE_RX_FLTR_OPT`, `R_BE_PLCP_HDR_FLTR`, `R_BE_RX_PLCP_EXT_OPTION_1/2`, `R_BE_BSR_UPD_CTRL`, and `R_BE_RXGCK_CTRL` in RX filter setup.
- `mac_be.c` programs CSI reserved pages with DLE reserved-queue data in `resp_pktctl_init_be()`.
- `mac_be.c` enables BFee/CSI response behavior through `R_BE_TRXPTCL_RESP_CSI_CTRL_0/1`, `R_BE_CSIRPT_OPTION`, `R_BE_TRXPTCL_RESP_CSI_RRSC`, and `R_BE_TRXPTCL_RESP_CSI_RATE`.

### BE TX Power and BB Wrapper Registers

The `R_BE_PWR_*` block defines the MAC-side TX power wrapper and table windows:

- Control registers include `R_BE_PWR_MODULE`, `R_BE_PWR_LISTEN_PATH`, `R_BE_PWR_REF_CTRL`, `R_BE_PWR_OFST_LMTBF`, `R_BE_PWR_FORCE_LMT`, `R_BE_PWR_RATE_CTRL`, `R_BE_PWR_RATE_OFST_CTRL`, `R_BE_PWR_BOOST`, `R_BE_PWR_OFST_RULMT`, `R_BE_PWR_FORCE_MACID`, `R_BE_PWR_REG_CTRL`, `R_BE_PWR_COEX_CTRL`, `R_BE_PWR_TH`, `R_BE_PWR_RSSI_TARGET_LMT`, `R_BE_PWR_OFST_SW`, `R_BE_PWR_FTM`, and `R_BE_PWR_FTM_SS`.
- Table windows include `R_BE_PWR_BY_RATE` to `R_BE_PWR_BY_RATE_END`, `R_BE_PWR_LMT` to `R_BE_PWR_LMT_MAX`, and `R_BE_PWR_RU_LMT` to `R_BE_PWR_RU_LMT_MAX`.
- Error/status definitions include `R_BE_C0_TXPWR_IMR`, `R_BE_TXPWR_ERR_FLAG`, and `R_BE_TXPWR_ERR_IMR`, with C1 aliases.

Integration examples:

- `phy_be.c` clears table windows in `rtw89_phy_bb_wrap_tpu_set_all()` and writes by-rate/limit/RU-limit pages in the BE TX-power programming functions.
- `phy_be.c` uses `R_BE_PWR_FORCE_*`, `R_BE_PWR_COEX_CTRL`, and `R_BE_PWR_RATE_CTRL` to clear force modes during BB wrapper initialization.
- `phy_be.c` configures `R_BE_PWR_LISTEN_PATH`, `R_BE_PWR_FTM`, `R_BE_PWR_FTM_SS`, `R_BE_PWR_TH`, and `R_BE_PWR_RSSI_TARGET_LMT` for listen-path, FTM, and uplink-power behavior.
- `rtw8922a.c` and `rtw8922d.c` write `R_BE_PWR_REF_CTRL`, `R_BE_PWR_RATE_CTRL`, `R_BE_PWR_REG_CTRL`, `R_BE_PWR_COEX_CTRL`, and `R_BE_PWR_BOOST` for chip-specific power and BT grant handling.
- `debug.c` uses the table ranges for dumping BE power-by-rate, power-limit, and RU-limit windows.

### PHY, CCX, EDCCA/NHM/IFS, and Channel Registers

The middle PHY block defines baseband measurement, channel, and path-control registers:

- Clock/reset/control: `R_UPD_P0`, `R_BBCLK`, `R_RSTB_WATCH_DOG`, `R_EMLSR`, `R_CHK_LPS_STAT`, `R_SPOOF_CG`, `R_DFS_FFT_CG`, `R_CHINFO_DATA`, `R_ANAPAR*`, `R_RFE_*`, `R_CIRST`, and SWSI/HWSI access registers.
- PHY-status and PMAC: `R_PLCP_HISTOGRAM`, `R_PHY_STS_BITMAP_*`, `R_PMAC_GNT`, `R_PMAC_RX_CFG1`, `R_PMAC_RXMOD`, `R_PMAC_TX_CTRL`, `R_PMAC_TX_PRD`, and `R_PMAC_TX_CNT`.
- CCX/noise/IFS: `R_CCX`, `R_NHM_CFG`, `R_NHM_TH*`, `R_FAHM`, `R_IFS_COUNTER`, `R_IFS_T1` through `R_IFS_T4`, `R_IFS_CLM_*`, `R_IFS_HIS`, `R_IFS_AVG_*`, `R_IFS_CCA_*`, `R_IFSCNT`, and BE4 alternatives such as `R_IFS_T1_AVG_BE4`.
- EDCCA and CCA: `R_EDCCA_RPT_*`, `R_SEG0R_EDCCA_LVL*`, `R_SEG0R_PPDU_LVL_BE*`, `R_RXCCA*`, `R_RXHE`, `R_SPOOF_ASYNC_RST`, and `R_BMODE_PDTH*`.
- Channel/bandwidth and RF path state: `R_FC0*`, `R_CHBW_MOD*`, `R_DBCC`, `R_ANT_CHBW`, `R_ANT_RX_BE4`, `R_BW_BE4`, path initial-gain registers, LNA/TIA/RXB init registers, BT-share registers, notch/5M detector registers, and BSS-color clear-map registers.
- TX filtering and coefficients: `R_TXFIR*`, `R_PCOEFF*`, `R_TX_CFR_MANUAL_EN_BE4`, `R_PATH0_TX_CFR`, and `R_PATH0_TX_POLAR_CLIPPING`.

Integration examples:

- `phy.c` maps the CCX/NHM/IFS definitions into `rtw89_ccx_regs`-style configuration used by channel-load/noise measurement.
- `phy.c` uses BSS-color clear-map registers in BSS color programming.
- Chip files such as `rtw8851b.c`, `rtw8852c.c`, and BE chip files use path, channel, EDCCA, and coefficient definitions to fill chip-info register tables for channel changes, BT coexistence, RSSI offsets, bandwidth programming, RXCCA control, and TX FIR/CFR setup.
- `phy_be.c` supplies BE and BE4 register structs for PHY status, CFO compensation, and BB wrapper behavior.

### RFK, IQK/DPK/DACK/TSSI Calibration Registers

The RF calibration block is dense and stateful:

- TSSI and TX power baseband registers include `R_TSSI_PA_K*`, `R_P0_TSSI_*`, `R_P1_TSSI_*`, `R_TSSI_THOF`, `R_TSSI_PWR_P0/P1`, `R_TSSI_MAP_OFST_P0/P1`, `R_TXAGC_REF_DBM_*`, `R_TSSI_K_*`, `R_TXPWRB*`, `R_TXPWR_RST*`, and BE4 path/table variants.
- DACK/ADDCK/DRCK registers include `R_DCOF*`, `R_DACK_S0P*`, `R_DACK_S1P*`, `R_DACK_BIAS*`, `R_DACK_DADCK*`, `R_DACK10/11`, `R_DACK1_K`, `R_DACK2_K`, `R_ADDCK0*`, `R_ADDCK1*`, `R_DRCK*`, and `R_DACKN*_CTL`.
- IQK/DPK/KIP/NCTL registers include `R_NCTL_CFG`, `R_NCTL_RPT`, `R_NCTL_N1/N2`, `R_IQK_*`, `R_TPG_*`, `R_MDPK_*`, `R_KIP_*`, `R_DPK_*`, `R_CFIR_*`, `R_DPD_*`, `R_GAPK`, coefficient LUT/register windows, and report/status registers.
- BE4 additions include OOB/DPD/QAM/RFSI compensation thresholds, override-value registers, band-edge controls, software SI data windows, KTBL controls, and thermal-compensation controls.

Integration examples:

- `phy_be.c` preinitializes RF/NCTL clocks and resets through `R_GOTX_IQKDPK_*`, `R_IQK_DPK_RST*`, and `R_IQK_DPK_PRST*`, using BE4 alternatives for newer chips.
- `rtw8922a_rfk.c`, `rtw8922d_rfk.c`, and older RFK implementations use the TSSI, DACK, ADDCK, DRCK, IQK, DPK, KIP, CFIR, and coefficient definitions for calibration sequencing, status polling, and result application.
- DACK state is read from result/status fields such as `B_DACK_S0P*_OK`, `B_DACK_S1P*_OK`, `B_ADDCKR*_A*`, and bias/DADCK masks, then written back through manual-control fields.
- TSSI calibration writes tracking enable/moving-average/reference-DBM/K-factor fields and controls SAR/maximum RF power through `R_P0_TXPWRB_BE`, `R_P1_TXPWRB_BE`, and BE4 equivalents.

### BE4/RTL8922D-Specific High Address Registers

The chunk adds many `_BE4` aliases in the `0x20000`, `0x24000`, `0x26000`, `0x2e000`, and `0x38000` ranges. These are used for later BE/BE4 hardware layout changes:

- `R_SYS_DBCC_BE4`, `R_EMLSR_SWITCH_BE4`, `R_CHINFO_SEG_BE4`, and `R_SEL_GNT_BT_RX*_BE4` cover DBCC, EMLSR, channel-info, and BT grant routing.
- `R_ENABLE_CCK0_BE4`, `R_RSTB_ASYNC_BE4`, `R_STS_HDR2_PARSING_BE4`, `R_TXINFO_PATH_BE4`, `R_TX_ERROR_SEL_BE4`, and `R_IMR_TX_ERROR_BE4` cover BE4 parsing/error behavior.
- BE4 EDCCA/IFS registers provide alternate measurement/report addresses.
- BE4 TSSI/TXAGC/path/channel/RX decode registers support per-path and per-table programming for newer chips.
- `R_SW_SI_*_BE4`, `R_RX_PATH*_TBL0_BE4`, `R_KTBL*_*_BE4`, and `R_TC_*_BE4` support software serial-interface access, RX path tables, calibration tables, and thermal-compensation triggers.

## Control Flow and State Behavior

Because this file is a register map, control flow is in consumers rather than here. The expected flow is:

1. Chip-specific probe selects chip operations and register configs.
2. MAC/CMAC initialization calls BE init helpers, checks MAC enablement, resolves C0/C1 addresses with `rtw89_mac_reg_by_idx()`, and writes protocol/RX/response bits.
3. PHY/BB initialization writes direct PHY registers, sets BB wrapper tables, and initializes RF/NCTL blocks.
4. Channel, bandwidth, coexistence, TX power, and calibration operations reuse these definitions to update hardware state after runtime state changes.
5. Error handling uses the composite IMR/ISR masks and error-flag definitions to enable/clear/report hardware faults.

The persistent state is almost entirely hardware-resident. Writes persist until firmware/driver reset, SER recovery, power-state transitions, channel changes, or explicit calibration reprogramming. Some calibration consumers copy hardware result fields into driver RFK state structures before later restoring them to manual fields. Table-window writes for TX power and RF coefficients persist in chip table SRAM/register windows and must be reloaded when regulatory/channel/SAR/calibration state changes.

## Dependencies

This header depends on common kernel bit helpers (`BIT`, `GENMASK`) and rtw89 register access wrappers in other files:

- MAC wrappers: `rtw89_read*()`, `rtw89_write*()`, `rtw89_write*_mask()`, `rtw89_mac_reg_by_idx()`, and `rtw89_mac_txpwr_write32*()`.
- PHY wrappers: `rtw89_phy_read32*()`, `rtw89_phy_write32*()`, and indexed PHY accessors.
- Polling helpers such as `read_poll_timeout_atomic()`.
- Chip metadata in `struct rtw89_chip_info`, `struct rtw89_rrsr_cfgs`, BB wrapper register structs, TX power tables, RFK state structs, and channel descriptors.

The definitions must remain aligned with hardware manuals and chip-ID/revision assumptions in `rtw8922a.c`, `rtw8922d.c`, `mac_be.c`, `phy_be.c`, and RFK implementation files.

## Integration Points

- `mac_be.c`: BE CMAC/TMAC/PTCL/RX/CSI/BFee initialization, TX idle polling, TX power address validation, and CMAC error dumps.
- `phy_be.c`: BE PHY status/CFO/CCX/BB wrapper register configs, RF/NCTL preinit, TX power table programming, FTM/listen-path/force-control setup, and BE4 RFSI/band-edge logic.
- `rtw8922a.c` and `rtw8922d.c`: chip-specific error IMR tables, RRSR configs, TX power reference/boost/coexistence programming, SAR max writes, and TSSI K-factor handling.
- `rtw8922*_rfk.c` and older `rtw8852*_rfk.c`: DACK/IQK/DPK/TSSI calibration sequences and status polling.
- `debug.c`: register-range dumps for BE TX power tables.
- Chip data files: channel/bandwidth, EDCCA, BSS color, BT coexistence, RSSI, TX filter, and path-control mappings.

## Risks and Edge Cases

- Address aliases are revision-sensitive. Many registers have C1 aliases and BE4 variants; using a base address without `rtw89_mac_reg_by_idx()` or the correct BE4 symbol can write the wrong MAC/PHY instance.
- Composite IMR masks encode policy, not only bit layout. Incorrect `*_CLR`, `*_SET`, or `_V1` selection can leave serious DMA/RU/FSM errors masked or cause noisy interrupts.
- Several aliases share the same address with different field names, for example OOB/DPD threshold registers. Consumers must use the mask matching the intended hardware mode.
- Table windows have strict sizes and ordering. TX-power by-rate/limit/RU-limit loops assume consecutive 32-bit registers and struct sizes checked with `BUILD_BUG_ON()` in consumers.
- Calibration sequencing is timing-sensitive. DACK/ADDCK/DRCK/IQK/DPK definitions include kick, reset, ready, and result fields; missed polling or wrong manual/auto selection can leave RF paths miscalibrated.
- Some status macros are used for error diagnostics only. If renamed or removed without updating dumps, SER triage loses observability.
- Register names mix generations (`AX`, `BE`, `BE4`, `V1`) and paths (`P0/P1`, `S0/S1`, C0/C1). Reviewers need to verify both generation and path before reusing a symbol.

## Test and Validation Signals

Useful validation for changes touching this range:

- Build coverage for all enabled rtw89 chips, especially RTL8922A/RTL8922D and BE4 paths, to catch missing/renamed macros.
- Boot/probe smoke tests with both MAC instances where supported, checking that CMAC init completes and `tx_idle_poll_band_be()` does not timeout.
- SER/error-injection or debug-trigger tests that verify IMR/ISR/error dump paths print the expected PTCL, DMA, PHYINFO, TRXPTCL, and TXPWR registers.
- RX/TX functional tests across legacy/HE/EHT rates, puncturing modes, AMPDU aggregation, BA/CSI/BFee response, and NAV/CTS-to-self behavior.
- Regulatory/SAR/TX-power tests that verify by-rate, limit, RU-limit, offset, BT coexistence, and forced-power controls are reflected in hardware.
- Channel/bandwidth switch tests across 20/40/80/160/320 MHz and DBCC/EMLSR modes, watching EDCCA/NHM/IFS counters and PHY status parsing.
- RFK validation after cold boot, resume, channel switch, and SER recovery: DACK/ADDCK/DRCK/IQK/DPK/TSSI status bits should complete, and EVM/RSSI/TSSI telemetry should remain in range.
