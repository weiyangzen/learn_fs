# Research: subset-b-004969

Grouped code research for TI `wl1251` and `wl12xx` wireless driver files under `sources/distributed-fs/ceph-client/drivers/net/wireless/ti/`. Each section preserves the source path and is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/init.c

Purpose: Implements wl1251 firmware/hardware initialization after boot, programming encryption defaults, firmware templates, memory/data path layout, RX/TX queues, PHY defaults, beacon/power settings, and enabling firmware data paths.

Important APIs and functions: `wl1251_hw_init()` is the exported orchestration entry used by core start. Helper stages include `wl1251_hw_init_hwenc_config()`, `wl1251_hw_init_templates_config()`, `wl1251_hw_init_rx_config()`, `wl1251_hw_init_phy_config()`, `wl1251_hw_init_beacon_filter()`, `wl1251_hw_init_pta()`, `wl1251_hw_init_energy_detection()`, `wl1251_hw_init_beacon_broadcast()`, `wl1251_hw_init_power_auth()`, `wl1251_hw_init_mem_config()`, `wl1251_hw_init_tx_queue_config()`, and `wl1251_hw_init_data_path_config()`.

Control flow: `wl1251_hw_init()` runs a strict sequence of ACX and command operations. It first disables special feature bits and sets the default key, reserves firmware template memory with empty probe/null/PS-poll/QoS/beacon/TIM templates, configures memory, interrogates data-path parameters, applies RX filtering, configures all TX AC queues, applies PHY and connection monitor parameters, configures beacon filtering/coexistence/CCA/beacon DTIM behavior, enables RX and TX data paths on `wl->channel`, and finally authorizes CAM power mode.

State and persistence: The file allocates and stores `wl->target_mem_map` and `wl->data_path`; those pointers are later consumed by RX/TX paths and freed on error or device teardown. It reads firmware-provided memory addresses rather than persisting configuration externally. Initialization mutates firmware state through ACX commands, not disk state.

Dependencies and integration points: Depends on `acx.h` command helpers, `cmd.h` template/data-path commands, `reg.h` constants, and `wl12xx_80211.h` template structure sizes. It integrates with `wl1251_op_start()` in `main.c`, and its produced `target_mem_map` and `data_path` are essential for `tx.c`, `rx.c`, and interrupt handling.

Risks: Several AC queue configuration calls after `wl1251_cmd_configure()` ignore return values for `wl1251_acx_ac_cfg()`, so AC programming failures can be missed. Error paths free allocated objects but do not set all freed pointers to `NULL`, which is manageable because startup fails immediately but still worth checking in future edits. The order of ACX programming is firmware-sensitive and should not be refactored casually.

Test signals: Successful boot logs include firmware boot in `main.c` followed by the `wl1251_info()` line reporting TX/RX block counts. Failure signals are ACX warnings such as template, memory map, data path, or queue configuration failures. Regression testing should exercise start/stop, scan, RX/TX, and PS transitions after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/init.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/init.h

Purpose: Declares the wl1251 initialization entry points implemented by `init.c`.

Important APIs and types: Exposes `wl1251_hw_init()`, plus stage-level helpers for hardware encryption config, templates, RX config, PHY config, beacon filter, PTA, energy detection, beacon/broadcast config, power authorization, and memory config. It depends on `struct wl1251` from `wl1251.h`.

Control flow: This header itself has no runtime control flow. It provides callable init stages, but production startup primarily enters through `wl1251_hw_init()` from `main.c`.

State and persistence: No state is stored here. The declarations imply mutation of the `struct wl1251` instance and firmware/device state by their implementations.

Dependencies and integration points: Included by `init.c` and by the core driver where initialization is invoked. It forms a narrow contract between the mac80211 core startup path and the ACX/firmware initialization sequence.

Risks: Because many stage functions are public within the driver, later code could call them out of order. Most stages assume earlier boot and wakeup state is valid.

Test signals: Compile coverage catches signature drift. Runtime validation comes from `wl1251_op_start()` successfully completing firmware boot and init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/io.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/io.c

Purpose: Implements address translation and partition programming for wl1251 target memory/register access over an abstract bus interface.

Important APIs and functions: `wl1251_mem_read()`, `wl1251_mem_write()`, `wl1251_mem_read32()`, `wl1251_mem_write32()`, `wl1251_reg_read32()`, `wl1251_reg_write32()`, and `wl1251_set_partition()`. Internal helpers translate logical target addresses through current partition state.

Control flow: Register reads below `REGISTERS_BASE` are interpreted as ACX register table indexes and looked up in `wl1251_io_reg_table`. Memory and register addresses are converted from physical target windows to virtual host-access windows before dispatching to `wl->if_ops->read/write`. `wl1251_set_partition()` clamps total virtual range, prevents overlapping memory/register windows, records physical and virtual bases in `wl`, and writes a `wl1251_partition_set` to `HW_ACCESS_PART0_SIZE_ADDR`.

State and persistence: Maintains `wl->physical_mem_addr`, `wl->physical_reg_addr`, `wl->virtual_mem_addr`, and `wl->virtual_reg_addr`. These are volatile per-device mappings and must match the active firmware partition.

Dependencies and integration points: Depends on `wl1251_if_operations` supplied by SPI or SDIO bus glue. Used by boot, interrupt, RX, TX, EEPROM/NVS, and ACX command paths.

Risks: Invalid ACX register indexes return `-EINVAL`, but callers of `wl1251_reg_read32()` receive that value as a `u32`, so bad indexes can propagate as register data. Partition writes allocate dynamically and log but otherwise return void, so allocation failure cannot be handled by callers. All callers must ensure partitions are correct before target access.

Test signals: Boot failures around chip ID, mailbox, firmware upload, or data-path access often indicate partition translation issues. Bus-level tracing should show partition programming before register/memory reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/io.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/io.h

Purpose: Defines wl1251 hardware access window constants and inline 32-bit/ELP IO helpers.

Important APIs and types: Defines `HW_ACCESS_MEMORY_MAX_RANGE`, partition control addresses, `HW_ACCESS_PRAM_MAX_RANGE`, `wl1251_read32()`, `wl1251_write32()`, `wl1251_read_elp()`, `wl1251_write_elp()`, memory/register access prototypes, and `wl1251_set_partition()`.

Control flow: Inline read/write helpers directly call `wl->if_ops`. `wl1251_read32()` uses `wl->buffer_32` and converts little-endian data to CPU order; `wl1251_write32()` performs the inverse. ELP helpers call specialized bus hooks when present and fall back to regular bus read/write otherwise.

State and persistence: Uses transient buffers in `struct wl1251` (`buffer_32`) for 32-bit access. ELP access may update bus-private state in SDIO because the SDIO backend caches the last ELP write value.

Dependencies and integration points: Depends on bus implementations filling `wl1251_if_operations`. Included by boot, power-save, RX/TX, command, and main logic.

Risks: Fallback ELP writes pass CPU-endian `u32` directly to bus write, unlike `wl1251_write32()`; this is tied to bus/hardware expectations and should be changed only with hardware validation. Inline helpers assume serialized access to shared buffers, usually via `wl->mutex`.

Test signals: ELP wake/sleep reliability, boot register reads, and interrupt handling are direct indicators for this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/main.c

Purpose: Provides the wl1251 mac80211 core driver: firmware/NVS loading, power and boot startup, IRQ work, TX enqueue, interface/config/filter/key/scan/BSS callbacks, EEPROM/NVS MAC handling, hardware allocation, registration, teardown, and module metadata.

Important APIs and functions: Public/exported functions are `wl1251_enable_interrupts()`, `wl1251_disable_interrupts()`, `wl1251_init_ieee80211()`, `wl1251_alloc_hw()`, and `wl1251_free_hw()`. Main mac80211 callbacks include `wl1251_op_start()`, `wl1251_op_stop()`, `wl1251_op_add_interface()`, `wl1251_op_remove_interface()`, `wl1251_op_config()`, `wl1251_op_prepare_multicast()`, `wl1251_op_configure_filter()`, `wl1251_op_tx()`, `wl1251_op_set_key()`, `wl1251_op_hw_scan()`, `wl1251_op_bss_info_changed()`, `wl1251_op_conf_tx()`, and `wl1251_op_get_survey()`. Internal lifecycle helpers load firmware/NVS, wake the chip, join BSS, and read/write MAC addresses.

Control flow: Bus drivers call `wl1251_alloc_hw()` and `wl1251_init_ieee80211()`. mac80211 `start` powers on, resets/wakes the chip, reads chip ID, fetches firmware, boots firmware via `boot.c`, runs `wl1251_hw_init()`, programs station ID, and marks state ON. IRQ handlers only queue `irq_work`; `wl1251_irq_work()` wakes from ELP, masks interrupts, reads/normalizes interrupt bits, handles RX buffers, TX completion, and event mailboxes, then restores interrupt mask and schedules ELP sleep. mac80211 `stop` aborts scans, disables IRQs, cancels work, flushes TX, powers off, and resets volatile state.

State and persistence: Maintains `struct wl1251` runtime state: ON/OFF, BSSID, MAC, BSS type, channel, monitor/joined/scanning flags, RX filters, TX queue state, ELP/PS mode, beacon/DTIM settings, NVS/firmware buffers, debugfs stats, and noise. Persistent inputs are firmware files `ti-connectivity/wl1251-fw.bin`, `ti-connectivity/wl1251-nvs.bin`, optional EEPROM, and possibly rewritten MAC bytes in the in-memory NVS buffer when a random MAC is generated.

Dependencies and integration points: Integrates with Linux mac80211/cfg80211, firmware loader, regulator/bus `if_ops`, `boot.c`, `init.c`, `cmd.c`, `acx.c`, `event.c`, `tx.c`, `rx.c`, `ps.c`, and debugfs. It registers 2.4 GHz channels/rates and station/adhoc interface support.

Risks: Workqueue and IRQ ordering are delicate: stop must disable IRQs, cancel work, and flush frames without racing with TX/RX callbacks. `wl1251_tx_flush()` paths can skip freeing some SKBs when TX status was not requested, which is a leak risk to inspect. Scan and idle transitions rely on ELP wake/sleep and correct join sequencing. The driver only supports a single interface and limited scan SSID behavior.

Test signals: Build warnings for mac80211 API drift, boot logs for firmware version, successful `ieee80211_register_hw()`, scan completion or abort events, TX status callbacks, RX delivery, power-save transitions, CQM RSSI events, key install/remove, and debugfs stats updates. Firmware/NVS absence or invalid MAC path should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/ps.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/ps.c

Purpose: Implements wl1251 power-save and ELP sleep/wakeup transitions.

Important APIs and functions: `wl1251_elp_work()`, `wl1251_ps_elp_sleep()`, `wl1251_ps_elp_wakeup()`, and `wl1251_ps_set_mode()`. Constants define a 5 ms delayed ELP entry and 100 ms ELP wake timeout.

Control flow: `wl1251_ps_elp_sleep()` queues delayed work unless station mode is active. The delayed work locks the device, skips if already in ELP or active, writes `ELPCTRL_SLEEP`, and marks `wl->elp`. Wakeup cancels delayed work, writes `ELPCTRL_WAKE_UP`, polls `ELPCTRL_WLAN_READY`, and clears `wl->elp`. `wl1251_ps_set_mode()` sends different ACX/command sequences for station power-save, idle, and active CAM.

State and persistence: Mutates volatile fields `wl->elp` and `wl->station_mode`, and programs firmware sleep authorization, beacon filtering, wake conditions, BET, PS mode, and disconnect templates. No persistent storage.

Dependencies and integration points: Called by TX work, IRQ work, config changes, scans, key changes, filter changes, BSS changes, and stop cleanup. Depends on ACX helpers and command helpers.

Risks: Wakeup polling is a FIXME replacement for IRQ-driven ready notification, so latency and timeout behavior matter. Mode transitions have multiple firmware steps and can leave partial state if an intermediate command fails. Delayed work cancellation must stay synchronized with `wl->mutex`.

Test signals: Power-save enable/disable, idle transitions, TX while asleep, IRQ wakeups, and scan-from-idle are key runtime checks. Timeout log `elp wakeup timeout` indicates hardware or bus wake failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/ps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/ps.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/ps.h

Purpose: Declares wl1251 power-save and ELP helpers.

Important APIs and types: Provides prototypes for `wl1251_ps_set_mode()`, `wl1251_ps_elp_sleep()`, `wl1251_ps_elp_wakeup()`, and `wl1251_elp_work()`. Uses `enum wl1251_station_mode` and `struct wl1251`.

Control flow: No control flow in the header. It defines the interface for code paths that need to wake firmware before touching registers or queue delayed sleep after work.

State and persistence: Header has no state. Implementations mutate `wl->elp`, `wl->station_mode`, and firmware PS state.

Dependencies and integration points: Included by `main.c`, `tx.c`, and `ps.c`, making power management part of both mac80211 callbacks and data-path work.

Risks: Callers must already understand locking expectations; most runtime callers hold `wl->mutex`. Calling wake/sleep out of sequence can race with delayed work.

Test signals: Compile coverage and runtime ELP transitions in TX, IRQ, scan, and config flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/ps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/reg.h

Purpose: Defines wl1251 target register addresses, partition sizes, ELP controls, EEPROM/chip registers, interrupt register indexes, RX filter bits, firmware boot constants, rates/modulations, and host-to-firmware interrupt trigger bits.

Important APIs and types: Important definitions include `REGISTERS_BASE`, `DRPW_BASE`, `HW_ACCESS_ELP_CTRL_REG_ADDR`, `ELPCTRL_*`, `CHIP_ID_B`, `ENABLE`, scratch-pad and mailbox pointers, `enum wl12xx_acx_int_reg`, `RX_CFG_*`, `RX_FILTER_OPTION_*`, EEPROM registers and control bits, firmware `CHUNK_SIZE`, rate enums, modulation bits, and `INTR_TRIG_*`.

Control flow: No executable control flow. These constants drive address translation, boot, firmware mailbox discovery, RX filter programming, TX/RX buffer acknowledgements, and ELP operations.

State and persistence: Describes hardware state and firmware-visible registers. Values are not stored by the driver except through reads/writes in other modules.

Dependencies and integration points: Included throughout wl1251 boot, IO, PS, RX/TX, ACX, command, event, SPI, and main files. The `enum wl12xx_acx_int_reg` is translated by `io.c` to concrete addresses.

Risks: Register constants are hardware contract values. Incorrect edits can break boot, partitioning, interrupts, EEPROM MAC reads, or data path acknowledgements. Some comments retain historical spelling and reference driver terminology; use behavior over comments when validating.

Test signals: Hardware boot, chip ID recognition, ELP wake, interrupt delivery, RX/TX acknowledgement, EEPROM read, and join/filter behavior validate this file indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/rx.c

Purpose: Implements wl1251 receive processing from firmware double buffers into mac80211 SKBs.

Important APIs and functions: `wl1251_rx()` is the entry from IRQ work. Internal helpers are `wl1251_rx_header()`, `wl1251_rx_body()`, `wl1251_rx_status()`, and `wl1251_rx_ack()`.

Control flow: `wl1251_rx()` checks device state, reads the RX descriptor from the current double-buffer slot, reads the frame body after descriptor and padding, builds `ieee80211_rx_status`, submits the SKB through `ieee80211_rx_ni()`, then acknowledges the consumed buffer by writing the appropriate RX_PROC trigger and toggling `wl->rx_current_buffer`.

State and persistence: Uses `wl->data_path` for firmware RX addresses, `wl->rx_current_buffer` for double-buffer selection, `wl->rx_last_id` for packet sequence sanity, `wl->noise` for survey reporting, and `wl->bss_type`/`monitor_present` for status behavior. No persistent storage.

Dependencies and integration points: Depends on IO helpers, ACX TSF interrogation for IBSS beacons, mac80211 RX status conventions, and rate constants from `reg.h`. Called by `wl1251_irq_work()` when RX interrupt bits are active.

Risks: Descriptor `length` is trusted enough to allocate/read after subtracting `PLCP_HEADER_LENGTH`; malformed firmware descriptors could underflow or oversize reads. For IBSS beacons, status construction can sleep through ACX TSF interrogation, so it is intentionally not in atomic context. Rate mapping has ambiguous 1/12 Mbps handling based on modulation bits.

Test signals: RX packet delivery, beacon reception in STA/IBSS, monitor mode decrypt flags, FCS failure reporting, noise survey values, and logs for out-of-sequence RX packet IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/rx.h

Purpose: Documents and defines the wl1251 RX double-buffer protocol and RX descriptor format.

Important APIs and types: Defines alignment macros, descriptor flag masks, modulation bits, PLCP length, packet ID fields, `struct wl1251_rx_descriptor`, and `wl1251_rx()`.

Control flow: Header comments describe the firmware/host RX sequence: firmware interrupts, host reads one of two buffers, host triggers RX acknowledgement, firmware prepares the next packet.

State and persistence: No state in header; constants map firmware descriptor state into driver decisions. Descriptor fields include timestamp, length, flags, type, rate, modulation/preamble, channel/band, RSSI/RCPI/SNR.

Dependencies and integration points: Used by `rx.c`, `wl1251.h`, and allocation of `wl->rx_descriptor` in `main.c`.

Risks: This packed structure must match firmware layout exactly. Any change to alignment, flag masks, or descriptor layout risks corrupt RX parsing.

Test signals: Compile layout compatibility, RX rate/status correctness, encryption/FCS flags, and buffer toggling under sustained receive load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/sdio.c

Purpose: Provides the SDIO bus binding for the wl1251 core driver, including SDIO memory access, ELP access, interrupts, power/runtime PM, probe/remove, and module registration.

Important APIs and functions: Core bus operations are `wl1251_sdio_read()`, `wl1251_sdio_write()`, `wl1251_sdio_read_elp()`, `wl1251_sdio_write_elp()`, `wl1251_sdio_set_power()`, IRQ enable/disable variants, and `wl1251_sdio_probe()/remove()`. `struct wl1251_sdio` stores the `sdio_func` and cached ELP value.

Control flow: Probe allocates wl1251 hw, allocates bus-private data, enables the SDIO function, sets block size, configures optional OF EEPROM flag and dedicated IRQ, selects dedicated line IRQ or SDIO IRQ operations, initializes/registers mac80211, stores drvdata, and drops runtime PM usage. Power on gets runtime PM, enables function, and power off disables function and puts runtime PM. Interrupt callbacks queue wl1251 IRQ work.

State and persistence: Maintains `wl->if_priv`, dynamic `wl1251_sdio`, `wl->irq`, `wl->use_eeprom`, and the cached `elp_val` required for SDIO RAW ELP reads. No persistent storage.

Dependencies and integration points: Implements `wl1251_if_operations` for the shared core in `main.c`. Integrates with Linux MMC/SDIO, OF IRQ lookup, runtime PM, and mac80211 registration.

Risks: `wl1251_sdio_ops` is a static struct mutated at probe time to choose IRQ operations, which can be unsafe for multiple devices with different IRQ modes. Some SDIO enable/disable return values are not checked in power paths. Remove always calls `sdio_release_irq()` even when dedicated line IRQ was used.

Test signals: SDIO probe/remove, runtime suspend/resume, dedicated IRQ and SDIO IRQ variants, ELP wake on SDIO, firmware boot, and repeated start/stop cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/spi.c

Purpose: Provides the SPI bus binding for wl1251, including WSPI reset/wake commands, SPI read/write transactions, GPIO power control, IRQ handling, regulator management, probe/remove, and module registration.

Important APIs and functions: `wl1251_spi_reset()`, `wl1251_spi_wake()`, `wl1251_spi_reset_wake()`, `wl1251_spi_read()`, `wl1251_spi_write()`, IRQ enable/disable, power setter, `wl1251_spi_probe()`, and `wl1251_spi_remove()`. `struct wl1251_spi` stores the SPI device and optional power GPIO.

Control flow: Probe requires an OF node, allocates shared hardware through `wl1251_alloc_hw()`, attaches SPI private data and operations, sets `bits_per_word` to 32, reads `ti,wl1251-has-eeprom`, acquires optional power GPIO and `vio` regulator, requests rising-edge IRQ with `IRQ_NOAUTOEN`, enables regulator, and initializes mac80211. IRQ handler queues core IRQ work. SPI read/write build WSPI command words, perform `spi_sync()`, and transfer busy words/data.

State and persistence: Stores bus-private pointer in `wl->if_priv`, selected operations in `wl->if_ops`, IRQ in `wl->irq`, regulator in `wl->vio`, and optional GPIO. Uses shared command/busy buffers in `struct wl1251`.

Dependencies and integration points: Implements the bus contract consumed by `io.h`/`io.c` and the core driver. Depends on Linux SPI, GPIO descriptor, regulator, OF, CRC7, and byte-swap helpers.

Risks: `spi_sync()` return values are ignored in reset, wake, read, and write paths, so bus transfer failures may be silent. Busy words are read but not validated. Command construction and byte swapping are hardware-specific; changes require WSPI validation. Probe requires OF and will reject non-DT SPI instantiation.

Test signals: Probe with valid DT/regulator/GPIO/IRQ, firmware boot over SPI, ELP wake, sustained RX/TX, and fault injection for failed SPI transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/spi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/spi.h

Purpose: Defines wl1251 WSPI command and initialization bit fields used by the SPI bus implementation.

Important APIs and types: Defines read/write command bits, byte length/address masks and shifts, init command fields, CRC length, command length, fixed busy length calculation, and init mask.

Control flow: No executable code. Constants are consumed by `spi.c` to build reset/wake/read/write transactions.

State and persistence: No state. Values encode hardware protocol requirements.

Dependencies and integration points: Includes `cmd.h`, `acx.h`, and `reg.h` for related firmware definitions. Used only by the SPI binding.

Risks: Bit masks must match the WSPI hardware protocol exactly. Mis-sizing `WL1251_BUSY_WORD_LEN` or command length changes SPI framing and can break all bus access.

Test signals: SPI reset/wake command success, correct register reads after wake, and stable firmware boot over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/tx.c

Purpose: Implements wl1251 transmit queue processing, firmware TX descriptor construction, double-buffer submission, TX completion processing, mac80211 status reporting, and TX flush.

Important APIs and functions: Public driver entry points are `wl1251_tx_work()`, `wl1251_tx_complete()`, and `wl1251_tx_flush()`. Internal helpers include `wl1251_tx_path_status()`, `wl1251_tx_id()`, `wl1251_tx_fill_hdr()`, `wl1251_tx_send_packet()`, `wl1251_tx_trigger()`, `wl1251_tx_packet_cb()`, and `enable_tx_for_packet_injection()`.

Control flow: mac80211 queues SKBs in `main.c`; `wl1251_tx_work()` wakes ELP once, drains the software queue, checks firmware double-buffer availability, assigns a completion ID, prepends a TX descriptor, handles TKIP IV space and DMA alignment, writes the packet into the selected firmware TX ring chunk, triggers firmware, and reschedules/backs off on `-EBUSY`. TX completion reads the cyclic result ring, walks entries owned by host (`done_1` and `done_2`), restores the SKB by removing private headers/TKIP space, reports status to mac80211, clears result entries back to firmware, updates `next_tx_complete`, and wakes queues if low-watermark is reached.

State and persistence: Uses and mutates `wl->data_in_count`, `wl->tx_queue`, `wl->tx_queue_stopped`, `wl->tx_frames[]`, `wl->next_tx_complete`, retry stats, `wl->joined`, and `wl->default_key`. All state is volatile and reset on stop.

Dependencies and integration points: Depends on `io.c` memory/register writes, power-save wake/sleep, command/event join for injection, mac80211 TX APIs, ACX default key programming, and firmware data path addresses from `init.c`.

Risks: TX SKB ownership is subtle. Error paths after ID assignment must not leak or double-free; alignment replacement updates `wl->tx_frames[id]`. `wl1251_tx_flush()` skips status and freeing for SKBs without requested status in some paths, which deserves leak-focused testing. Static status parser buffer is not reentrant, though used under serialized context. Hardware queue fullness depends on modulo counters.

Test signals: Sustained TX under queue pressure, queue stop/wake transitions, TKIP and CCMP encrypted TX, injected monitor TX, TX retry/excessive retry stats, completion ring wraparound, and stop-time flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/tx.h

Purpose: Defines wl1251 TX descriptor/control/result layouts, status bits, alignment helpers, queue mapping, and TX path entry points.

Important APIs and types: `struct tx_control`, `struct tx_double_buffer_desc`, `struct tx_result`, TX status bit enum, `wl1251_tx_get_queue()`, `wl1251_tx_work()`, `wl1251_tx_complete()`, and `wl1251_tx_flush()`.

Control flow: Header comments document host TX double-buffer flow and TX-complete cyclic ring ownership protocol. `wl1251_tx_get_queue()` maps mac80211 queue indexes to firmware AC queues VO/VI/BE/BK.

State and persistence: No stored state in the header; packed structures define firmware-owned/shared memory layouts and host-owned SKB metadata IDs.

Dependencies and integration points: Included by `tx.c` and `main.c`; descriptor size is used as mac80211 `extra_tx_headroom`.

Risks: Packed bitfields and firmware descriptors must match target ABI. Compiler bitfield layout assumptions are always a portability risk in hardware descriptors. Queue mapping must stay consistent with ACX queue config.

Test signals: Compile layout, successful TX completion ownership handoff, correct ACK status reporting, and queue mapping behavior under QoS traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/wl1251.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/wl1251.h

Purpose: Central wl1251 core header defining logging/debug macros, default RX filters, driver state enums, partition structures, statistics/debugfs structures, bus operation interface, main `struct wl1251`, public core APIs, defaults, chip IDs, firmware names, and partition constants.

Important APIs and types: `enum wl1251_state`, `enum wl1251_partition_type`, `enum wl1251_station_mode`, `struct wl1251_if_operations`, `struct wl1251`, `wl1251_alloc_hw()`, `wl1251_free_hw()`, `wl1251_init_ieee80211()`, IRQ enable/disable helpers, chip IDs, firmware/NVS names, TX queue watermarks, default channel/beacon/DTIM/power values, and partition definitions.

Control flow: No executable control flow, but the structure layout defines how all modules share runtime state. Bus drivers fill `if_priv`, `if_ops`, `irq`, and optional power resources; core mac80211 and data path modules mutate the remaining fields.

State and persistence: `struct wl1251` stores all volatile driver state: hardware pointer, registration flag, bus operations, partitions, firmware/NVS buffers, MAC/BSSID/channel/interface state, memory maps, TX/RX counters and queues, IRQ/event masks, ELP/PS flags, stats, debugfs dentries, buffers, chip ID, firmware version, and noise. Firmware and NVS names identify persistent external blobs.

Dependencies and integration points: Included by nearly every wl1251 file. Bridges bus-specific SPI/SDIO code with common mac80211 core through `wl1251_if_operations`.

Risks: This is a broad shared-state contract. Adding fields or changing semantics requires auditing locking, reset in `wl1251_op_stop()`, allocation/free paths, and bus probe/remove. Debug macros are compile-time disabled by `DEBUG_LEVEL`, so runtime diagnostics may be sparse.

Test signals: Whole-driver compile, probe/start/stop, leak checks across `wl1251_alloc_hw()`/`wl1251_free_hw()`, and consistency of state reset after repeated interface cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/wl1251.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/wl12xx_80211.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/wl12xx_80211.h

Purpose: Defines 802.11 rate constants, rate masks, IE structures, and firmware template packet layouts used by wl1251 command template programming.

Important APIs and types: Rate constants/masks for CCK and OFDM, `MAX_SUPPORTED_RATES`, `MAX_COUNTRY_TRIPLETS`, `struct ieee80211_header`, IE structures for SSID/rates/DS/country, and template structures for beacon, null data, PS-poll, QoS null, probe request, and probe response.

Control flow: No executable logic. The structures provide fixed sizes and layouts used when reserving or uploading firmware templates.

State and persistence: No state. Template structures represent firmware-resident frame templates after uploaded through command helpers.

Dependencies and integration points: Included by `init.c` and `main.c` for template sizing and construction. Uses Linux Ethernet and IEEE80211 constants.

Risks: Packed template layouts must match firmware expectations. `MAX_SUPPORTED_RATES` is intentionally larger than standard expectations because of firmware behavior; shrinking it can break template compatibility.

Test signals: Successful template reservation during init, probe request scan templates, null/QoS null power-save templates, AP/IBSS beacon/probe response template updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/wl12xx_80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/Kconfig

Purpose: Defines the kernel configuration option for the wl12xx driver.

Important APIs and symbols: `config WL12XX` is a tristate named "TI wl12xx support"; it depends on `MAC80211` and selects `WLCORE`.

Control flow: No runtime control flow. Build selection determines whether the wl12xx module is compiled.

State and persistence: Kconfig state is build configuration, not runtime state. The help text explicitly excludes wl1251 support and points users to the separate wl1251 driver.

Dependencies and integration points: Integrates with the kernel wireless driver Kconfig tree and wlcore common library.

Risks: Missing `select WLCORE` would break linkage because wl12xx delegates most runtime logic to wlcore. Confusing wl12xx with wl1251 can lead to unsupported hardware selection.

Test signals: Kernel config resolution, module build, and dependency selection for `MAC80211`/`WLCORE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/Makefile

Purpose: Defines the wl12xx module object composition.

Important APIs and symbols: `wl12xx-objs` includes `main.o`, `cmd.o`, `acx.o`, `debugfs.o`, `scan.o`, and `event.o`; `obj-$(CONFIG_WL12XX)` builds `wl12xx.o`.

Control flow: No runtime control flow. The object list controls what code is linked into the module.

State and persistence: Build metadata only.

Dependencies and integration points: Must align with functions referenced by the `wlcore_ops` table in `main.c`, including scan/event/debugfs callbacks.

Risks: Omitting an object causes unresolved symbols or missing callbacks. Adding files requires updating this list.

Test signals: Module link success for `CONFIG_WL12XX=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/acx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/acx.c

Purpose: Implements a wl12xx-specific ACX helper for configuring host interface behavior.

Important APIs and functions: `wl1271_acx_host_if_cfg_bitmap(struct wl1271 *wl, u32 host_cfg_bitmap)` allocates a `wl1271_acx_host_config_bitmap`, stores the bitmap little-endian, and sends `ACX_HOST_IF_CFG_BITMAP` through `wl1271_cmd_configure()`.

Control flow: Allocation, field fill, configure command, warning on failure, free, return status. It is called from wl12xx hardware init before memory configuration for wl128x, especially to enable RX FIFO and optional SDIO TX padding.

State and persistence: Does not store host state locally; programs firmware configuration. The requested bitmap comes from `main.c` according to chip quirks.

Dependencies and integration points: Depends on wlcore command and ACX infrastructure. Used by `wl12xx_hw_init()` in `main.c`.

Risks: Must be sent before memory configuration per comment in `main.c`; wrong order can break wl128x host interface behavior. Allocation failure and firmware command failure are propagated.

Test signals: wl128x boot/hw init success, RX FIFO operation, and TX blocksize padding behavior on SDIO-aligned chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/acx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/acx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/acx.h

Purpose: Defines wl12xx ACX event masks, host interface bitmap command structure, and firmware statistics layout used by debugfs and wlcore.

Important APIs and types: `WL12XX_ACX_ALL_EVENTS_VECTOR`, `WL12XX_INTR_MASK`, `struct wl1271_acx_host_config_bitmap`, many `wl12xx_acx_*_statistics` structs, aggregate `struct wl12xx_acx_statistics`, and `wl1271_acx_host_if_cfg_bitmap()`.

Control flow: Header only. The event mask constants are used by boot interrupt setup, and statistics structs are used for debugfs field extraction.

State and persistence: Describes firmware statistics snapshots and interrupt mask bits. No local storage.

Dependencies and integration points: Includes wlcore core and ACX headers. Tied to `debugfs.c`, `acx.c`, and `main.c`.

Risks: Statistics structure layout must match firmware ACX statistics response exactly; debugfs fields will report nonsense if offsets drift. Interrupt mask constants determine which firmware interrupts reach the host.

Test signals: Debugfs firmware stats reads, event interrupt delivery, and wl128x host interface configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/acx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/cmd.c

Purpose: Implements wl12xx firmware command helpers for INI/NVS general parameters, radio parameters, extended RF compensation, and channel switch commands.

Important APIs and functions: `wl1271_cmd_general_parms()`, `wl128x_cmd_general_parms()`, `wl1271_cmd_radio_parms()`, `wl128x_cmd_radio_parms()`, `wl1271_cmd_ext_radio_parms()`, and `wl12xx_cmd_channel_switch()`.

Control flow: General parameter commands validate NVS presence and FEM index, copy chip-specific NVS general parameters, optionally force FEM auto-detect in PLT mode, override ref/TCXO clocks from platform/private config, send a firmware test command, then copy back the detected FEM manufacturer. Radio parameter commands select the FEM-specific NVS entry and send static/dynamic 2.4/5 GHz radio parameters. Extended radio parameters send per-channel power compensation arrays. Channel switch allocates a command, fills role/channel/count/stop flags from mac80211, and sends `CMD_CHANNEL_SWITCH`.

State and persistence: Reads and mutates the in-memory NVS blob for FEM manufacturer, stores detected FEM in `wl->fem_manuf` during calibrator mode, and uses `priv->conf.rf` compensation and `priv->ref_clock`/`tcxo_clock`. No disk persistence.

Dependencies and integration points: Called by `wl12xx_hw_init()` and channel-switch wlcore op. Depends on wlcore command transport, `conf.h`, `wl12xx.h` NVS layouts, and mac80211 channel switch data.

Risks: FEM index bounds are critical before indexing dynamic radio parameter arrays. The functions return `-ENODEV` without NVS, so NVS loading is mandatory except special flows. Incorrect clock override values can make firmware radio calibration fail.

Test signals: Boot/hw init on wl127x and wl128x with valid NVS, PLT FEM auto-detect, channel switch completion events, and command failure warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/cmd.h

Purpose: Defines wl12xx command payload structures for INI/NVS firmware test commands and channel switching.

Important APIs and types: Test command IDs `TEST_CMD_INI_FILE_RADIO_PARAM`, `TEST_CMD_INI_FILE_GENERAL_PARAM`, and `TEST_CMD_INI_FILE_RF_EXTENDED_PARAM`; command structs for wl1271/wl128x general parameters, radio parameters, extended radio parameters, and `wl12xx_cmd_channel_switch`; prototypes for command helpers.

Control flow: No executable control flow. Struct definitions determine payload layout for `cmd.c`.

State and persistence: No stored state. Structures carry NVS-derived data into firmware and may carry updated general params back from firmware test commands.

Dependencies and integration points: Includes `conf.h` for RF compensation lengths. Depends on wlcore command header types and NVS parameter types via included headers.

Risks: Packed structure layouts are firmware ABI. Padding bytes are explicit and should not be removed. wl1271 and wl128x layouts differ and must not be interchanged.

Test signals: Firmware accepts test commands during hw init; FEM auto-detect and radio parameter programming work on both chip families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/conf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/conf.h

Purpose: Defines wl12xx private configuration structures and Soft Gemini coexistence parameter indexes.

Important APIs and types: `CONF_TX_PWR_COMPENSATION_LEN_2`, `CONF_TX_PWR_COMPENSATION_LEN_5`, `struct wl12xx_conf_rf`, `struct wl12xx_priv_conf`, and `enum wl12xx_sg_params`.

Control flow: Header only. The enum indexes into `wlcore_conf.sg.params`, and the RF arrays feed extended radio parameter commands.

State and persistence: No storage here. `main.c` creates default instances using these types, and `cmd.c` reads them while building firmware commands.

Dependencies and integration points: Used by `main.c`, `cmd.c`, and `cmd.h`. Ties wl12xx-specific SG and RF values to generic wlcore configuration.

Risks: SG enum order is an ABI between default config and firmware ACX configuration. Changing enum order without updating defaults changes coexistence behavior. RF compensation lengths must match firmware expectations.

Test signals: Bluetooth/WLAN coexistence behavior, scan under BT traffic, extended radio parameter command success, and compile-time bounds checks in `main.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/conf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/debugfs.c

Purpose: Adds wl12xx-specific firmware statistics files under debugfs.

Important APIs and functions: Macro `WL12XX_DEBUGFS_FWSTATS_FILE()` defines many field readers over `struct wl12xx_acx_statistics`. `wl12xx_debugfs_add_files()` creates a module directory, `fw_stats` directory, and registers statistic files for tx, rx, dma, isr, wep, pwr, mic, aes, event, ps, and rxpipe groups.

Control flow: At debugfs init, create directories and add each firmware stat file through wlcore debugfs macros. Reads are handled by generated wlcore/debugfs helpers.

State and persistence: Debugfs exposes volatile firmware statistics snapshots stored in wlcore stats buffers. It does not persist data.

Dependencies and integration points: `wl12xx_ops.debugfs_init` points here. Depends on `wlcore/debugfs.h`, `wlcore/wlcore.h`, and the statistics layout in `acx.h`.

Risks: No explicit error handling for failed debugfs directory/file creation, consistent with debugfs being optional. Field definitions must match `struct wl12xx_acx_statistics`.

Test signals: Presence and readability of `/sys/kernel/debug/.../wl12xx/fw_stats/*` files after device init, and plausible changing counters under RX/TX/PS activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/debugfs.h

Purpose: Declares wl12xx debugfs initialization hook.

Important APIs and types: `wl12xx_debugfs_add_files(struct wl1271 *wl, struct dentry *rootdir)`.

Control flow: No control flow. The function is referenced by the wlcore ops table.

State and persistence: No state; implementation exposes volatile firmware stats through debugfs.

Dependencies and integration points: Included by `main.c` for `wl12xx_ops.debugfs_init` and by `debugfs.c`.

Risks: Signature must match wlcore's expected debugfs callback type.

Test signals: Build/link success and debugfs file creation after wlcore debugfs init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/event.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/event.c

Purpose: Translates wl12xx firmware mailbox events into wlcore/mac80211 actions and implements waiting for selected firmware events.

Important APIs and functions: `wl12xx_wait_for_event()` maps generic wlcore wait events to wl12xx event bits, and `wl12xx_process_mailbox_events()` consumes a `wl12xx_event_mailbox`.

Control flow: `wl12xx_wait_for_event()` supports role stop and peer remove completion by calling `wlcore_cmd_wait_for_event_or_timeout()`. Mailbox processing masks event bits by `events_mask`, logs the vector, completes scans, reports scheduled scan results/completion, handles soft Gemini sense, beacon loss, RSSI trigger, BA RX constraint, channel switch, dummy packet, max TX retry, inactive station, and remain-on-channel completion through wlcore event helpers.

State and persistence: Reads volatile mailbox data from `wl->mbox`. It may clear scan state indirectly through scan completion helpers and update cfg80211/mac80211 state through wlcore events.

Dependencies and integration points: Registered as `process_mailbox_events` and `wait_for_event` in `wl12xx_ops`. Depends on `scan.h`, `event.h`, wlcore command/debug/event helpers, and mac80211/cfg80211 upper layers through wlcore.

Risks: Unsupported wait events return success (`0`) without waiting, which is intentional for unimplemented events but can hide missing mappings if new wlcore waits are added. Event role IDs sometimes pass `0xff` rather than mailbox role fields, so multi-role handling depends on wlcore semantics.

Test signals: Scan completion, scheduled scan reports, beacon loss CQM, RSSI triggers, channel switch completion, ROC completion, inactive station cleanup, and AP max retry handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/event.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/event.h

Purpose: Defines wl12xx firmware event bit IDs, mailbox layout, and event-processing prototypes.

Important APIs and types: Event bit enum includes scan, role stop, radar/channel switch, BSS loss/regain, max TX retry, dummy packet, Soft Gemini, inactive station, peer remove, periodic scan, BA constraint, and remain-on-channel. `struct wl12xx_event_mailbox` defines the firmware mailbox fields. Prototypes expose wait and processing functions.

Control flow: No executable control flow. The bit definitions drive event masks and mailbox processing.

State and persistence: Describes volatile firmware mailbox state. Fields carry scan status, RSSI metrics, HLID bitmaps, channel switch status, role IDs, and event status bytes.

Dependencies and integration points: Included by `event.c` and `main.c`; event masks in `wl12xx_boot()` use these constants.

Risks: Packed mailbox layout is firmware ABI. Bit positions overlap a 32-bit event vector and must remain correct. Any mismatch will route wrong events to wlcore.

Test signals: Correct handling of each event class, especially scheduled scan, channel switch, peer removal, and AP station aging/retry events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/main.c

Purpose: Implements the wl12xx wlcore child driver: default configuration, chip identification, boot clock programming, partition/register tables, firmware boot hooks, command/event/TX/RX/status ops, MAC/fuse handling, setup/probe/remove, module parameters, and firmware metadata.

Important APIs and functions: Key functions include `wl12xx_identify_chip()`, `wl12xx_top_reg_read/write()`, `wl128x_boot_clk()`, `wl127x_boot_clk()`, `wl1271_boot_soft_reset()`, `wl12xx_pre_boot()`, `wl12xx_pre_upload()`, `wl12xx_enable_interrupts()`, `wl12xx_boot()`, `wl12xx_trigger_cmd()`, `wl12xx_ack_event()`, TX descriptor helpers, RX packet helpers, `wl12xx_hw_init()`, `wl12xx_convert_fw_status()`, `wl12xx_get_pg_ver()`, `wl12xx_get_mac()`, `wl12xx_plt_init()`, `wl12xx_setup()`, `wl12xx_probe()`, and `wl12xx_remove()`. `wl12xx_ops` is the central wlcore callback table.

Control flow: Platform probe allocates wlcore hardware, installs `wl12xx_ops` and partition table, then calls `wlcore_probe()`. Setup populates wlcore capabilities, descriptor counts, link counts, interface combinations, rate tables, HT caps, config defaults, platform/module clock indexes, and private RX memory helper. Chip identification chooses wl127x or wl128x firmware names, quirks, memory config, min firmware versions, and prepare-read behavior. Boot configures clocks and partitions, uploads NVS, applies pre-upload register tweaks, uploads/runs firmware, programs event masks, and enables interrupts. Hardware init sends chip-specific NVS radio/general commands and wl128x host-interface bitmap. Runtime ops delegate most behavior to wlcore with wl12xx-specific descriptor, status, event, scan, key, and channel switch hooks.

State and persistence: Static defaults in `wl12xx_conf` and `wl12xx_default_priv_conf` seed runtime `wl->conf` and private config. Runtime state includes wlcore `wl1271`, `wl12xx_priv`, quirks, firmware names, partition/register tables, platform clock selections, FEM manufacturer, fuse MAC pieces, and allocated `priv->rx_mem_addr`. Module parameters `fref` and `tcxo` can override platform clock data.

Dependencies and integration points: Deeply integrated with `../wlcore` for allocation, probe, IO, boot upload, commands, TX/RX, ACX, scan, event, debugfs, and mac80211 integration. Uses local `reg.h`, `cmd.h`, `acx.h`, `scan.h`, `event.h`, `debugfs.h`, and `conf.h`. Platform data supplies clock frequencies and XTAL flags.

Risks: Boot clock programming is hardware-sensitive, especially wl128x TCXO/FREF switching and OCP top-register polling. There is a suspicious check in XTAL-only wl128x flow where success from `wl128x_switch_tcxo_to_fref()` causes `-EINVAL`, worth reviewing against upstream history. Module parameter parsing logs invalid strings but does not always return an error immediately. Unlocking mutex inside `wl12xx_plt_init()` to disable interrupts is explicitly called unsafe but justified by state assumptions.

Test signals: Probe with wl127x PG10/PG20 and wl128x PG20 IDs, invalid chip rejection, firmware name/min-version validation, NVS upload and radio command success, interrupt delivery, scan/scheduled scan, TX/RX, channel switch, PLT/FEM detect, fuse MAC extraction, debugfs stats, and module clock override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/reg.h

Purpose: Defines wl12xx hardware register addresses, firmware status address, OCP top-register access protocol, clock/PLL configuration bits, interrupt trigger bits, HI config, PG/fuse decoding macros, and fuse MAC register addresses.

Important APIs and types: Key constants include `REGISTERS_BASE`, `DRPW_BASE`, `FW_STATUS_ADDR`, `WL12XX_SLV_SOFT_RESET`, slave data registers, interrupt registers, ECPU/HI config, OCP registers and status bits, scratch pads, PLL/clock registers, `WL12XX_CMD_MBOX_ADDRESS`, `WL12XX_EEPROMLESS_IND`, `WL12XX_INTR_TRIG_CMD`, `WL12XX_INTR_TRIG_EVENT_ACK`, `HI_CFG_DEF_VAL`, PG version masks/macros, and fuse BD address registers.

Control flow: Header only. Its constants drive `main.c` boot, OCP read/write polling, partition register table setup, interrupt enabling, command triggering, and MAC/fuse reads.

State and persistence: Describes hardware register state and fuse contents. Fuse MAC and PG version are persistent in hardware, while most registers are volatile boot/runtime state.

Dependencies and integration points: Included by wl12xx `main.c` and any code needing chip register definitions. Values are mapped into wlcore generic register IDs through `wl12xx_rtable`.

Risks: Register values are hardware ABI. Incorrect OCP status masks or clock bits can break boot. PG version macros differ between wl127x and wl128x and must be used with the correct chip family.

Test signals: Successful chip ID and PG version reads, soft reset completion, clock/PLL programming, firmware status reads, command/event interrupt triggers, and fuse MAC extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/reg.h -->
