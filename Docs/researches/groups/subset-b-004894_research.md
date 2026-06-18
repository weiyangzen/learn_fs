<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.h

## Purpose
Defines the RTL8723B power transition scripts consumed by the rtlwifi power-sequence executor. The file maps high-level NIC transitions such as power on, radio off, suspend, resume, hardware power down, and LPS enter/leave into ordered `struct wlan_pwr_cfg` register commands.

## Important APIs, Types, And Functions
- Includes `../pwrseqcmd.h` for `struct wlan_pwr_cfg`, command IDs, base-address selectors, cut/fab/interface masks, and delay constants.
- Step-count macros include `RTL8723B_TRANS_CARDEMU_TO_ACT_STEPS`, `RTL8723B_TRANS_ACT_TO_CARDEMU_STEPS`, `RTL8723B_TRANS_CARDEMU_TO_SUS_STEPS`, `RTL8723B_TRANS_CARDEMU_TO_PDN_STEPS`, `RTL8723B_TRANS_ACT_TO_LPS_STEPS`, `RTL8723B_TRANS_LPS_TO_ACT_STEPS`, and `RTL8723B_TRANS_END_STEPS`.
- Command-list macros include `RTL8723B_TRANS_CARDEMU_TO_ACT`, `RTL8723B_TRANS_ACT_TO_CARDEMU`, `RTL8723B_TRANS_CARDEMU_TO_SUS`, `RTL8723B_TRANS_SUS_TO_CARDEMU`, card-disable/card-enable aliases, `RTL8723B_TRANS_CARDEMU_TO_PDN`, `RTL8723B_TRANS_PDN_TO_CARDEMU`, `RTL8723B_TRANS_ACT_TO_LPS`, `RTL8723B_TRANS_LPS_TO_ACT`, and `RTL8723B_TRANS_END`.
- Extern flow arrays include `rtl8723B_power_on_flow`, `rtl8723B_radio_off_flow`, `rtl8723B_card_disable_flow`, `rtl8723B_card_enable_flow`, `rtl8723B_suspend_flow`, `rtl8723B_resume_flow`, `rtl8723B_hwpdn_flow`, `rtl8723B_enter_lps_flow`, and `rtl8723B_leave_lps_flow`.
- Public aliases such as `RTL8723_NIC_PWR_ON_FLOW`, `RTL8723_NIC_RF_OFF_FLOW`, `RTL8723_NIC_DISABLE_FLOW`, and `RTL8723_NIC_LPS_LEAVE_FLOW` provide chip-family names to the rest of the driver.

## Control Flow
This header has no executable functions. The control flow is the array order itself: each entry selects a register offset, hardware cut/fab/interface applicability, base address, command type, bit mask, and value. The power-sequence runner executes writes, polls, delays, and `PWR_CMD_END` in order. The active path releases isolation, disables suspend and HWPDN bits, polls power-ready and MAC-off bits, restores WLON reset, and configures GPIO9 wake interrupt wiring. The low-power entry path stops PCIe DMA, pauses transmit, polls transmit queues empty, gates BB/OFDM/CCK clocks, resets MAC TRX, and responds TxOK to the scheduler. The low-power exit path writes RPWM for SDIO/USB/PCIe, waits, restores TSF/BB/MAC clocks, and unpauses transmit.

## State And Persistence
The state is persisted in device registers and power islands, not in kernel memory. Key state includes MAC isolation, LDO and crystal ownership, WL suspend/HWPDN bits, WLON reset, PCIe DMA stop/start, transmit pause, baseband reset, GPIO wake interrupt enables, and SDIO local suspend state. The exported flow arrays are defined in the companion `pwrseq.c` and remain static kernel data for all devices using the module.

## Dependencies And Integration Points
The file depends on rtlwifi's generic power-sequence interpreter and is integrated by the RTL8723BE hardware init, suspend/resume, disable, and low-power code. The same macro set contains USB, SDIO, and PCIe masks even though this PCI driver primarily uses the PCIe entries. Register offsets correspond to RTL8723B MAC, SDIO local, and power-management registers defined elsewhere.

## Risks And Edge Cases
Step-count macros must match the macro bodies used by `pwrseq.c`; mismatches can overrun or truncate flow arrays. Polling commands can hang if firmware or hardware state machines do not reach the expected bit values. Interface masks are easy to regress because USB/SDIO/PCIe commands are mixed in the same sequence. Incorrect power ordering can leave RF on during disable, lose wake events, or break resume from LPS/suspend.

## Test Signals
Useful signals are successful probe power-on, RF on/off toggles, suspend/resume, runtime LPS entry/exit under traffic, no stuck polling during module load/unload, valid wake interrupt behavior on GPIO9, and no transmit queue stall after leaving LPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/reg.h

## Purpose
Provides the RTL8723BE register map, bit masks, descriptor/control constants, baseband register aliases, RF register masks, EFUSE definitions, interrupt masks, and wake-on-WLAN flags used across the chip-specific driver. It is the central symbolic contract between driver code and RTL8723BE hardware registers.

## Important APIs, Types, And Functions
- System and power registers: `REG_SYS_ISO_CTRL`, `REG_SYS_FUNC_EN`, `REG_APS_FSMCO`, `REG_SYS_CLKR`, `REG_RSV_CTRL`, `REG_RF_CTRL`, LDO/AFE/PLL controls, EFUSE registers, GPIO and LED configuration registers.
- MAC/queue registers: command/control registers, DMA queues, beacon/TBTT/TSF controls, EDCA parameters, retry limits, NAV controls, response rate sets, security CAM registers, and packet buffer selectors.
- Interrupt definitions: normal IMR/HISR bits such as `IMR_ROK`, `IMR_RDU`, `IMR_BEDOK`, `IMR_C2HCMD`, `IMR_HSISR_IND_ON_INT`, plus high-speed/system interrupt bits.
- Baseband aliases: `RFPGA0_*`, `ROFDM0_*`, `RCCK0_*`, AGC, IQ imbalance, CCK/OFDM counters, TXAGC registers such as `RTXAGC_A_RATE18_06`, and RF serial-interface masks such as `BLSSIREADADDRESS`.
- Generic masks and helpers: `MASKBYTE0`, `MASKBYTE1`, `MASKDWORD`, `RFREG_OFFSET_MASK`, `BIT`-based control fields, antenna constants, WOWLAN event and reason bits, and `EFUSE_SEL` helpers.

## Control Flow
There is no runtime control flow. Other files use these macros to perform register reads and writes through `rtl_read_*`, `rtl_write_*`, `rtl_get_bbreg`, `rtl_set_bbreg`, RF serial helpers, descriptor helpers, interrupt recognition, firmware download, and power sequencing. The header enables common code to express register operations symbolically instead of embedding numeric offsets in each path.

## State And Persistence
All constants address persistent hardware state. They cover power domains, firmware/8051 state, PCIe DMA engines, packet buffers, EFUSE contents, security CAM entries, TSF/beacon timers, dynamic management counters, BB/RF calibration state, and wake-on-WLAN status. The header itself persists no state.

## Dependencies And Integration Points
Included by RTL8723BE hardware, PHY, RF, firmware, TX/RX, software registration, and dynamic-management files. It also aligns with shared rtlwifi core abstractions that use `rtl_hal_cfg.maps[]` to translate generic rtlwifi register roles into chip-specific offsets. The definitions must match the vendor datasheet and the initialization arrays in `table.c`.

## Risks And Edge Cases
Wrong offsets or masks can silently corrupt unrelated hardware fields. Many masks are reused with partial-register operations, so width and shift mistakes can cause power, DMA, interrupt, RF, or security regressions. The file also contains broad legacy compatibility definitions; deleting apparently unused symbols can break chip-family shared code. WOWLAN and EFUSE definitions are especially sensitive because invalid values can persist across suspend or device reinitialization.

## Test Signals
Validation comes from successful module load, firmware download, interrupt recognition, TX/RX traffic, beacon operation in AP/IBSS modes, suspend/resume, RF calibration, EFUSE parsing, security offload, and wake-on-WLAN event handling. Static signals include compile coverage of every including file and sparse/build warnings for invalid masks or duplicate definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.c

## Purpose
Implements RTL8723BE RF6052 radio configuration and transmit-power programming. It adjusts RF channel bandwidth, CCK/OFDM TX power per RF path, regulatory/channel power limits, dynamic TX power tracking, and RF parameter loading from vendor table data.

## Important APIs, Types, And Functions
- Public APIs exported through `rf.h`: `rtl8723be_phy_rf6052_set_bandwidth`, `rtl8723be_phy_rf6052_set_cck_txpower`, `rtl8723be_phy_rf6052_set_ofdm_txpower`, and `rtl8723be_phy_rf6052_config`.
- Internal helpers: `rtl8723be_phy_get_power_base`, `_rtl8723be_get_txpower_writeval_by_regulatory`, `_rtl8723be_write_ofdm_power_reg`, and `_rtl8723be_phy_rf6052_config_parafile`.
- Uses `struct rtl_priv`, `struct rtl_phy`, `struct rtl_mac`, `struct rtl_efuse`, `struct bb_reg_def`, `enum radio_path`, `RF_CHNLBW`, `RF90_PATH_A/B`, `RF6052_MAX_TX_PWR`, `HT_CHANNEL_WIDTH_20`, and `HT_CHANNEL_WIDTH_20_40`.
- Integrates with dynamic management via `rtl8723be_dm_txpower_track_adjust`.

## Control Flow
Bandwidth changes update `rtlphy->rfreg_chnlval[0]` and write RF channel/bandwidth bits on path A. CCK power setup builds four-byte AGC words per RF path, changes behavior during scanning and by EEPROM regulatory mode, clamps each byte to `RF6052_MAX_TX_PWR`, applies thermal/power-tracking adjustment, then writes CCK AGC BB registers. OFDM setup first computes OFDM and MCS base power for path A/B, derives per-rate write values using regulatory mode and channel group, applies dynamic high-power and thermal adjustments, clamps bytes, and writes six rate-group registers per path. RF configuration sets total RF path count, enables RF serial interface state per path, loads RF tables with `rtl8723be_phy_config_rf_with_headerfile`, restores prior RF interface state, and fails if a table load fails.

## State And Persistence
The file mutates `rtlpriv->phy.rfreg_chnlval`, `rtlpriv->phy.num_total_rfpath`, BB TXAGC registers, RF channel/bandwidth registers, and RF serial-interface control registers. It consumes EEPROM/EFUSE regulatory and power-group data, current bandwidth/channel state, scanning state, dynamic high-power level, and thermal tracking output. Hardware register writes persist until channel/power changes, reset, suspend, or full reinitialization.

## Dependencies And Integration Points
Called from PHY channel/bandwidth and hardware initialization paths. Depends on register constants from `reg.h`, chip data from `def.h`, RF/PHY helpers from `phy.h`, dynamic-management code in `dm.h`, and RF table arrays selected by `rtl8723be_phy_config_rf_with_headerfile`. It also depends on shared rtlwifi BB/RF accessors and EFUSE fields initialized earlier in probe.

## Risks And Edge Cases
TX power calculations are packed byte-wise into 32-bit values; overflow, underflow, or missing clamps can program illegal power. Regulatory mode handling differs across EEPROM modes 0 to 3, so channel-group boundaries and customer power limits need careful review. Dynamic high-power subtraction can underflow unsigned packed words. RF path B is handled even though some hardware is 1T1R, so path-count setup must remain correct. Failed RF table loading must prevent partially initialized radio operation.

## Test Signals
Signals include correct association on 20 MHz and 40 MHz channels, sane TX power across channels 1 to 14 and regulatory modes, stable scans without excessive power, thermal power tracking logs, no RF init failure, no out-of-range TXAGC values, and throughput/RSSI behavior after channel switches and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.h

## Purpose
Declares the RTL8723BE RF6052 interface used by PHY and hardware initialization code, and defines the chip's maximum encoded TX power value.

## Important APIs, Types, And Functions
- `RF6052_MAX_TX_PWR` limits per-rate TX power bytes to `0x3f`.
- `rtl8723be_phy_rf6052_set_bandwidth(struct ieee80211_hw *hw, u8 bandwidth)` programs RF bandwidth bits.
- `rtl8723be_phy_rf6052_set_cck_txpower(struct ieee80211_hw *hw, u8 *ppowerlevel)` programs CCK TX AGC.
- `rtl8723be_phy_rf6052_set_ofdm_txpower(struct ieee80211_hw *hw, u8 *ppowerlevel_ofdm, u8 *ppowerlevel_bw20, u8 *ppowerlevel_bw40, u8 channel)` programs OFDM/HT TX AGC.
- `rtl8723be_phy_rf6052_config(struct ieee80211_hw *hw)` loads RF table configuration.

## Control Flow
The header has no control flow. It exposes the RF configuration hooks implemented in `rf.c` to the chip PHY code.

## State And Persistence
The declarations operate on `struct ieee80211_hw` and indirectly mutate persistent RF/BB registers, `rtl_priv` PHY state, and EFUSE-derived power behavior in the implementation.

## Dependencies And Integration Points
Included by `rf.c` and chip PHY/hardware code that needs RF bandwidth, power, or initialization hooks. It assumes `struct ieee80211_hw`, `u8`, and `bool` are available through the including rtlwifi headers.

## Risks And Edge Cases
Changing function signatures breaks the `rtl8723be` PHY integration. Changing `RF6052_MAX_TX_PWR` affects regulatory and thermal TX power clamping for every rate.

## Test Signals
Compile coverage of all includers, successful RF initialization, channel bandwidth switching, and TX power programming without register value overflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/sw.c

## Purpose
Registers the RTL8723BE PCI driver with rtlwifi and the kernel PCI/module core. It initializes software defaults, power-management settings, firmware loading, HAL operation callbacks, register maps, module parameters, PCI IDs, and module metadata.

## Important APIs, Types, And Functions
- Initialization helpers: `rtl8723be_init_aspm_vars`, `rtl8723be_init_sw_vars`, `rtl8723be_deinit_sw_vars`, `rtl8723be_get_btc_status`, and `is_fw_header`.
- HAL operation table `rtl8723be_hal_ops` wires rtlwifi callbacks for EEPROM, interrupts, hardware init/disable/suspend/resume, network type, QoS, beacon handling, rate tables, TX/RX descriptors, channel/RF operations, watchdog, security, BB/RF accessors, H2C firmware commands, BTC status, and firmware header detection.
- HAL configuration `rtl8723be_hal_cfg` maps generic rtlwifi register roles, EFUSE roles, CAM/security roles, interrupt bits, and rate constants to RTL8723BE register definitions.
- Module parameters include `swenc`, `debug_level`, `debug_mask`, `ips`, `swlps`, `fwlps`, `msi`, `aspm`, `disable_watchdog`, and `ant_sel`.
- PCI registration uses `rtl8723be_pci_ids`, `SIMPLE_DEV_PM_OPS`, `rtl_pci_probe`, `rtl_pci_disconnect`, and `module_pci_driver`.

## Control Flow
At module load, `module_pci_driver` registers a PCI driver for Realtek device `0xB723`. During probe, rtlwifi calls `rtl8723be_init_sw_vars`, which initializes Bluetooth coexistence hooks, dynamic-management defaults, transmit/receive configuration masks, interrupt masks, IPS/LPS/MSI/ASPM module settings, band and MAC/PHY mode, firmware buffer allocation, and asynchronous firmware request for `rtlwifi/rtl8723befw_36.bin`. Later rtlwifi invokes the `rtl8723be_hal_ops` callbacks for hardware bring-up, TX/RX, scanning, power, security, and teardown. Deinit frees the firmware buffer.

## State And Persistence
The file initializes persistent driver state in `rtl_priv`, `rtl_pci`, `rtl_mac`, `rtl_hal`, PHY, DM, PSC, and BT coexistence structures. It allocates `rtlhal.pfirmware` with `vzalloc`, records `max_fw_size`, sets interrupt masks and receive/transmit configs, stores module parameter values, and registers immutable HAL config tables. Firmware is requested asynchronously and stored until deinit.

## Dependencies And Integration Points
Depends on rtlwifi core, PCI support, shared RTL8723 common firmware/PHY/DM helpers, chip-specific hardware/PHY/DM/FW/TRX/LED/table modules, and Bluetooth coexistence ops. Kernel integration points are firmware loading, module parameters, PCI device matching, and PM callbacks.

## Risks And Edge Cases
Asynchronous firmware loading means hardware init must tolerate firmware not ready until the callback completes. Firmware buffer allocation failure aborts probe setup. Incorrect HAL op wiring can misroute descriptor handling, interrupts, or RF access. Register-map mistakes affect generic rtlwifi helpers. Module parameter defaults shape power saving and ASPM behavior, so changes can cause hangs, missed interrupts, higher power use, or resume failures. The firmware header check accepts signatures masked by `0xfff0`, so it must stay aligned with firmware format.

## Test Signals
Signals include module insertion/removal, PCI probe on `0xB723`, firmware request success and fallback naming behavior, hardware init through the HAL ops table, interrupt delivery, TX/RX traffic, suspend/resume, module parameter parsing, Bluetooth coexistence presence, and no leaks from repeated probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.c

## Purpose
Stores vendor-supplied RTL8723BE initialization tables for baseband, power-by-rate, RF radio path A, MAC registers, and AGC. These arrays are consumed during hardware/PHY/RF initialization instead of being generated algorithmically.

## Important APIs, Types, And Functions
- Baseband table: `RTL8723BEPHY_REG_1TARRAY` and `RTL8723BEPHY_REG_1TARRAYLEN`.
- Power-group table: `RTL8723BEPHY_REG_ARRAY_PG` and `RTL8723BEPHY_REG_ARRAY_PGLEN`.
- RF path table: `RTL8723BE_RADIOA_1TARRAY` and `RTL8723BE_RADIOA_1TARRAYLEN`.
- MAC table: `RTL8723BEMAC_1T_ARRAY` and `RTL8723BEMAC_1T_ARRAYLEN`.
- AGC table: `RTL8723BEAGCTAB_1TARRAY` and `RTL8723BEAGCTAB_1TARRAYLEN`.
- Uses `ARRAY_SIZE` to bind exported length symbols to the table contents.

## Control Flow
There is no executable control flow. Initialization code iterates these arrays as register/value pairs or vendor table commands. Some RF entries contain condition markers such as high-bit command words that the header-file parser interprets for chip cuts or modes before applying following register writes.

## State And Persistence
The arrays are static module data. When consumed, they program persistent MAC, baseband, AGC, RF, TX power, channel, gain, and calibration-related hardware registers. The arrays themselves are read-only in normal operation, although they are declared as mutable `u32`.

## Dependencies And Integration Points
Declared by `table.h` and used by chip PHY/RF helpers such as `rtl8723be_phy_config_rf_with_headerfile` and related MAC/BB table loading paths. Register offsets and values correspond to `reg.h` constants and the RTL8723BE vendor programming guide.

## Risks And Edge Cases
These opaque values are hardware-sensitive. Reordering, truncating, or editing values can break radio bring-up, calibration, AGC, channel operation, or regulatory power behavior. Length symbols must stay correct. Conditional RF table markers must remain in parser-compatible order. Because the values are magic register data, normal review cannot infer correctness without hardware testing or vendor reference comparison.

## Test Signals
Signals include successful BB/MAC/RF table load, stable association, expected RSSI and throughput, no RF calibration failures, no invalid register access warnings, correct TX power levels, and comparison against known-good register dumps after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.h

## Purpose
Declares the RTL8723BE vendor initialization table arrays and their length symbols for MAC, PHY, RF, AGC, and power-group programming.

## Important APIs, Types, And Functions
- Extern declarations for `RTL8723BEPHY_REG_1TARRAY`, `RTL8723BEPHY_REG_ARRAY_PG`, `RTL8723BE_RADIOA_1TARRAY`, `RTL8723BEMAC_1T_ARRAY`, and `RTL8723BEAGCTAB_1TARRAY`.
- Extern declarations for the matching `*_ARRAYLEN` symbols.
- Includes `<linux/types.h>` for `u32`.

## Control Flow
The header has no control flow. It exposes table data from `table.c` to chip initialization code.

## State And Persistence
The declarations reference static module arrays whose values are applied to hardware registers during initialization. The header itself stores no state.

## Dependencies And Integration Points
Included by `table.c`, `sw.c`, and PHY/hardware table-loading code. It is part of the boundary between opaque vendor register tables and the code that interprets them.

## Risks And Edge Cases
Signature or symbol-name changes break table loading at compile or link time. Missing length declarations can cause consumers to use stale sizes or hard-coded lengths. The arrays are mutable declarations, so accidental writes by future code would corrupt subsequent initialization.

## Test Signals
Compile/link success for RTL8723BE, successful PHY/RF/MAC initialization, and no unresolved symbols for table arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.c

## Purpose
Implements RTL8723BE transmit and receive descriptor handling for the PCI rtlwifi path. It maps mac80211 frames into hardware TX descriptors, parses RX descriptors and PHY status into `rtl_stats` and `ieee80211_rx_status`, handles early-mode aggregation metadata, command descriptors, descriptor ownership helpers, and TX queue polling.

## Important APIs, Types, And Functions
- RX path: `rtl8723be_rx_query_desc`, `_rtl8723be_query_rxphystatus`, and `_rtl8723be_translate_rx_signal_stuff`.
- TX path: `rtl8723be_tx_fill_desc`, `_rtl8723be_map_hwqueue_to_fwqueue`, `_rtl8723be_insert_emcontent`, and `rtl8723be_tx_fill_cmddesc`.
- Descriptor helpers: `rtl8723be_set_desc`, `rtl8723be_get_desc`, `rtl8723be_is_tx_desc_closed`, and `rtl8723be_tx_polling`.
- Uses `struct rtl_stats`, `struct ieee80211_rx_status`, `struct rtl_tcb_desc`, `struct rx_fwinfo_8723be`, `struct phy_status_rpt`, PCI DMA mapping, mac80211 header helpers, and the inline descriptor bit helpers from `trx.h`.

## Control Flow
TX frames are classified into firmware queues, TCB metadata is filled, optional early-mode bytes are pushed into the skb, the skb is DMA mapped, the descriptor is cleared, and first-segment fields are populated with rate, SGI/preamble, AMPDU, sequence, RTS/CTS, bandwidth/subcarrier, security type, queue selection, fallback limits, rate control, RDG, report settings, segment flags, DMA address, MAC ID, and multicast/broadcast flags. Command descriptors use a simpler beacon queue, 1 Mbps fixed rate, one segment, own bit set, and DMA address. RX parsing reads descriptor fields, classifies normal RX versus C2H report, marks CRC/ICV/decryption/HT/40 MHz/mac time fields for mac80211, handles robust management frame decryption flags, maps hardware rate to rate index, parses PHY status when present, and records TX report 2 MAC ID bitmaps when applicable.

## State And Persistence
The file mutates descriptor memory shared with the PCI device, DMA mappings for outgoing skbs, per-packet `rtl_stats`, mac80211 RX status, dynamic-management counters such as CFO tails and packet count, beacon query debug counters, and TX report descriptor fields. Hardware observes descriptor ownership and buffer addresses until rings recycle them.

## Dependencies And Integration Points
Integrated through `rtl8723be_hal_ops.fill_tx_desc`, `fill_tx_cmddesc`, `query_rx_desc`, `set_desc`, `get_desc`, `is_tx_desc_closed`, and `tx_polling` in `sw.c`. Depends on mac80211 frame helpers, rtlwifi PCI rings, rate mapping, PHY signal conversion helpers, security helpers, `reg.h`, `def.h`, `fw.h`, `dm.h`, and descriptor layout definitions in `trx.h`.

## Risks And Edge Cases
DMA mapping errors return without a descriptor, so callers must avoid queue corruption. Descriptor bit offsets must match hardware exactly. The RX signal path has separate CCK and OFDM calculations with signed conversions and percentage clamping. Robust management frame handling deliberately clears `RX_FLAG_DECRYPTED` for IEEE 802.11w frames even when hardware reports decrypted. Early-mode `skb_push` changes buffer layout and must match descriptor offsets. `rtl8723be_get_desc` lacks an explicit return assignment for some names and warns on unsupported descriptors, so HAL callers must use only supported names.

## Test Signals
Signals include TX under all access categories, management/beacon/command TX, AMPDU aggregation, encrypted traffic including CCMP/TKIP/WEP and robust management frames, RX RSSI/EVM reporting for CCK and OFDM/HT rates, wake packet debug logs, TX report handling, descriptor ring progress, and no DMA mapping or ownership stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.h

## Purpose
Defines RTL8723BE TX/RX descriptor sizes, bitfield accessors, early-mode metadata accessors, PHY status structures, descriptor structures, and TRX function prototypes.

## Important APIs, Types, And Functions
- Size constants: `TX_DESC_SIZE`, `TX_DESC_AGGR_SUBFRAME_SIZE`, `RX_DESC_SIZE`, `RX_DRV_INFO_SIZE_UNIT`, `TX_DESC_NEXT_DESC_OFFSET`, `USB_HWDESC_HEADER_LEN`, and `CRCLENGTH`.
- TX descriptor setters cover packet size, offset, BMC, HTC, segment flags, OWN, MAC ID, queue select, rate ID, security type, aggregation, RDG, fragmentation, AMPDU density, hardware sequence, rate/fallback, RTS/CTS, bandwidth, SGI, DMA buffer size/address, and next descriptor address.
- RX descriptor getters/setters cover packet length, CRC/ICV, driver-info size, shift, PHY status, software decrypt flag, OWN, MAC ID, aggregation, C2H report select, rate/MCS, HT, wake matches, SPLCP, bandwidth, TSF, buffer address, and TX report 2 bitmaps.
- Early-mode setters encode packet count and five length fields.
- Structures include `phy_rx_agc_info_t`, `phy_status_rpt`, `rx_fwinfo_8723be`, `tx_desc_8723be`, and `rx_desc_8723be`.
- Prototypes expose `rtl8723be_tx_fill_desc`, `rtl8723be_rx_query_desc`, descriptor get/set helpers, TX close check, polling, and command descriptor fill.

## Control Flow
The inline helpers perform little-endian bit extraction and replacement using `le32_get_bits`, `le32p_replace_bits`, `cpu_to_le32`, and `le32_to_cpu`. `clear_pci_tx_desc_content` clears only the first descriptor area up to `TX_DESC_NEXT_DESC_OFFSET`, preserving possible extended fields outside that range.

## State And Persistence
The helpers directly mutate or read descriptor memory shared with hardware. The packed descriptor and PHY status structures document hardware-provided memory layouts. Because descriptor rings are persistent DMA-visible structures, field correctness persists across queue ownership handoff until the ring entry is reused.

## Dependencies And Integration Points
Consumed by `trx.c` and rtlwifi PCI descriptor ring code. It depends on Linux endian helpers, bit macros, mac80211-facing TRX prototypes, and RTL8723BE hardware descriptor format. The structures also anchor RX PHY parsing and TX descriptor programming in the HAL ops table.

## Risks And Edge Cases
Bitfield C structures are for documentation and typed access only; portable behavior relies on the inline endian helpers. Any bit offset or mask change can break DMA descriptors. `USB_HWDESC_HEADER_LEN` is reused as a descriptor offset in this PCI driver, so renaming or changing it carelessly can affect TX layout. 64-bit DMA address fields exist in the structure but the helpers here set 32-bit addresses, so DMA mask assumptions matter.

## Test Signals
Compile coverage, descriptor dumps matching hardware documentation, TX/RX traffic, AMPDU and fragmented frames, 32-bit DMA address operation, RX PHY status parsing, and no endian or sparse warnings around packed/bitfield structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/Makefile

## Purpose
Builds the shared RTL8723 common rtlwifi object used by both RTL8723AE and RTL8723BE drivers.

## Important APIs, Types, And Functions
- `rtl8723-common-objs` lists `main.o`, `dm_common.o`, `fw_common.o`, and `phy_common.o`.
- `obj-$(CONFIG_RTL8723_COMMON) += rtl8723-common.o` hooks the composite object into Kbuild when the common config symbol is enabled.

## Control Flow
Kbuild compiles the listed objects and links them into `rtl8723-common.o` when `CONFIG_RTL8723_COMMON` is set. There is no runtime control flow.

## State And Persistence
The file affects build artifacts only: object files and the resulting kernel module or built-in object. It stores no runtime state.

## Dependencies And Integration Points
Integrated by the Linux kernel Kbuild system under the rtlwifi driver tree. Chip drivers select or depend on `CONFIG_RTL8723_COMMON` so shared DM, firmware, PHY, and module metadata code is available.

## Risks And Edge Cases
Removing an object from `rtl8723-common-objs` can create unresolved symbols in RTL8723AE/BE modules. Incorrect config gating can build chip drivers without shared helpers.

## Test Signals
Signals include `CONFIG_RTL8723_COMMON=m/y` builds, successful linking of RTL8723AE/BE, and no unresolved exported symbol errors for common helper functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.c

## Purpose
Provides shared RTL8723 dynamic-management initialization helpers for TX power, EDCA turbo, and dynamic baseband power saving.

## Important APIs, Types, And Functions
- `rtl8723_dm_init_dynamic_txpower` disables dynamic TX power and initializes last/current high-power level to `TXHIGHPWRLEVEL_NORMAL`.
- `rtl8723_dm_init_edca_turbo` resets EDCA turbo state and non-BE/read-load flags.
- `rtl8723_dm_init_dynamic_bb_powersaving` initializes `struct ps_t` CCA/RF states to max and clears minimum RSSI and initialization fields.
- All three functions are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
Each function obtains `struct rtl_priv` from `struct ieee80211_hw` and assigns default fields. There are no branches other than straightforward state initialization.

## State And Persistence
The functions mutate `rtlpriv->dm` and `rtlpriv->dm_pstable`. The values persist as dynamic-management baselines until watchdog or PHY code updates them during runtime.

## Dependencies And Integration Points
Included through `dm_common.h` by RTL8723AE/BE dynamic-management setup. It imports shared rtlwifi state from `../wifi.h` and level constants from the RTL8723AE DM header, reflecting code reuse between chip variants.

## Risks And Edge Cases
Because this common code uses constants from `rtl8723ae/dm.h`, enum or macro divergence between AE and BE can break BE behavior. Defaults shape later watchdog behavior; incorrect initial RF/CCA states can suppress power-saving transitions or TX power limits.

## Test Signals
Signals include successful driver init, dynamic-management watchdog transitions from known initial states, EDCA turbo behavior under traffic, and TX power level staying normal until later logic changes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.h

## Purpose
Declares shared RTL8723 dynamic-management initialization helpers.

## Important APIs, Types, And Functions
- `rtl8723_dm_init_dynamic_txpower(struct ieee80211_hw *hw)`.
- `rtl8723_dm_init_edca_turbo(struct ieee80211_hw *hw)`.
- `rtl8723_dm_init_dynamic_bb_powersaving(struct ieee80211_hw *hw)`.

## Control Flow
The header has no control flow; it provides prototypes for `dm_common.c`.

## State And Persistence
The declared functions initialize persistent runtime DM fields in `rtl_priv`.

## Dependencies And Integration Points
Included by chip-specific DM code for RTL8723AE and RTL8723BE. It assumes `struct ieee80211_hw` is available from the including rtlwifi headers.

## Risks And Edge Cases
Prototype changes break shared chip-specific callers and exported symbol users. Missing declarations can hide type mismatches in common DM setup.

## Test Signals
Compile coverage for AE/BE DM code and successful symbol resolution for the three common initialization functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.c

## Purpose
Implements shared RTL8723 firmware download, page writing, firmware-ready polling, and 8051 self-reset helpers for RTL8723AE and RTL8723BE.

## Important APIs, Types, And Functions
- `rtl8723_enable_fw_download` toggles MCU firmware download mode through `REG_SYS_FUNC_EN` and `REG_MCUFWDL`.
- `rtl8723_write_fw` pads firmware with `rtl_fill_dummy`, splits it into `FW_8192C_PAGE_SIZE` pages, and writes pages through `rtl_fw_page_write`.
- `rtl8723ae_firmware_selfreset` and `rtl8723be_firmware_selfreset` implement chip-specific 8051 reset sequences.
- `rtl8723_fw_free_to_go` waits for `FWDL_CHKSUM_RPT`, sets `MCUFWDL_RDY`, optionally resets BE firmware, and polls `WINTINI_RDY`.
- `rtl8723_download_fw` validates loaded firmware buffer, strips a firmware header when present, resets any existing firmware state, enables download, writes firmware, disables download, and waits for readiness.
- All public helpers are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
Firmware download starts by checking `rtlpriv->max_fw_size` and `rtlhal->pfirmware`, reading firmware header version/subversion, choosing max page count of 6 for AE or 8 for BE, optionally skipping the header, resetting the MCU if bit 7 of `REG_MCUFWDL` indicates an existing firmware state, enabling download mode, writing all full and remaining pages, disabling download mode, and polling readiness. Polling loops are bounded by the caller-provided max count and report errors on checksum or ready timeout.

## State And Persistence
The file mutates MCU control registers, firmware download status bits, 8051 reset state, and `rtlhal->fw_version`/`fw_subversion`. Firmware bytes are transferred from `rtlhal->pfirmware` into device memory and persist until hardware reset, firmware reset, or power loss.

## Dependencies And Integration Points
Used by RTL8723AE/BE firmware-specific code through `fw_common.h`. Depends on rtlwifi firmware helpers, register constants, `struct rtlwifi_firmware_header`, and chip-specific `is_fw_header` HAL op. Kernel firmware request and callback code populates `rtlhal->pfirmware` before this path runs.

## Risks And Edge Cases
`rtl8723_write_fw` only prints if page count exceeds `max_page` and continues, so oversized firmware relies on earlier size limits. `rtl8723_download_fw` returns 0 even after `rtl8723_fw_free_to_go` reports an error, while logging failure; callers must inspect behavior carefully. Header stripping depends on chip-specific signature checks. Reset sequences differ between AE and BE, and timing/polling constants are hardware-sensitive.

## Test Signals
Signals include firmware version logs, successful checksum report, `WINTINI_RDY` polling success, working H2C commands after download, recovery when firmware was already loaded, and failure-path logs for missing firmware, bad checksum, or ready timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.h

## Purpose
Declares shared RTL8723 firmware control constants, firmware version identifiers, H2C command IDs for RTL8723BE, and firmware helper prototypes.

## Important APIs, Types, And Functions
- Register and status constants: `REG_SYS_FUNC_EN`, `REG_MCUFWDL`, `REG_RSV_CTRL`, `REG_HMETFR`, `FW_8192C_PAGE_SIZE`, `FW_8723A_POLLING_TIMEOUT_COUNT`, `FW_8723B_POLLING_TIMEOUT_COUNT`, `FW_8192C_POLLING_DELAY`, `MCUFWDL_RDY`, `FWDL_CHKSUM_RPT`, and `WINTINI_RDY`.
- `enum version_8723e` distinguishes test/normal UMC and SMIC chip cuts for RTL8723A/B.
- `enum rtl8723be_cmd` names H2C commands for reserved pages, join report, scan, keep-alive, disconnect decision, offloads, power modes, P2P power save, wake-on-WLAN, RSSI report, and rate-adaptive mask.
- Prototypes expose firmware self-reset, download-mode enable, page writing, free-to-go polling, and full firmware download.

## Control Flow
The header has no control flow. It supplies constants and declarations used by firmware command/download implementations.

## State And Persistence
The declared helpers mutate firmware control registers, firmware readiness bits, and device-resident firmware state. H2C command IDs define persistent firmware ABI values.

## Dependencies And Integration Points
Included by RTL8723AE/BE firmware and software registration code. The H2C enum must match firmware expectations, while the register constants must match chip hardware.

## Risks And Edge Cases
Changing command IDs breaks host-to-firmware ABI compatibility. Polling timeout changes can make firmware load flaky or slow. Register bit definitions overlap with chip reset behavior, so incorrect values can leave the MCU stuck.

## Test Signals
Compile coverage, firmware download success, H2C command acceptance for power and rate control, WOWLAN command behavior, and readiness polling within expected timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/main.c

## Purpose
Provides module metadata for the shared RTL8723 common routines object.

## Important APIs, Types, And Functions
- Includes `../wifi.h` and `<linux/module.h>`.
- Module metadata declares Realtek and Larry Finger authorship, GPL license, and description for RTL8723AE/RTL8723BE common PCI wireless routines.

## Control Flow
There is no executable control flow. The file contributes metadata to the linked `rtl8723-common` object.

## State And Persistence
No runtime state is created. Metadata persists in the module image and can be observed through kernel module tooling.

## Dependencies And Integration Points
Built by `rtl8723com/Makefile` into `rtl8723-common.o`. It integrates with kernel module metadata infrastructure and complements exported helper symbols from the other common files.

## Risks And Edge Cases
Incorrect license metadata can affect GPL-only symbol access. Misleading description or author data is low runtime risk but impacts module identification.

## Test Signals
Successful module build/link and expected metadata from `modinfo` when built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.c

## Purpose
Implements shared RTL8723 PHY helpers for BB register access, RF serial access, TX power conversion, RF register definition initialization, channel-switch command construction, IQ calibration matrix application, register backup/restore, ADDA path control, calibration MAC settings, path standby, and PI mode switching.

## Important APIs, Types, And Functions
- Register access: `rtl8723_phy_query_bb_reg`, `rtl8723_phy_set_bb_reg`, `rtl8723_phy_rf_serial_read`, and `rtl8723_phy_rf_serial_write`.
- Utility/setup: `rtl8723_phy_txpwr_idx_to_dbm`, `rtl8723_phy_init_bb_rf_reg_def`, and `rtl8723_phy_set_sw_chnl_cmdarray`.
- Calibration: `rtl8723_phy_path_a_fill_iqk_matrix`, `rtl8723_save_adda_registers`, `rtl8723_phy_save_mac_registers`, `rtl8723_phy_reload_adda_registers`, `rtl8723_phy_reload_mac_registers`, `rtl8723_phy_path_adda_on`, `rtl8723_phy_mac_setting_calibration`, `rtl8723_phy_path_a_standby`, and `rtl8723_phy_pi_mode_switch`.
- Uses `struct rtl_priv`, `struct rtl_phy`, `struct bb_reg_def`, `struct swchnlcmd`, `enum radio_path`, `enum wireless_mode`, and many BB/RF register constants.

## Control Flow
BB access helpers read/modify/write selected bit fields using `calculate_bit_shift`. RF serial read programs the LSSI read address and edge, waits 120 microseconds, selects PI or non-PI readback register, and returns RF data. RF serial write packs 8-bit offset plus 20-bit data into the three-wire register. RF register definition initialization fills the `rtlphy->phyreg_def[]` table for paths A through D. Channel command setup bounds-checks the command table before writing one entry. IQK matrix fill applies signed calibration results to TX/RX IQ imbalance registers unless no final candidate exists or TX-only mode is requested. Backup/restore helpers snapshot and restore ADDA/MAC registers. ADDA setup differs for RTL8723AE and RTL8723BE hardware type.

## State And Persistence
The file mutates BB/RF hardware registers, RF definition tables in `rtlphy`, calibration backup arrays supplied by callers, and command-table entries. Calibration and RF serial writes persist in hardware until reset, reload, or channel/calibration changes.

## Dependencies And Integration Points
Used by both RTL8723AE and RTL8723BE PHY code. It depends on `phy_common.h`, rtlwifi BB/RF register accessors, RTL8723AE register constants for shared aliases, and chip-specific hardware type checks. Several functions are exported with `EXPORT_SYMBOL_GPL` for chip modules.

## Risks And Edge Cases
`RT_CANNOT_IO(hw)` is currently defined as false, so IO-suppression paths are dead unless that macro changes. RF serial timing and bit packing are hardware-sensitive. RF definition table initialization must match every path's register aliases before RF operations run. IQK math sign-extends 10-bit values manually; mistakes affect calibration quality. Channel command setup silently fails on out-of-bounds indexes.

## Test Signals
Signals include successful BB/RF reads and writes, RF initialization on both AE and BE, channel switching command execution, IQK calibration pass/fail behavior, restored register snapshots after calibration, stable RSSI/EVM after PI mode switches, and no warnings from null or oversized switch-command tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.h

## Purpose
Declares shared RTL8723 PHY helper APIs and the channel-switch command structure used by chip-specific PHY code.

## Important APIs, Types, And Functions
- `RT_CANNOT_IO(hw)` currently expands to `false`.
- `enum swchnlcmd_id` defines channel-switch command opcodes: end, set TX power, BB write, port writes of several widths, and RF write.
- `struct swchnlcmd` stores command ID, two parameters, and millisecond delay.
- Prototypes cover BB register access, RF serial read/write, TX power index conversion, RF register definition initialization, channel-command setup, IQK matrix fill, ADDA/MAC save/restore, ADDA path enable, calibration MAC settings, path A standby, and PI mode switching.

## Control Flow
The header has no executable flow. Its enum and structure define the command language consumed by chip-specific channel-switch logic.

## State And Persistence
Declared functions operate on hardware BB/RF/MAC registers, `rtlphy->phyreg_def`, caller-provided backup arrays, and switch-command arrays. The header itself persists no state.

## Dependencies And Integration Points
Included by RTL8723AE/BE PHY code and common implementation. It is the shared ABI for PHY operations between chip modules and `rtl8723-common`.

## Risks And Edge Cases
Changing enum values or `struct swchnlcmd` layout can break channel-switch command tables. The `RT_CANNOT_IO` macro currently disables no IO; changing it affects all BB/RF access behavior. Prototype drift breaks exported common helper usage.

## Test Signals
Compile coverage for AE/BE PHY code, successful channel switching, RF register access, IQ calibration, and no ABI mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/Makefile

## Purpose
Builds the RTL8821AE rtlwifi chip driver composite object.

## Important APIs, Types, And Functions
- `rtl8821ae-objs` lists chip modules: `dm.o`, `fw.o`, `hw.o`, `led.o`, `phy.o`, `pwrseq.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`.
- `obj-$(CONFIG_RTL8821AE) += rtl8821ae.o` hooks the composite driver into Kbuild.

## Control Flow
Kbuild compiles and links the listed objects when `CONFIG_RTL8821AE` is enabled. Runtime control flow is provided by the linked C files, not the Makefile.

## State And Persistence
This file affects build artifacts only. It determines which object files are linked into the driver module or built-in object.

## Dependencies And Integration Points
Integrated with the Linux kernel Kbuild system and the parent rtlwifi Makefiles/Kconfig. The listed objects provide the HAL, firmware, PHY/RF, power sequence, table, LED, dynamic management, and TX/RX pieces of the RTL8821AE driver.

## Risks And Edge Cases
Omitting an object can remove required callbacks or produce unresolved symbols. Incorrect config gating can prevent the PCI ID driver from building. Object order usually matters less for relocatable links, but missing support files breaks module functionality.

## Test Signals
Signals include `CONFIG_RTL8821AE=m/y` build success, module link success, expected object inclusion, and no unresolved symbols for HAL operations or table data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/def.h

## Purpose
Defines RTL8821AE/RTL8812AE chip constants for rates, chip version decoding, board capabilities, RF and power states, PCI interface selection, descriptor queue selectors, CCK PHY status, and firmware H2C command descriptors.

## Important APIs, Types, And Functions
- Rate constants cover CCK, OFDM, HT MCS0 to MCS15, VHT 1SS/2SS/3SS MCS0 to MCS9, SG variants, and `MGN_UNKNOWN`.
- Hardware limits and channel constants include `WIFI_NAV_UPPER_US`, `HAL_92C_NAV_UPPER_UNIT`, `MAX_RX_DMA_BUFFER_SIZE`, `MAX_RX_DMA_BUFFER_SIZE_8812`, and primary channel offset values.
- Chip identity constants and masks include `CHIP_8812`, `CHIP_8821`, `NORMAL_CHIP`, RF type bits, vendor/cut bits, `IC_TYPE_MASK`, `RF_TYPE_MASK`, `CUT_VERSION_MASK`, and extraction helpers such as `GET_CVID_IC_TYPE`.
- Version helpers include `IS_1T1R`, `IS_1T2R`, `IS_2T2R`, `IS_8812_SERIES`, `IS_8821_SERIES`, and vendor/cut checks for 8812A and 8821A.
- Enums define `version_8821ae`, `vht_data_sc`, `board_type`, `rf_optype`, `rf_power_state`, `power_save_mode`, `power_polocy_config`, `interface_select_pci`, and `rtl_desc_qsel`.
- Structures define `phy_sts_cck_8821ae_t` and `h2c_cmd_8821ae`.

## Control Flow
The header has no executable control flow. Its macros are used by chip detection, rate mapping, descriptor construction, PHY status parsing, firmware command construction, and feature selection code throughout the RTL8821AE driver.

## State And Persistence
The values encode persistent hardware and firmware ABI meanings: chip version bits, RF path capabilities, board options such as external PA/LNA/TRSW and Bluetooth presence, power state labels, descriptor queue selectors, and H2C command buffer layout. The header itself stores no mutable state.

## Dependencies And Integration Points
Included by RTL8821AE driver components such as software registration, hardware init, firmware, PHY/RF, dynamic management, and TRX code. It aligns driver-visible constants with mac80211 rates, RTL8821/8812 hardware version registers, firmware H2C ABI, and descriptor queue selection.

## Risks And Edge Cases
Chip-version helper macros depend on masks and bit values matching hardware. A bad helper can select the wrong RF path count, board capabilities, or firmware flow. Queue selector constants must match descriptor hardware. The `power_polocy_config` spelling is part of the local ABI and should not be casually renamed. Rate constants must remain compatible with firmware/rate-adaptive tables.

## Test Signals
Signals include correct detection of 8812 versus 8821, RF type and chip cut logging, successful VHT/HT rate operation, correct queue selection for TX descriptors, firmware H2C command handling, board-type feature behavior for external front-end components, and compile coverage of all includers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/def.h -->
