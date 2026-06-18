# Research: subset-b-004889

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/hw.c

## Purpose
`hw.c` is the RTL8192EE PCIe hardware orchestration layer. It bridges mac80211/rtlwifi core requests to device registers, firmware H2C commands, EFUSE-derived configuration, PCIe DMA rings, interrupt masks, beacon controls, CAM security entries, Bluetooth coexistence hooks, and RF power transitions. It is the main bring-up/tear-down file for this chip.

## Important APIs, Types, And Functions
The exported entry points match `hw.h`: `rtl92ee_hw_init`, `rtl92ee_card_disable`, `rtl92ee_get_hw_reg`, `rtl92ee_set_hw_reg`, `rtl92ee_read_eeprom_info`, interrupt enable/disable/recognition, beacon setup, network type/QoS setup, security setup, key programming, BT coexistence init, suspend/resume stubs, promiscuous RCR control, and firmware clock-off timer callback. Internally, `_rtl92ee_init_mac`, `_rtl92ee_hw_configure`, `_rtl8192ee_check_pcie_dma_hang`, `_rtl8192ee_reset_pcie_interface_dma`, `_rtl92ee_poweroff_adapter`, `_rtl92ee_download_rsvd_page`, `_rtl92ee_read_adapter_info`, and `_rtl92ee_read_txpower_info_from_hwpg` are central. State is carried through `struct rtl_priv`, `rtl_hal`, `rtl_pci`, `rtl_mac`, `rtl_phy`, `rtl_efuse`, and `rtl_ps_ctl`.

## Control Flow
Initialization disables ASPM, detects whether MAC is already alive, checks/resets PCIe DMA hang state, runs the RTL8192E power sequence, initializes MAC/DMA descriptor addresses, downloads firmware, configures MAC/BB/RF tables, enables CCK/OFDM blocks, configures defaults, resets CAM, enables security, writes MAC address, re-enables ASPM, initializes BT coexistence, and runs IQK calibration. Runtime setters use `HW_VAR_*` switch dispatch for MAC address, BSSID, rates, SIFS/slot timing, RCR, RPWM, firmware LPS actions, join reports, AID, TSF correction, and keepalive. Link mode changes update MSR, beacon stop/resume, BSSID filtering, LED state, and beacon timing. Disable transitions stop link state, update LEDs, self-reset firmware when needed, run LPS/card-disable power sequences, reset MCU wrapper, and invalidate IQK state when BT coexistence is not active.

## State And Persistence Behavior
Persistent device-derived values are loaded from EFUSE/EEPROM into `rtl_efuse`: channel plan, tx-power tables, thermal meter, regulatory mode, board type, crystal cap, OEM/customer ID, and BT coexistence flags. Runtime state is cached in `rtlpci->receive_config`, `rtlpci->reg_bcn_ctrl_val`, `rtlpci->irq_mask`, `rtlhal->fw_ready`, firmware power-save state, ASPM state, `ppsc->rfpwr_state`, and security key buffers. Hardware CAM entries persist until explicitly cleared or power-cycled.

## Dependencies And Integration Points
This file depends on rt lwifi core helpers (`rtl_read_*`, `rtl_write_*`, CAM, EFUSE, PCI, base, regulatory, power-save helpers), local chip modules (`phy`, `dm`, `fw`, `led`, `pwrseq`, `reg`, `def`), mac80211 station/link metadata, PCIe DMA ring allocation, firmware H2C command definitions, and BT coexistence ops. It integrates upward through the driver ops table used by the rtlwifi core and downward through register writes and firmware commands.

## Risks
Most behavior is register-sequence sensitive. Risks include silent hardware misconfiguration from wrong constants, polling loops that continue after timeout without hard failure, a likely typo in `rtl92ee_bt_reg_init` where `reg_bt_sco` is assigned twice and `reg_bt_sco` overwrites the intended AMPDU field, concurrency hazards around firmware clock changes despite the lock, DMA hang recovery interacting with live rings, and EFUSE autoload failures leaving partial defaults. Security CAM programming depends on correct `key_len` state from upper layers.

## Test Signals
Useful signals are successful firmware download, `rtl92ee_hw_init` returning zero, interrupt recognition with expected ISR/HISRE masks, stable link mode transitions, beacon TX in AP/IBSS mode, successful reserved-page download, CAM entries visible through encrypted traffic, no PCIe DMA hang logs after reset, correct tx-power from EFUSE defaults and real EFUSE, LED transitions, suspend/resume no-ops not regressing power management, and RF/BT coexistence behavior under IPS/LPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/hw.h

## Purpose
`hw.h` is the public chip-hardware interface for the RTL8192EE implementation. It exposes the routines implemented in `hw.c` to the rtlwifi core and adjacent chip modules without carrying implementation state.

## Important APIs, Types, And Functions
The header declares hardware register access dispatch (`rtl92ee_get_hw_reg`, `rtl92ee_set_hw_reg`), EEPROM/EFUSE parsing, interrupt recognition and mask control, full hardware init and card disable, network type/BSSID/QoS/beacon configuration, rate-table updates, GPIO radio checking, security enablement and key programming, BT coexistence EFUSE and hardware init, suspend/resume hooks, receive-all-destination control, and the firmware clock-off timer callback. It uses shared rtlwifi/mac80211 types such as `struct ieee80211_hw`, `struct ieee80211_sta`, `struct rtl_int`, `enum nl80211_iftype`, and `enum led_ctl_mode` indirectly.

## Control Flow
This header does not implement flow, but it defines the callable surface used by the driver ops table and by sibling modules. The main lifecycle is `read_eeprom_info` before hardware bring-up, `hw_init`, runtime setters and interrupt helpers during operation, and `card_disable` during shutdown or IPS.

## State And Persistence Behavior
No state is stored here. All persistent and runtime state lives in rtlwifi structures reached from `struct ieee80211_hw`.

## Dependencies And Integration Points
It depends on the includer already having definitions for mac80211 and rtlwifi structures/enums. Integration is broad: PCI probe/remove, mac80211 callbacks, firmware power-save work, security key paths, and BT coexistence all consume these declarations.

## Risks
Because this is a declaration boundary, mismatches with `hw.c` signatures or missing prototypes would show up as build failures. The broad API also makes `hw.c` a high-blast-radius module; changes to these declarations affect driver ops registration and adjacent code.

## Test Signals
Compile coverage is the primary signal. Link-time success confirms all declared functions are implemented, and runtime smoke tests for initialization, interrupt handling, link setup, and shutdown validate the exported surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/led.c

## Purpose
`led.c` implements the software LED control path for RTL8192EE. It maps rtlwifi LED actions to GPIO/LED register operations and suppresses inappropriate LED activity while RF is off for reasons stronger than normal power saving.

## Important APIs, Types, And Functions
The exported APIs are `rtl92ee_sw_led_on`, `rtl92ee_sw_led_off`, and `rtl92ee_led_control`. `_rtl92ee_sw_led_control` maps high-level `enum led_ctl_mode` values to on/off actions. The code uses `struct rtl_priv`, `struct rtl_ps_ctl`, `enum rtl_led_pin`, and register `REG_GPIO_PIN_CTRL` from `reg.h`.

## Control Flow
`rtl92ee_led_control` first checks RF-off reason and ignores TX/RX/survey/link/power-on LED actions when the device is off for non-PS reasons. It logs the action and delegates to `_rtl92ee_sw_led_control`. Only `LED_CTL_POWER_ON`, `LED_CTL_LINK`, and `LED_CTL_NO_LINK` turn LED0 on; `LED_CTL_POWER_OFF` turns it off. The GPIO0 and LED1 cases are intentionally empty.

## State And Persistence Behavior
The selected LED pin comes from `rtlpriv->ledctl.sw_led0`. Hardware state is persisted only in GPIO register bits until overwritten or reset. There is no timer, blink state, or software state machine in this file.

## Dependencies And Integration Points
This module is called from hardware init/disable and media status changes in `hw.c`, and through the rtlwifi ops table. It depends on MMIO helpers and `REG_GPIO_PIN_CTRL` bit layout. It also reads power-save state to avoid misleading UI when RF is off.

## Risks
The LED-off path uses `ledcfg |= ~BIT(21)`, which sets almost every bit in the register before clearing bit 29; that is suspicious and may clobber unrelated GPIO controls. The empty LED1/GPIO0 cases mean boards wired differently may show no LED behavior. There is no debounce or blink support.

## Test Signals
Validate LED on at power/link/no-link, LED off at power-off, no LED activity during RF-off non-PS states, and no unintended GPIO side effects. A register trace around `REG_GPIO_PIN_CTRL` is useful because of the broad bit operation in the off path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/led.h

## Purpose
`led.h` exposes the RTL8192EE LED control functions to the rest of the chip driver.

## Important APIs, Types, And Functions
It declares `rtl92ee_sw_led_on`, `rtl92ee_sw_led_off`, and `rtl92ee_led_control`, all operating on `struct ieee80211_hw` and using rtlwifi LED enums.

## Control Flow
There is no implementation here. Callers use direct pin-level on/off functions when they know the LED pin, or `rtl92ee_led_control` for high-level LED actions.

## State And Persistence Behavior
The header stores no state. State is in `rtlpriv->ledctl` and GPIO registers managed by `led.c`.

## Dependencies And Integration Points
It requires the includer to know `struct ieee80211_hw`, `enum rtl_led_pin`, and `enum led_ctl_mode`. It is included by `hw.c` and `led.c`.

## Risks
The narrow declaration surface is low risk, but any signature change must be coordinated with driver ops and callers.

## Test Signals
Build success and LED action smoke tests through `rtl92ee_led_control` cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/phy.c

## Purpose
`phy.c` owns RTL8192EE baseband and RF programming: BB/RF register access, MAC/BB/RF table loading, transmit-power derivation, channel and bandwidth switching, scan-time DIG/CCA adjustments, IQ calibration, LC calibration, antenna path switching, and RF power-state transitions.

## Important APIs, Types, And Functions
Public functions include BB/RF query/set helpers, `rtl92ee_phy_mac_config`, `rtl92ee_phy_bb_config`, `rtl92ee_phy_rf_config`, `rtl92ee_phy_config_rf_with_headerfile`, original-value capture, tx-power get/set, scan backup/restore, bandwidth and channel switching, IQ/LC calibration, RF path switch, IO command dispatch, and RF power-state control. Important internal helpers are `_rtl92ee_phy_rf_serial_read/write`, `_check_condition`, register-table loaders, tx-power-by-rate conversion, `_rtl92ee_phy_sw_chnl_step_by_step`, IQK path routines, IQK matrix fill/save/restore helpers, and `_rtl92ee_phy_set_rf_power_state`.

## Control Flow
BB config initializes `phyreg_def`, enables BB/RF functional blocks, loads PHY register and AGC tables from `table.h`, optionally loads PG tx-power data, converts absolute dBm table values into relative offsets, and applies crystal-cap settings. RF config delegates to RF6052 setup. Register tables support conditional sections marked by magic values and matched against board type, interface, and platform. Channel switching builds pre/RF/post command arrays, sets tx power first, then writes `RF_CHNLBW` channel bits for every active RF path. Bandwidth switching updates MAC `REG_BWOPMODE`, response sideband fields, BB modulation mode, CCK/OFDM sideband controls, and RF6052 bandwidth bits.

## State And Persistence Behavior
State is cached in `rtlpriv->phy`: RF path register definitions, RF channel values, tx-power by-rate offsets and bases, current channel/bandwidth, in-progress flags, backup RF register values, default initial gain, framesync, calibration backups, IQK matrix per channel, and current IO command. EFUSE tx-power tables and regulatory mode feed power index calculations. RF power state is persisted in `ppsc->rfpwr_state`, with last-awake/sleep timestamps.

## Dependencies And Integration Points
This file depends on `reg.h` constants, `table.h` generated register arrays, local `rf.c` for RF6052 configuration, `dm.c` for DIG/CCA writes, PCI rings for RF-off queue draining, power-save helpers for NIC disable/enable, and `hw.c` for `HW_VAR_IO_CMD` and RF/LPS interaction. It is timing-sensitive and relies on `udelay`/`mdelay` around serial RF and calibration sequences.

## Risks
The code is register-table and magic-value heavy; incorrect table parsing or condition matching can silently misprogram hardware. Several loops time out but continue, so failures may appear later as weak RF performance. `_rtl92ee_phy_init_tx_power_by_rate` uses nested loops without resetting inner loop counters per outer iteration, so only part of the intended matrix may be zeroed. Channel switching warns on channels above 14 even though helper tables include 5 GHz channel places, suggesting this variant is effectively 2.4 GHz focused or incomplete for 5 GHz. RF-off waits can delay while queues drain and may still proceed after busy timeout.

## Test Signals
Signals include correct BB/RF table load logs, stable RF serial readback, channel changes updating RF channel bits, tx-power registers matching EFUSE-derived expectations across CCK/OFDM/MCS rates, bandwidth changes working in 20 and 40 MHz, scan pause/restore lowering/restoring DIG and CCA thresholds, IQK success logs with stored matrix, LC calibration completion outside active scan, RF on/off/sleep LED and queue-drain behavior, and throughput/RSSI sanity after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/phy.h

## Purpose
`phy.h` defines the public PHY/RF interface and local constants needed by RTL8192EE baseband, RF, tx-power, channel switching, antenna diversity, and calibration code.

## Important APIs, Types, And Functions
The header defines tx-count and power constants, IQK/APK array sizes, tolerance/delay limits, EFUSE content offsets, RF path limits, `enum swchnlcmd_id`, `struct swchnlcmd`, `enum baseband_config_type`, `enum ant_div_type`, and all public `rtl92ee_phy_*` functions. The exported functions cover BB/RF register access, MAC/BB/RF config, tx-power programming, scan backup, bandwidth/channel switching, IQ/LC calibration, RF path switching, RF table config, IO commands, and RF power state transitions.

## Control Flow
The header itself has no flow, but it constrains the control structures used by `phy.c`: channel changes are expressed as `struct swchnlcmd` sequences, baseband config selects PHY register or AGC tables, and antenna diversity values guide RF path switching.

## State And Persistence Behavior
No state is allocated here. Constants such as `MAX_TX_COUNT`, EFUSE offsets, IQK dimensions, and RF path limits define the shape of persistent arrays in `struct rtl_phy` and `struct rtl_efuse`.

## Dependencies And Integration Points
It depends on shared rtlwifi/mac80211 types and radio/power enums defined elsewhere. It is consumed by `hw.c`, `rf.c`, and `phy.c`, making it the main local contract for PHY services.

## Risks
The comment on `MAX_TX_COUNT` warns that changing it breaks EFUSE parsing sequence. Function prototypes expose many timing-sensitive operations; callers must respect in-progress flags and RF power state. `RT_CANNOT_IO(hw)` is hardcoded to `false`, so any future sleep/unload protection would need real implementation elsewhere.

## Test Signals
Compile coverage validates prototypes and enum visibility. Runtime coverage should exercise all declared public operations through init, scan, channel switch, bandwidth switch, calibration, and RF power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/pwrseq.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/pwrseq.c

## Purpose
`pwrseq.c` materializes RTL8192E power-transition macros from `pwrseq.h` into concrete `struct wlan_pwr_cfg` arrays that the shared rtlwifi power-sequence parser can execute.

## Important APIs, Types, And Functions
There are no functions. The exported data arrays are `rtl8192E_power_on_flow`, `rtl8192E_radio_off_flow`, `rtl8192E_card_disable_flow`, `rtl8192E_card_enable_flow`, `rtl8192E_suspend_flow`, `rtl8192E_resume_flow`, `rtl8192E_hwpdn_flow`, `rtl8192E_enter_lps_flow`, and `rtl8192E_leave_lps_flow`. Each is sized by step-count macros and terminated by `RTL8192E_TRANS_END`.

## Control Flow
Execution flow is external: callers such as `_rtl92ee_init_mac` and `_rtl92ee_poweroff_adapter` pass these arrays to `rtl_hal_pwrseqcmdparsing`, which interprets writes, polling operations, and delays. Each flow concatenates one or more transition macros, for example card enable is card-disable-to-card-emulation followed by card-emulation-to-active.

## State And Persistence Behavior
The arrays are static driver data. They encode hardware register operations for power states but hold no mutable state themselves. Hardware power state changes persist in the device until another sequence or reset changes them.

## Dependencies And Integration Points
This file includes `pwrseq.h`, which depends on `../pwrseqcmd.h` for `struct wlan_pwr_cfg` and command/base/interface masks. It integrates with `hw.c` MAC init, card disable, suspend/resume concepts, LPS entry/leave, and hardware power-down.

## Risks
Array sizes must match the number of entries produced by the macros; a mismatch would be a compile-time or memory-layout issue. Any wrong offset/mask/value in `pwrseq.h` can break bring-up, low-power entry, or wake. Some arrays use size expressions involving PDN steps while containing card-disable transitions, so size slack must remain harmless.

## Test Signals
Signals are successful power-on parsing, MAC init continuation, clean RF/card disable, LPS entry/leave with firmware still responsive, suspend/resume transitions where used, and no parser overrun before `PWR_CMD_END`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/pwrseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/pwrseq.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/pwrseq.h

## Purpose
`pwrseq.h` describes RTL8192E hardware power-state transitions as macro-expanded sequences of `struct wlan_pwr_cfg` entries. It is the declarative power architecture for transitions among card emulation, active, suspend, card disabled, power down, and low-power state.

## Important APIs, Types, And Functions
The header defines step counts and transition macros for `CARDEMU_TO_ACT`, `ACT_TO_CARDEMU`, `CARDEMU_TO_SUS`, `SUS_TO_CARDEMU`, `CARDEMU_TO_CARDDIS`, `CARDDIS_TO_CARDEMU`, `CARDEMU_TO_PDN`, `PDN_TO_CARDEMU`, `ACT_TO_LPS`, `LPS_TO_ACT`, and `TRANS_END`. It declares all arrays provided by `pwrseq.c` and aliases them as `RTL8192E_NIC_*_FLOW`.

## Control Flow
The shared parser walks each array and performs command entries: MAC/SDIO/USB/PCI base writes, polling until masked values match, and microsecond/millisecond delays. Active-to-LPS pauses PCIe DMA and TX, polls transmit-empty counters, gates BB/MAC, and acknowledges scheduler state. LPS-to-active writes RPWM for SDIO/USB/PCIe, delays, restores TSF clocking, enables WMAC TRX and BB macro, clears TX pause, and clears ISR.

## State And Persistence Behavior
No C state is mutated by the header. The encoded register writes alter device power state, clocking, reset, RF, DMA, and suspend bits. Interface masks allow entries to apply only to PCI, USB, SDIO, or all interfaces.

## Dependencies And Integration Points
It depends on `../pwrseqcmd.h` for masks, command IDs, bases, and `PWRSEQ_DELAY_*`. It is consumed by `pwrseq.c` and by `hw.c` through aliases passed to `rtl_hal_pwrseqcmdparsing`.

## Risks
This file is highly hardware-specific; wrong bit definitions can produce hard-to-debug hangs. Polling entries can block progress if hardware never reaches expected state. Interface masks include USB/SDIO paths even though this chip directory is PCIe-oriented, so unused paths must not affect PCIe behavior.

## Test Signals
Power parser success, active MAC/RF after enable, quiet TX/RX before LPS/card-disable, reliable wake from LPS, correct handling of PCIe RPWM, and absence of stuck polling in dmesg are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/pwrseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/reg.h

## Purpose
`reg.h` is the RTL8192EE register map and bit-mask catalog. It names MAC, DMA, PCIe, protocol, EDCA, WMAC, security, power, BB, OFDM/CCK, IQK, RF, EFUSE/EEPROM, interrupt, rate, and WOL constants used by the local chip driver.

## Important APIs, Types, And Functions
There are no functions. Important groups include system/power registers (`REG_SYS_FUNC_EN`, `REG_APS_FSMCO`, `REG_RF_CTRL`), firmware/interrupt registers (`REG_MCUFWDL`, `REG_HIMR`, `REG_HISR`, `REG_HIMRE`, `REG_HISRE`), DMA and PCIe descriptors (`REG_*_DESA`, `REG_*_TXBD_NUM`, `REG_PCIE_HRPWM`), beacon/protocol registers, WMAC/RCR/SECCFG/CAM registers, EFUSE/EEPROM offsets, rate bitmaps, interrupt masks, BB register addresses, IQK registers, RF register numbers, and generic masks such as `MASKBYTE*`, `MASKDWORD`, and `RFREG_OFFSET_MASK`.

## Control Flow
The header does not execute, but it directs control in `hw.c`, `phy.c`, `rf.c`, and `led.c`. Register names group hardware pages by function, while bit masks make switch cases and table programming readable. Some aliases, such as `MSR`, `ISR`, `TSFR`, and RF channel aliases, normalize older naming.

## State And Persistence Behavior
No software state lives here. The constants describe persistent hardware state locations: EEPROM-derived configuration, CAM entries, receive filter state, interrupt masks/status, DMA pointers, RF channel/bandwidth, IQK measurements, and power state bits.

## Dependencies And Integration Points
Every local source file in this subset includes or depends on `reg.h`. It also binds to generated table arrays whose register addresses must match these definitions, shared rtlwifi bit macros, firmware command paths, CAM helpers, and the power-sequence parser.

## Risks
Register maps are high risk because compile success does not prove semantic correctness. Duplicate or aliased constants can hide mistakes. Bit masks must match hardware docs exactly, especially for power, DMA, CAM, and IQK. A wrong mask can clobber unrelated bits in read-modify-write sequences.

## Test Signals
Broad hardware smoke tests are needed: init, interrupt delivery, DMA RX/TX, beaconing, encryption, power-save transitions, channel/bandwidth switch, IQK, EFUSE parsing, and WOL. Register readback traces around changed definitions are the best targeted tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/rf.c

## Purpose
`rf.c` implements RTL8192EE RF6052-specific configuration and bandwidth programming. It is a small bridge between generic PHY code and RF register-table programming for paths A/B.

## Important APIs, Types, And Functions
The exported APIs are `rtl92ee_phy_rf6052_set_bandwidth` and `rtl92ee_phy_rf6052_config`. The internal `_rtl92ee_phy_rf6052_config_parafile` prepares the RF serial interface for each path, calls `rtl92ee_phy_config_rf_with_headerfile`, and restores RF environment bits. It uses `struct rtl_priv`, `struct rtl_phy`, `struct bb_reg_def`, RF path enums, `RF_CHNLBW`, `RFREG_OFFSET_MASK`, and HSSI/3-wire bit masks from `reg.h`.

## Control Flow
`rtl92ee_phy_rf6052_config` sets `rtlphy->num_total_rfpath` to one or two based on RF type, then loads RF tables. The parafile loader loops over active RF paths, saves RFENV from path-specific BB interface registers, enables RFENV/OE, configures 3-wire address/data length, loads the path table for A/B, restores RFENV, and aborts on failure. Bandwidth changes update cached `rfreg_chnlval[0]` and write RF channel/bandwidth register on paths A and B: 20 MHz sets bits 10 and 11, while 20/40 sets bit 10.

## State And Persistence Behavior
The main software state is `rtlphy->num_total_rfpath` and `rtlphy->rfreg_chnlval[]`. Hardware RF path registers retain bandwidth and table-programmed values until another RF write or reset.

## Dependencies And Integration Points
It depends on `phy.c` for `rtl92ee_phy_config_rf_with_headerfile`, on `reg.h` for RF/BB masks, and on `dm.h`/`def.h` for surrounding driver context. It is called from `rtl92ee_phy_rf_config` during init and `rtl92ee_phy_set_bw_mode_callback` during bandwidth changes.

## Risks
Bandwidth programming writes both A and B even if only one path is active in the bandwidth helper, which is probably harmless but worth noting on 1T1R variants. RF table load failures return false, but detailed failure diagnosis depends on logs. Timing is delay-sensitive.

## Test Signals
RF init success logs, valid RF register readback after table load, correct `num_total_rfpath`, stable 20/40 MHz throughput, and no RF path B access faults on 1T1R hardware are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/rf.h

## Purpose
`rf.h` exposes the RF6052 helper surface for RTL8192EE and defines the maximum RF transmit-power index constant used by RF-related code.

## Important APIs, Types, And Functions
It defines `RF6052_MAX_TX_PWR` as `0x3F` and declares `rtl92ee_phy_rf6052_set_bandwidth` and `rtl92ee_phy_rf6052_config`.

## Control Flow
No control flow is implemented. Callers invoke config during PHY/RF initialization and bandwidth programming during channel-width changes.

## State And Persistence Behavior
No state is stored here. RF state is in `rtlpriv->phy` and hardware RF registers.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw` and is consumed by `phy.c` and `rf.c`. It is part of the local contract between generic PHY initialization and RF6052-specific behavior.

## Risks
The interface is narrow. The main risk is semantic: callers must use supported bandwidth values and call config before bandwidth changes so cached RF channel values are valid.

## Test Signals
Build coverage plus RF init and bandwidth-switch runtime tests cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/rf.h -->
