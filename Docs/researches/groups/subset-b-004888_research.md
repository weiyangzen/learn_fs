# Research: subset-b-004888

Grouped research for the rtlwifi rtl8192du and rtl8192ee source files assigned to `subset-b-004888`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/phy.c

Purpose: This file implements the RTL8192DU PHY and RF-control programming path for the USB dual-MAC/dual-PHY 802.11n chipset. It owns BB register access wrappers, MAC/BB/RF table loading, bandwidth changes, band/channel switching, IQK/LCK calibration, RF power-state transitions, BB/RF band reconfiguration, and PA-bias initialization.

Important APIs and functions:
- `rtl92du_phy_query_bb_reg()` and `rtl92du_phy_set_bb_reg()` wrap dword BB register reads/writes with bitmask extraction/insertion and special address routing when one MAC is initializing the other PHY.
- `rtl92du_phy_mac_config()`, `rtl92du_phy_bb_config()`, `rtl92du_phy_rf_config()`, and `rtl92du_phy_config_rf_with_headerfile()` load MAC, BB, AGC, RF, and power-index table data from `table.c`.
- `rtl92du_phy_set_bw_mode()` programs 20 MHz versus 20/40 MHz MAC/BB/RF bandwidth state.
- `rtl92du_phy_sw_chnl()` is the channel switch entry point. It may switch band, updates TX power, writes RF channel/bandwidth registers, reloads IMR/RF settings, and applies or runs IQK.
- `rtl92du_phy_iq_calibrate()` and helpers run multi-pass IQK, compare candidate results, fill path A/B IQK matrices, and cache successful per-channel calibration in `rtlphy->iqk_matrix`.
- `rtl92du_phy_lc_calibrate()` and `_rtl92du_phy_lc_calibrate_sw()` run LC calibration, collect curve-count data, derive curve indexes for 2.4 GHz/5 GHz, and reload LCK settings for the current channel.
- `rtl92du_phy_set_rf_power_state()`, `rtl92du_phy_set_poweron()`, and `rtl92du_phy_check_poweroff()` manage RF on/off/sleep and dual-MAC power handoff.
- `rtl92du_update_bbrf_configuration()` applies band-specific BB/RF topology, antenna, PA, RSSI table, and RF register state.
- `rtl92du_phy_init_pa_bias()` uses EFUSE byte `0x3FA` to decide whether to run PA-bias sequences for 2G/5G path A/B.

Control flow: Initialization normally enters through `sw.c` HAL ops, which call MAC, BB, and RF config. BB config enables hardware functions, loads PHY registers, optionally stores power-index offsets when EFUSE autoload is valid, loads AGC tables, and applies crystal-cap calibration. RF config delegates to `rf.c`, which calls back to `rtl92du_phy_config_rf_with_headerfile()` for radio table programming. Runtime channel changes go through `rtl92du_phy_sw_chnl()`: it waits for LC calibration, switches wireless band for single-MAC dual-band operation, validates channel/band consistency, updates TX power and RF `RF_CHNLBW`, reloads IMR and RF synthesizer settings, and reloads or executes IQK. Bandwidth changes go through `rtl92du_phy_set_bw_mode()`, which uses both MAC registers and BB registers before calling the common RF6052 bandwidth helper.

State and persistence behavior: The file persists calibration and topology state in `struct rtl_phy`, `struct rtl_hal`, `struct rtl_efuse`, and `struct rtl_ps_ctl`. Key fields include `current_channel`, `current_chan_bw`, `rfreg_chnlval[]`, `reg_rf3c[]`, `iqk_matrix[]`, `curveindex_2g`, `curveindex_5g`, `load_imrandiqk_setting_for2g`, `during_mac0init_radiob`, `during_mac1init_radioa`, and RF power timestamps. There is no filesystem persistence; calibration state lasts for the live driver instance and shared curve arrays may be shared by both USB interfaces.

Dependencies and integration points: It depends heavily on rtlwifi core helpers (`rtl_read_*`, `rtl_write_*`, `rtl_set_bbreg`, `rtl_get_bbreg`, `rtl_set_rfreg`), rtl8192d common definitions (`reg.h`, `def.h`, `phy_common.h`, `rf_common.h`), USB speed checks, EFUSE data, power-save helpers, and table arrays from `table.c`. It is wired into the driver through HAL ops in `sw.c`, and it cooperates with `rf.c` to temporarily address the peer PHY in DUALMAC_DUALPHY mode.

Risks: The code is register-sequence dense and timing-sensitive, with many magic constants and sleeps. Incorrect dual-MAC flags can send writes to the wrong PHY. IQK/LCK flows save and restore many BB/MAC/RF registers, so missed restore paths can leave the chip deaf or stuck. Channel/band mismatch is guarded by `WARN_ONCE`, but returns without recovery. USB full-speed devices skip IMR/RF switch helpers, which may create behavior differences. RF power-state transitions rely on shared mutexes and state bits; regressions could break suspend/resume or one-interface teardown while the other interface is active.

Test signals: Useful coverage includes module load with firmware, both USB interfaces probing in both orders, 2.4 GHz and 5 GHz association, channel switches including 20/40 MHz secondary-channel changes, scan while connected, suspend/resume and IPS/LPS transitions, dual-MAC operation where one interface is absent, and debug traces for IQK/LCK success and cached reload behavior. Hardware tests should watch for warnings about band/channel mismatch and MAC power-off timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/phy.h

Purpose: This header exposes the RTL8192DU PHY service API used by the USB driver glue, RF setup code, hardware initialization, and runtime channel/power logic.

Important APIs and types: It declares BB register accessors, MAC/BB/RF configuration functions, RF table loading, bandwidth and channel switching, RF power-state transitions, power-on/off coordination, LC/IQ calibration, IQK reload, BB/RF reconfiguration, and PA-bias initialization. The exported signatures use common rtlwifi/mac80211 types such as `struct ieee80211_hw`, `enum nl80211_channel_type`, `enum rf_content`, `enum radio_path`, and `enum rf_pwrstate`.

Control flow and integration: `sw.c` installs many of these functions into `rtl_hal_ops`; `rf.c` consumes the RF table loader and peer-PHY helpers; `hw.c` and common rtl8192d code call the power, calibration, and register routines during initialization and runtime transitions.

State and persistence behavior: The header does not own state, but every API assumes the caller has valid `rtl_priv`, `rtl_hal`, `rtl_phy`, and power-save state attached to `ieee80211_hw`. State mutations occur in `phy.c`.

Dependencies: It relies on prior inclusion of rtlwifi/mac80211 definitions by C files. It has include guards and no inline behavior.

Risks and test signals: Header/API drift is the main risk. Changing prototypes must be compiled against all rtl8192du translation units and common rtl8192d callers. Build tests with `CONFIG_RTL8192DU` are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/rf.c

Purpose: This file implements RTL8192DU RF path configuration and peer-PHY power gating for single-PHY and dual-MAC/dual-PHY modes.

Important APIs and functions:
- `rtl92du_phy_enable_anotherphy()` temporarily powers and enables the other PHY so the current MAC can load RF settings into it. It chooses `MAC0_ACCESS_PHY1` or `MAC1_ACCESS_PHY0` address masks and returns whether the caller should power it back down.
- `rtl92du_phy_powerdown_anotherphy()` clears the other PHY's LSSI parameter register when the peer MAC is not on.
- `rtl92du_phy_rf6052_config()` selects the number of RF paths, handles dual-MAC path remapping, prepares RFENV/3-wire register access, calls `rtl92du_phy_config_rf_with_headerfile()`, restores RFENV, and powers down temporarily enabled peer PHYs.

Control flow: RF setup starts by deriving `num_total_rfpath` from `rtlphy->rf_type`. In DUALMAC_DUALPHY mode, MAC0 on 2.4 GHz may need to initialize radio B through PHY1, while MAC1 on 5 GHz may need to initialize radio A through PHY0. The path loop saves RFENV, enables RF serial access, configures RF address/data widths, loads radio A or B tables through `phy.c`, restores RFENV, and exits on table-load failure.

State and persistence behavior: It mutates `rtlphy->num_total_rfpath` during special dual-MAC setup and toggles `rtlhal->during_mac0init_radiob` / `during_mac1init_radioa` so BB/RF accessors route to the intended PHY. It checks peer MAC on bits (`MAC0_ON`, `MAC1_ON`) before enabling or powering down shared hardware.

Dependencies and integration points: It depends on rtlwifi core I/O, rtl8192d register definitions, common PHY helpers, and `phy.c`'s table-loader callback. It is called by `rtl92du_phy_rf_config()` from the HAL initialization flow.

Risks: The boolean parameter name `bmac0` is easy to misread because the helper selects the opposite MAC register/bit in some paths. Incorrect `during_*` flag lifetime can corrupt RF writes. Early returns when the peer MAC is already on assume that both radio tables were already loaded. Error handling is minimal after partial RF setup.

Test signals: Probe both interfaces in both orders, test DUALMAC_DUALPHY with one interface absent/present, verify RF path counts for 1T1R and 2T2R devices, and validate 2.4 GHz plus 5 GHz association after module reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/rf.h

Purpose: This header exposes the small RTL8192DU RF setup API for RF6052 configuration and peer-PHY enable/powerdown handling.

Important APIs: `rtl92du_phy_rf6052_config()` is the main RF initialization entry point. `rtl92du_phy_enable_anotherphy()` and `rtl92du_phy_powerdown_anotherphy()` are used by both `rf.c` and `phy.c` when programming another PHY in dual-MAC modes.

Control flow and integration: `phy.c` includes this header for band/channel RF switching helpers, and `sw.c` reaches RF setup through `rtl92du_phy_rf_config()`.

State and persistence behavior: The declarations imply mutation of `rtl_hal` routing flags and peer MAC/PHY power bits, but state is implemented in `rf.c` and `phy.c`.

Dependencies: It relies on `struct ieee80211_hw` and `bool` being visible from rtlwifi includes before use.

Risks and test signals: Prototype mismatch is the main risk. Build coverage with rtl8192du enabled and runtime RF initialization on dual-interface USB devices are the relevant checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/sw.c

Purpose: This file is the RTL8192DU USB driver registration and software-variable setup module. It binds the chipset-specific HAL operations, USB endpoint callbacks, module parameters, device IDs, and firmware request path into the rtlwifi USB framework.

Important APIs and structures:
- `rtl92du_get_other_intf()` finds the sibling USB interface for dual-interface devices.
- `rtl92du_init_shared_data()` shares curve-index arrays and power/hw-init mutexes between the two USB interfaces when both are present, or allocates them for the first interface.
- `rtl92du_deinit_shared_data()` frees shared allocations only when the sibling interface is absent or already disconnected.
- `rtl92du_init_sw_vars()` initializes dynamic-management defaults, initial channel, power-save settings, early mode, firmware buffer, and asynchronous firmware request.
- `rtl92du_deinit_sw_vars()` releases firmware memory and shared data.
- `rtl8192du_hal_ops`, `rtl92du_interface_cfg`, and `rtl92du_hal_cfg` wire rtl8192du-specific callbacks into common rtlwifi operations.
- `rtl8192du_probe()` delegates to `rtl_usb_probe()`, and `module_usb_driver()` registers the USB driver.

Control flow: On USB probe, `rtl_usb_probe()` uses `rtl92du_hal_cfg`, which eventually calls `rtl92du_init_sw_vars()`. Software init creates or reuses shared calibration/mutex state, initializes DM and power-save fields, allocates a 32 KiB firmware buffer, and starts `request_firmware_nowait()` for `rtlwifi/rtl8192dufw.bin`. The HAL ops table routes later core operations to `hw.c`, `phy.c`, `dm.c`, `trx.c`, `led.c`, and common rtl8192d helpers.

State and persistence behavior: Persistent live driver state includes shared `curveindex_2g`, `curveindex_5g`, `mutex_for_power_on_off`, and `mutex_for_hw_init`; per-interface `rtlpriv->dm`, `rtlpriv->psc`, `rtlpriv->phy.current_channel`, `rtlhal->disable_amsdu_8k`, `rtlhal->earlymode_enable`, and `rtlhal->pfirmware`. No disk state is written; firmware is requested from the kernel firmware loader.

Dependencies and integration points: It depends on Linux USB/module APIs, firmware loading, mac80211/rtlwifi core, rtl8192d common helpers, and local rtl8192du PHY/DM/HW/TRX/LED modules. The USB ID table maps many Realtek and vendor-rebranded VID/PIDs to `rtl92du_hal_cfg`.

Risks: Shared-data lifetime is tied to sibling interface presence and `usb_get_intfdata()`, making disconnect ordering important. If firmware request fails after shared-data allocation, `rtl92du_init_sw_vars()` frees only firmware but does not call shared-data deinit in that error path. Because firmware loading is asynchronous, later operations must tolerate firmware-not-ready state. Module parameter defaults disable inactive power save and software LPS.

Test signals: Probe/remove both interfaces in either order, unplug during firmware load, reload module repeatedly, verify firmware callback path, inspect sysfs module parameters, and exercise TX/RX, LED, power-save, channel switching, and encryption callbacks through normal association.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/table.c

Purpose: This file contains the RTL8192DU hardware programming tables consumed by PHY/RF/MAC initialization. It has no functions; it exports constant `u32` arrays of register/value or register/mask/value tuples.

Important data exports:
- `rtl8192du_phy_reg_2tarray` programs baseline BB/PHY registers.
- `rtl8192du_phy_reg_array_pg` stores per-rate/per-path power-index offset data as triples.
- `rtl8192du_radioa_2tarray` and `rtl8192du_radiob_2tarray` are RF radio A/B tables for normal PA configurations.
- `rtl8192du_radioa_2t_int_paarray` and `rtl8192du_radiob_2t_int_paarray` are RF tables for devices with internal 5 GHz PA.
- `rtl8192du_mac_2tarray` programs MAC registers during MAC config.
- `rtl8192du_agctab_array`, `rtl8192du_agctab_5garray`, and `rtl8192du_agctab_2garray` program AGC values for MAC0/all-band and MAC1 band-specific paths.

Control flow: `phy.c` iterates these arrays with fixed strides: MAC/PHY/AGC/RF tables use pairs, while the power group table uses triples. `rtl_addr_delay()` and `rtl_rfreg_delay()` handle special delay marker addresses while programming. The tables are selected based on interface index, current band, and EFUSE internal-PA flags.

State and persistence behavior: The arrays are `const` and stateless. They indirectly initialize hardware state by writes performed in `phy.c`.

Dependencies and integration points: The only source dependency is `table.h` for length macros and declarations. Runtime consumers are `rtl92du_phy_mac_config()`, `_rtl92du_phy_config_bb()`, `_rtl92du_phy_config_bb_pg()`, and `rtl92du_phy_config_rf_with_headerfile()`.

Risks: Array length macros must exactly match initializer element counts and the expected stride. Any wrong register literal can break hardware bring-up, RF performance, regulatory power, or calibration. Because values are opaque vendor tables, review is difficult and tests must be hardware based.

Test signals: Compile-time array-size checks from C initializers, successful probe/firmware load, RF calibration success, association on 2.4 GHz and 5 GHz, throughput/RSSI sanity, and regulatory/channel tests provide practical validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/table.h

Purpose: This header declares the RTL8192DU register-table lengths and exported table arrays used by PHY, RF, MAC, AGC, and power-index initialization.

Important APIs/data: It defines length macros for each table and `extern const u32` declarations for PHY register, PHY power group, radio A/B, internal-PA radio A/B, MAC, and AGC tables.

Control flow and integration: `table.c` defines the arrays; `phy.c` consumes them by using the length macros as loop bounds. Pair versus triple stride is determined by the consumer: most arrays are pairs, while `rtl8192du_phy_reg_array_pg` is triples.

State and persistence behavior: The header is declarative and stateless; the table data initializes volatile device registers at runtime.

Dependencies: It assumes `u32` is already defined by includes in the C file.

Risks and test signals: Length macro drift is the primary risk, especially because a wrong length can truncate programming or overrun an array in initialization loops. Build tests catch some mismatches; hardware probe and association tests are required to validate actual values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/trx.c

Purpose: This file implements RTL8192DU USB TX descriptor construction, simple TX aggregation handling, USB endpoint mapping, and mac80211 queue-to-hardware queue selection.

Important APIs and functions:
- `rtl92du_tx_fill_desc()` builds a Realtek TX descriptor by prepending `RTL_TX_HEADER_SIZE` bytes to the skb and setting packet length, rate, aggregation, RTS/CTS, bandwidth, encryption, queue, rate mask, QoS/RDG, MAC ID, power-save sequence, multicast/broadcast, ownership, segment flags, and checksum.
- `rtl92du_tx_aggregate_hdl()` returns one skb from the aggregate list; this driver does not coalesce multiple skbs here.
- `rtl92du_endpoint_mapping()` derives USB output endpoint queue mappings and validates endpoint topology.
- `rtl92du_mq_to_hwq()` maps mac80211 queues and management/beacon frames to Realtek hardware queues.
- `rtl92du_tx_cleanup()` and `rtl92du_tx_post_hdl()` are no-op/success hooks installed into USB interface config.

Control flow: TX starts when rtlwifi asks the HAL to fill a descriptor. The function calls `rtl_get_tcb_desc()`, pushes descriptor space, clamps CCK rates on 5 GHz to OFDM minimum, sets AMPDU state from station TID aggregation, applies RTS/CTS and bandwidth flags from `ieee80211_tx_info`, encodes hardware encryption type from key cipher, assigns queue and rate fallback controls, handles QoS/RDG and LPS null frame behavior, marks BMC/more-fragment state, and finishes with descriptor checksum. Endpoint mapping reads MAC-specific USB queue-selection registers, optionally overrides by detected out-pipe count, then maps BE/BK/VI/VO/MGT/BCN/HI queues to one, two, or three USB endpoints.

State and persistence behavior: The function mutates skb headroom/descriptors and uses live state from `rtl_priv`, `rtl_hal`, `rtl_mac`, `rtl_ps_ctl`, station private aggregation state, and `rtl_usb`. Endpoint mapping persists in `rtlusb->out_queue_sel`, `out_ep_nums`, and `ep_map`.

Dependencies and integration points: It depends on mac80211 frame/control structures, rtlwifi base/USB helpers, rtl8192d descriptor setters from `trx_common.h`, register definitions, and `trx.h` inline setters. `sw.c` registers these routines in `rtl92du_interface_cfg` and `rtl8192du_hal_ops`.

Risks: TX descriptor bitfields are hardware-sensitive. Wrong 5 GHz rate clamping can transmit invalid CCK rates. skb headroom must be sufficient for `skb_push()`. The descriptor checksum covers 16 little-endian words and must be updated after all descriptor writes. Endpoint validation rejects one-out/multiple-in combinations, so endpoint count detection matters. Queue mapping defaults invalid mac80211 queues to BE with a warning.

Test signals: Association plus data TX in 2.4/5 GHz, AMPDU traffic, encrypted WEP/TKIP/CCMP frames, management/beacon transmission, power-save null frames, one/two/three endpoint devices, and warnings from invalid queue or endpoint mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/trx.h

Purpose: This header provides RTL8192DU TX queue constants, TX page-budget constants, descriptor bitfield helpers, and TRX function declarations.

Important APIs and definitions: `TX_SELE_HQ/LQ/NQ` define USB output queue-selection bits. Page-number macros describe normal and dual-MAC queue budgets. Inline setters update descriptor BMC, aggregation-break, and checksum fields via little-endian bit replacement. Function declarations expose TX descriptor fill, endpoint mapping, mac80211-to-hardware queue mapping, aggregation, cleanup, and post-URB hooks.

Control flow and integration: `trx.c` uses the inline setters and implements the declared functions. `sw.c` registers these functions in HAL and USB interface configuration. Common rtl8192d descriptor setters from `trx_common.h` complement the local helpers.

State and persistence behavior: The header itself is stateless; helpers mutate descriptor memory passed by the caller.

Dependencies: It requires Linux bit macros, `__le32`, mac80211/USB types, and rtlwifi queue constants to be visible through including C files.

Risks and test signals: Descriptor bit positions must match hardware layout. Compile coverage catches prototype drift; TX traffic, AMPDU, BMC frames, and endpoint mapping are runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/Makefile

Purpose: This Kbuild file defines the object composition for the `rtl8192ee` PCI wireless driver module.

Important declarations: `rtl8192ee-objs` lists `dm.o`, `fw.o`, `hw.o`, `led.o`, `phy.o`, `pwrseq.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`. `obj-$(CONFIG_RTL8192EE) += rtl8192ee.o` builds the module when the kernel config option is enabled.

Control flow and integration: Kbuild links all listed translation units into one module object. This is the build-time integration point connecting dynamic management, firmware, hardware setup, LEDs, PHY/RF, power sequence, software registration, tables, and TX/RX.

State and persistence behavior: No runtime state; it controls build artifacts.

Dependencies: It depends on kernel Kbuild conventions and `CONFIG_RTL8192EE`.

Risks and test signals: Missing an object causes unresolved symbols or missing runtime functionality. Build with `CONFIG_RTL8192EE=m` or `y` is the main test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/def.h

Purpose: This header centralizes RTL8192EE constants for descriptor counts, channel-offset encoding, queue selectors, chip version IDs, and hardware rate codes.

Important APIs and types: It defines `RX_DESC_NUM_92E`, primary-channel offset constants, `RX_MPDU_QUEUE`, rate classification macros (`IS_HT_RATE`, `IS_CCK_RATE`, `IS_OFDM_RATE`), `enum version_8192e`, `enum rtl_desc_qsel`, and `enum rtl_desc92c_rate` values from CCK through MCS15.

Control flow and integration: TX/RX, firmware, dynamic management, and hardware setup code use these constants to interpret descriptor rates, queue selectors, and chip version. `fw.c` uses `enum version_8192e`; `dm.c` uses rate constants in adaptive fallback logic.

State and persistence behavior: It is stateless and declarative.

Dependencies: It expects descriptor rate constants and bit macros to be consumed by RTL8192EE C files.

Risks and test signals: Rate-code or queue-selector mistakes can break TX descriptor encoding, rate adaptation, or firmware commands. Build coverage plus TX/RX at CCK, OFDM, and HT rates are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/dm.c

Purpose: This file implements RTL8192EE dynamic management: false-alarm accounting, DIG/CCA tuning, RSSI reporting, EDCA turbo, EDCCA/adaptivity, primary CCA interference handling, CFO/ATC crystal-cap tracking, TX power tracking initialization, rate-adaptive mask refresh, ARFB fallback selection, and the periodic watchdog.

Important APIs and functions:
- `rtl92ee_dm_init()` initializes DIG, rate-adaptive mask, primary CCA, EDCA turbo, TX power tracking, and dynamic ATC state.
- `rtl92ee_dm_watchdog()` is the periodic orchestrator. Under RF power lock it checks RF/FW power-save state, then runs all dynamic management routines when awake.
- `rtl92ee_dm_false_alarm_counter_statistics()` samples OFDM/CCK false alarm and CCA counters, stores `rtlpriv->falsealm_cnt`, and resets hardware counters.
- `rtl92ee_dm_dig()`, `rtl92ee_dm_write_dig()`, and `rtl92ee_dm_write_cck_cca_thres()` tune initial gain and CCK CCA thresholds from link state, RSSI, false alarms, and beacon count.
- `rtl92ee_dm_check_rssi_monitor()` gathers AP/adhoc/mesh station RSSI, reports RSSI to firmware using `H2C_92E_RSSI_REPORT`, dumps RSSI/EVM/SNR/CFO values to monitor registers, and updates minimum RSSI for DIG.
- `rtl92ee_dm_check_edca_turbo()` biases EDCA BE parameters toward uplink/downlink when only BE traffic is active.
- `rtl92ee_dm_dynamic_edcca()` and `rtl92ee_dm_adaptivity()` adjust EDCCA thresholds based on IGI values and firmware power-save state.
- `rtl92ee_dm_dynamic_primary_cca_check()` detects secondary-channel interference from OFDM CCA/FA counters and adjusts MF state.
- `rtl92ee_dm_dynamic_atc_switch()` adjusts crystal cap and ATC based on CFO tails and Bluetooth coexistence.
- `rtl92ee_dm_refresh_rate_adaptive_mask()` changes rate-adaptive state and asks HAL to update rate tables for the connected station.
- `rtl92ee_dm_dynamic_arfb_select()` writes fallback-rate registers based on firmware C2H RA reports.

Control flow: `rtl92ee_dm_init()` seeds state once during hardware/software setup. At runtime the watchdog first queries firmware power-save status and P2P power-save state, locks `rf_ps_lock`, and only proceeds when RF is on, firmware is awake, and no RF change is in progress. The watchdog then updates common link context, samples false alarms, reports RSSI to firmware, adjusts DIG/CCA/EDCCA/rate masks/EDCA/CFO/primary CCA, and releases the lock.

State and persistence behavior: This file mutates live driver state in `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->falsealm_cnt`, `rtlpriv->primarycca`, `rtlpriv->ra`, `rtlpriv->stats`, and firmware/HW registers. Some static counters in EDCA and primary CCA retain values across watchdog calls. No disk persistence exists.

Dependencies and integration points: It depends on rtlwifi core, mac80211 link/opmode state, PCI/core helpers, RTL8192EE register definitions, `fw.c` for H2C RSSI reporting, `trx.h`/`def.h` rate codes, Bluetooth coexistence ops, and HAL callbacks (`get_hw_reg`, `set_hw_reg`, `update_rate_tbl`, `get_btc_status`).

Risks: The algorithms are threshold-heavy and sensitive to hardware counter semantics. Static EDCA counters are shared at function scope rather than per-device, which is risky if multiple devices exist. Watchdog gating can suppress tuning while firmware is in power-save. RSSI reporting loops over station entries under spinlock and sends H2C commands in that loop, which may deserve scrutiny for lock context expectations. Crystal-cap adjustment clamps values but uses signed/unsigned-like fields that must remain compatible. EDCA turbo can degrade non-BE latency if non-BE packet detection misses traffic.

Test signals: Monitor false-alarm counters, IGI changes, rate-table updates, CCK CCA thresholds, EDCA BE register changes under uplink/downlink traffic, RSSI H2C reports in AP and station modes, CFO tracking under frequency offset, Bluetooth coexistence behavior, P2P power-save gating, and watchdog behavior during suspend/resume/LPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/dm.h

Purpose: This header defines RTL8192EE dynamic-management register addresses, thresholds, state constants, RSSI dump registers, and exported DM entry points.

Important APIs and definitions: It names RF, BB, and MAC registers used by DM logic; defines DIG false-alarm thresholds, primary CCA states (`MF_USC`, `MF_LSC`, `MF_USC_LSC`), rate-adaptive states, ATC/CFO thresholds, TX power tracking constants, and RSSI/CFO dump registers. It declares `rtl92ee_dm_init()`, `rtl92ee_dm_watchdog()`, DIG/CCA writers, EDCA/rate-adaptive init, and `rtl92ee_dm_dynamic_arfb_select()`.

Control flow and integration: `dm.c` implements the routines. `fw.c` calls `rtl92ee_dm_dynamic_arfb_select()` from the C2H RA report handler, while hardware setup calls DM init and the rtlwifi watchdog calls `rtl92ee_dm_watchdog()`.

State and persistence behavior: The header is stateless; constants map to live hardware registers and state fields mutated in `dm.c`.

Dependencies: It assumes rtlwifi/mac80211 types and bit macros are available. Many register constants duplicate hardware documentation semantics.

Risks and test signals: Incorrect register addresses or thresholds can destabilize gain control, CCA, CFO tracking, and rate adaptation. Build coverage plus runtime DM trace/debugfs/register observation are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/fw.c

Purpose: This file handles RTL8192EE firmware download, firmware reset/readiness polling, H2C mailbox command transmission, power-mode and media-status firmware commands, reserved-page packet offload, P2P power-save offload, and C2H RA report handling.

Important APIs and functions:
- `rtl92ee_download_fw()` strips an optional firmware header, toggles firmware-download mode, writes firmware pages, and waits for checksum and firmware ready bits.
- `_rtl92ee_enable_fw_download()`, `_rtl92ee_write_fw()`, and `_rtl92ee_fw_free_to_go()` implement the low-level download sequence.
- `_rtl92ee_fill_h2c_command()` serializes H2C mailbox access, waits for firmware to clear a mailbox, writes normal and extension boxes for command lengths 1-7, and advances `last_hmeboxnum`.
- `rtl92ee_fill_h2c_cmd()` validates `fw_ready`, copies the command into an 8-byte temporary buffer, and calls the mailbox writer.
- `rtl92ee_firmware_selfreset()` toggles 8051 reset bits in `REG_RSV_CTRL` and `REG_SYS_FUNC_EN`.
- `rtl92ee_set_fw_pwrmode_cmd()` builds `H2C_92E_SETPWRMODE` with LPS mode, RLBM, smart PS, awake interval, U-APSD, and RPWM/power state, with Bluetooth coexistence overrides.
- `rtl92ee_set_fw_media_status_rpt_cmd()` sends connect/disconnect media status.
- `rtl92ee_set_fw_rsvdpagepkt()` patches a static 1024-byte reserved-page image with current MAC/BSSID/AID, sends it through `rtl_cmd_send_packet()`, then sends `H2C_92E_RSVDPAGE` page locations.
- `rtl92ee_set_p2p_ps_offload_cmd()` programs CTWindow/NoA registers and sends P2P offload state to firmware.
- `rtl92ee_c2h_ra_report_handler()` decodes firmware rate/collision data and delegates ARFB update to `dm.c`.

Control flow: Firmware download happens during hardware init after firmware bytes are available in `rtlhal->pfirmware`. The writer pads firmware with `rtl_fill_dummy()`, pages through `rtl_fw_page_write()`, then waits for `FWDL_CHKSUM_RPT` and `WINTINI_RDY`. H2C commands are blocked when RF is off or firmware is not ready, and protected by `h2c_lock` plus `rtlhal->h2c_setinprogress`. Reserved-page offload mutates a static packet template, allocates an skb, sends it as a command packet, and only then informs firmware of page locations. P2P offload writes hardware NoA registers before sending an H2C command with the packed offload structure.

State and persistence behavior: The file updates `rtlhal->fw_version`, `fw_subversion`, `last_hmeboxnum`, `h2c_setinprogress`, and `p2p_ps_offload`; reads power-save state from `rtl_ps_ctl`; mutates the static `reserved_page_packet`; and writes MCU/H2C/P2P registers. Firmware state persists in device memory until reset/power loss, not on disk.

Dependencies and integration points: It depends on rtlwifi core firmware helpers, PCI/base/core/EFUSE includes, RTL8192EE `reg.h`, `def.h`, `fw.h`, and `dm.h`, Bluetooth coexistence ops, P2P/mac80211 state, and common 802.11 frame patch macros for reserved packets. `dm.c` consumes the C2H RA report callback indirectly through firmware events.

Risks: `buse_wake_on_wlan_fw` and `_rtl92ee_write_fw()`'s `version` argument are unused. `rtl92ee_download_fw()` returns `1` rather than a negative errno when firmware memory is missing. H2C wait loops can silently drop commands after timeout, and command lengths above 7 are not supported. Some macros in `fw.h` reference `__ph2ccmd` while accepting `__cmd`, which is suspicious for the unused MACID setters. Reserved-page packet is static global data modified per device, so multiple devices or concurrent calls could race. The function ignores `b_dl_finished`. P2P NoA loop assumes hardware supports two descriptors but iterates `p2pinfo->noa_num` without an explicit cap in this function.

Test signals: Firmware load success should show checksum and ready bits, `rtlhal->fw_ready` should gate H2C, LPS entry/exit should send correct pwrmode commands, reserved page setup should send an skb and H2C locations after association, P2P GO/client NoA/CTWindow flows should update registers, and C2H RA reports should alter ARFB registers. Multi-device tests are valuable for the static reserved-page buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/fw.h

Purpose: This header defines RTL8192EE firmware size/download constants, firmware header detection, H2C command IDs and lengths, firmware power-state bit encodings, H2C command packing macros, and firmware-facing function declarations.

Important APIs and definitions: It defines firmware size/page/polling limits; `IS_FW_HEADER_EXIST()` for 0x92E firmware signatures; H2C command IDs for reserved pages, media status, scan/keepalive/offload, power mode, RA/RSSI, P2P, WoWLAN, and AOAC; firmware power-state bits such as `FW_PS_RF_ON`, `FW_PS_REGISTER_ACTIVE`, `FW_PS_ACK`, and `FW_PS_CLOCK_OFF`; `pagenum_128()`; setters for pwrmode, reserved-page locations, and media-status report commands; and exported functions implemented in `fw.c`.

Control flow and integration: `fw.c` uses these definitions to download firmware and pack H2C commands. DM code and hardware/power-save code call the declared routines for RSSI, LPS, media status, reserved pages, P2P offload, and C2H RA handling.

State and persistence behavior: The header is stateless. Its macros pack bytes into caller-provided command buffers that are sent to firmware or used to interpret firmware power state.

Dependencies: It needs endian helpers, bit macros, and rtlwifi/mac80211 types. Some command IDs vary under `USE_OLD_WOWLAN_DEBUG_FW`.

Risks and test signals: Macro correctness is critical because command packing has no type safety. `H2C_92E_P2P_PS_OFFLOAD = 024` is an octal literal for decimal 20, which may be intentional but is visually risky. `FW_PWR_STATE_ACTIVE` and `FW_PWR_STATE_RF_OFF` are defined twice. Media-status MACID macros use `__ph2ccmd` despite taking `__cmd`, which would break if used. Build tests plus firmware command traces are the main checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/fw.h -->
