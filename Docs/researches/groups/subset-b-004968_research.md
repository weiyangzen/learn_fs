# Research Report: subset-b-004968

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/txrx.c

Purpose: Implements the CW1200 mac80211 datapath above the WSM firmware transport. It prepares outgoing skbs with WSM TX headers, maps Linux queues/link IDs to firmware identifiers, manages firmware retry-policy cache entries, handles TX confirmations, converts firmware RX indications into mac80211 RX status, manages key slot bookkeeping, and maintains AP-mode link-id lifecycle.

Important APIs, types, and functions: `cw1200_tx()` is the mac80211 TX entry point. `cw1200_tx_confirm_cb()` consumes `struct wsm_tx_confirm` and reports completion to mac80211. `cw1200_rx_cb()` processes `struct wsm_rx` metadata and passes frames to `ieee80211_rx_irqsafe()`. Retry-policy helpers include `tx_policy_init()`, `tx_policy_get()`, `tx_policy_upload_work()`, and `tx_policy_clean()`. Link-id/security APIs include `cw1200_alloc_key()`, `cw1200_upload_keys()`, `cw1200_find_link_id()`, `cw1200_alloc_link_id()`, and `cw1200_link_id_gc_work()`.

Control flow: TX starts by deriving queue, destination address, header length, station private link id, TID, crypto trailer space, DMA alignment, and WSM header fields. It assigns BT coexistence priority, resolves a firmware retry-policy slot, updates buffered power-save state under `ps_state_lock`, enqueues into `priv->tx_queue[]`, and wakes the bottom half. `wsm_get_tx()` later pulls queued `struct wsm_tx` buffers for the bus path. RX validates mode/status, handles PSPOLL locally in AP mode, converts channel/rate/signal/encryption/TSF metadata, strips firmware-processed crypto material, updates beacon/TIM driven state, and either queues early data for soft link IDs or submits to mac80211. TX confirms may requeue firmware-suspended frames, update BSS-loss recovery, adjust mac80211 retry counts, trim crypto trailers, and remove queue entries.

State and persistence: State is in memory only: `tx_policy_cache` LRU/free lists and usage counts, `key_map`/`keys[]`, `link_id_db[]`, `link_id_map`, `sta_asleep_mask`, `pspoll_mask`, buffered multicast flags, BSS-loss confirmation id, and delayed work. Firmware retry-policy uploads persist in device state until reset or policy rewrite, but no on-disk persistence exists.

Dependencies and integration points: Integrates with mac80211/cfg80211 (`ieee80211_tx_status_skb`, `ieee80211_sta_set_buffered`, `ieee80211_rx_irqsafe`), CW1200 queue helpers, WSM commands (`wsm_add_key`, `wsm_reset`, `wsm_map_link`, `wsm_set_tx_rate_retry_policy`), driver workqueue tasks, PM helpers, and debug counters.

Risks: Retry-policy cache exhaustion locks TX queues and depends on upload work always unlocking; failures can deadlock traffic. Link-id GC interleaves firmware reset/map commands with `ps_state_lock` release/reacquire and can race AP station state. RX crypto stripping relies on hardcoded IV/ICV lengths. TX status retry count reconstruction can skew rate-control feedback. Several firmware workarounds intentionally drop or transform frames, so behavior is firmware-version sensitive.

Test signals: Exercise AP power-save multicast/PSPOLL, WEP default-key switching, TKIP/AES RX stripping, firmware `WSM_REQUEUE`, link-id allocation/GC/reset-remap, scan probe conversion, BSS-loss nullfunc recovery, and TX policy upload under all 8 cache slots. Kernel logs for "TX Frames stuck", "Too many attempts to requeue", malformed SDU warnings, and queue lock stalls are important runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/txrx.h

Purpose: Declares the CW1200 datapath interface shared by mac80211 glue, WSM transport, security setup, and AP link-id maintenance.

Important APIs, types, and functions: `struct tx_policy` encodes firmware retry counts in three little-endian words plus local metadata. `struct tx_policy_cache` provides eight cache entries, used/free lists, and a spinlock. Public entry points cover policy lifecycle (`tx_policy_init`, `tx_policy_upload_work`, `tx_policy_clean`), TX/RX callbacks (`cw1200_tx`, `cw1200_tx_confirm_cb`, `cw1200_rx_cb`), key lifecycle (`cw1200_alloc_key`, `cw1200_upload_keys`), timeout work, and link-id work/GC.

Control flow: The header does not implement flow, but it defines the contract that WSM uses for callbacks and the mac80211 side uses for TX submission. The retry policy cache exists because the firmware accepts a retry-policy id rather than a per-frame retry chain.

State and persistence: Declares in-memory policy cache and AP link-id GC timeout (`CW1200_LINK_ID_GC_TIMEOUT`). No persistent storage.

Dependencies and integration points: Depends on Linux lists/spinlocks, `struct ieee80211_hw`, `struct sk_buff`, WSM TX/RX structs, and CW1200 private state.

Risks: The small fixed retry-policy cache makes correct usage counting and release critical. Callers must preserve skb private offsets for `cw1200_skb_dtor()`.

Test signals: Compile coverage for all declared callbacks, TX policy cache saturation, and key/link-id lifecycle paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/wsm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/wsm.c

Purpose: Implements the CW1200 WSM host-interface command, confirmation, indication, and TX-buffer plumbing. It serializes firmware commands, marshals/unmarshals WSM byte streams, dispatches firmware indications, and selects TX frames or commands for the bus bottom half.

Important APIs, types, and functions: Command APIs include `wsm_configuration`, `wsm_reset`, `wsm_read_mib`, `wsm_write_mib`, `wsm_scan`, `wsm_join`, `wsm_set_bss_params`, `wsm_add_key`, `wsm_set_edca_params`, `wsm_switch_channel`, `wsm_set_pm`, `wsm_start`, `wsm_map_link`, and `wsm_update_ie`. Transport functions include `wsm_cmd_send`, `wsm_handle_rx`, `wsm_get_tx`, `wsm_txed`, `wsm_lock_tx`, `wsm_flush_tx`, and WSM buffer helpers.

Control flow: Command helpers fill `priv->wsm_cmd_buf` using checked `WSM_PUT*` macros, serialize with `wsm_cmd_mux`, publish `priv->wsm_cmd` under spinlock, wake the BH, and wait on `wsm_cmd_wq`. `wsm_handle_rx()` strips link ID bits, dispatches TX confirms, command responses, or indications by WSM ID, runs command-specific confirm parsers, stores `priv->wsm_cmd.ret`, and wakes waiters. Indications update firmware caps/startup readiness, deliver RX frames to `cw1200_rx_cb`, enqueue generic events, signal scan/join/channel/PM completion, and handle suspend/resume. TX selection prioritizes pending commands, then AP multicast, sleeping-station constraints, EDCA scoring, bursting, and special firmware workarounds.

State and persistence: In-memory state includes `priv->wsm_cmd`, `wsm_cmd_buf`, firmware capability fields, `firmware_ready`, TX lock counter, channel/PM wait states, event queue, and BH error flags. Device-side state is changed through WSM/MIB commands but is not persisted by this file.

Dependencies and integration points: Integrates with CW1200 BH, queue, STA, scan, join, PM, and debug code; Linux wait queues, mutexes, spinlocks, workqueues, skbs, and mac80211 frame helpers; and firmware WSM message IDs from `wsm.h`.

Risks: Firmware command timeout kills the BH thread and sets fatal state; lost or repeated responses are guarded but still fragile. Buffer macros rely on `goto underflow/nomem` in each function. `wsm_flush_tx()` can declare fatal BH error if firmware keeps frames too long. Some message IDs are literal constants, making spec drift harder to audit. `wsm_cmd_send()` busy-spins under a spinlock until `done` instead of sleeping.

Test signals: Validate startup indication, command timeout path, MIB read/write, scan/join/channel-switch/PM indications, multi-TX confirm buffer release, TX lock/flush behavior, event queue processing, and malformed WSM underflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/wsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/wsm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/wsm.h

Purpose: Defines the CW1200 WSM firmware ABI used by the driver: command/response IDs, MIB IDs, status bits, packed request/response structs, inline MIB helpers, TX/RX message headers, queue mappings, and command-buffer structures.

Important APIs, types, and functions: Key exported structs include `wsm_hdr`, `wsm_startup_ind`, `wsm_configuration`, `wsm_scan`, `wsm_tx`, `wsm_rx`, `wsm_join`, `wsm_set_pm`, `wsm_add_key`, `wsm_edca_params`, `wsm_update_ie`, `wsm_cmd`, and `wsm_buf`. Inline helpers wrap MIBs for output power, beacon wakeup, counters, station id, RX filter, beacon filter, operational mode, template frames, protected management, block ack, association mode, retry policy, filters, keepalive, multicast, ARP, P2P PS, UAPSD, and internal TX rate. Public APIs cover WSM command calls, TX locking, RX handling, and TX buffer retrieval.

Control flow: The header encodes the firmware contract consumed by `wsm.c` and higher layers. Command structs are caller-filled, marshaled by `wsm.c`, and confirmed by firmware response IDs. Inline helpers turn typed configuration into `wsm_read_mib`/`wsm_write_mib` calls. Queue mapping helpers translate Linux VO/VI/BE/BK to firmware BE/BK/VI/VO ordering.

State and persistence: Defines in-memory command state (`struct wsm_cmd`) and dynamic command buffer (`struct wsm_buf`). MIB writes change firmware runtime state; no host persistence is declared.

Dependencies and integration points: Depends on Linux spinlocks, skbs, Ethernet constants, endian types, and `struct cw1200_common`. It is the shared contract for cw1200 TX/RX, STA, scan, AP, and BH code.

Risks: The ABI is densely packed and endian-sensitive. Several helpers compute variable payload sizes from caller-provided counts and assume bounds were already checked. `wsm_set_template_frame()` mutates skb headroom temporarily. Queue mapping arrays have no runtime bounds checking.

Test signals: Build with sparse/endian checking, exercise every MIB helper used by STA/AP setup, verify packed struct sizes against firmware spec, and test queue mapping/rate-policy MIB upload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/wsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/Kconfig

Purpose: Adds the top-level Texas Instruments wireless vendor menu for kernel configuration and includes all TI wireless subdriver Kconfig files.

Important APIs, types, and functions: Defines `config WLAN_VENDOR_TI` as a boolean, default `y`, and conditionally sources `wl1251`, `wl12xx`, `wl18xx`, and finally `wlcore` Kconfigs.

Control flow: Kconfig visibility is gated by `if WLAN_VENDOR_TI`; selecting `N` hides vendor-specific TI driver prompts without directly changing built objects.

State and persistence: Kconfig selections persist in the kernel `.config`, not in driver runtime state.

Dependencies and integration points: Integrates with Linux wireless Kconfig hierarchy and the Makefile's `CONFIG_*` object selection.

Risks: Because `wlcore` is sourced last for automatic dependencies, reordering can affect dependency resolution. Typo in help text says "Texas Instrument" rather than "Texas Instruments" but is nonfunctional.

Test signals: `oldconfig/menuconfig` visibility for TI drivers and build matrix with `WLAN_VENDOR_TI=n/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/Makefile

Purpose: Routes enabled TI wireless driver families into their subdirectories.

Important APIs, types, and functions: Uses `obj-$(CONFIG_WLCORE) += wlcore/`, `obj-$(CONFIG_WL12XX) += wl12xx/`, `obj-$(CONFIG_WL1251) += wl1251/`, and `obj-$(CONFIG_WL18XX) += wl18xx/`.

Control flow: Kbuild descends only into subdirectories whose config symbol is enabled as built-in or module.

State and persistence: Build-time only.

Dependencies and integration points: Depends on Kconfig symbols defined by included TI Kconfig files.

Risks: Missing or mismatched config symbol names would silently omit driver directories. No special ordering beyond listing.

Test signals: Kernel builds for each TI driver as built-in/module and clean omission when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/Kconfig

Purpose: Defines kernel configuration options for the TI wl1251 core driver and its SPI/SDIO bus frontends.

Important APIs, types, and functions: `WL1251` is a tristate requiring `MAC80211` and selecting `FW_LOADER` and `CRC7`. `WL1251_SPI` depends on `WL1251 && SPI_MASTER`. `WL1251_SDIO` depends on `WL1251 && MMC`.

Control flow: The core module must be enabled before a bus-specific module can be selected. Help text identifies module names `wl1251`, `wl1251_spi`, and `wl1251_sdio`.

State and persistence: Build configuration only.

Dependencies and integration points: Integrates with mac80211, firmware loading, CRC7 support, SPI, MMC/SDIO, and the wl1251 Makefile.

Risks: Bus modules are selectable only when the core is enabled; distro configs must include the correct frontend for hardware discovery. Firmware availability remains runtime dependent.

Test signals: Kconfig dependency checks and module build/load tests for SPI and SDIO variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/Makefile

Purpose: Defines wl1251 module composition for Kbuild.

Important APIs, types, and functions: The core `wl1251.o` is built from `main.o event.o tx.o rx.o ps.o cmd.o acx.o boot.o init.o debugfs.o io.o`. Bus modules add `spi.o` and `sdio.o` for `wl1251_spi.o` and `wl1251_sdio.o`.

Control flow: `obj-$(CONFIG_WL1251)` emits the core object; bus objects are emitted when their config symbols are enabled.

State and persistence: Build-time only.

Dependencies and integration points: Aligns with Kconfig symbols and links the files researched here into the core wl1251 module.

Risks: A missing object in `wl1251-objs` causes unresolved symbols or absent functionality, especially command/ACX/boot/debugfs/event support.

Test signals: Module link tests for `wl1251`, `wl1251_spi`, and `wl1251_sdio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/acx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/acx.c

Purpose: Implements wl1251 ACX information-element configuration and interrogation helpers. These functions allocate packed ACX payloads, fill firmware parameters, send `CMD_CONFIGURE` or `CMD_INTERROGATE`, and update selected driver state.

Important APIs, types, and functions: Configuration helpers cover frame rates, station ID, default key, wake/sleep authorization, TX power, feature flags, data path params, RX config, slot time, multicast table, RTS threshold, beacon filtering, connection monitoring, SoftGemini BT coexistence, CCA, DTIM/broadcast behavior, AID, event mask, low RSSI, preamble/CTS protection, memory config, TBTT/DTIM, BET, ARP filter, AC/TID QoS. Interrogation helpers include firmware version, memory map, statistics, and TSF.

Control flow: Most functions follow a strict pattern: allocate zeroed ACX struct, fill fields and defaults from arguments or constants, call `wl1251_cmd_configure()` with an ACX ID, log failures, free memory, and return. Readback functions call `wl1251_cmd_interrogate()` and copy response fields. `wl1251_acx_data_path_params()` first configures ring sizes and thresholds, then interrogates response parameters and validates command status.

State and persistence: Host state updates are limited, e.g. `wl->default_key` and returned buffers such as firmware version/statistics/TSF. Firmware runtime state is extensively changed but not persisted by the host.

Dependencies and integration points: Depends on `cmd.c` mailbox helpers, ACX structs/IDs from `acx.h`, rate/filter constants, power-save code, and wl1251 core state. It is used by boot/init/mac80211 operations to establish firmware behavior.

Risks: Many helpers trust caller-provided sizes/counts; multicast copy can overflow if `mc_list_len` exceeds firmware table capacity. Some FIXME comments note unset PD threshold and ambiguous data-path response ID. All allocations are per-command, so memory pressure can fail configuration. Firmware defaults embedded as constants may not suit all board/NVS variants.

Test signals: Validate boot/init sequence reaches configured data path, RX filters match interface modes, event masks generate expected events, debugfs statistics reads succeed, multicast table bounds are respected, and power-save/BT coexistence parameters do not regress association stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/acx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/acx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/acx.h

Purpose: Defines the wl1251 ACX firmware information-element ABI: ACX header, element IDs, packed payload structs, default constants, interrupt bits, statistics layouts, and prototypes implemented by `acx.c`.

Important APIs, types, and functions: `struct acx_header` embeds `wl1251_cmd_header` plus ACX id/length. Major structs cover revision, sleep auth, data path params, RX config/filter flags, QoS queues, slot, multicast, service period timeouts, low RSSI, beacon filter, connection monitor, BT/WLAN coexistence, event mask, frame rates, station ID, TSF, wake conditions, preamble/CTS, statistics, memory config/map, TBTT/DTIM, BET, ARP filtering, AC config, and TID config. The ACX ID enum maps firmware element numbers, and interrupt defines map host interrupt bits.

Control flow: The header enables `cmd.c` to wrap ACX payloads in `CMD_CONFIGURE`/`CMD_INTERROGATE` and lets init/debugfs/event code share exact firmware struct layouts.

State and persistence: No runtime state is stored here, but the packed structures define firmware state that can be written or read. Statistics structs are cached by debugfs in `wl->stats.fw_stats`.

Dependencies and integration points: Includes `wl1251.h` and `cmd.h`; uses kernel integer/endian types and `ETH_ALEN`. It is a central dependency for boot, init, command, event, debugfs, RX/TX config, and power-save code.

Risks: ABI correctness is critical: packing, field widths, endian annotations, and ACX IDs must match firmware. Some fields are host pointers in `wl1251_acx_mem_map`, which are really firmware addresses and can be confusing. A few comments mark undocumented or unused firmware elements.

Test signals: Compile-time packed layout checks where possible, runtime ACX interrogate/configure success, firmware statistics sanity, and interrupt mask behavior during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/acx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/boot.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/boot.c

Purpose: Performs wl1251 hardware and firmware boot: soft reset, NVS/EEPROM handling, PLL/init sequencing, firmware upload, firmware start, mailbox discovery, interrupt setup, event mask setup, and firmware version readout.

Important APIs, types, and functions: Public functions are `wl1251_boot_target_enable_interrupts()`, `wl1251_boot_soft_reset()`, `wl1251_boot_init_seq()`, `wl1251_boot_run_firmware()`, and `wl1251_boot()`. Static helpers upload firmware chunks and NVS tables and clear ECPU halt.

Control flow: `wl1251_boot()` halts the embedded CPU, soft-resets hardware, loads NVS from EEPROM or host NVS file, reads boot attributes, runs the PLL/restart initialization sequence, verifies ECPU halt, uploads firmware in chunks through the download partition, starts firmware, waits for `WL1251_ACX_INTR_INIT_COMPLETE`, reads command/event mailbox addresses, switches to working memory partition, enables host/target interrupts, configures event mask and mailbox pointers, and returns.

State and persistence: Updates `wl->boot_attr`, `wl->cmd_box_addr`, `wl->event_box_addr`, `wl->intr_mask`, `wl->event_mask`, mailbox pointers via event config, and firmware version. NVS contents and firmware are copied to device memory; no host persistence is written.

Dependencies and integration points: Depends on register/memory IO helpers, partition switching, SPI/bus DMA requirements, ACX/event helpers, firmware/NVS buffers in `struct wl1251`, and hardware constants from register headers.

Risks: Hardware timing is sensitive: reset self-clear timeout, EEPROM sleep, PLL delays, and init interrupt polling must match silicon. Firmware length is parsed from raw header bytes and must be 4-byte aligned. NVS parsing trusts encoded burst lengths and destination addresses. Firmware upload uses a temporary DMA-safe chunk buffer and partition window math that must not overrun device memory.

Test signals: Boot logs for chip-id match, soft reset completion, init-complete interrupt, mailbox addresses, firmware version, event unmask success, and failure paths for missing NVS, malformed firmware length, or init timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/boot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/boot.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/boot.h

Purpose: Declares the wl1251 boot API and init-complete polling constants.

Important APIs, types, and functions: Exports boot-stage functions `wl1251_boot_soft_reset`, `wl1251_boot_init_seq`, `wl1251_boot_run_firmware`, `wl1251_boot_target_enable_interrupts`, and `wl1251_boot`. Defines `INIT_LOOP` and `INIT_LOOP_DELAY`.

Control flow: Used by wl1251 initialization to sequence hardware reset, firmware upload/start, and interrupt enablement.

State and persistence: No direct state; functions mutate `struct wl1251` and device registers.

Dependencies and integration points: Includes `wl1251.h`; implemented by `boot.c`.

Risks: Constants control total init wait time and can affect slow hardware or broken firmware diagnosis.

Test signals: Build references from init path and boot timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/boot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/cmd.c

Purpose: Implements wl1251 firmware command mailbox operations and high-level command builders for ACX configure/interrogate, RX/TX data path control, join, power-save mode, templates, scan, and scan timeout.

Important APIs, types, and functions: `wl1251_cmd_send()` is the low-level command path. `wl1251_cmd_interrogate()` and `wl1251_cmd_configure()` wrap ACX reads/writes. Other commands include `wl1251_cmd_vbm`, `wl1251_cmd_data_path_rx`, `wl1251_cmd_data_path_tx`, `wl1251_cmd_join`, `wl1251_cmd_ps_mode`, `wl1251_cmd_template_set`, `wl1251_cmd_scan`, and `wl1251_cmd_trigger_scan_to`.

Control flow: `wl1251_cmd_send()` writes a command buffer to `wl->cmd_box_addr`, triggers `INTR_TRIG_CMD`, polls `ACX_REG_INTERRUPT_NO_CLEAR` until `WL1251_ACX_INTR_CMD_COMPLETE` or timeout, and ACKs completion. ACX interrogate writes an ACX header command then reads the full response back from the mailbox. Scan/join/template helpers allocate packed command structs, fill firmware fields, send the command, and in scan's case read back and validate command status.

State and persistence: Mutates firmware command mailbox and command status. Uses `wl->cmd_box_addr`, `wl->bssid`, `wl->rx_config`, `wl->rx_filter`, and scan/join inputs. No on-disk persistence.

Dependencies and integration points: Depends on memory/register IO, ACX structs/IDs, command IDs from `cmd.h`, power-save constants, cfg80211 channels, and wl1251 core state.

Risks: Polling command completion sleeps in 1 ms increments and can block callers for up to 2 seconds. Buffers must be DMA-compatible and 4-byte aligned. Some fields such as BSSID are reversed for firmware layout. Scan warns but still allocates a fixed max-channel command; callers must respect channel limits.

Test signals: Command timeout/ACK handling, ACX status validation, join on IBSS/BSS, scan completion after `CMD_SCAN`, template truncation at 300 bytes, and RX/TX data path enable/disable around boot and suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/cmd.h

Purpose: Defines wl1251 firmware command IDs, status codes, packed command payloads, scan/join/template/key structures, and command function prototypes.

Important APIs, types, and functions: Exports all functions implemented by `cmd.c`. Defines `WL1251_COMMAND_TIMEOUT`, `enum wl1251_commands`, `struct wl1251_cmd_header`, generic `struct wl1251_command`, status constants, memory read/write command payload, scan parameters/channels, join command, path enable/disable command, packet template command, VBM/TIM update, power-save params, trigger scan timeout, and key action/type/set-key payload.

Control flow: The structs are filled by command builders, sent through `wl1251_cmd_send()`, and interpreted by firmware. ACX commands reuse `struct wl1251_cmd_header` through `struct acx_header`.

State and persistence: Defines transient mailbox command payloads and firmware status values. No host state.

Dependencies and integration points: Includes `wl1251.h` and cfg80211; referenced by `acx.h`, `cmd.c`, TX/security setup, and boot/init code.

Risks: ABI mismatch in packed structs breaks firmware communication. `MAX_CMD_PARAMS` and fixed arrays bound mailbox payload sizes; callers must clamp template, scan, and key lengths. Status codes include driver-internal timeout/reset values mixed with firmware statuses.

Test signals: Compile with packed layout assumptions, command status decoding, scan channel limit handling, and key installation/removal across WEP/TKIP/AES.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/debugfs.c

Purpose: Exposes wl1251 firmware and driver statistics through debugfs and manages the debugfs lifecycle.

Important APIs, types, and functions: Public APIs are `wl1251_debugfs_init()`, `wl1251_debugfs_exit()`, and `wl1251_debugfs_reset()`. Macro-generated file operations expose fields from `struct acx_statistics`; custom readers expose TX queue length/status and retry counters. `wl1251_debugfs_update_stats()` refreshes firmware statistics with a 1000 ms cache lifetime.

Control flow: Init allocates `wl->stats.fw_stats`, creates root and `fw-statistics` dirs, seeds update timestamp, and creates many read-only files. Reads of firmware-stat files wake ELP, conditionally interrogate `ACX_STATISTICS`, let firmware sleep, then format one counter. Exit removes every file and directory and frees stats memory. Reset zeros cached firmware stats and driver counters.

State and persistence: Maintains in-memory cached stats and debugfs dentries under `wl->debugfs`. Debugfs files are runtime-only and disappear on module/device removal.

Dependencies and integration points: Depends on debugfs, simple file operations, wl1251 mutex, ELP power-save helpers, ACX statistics interrogation, skb queue state, and `KBUILD_MODNAME` for root directory.

Risks: `debugfs_create_*` return values are not checked; later remove calls tolerate NULL but missing files may go unnoticed. Stats reads take `wl->mutex` and may wake firmware, so debugfs access can affect power behavior. The file list is manually mirrored in add/delete macros and can drift.

Test signals: Mount debugfs and read all files while device is on/off/ELP, verify no leaks on init failure/removal, confirm stats cache throttling, and check queue status reflects stopped/running TX queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/debugfs.h

Purpose: Declares wl1251 debugfs lifecycle functions.

Important APIs, types, and functions: `wl1251_debugfs_init`, `wl1251_debugfs_exit`, and `wl1251_debugfs_reset`.

Control flow: Called by wl1251 core probe/remove/reset paths to create, destroy, or clear debugfs-visible stats.

State and persistence: No direct state; implementation manages `wl->debugfs` and `wl->stats`.

Dependencies and integration points: Includes `wl1251.h`; implemented by `debugfs.c`.

Risks: Call order matters: reset assumes stats may already be allocated; exit assumes files were initialized.

Test signals: Build linkage and probe/remove/reset coverage with debugfs enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/event.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/event.c

Purpose: Handles wl1251 firmware event mailboxes, translates event bits into mac80211 notifications and power-save actions, and ACKs processed event buffers.

Important APIs, types, and functions: Public APIs are `wl1251_event_wait()`, `wl1251_event_unmask()`, `wl1251_event_mbox_config()`, and `wl1251_event_handle()`. Internal handlers process scan completion, power-save reports, BSS loss/regain, synchronization timeout, and RSSI threshold events.

Control flow: Boot configures mailbox pointers and unmask bits. On event interrupt, `wl1251_event_handle()` validates mailbox number, reads the selected `event_mailbox`, calls `wl1251_event_process()`, frees the buffer, and triggers `INTR_TRIG_EVENT_ACK`. Processing masks off firmware-disabled events, completes scans, retries or abandons PS entry, forces active mode on BSS loss, reports beacon loss to mac80211, restores requested PS on BSS regain, and sends CQM RSSI notifications.

State and persistence: Updates `wl->scanning`, `wl->station_mode` via PS commands, `wl->psm_entry_retry`, mailbox pointer array, and uses `wl->event_mask`. No persistent storage.

Dependencies and integration points: Depends on ACX event mask configuration, register/memory IO, PS mode helper, mac80211 scan/beacon/CQM notification APIs, and event bit definitions from `event.h`.

Risks: Event processing is bitmask-based and ignores many defined events. PS entry retry can issue nested PS commands from event context. `wl1251_event_wait()` polls both mailbox event fields and may race with normal interrupt-driven processing if used incorrectly.

Test signals: Scan completion clears `wl->scanning`; BSS loss triggers `ieee80211_beacon_loss`; low/regained RSSI triggers CQM notifications; PS entry fail retries exactly three times; invalid mailbox returns `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/event.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/event.h

Purpose: Defines the wl1251 firmware event mailbox ABI, event bit IDs, mailbox layout, power-save status values, and event API prototypes.

Important APIs, types, and functions: Event ID bits cover scan complete, calibration, low/regained RSSI/SNR, PS report, sync timeout, health/debug/MAC status, join/channel switch, BSS lose/regain, BT PTA, and PLT calibration. `struct event_mailbox` contains event vectors/masks plus RSSI, PS status, health, debug, FCS, and SNR fields. `wl1251_event_unmask`, `wl1251_event_mbox_config`, `wl1251_event_handle`, and `wl1251_event_wait` are exported.

Control flow: Firmware alternates between two fixed event buffers; host reads one, processes bits, and ACKs to free it.

State and persistence: Defines transient mailbox contents and status codes. No host persistence.

Dependencies and integration points: Depends on `wl1251.h`, event handling in `event.c`, boot-time event mask setup, and mac80211 notification paths.

Risks: Packed mailbox layout must match firmware exactly. Event masks are inverted by ACX configuration (`~wl->event_mask`), so misunderstanding mask semantics can suppress needed events.

Test signals: Validate mailbox pointer spacing, event ACK behavior, mask/unmask semantics, and PS status handling for all defined status values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/event.h -->
