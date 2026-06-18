# Research: subset-b-004893

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/trx.h

## Purpose
Defines the RTL8723E PCI transmit and receive descriptor layout used by the rtl8723ae driver. It is a hardware contract header: descriptor sizes, bitfield setters/getters, packed descriptor structures, RX PHY status metadata, and the exported TX/RX descriptor operation prototypes used by the PCI queue layer.

## Important APIs, Types, And Functions
The inline setters populate TX descriptor words for packet size, offset, ownership, MAC id, queue selector, security type, sequence number, RTS/CTS control, fixed TX rate, bandwidth, short GI, retry fallback limits, buffer size, DMA buffer address, and next descriptor address. RX accessors decode length, CRC/ICV errors, driver-info size, PHY status, software decrypt flag, aggregation flags, MCS/rate, HT flag, short preamble, bandwidth, TSF, and DMA buffer address. `clear_pci_tx_desc_content()` zeroes descriptor content up to the hardware next-descriptor offset. `struct tx_desc_8723e`, `struct rx_desc_8723e`, and `struct rx_fwinfo_8723e` document the packed hardware bit layout. The prototypes bind to implementation functions such as `rtl8723e_tx_fill_desc()`, `rtl8723e_rx_query_desc()`, `rtl8723e_set_desc()`, `rtl8723e_get_desc()`, `rtl8723e_is_tx_desc_closed()`, `rtl8723e_tx_polling()`, and `rtl8723e_tx_fill_cmddesc()`.

## Control Flow
The file itself has no runtime control loop; callers allocate descriptors in TX/RX rings, clear or update fields through these inline helpers, and then hand ownership to or from hardware by toggling OWN bits. TX preparation fills descriptor metadata and DMA addresses before polling the queue; RX completion reads fields to build `rtl_stats` and `ieee80211_rx_status` and then returns buffers to hardware.

## State And Persistence
Descriptor state is persistent only while a DMA ring entry is live. The packed C bitfields mirror little-endian hardware words but actual safe access is through `__le32` helpers, which preserve endian correctness. Ownership bits synchronize software and NIC use of the same ring slots.

## Dependencies And Integration Points
Depends on Linux bit helpers (`GENMASK`, `BIT`, `le32_get_bits`, `le32p_replace_bits`) and rtlwifi/mac80211 data types. It integrates with rtl8723ae PCI TX/RX implementation files, the common rtlwifi queue code, and DMA-mapped skb buffers.

## Risks
The main risk is descriptor contract drift: wrong bit masks, byte order, or offsets can corrupt DMA, leak ownership, or misclassify RX frames. The packed bitfield structures are documentation-like and compiler-sensitive; the inline little-endian helpers are the safer operational API. Descriptor clearing must not erase the next descriptor pointer past `TX_DESC_NEXT_DESC_OFFSET`.

## Test Signals
Useful signals are successful TX completion without stuck OWN bits, RX frames with correct length/status/rate/bandwidth, no DMA mapping warnings, no malformed skb lengths, correct encryption status reporting, and stable operation under aggregation, RTS/CTS, fixed-rate management TX, and ring wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/Makefile

## Purpose
Builds the RTL8723BE PCI wireless driver object as `rtl8723be.o` when `CONFIG_RTL8723BE` is enabled. It lists the per-device compilation units that implement dynamic management, firmware commands, hardware control, LEDs, PHY/RF, power sequencing, mac80211 glue, tables, and TX/RX descriptors.

## Important APIs, Types, And Functions
There are no C APIs in this file. The important build contract is `rtl8723be-objs`, containing `dm.o`, `fw.o`, `hw.o`, `led.o`, `phy.o`, `pwrseq.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`, and `obj-$(CONFIG_RTL8723BE) += rtl8723be.o`.

## Control Flow
Kbuild aggregates the listed objects into one module/built-in driver object. Link order is mostly conventional, but it matters for symbol resolution within the final object and for ensuring all device operation callbacks referenced by `sw.o` are present.

## State And Persistence
No runtime state is maintained. Persistent behavior is the build composition of the driver.

## Dependencies And Integration Points
Integrates with the kernel Kbuild system and the parent rtlwifi Realtek directory. It assumes adjacent source files and shared rtlwifi common objects supply all referenced symbols.

## Risks
Omitting an object silently removes whole driver capabilities at link time. Adding a source file without listing it here causes unresolved symbols or missing callback behavior. The trailing backslash style should remain valid Kbuild syntax.

## Test Signals
Build `CONFIG_RTL8723BE=m` and `=y`, verify `rtl8723be.o` links, and load the module on supported PCI IDs. A strong signal is that probe reaches `rtl8723be_hw_init()` and mac80211 registration from `sw.o` without unresolved symbol failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/def.h

## Purpose
Provides small RTL8723BE constants shared across descriptor, hardware, and PHY code: channel offset values, RX queue id, chip-version bits, queue selector encodings, and descriptor rate ids.

## Important APIs, Types, And Functions
`enum rtl_desc_qsel` maps software traffic categories and special queues to descriptor queue selector values such as BK, BE, VI, VO, beacon, high, management, and command. `enum rtl_desc8723e_rate` assigns hardware descriptor rate ids for CCK, OFDM, and HT MCS0-MCS15 rates. Macros such as `CHIP_8723B`, `NORMAL_CHIP`, `CHIP_VENDOR_SMIC`, `EXT_VENDOR_ID`, and `RX_MPDU_QUEUE` are consumed by chip detection, PCI ring setup, and rate/power code.

## Control Flow
No direct control flow. These constants shape switch statements in TX descriptor filling, rate-mask construction, chip-version parsing, PHY TX-power programming, and channel-width handling.

## State And Persistence
No mutable state. The enum values are persistent ABI-like values between driver software and RTL8723BE hardware/firmware.

## Dependencies And Integration Points
Included by `dm.c`, `fw.c`, `hw.c`, `phy.c`, and descriptor code. Rate ids are shared with PHY TX-power routines and TX descriptor construction, so changes affect both firmware rate adaptation and direct BB TXAGC programming.

## Risks
Queue selector or rate-id changes are high risk because they alter the wire contract with descriptors and firmware. Chip bit masks must match `REG_SYS_CFG*` layout; bad masks can pick wrong board-specific paths or RF assumptions.

## Test Signals
Check correct queue mapping for AC traffic and management frames, valid rate reporting under CCK/OFDM/HT traffic, and chip-version logs identifying RTL8723B/NORMAL/SMIC attributes correctly during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/dm.c

## Purpose
Implements RTL8723BE dynamic-management logic run after hardware initialization and periodically from the driver watchdog. It adapts receive gain, CCK packet-detection thresholds, EDCA parameters, firmware RSSI reporting, rate masks, CFO/crystal tracking, thermal TX power tracking, and calibration triggers based on link state, RSSI, false alarms, traffic direction, power-save state, and Bluetooth coexistence.

## Important APIs, Types, And Functions
Public entry points are `rtl8723be_dm_init()`, `rtl8723be_dm_watchdog()`, `rtl8723be_dm_write_dig()`, `rtl8723be_dm_check_txpower_tracking()`, `rtl8723be_dm_init_rate_adaptive_mask()`, `rtl8723be_dm_txpower_track_adjust()`, and `rtl8723be_dm_set_tx_ant_by_tx_info()`/statistics hooks declared in `dm.h`. Important internals include `rtl8723be_dm_dig()` for initial-gain control, `rtl8723be_dm_false_alarm_counter_statistics()` for OFDM/CCK false-alarm accounting, `rtl8723be_dm_check_rssi_monitor()` for station RSSI aggregation and H2C RSSI reports, `rtl8723be_dm_refresh_rate_adaptive_mask()` for RA mask changes, `rtl8723be_dm_check_edca_turbo()` for BE EDCA tuning, `rtl8723be_dm_dynamic_atc_switch()` for CFO/XTAL and ATC toggling, and `rtl8723be_dm_txpower_tracking_callback_thermalmeter()` for thermal swing-table adjustment and IQK/LCK scheduling.

## Control Flow
Initialization sets driver-controlled DM mode, initializes common DIG/EDCA/BB power saving/dynamic TX power state, seeds OFDM/CCK swing indexes, thermal tracking, and crystal-cap/CFO state. The watchdog first verifies RF is on, firmware is not in power-save sleep, P2P PS is not holding the device asleep, and RF changes are not in progress. It then updates one-entry state, samples false alarms, updates RSSI minimums, adjusts DIG, EDCCA, CCK CCA threshold, rate masks, EDCA turbo, ATC/CFO state, thermal tracking, and finally clears beacon debug counters.

## State And Persistence
The code mutates `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->falsealm_cnt`, `rtlpriv->ra`, `rtlpriv->stats`, and pieces of `rtlhal`. Persistent state includes current/pre IGI, forbidden IGI and recovery counters, RSSI smoothed values, rate-adaptive state, thermal averages and base swing indexes, CFO tails/packet counters, crystal cap, ATC status, EDCA turbo state, and one-entry-only detection. Hardware state persists in BB/RF/MAC registers until overwritten by later DM iterations or reset.

## Dependencies And Integration Points
Depends on rtlwifi common DM helpers in `rtl8723com/dm_common.h`, BB/RF accessors, `fw.c` H2C command submission, `phy.c` TX-power/IQK/LC calibration, mac80211 link/opmode state, station RSSI lists protected by `entry_list_lock`, PCI/power locks, and Bluetooth coexistence callbacks. Rate-adaptive updates call the configured hardware op `update_rate_tbl()`.

## Risks
The watchdog writes live radio registers and must stay gated by RF/power-save state; running while firmware sleeps or RF is changing can race LPS/IPS. DIG thresholds can reduce sensitivity or cause false alarms if RSSI accounting is wrong. Thermal tracking uses swing-table bounds and signed deltas; bad EFUSE thermal data or index handling can over/under-drive TX power. EDCA turbo rewrites BE parameters based on traffic deltas and can hurt QoS. CFO/ATC crystal changes interact with Bluetooth coexistence and should not churn on noisy packet counts.

## Test Signals
Probe and associate while watching DIG, false-alarm, CCK CCA, and RSSI logs. Test low/high RSSI roaming, scan pause/resume, AP/adhoc station lists, power-save entry/exit, P2P PS, Bluetooth active/inactive, thermal changes, and sustained UL/DL traffic. Useful failures include stuck low throughput after EDCA changes, unstable RSSI near thresholds, repeated IQK/LCK triggers, firmware H2C RSSI errors, or lockdep warnings around RF PS and entry-list locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/dm.h

## Purpose
Declares the RTL8723BE dynamic-management interface and the register/threshold constants that drive DIG, BB power saving, EDCA, TX power tracking, ATC/CFO tracking, antenna selection, and Bluetooth RSSI policy.

## Important APIs, Types, And Functions
Key constants include RF/BB/MAC register aliases, `DM_DIG_*` false-alarm thresholds, rate-adaptive states, TX high-power levels, `TXPWRTRACK_MAX_IDX`, CFO thresholds, and antenna identifiers. Enums define 1R CCA mode, RF save/normal mode, software antenna switching, and power tracking method (`BBSWING` or `TXAGC`). Public prototypes expose initialization, watchdog, DIG write, thermal tracking, rate-mask initialization, TX-power track adjustment, and antenna selection/statistics callbacks.

## Control Flow
No executable flow, but this header defines which knobs `dm.c` can drive and what external rtlwifi code can invoke. `GET_UNDECORATED_AVERAGE_RSSI()` selects the relevant smoothed RSSI source depending on adhoc versus infrastructure operation.

## State And Persistence
No state is stored in the header. Constants describe persistent hardware register addresses and stable policy thresholds; changing them alters runtime behavior across watchdog iterations.

## Dependencies And Integration Points
Included by `dm.c`, `hw.c`, and `phy.c`; it also depends on common rtlwifi structures such as `struct rtl_priv`. Bluetooth RSSI masks align with btcoexist logic, and antenna constants align with descriptor antenna-selection hooks.

## Risks
Register aliases and thresholds are global assumptions. Incorrect register numbers can redirect watchdog writes into unrelated BB/MAC state. Threshold changes can make DIG, CFO tracking, or TX-power tracking unstable across all runtime modes.

## Test Signals
Build coverage catches prototype drift. Runtime signals come from DM watchdog behavior: stable DIG values, no excessive false alarm response, correct thermal compensation, and expected Bluetooth coexistence decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/fw.c

## Purpose
Implements RTL8723BE host-to-firmware command submission and firmware-side power-management support. It serializes H2C mailbox writes, constructs LPS power-mode and media-status commands, downloads reserved pages for firmware autonomous frames, and configures P2P power-save offload.

## Important APIs, Types, And Functions
`rtl8723be_fill_h2c_cmd()` is the public H2C wrapper, gated by `rtlhal->fw_ready`. `_rtl8723be_fill_h2c_command()` owns mailbox selection, locking, firmware-read polling, register writes to HMEBOX and extension boxes, and box index advancement. `rtl8723be_set_fw_pwrmode_cmd()` builds `H2C_8723B_SETPWRMODE` using LPS mode, smart PS, awake interval, RPWM state, and Bluetooth coexistence overrides. `rtl8723be_set_fw_media_status_rpt_cmd()` reports connect/disconnect. `rtl8723be_set_fw_rsvdpagepkt()` patches a static reserved-page packet image with current MAC/BSSID/AID, sends it as a command skb, and reports page locations to firmware. `rtl8723be_set_p2p_ps_offload_cmd()` programs CTWindow/NoA registers and sends P2P PS offload state.

## Control Flow
H2C submission waits for any in-progress command under `h2c_lock`, selects the next firmware mailbox, waits for firmware to clear that box, writes normal and extension payload bytes depending on command length, rotates `last_hmeboxnum`, and clears the in-progress flag. LPS command flow optionally lets BT coexistence force active/min mode and supply byte5/RPWM values. Reserved-page flow mutates static packet templates, sends them through `rtl_cmd_send_packet()`, then sends page-location H2C only if the packet download succeeded.

## State And Persistence
Persistent state includes `rtlhal->last_hmeboxnum`, `rtlhal->h2c_setinprogress`, `rtlhal->p2p_ps_offload`, `rtlps->p2p_ps_info`, firmware mailbox registers, P2P NoA hardware registers, and the static `reserved_page_packet` template. Firmware retains reserved-page locations and power-save/offload settings until replaced or reset.

## Dependencies And Integration Points
Depends on rtlwifi firmware common helpers, register definitions, `rtl_cmd_send_packet()`, power-save state from `rtl_ps_ctl`, Bluetooth coexistence callbacks, mac80211 BSSID/MAC/AID state, and H2C command ids/macros in `fw.h`. `hw.c` calls these through `set_hw_reg()` for join reports, keepalive, LPS, and P2P PS.

## Risks
Mailbox serialization is timing-sensitive; timeouts can silently drop firmware commands. Command lengths above seven bytes are unsupported by the switch. Reserved-page templates contain fixed frame bodies that are only partially patched, so wrong offsets or stale addresses break firmware PS responses. P2P NoA start-time adjustment loops mutate count values and depend on TSF timing. BT-controlled LPS can override requested mode, making power regressions hard to attribute.

## Test Signals
Verify firmware-ready gating, successful H2C logs, association reserved-page download, LPS entry/exit, keepalive behavior, P2P GO/client CTWindow and NoA operation, and Bluetooth coexistence LPS transitions. Failures show as HMEBOX wait warnings, missed PS-Poll/null/QoS-null behavior, P2P clients waking incorrectly, or firmware not acknowledging power-mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/fw.h

## Purpose
Defines RTL8723BE firmware constants, RPWM/LPS state bits, H2C command ids, H2C payload packing macros, and public firmware command prototypes.

## Important APIs, Types, And Functions
Firmware size/address constants describe the legacy firmware layout. RPWM macros define RF-on/off, clock-on/off, ACK/toggle, active/register bits, and helpers such as `IS_IN_LOW_POWER_STATE()` and `FW_PS_IS_ACK()`. `enum rtl8723b_h2c_cmd` lists command ids for reserved pages, media status, scan, keepalive, disconnect decision, power mode, LPS parameters, P2P PS offload, RA mask, and RSSI reports. Payload macros set fields for power mode, media status, and reserved-page locations. Public functions are the command helpers implemented in `fw.c`.

## Control Flow
No direct flow, but the macros define how `fw.c` packs mailbox payloads and how `hw.c` interprets firmware power-state transitions.

## State And Persistence
No state is stored here. Constants describe firmware-visible bits and command numbers that persist as ABI with the RTL8723B firmware image.

## Dependencies And Integration Points
Included by `fw.c`, `hw.c`, and dynamic-management code. It ties rtlwifi software power-save state to firmware RPWM/CPWM handshakes and H2C mailbox commands.

## Risks
Duplicated `FW_PWR_STATE_ACTIVE`/`FW_PWR_STATE_RF_OFF` definitions should remain identical but are maintenance noise. Incorrect command ids or bit packing would make firmware ignore or misinterpret power, media, reserved-page, and P2P commands.

## Test Signals
Compile-time macro use, firmware command acceptance, correct LPS state transitions, successful reserved-page location H2C, and RA/RSSI reports reaching firmware are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/hw.c

## Purpose
Provides the RTL8723BE hardware operations behind the rtlwifi/mac80211 driver: power-on/off sequencing, PCIe DMA and LLT setup, firmware download, MAC/BB/RF initialization, hardware register get/set dispatch, beacon and media-state programming, interrupt control, EFUSE/OEM parsing, rate-mask H2C updates, CAM security programming, GPIO radio detection, Bluetooth coexistence setup, and card disable.

## Important APIs, Types, And Functions
Primary public entry points include `rtl8723be_hw_init()`, `rtl8723be_card_disable()`, `rtl8723be_get_hw_reg()`, `rtl8723be_set_hw_reg()`, `rtl8723be_read_eeprom_info()`, `rtl8723be_enable_interrupt()`, `rtl8723be_disable_interrupt()`, `rtl8723be_interrupt_recognized()`, `rtl8723be_set_network_type()`, `rtl8723be_set_check_bssid()`, `rtl8723be_set_qos()`, beacon setup helpers, `rtl8723be_update_hal_rate_tbl()`, `rtl8723be_gpio_radio_on_off_checking()`, `rtl8723be_enable_hw_security_config()`, `rtl8723be_set_key()`, and BT coexistence init/read helpers. Important internals include `_rtl8723be_init_mac()`, `_rtl8723be_llt_table_init()`, `_rtl8723be_poweroff_adapter()`, `_rtl8723be_check_pcie_dma_hang()`, `_rtl8723be_reset_pcie_interface_dma()`, `_rtl8723be_download_rsvd_page()`, `_rtl8723be_fwlps_enter()`/leave, and EFUSE TX-power parsing routines.

## Control Flow
`rtl8723be_hw_init()` enables interrupts locally, disables ASPM, detects whether MAC was already enabled, resets DMA if hung, powers off stale MAC state, runs the MAC power-on flow, downloads firmware, configures MAC/BB/RF, updates receive config, initializes RF channel values, programs hardware defaults, resets CAM, enables security, sets MAC address, applies ASPM backdoor settings, initializes BT hardware, runs RF-path/IQK/thermal/LC calibration when RF is on, releases RX/PCIe DMA, and initializes DM. Shutdown sets no-link media state, updates LEDs, marks NIC halt power level, runs firmware self-reset and power sequencing, resets MCU wrapper, and locks power-control registers.

## State And Persistence
This file is the major state bridge between rtlwifi software state and hardware registers. It mutates `rtlhal` flags (`fw_ready`, `mac_func_enable`, `being_init_adapter`, firmware PS fields), PCI ring DMA registers and IRQ masks, `rtlpci->receive_config`, beacon-control cache, `rtlpriv->sec`/CAM entries, EFUSE TX-power tables, OEM id, board/package type, BT coexistence info, power-save state, MAC link/opmode fields, and LED state. Hardware persistence includes LLT page chains, queue boundaries, DMA descriptors, CAM key slots, media-state register, RCR, interrupt masks, TSF/beacon registers, and firmware LPS/offload state.

## Dependencies And Integration Points
Depends on rtlwifi common EFUSE, CAM, PCI, PS, register, firmware, PHY, DM, LED, power-sequence, and BT coexistence layers. It is called by the rtlwifi core operation table from `sw.c` and routes many generic `HW_VAR_*` operations to RTL8723BE-specific registers or firmware H2C commands. It also integrates with mac80211 station rate capabilities when building RA-mask commands.

## Risks
Initialization order is firmware- and hardware-sensitive: LLT, DMA descriptors, firmware readiness, BB/RF config, CAM, ASPM, BT, and calibration must happen in the right order. PCIe DMA hang reset pauses and restores DMA/register locks and can disrupt live state if misdetected. `set_hw_reg()` is a large switch with many typed `u8 *` casts; wrong caller value types corrupt state. EFUSE parsing uses many defaults and OEM tables, so bad autoload handling affects TX power, LED behavior, and BT antenna selection. CAM key programming must allocate/free correct entries for AP, station, group, pairwise, WEP, and adhoc modes.

## Test Signals
Probe logs should show firmware download, MAC/BB/RF config, chip version, EFUSE autoload, and calibration without errors. Validate interrupts, TX/RX DMA, association and reserved-page download, AP/adhoc beaconing, BSSID filtering, QoS/EDCA, security with WEP/TKIP/CCMP group and pairwise keys, RF-kill GPIO toggles, suspend/card disable/resume path expectations, BT coexistence antenna overrides, and rate-mask H2C changes as RSSI changes. DMA API, lockdep, and firmware assertion logs are important diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/hw.h

## Purpose
Declares the RTL8723BE hardware-operation API implemented by `hw.c` and consumed by the rtlwifi core/device operation table.

## Important APIs, Types, And Functions
The prototypes cover register get/set, EEPROM/EFUSE parsing, interrupt recognition and masking, hardware initialization, card disable, network type/BSSID/QoS/beacon setup, rate-table update, channel-access update, GPIO radio check, hardware security/CAM configuration, key programming, BT coexistence EFUSE/register/hardware init, and suspend/resume stubs.

## Control Flow
No local flow. The header defines the callable surface that higher-level rtlwifi callbacks use during probe, start/stop, config changes, association, key install/remove, interrupt handling, RF-kill polling, and power transitions.

## State And Persistence
No state is held here, but all declared functions mutate persistent driver and hardware state in `hw.c`.

## Dependencies And Integration Points
Depends on mac80211 types (`ieee80211_hw`, `ieee80211_sta`, `nl80211_iftype`) and rtlwifi types (`rtl_int`). It is included by `hw.c` and likely `sw.c` for operation-table binding.

## Risks
Prototype drift breaks operation table assignments or causes mismatched call signatures. Since most functions accept raw `u8 *` values or hardware-level enums, callers must honor the expected payload type for each operation.

## Test Signals
Build warnings are the primary header signal. Runtime coverage comes from successful probe, interrupts, association, key programming, RF-kill, and power-management callbacks reaching the implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/led.c

## Purpose
Implements simple software LED control for RTL8723BE. It maps rtlwifi LED events onto register writes for LED0/LED1/GPIO0 pins, with open-drain handling for LED-off behavior.

## Important APIs, Types, And Functions
`rtl8723be_sw_led_on()` drives the selected LED pin on by programming `REG_LEDCFG2` or `REG_LEDCFG1`. `rtl8723be_sw_led_off()` switches pins off and handles `led_opendrain` by updating `REG_MAC_PINMUX_CFG`. `_rtl8723be_sw_led_control()` maps power/link/no-link actions to on and power-off to off. `rtl8723be_led_control()` is the exported dispatcher and suppresses activity/link LED changes when RF is off for reasons stronger than software power save.

## Control Flow
Higher-level hardware and mac80211 events call `rtl8723be_led_control()`. The dispatcher checks RF-off reason, logs the action, and invokes the private control helper. Only power-on/link/no-link and power-off states actively toggle the LED; TX/RX/site-survey/start-link events are ignored in this implementation.

## State And Persistence
State is in hardware LED registers and `rtlpriv->ledctl` fields such as `sw_led0` and `led_opendrain`. Register state persists until another LED or power event changes it.

## Dependencies And Integration Points
Depends on rtlwifi LED enums, power-save state from `rtl_ps_ctl`, and register definitions. Called from `hw.c` during init, media-state changes, RF power changes, and card disable.

## Risks
LED polarity/open-drain assumptions are board-specific. Incorrect pin or register handling can leave LEDs stuck on/off or interfere with MAC pin mux. Suppressing LED updates during RF-off is intentional but can hide link-state transitions until RF returns.

## Test Signals
Observe LED behavior on power on/off, link/no-link transitions, RF-kill, IPS/LPS, and card disable across boards with open-drain LED wiring. Register traces should show only expected `REG_LEDCFG*` and pinmux writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/led.h

## Purpose
Declares the RTL8723BE LED-control functions implemented in `led.c`.

## Important APIs, Types, And Functions
The exported API consists of `rtl8723be_sw_led_on()`, `rtl8723be_sw_led_off()`, and `rtl8723be_led_control()`. The first two operate on explicit `enum rtl_led_pin`; the dispatcher accepts higher-level `enum led_ctl_mode`.

## Control Flow
No control flow in the header. It allows `hw.c` and operation-table setup code to call LED functions for power and link events.

## State And Persistence
No state is stored. Implementations mutate LED hardware registers and `rtlpriv->ledctl`-selected pins.

## Dependencies And Integration Points
Depends on rtlwifi/mac80211 hardware and LED enums. Included by `hw.c` and `led.c`.

## Risks
Prototype mismatch would break LED callback binding. Pin-mode semantics remain in implementation and board data, not in the header.

## Test Signals
Build success and successful link/power LED callback execution are sufficient header-level signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/phy.c

## Purpose
Implements RTL8723BE PHY/RF configuration and runtime radio control. It programs MAC/BB/RF table data, parses conditional PHY table entries, stores TX-power-by-rate data, computes and writes per-rate TXAGC values, switches bandwidth and channel, handles scan-time DM pause/resume IO commands, runs IQK and LC calibrations, controls antenna/RF path switching, and transitions RF power state.

## Important APIs, Types, And Functions
Public configuration APIs are `rtl8723be_phy_mac_config()`, `rtl8723be_phy_bb_config()`, `rtl8723be_phy_rf_config()`, and `rtl8723be_phy_config_rf_with_headerfile()`. Register APIs are `rtl8723be_phy_query_rf_reg()` and `rtl8723be_phy_set_rf_reg()`, serialized by `rf_lock`. TX-power APIs include `rtl8723be_phy_set_txpower_level()` and helpers for EFUSE base power, per-rate offsets, relative conversion, and BB TXAGC writes. Channel APIs are `rtl8723be_phy_set_bw_mode()`, `rtl8723be_phy_set_bw_mode_callback()`, `rtl8723be_phy_sw_chnl()`, and `_rtl8723be_phy_sw_chnl_step_by_step()`. Calibration APIs are `rtl8723be_phy_iq_calibrate()`, `_rtl8723be_phy_iq_calibrate()`, path A/B TX/RX IQK helpers, similarity comparison, matrix fill, and `rtl8723be_phy_lc_calibrate()`. Power APIs include `rtl8723be_phy_set_rf_power_state()`, `_rtl8723be_phy_set_rf_power_state()`, `rtl8723be_phy_set_rf_on()`, and `_rtl8723be_phy_set_rf_sleep()`.

## Control Flow
BB config enables BB/RF-related clocks/resets, applies MAC/PHY/AGC table arrays, applies PG TX-power data if EFUSE autoload succeeded, converts power values to relative offsets, and sets crystal cap. Channel switch builds pre/RF/post command arrays: set TX power first, write RF channel bandwidth register for each RF path, then finish. Bandwidth switch updates MAC BW operation/RRSR sideband fields, BB RF mode and CCK/OFDM sideband fields, then calls RF6052 bandwidth programming. IQK runs up to three calibration rounds, compares candidates, fills path A/B matrices, saves per-channel IQK matrices, and restores backed-up BB/MAC/ADDA/path state. RF power changes wait for TX queues, call NIC enable/disable for IPS halt level, program RF-on or RF-sleep registers, and update LED state.

## State And Persistence
State lives in `rtlpriv->phy` and EFUSE structures: RF register channel values, current channel/bandwidth, set-in-progress flags, default initial gain/frame sync, TX-power-by-rate offsets and base arrays, IQK backups/matrices/results, RF path type/count, LCK in-progress state, and init-gain backup for scans. Hardware state persists in MAC/BB/RF registers, TXAGC tables, crystal-cap register fields, RF channel/bandwidth registers, IQK matrices, and RF sleep/on state.

## Dependencies And Integration Points
Depends on rtl8723 common PHY helpers, RF6052 helpers in `rf.c`, generated table arrays in `table.c/table.h`, EFUSE data parsed in `hw.c`, descriptor rate ids in `def.h`, DM scan/power tracking in `dm.c`, rtlwifi power-save helpers, PCI TX rings for RF sleep waits, and mac80211 channel/bandwidth state. `hw.c` calls configuration and calibration during probe; mac80211 config paths call channel and bandwidth changes through rtlwifi ops.

## Risks
This file contains many direct magic register writes and timing delays. Table conditional parsing must match board/cut/package/interface data or the wrong RF settings are applied. TX-power computation mixes signed EFUSE deltas, per-rate offsets, bandwidth differences, and regulatory mode; overflow or wrong channel indexing can violate power limits or reduce range. IQK/LC calibration can disturb Bluetooth/audio and is guarded with delays and locks but still touches many BB/RF registers. RF power off waits for queues but can time out, and BEACON queue handling differs between ERFOFF and ERFSLEEP.

## Test Signals
Probe should complete MAC/BB/RF config, firmware start, IQK, LC, and TX-power setup without warnings. Test channels 1-14, 20/40 MHz sideband changes, scanning pause/resume, low/high RSSI TX-power updates, RF-kill/IPS/LPS transitions, BT coexistence active during calibration, and repeated suspend-like card disable/enable. Signals include correct RF channel register values, stable throughput, no stuck `sw_chnl_inprogress`/`set_bwmode_inprogress`, no TX queue sleep timeout spam, and sane TX power across CCK/OFDM/MCS rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/phy.h

## Purpose
Declares RTL8723BE PHY constants, EFUSE offsets, calibration dimensions, antenna diversity modes, baseband config types, and the public PHY/RF API.

## Important APIs, Types, And Functions
Constants cover TX path counts, max power index, channel-switch command array sizes, IQK/LC/APK dimensions, EFUSE offsets for MAC/TX power/channel plan/thermal/RF option/customer id, RF path count, and RF register masks. Enums define baseband config type and antenna-diversity type. Function prototypes expose RF register access, MAC/BB/RF config, default register capture, TX-power setting, scan backup/restore, bandwidth and channel switching, IQK/LC calibration, RF path switching, RF table config, IO command handling, and RF power-state changes.

## Control Flow
No executable flow. The header defines what `hw.c`, `dm.c`, and rtlwifi operation tables can call in `phy.c`.

## State And Persistence
No mutable state is stored. Constants define array sizes and EFUSE offsets that shape persistent `rtl_phy` and `rtl_efuse` data.

## Dependencies And Integration Points
Depends on mac80211 channel types, rtlwifi radio path/power enums, and hardware register definitions. It bridges `hw.c` initialization, `dm.c` calibration/power tracking, `rf.c` RF6052 helpers, and generated table programming.

## Risks
Array-size constants such as `MAX_TX_COUNT`, IQK register counts, and command counts must match implementation loops and EFUSE layout. The comment warns `MAX_TX_COUNT` must remain 4 or EFUSE table reads break.

## Test Signals
Build coverage for prototypes and runtime validation of EFUSE TX-power parsing, channel switch, bandwidth switch, IQK/LC, scan backup/restore, and RF power state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.c

## Purpose
Defines RTL8723B power-transition flow arrays consumed by the common Realtek power-sequence parser. These arrays encode card-emulation, active, suspend, power-down, card-disable, and low-power-state transitions for PCI operation.

## Important APIs, Types, And Functions
The file exports `struct wlan_pwr_cfg` arrays: `rtl8723B_power_on_flow`, `rtl8723B_radio_off_flow`, `rtl8723B_card_disable_flow`, `rtl8723B_card_enable_flow`, `rtl8723B_suspend_flow`, `rtl8723B_resume_flow`, `rtl8723B_hwpdn_flow`, `rtl8723B_enter_lps_flow`, and `rtl8723B_leave_lps_flow`. Each is composed from macros in `pwrseq.h` and terminated with `RTL8723B_TRANS_END`.

## Control Flow
There is no local executable control flow. `rtl_hal_pwrseqcmdparsing()` walks these arrays when `hw.c` initializes MAC power, powers off the adapter, disables/enables the card, or enters/leaves firmware LPS.

## State And Persistence
The arrays are static configuration data. The persistent effects occur when the parser writes hardware power, clock, reset, isolation, and low-power registers according to the macro-expanded commands.

## Dependencies And Integration Points
Depends on `../pwrseqcmd.h` and `pwrseq.h` for command structure and transition macro definitions. Integrated by `hw.c` through constants such as `RTL8723_NIC_ENABLE_FLOW`, `RTL8723_NIC_DISABLE_FLOW`, and `RTL8723_NIC_LPS_ENTER_FLOW`.

## Risks
Array sizing must match the step-count macros plus end marker. Wrong transition ordering can leave the chip in card-emulation, suspend, PDN, or active states incorrectly, which affects firmware download, RF power, and wake behavior. Since this is data-driven, errors surface only at runtime through parser failures or dead hardware.

## Test Signals
Probe power-on, card disable, IPS/LPS entry/exit, suspend/resume-like flows, and hardware power-down should complete without power-sequence parser failures. Hardware signals include successful register access after enable, firmware download after active transition, and low idle power after LPS/card-disable transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.c -->
