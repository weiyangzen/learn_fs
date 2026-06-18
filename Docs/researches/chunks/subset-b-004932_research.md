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
