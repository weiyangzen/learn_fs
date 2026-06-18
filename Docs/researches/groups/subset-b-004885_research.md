# subset-b-004885 research

This grouped report covers the requested Realtek rtlwifi 8192C/8192D source files. Each file section is bounded with the required reconciliation markers and has a source-path title so it can be split directly into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/trx.c

Purpose: Implements the RTL8192CE PCIe transmit and receive descriptor path. It translates mac80211 skb metadata into 92C hardware descriptors, maps hardware queues to firmware queue selectors, decodes RX descriptors into `rtl_stats` and `ieee80211_rx_status`, performs RSSI/EVM signal translation, exposes generic descriptor get/set helpers to the PCI core, and kicks hardware TX polling registers.

Important APIs/functions: `_rtl92ce_map_hwqueue_to_fwqueue()` selects `QSLT_BEACON`, `QSLT_MGNT`, or skb priority. `rtl92ce_rx_query_desc()` parses descriptor fields, handles robust-management decryption flag correction, maps rates with `rtlwifi_rate_mapping()`, and invokes `_rtl92ce_translate_rx_signal_stuff()` when PHY status is present. `rtl92ce_tx_fill_desc()` DMA maps the skb, fills rate, security, AMPDU, RTS/CTS, bandwidth, segment, buffer-address, MAC ID, and multicast bits. `rtl92ce_tx_fill_cmddesc()` builds a firmware command/beacon queue descriptor. `rtl92ce_set_desc()`, `rtl92ce_get_desc()`, `rtl92ce_is_tx_desc_closed()`, and `rtl92ce_tx_polling()` are the PCI ring integration hooks.

Control flow: TX starts with skb/frame classification, DMA mapping, optional station lookup under RCU, `rtl_get_tcb_desc()`, descriptor zeroing, first-segment-only rate/protection programming, segment ownership fields, buffer address programming, and optional hardware sequence enable for firmware-controlled power save. RX starts with descriptor bit extraction, status population, optional PHY status parsing, signal scaling, and return to the caller for mac80211 receive handling.

State and persistence: The file writes transient descriptor memory and persistent hardware DMA ownership bits. It reads `rtlpriv->dm.useramask`, `rtl_mac` operating mode/bandwidth/BSSID, power-save state, and station private rate indexes. DMA mappings persist until ring cleanup elsewhere; incorrect ownership or buffer address state can wedge TX/RX rings.

Dependencies/integration: Depends on `../pci.h`, `../base.h`, `../stats.h`, 8192CE register/PHY definitions, mac80211 frame helpers, DMA APIs, CAM/security state, and rtlwifi common rate/signal helpers. It is wired into the 8192CE PCI HAL ops by the surrounding driver.

Risks: DMA mapping failure exits after logging but leaves higher layers dependent on cleanup behavior. Descriptor bit layout must match `trx.h`; any field drift corrupts DMA. RX robust-management handling is security-sensitive. `rtl92ce_is_tx_desc_closed()` ignores the requested `index` and checks `ring->idx`, which is worth regression testing if ring indexing changes. The beacon descriptor ownership exception is hardware-specific.

Test signals: Exercise PCIe TX with data, management, nullfunc, fragmented, multicast, encrypted, and AMPDU frames; verify DMA mappings are unmapped by ring completion code. RX tests should validate CRC/ICV flags, HT/40 MHz rate mapping, robust management frame decryption handling, RSSI/EVM reporting, and beacon/probe/data receive paths. Hardware tests should confirm `REG_PCIE_CTRL_REG` polling per queue and no stuck OWN bits under suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/trx.h

Purpose: Defines the RTL8192CE PCIe RX/TX descriptor contract used by `trx.c` and the PCI rtlwifi core. It contains descriptor sizes, offsets, inline bitfield accessors, packed firmware/RX/TX descriptor structs, and the exported TX/RX descriptor API prototypes.

Important APIs/types: Constants include `TX_DESC_SIZE` 64, `RX_DESC_SIZE` 32, `TX_DESC_NEXT_DESC_OFFSET` 40, and `USB_HWDESC_HEADER_LEN` 32 despite PCIe usage. Inline setters cover packet size, offset, BMC, HTC, segment bits, OWN, MAC ID, queue selector, rate ID, security type, sequence, RTS/CTS, bandwidth/subcarrier, retry fallback limits, buffer size/address, and next descriptor address. RX accessors parse packet length, CRC, ICV, driver-info size, shift, PHY status, software decrypt, OWN, PAGGR/FAGGR, MCS, HT, short preamble, bandwidth, TSF low, and buffer address. `struct rx_fwinfo_92c`, `struct tx_desc_92c`, and `struct rx_desc_92c` document the packed hardware layout.

Control flow: This header has no runtime flow, but its inline helpers are the only supported way for PCIe code to set descriptor dwords. `clear_pci_tx_desc_content()` zeros only up to `TX_DESC_NEXT_DESC_OFFSET`, preserving next-descriptor linkage in ring descriptors.

State and persistence: The structures describe DMA-visible memory shared with hardware. OWN bits and buffer/next-address fields persist across CPU/hardware ownership transitions. The use of little-endian helpers is critical because descriptor memory is consumed by the device, not just the CPU.

Dependencies/integration: Used by 8192CE TX/RX implementation, PCI ring management, and rtlwifi descriptor abstraction (`HW_DESC_*`). It relies on kernel bit helpers `le32_get_bits()` and `le32p_replace_bits()`, and on common enums such as `rtl_desc_qsel`.

Risks: Packed bitfield structs are documentation-like and can be compiler-sensitive if directly relied on; the inline le32 helpers are safer. Wrong masks or dword offsets produce silent hardware failures. `clear_pci_tx_desc_content()` intentionally preserves ring links, so replacing it with full `memset()` can break the TX ring.

Test signals: Descriptor unit tests can validate each inline helper against expected little-endian dword values. Integration tests should watch for valid DMA buffer addresses, stable next-desc pointers after fill, RX EOR/OWN recycling, and correct handling on big-endian or sparse-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/Makefile

Purpose: Builds the `rtl8192cu` USB driver module from its per-device implementation objects and connects it to `CONFIG_RTL8192CU`.

Important APIs/types/functions: The object list is `dm.o`, `hw.o`, `led.o`, `mac.o`, `phy.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`. `obj-$(CONFIG_RTL8192CU) += rtl8192cu.o` binds the composite object to the kernel Kconfig symbol.

Control flow: No runtime control flow. At build time, Kbuild combines the listed objects into `rtl8192cu.o`; `sw.o` provides module/USB driver registration, while other objects provide HAL operations referenced from the configuration tables.

State and persistence: Build artifact only. The ordering matters only for link visibility and reproducibility, not runtime initialization order.

Dependencies/integration: The module relies on shared rtlwifi infrastructure and shared 8192C/8192CE headers included from the C files. Omitting any object breaks HAL op resolution, firmware/table access, or USB TRX behavior.

Risks: Since `mac.o` contains functions also used by PCIe-family code concepts, moving it can affect symbol ownership. Kconfig-disabled builds should not compile this module. New source files require explicit addition here.

Test signals: `make M=drivers/net/wireless/realtek/rtlwifi/rtl8192cu` or an equivalent subtree build should produce one module with no unresolved symbols. Modpost should include firmware declarations from `sw.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/def.h

Purpose: Extends/reuses RTL8192CE definitions for the USB 8192CU/8188CU variant. It imports `../rtl8192ce/def.h` and overlays chip-version bits and helpers specific to 8192CU chip identification.

Important APIs/types/functions: Defines `NORMAL_CHIP`, `CHIP_VENDOR_UMC`, `CHIP_VENDOR_UMC_B_CUT`, `IS_92C_1T2R(version)`, `IS_VENDOR_UMC(version)`, `CHIP_BONDING_92C_1T2R`, and `CHIP_BONDING_IDENTIFIER(_value)`. These are used by `mac.c`, `hw.c`, and `sw.c` to decode `REG_SYS_CFG`/`REG_HPON_FSM`, choose RF path counts, choose firmware variants, and select high-power/board behaviors.

Control flow: No runtime flow, but the macros drive branch decisions during chip-version reading, firmware selection, EEPROM parsing, RF table selection, and special UMC cut workarounds.

State and persistence: Encodes version bits stored in `rtlhal->version`. Those bits persist in driver state after probe and are used throughout the device lifetime.

Dependencies/integration: Depends on the CE definition header for base enum values such as `CHIP_92C_1T2R` and version constants. It is a compatibility layer between CU code and the shared 8192C/CE family definitions.

Risks: Bit definitions differ from 8192D and some other Realtek families. Accidentally mixing `def.h` versions can mis-detect RF type or vendor cut, leading to wrong firmware, wrong RF table, or unsafe tx-power programming.

Test signals: Probe logs should identify expected chip version and RF type for 8188CU 1T1R, 8192CU 2T2R, and UMC A/B cut devices. Firmware filename selection should match those decoded bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/dm.c

Purpose: Provides the CU-specific dynamic transmit power adjustment hook used by the common rtl8192c dynamic-management watchdog. It reduces transmit power for near-field conditions based on smoothed PWDB signal levels and restores normal power when the peer is farther away.

Important APIs/functions: `rtl92cu_dm_dynamic_txpower()` checks `rtlpriv->dm.dynamic_txpower_enable`, `HAL_DM_HIPWR_DISABLE`, link state, AP/STA/adhoc mode, `undec_sm_pwdb` or `entry_min_undec_sm_pwdb`, and updates `dynamic_txhighpower_lvl`. On transitions it calls `rtl92c_phy_set_txpower_level()`, `dm_restorepowerindex()`, or `dm_writepowerindex()` with calibrated index values.

Control flow: Disabled paths return immediately. If unlinked and no minimum undecoded PWDB exists, the function resets to normal. For linked/ad-hoc/AP extension cases it selects a signal source, compares against `TX_POWER_NEAR_FIELD_THRESH_LVL2` and `TX_POWER_NEAR_FIELD_THRESH_LVL1` with hysteresis, then applies a power-level transition only when the level changed from `last_dtp_lvl`.

State and persistence: Mutates `rtlpriv->dm.dynamic_txhighpower_lvl` and `last_dtp_lvl`; indirectly updates BB/RF tx power registers. It relies on shared DM state populated by RX signal processing and common watchdog code.

Dependencies/integration: Called via `.dm_dynamic_txpower` in `rtl8192cu_hal_ops`. Uses shared helpers from `../rtl8192ce/dm.h` and 8192C PHY code. Its result influences RF tx-power writes in `rf.c`, which checks `dynamic_txhighpower_lvl`.

Risks: Threshold hysteresis is hard-coded; bad signal smoothing can cause power oscillation or underpowered links. `TXHIGHPWRLEVEL_LEVEL2` is handled in write logic but this CU function only sets normal or level1 in visible branches. Power changes during active scanning/association need hardware testing.

Test signals: Verify tx-power register changes as RSSI/PWDB crosses near-field thresholds, with no repeated writes when level is unchanged. Test linked STA, adhoc, unlinked, and HIPWR-disable cases. Monitor throughput and regulatory tx-power behavior after transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/dm.h

Purpose: Declares CU dynamic-management interfaces while importing the CE dynamic-management definitions that hold shared thresholds, enums, and helper prototypes.

Important APIs/types/functions: Includes `../rtl8192ce/dm.h`, then declares `rtl92cu_dm_dynamic_txpower()`, `dm_savepowerindex()`, `dm_writepowerindex()`, and `dm_restorepowerindex()`. The `dm_*powerindex` helpers are implemented in shared code but used by CU dynamic tx-power transitions.

Control flow: Header only. Its declarations let `hw.c`, `sw.c`, and `dm.c` wire the dynamic tx-power callback into `rtl_hal_ops`.

State and persistence: No direct state. It exposes functions that operate on `rtlpriv->dm` and PHY power index registers.

Dependencies/integration: Bridges CU files to CE/common dynamic-management support. Because CU borrows CE DM declarations, changes in the CE header affect CU compile and behavior.

Risks: Prototype drift between this header and shared implementations would be caught at compile time. Semantic drift in CE DM constants can alter CU tx-power behavior without changing this file.

Test signals: Build should verify prototypes. Runtime watchdog testing should confirm `.dm_dynamic_txpower` invokes the CU implementation and shared power-index save/write/restore functions resolve correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/hw.c

Purpose: Main RTL8192CU hardware bring-up, shutdown, EEPROM parsing, register get/set, media/beacon control, rate-mask programming, power-state, and GPIO radio switch implementation. It is the central USB HAL backend used by `sw.c`.

Important APIs/functions: `rtl92cu_read_eeprom_info()` selects EEPROM/efuse boot source, reads adapter info, tx-power tables, board type, OEM ID, and LED behavior. `_rtl92cu_init_mac()` powers the device, initializes LLT, queue pages, TRX buffers, endpoint priority, interrupts, WMAC filters, EDCA/rate fallback/retry, bandwidth, and beacon parameters. `rtl92cu_hw_init()` chains MAC init, firmware download, table selection, MAC/BB/RF config, CAM reset, security setup, IQ/LC calibration, PA bias, and DM init. `rtl92cu_card_disable()` performs RF, digital, GPIO, and analog shutdown. `rtl92cu_set_hw_reg()` and `rtl92cu_get_hw_reg()` multiplex many core hardware variables. `rtl92cu_update_hal_rate_tbl()` builds rate tables or firmware rate masks. `rtl92cu_gpio_radio_on_off_checking()` reads GPIO/powerdown state under `rf_ps_lock`.

Control flow: Probe-time flow is chip version read in `mac.c`, firmware buffer setup in `sw.c`, EEPROM read, endpoint mapping, then `hw_init`. Hardware init temporarily enables IRQs because it can take hundreds of milliseconds, then restores flags before returning. Join/report flow sends reserved-page/H2C commands via scheduled work to avoid USB I/O in atomic context. Card disable clears link/media state, LEDs, RF PS levels, and runs one of two disable sequences depending on `rtlusb->disablehwsm`.

State and persistence: Maintains `rtlhal->fw_ready`, `hw_type`, `last_hmeboxnum`, `rtlphy->hwparam_tables`, RF channel values, IQK initialized flag, EEPROM tx-power arrays, board/OEM identity, `rtlusb->reg_bcn_ctrl_val`, MAC filters, security config, rate masks, PS flags, and hardware registers. EEPROM-derived tx-power state persists for channel changes and regulatory calculations.

Dependencies/integration: Depends on rtlwifi USB core, efuse, CAM, PS, firmware common, 8192C common PHY/DM, CE hw/phy headers, CU TRX/LED/table code, and mac80211 interface types. Exported through `rtl8192cu_hal_ops` in `sw.c`.

Risks: Highly register-order-sensitive. `usb_cmd_send_packet()` intentionally frees the skb and does not send a command packet; comments associate this with WPA2 802.11n traffic stops, making reserved-page/H2C behavior a notable risk. `rtl92cu_update_interrupt_mask()` is empty. `rtl92cu_gpio_radio_on_off_checking()` sets `hwradiooff = true` even in the `actuallyset` branch before checking the target state, which is subtle. Rate-mask update copies five bytes into shared state then schedules work, so races with station teardown need coverage. Init temporarily re-enables IRQs and assumes device interrupts remain disabled.

Test signals: Cold probe, warm reset, suspend/resume-like disable/enable, firmware download failure, EEPROM autoload failure, 8188/8192 and high-PA boards, AP/STA/adhoc media transitions, beacon interval updates, hardware crypto, reserved-page H2C join reports, GPIO radio toggle, LPS/RPWM transitions, and rate-mask updates under traffic. Register traces should confirm init/shutdown sequences match vendor expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/hw.h

Purpose: Declares RTL8192CU hardware constants and HAL entry points for init, security, register access, beacon control, rate updates, firmware commands, and radio checks.

Important APIs/types/functions: Defines LLT/page allocation constants such as `TX_TOTAL_PAGE_NUMBER`, `TX_PAGE_BOUNDARY`, chip A/B and WMM queue page sizes, board type masks, `enum _BOARD_TYPE_8192CUSB`, `IS_HIGHT_PA(boardtype)`, and `RTL92C_DRIVER_INFO_SIZE`. Prototypes include `rtl92cu_read_eeprom_info()`, `rtl92cu_hw_init()`, `rtl92cu_card_disable()`, `rtl92cu_set_hw_reg()`, `rtl92cu_get_hw_reg()`, `rtl92cu_update_channel_access_setting()`, `rtl92cu_gpio_radio_on_off_checking()`, firmware H2C wrappers, and `rtl92cu_update_hal_rate_tbl()`.

Control flow: Header only, but constants shape `hw.c` init logic for queue page reservation, high-power table selection, and board behavior.

State and persistence: Constants define persistent hardware packet-buffer partitioning and board-type interpretation. Function prototypes operate on `rtl_priv`, `rtl_hal`, `rtl_phy`, `rtl_usb`, `rtl_efuse`, and `rtl_ps_ctl` state.

Dependencies/integration: Included by `hw.c` and `sw.c`; it also exposes shared firmware functions from rtl8192c common code used by CU HAL ops. It ties Kbuild-visible CU code to common rtlwifi hardware variable enums.

Risks: Page-number constants must match firmware and endpoint mapping. `IS_HIGHT_PA` spelling is nonstandard but used as API; renaming can break callers. Board-type masks are used directly against EEPROM fields, so changes must be validated on real hardware variants.

Test signals: Compile coverage for all prototypes, endpoint-count/page-reservation hardware tests for one/two/three OUT endpoints, and high-power board detection checks through EEPROM fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/led.c

Purpose: Implements basic software LED register manipulation and LED-action filtering for RTL8192CU USB devices.

Important APIs/functions: `rtl92cu_sw_led_on()` writes `REG_LEDCFG2` for `LED_PIN_LED0` and `LED_PIN_LED1`; `LED_PIN_GPIO0` is a no-op. `rtl92cu_sw_led_off()` writes off-state bits, honoring `rtlpriv->ledctl.led_opendrain` for LED0. `rtl92cu_led_control()` currently filters LED actions when RF is off for reasons stronger than power save, then logs the action without state-machine blinking behavior.

Control flow: LED on/off read the current LED config byte, mask the nibble associated with the selected LED, and write back hardware-specific bit combinations. `led_control` returns early for TX/RX/survey/link/power-on actions when RF-off reason indicates the device should not show active state.

State and persistence: Writes persistent LED config registers until changed or power-cycled. Reads `led_opendrain` set by HP/OEM customization in `hw.c` and `ppsc->rfoff_reason`.

Dependencies/integration: Wired into `.led_control` in `sw.c`; direct on/off helpers are available through `led.h`. Depends on `../usb.h`, `REG_LEDCFG2`, `enum rtl_led_pin`, and `enum led_ctl_mode`.

Risks: `rtl92cu_led_control()` does not call on/off helpers, so link/TX/RX blinking may be intentionally unimplemented or handled elsewhere. Incorrect open-drain handling can invert or leave LEDs stuck on certain HP boards. GPIO0 is unsupported here.

Test signals: Manual LED tests on normal and HP open-drain devices, RF-off action suppression checks, and register trace verification for LED0/LED1 on/off paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/led.h

Purpose: Declares the RTL8192CU LED control functions implemented in `led.c`.

Important APIs/functions: `rtl92cu_sw_led_on()`, `rtl92cu_sw_led_off()`, and `rtl92cu_led_control()` accept `struct ieee80211_hw *` plus LED pin or LED action enums from the rtlwifi core.

Control flow: Header only. The prototypes allow `sw.c` to install `.led_control` and other CU code to manipulate LED pins.

State and persistence: No direct state, but exposed functions write LED registers and consult power-save/OEM LED state.

Dependencies/integration: Guarded by `__RTL92CU_LED_H__`; depends on enum definitions from included rtlwifi headers at the call site.

Risks: If LED state-machine behavior is later added, this header is the public CU surface. Missing declarations for any new helper will produce compile errors in `sw.c` or `hw.c`.

Test signals: Build validation and runtime LED action checks through the HAL `.led_control` callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/mac.c

Purpose: Provides shared RTL8192C MAC-layer support compiled into the USB CU module: chip-version decode, LLT setup, CAM key programming, interrupt mask enable/disable, QoS/EDCA/rate fallback initialization, network type programming, and RX PHY-signal translation.

Important APIs/functions: `rtl92c_read_chip_version()` decodes `REG_SYS_CFG` and `REG_HPON_FSM` into `rtlhal->version` and `rtlphy->rf_type`. `rtl92c_llt_write()` and `rtl92c_init_llt_table()` initialize the logical link table. `rtl92c_set_key()` manages CAM entries for WEP/TKIP/AES, group/pairwise/default keys, AP/mesh free-entry allocation, and deletion. Interrupt helpers write `REG_HIMR/HIMRE` using PCI or USB masks depending on hardware type. EDCA/rate functions program SIFS, retry, fallback, aggregation, and min-space registers. `_rtl92c_query_rxphystatus()` and `rtl92c_translate_rx_signal_stuff()` derive RSSI, EVM, PWDB, signal quality, and beacon/self/BSSID matching.

Control flow: Chip identification runs early during probe. LLT initialization writes a linear TX page list, marks boundary-1 as end, then creates a ring buffer for the remaining pages. Key programming either clears CAM entries, deletes empty keys, or writes CAM entries. RX signal flow computes CCK or OFDM/HT signal metrics and feeds `rtl_process_phyinfo()`.

State and persistence: Writes `rtlhal->version`, `rtlphy->rf_type`, `rtlpriv->dm.rfpath_rxenable`, CAM hardware entries, interrupt registers, MAC timing registers, and statistics such as SNR. Key buffers in `rtlpriv->sec` determine CAM content.

Dependencies/integration: Used by `hw.c`, `sw.c`, and `trx.c`; depends on PCI and USB structs because interrupt logic supports both. Integrates with rtlwifi CAM, stats, base, firmware/rate helpers, and 8192C common definitions.

Risks: CAM entry selection is security-sensitive, especially AP/mesh free-entry handling and default key modes. The file is in the CU directory but includes PCI paths and hardware-type branches, so changes can have wider family implications. RX signal formulas include hardware-tuned offsets; altering them affects roaming and rate control. LLT polling timeout failure aborts MAC init.

Test signals: Probe version logs for chip variants, LLT timeout injection, hardware crypto connect/disconnect for WEP/TKIP/CCMP/group keys, interrupt mask enable/disable, WMM/EDCA parameter checks, and RX RSSI/EVM correlation against known signal levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/mac.h

Purpose: Declares RTL8192C MAC helper functions and RX descriptor/firmware-info structures used by CU TRX and hardware initialization code.

Important APIs/types: Defines LLT and beacon timing constants, prototypes for chip version, LLT, CAM keys, interrupts, QoS, EDCA/rate/retry/beacon/min-space helpers, `rtl92c_get_txdma_status()`, `rtl92c_map_hwqueue_to_fwqueue()`, and `rtl92c_translate_rx_signal_stuff()`. `struct rx_fwinfo_92c` captures PHY status bytes; `struct rx_desc_92c` documents RX descriptor bitfields.

Control flow: Header only. It creates the compile-time contract between `mac.c`, `hw.c`, `trx.c`, and the HAL ops in `sw.c`.

State and persistence: The declared functions read/write hardware MAC registers, CAM state, interrupt masks, and signal statistics. The RX structs describe DMA-delivered state.

Dependencies/integration: Included by CU MAC/TRX/HW/SW files. Uses mac80211 types, rtlwifi `rtl_stats`, descriptor queue enums, and hardware rate definitions inherited from surrounding includes.

Risks: Struct bitfields mirror hardware and should not be used as a portable serialization mechanism when le32 helpers are available. Prototype/order drift with `mac.c` or common users breaks the module. The `rtl92c_init_edca_param()` declaration parameter names differ in order from the implementation names, so callers must rely on position.

Test signals: Build coverage, RX descriptor parsing checks, and HAL op invocation tests for each declared initializer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/phy.c

Purpose: Implements RTL8192CU PHY and RF-register access wrappers, MAC/BB/RF table replay, bandwidth switching, BB enable, LC calibration, and RF power-state transitions.

Important APIs/functions: `rtl92cu_phy_query_rf_reg()` and `rtl92cu_phy_set_rf_reg()` choose direct 3-wire or firmware-mediated RF serial access based on `rtlphy->rf_mode` and apply bit masks. `rtl92cu_phy_mac_config()` replays MAC tables. `rtl92cu_phy_bb_config()` enables BB/RF clocks and delegates baseband config to common code. `_rtl92cu_phy_config_bb_with_headerfile()` and `_rtl92cu_phy_config_bb_with_pgheaderfile()` replay PHY/AGC/power-group tables selected for 1T/2T/high-PA boards. `rtl92cu_phy_config_rf_with_headerfile()` replays RF path A/B tables. `rtl92cu_phy_set_bw_mode_callback()` updates MAC/BB/RF bandwidth registers. `_rtl92cu_phy_lc_calibrate()` performs LC calibration with TX paused or RF mode saved/restored. `rtl92cu_phy_set_rf_power_state()` wraps ERFON/ERFOFF/ERFSLEEP transitions.

Control flow: Init-time flow configures BB register definitions, enables clocks/resets, applies table arrays, configures RF paths, then later channel/bandwidth changes call the bandwidth callback. RF power-state transitions may call NIC enable/disable, CE RF-on/sleep helpers, LED updates, and queue drain waits.

State and persistence: Updates RF registers, BB registers, `rtlphy->set_bwmode_inprogress`, `rtlphy->rfreg_chnlval`, `rtlphy->pwrgroup_cnt`, `ppsc->rfpwr_state`, and sleep/awake jiffies. Table replay persists hardware calibration state.

Dependencies/integration: Depends on 8192C common PHY/DM/FW helpers, CU RF/table data, CE PHY declarations, rtlwifi PS/core APIs, and mac80211 channel width state.

Risks: `rtl92cu_phy_set_rf_power_state()` references PCI private TX rings (`rtl_pcipriv`, `rtl8192_tx_ring`) in a CU file, which is a transport-coupling risk and could be unsafe for USB-only contexts if executed. Bandwidth and LC calibration sequences are register-order-sensitive. Table lengths must match arrays. RF path C/D are logged or ignored.

Test signals: RF register read/write mask tests, 1T/2T and high-PA table replay traces, 20/40 MHz bandwidth switching with sideband changes, LC calibration under active and idle TX, IPS/LPS RF on/off transitions, and build/runtime checks for USB devices invoking RF power-state paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/phy.h

Purpose: Declares CU PHY entry points while importing the CE PHY header for shared RTL8192C definitions.

Important APIs/functions: Exposes BB enable, RF path legality, IO command, MAC/BB/RF table configuration, RF register query/set, LC calibration, bandwidth callback, and RF power-state functions. It includes `../rtl8192ce/phy.h`, so many common 8192C PHY constants and prototypes are inherited.

Control flow: Header only. These prototypes are consumed by `hw.c`, `rf.c`, and `sw.c` HAL operation setup.

State and persistence: Exposed functions manipulate `rtl_phy`, RF/BB registers, channel bandwidth state, power state, and table-derived calibration data.

Dependencies/integration: Bridges CU code to common/CE PHY infrastructure. `rtl8192_phy_check_is_legal_rfpath()` is implemented in common 8192C PHY code and exported there.

Risks: Because this header layers on CE PHY declarations, incompatible CE changes can affect CU. Duplicate declarations of common functions must remain ABI-compatible. Any new PHY callback added to `rtl_hal_ops` needs a matching declaration here or in included common headers.

Test signals: Compile with `CONFIG_RTL8192CU`, static symbol resolution for common PHY exports, and runtime exercise of each HAL PHY callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/reg.h

Purpose: Reuses the RTL8192CE register definitions for the USB CU driver by including `../rtl8192ce/reg.h`.

Important APIs/types/functions: No local macros beyond the SPDX/header comments and include. All register names used by CU code, such as `REG_SYS_CFG`, `REG_APS_FSMCO`, `REG_RQPN`, `REG_BCN_CTRL`, descriptor status registers, and bit masks, come from the CE register header.

Control flow: Header only. Compile-time aliasing lets CU implementation share the same register symbolic names as CE.

State and persistence: No direct state. It defines the symbolic map for hardware register reads/writes throughout the CU module.

Dependencies/integration: Every CU file that includes `reg.h` depends on CE register definitions staying compatible with 8192CU. This mirrors the shared 8192C silicon register layout.

Risks: USB-specific registers and PCIe-specific registers share a namespace; relying on CE definitions requires care where transport-specific offsets differ. Any change to the CE reg header affects CU builds and runtime register programming.

Test signals: Build coverage and hardware register traces for CU init, endpoint mapping, USB power, LED, and TRX paths to confirm all imported addresses match USB silicon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/rf.c

Purpose: Implements RTL8192CU RF6052 transmit-power programming, bandwidth RF-register adjustment, and RF table configuration.

Important APIs/functions: `rtl92cu_phy_rf6052_set_bandwidth()` toggles RF channel/bandwidth bits for 20 or 20/40 MHz. `rtl92cu_phy_rf6052_set_cck_txpower()` computes CCK AGC values from channel power levels, dynamic tx-high-power state, external PA, and regulatory offsets, then writes CCK TXAGC BB registers. `rtl92c_phy_get_power_base()` builds OFDM/MCS base power from EEPROM channel power and HT/legacy diffs. `_rtl92c_get_txpower_writeval_by_regulatory()` applies regulatory modes 0-3 and customer limits. `_rtl92c_write_ofdm_power_reg()` clamps per-rate bytes and writes OFDM/MCS TXAGC registers. `rtl92cu_phy_rf6052_set_ofdm_txpower()` iterates six register groups. `rtl92cu_phy_rf6052_config()` and `_rtl92c_phy_rf6052_config_parafile()` configure one or two RF paths from table arrays.

Control flow: Channel/power changes compute bases, regulatory write values, clamp to `RF6052_MAX_TX_PWR`, and write BB registers. RF init determines `num_total_rfpath` from `rtlphy->rf_type`, enables RF interface bits, replays RF path tables, then restores RF environment bits.

State and persistence: Uses EEPROM-derived tx-power arrays, `rtlphy->mcs_offset`, `rtlphy->current_chan_bw`, `rtlphy->rfreg_chnlval`, `rtlphy->num_total_rfpath`, `rtlpriv->dm.dynamic_txhighpower_lvl`, and `rtlefuse->external_pa/eeprom_regulatory`. Writes persistent RF/BB TX power registers.

Dependencies/integration: Called through HAL ops in `sw.c` and common PHY code. Depends on CU table arrays, `rtl_set_bbreg()`, `rtl_set_rfreg()`, and EEPROM parsing in `hw.c`.

Risks: Regulatory and tx-power calculations are safety-sensitive. Underflow can occur in the BT1 adjustment (`writeval - 0x06060606`) if values are low before unsigned subtraction. External PA clipping only occurs in the scanning CCK branch. Incorrect table selection for 1T/2T/high-PA devices can misprogram RF paths.

Test signals: Per-channel tx-power verification, regulatory mode fixtures, dynamic tx-power transitions, external PA scan behavior, RF path count tests, 20/40 MHz bandwidth changes, and spectrum/regulatory compliance measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/rf.h

Purpose: Declares CU RF6052 helper functions and RF constants.

Important APIs/functions: Defines `RF6052_MAX_TX_PWR` as `0x3F` and `RF6052_MAX_PATH` as 2. Declares bandwidth, CCK tx-power, OFDM tx-power, RF config, and RF-table replay functions. It includes both `rtl92c_*` and `rtl92cu_*` CCK/OFDM tx-power prototypes; the implemented CU functions are the `rtl92cu_*` variants used by HAL ops.

Control flow: Header only. Prototypes allow `phy.c`, `hw.c`, and `sw.c` to call RF helpers.

State and persistence: Exposed functions modify RF/BB bandwidth and tx-power registers and consume EEPROM/PHY state.

Dependencies/integration: Used by CU PHY/HW/SW and tied to RF6052 hardware. The duplicate/common-looking prototypes reflect shared 8192C naming conventions.

Risks: The `rtl92c_phy_rf6052_set_*` prototypes do not correspond to implementations in this CU file under those names, so callers should use HAL ops or the CU-named functions unless shared symbols exist elsewhere. Constant changes affect tx-power clamping and path loops.

Test signals: Build symbol resolution, HAL op invocation of CU-named functions, and tx-power clamp checks at values above `0x3F`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/sw.c

Purpose: Module and USB driver glue for RTL8192CU/8188CU. It allocates firmware state, declares module parameters and firmware files, wires CU implementations into `rtl_hal_ops`, defines USB interface parameters, maps rtlwifi abstract registers/constants, declares supported USB IDs, and registers the `usb_driver`.

Important APIs/functions: `rtl92cu_init_sw_vars()` initializes DM defaults, allocates a 0x4000 firmware buffer, chooses firmware (`rtl8192cufw_A.bin`, `_B.bin`, or `_TMSC.bin`) based on chip cut/version, and requests firmware asynchronously with `rtl_fw_cb`. `rtl92cu_deinit_sw_vars()` frees firmware memory. `rtl92cu_get_btc_status()` returns false. `rtl8192cu_probe()` delegates to `rtl_usb_probe()`. `module_usb_driver()` registers `rtl8192cu_driver`.

Control flow: On module load, USB IDs are registered. Probe calls rtlwifi USB core with `rtl92cu_hal_cfg`; core invokes HAL ops for chip/version, EEPROM, init, TRX, PHY, security, LED, and DM. Firmware request is asynchronous, so hardware init must handle firmware readiness through rtlwifi callback state. Disconnect delegates to `rtl_usb_disconnect`.

State and persistence: Stores firmware buffer pointer and `max_fw_size`, module parameters `swenc`, `debug_level`, `debug_mask`, USB interface config (`rx_urb_num`, `rx_max_size`, handlers), maps array entries, and the static USB ID table. Disables hub-initiated LPM in the USB driver struct.

Dependencies/integration: Integrates all CU files plus common rtlwifi core, USB, efuse, base, firmware common, PHY common, and mac80211/USB module infrastructure. The `rtl_hal_cfg` maps abstract rtlwifi constants to 8192C register/bit values used by common code.

Risks: Firmware selection depends on `rtlhal.version` being valid before `init_sw_vars`; ordering must be preserved by probe. Firmware allocation failure returns `1` rather than a conventional negative errno. Large USB ID table changes can affect device binding. PM callbacks are commented out, so suspend/resume coverage may be limited. The empty BTC status disables Bluetooth coexistence behavior.

Test signals: Module load/unload, firmware request success/failure, probe on representative Realtek/customer USB IDs, software crypto module parameter, debug parameters, RX/TX URB count behavior, LPM behavior on USB hubs, and full HAL op smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/table.c

Purpose: Provides static RTL8192CU hardware programming tables for MAC, PHY, AGC, RF path A/B, power-group offsets, and high-power board variants. These arrays are replayed by `hw.c`, `phy.c`, and `rf.c` during initialization and tx-power setup.

Important APIs/data: Defines `RTL8192CUPHY_REG_2TARRAY`, `RTL8192CUPHY_REG_1TARRAY`, `RTL8192CUPHY_REG_ARRAY_PG`, `RTL8192CURADIOA_2TARRAY`, `RTL8192CU_RADIOB_2TARRAY`, `RTL8192CU_RADIOA_1TARRAY`, `RTL8192CU_RADIOB_1TARRAY`, `RTL8192CUMAC_2T_ARRAY`, `RTL8192CUAGCTAB_2TARRAY`, `RTL8192CUAGCTAB_1TARRAY`, `RTL8192CUPHY_REG_1T_HPARRAY`, `RTL8192CUPHY_REG_ARRAY_PG_HP`, `RTL8192CURADIOA_1T_HPARRAY`, and `RTL8192CUAGCTAB_1T_HPARRAY`. Most arrays are register/value pairs; power-group arrays are register/mask/value triples.

Control flow: No executable logic. Runtime code chooses arrays based on RF type and `IS_HIGHT_PA(board_type)`, then iterates by 2 or 3 entries and writes registers with delays where needed.

State and persistence: Static read-only initialization payload in the module image. Once replayed, the values persist in hardware registers until reset or changed by later channel/power logic.

Dependencies/integration: Length constants and extern declarations live in `table.h`. `_rtl92cu_phy_param_tab_init()` installs these arrays into `rtlphy->hwparam_tables`; PHY/RF config functions consume those table slots.

Risks: Array length constants must exactly match initializer counts. Values are vendor calibration data with little local validation. High-power variants differ in PHY, PG, RadioA, and AGC tables; wrong board detection can over/underdrive RF. `RTL8192CU_RADIOB_1TARRAY` is a one-entry zero table, so path B must not be meaningfully configured for 1T hardware.

Test signals: Build-time array bounds, init register trace comparison against vendor tables, 1T/2T/high-PA hardware bring-up, RF calibration success, receive sensitivity and transmit EVM checks after table replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/table.h

Purpose: Declares the RTL8192CU static hardware table arrays and their expected lengths.

Important APIs/data: Provides length macros and `extern u32` declarations for 2T/1T PHY arrays, PHY power-group arrays, RadioA/RadioB arrays, MAC array, AGC arrays, and high-power 1T/PG/RadioA/AGC variants. Includes `<linux/types.h>` for `u32`.

Control flow: Header only. The length macros drive loops in `phy.c` and table assignment in `hw.c`.

State and persistence: No direct state. The declarations expose static calibration payload stored in `table.c` and later persisted into hardware registers by replay.

Dependencies/integration: Included by `hw.c`, `phy.c`, `rf.c`, and `table.c`. The `rtlphy->hwparam_tables` indexes are assigned using these length/data pairs.

Risks: Mismatched length macros versus actual array initializers can cause truncated configuration or out-of-bounds reads. The guard macro name has a double underscore style and unusual spelling (`__RTL92CU_TABLE__H_`) but is internally consistent.

Test signals: Compile-time symbol resolution, optional static assertions if added, and init trace confirming each length is consumed with the correct pair/triple stride.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/trx.c

Purpose: Implements RTL8192CU USB endpoint mapping, mac80211 queue mapping, RX skb processing, TX descriptor construction, command descriptor construction, and minimal USB TX completion/aggregation hooks.

Important APIs/functions: `rtl8192cu_endpoint_mapping()` validates hardware endpoint configuration and fills `rtlusb->ep_map`. `rtl8192cu_mq_to_hwq()` maps mac80211 queues and frame control to rtlwifi TX queues. `_rtl8192cu_mq_to_descq()` maps to firmware descriptor QSEL values. `rtl92cu_rx_query_desc()` decodes descriptor metadata into `rtl_stats`/`rx_status`; `_rtl_rx_process()` is the actual USB RX handler that pulls descriptor/driver-info bytes and calls `ieee80211_rx()`. `rtl8192c_tx_cleanup()`, `rtl8192c_tx_post_hdl()`, and `rtl8192c_tx_aggregate_hdl()` are USB core hooks, with cleanup/post currently empty and aggregation returning one dequeued skb. `rtl92cu_tx_fill_desc()` pushes `RTL_TX_HEADER_SIZE`, fills a USB TX descriptor, and writes a checksum. `rtl92cu_tx_fill_cmddesc()` builds firmware command descriptors.

Control flow: Endpoint flow reads normal/test SIE endpoint registers, compares against enumerated USB endpoint count, and maps one/two/three OUT endpoint layouts. RX flow decodes descriptor fields, optionally parses PHY status, pulls metadata, logs frame class, and hands skb to mac80211. TX flow computes TCB descriptor, handles AMPDU and RTS/CTS, bandwidth/subcarrier, security, rate fallback, RDG, rate-mask MAC ID, hardware sequence for LPS, multicast/BMC, OWN/segment bits, and descriptor checksum.

State and persistence: Updates `rtlusb->out_queue_sel` and endpoint map. TX mutates skb headroom and descriptor bytes consumed by USB hardware. RX consumes skb descriptor bytes and fills mac80211 RX control block. Uses station aggregation state and `rtlpriv->dm.useramask`.

Dependencies/integration: Wired by `rtl92cu_interface_cfg` in `sw.c`. Depends on USB core structs, `mac.c` signal translator, firmware common, mac80211, and `trx.h` inline descriptor helpers.

Risks: `_rtl_rx_process()` warns on short skb but continues, which can risk out-of-bounds parsing if malformed URBs are delivered. It computes `p_drvinfo` as `(rxdesc + RTL_RX_DESC_SIZE)`, which is pointer arithmetic on `__le32 *` and looks suspicious because `RTL_RX_DESC_SIZE` is byte-sized in the header. Empty cleanup/post hooks may omit accounting or DMA/error handling expected by USB core. TX requires sufficient skb headroom for descriptor push. Endpoint mapping must match actual USB descriptors.

Test signals: USB probe on one/two/three endpoint devices, malformed/short RX frame tests, RX PHY status and rate mapping, TX encrypted/AMPDU/RDG/multicast/nullfunc paths, descriptor checksum validation, skb headroom assertions, and throughput tests with aggregation disabled/enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/trx.h

Purpose: Defines RTL8192CU USB TRX constants, RX PHY-info layout, descriptor bit accessors, and public USB TX/RX helper prototypes.

Important APIs/types: Constants include `RTL92C_NUM_RX_URBS` 8, `RTL92C_NUM_TX_URBS` 32, `RTL92C_SIZE_MAX_RX_BUFFER` 15360, USB RX aggregation modes, endpoint selection bits, USB TX/RX aggregation tuning, and `RX_DRV_INFO_SIZE_UNIT`. `struct rx_drv_info_92c` mirrors PHY status. RX getters parse packet length, CRC/ICV, driver info size, shift, PHY status, software decrypt, aggregation flags, MCS/HT/short preamble/bandwidth, and TSF. TX setters fill packet size, offset, BMC/HTC/segment/OWN, MAC ID, aggregation/RDG/QSEL/rate/security, sequence, RTS/CTS, bandwidth/subcarrier, fallback limits, aggregation count, and descriptor checksum. Prototypes expose endpoint mapping, queue mapping, RX query/handler, TX hooks, and descriptor fill functions.

Control flow: Header only. It is the descriptor access layer used by `trx.c` and HAL ops.

State and persistence: Inline setters write USB TX descriptor memory that is transmitted with the skb. RX getters parse device-provided little-endian descriptor memory. Constants configure persistent USB core behavior through `sw.c`.

Dependencies/integration: Used by `trx.c`, `sw.c`, and hardware init. Depends on kernel bit helpers and rtlwifi/mac80211 types.

Risks: Descriptor offset/mask errors are hardware-fatal. `RTL92C_SIZE_MAX_RX_BUFFER` comment says `8192` while value is `15360`, so buffer sizing assumptions need care. Because setters operate on `__le32 *`, callers must pass correctly aligned descriptor memory with enough dwords.

Test signals: Descriptor bitfield unit checks, USB RX buffer stress, TX checksum verification, queue selector mapping checks, and compile coverage for all prototypes used by `rtl_hal_ops` and `rtl_hal_usbint_cfg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/Makefile

Purpose: Builds the shared RTL8192D common support object used by 8192D-family rtlwifi drivers.

Important APIs/types/functions: Defines `rtl8192d-common-objs` as `dm_common.o`, `fw_common.o`, `hw_common.o`, `main.o`, `phy_common.o`, `rf_common.o`, and `trx_common.o`. `obj-$(CONFIG_RTL8192D_COMMON) += rtl8192d-common.o` binds the composite object to the common Kconfig symbol.

Control flow: No runtime flow. Kbuild links common DM, firmware, hardware, PHY, RF, and TRX support into a reusable common module/object.

State and persistence: Build metadata only. Runtime state lives in the listed source objects.

Dependencies/integration: Downstream 8192D transport-specific drivers depend on these common symbols. The object list is the authoritative compile boundary for shared 8192D support.

Risks: Adding 8192D common functionality without updating this list causes unresolved symbols. Removing or renaming objects can break transport drivers that expect common exports. The common object is gated separately from transport-specific symbols.

Test signals: Kbuild with `CONFIG_RTL8192D_COMMON`, modpost symbol checks, and transport driver builds that depend on this common object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/def.h

Purpose: Defines RTL8192D family constants, chip-version encodings, RF operation enums, descriptor queue selectors, channel plans, CCK PHY status layout, H2C command wrapper, and tx-power EEPROM data layout.

Important APIs/types: Constants include min-spacing densities, `RF6052_MAX_TX_PWR`, RSSI/link-quality window sizes, AC interrupt masks, channel offset values, and RX queue IDs. `enum version_8192d` covers test/normal 88C/92C/8723/92D variants, UMC cuts, and 92D single/dual PHY C/D/E cuts. Macros decode chip ID fields: `GET_CVID_*`, `IS_1T1R`, `IS_1T2R`, `IS_2T2R`, `IS_92D_SINGLEPHY`, `IS_92D`, and cut checks. `enum rf_optype` selects software 3-wire or firmware RF ops. `enum rtl_desc_qsel` defines firmware queue selectors. `enum channel_plan` enumerates regulatory domain plans. `struct phy_sts_cck_8192d`, `struct h2c_cmd_8192c`, and `struct txpower_info` describe hardware/firmware data.

Control flow: Header only. The macros drive chip-version branches, RF path selection, channel-plan handling, descriptor queue selection, and tx-power parsing in 8192D common code.

State and persistence: Encoded version bits persist in HAL state after probe. `struct txpower_info` holds EEPROM/efuse power calibration arrays across channels and RF paths.

Dependencies/integration: Used by 8192D common source files and likely transport-specific 8192D drivers. Relies on common bit macros and `CHANNEL_GROUP_MAX` from surrounding rtlwifi headers.

Risks: `RF_TYPE_1T1R` is defined as an inverted mask expression for comparison through `GET_CVID_RF_TYPE`; misuse outside `IS_1T1R()` can be confusing. Version bit layouts differ from 8192CU/CE, so cross-family macro reuse is unsafe. Regulatory channel-plan constants affect allowed channel behavior when consumed by common code.

Test signals: Chip-version decode tests for all 92D single/dual PHY and cut variants, RF type selection, tx-power EEPROM parsing for both RF paths, descriptor queue mapping, and country/channel-plan behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/def.h -->
