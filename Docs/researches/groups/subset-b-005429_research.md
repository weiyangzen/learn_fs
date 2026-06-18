# subset-b-005429 research

This grouped report covers the RTL8723BS HAL, SDIO, PHY/RF, and shared include files assigned to `subset-b-005429`. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_hal_init.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_hal_init.c

Purpose: this is the common RTL8723B HAL support file used by the SDIO variant for firmware download, EFUSE/EEPROM parsing, chip-version discovery, beacon control, rate-mask updates, TX descriptor construction, C2H handling, and generic `SetHwReg`/`GetHwReg` dispatch.

Important APIs and functions: `_FWDownloadEnable`, `_WriteFW`, `_FWFreeToGo`, and `rtl8723b_FirmwareDownload` request `rtlwifi/rtl8723bs_nic.bin`, strip a 32-byte firmware header when present, write paged firmware at `FW_8723B_START_ADDRESS`, poll checksum and firmware-ready bits, and cache firmware version/signature in `hal_com_data`. EFUSE APIs include `Hal_GetEfuseDefinition`, `Hal_EfusePowerSwitch`, `Hal_ReadEFuse`, `Hal_InitPGData`, and parse helpers for ID, TX power, BT coexistence, package type, channel plan, crystal cap, thermal meter, and RF gain. TX path APIs include `BWMapping_8723B`, `SCMapping_8723B`, `rtl8723b_update_txdesc`, and `rtl8723b_fill_fake_txdesc`.

Control flow: firmware reset/download happens before MAC/BB/RF init in `sdio_halinit.c`. EFUSE parsing populates `eeprom_priv` and `hal_com_data`; later PHY and TX-power code consumes those fields. TX descriptor fill branches by frame tag: data frames use RA/rate/aggregation/security/VCS settings, management frames force driver rates and retry limits, and special packets can request CCX reports. `SetHwReg8723B` is a large dispatcher for media state, beacon/TSF, BSSID filters, CAM, EDCA, firmware power H2C commands, initial gain, FIFO cleanup, NAV, reserved pages, and MACID sleep.

State and persistence: persistent hardware-derived state lives in `hal_com_data` (`VersionID`, firmware fields, EEPROM power tables, BT coexistence flags, beacon register shadows, EFUSE usage, RF channel values) and `eeprom_priv` (`mac_addr`, autoload status, RF gain). Register writes are immediate hardware state; several values are shadowed so survey/join/beacon transitions can restore them. Global test hooks `g_fwdl_chksum_fail` and `g_fwdl_wintint_rdy_fail` can force firmware-download failures.

Dependencies and integration: depends on Linux firmware loading, Realtek IO helpers (`rtw_read*`, `rtw_write*`), ODM/PHY helpers, BT coexistence notifications, MLME state, xmit/recv structures, and the register macros in `hal_com_reg.h`/`Hal8192CPhyReg.h`. SDIO-specific init calls these routines and the xmit path relies on descriptor helpers.

Risks and test signals: firmware download has retry and timeout paths that should be tested with missing, oversized, corrupt, and slow-ready firmware. EFUSE parsing must handle all-`0xff` autoload failures without out-of-bounds table access. TX descriptor checksum and bitfield packing are high-risk because hardware silently drops malformed descriptors. Useful signals include successful firmware-ready polling, valid MAC address/channel plan, association traffic across data/management/EAP/ARP/DHCP frames, beacon mode transitions, C2H BT/CCX event handling, and suspend/resume FIFO cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_hal_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_phycfg.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_phycfg.c

Purpose: this file implements RTL8723B baseband and RF register access, MAC/BB/RF configuration loading, TX power programming, and channel/bandwidth switching.

Important APIs and functions: `PHY_QueryBBReg_8723B` and `PHY_SetBBReg_8723B` read/write masked BB register fields using `phy_CalculateBitShift`. `PHY_QueryRFReg_8723B` and `PHY_SetRFReg_8723B` wrap RF serial read/write over the HSSI/LSSI BB registers initialized by `phy_InitBBRFRegisterDefinition`. `PHY_MACConfig8723B`, `PHY_BBConfig8723B`, and `PHY_RFConfig8723B` load ODM header-file tables and perform RF LCK. TX power APIs include `PHY_SetTxPowerIndex`, `PHY_GetTxPowerIndex`, and `PHY_SetTxPowerLevel8723B`. `PHY_SwChnl8723B` and `PHY_SetSwChnlBWMode8723B` update runtime channel and bandwidth.

Control flow: BB config first initializes RF register definitions, enables BB/RF clocks and resets, applies MAC/BB/AGC tables, initializes TX-power-by-rate and optional power-limit tables, and applies crystal-cap settings. RF config delegates to `PHY_RF6052_Config8723B` and then performs LCK. Channel/bandwidth changes stage new values in `hal_com_data`, apply RF channel bits and BB bandwidth registers, then reprogram TX power for the current channel.

State and persistence: `hal_com_data` stores `PHYRegDef`, `CurrentChannel`, `CurrentChannelBW`, primary side-channel offsets, `RfRegChnlVal`, antenna diversity configuration, and EEPROM-derived power tables. Register writes persist in hardware until reset or a later channel/bandwidth operation.

Dependencies and integration: uses ODM config routines (`ODM_ReadAndConfig_MP_8723B_MAC_REG`, `ODM_ConfigBBWithHeaderFile`, `ODM_ConfigRFWithHeaderFile`) and common power-limit helpers declared in `hal_com_phycfg.h`. SDIO HAL init calls MAC, BB, and RF config in sequence, and xmit descriptor mapping reads current bandwidth state from `hal_com_data`.

Risks and test signals: masked register writes depend on correct bit masks; RF serial reads require timing delays and correct RF path definitions. Channel switching rolls state forward before applying hardware writes and only rolls back when the adapter is already stopped/removed. Tests should cover legal/illegal channels, 20/40 MHz transitions, crystal-cap programming, TX power for CCK/OFDM/MCS rates, antenna-diversity path selection, and init failure propagation from ODM table loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_phycfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_rf6052.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_rf6052.c

Purpose: this file contains the RF6052-specific RF programming used by RTL8723B. It configures RF paths, RF bandwidth bits, and RF power-tracking tables.

Important APIs and functions: `PHY_RF6052SetBandwidth8723B` updates `RF_CHNLBW` for 20 MHz or 40 MHz operation on RF path A and B using the cached `hal_com_data.RfRegChnlVal[0]`. `PHY_RF6052_Config8723B` sets `NumTotalRFPath` to one and invokes `phy_RF6052_Config_ParaFile`. The static config routine enables RF environment control, sets 3-wire address/data lengths, calls `ODM_ConfigRFWithHeaderFile(CONFIG_RF_RADIO, path)`, restores original RF environment state, and loads TX power tracking via `ODM_ConfigRFWithTxPwrTrackHeaderFile`.

Control flow: PHY RF init reaches this file through `PHY_RFConfig8723B`. Each configured RF path is prepared by reading and enabling RF interface control in the BB register definition table, ODM RF config writes the radio registers, then the original RF environment control bit is restored. Bandwidth changes are later called from `phy_PostSetBwMode8723B`.

State and persistence: the main state is `hal_com_data.NumTotalRFPath`, `PHYRegDef`, and `RfRegChnlVal`. Hardware state persists in RF registers, especially `RF_CHNLBW`; the cached value is reused for later channel/bandwidth updates.

Dependencies and integration: depends on RF/BB helpers from `rtl8723b_phycfg.c`, register constants from `Hal8192CPhyReg.h`, and ODM-generated RF tables. It is integrated into SDIO HAL init through the PHY config sequence.

Risks and test signals: this driver sets only one total RF path but writes bandwidth to A and B in the bandwidth helper, so path assumptions should be validated on boards with different antenna routing. RF environment restore correctness is critical; a stale RFENV bit can break later RF access. Useful tests include RF init success, repeated 20/40 MHz switching, TX power tracking table load, and post-init RF register reads matching expected channel/bandwidth bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_rf6052.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_rxdesc.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_rxdesc.c

Purpose: this small file updates user-visible receive signal statistics from parsed PHY information for RTL8723B receive frames.

Important APIs and functions: `rtl8723b_process_phy_info` is the exported entry point. It calls `process_rssi` and `process_link_qual`, which accumulate `SignalStrength` and `SignalQuality` from `rx_pkt_attrib.phy_info` into `recvpriv.signal_strength_data` and `recvpriv.signal_qual_data`.

Control flow: the SDIO receive tasklet parses RX descriptors and optional PHY status in `rtl8723bs_recv.c`. When PHY status belongs to a packet relevant to the current BSSID, self, beacon, or AP station, `update_recvframe_phyinfo` calls `rtl8723b_process_phy_info`. Each statistic resets its accumulator when `signal_stat.update_req` is set, then increments total count/value and recomputes an integer average.

State and persistence: state is purely in `recv_priv` signal statistic accumulators. There is no hardware access and no persistence outside adapter memory. The averages remain until reset by `update_req`, adapter teardown, or reinitialization.

Dependencies and integration: depends on `union recv_frame`, `rx_pkt_attrib`, and PHY parsing from ODM. It is tightly coupled to the receive tasklet selecting which frames should influence RSSI/link quality.

Risks and test signals: integer accumulation can grow over long sessions if `update_req` is not set by higher layers; there is no saturation. Because `process_rssi` lacks explicit null checks, callers must pass valid adapter/frame pointers. Tests should verify signal updates after beacon/self packets, AP-mode station packets, reset behavior when `update_req` is set, and no updates for CRC/ICV-dropped frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_rxdesc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723bs_recv.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723bs_recv.c

Purpose: this file implements the RTL8723BS SDIO receive-buffer lifecycle, RX descriptor parsing, PHY status processing, C2H packet dispatch, and tasklet-driven delivery to the common receive stack.

Important APIs and functions: `rtl8723bs_init_recv_priv` allocates and initializes `NR_RECVBUFF` receive buffers and sets up `recv_tasklet`; `rtl8723bs_free_recv_priv` kills the tasklet and frees buffers. `rtl8723bs_recv_tasklet` is the main parser. Helpers include `update_recvframe_attrib`, `update_recvframe_phyinfo`, `rtl8723bs_c2h_packet_handler`, `try_alloc_recvframe`, `rx_crc_err`, and `pkt_exceeds_tail`.

Control flow: SDIO interrupt handling reads RX FIFO data into a `recv_buf` and schedules this tasklet. The tasklet dequeues buffers, walks each packed descriptor/payload sequence, allocates a `recv_frame`, parses `rxreport_8723b`, checks CRC policy and tail bounds, allocates an aligned skb, copies packet bytes after descriptor/driver-info/shift offset, optionally removes FCS, and dispatches normal frames to `rtw_recv_entry`. C2H packets are handled inline for CCX TX reports or forwarded to C2H workqueue commands.

State and persistence: receive buffer queues and skb ownership live in `recv_priv`. PHY-derived RSSI is written to `sta_info.rssi` and aggregate signal stats. `hal_com_data.ReceiveConfig` controls CRC/FCS/BA-SSN behavior. No on-disk persistence exists.

Dependencies and integration: depends on SDIO interrupt/RX FIFO code in `sdio_ops.c`, descriptor bit layouts, ODM `odm_phy_status_query`, station/MLME helpers, common receive queues, and C2H handlers from `rtl8723b_hal_init.c`.

Risks and test signals: length validation is critical because descriptor fields determine copy offsets. On `sd_recv_rxfifo` allocation/read failures, buffers can be temporarily unavailable; repeated allocation failures in the DPC stop RX draining. Tasklet code must avoid leaking skbs/frames on CRC, ICV, C2H, and allocation error paths. Tests should stress aggregated RX buffers, malformed descriptors, CRC policy, QoS alignment, fragmented first packets, C2H packets, AP-mode RSSI updates, and free/init symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723bs_recv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723bs_xmit.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723bs_xmit.c

Purpose: this file implements the RTL8723BS SDIO transmit scheduler, aggregation into xmit buffers, write-port draining, management-frame transmit handling, and transmit private initialization/free.

Important APIs and functions: `rtl8723bs_hal_xmit` enqueues data frames and wakes `SdioXmitStart`; `rtl8723bs_xmit_thread` runs `rtl8723bs_xmit_handler`; `xmit_xmitframes` aggregates queued frames into `xmit_buf` objects; `rtl8723bs_xmit_buf_handler` drains pending xmit buffers to SDIO write ports. `rtl8723bs_mgnt_xmit` prepares management/beacon frames. Init/free entry points are `rtl8723bs_init_xmit_priv` and `rtl8723bs_free_xmit_priv`.

Control flow: data transmit queues frames by WMM/hardware queue. The xmit thread wakes on `SdioXmitStart`, checks pending frames, selects queue order from WMM settings, allocates/extends an xmit buffer until SDIO max length or OQT space constraints, coalesces frames, fills TX descriptors with `rtl8723b_update_txdesc`, and enqueues the xmit buffer. The buffer handler waits on `xmit_comp`, checks free page counts and OQT space, writes to the mapped SDIO device ID, updates cached free pages, and frees the xmit buffer.

State and persistence: transient state lives in `xmit_priv` queues/completions, `xmit_buf` aggregation counters/page counts, `hal_com_data.SdioTxFIFOFreePage`, `SdioTxOQTFreeSpace`, and `SdioTxFIFOFreePageLock`. Link busy state can trigger ADDBA requests and low-power exit traffic notifications.

Dependencies and integration: depends on common xmit queues/coalescing, SDIO port writes from `sdio_ops.c`, queue/page mapping from `sdio_halinit.c`, TX descriptor construction in `rtl8723b_hal_init.c`, and MLME/power state.

Risks and test signals: resource accounting errors can deadlock TX or overrun FIFO pages. `pxmitbuf->priv_data` is special because the first aggregated frame is freed only after the final descriptor update; error paths must not double-free it. Tests should cover high/low/normal queues, busy traffic, AP sleeping stations, beacon direct write, management ack reports, OQT exhaustion, surprise removal/driver stop, and cleanup of pending buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723bs_xmit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/sdio_halinit.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/sdio_halinit.c

Purpose: this is the RTL8723BS SDIO hardware initialization, deinitialization, interface-configuration, adapter-info, and SDIO-specific hardware-variable dispatch file.

Important APIs and functions: `rtl8723bs_hal_init` is the main bring-up sequence; `rtl8723bs_hal_deinit` and `CardDisableRTL8723BSdio` power down the device. `_InitPowerOn_8723BS` powers on MAC/SDIO blocks; queue/page setup is handled by `_InitQueueReservedPage`, `_InitTxBufferBoundary`, `_InitQueuePriority`, `_InitPageBoundary`, and `_InitTransferPageSize`. `_InitWMACSetting`, `_InitAdaptiveCtrl`, `_InitEDCA`, `_initSdioAggregationSetting`, `_InitInterrupt`, and `_InitBurstPktLen_8723BS` program runtime MAC/SDIO defaults. `ReadAdapterInfo8723BS` reads EFUSE/EEPROM fields and `SetHwReg8723BS`/`GetHwReg8723BS` add SDIO-specific hardware variables.

Control flow: init handles an IPS fast path first, otherwise powers on, downloads firmware, initializes firmware variables, detects power-down mode, configures MAC/BB/RF, records RF channel registers, sets TX/RX queue pages and LLT, programs WMAC filters, aggregation, beacon, interrupts, current channel/bandwidth, antenna selection, reserved hardware controls, dynamic management, free-page/OQT status, MAC TX/RX enable, NAV, IQK/LCK, and BT coexistence hardware config.

State and persistence: `hal_com_data` caches SDIO endpoint count/queue selection, free pages, OQT maximum, `SdioRxFIFOCnt`, `SdioRxFIFOSize`, RF type, current channel, and MAC power-control status. `pwrctrl_priv` tracks RF power state, IPS state, RPWM toggles, and pre-IPS type. EFUSE parsing populates adapter EEPROM and HAL fields.

Dependencies and integration: uses power sequence tables, firmware download from `rtl8723b_hal_init.c`, PHY/RF config, SDIO interrupt functions, BT coexistence, ODM calibration, and common adapter/MLME/power abstractions.

Risks and test signals: init has many early returns without a common unwind path, so partial initialization failures should be tested. Power-state handling differs for normal init, IPS resume, IPS suspend, and module-loaded-but-GUI-off adapter-info reads. Tests should validate firmware-ready path, missing firmware failure, LLT timeout, endpoint/page mapping for `wifi_spec`, interrupt enable/disable, RX aggregation settings, EFUSE autoload failure, random MAC fallback, deinit in netif-up/down IPS paths, and CPWM/RPWM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/sdio_halinit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/sdio_ops.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/sdio_ops.c

Purpose: this file implements RTL8723BS SDIO address translation, register/memory/port IO operations, SDIO local register access, interrupt handling, RX FIFO draining, and TX buffer status queries.

Important APIs and functions: `sdio_set_intf_ops` installs `_read8/_read16/_read32/_read_mem/_read_port` and write counterparts. `_cvrt2ftaddr` and `hal_sdio_get_cmd_addr_8723b` map pseudo-addresses/device IDs to SDIO function-transfer addresses. `sdio_read_port` and `sdio_write_port` move RX/TX FIFO data. `EnableInterrupt8723BSdio`, `DisableInterrupt8723BSdio`, `sd_int_hdl`, and `sd_int_dpc` handle host interrupts. `HalQueryTxBufferStatus8723BSdio` and `HalQueryTxOQTBufferStatus8723BSdio` refresh transmit resource state.

Control flow: normal register access maps the address to a device ID and chooses CMD52 for early IO, low MAC power, or firmware power-save mode; otherwise CMD53/block access is used with alignment fixups. RX interrupts read `SDIO_REG_RX0_REQ_LEN`, pull RX FIFO data into a `recv_buf`, enqueue it, and schedule the receive tasklet until no more RX request is pending. AVAL interrupts refresh free pages and complete TX waiters; C2H interrupts read firmware events and either handle CCX directly or queue work; CPWM interrupts wake power-control work.

State and persistence: SDIO runtime state is in `hal_com_data.sdio_himr`, `sdio_hisr`, `SdioRxFIFOCnt`, `SdioRxFIFOSize`, `SdioTxFIFOFreePage`, and `SdioTxOQTFreeSpace`. `sdio_data.block_transfer_len` controls transfer rounding. Adapter hardware-init and power-save flags gate IO mode.

Dependencies and integration: depends on low-level SDIO helpers (`sd_read`, `_sd_read`, `sd_cmd52_read`, `sd_write`), receive buffers from `rtl8723bs_recv.c`, xmit completions from `rtl8723bs_xmit.c`, C2H handlers, and register definitions in `hal_com_reg.h`.

Risks and test signals: unaligned read/write paths allocate temporary buffers in atomic context and can fail. `sd_recv_rxfifo` returns `NULL` without requeueing if skb allocation or port read fails after a recvbuf is dequeued, so RX starvation paths need attention. Tests should cover early CMD52-only register access, CMD53 alignment, block-size rounding, interrupt clear masks, repeated RX packets in one interrupt, TX free-page completion, C2H queueing, CPWM power events, and surprise removal guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/sdio_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/Hal8192CPhyReg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/Hal8192CPhyReg.h

Purpose: this header defines BB/PMAC/RF register offsets and bit masks used by the RTL8723B PHY and RF configuration code. Despite the 8192C name, the RTL8723BS PHY code includes these shared definitions.

Important APIs/types/macros: it exports register constants for Page 8 RF mode/HSSI/LSSI/TxAGC registers, Page 9 RF mode/path switch, Page A CCK system registers, Page C/D OFDM registers, Page E IQK and TxAGC registers, and RF6052 RF register IDs such as `RF_CHNLBW`. It also defines masks including `bRFMOD`, `b3WireDataLength`, `b3WireAddressLength`, `bRFSI_RFENV`, `bLSSIReadAddress`, `bLSSIReadEdge`, `bLSSIReadBackData`, `bCCKSideBand`, and byte/dword masks.

Control flow and integration: there is no executable code. `rtl8723b_phycfg.c` uses these constants for BB masked reads/writes, RF serial access, channel/bandwidth switching, and TX power index programming. `rtl8723b_rf6052.c` uses the RFENV/HSSI/LSSI masks and `RF_CHNLBW`; `rtl8723b_hal_init.c` uses `rOFDM0_RxDSP` for notch filtering.

State and persistence: the header describes hardware register state but stores none. The masks determine which hardware bits are preserved or overwritten by callers.

Dependencies: depends only on kernel `BIT` macros being available indirectly through including contexts. It is included through HAL/PHY headers.

Risks and test signals: incorrect offsets or masks can corrupt unrelated BB/RF fields. Some constants are legacy or path-B-oriented while this chip is configured as one RF path, so callers must pair them with the correct `hal_com_data.PHYRegDef`. Test signals include successful BB/RF init, correct RF readback, stable channel/bandwidth switching, and expected TxAGC register writes for every supported rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/Hal8192CPhyReg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/HalPwrSeqCmd.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/HalPwrSeqCmd.h

Purpose: this header defines the compact power-sequence command format used to execute Realtek card enable, disable, and low-power flows.

Important APIs/types/macros: command values are `PWR_CMD_READ`, `PWR_CMD_WRITE`, `PWR_CMD_POLLING`, `PWR_CMD_DELAY`, and `PWR_CMD_END`. Base address constants include `PWR_BASEADDR_MAC` and `PWR_BASEADDR_SDIO`; interface masks include `PWR_INTF_SDIO_MSK`, USB, PCI, and all. `struct wlan_pwr_cfg` packs offset, cut/fab/interface masks, base, command, mask, and value. Accessor macros such as `GET_PWR_CFG_OFFSET`, `GET_PWR_CFG_CMD`, and `GET_PWR_CFG_VALUE` hide the packed fields. The main function prototype is `HalPwrSeqCmdParsing`.

Control flow and integration: `sdio_halinit.c` passes SDIO-specific flow arrays (`rtl8723B_card_enable_flow`, `rtl8723B_enter_lps_flow`, `rtl8723B_card_disable_flow`) to `HalPwrSeqCmdParsing`, with all cut/fab masks and SDIO interface mask. The parser interprets table rows, performing reads/writes/polls/delays until an END command.

State and persistence: the header stores no state; table execution changes MAC/SDIO power registers and determines whether `hal_com_data.bMacPwrCtrlOn` can be set.

Dependencies: includes `drv_types.h`, so it depends on the adapter type and broad driver includes.

Risks and test signals: bitfield layout in `struct wlan_pwr_cfg` must match table initializers and compiler ABI assumptions. Polling commands need bounded timeouts in the parser. Tests should validate card enable/disable flow success, low-power entry, interface-mask filtering, and behavior when a polling condition never becomes true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/HalPwrSeqCmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/HalVerDef.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/HalVerDef.h

Purpose: this header defines the HAL chip-version data model for RTL8723B and macros for classifying chip type, cut version, vendor, and ROM version.

Important APIs/types/macros: enums include `hal_ic_type_e` with `CHIP_8723B`, `hal_chip_type_e` (`TEST_CHIP`, `NORMAL_CHIP`, `FPGA`), `hal_cut_version_e` from A through K, and `hal_vendor_e` (`TSMC`, `UMC`, `SMIC`). `struct hal_version` stores IC type, chip type, cut, vendor, and `ROMVer`. Getter macros extract each field and predicate macros such as `IS_NORMAL_CHIP`, `IS_A_CUT`, and `IS_CHIP_VENDOR_TSMC` classify versions.

Control flow and integration: `rtl8723b_hal_init.c` fills `hal_com_data.VersionID` in `ReadChipVersion8723B` from `REG_SYS_CFG`, `REG_GPIO_OUTSTS`, and multi-function registers. Later init logic uses `IS_NORMAL_CHIP` to select ARFR values and other chip-dependent behavior.

State and persistence: the header defines only type shape. Runtime state persists in `hal_com_data.VersionID`.

Dependencies: relies on `ROM_VERSION_MASK` and `BIT` definitions from included contexts. It is included by `hal_com.h` and therefore widely available.

Risks and test signals: spelling of `GET_CVID_MANUFACTUER` is legacy and should not be “fixed” without updating call sites. Any new chip cut or vendor requires enum and predicate updates. Tests should confirm chip-version dumping and normal/test chip paths on real or mocked register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/HalVerDef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/basic_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/basic_types.h

Purpose: this header supplies legacy Realtek basic constants, pointer-size aliases, endian conversion helpers, little-endian bitfield accessors, alignment macros, and flag helpers.

Important APIs/types/macros: `SUCCESS`/`FAIL`, `SIZE_PTR`, `SSIZE_PTR`, `EF1BYTE`/`EF2BYTE`/`EF4BYTE`, `BIT_LEN_MASK_*`, `BIT_OFFSET_LEN_MASK_*`, `LE_BITS_TO_*`, `LE_BITS_CLEARED_TO_*`, `SET_BITS_TO_LE_*`, `N_BYTE_ALIGMENT`, and flag macros `TEST_FLAG`, `SET_FLAG`, `CLEAR_FLAG`, `TEST_FLAGS`.

Control flow and integration: there is no runtime control flow. Descriptor, EFUSE, C2H, and register bitfield code uses these macros to extract or set fields from little-endian byte streams. `N_BYTE_ALIGMENT` is used by the SDIO receive initialization to align the receive-buffer array.

State and persistence: macros mutate caller-provided memory for `SET_BITS_TO_LE_*`; there is no standalone state. The macros are often used on hardware descriptor buffers, so writes become part of data sent to hardware or parsed from hardware.

Dependencies: includes Linux types and stddef. It assumes unaligned pointer casts are acceptable in the caller context, which can be architecture-sensitive.

Risks and test signals: `BIT_LEN_MASK_*` shifts by width minus bitlen, so a bit length of zero or greater than width must be avoided by callers. `SET_BITS_TO_LE_4BYTE` writes through `u32 *` rather than `__le32 *`, so endian and alignment assumptions are important. Tests should include descriptor field extraction/setting on little-endian buffers, alignment computations, and build coverage on architectures with stricter alignment rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/basic_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/cmd_osdep.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/cmd_osdep.h

Purpose: this header declares OS-dependent command/event queue initialization, cleanup, enqueue, and dequeue hooks for the Realtek command subsystem.

Important APIs/types/functions: prototypes include `rtw_init_cmd_priv`, `rtw_init_evt_priv`, `_rtw_free_evt_priv`, `_rtw_free_cmd_priv`, `_rtw_enqueue_cmd`, and `_rtw_dequeue_cmd`. The referenced types are `cmd_priv`, `evt_priv`, `__queue`, and `cmd_obj`, all provided by the broader driver includes.

Control flow and integration: this header has no implementation. `drv_types.h` includes it between `rtw_cmd.h` and the adapter definition, making these functions visible to core command-thread and event-thread setup/teardown code. The HAL files in this subset integrate indirectly through C2H work commands and firmware H2C command paths.

State and persistence: command and event state is owned by `struct adapter.cmdpriv` and `struct adapter.evtpriv`; this header only declares lifecycle operations for that state.

Dependencies: depends on prior declarations from `rtw_cmd.h`, queue helpers, and OS service types included by `drv_types.h`.

Risks and test signals: this header is small, but ordering matters because it uses incomplete driver types. Mismatched enqueue/dequeue locking semantics would affect C2H events, scan/join commands, and transmit aggregation requests. Tests should cover command/event init/free symmetry, enqueue/dequeue ordering, and C2H work submission from SDIO interrupt context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/cmd_osdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/drv_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/drv_types.h

Purpose: this is the central RTL8723BS driver type aggregation header. It pulls in the common Wi-Fi, MLME, xmit, recv, power, IO, security, EFUSE, event, cfg80211, and HAL headers and defines the top-level runtime objects.

Important APIs/types/macros: `struct registry_priv` stores module/registry configuration such as wireless mode, channel, power, HT/AMPDU, WMM/UAPSD, antenna, TX power, firmware power-save, and queue options. `struct dvobj_priv` represents the shared device object, including primary adapter, hardware locks, CAM cache, pipe mapping, IO error counters, power control, traffic stats, and `sdio_data`. `struct adapter` is the per-interface root object containing MLME, command/event, IO, xmit, recv, station, security, registry, EEPROM, HAL data, netdev, firmware readiness, removal/stop flags, and debug knobs. Macros include `GET_PRIMARY_ADAPTER`, `adapter_to_dvobj`, `adapter_to_pwrctl`, `RTW_CANNOT_IO/RX/TX`, and `myid`.

Control flow and integration: all HAL C files in this subset include `drv_types.h` directly or indirectly. HAL init reads registry options, stores HAL state through `HalData`, and checks adapter stop/removal flags. SDIO ops use `dvobj_priv.intf_data`; TX/RX paths use adapter xmit/recv substructures.

State and persistence: this header defines the in-memory persistence boundary for the driver. `adapter`, `dvobj_priv`, `registry_priv`, and substructures retain state across operations until interface teardown.

Dependencies: extremely broad, including Linux networking headers and most local Realtek subsystem headers. Include ordering is significant and can hide circular dependencies.

Risks and test signals: because this header couples most subsystems, small type changes have wide compile and behavioral impact. Tests should include full driver build, probe/remove, multi-interface assumptions, power transitions, TX/RX disable flags, and registry option combinations such as `wifi_spec`, `ant_num`, and TX power controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/drv_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/drv_types_sdio.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/drv_types_sdio.h

Purpose: this header defines the SDIO-specific device-interface data embedded in `dvobj_priv`.

Important APIs/types: `struct sdio_data` contains the SDIO function number, TX/RX block-mode flags, `block_transfer_len`, the kernel `struct sdio_func *func`, and an opaque `sys_sdio_irq_thd` pointer for the SDIO IRQ thread. The header includes Linux MMC SDIO function and ID headers.

Control flow and integration: there is no executable code. `drv_types.h` embeds `struct sdio_data intf_data` in `dvobj_priv`. `sdio_ops.c` uses `block_transfer_len` to round port transfers and `func` indirectly through device conversion. `rtl8723bs_interface_configure` maps SDIO output pipes in `dvobj_priv`, while lower-level SDIO probe code is expected to initialize `sdio_data`.

State and persistence: `sdio_data` persists for the lifetime of the device object and is shared by adapters attached to the same SDIO function. It stores host-transfer geometry used by all IO paths.

Dependencies: depends on Linux MMC SDIO core types. Consumers assume `func` is valid for firmware loading device lookup and SDIO command execution.

Risks and test signals: incorrect `block_transfer_len` leads to under/over-rounded RX/TX port transfers. IRQ-thread ownership and teardown must be coordinated with adapter stop/removal. Tests should cover block sizes from the host controller, probe/remove, runtime suspend/resume, and concurrent TX/RX access through shared `dvobj_priv.intf_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/drv_types_sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_btcoex.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_btcoex.h

Purpose: this header declares the HAL Bluetooth coexistence interface used by RTL8723B Wi-Fi code to coordinate shared antenna/RF/power behavior with Bluetooth.

Important APIs/types/macros: `struct bt_coexist` stores whether BT exists, antenna count, BT chip type, and initialization status. Notifications include `hal_btcoex_IpsNotify`, `LpsNotify`, `ScanNotify`, `ConnectNotify`, `MediaStatusNotify`, `SpecialPacketNotify`, `IQKNotify`, `BtInfoNotify`, `SuspendNotify`, and `HaltNotify`. Configuration/control APIs include `hal_btcoex_SetBTCoexist`, `SetPgAntNum`, `SetSingleAntPath`, `Initialize`, `PowerOnSetting`, `InitHwConfig`, `Handler`, `GetRaMask`, and power-mode helpers.

Control flow and integration: HAL init calls power-on and hardware-config functions; EFUSE parsing configures coexistence, antenna count, and single-antenna path; scan/join/IQK paths send notifications; C2H BT info events are forwarded from receive/interrupt handling; rate-mask updates subtract the BT coexistence RA mask.

State and persistence: runtime state lives in `hal_com_data.bt_coexist` plus additional implementation-private coexistence state outside this header. Parsed EFUSE values in `hal_com_data` drive initial BT coexistence configuration.

Dependencies: includes `drv_types.h`, which creates a heavy include cycle but gives all prototypes access to `struct adapter`.

Risks and test signals: coexistence callbacks are invoked from init, MLME transitions, C2H event paths, and calibration, so ordering and context matter. Missing or incorrect BT EFUSE parsing can select the wrong antenna path. Tests should cover BT-present and BT-absent boards, single/two antenna settings, scan/connect notifications, IQK notification pairing, C2H BT info handling, and rate-mask adjustment under BT activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_btcoex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com.h

Purpose: this header declares shared HAL helpers and common constants used by the RTL8723BS HAL, including descriptor rates, queue selection, firmware page size, channel-plan helpers, pipe mapping, chip info, C2H, and generic hardware-variable accessors.

Important APIs/types/macros: it includes version, power/PHY/register headers and defines descriptor rates `DESC_RATE*`, `HDATA_RATE`, media status, `MAX_DLFW_PAGE_SIZE`, TX queue selection flags `TX_SELE_HQ/LQ/NQ/EQ`, and `PageNum_128`. Function declarations include `rtw_hal_data_init/deinit`, `dump_chip_info`, `hal_com_config_channel_plan`, `HAL_IsLegalChannel`, `MRateToHwRate`, `HalSetBrateCfg`, `Hal_MappingOutPipe`, `hal_init_macaddr`, C2H helpers, `SetHwReg`, `GetHwReg`, `GetHalDefVar`, and `SetHalODMVar`.

Control flow and integration: the HAL init, PHY, xmit, and SDIO ops code use these declarations as common glue. Queue-selection flags drive SDIO endpoint/page setup; rate conversion feeds TX descriptors; generic `SetHwReg`/`GetHwReg` are fallbacks for chip-specific dispatchers; C2H helpers are used by SDIO interrupt processing.

State and persistence: no state is stored here. Constants influence persistent hardware state by controlling firmware download paging, TX descriptor rates, and queue mappings.

Dependencies: pulls in multiple HAL headers, so it is a central include dependency. It assumes descriptor/register constants from included headers are consistent with RTL8723B hardware.

Risks and test signals: changing common rate constants or queue flags affects TX descriptors and SDIO pipe mapping. Tests should include rate conversion correctness, channel-plan resolution with EFUSE and registry inputs, pipe mapping for one/two/three output queues, generic hardware-variable fallback behavior, and C2H event read/clear handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_h2c.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_h2c.h

Purpose: this header defines shared host-to-controller command payload lengths and the reserved-page location structure used when communicating with RTL8723B firmware.

Important APIs/types/macros: constants include `H2C_RSVDPAGE_LOC_LEN`, `H2C_MEDIA_STATUS_RPT_LEN`, `H2C_PWRMODE_LEN`, `H2C_PSTUNEPARAM_LEN`, `H2C_MACID_CFG_LEN`, and `H2C_RSSI_SETTING_LEN`. `struct rsvdpage_loc` records firmware reserved-page offsets for probe response, PS-Poll, null data, QoS null, and BT QoS null frames.

Control flow and integration: this header has no code. `rtl8723b_hal_init.c` includes it for firmware variable initialization and H2C-related operations. `sdio_halinit.c` includes it for BT/WLAN calibration H2C command use. Reserved-page download and firmware power-mode helpers rely on these sizes and locations when packaging commands.

State and persistence: H2C payloads are transient command buffers sent to firmware. Reserved-page locations may be cached while firmware is running, but the header only defines shape and sizes.

Dependencies: no heavy dependencies beyond local include ordering. It is intentionally small and common to HAL command code.

Risks and test signals: payload length constants must match firmware expectations exactly; off-by-one command buffers can corrupt adjacent H2C boxes or be ignored. Tests should verify firmware accepts power mode, PS tune, media status, MACID config, and reserved-page commands, especially after firmware download and after low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_h2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_phycfg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_phycfg.h

Purpose: this header defines shared PHY configuration types and declarations for TX power by rate, TX power limits, RF path register definitions, and channel-plan-to-regulation conversion.

Important APIs/types/macros: path constants `PathA` through `PathD`, `enum rate_section` (`CCK`, `OFDM`, `HT_MCS0_MCS7`), `MAX_POWER_INDEX`, and power-limit regulation IDs are defined. `struct bb_register_def` maps per-RF-path BB register addresses for RF interface software control, output, enable, 3-wire offset, HSSI parameter, and LSSI readback. Function declarations cover TX power base/rate index lookup, storing/configuring TX power by rate, setting power by path/rate array, power-limit initialization/conversion, `phy_get_tx_pwr_lmt`, tracking offsets, and `Hal_ChannelPlanToRegulation`.

Control flow and integration: `rtl8723b_phycfg.c` fills `hal_com_data.PHYRegDef` using this struct, then callers use it for RF serial operations. TX power parsing in `rtl8723b_hal_init.c` populates `hal_com_data`; PHY functions declared here consume that data to program hardware power indexes.

State and persistence: the declarations operate on `hal_com_data` power tables and RF register definitions. Actual persistent runtime values are held in the adapter HAL data and hardware registers.

Dependencies: depends on `struct adapter`, channel-width enums, and RF path/rate constants from surrounding driver headers.

Risks and test signals: RF path argument ordering must match implementations; `PHY_GetTxPowerTrackingOffset` declaration uses `Rate, RFPath` while some callers pass `RFPath, Rate` in the implementation context, which deserves compile/signature review. Tests should validate per-rate power indexes, regulatory limits, channel-plan regulation mapping, and RF path A/B register definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_phycfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_reg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_reg.h

Purpose: this header defines the shared MAC, TXDMA/RXDMA, protocol, EDCA, WMAC, security, power, EFUSE, firmware, and SDIO local register map and bit masks used by RTL8723BS HAL code.

Important APIs/types/macros: register constants cover system configuration (`REG_SYS_FUNC_EN`, `REG_APS_FSMCO`, `REG_MCUFWDL`, `REG_SYS_CFG`), MAC top (`REG_CR`, `REG_TRXDMA_CTRL`, `REG_HIMR/HISR`), TXDMA/RXDMA (`REG_RQPN`, `REG_AUTO_LLT`, `REG_RXDMA_AGG_PG_TH`), protocol (`REG_FWHW_TXQ_CTRL`, `REG_RRSR`, `REG_MACID_SLEEP`), EDCA/beacon/TSF registers, WMAC filters/CAM/security, EFUSE aliases, response rates, RCR bits, firmware download bits (`MCUFWDL_RDY`, `FWDL_ChkSum_rpt`, `WINTINI_RDY`, `RAM_DL_SEL`), queue mapping helpers, and SDIO device IDs/local registers/interrupt masks.

Control flow and integration: every HAL C file in this subset uses these constants for hardware access. SDIO ops rely on pseudo-address masks/device IDs; init relies on power, DMA, beacon, and interrupt masks; TX/RX paths use queue and RCR constants; firmware download uses MCUFWDL bits.

State and persistence: the header names hardware state but stores none. Its constants define how driver memory state maps to persistent hardware registers during a powered session.

Dependencies: requires `BIT`/`BIT0` style macros from included contexts. It is included via `hal_com.h` and other HAL headers.

Risks and test signals: register-map errors affect low-level hardware behavior and are hard to diagnose. The SDIO address-domain masks must match `_cvrt2ftaddr` logic. Tests should cover firmware download status bits, LLT init, TX page allocation, RX filter maps, beacon timing, CAM writes, SDIO interrupt clear behavior, and local register access in both power-on and power-save modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_data.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_data.h

Purpose: this header defines the RTL8723B HAL private state stored behind `adapter->HalData`, including firmware, chip identity, PHY/channel, EFUSE/EEPROM, TX power, RF, beacon, antenna, SDIO, dynamic-management, ODM, and BT coexistence state.

Important APIs/types/macros: enums define multi-function support, polarity, regulator mode, and AMPDU burst mode. `struct dm_priv` stores dynamic-management and calibration state, including RSSI/PWDB smoothing, thermal values, IQK backups, Tx power tracking state, EDCA turbo history, and `INIDATA_RATE[32]`. `struct hal_com_data` is the main state object, with fields for version, firmware version/signature, current channel/bandwidth/side channel, basic rates, receive config, RF chip/path/package, EEPROM-derived customer/regulatory/BT/power/thermal/crystal data, TX power tables and limits, RF register definitions, channel register cache, beacon register shadows, antenna path/diversity, power-down, SDIO endpoint/free-page/OQT/RX FIFO state, ODM private state, BT coexistence, and interrupt masks. Macros include `GET_HAL_DATA` and RF path helpers.

Control flow and integration: almost every file in the subset reads or writes this structure. Firmware download fills firmware fields; chip-version and EFUSE parsing fill identity and calibration inputs; PHY config consumes RF/channel/TX power fields; SDIO init populates endpoint and FIFO state; TX/RX paths consume receive config, rate-control, and SDIO page state.

State and persistence: this is the central in-memory persistence object for one adapter. It persists from HAL data allocation through adapter teardown and mirrors selected hardware state so transitions can restore or update registers safely.

Dependencies: includes ODM precompilation headers, BT coexistence, and SDIO HAL declarations. Many fields depend on constants from RF, TX power, EFUSE, and SDIO headers.

Risks and test signals: field coupling is high; uninitialized fields can affect firmware commands, PHY power, SDIO resource accounting, and RX filters. Tests should include default-value initialization, EFUSE autoload success/failure, firmware download, channel/bandwidth switching, TX power calculations, free-page/OQT accounting, BT coexistence, and teardown/reinit cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_data.h -->
