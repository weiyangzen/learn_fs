# Research Group: subset-b-004967

This grouped report covers the assigned wireless driver sources and preserves source paths for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/traces.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/traces.h

Purpose: Defines Linux tracepoints for the Silicon Labs WFX wireless driver. It gives ftrace/perf visibility into HIF command traffic, bus register I/O, piggybacked control words, bottom-half accounting, TX completion latency, rate retry state, and per-VIF queue depth.

Important APIs and types: The file exports trace events through `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_EVENT`: `hif_send`, `hif_recv`, `io_write`, `io_read`, `io_write32`, `io_read32`, `piggyback`, `bh_stats`, `tx_stats`, and `queues_stats`. Symbol tables are built with `TRACE_DEFINE_ENUM` lists for HIF message IDs, HIF MIB IDs, and WFX register IDs so trace output remains readable. The event payloads depend on `struct wfx_hif_msg`, `struct wfx_hif_cnf_tx`, `struct wfx_dev`, `struct wfx_vif`, and `struct wfx_queue`.

Control flow: There is no runtime control path beyond tracepoint fast-assign and print formatting. The HIF event class computes message type from direction and message ID, detects READ/WRITE MIB requests, copies a bounded payload preview, and prints symbolic command/MIB names. I/O tracepoints copy short register payload previews. `tx_stats` decodes mac80211 retry flags and firmware status. `queues_stats` iterates WFX VIFs to snapshot hardware-pending, normal, and CAB queues.

State and persistence: Tracepoints do not persist driver state. They sample transient buffers, queue atomics, skb metadata, and firmware completion fields. Bounded array copies are used for trace payload safety.

Dependencies and integration: Depends on kernel tracing, mac80211, WFX bus/register constants, HIF API headers, and `wfx.h` iteration helpers. The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` block is required by Linux tracepoint generation.

Risks: Trace format must stay synchronized with HIF numeric IDs and WFX rate tables; the comment in `tx_stats` explicitly ties hardware rate decoding to `main.c`. Bad length handling could underflow `buf_len` if malformed HIF frames report very short lengths, so callers must trace valid frames. Queue indexing assumes at most two VIFs.

Test signals: Build with tracing enabled; verify generated trace headers compile. Runtime signals include enabling `wfx:hif_send`, `wfx:hif_recv`, and queue/TX events while scanning and transmitting, checking symbolic names, bounded hex dumps, and sensible queue depth output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/traces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/wfx.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/wfx.h

Purpose: Central private data header for the Silicon Labs WFX mac80211 driver. It defines device-wide and virtual-interface state shared across bus, HIF, TX/RX, scan, power, and queue code.

Important APIs and types: `struct wfx_dev` holds platform data, device and mac80211 handles, two VIF slots, hardware bus callbacks, firmware startup data, HIF command state, bottom-half workqueue, TX pending queues, packet/key maps, scan/config mutexes, and RX/TX statistics. `struct wfx_vif` stores per-interface channel/id, link map, power-save/join state, beacon-loss work, four TX queues, TX policy cache, TIM update work, scan work, and remain-on-channel state. Inline helpers include `wvif_to_vif`, `wdev_to_wvif`, `wvif_iterate`, `wvif_count`, `memreverse`, and `memzcmp`.

Control flow: The header provides safe VIF lookup and iteration. `wdev_to_wvif` validates the VIF index, uses `array_index_nospec` to avoid speculative out-of-bounds access, and maps mac80211 `drv_priv` into driver-private VIF data. `wvif_iterate` walks the two VIF slots from either the start or after a current VIF.

State and persistence: State is in memory only and bound to mac80211 device lifetime. Important synchronization primitives are mutexes, completions, wait queues, atomics, work items, and delayed work.

Dependencies and integration: Includes mac80211, Linux workqueue/mutex/completion APIs, and WFX local headers for bottom-half, TX, queue, and HIF command handling. Other WFX files include this header to share the common object model.

Risks: Many fields are concurrency-sensitive and rely on external locking conventions not documented here. The driver supports exactly two VIF slots, so code using VIF IDs must respect that limit. `memzcmp` returns `memcmp(buf, buf + 1, size - 1)` after checking the first byte, which is compact but non-obvious.

Test signals: Compile coverage should catch struct/member drift. Runtime testing should exercise two-VIF lookup/iteration, VIF add/remove, scan and TX paths, and invalid VIF ID debug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/wfx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/Kconfig

Purpose: Vendor-level Kconfig menu for STMicroelectronics wireless devices.

Important APIs and types: Defines `WLAN_VENDOR_ST` as a boolean menu gate defaulting to `y`. When enabled, it sources `drivers/net/wireless/st/cw1200/Kconfig`.

Control flow: Kconfig selection only affects configuration visibility. Disabling the vendor option hides ST driver questions; it does not directly build code.

State and persistence: The selected Kconfig symbols persist in the kernel `.config`.

Dependencies and integration: Integrated from the parent wireless vendor Kconfig tree. Its only child in this subset is the CW1200 family.

Risks: If `WLAN_VENDOR_ST=n`, users cannot select CW1200 bus support even when hardware is present. The file is intentionally minimal and depends on the parent tree for menu placement.

Test signals: `make menuconfig` should show the vendor menu and reveal CW1200 options when enabled. Kconfig lint/build tests should verify the sourced path remains valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/Makefile

Purpose: Vendor-level build glue for ST wireless drivers.

Important APIs and types: Adds the `cw1200/` subdirectory to `obj-y`/`obj-m` when `CONFIG_CW1200` is enabled.

Control flow: Kbuild descends into the CW1200 directory only for enabled core support. Bus modules are selected within that subdirectory.

State and persistence: No runtime state. Build state is controlled by kernel configuration symbols.

Dependencies and integration: Depends on the CW1200 subdirectory Makefile and parent wireless Makefile traversal.

Risks: If new ST drivers are added, this Makefile must be extended. Current file intentionally builds only CW1200.

Test signals: `make M=drivers/net/wireless/st` or full kernel builds should include `cw1200/` when `CONFIG_CW1200` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/Kconfig

Purpose: Configuration menu for the ST-Ericsson CW1100/CW1200 mac80211 driver family.

Important APIs and types: Defines `CW1200` as the shared core tristate depending on `MAC80211` and `CFG80211`. Under `if CW1200`, it defines `CW1200_WLAN_SDIO` depending on `MMC` and `CW1200_WLAN_SPI` depending on `SPI`.

Control flow: Users first enable the common core, then choose one or both bus front-ends. Help text documents that SDIO defaults target Sagrad SG901-1091/1098 style platform data and that other designs need board/platform-data glue.

State and persistence: Kconfig selections persist in `.config` and drive Kbuild module generation.

Dependencies and integration: Integrates with cfg80211/mac80211 and either MMC SDIO or SPI subsystems. It controls objects declared in the CW1200 Makefile.

Risks: The driver is platform-data oriented; modern device-tree-only systems may need board-specific glue not represented by these options. Enabling the core without a bus module builds common code but cannot bind hardware.

Test signals: Build matrix should cover `CW1200=m` with SDIO, SPI, both, and neither bus front-end, plus dependency rejection when MMC/SPI or mac80211/cfg80211 are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/Makefile

Purpose: Kbuild definition for CW1200 common and bus-specific modules.

Important APIs and types: `cw1200_core-y` combines `fwio.o`, `txrx.o`, `main.o`, `queue.o`, `hwio.o`, `bh.o`, `wsm.o`, `sta.o`, `scan.o`, and `debug.o`. `cw1200_core-$(CONFIG_PM)` adds `pm.o`. `cw1200_wlan_sdio-y` and `cw1200_wlan_spi-y` define one-object bus modules.

Control flow: `obj-$(CONFIG_CW1200)` emits the core module; SDIO and SPI configs emit front-end modules that call exported core probe/release symbols.

State and persistence: Build-only state.

Dependencies and integration: Mirrors the Kconfig symbols and links common code separately from transport-specific code. Comments include an optional debug CFLAG for `sta.o`.

Risks: Common code and bus modules must agree on exported symbols such as `cw1200_core_probe`, `cw1200_core_release`, `cw1200_irq_handler`, and `cw1200_can_suspend`. Missing a source in `cw1200_core-y` would manifest as unresolved symbols.

Test signals: Module builds should produce `cw1200_core`, `cw1200_wlan_sdio`, and/or `cw1200_wlan_spi` according to config. PM-enabled builds should link suspend/resume handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/bh.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/bh.c

Purpose: Implements the CW1200 bottom-half service loop that connects device interrupts, WSM RX/TX processing, firmware queue buffers, and chip sleep/wake management.

Important APIs and functions: Public entry points are `cw1200_register_bh`, `cw1200_unregister_bh`, `cw1200_irq_handler`, `cw1200_bh_wakeup`, `cw1200_bh_suspend`, `cw1200_bh_resume`, `cw1200_enable_powersave`, and `wsm_release_tx_buffer`. Internal helpers include `cw1200_bh_read_ctrl_reg`, `cw1200_device_wakeup`, `cw1200_bh_rx_helper`, `cw1200_bh_tx_helper`, and the main `cw1200_bh` worker.

Control flow: Registration creates a high-priority workqueue and queues the BH worker. IRQ handlers disable device interrupts under bus lock and increment `bh_rx`. TX producers increment `bh_tx`. The loop sleeps on `bh_wq`, periodically wakes for interrupt-loss detection or power-down, reads the control register, drains one or two RX frames based on `NEXT_LEN`, feeds TX if firmware input buffers are available, then re-enables interrupts. Suspend requests transition through `CW1200_BH_SUSPEND`, `CW1200_BH_SUSPENDED`, `CW1200_BH_RESUME`, and `CW1200_BH_RESUMED`.

State and persistence: State lives in `cw1200_common`: atomics for RX/TX/term/suspend, WSM sequence numbers, hardware buffer counts, sleep flags, and wait queues. It is reset on BH registration and destroyed on unregister. Fatal errors set `bh_error`.

Dependencies and integration: Depends on `hwio` for register/data I/O, `hwbus_ops` locking and IRQ enable, WSM handlers for RX/TX command framing, queue timestamp checks, firmware DPLL setup, and debug counters.

Risks: This file is concurrency-critical. Lost interrupts, stale `hw_bufs_used`, bad control lengths, or missed TX confirmations can terminate the BH and set a fatal error. RX length validation relies on firmware control fields and aligned bus reads. Power-save writes to the control register must not race active transfers.

Test signals: Exercise interrupt-driven RX/TX, TX bursts up to `wsm_caps.input_buffers`, scan wake holdoff, suspend/resume, missed-interrupt recovery, firmware exception handling, and timeout paths that warn about stuck TX confirms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/bh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/bh.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/bh.h

Purpose: Public interface for the CW1200 bottom-half worker and IRQ bridge.

Important APIs and types: Declares `cw1200_register_bh`, `cw1200_unregister_bh`, `cw1200_irq_handler`, `cw1200_bh_wakeup`, `cw1200_bh_suspend`, `cw1200_bh_resume`, `cw1200_enable_powersave`, and `wsm_release_tx_buffer`.

Control flow: Bus drivers call `cw1200_irq_handler` from SDIO/SPI IRQ context. TX and WSM code call `cw1200_bh_wakeup` and `wsm_release_tx_buffer`. PM paths call suspend/resume wrappers. `cw1200_enable_powersave` must run from the BH thread.

State and persistence: No state is defined here; all state is in `struct cw1200_common`.

Dependencies and integration: Included by bus, firmware, PM, main, and WSM-facing code to share BH lifecycle and wakeup APIs.

Risks: The header documents a key context rule for `cw1200_enable_powersave`; violating it can race device sleep state. IRQ enable/disable locking is handled elsewhere and must remain consistent with BH semantics.

Test signals: Link-time coverage of all prototypes and runtime validation through bus IRQ delivery, BH registration/unregistration, and PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/bh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200.h

Purpose: Main private state and driver-wide constants for the ST-Ericsson CW1200 mac80211 core.

Important APIs and types: Defines link limits, block-ack constants, join/auth timeouts, `struct cw1200_ht_info`, `enum cw1200_join_status`, `enum cw1200_link_status`, `struct cw1200_link_entry`, `struct cw1200_common`, and `struct cw1200_sta_priv`. Declares `cw1200_core_probe`, `cw1200_core_release`, and `cw1200_dpll_from_clk`; inline helpers classify HT, greenfield, and AMPDU density.

Control flow: This header is the shared contract between bus modules, common mac80211 glue, queues, WSM, scan, PM, and AP station handling. `cw1200_common` groups all state needed for lifecycle, hardware bus access, firmware metadata, queues, WSM command handling, scan, join/unjoin, key storage, AP power-save, event queues, CQM, rate policy, and work items.

State and persistence: All runtime state is memory-resident and tied to `ieee80211_hw` lifetime. It uses mutexes, spinlocks, wait queues, atomics, work items, delayed work, timers, firmware references, and queue objects. Firmware and SDD blobs are held by `const struct firmware *`.

Dependencies and integration: Includes queue, WSM, scan, txrx, and PM headers plus mac80211. Bus modules pass `hwbus_ops` and platform data into the exported core probe.

Risks: The structure is a large shared mutable object with many lock domains; bugs often come from wrong locking or stale join/link state. Constants hard-code AP station/link capacity. Feature support depends on firmware behavior and WSM fields.

Test signals: Compile all users after struct changes. Runtime coverage should include core probe/release, station join/unjoin, AP link allocation, scan, power management, TX queueing, firmware restart/error paths, and debugfs status reading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200_sdio.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200_sdio.c

Purpose: SDIO bus front-end for CW1200 hardware. It powers the module, subscribes SDIO or GPIO IRQs, implements `hwbus_ops`, and calls the shared CW1200 core.

Important APIs and functions: Exports `cw1200_sdio_set_platform_data`. Defines `struct hwbus_priv`, SDIO ID table, bus copy functions, SDIO claim/release locking, IRQ handlers, `cw1200_sdio_on/off`, `cw1200_sdio_align_size`, PM wake control, `cw1200_sdio_probe`, `cw1200_sdio_disconnect`, suspend/resume hooks, and module init/exit.

Control flow: Module init powers on platform resources and registers the SDIO driver. Probe accepts function 1, allocates `hwbus_priv`, enables the SDIO function, subscribes IRQs, then calls `cw1200_core_probe`. Disconnect reverses IRQ subscription, core release, function disable, and allocation. IRQs call `cw1200_irq_handler`, either from SDIO function IRQ or a platform GPIO IRQ.

State and persistence: Uses a global platform-data pointer and global optional GPIO descriptors, so the implementation supports only one device per system. Per-device `hwbus_priv` stores SDIO function, core pointer, and platform data.

Dependencies and integration: Depends on MMC/SDIO APIs, GPIO descriptors, platform data from `linux/platform_data/net-cw1200.h`, shared `hwbus_ops`, and PM callback `cw1200_can_suspend`.

Risks: The single-device global platform-data/GPIO design is a limitation. Probe ignores the return from `cw1200_sdio_irq_subscribe` before calling core probe, which can hide IRQ setup failure. Platform-specific reset polarity and timing are critical. Suspend only requests keep-power; resume is a no-op.

Test signals: SDIO enumeration, IRQ delivery via both SDIO and GPIO modes, firmware load through aligned SDIO transfers, suspend with `MMC_PM_KEEP_POWER`, module unload/reload, and board-specific power/reset sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200_sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200_spi.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200_spi.c

Purpose: SPI bus front-end for CW1200 hardware. It adapts CW1200 register accesses to SPI framing, manages GPIO power/reset, IRQ wake, and shared core registration.

Important APIs and functions: Defines `struct hwbus_priv`, `cw1200_spi_memcpy_fromio`, `cw1200_spi_memcpy_toio`, custom lock/unlock functions, threaded IRQ handler, IRQ subscribe/unsubscribe, `cw1200_spi_on/off`, alignment and PM callbacks, `cw1200_spi_probe`, `cw1200_spi_disconnect`, suspend hook, and the `spi_driver`.

Control flow: Probe clamps SPI speed to 1-52 MHz, sets bits-per-word from platform data or defaults to 16, requests GPIOs, powers hardware, calls `spi_setup`, subscribes IRQ, and invokes `cw1200_core_probe`. Register reads/writes build a 16-bit command header and run `spi_sync`. Disconnect unsubscribes IRQ, releases core, and powers off.

State and persistence: Per-SPI-device `hwbus_priv` tracks SPI device, core, platform data, GPIOs, a spinlock-protected claimed flag, and a wait queue used as a sleeping bus mutex.

Dependencies and integration: Depends on SPI, GPIO descriptors, threaded IRQs, platform data, and shared CW1200 core/hwbus APIs.

Risks: `cw1200_spi_memcpy_toio` temporarily byte-swaps the source buffer in place for 8-bit or big-endian transfers, which is risky if callers pass immutable or shared data. Probe does not check `plat_data` for NULL before dereferencing. The consumer name for `powerup` mistakenly uses `self->reset`. IRQ subscription status is overwritten by core probe status. Locking is custom and must not be used in hard IRQ context.

Test signals: SPI transfer tests with 8-bit and 16-bit modes, endian-sensitive register read/write validation, IRQ wake suspend path, missing platform-data failure behavior, and module unload/reload with GPIO state inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/debug.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/debug.c

Purpose: Debugfs implementation for CW1200 runtime state, firmware counters, and optional WSM frame dumps.

Important APIs and functions: Provides `cw1200_debug_init` and `cw1200_debug_release`. Debugfs files include `status`, `counters`, and writable `wsm_dumps`. Show helpers render join mode, interface mode, queue state, link maps, firmware identity, power-save state, WSM command state, and debug counters.

Control flow: `cw1200_debug_init` allocates `cw1200_debug_priv`, creates a `cw1200` directory under the wiphy debugfs directory, and creates files. Reading `status` snapshots driver fields and queue/link maps. Reading `counters` calls `wsm_get_counters_table`. Writing `wsm_dumps` toggles `priv->wsm_enable_wsm_dumps`.

State and persistence: Debug counters live in `struct cw1200_debug_priv` and reset on driver initialization. Debugfs files are removed recursively during release. `wsm_dumps` persists only for the current device instance.

Dependencies and integration: Depends on debugfs, seq_file, WSM MIB counter reads, queue structures, CW1200 join/link enums, and debug increment helpers in `debug.h`.

Risks: Status reads inspect many fields without uniform locking; output is diagnostic and may be slightly racy. `cw1200_debug_init` does not check each `debugfs_create_file` result. Counter reads require firmware command responsiveness.

Test signals: Mount debugfs and read all files during idle, scan, joined STA, AP mode, and teardown. Toggle `wsm_dumps` and verify BH TX/RX hex dumps appear only when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/debug.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/debug.h

Purpose: Debugfs state and lightweight counter helpers for the CW1200 driver.

Important APIs and types: `struct cw1200_debug_priv` stores a debugfs root dentry and counters for TX, aggregated TX/RX, multi-TX, cache misses, alignment fixes, TTL expirations, bursts, and block-ack stats. Declares `cw1200_debug_init` and `cw1200_debug_release`. Inline helpers increment counters from hot paths.

Control flow: Other modules call inline helpers at notable events, avoiding function-call overhead and centralizing counter names.

State and persistence: Counter state is per-device, in memory, and reset on driver reinitialization. No locking is used for increments, so values are diagnostic rather than strict accounting.

Dependencies and integration: Requires `struct cw1200_common` to hold `priv->debug`. Used by TX/RX, queue GC, BH burst paths, and debugfs rendering.

Risks: Inline helpers dereference `priv->debug`; they require debug initialization before use and no use after release. Unsynchronized increments can lose counts under concurrency.

Test signals: Build users with debugfs enabled/disabled configs and compare debugfs `status` counter movement during TX, RX, bursts, and queue TTL expiration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/fwio.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/fwio.c

Purpose: Firmware loading and hardware revision detection for CW1200/CW1x00 devices.

Important APIs and functions: Public entry point is `cw1200_load_firmware`. Internal helpers include `cw1200_get_hw_type`, `cw1200_load_firmware_cw1200`, `config_reg_read`, and `config_reg_write`.

Control flow: `cw1200_load_firmware` reads the config register, derives hardware type and major revision, writes and verifies DPLL based on reference clock, wakes the device, detects silicon cut by AHB ID reads, disables block ACK on old cuts, verifies access mode, loads firmware for supported HIF silicon, enables interrupt signaling, and switches from access mode to message/queue mode. `cw1200_load_firmware_cw1200` selects firmware and SDD file names by revision, initializes bootloader control registers, releases CPU reset/clock, requests the firmware blob, waits for bootloader readiness, writes firmware blocks into APB FIFO while polling `GET`, and waits for completion status.

State and persistence: Updates `priv->hw_type`, `priv->hw_revision`, `priv->sdd_path`, and block-ack masks. Firmware data is requested transiently for download and released after loading; SDD is loaded later by MAC setup.

Dependencies and integration: Uses `hwio` APB/AHB/register accessors, firmware loader API, DPLL helper from `main.c`, IRQ enable from BH/hwio, and firmware/SDD names from `fwio.h`.

Risks: Only `HIF_8601_SILICON` firmware load is implemented; CW1160/1260 is explicitly unsupported. Timeout and FIFO polling values are hardware-sensitive. Switching access/message mode and IRQ enable ordering are fragile. Some config read/write helpers ignore return values in default branches.

Test signals: Hardware boot with each supported cut, missing firmware files, malformed hardware config register, DPLL mismatch, bootloader timeout, FIFO backpressure, download error statuses, and startup indication after message mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/fwio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/fwio.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/fwio.h

Purpose: Firmware and SDD constants plus the firmware loading interface.

Important APIs and types: Defines firmware blob names (`wsm_10.bin`, `wsm_11.bin`, `wsm_20.bin`, `wsm_22.bin`, `wsm_cw1x60.bin`), SDD blob names, SDD TLV element IDs for PTA config and reference frequency, declares `cw1200_load_firmware`, and declares `cw1200_dpll_from_clk`.

Control flow: Used by firmware loading to select files by hardware revision and by MAC setup to parse SDD TLVs.

State and persistence: No direct state; file names correspond to firmware files persisted in the system firmware search path.

Dependencies and integration: Tied to `fwio.c`, `sta.c` SDD parsing, and platform/module overrides for `sdd_path`.

Risks: File names are ABI-like expectations for distributions and firmware packages. Missing or mismatched SDD files can break calibration/reference-clock behavior.

Test signals: Firmware package validation should include all named blobs needed by supported hardware; SDD parsing should confirm reference clock and PTA listen interval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/fwio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwbus.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwbus.h

Purpose: Defines the bus abstraction used by CW1200 common code to run over SDIO or SPI.

Important APIs and types: Forward-declares `struct hwbus_priv`, declares `cw1200_irq_handler` and `__cw1200_irq_enable`, and defines `struct hwbus_ops` with copy-from-I/O, copy-to-I/O, lock, unlock, align-size, and power-management callbacks.

Control flow: Bus modules instantiate `hwbus_ops` and pass them to `cw1200_core_probe`. Common `hwio`, BH, firmware, and PM code call through the ops without knowing the physical bus.

State and persistence: No direct state; bus-private state is opaque and owned by SDIO/SPI modules.

Dependencies and integration: Bridges core code to SDIO/SPI implementations. The comment on `__cw1200_irq_enable` requires callers to hold `hwbus_ops->lock`.

Risks: The ops contract is small but strict. Incorrect alignment, missing lock coverage, or IRQ enable without bus lock can corrupt transfers or race interrupts. PM callback semantics must match wake-capable IRQ setup for each bus.

Test signals: Run identical core tests over SDIO and SPI, including aligned/unaligned frame sizes, IRQ enable/disable paths, and suspend wake configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwio.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwio.c

Purpose: Low-level register, data queue, APB, and AHB accessors for CW1200 hardware through `hwbus_ops`.

Important APIs and functions: Public functions are `cw1200_reg_read`, `cw1200_reg_write`, `cw1200_data_read`, `cw1200_data_write`, `cw1200_indirect_read`, `cw1200_apb_write`, and `__cw1200_irq_enable`. Internal helpers implement raw register reads/writes with SDIO-style 17-bit address formation and endian conversion.

Control flow: Register accessors lock the bus, perform one raw transfer, and unlock. Data read/write uses the queue register with rotating RX/TX buffer IDs and retries up to three times. Indirect reads write the SRAM base address, set a prefetch bit, poll for prefetch completion, then read the data port. APB writes set the base address and write the SRAM data port. IRQ enable manipulates different config bits depending on hardware type.

State and persistence: Updates `priv->buf_id_rx` and `priv->buf_id_tx`; otherwise performs hardware register state changes. IRQ enable writes persist in device registers until changed.

Dependencies and integration: Depends on `hwbus_ops` implementations, register constants from `hwio.h`, `cw1200_common` hardware type, and callers in firmware loading and BH paths.

Risks: Buffer alignment is enforced for reads larger than four bytes. Retry loops use blocking delays. `cw1200_data_read/write` return the last `ret`, so retry exhaustion behavior must be monitored. Indirect access limits transfers to less than 0x1000 words. IRQ enable must be called with bus lock when using `__cw1200_irq_enable`.

Test signals: Register read/write loopback where possible, firmware APB writes, AHB cut-ID reads, data queue transfers with retry injection, buffer-ID rollover, and IRQ bit toggling on both supported hardware paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwio.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwio.h

Purpose: Hardware register map, firmware download control layout, and typed access helpers for CW1200 I/O.

Important APIs and types: Defines cut-ID constants, download SRAM offsets, `struct download_cntl_t`, bootloader status/error constants, APB address macro, register IDs, control/config bits, and declarations for data/register/APB/AHB accessors. Inline helpers provide 16-bit and 32-bit register/APB/AHB reads/writes.

Control flow: Firmware loading and BH code use these constants to wake the device, configure DPLL, download firmware, switch access modes, and move WSM frames through the queue register.

State and persistence: No host state, but constants represent persistent device register layout and bootloader shared-memory protocol.

Dependencies and integration: Used by `hwio.c`, `fwio.c`, `bh.c`, and bus modules. Register helper inlines convert little-endian device data to CPU-endian values.

Risks: Register constants and bit definitions must match silicon. `cw1200_reg_read_16` masks with `0xfffff`, wider than 16 bits, which is suspicious but usually harmless when assigned to `u16`. Download control comments contain typos but describe critical bootloader protocol.

Test signals: Firmware download, config/control register inspection, indirect APB/AHB reads, queue-mode data movement, and hardware revision detection are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/main.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/main.c

Purpose: Shared mac80211 core initialization, registration, supported bands/rates, module parameters, DPLL mapping, and exported probe/release functions for CW1200 bus modules.

Important APIs and functions: Defines module parameters `macaddr`, `cw1200_sdd_path`, `cw1200_refclk`, `cw1200_power_mode`, and block-ack TID masks. Provides `cw1200_init_common`, `cw1200_register_common`, `cw1200_unregister_common`, `cw1200_dpll_from_clk`, `cw1200_core_probe`, and `cw1200_core_release`. `cw1200_ops` binds mac80211 callbacks to STA, scan, TX/RX, PM, and AP functions.

Control flow: Bus probe calls `cw1200_core_probe`, which allocates and initializes `ieee80211_hw`, stores bus/platform values, registers BH, loads firmware, waits for WSM startup, configures operational mode and multi-TX confirm, then registers with mac80211. Release disables IRQs, unregisters mac80211/BH/debugfs/queues/PM, and frees the hardware object.

State and persistence: Initializes `cw1200_common` fields, workqueues, delayed works, spinlocks, wait queues, WSM buffers, queue stats, TX queues, bands, permanent MAC address, and firmware/SDD overrides. Runtime state is not persistent beyond module/device lifetime.

Dependencies and integration: Integrates mac80211, cfg80211, firmware loading, WSM, queues, scan, STA/AP code, PM, debugfs, and bus modules through exported GPL symbols.

Risks: Error unwinding must keep BH/core lifetimes correct. Randomizing the lower MAC bytes when template bytes are zero is convenient but may surprise users. Static band tables are mutated before registration, so shared state must be treated carefully across re-registration. `cw1200_core_probe` sets `*core` before all initialization finishes and resets it on failure.

Test signals: Build and probe over each bus, mac80211 registration, firmware startup indication within 3 seconds, supported band exposure with/without 5 GHz, module parameter overrides, and clean unload after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/pm.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/pm.c

Purpose: mac80211 WoWLAN and runtime suspend/resume support for CW1200.

Important APIs and functions: Public functions are `cw1200_pm_init`, `cw1200_pm_deinit`, `cw1200_pm_stay_awake`, `cw1200_can_suspend`, `cw1200_wow_suspend`, and `cw1200_wow_resume`. Internal helpers preserve delayed-work timers and filter settings during suspend.

Control flow: Suspend rejects if the stay-awake timer is pending, TX queues are non-empty, config mutex cannot be acquired, channel switch/join/scan is active, or BH buffers do not drain quickly. It locks TX, installs UDP and ethertype filters, optionally switches station mode to legacy PS, snapshots delayed work, enables beacon skipping, suspends BH, stores suspend state, and enables bus IRQ wake. Resume disables IRQ wake, releases scan lock, resumes BH, restores PS/beacon wake settings, queues delayed work with saved timeouts, removes filters, unlocks TX/config, and frees suspend state.

State and persistence: `cw1200_pm_state` stores a stay-awake timer, spinlock, and suspend-state pointer. Suspend-state captures delayed-work remaining times, previous PS mode, and beacon-skipping state.

Dependencies and integration: Depends on WSM filter/PM/beacon MIBs, BH suspend/resume, scan/unjoin/link work, `hwbus_ops->power_mgmt`, and mac80211 WoWLAN callbacks registered in `main.c`.

Risks: Several suspend steps call WSM commands after locking and must unwind in correct order. `cw1200_wow_resume` assumes `suspend_state` is non-NULL. Race handling with incoming IRQs returns `-EAGAIN`. PM behavior is limited to any/disconnect WoWLAN.

Test signals: Suspend rejection during TX, scan, join, channel switch, and stay-awake timer. Successful suspend/resume while associated, IRQ wake event resume, beacon skipping restoration, filter restoration, and no leaked TX/config locks after failed suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/pm.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/pm.h

Purpose: Power-management interface and state structure for CW1200.

Important APIs and types: Defines `struct cw1200_pm_state` with suspend-state pointer, stay-awake timer, optional platform device pointer, and lock. Declares PM init/deinit, WoW suspend/resume, suspend eligibility, and stay-awake helpers when `CONFIG_PM` is enabled; provides no-op/negative inline fallbacks otherwise.

Control flow: Main registration initializes PM state, mac80211 callbacks call WoW functions, and queue/scan/BH code uses `cw1200_pm_stay_awake` to defer sleep.

State and persistence: In-memory per-device PM state only.

Dependencies and integration: Included by `cw1200.h`, `main.c`, queue, scan, BH, and STA code. Conditional compilation tracks `CONFIG_PM`.

Risks: Non-PM builds make `cw1200_can_suspend` return 0, so bus suspend code must be compiled consistently. The `pm_dev` field is present but not used in this subset.

Test signals: Compile with and without `CONFIG_PM`; verify callers link and PM callbacks are only registered when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/queue.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/queue.c

Purpose: Implements bounded O(1)-style TX queues with packet IDs, per-link accounting, pending/queued separation, queue locking, and TTL garbage collection.

Important APIs and functions: Provides queue stats init/deinit, queue init/deinit/clear, `cw1200_queue_put`, `cw1200_queue_get`, `cw1200_queue_requeue`, `cw1200_queue_remove`, `cw1200_queue_get_skb`, lock/unlock wrappers, timestamp lookup, and stats empty checks. Private `cw1200_queue_item` stores skb, packet ID, timestamps, txpriv, and generation.

Control flow: `put` takes a free item, assigns a packet ID from queue generation, queue ID, item generation, and pool index, updates per-link stats, and may stop the mac80211 queue if near capacity. `get` selects the first queued item matching a link map, moves it to pending, stamps transmit time, and exposes WSM TX data. `remove` completes a pending item and calls the skb destructor. `requeue` moves a pending item back to queued with incremented item generation. GC expires stale queued frames based on TTL and wakes waiters when link maps empty.

State and persistence: Queue state is memory-resident: item pool, free/queued/pending lists, generation counters, counts, link-map caches, timer, and spinlocks. Stats aggregate queued counts across queues.

Dependencies and integration: Used by TX/RX WSM code, BH timeout detection, AP power-save link maps, flush logic, and mac80211 queue stop/wake APIs. Calls debug and PM stay-awake helpers.

Risks: Packet ID parsing indexes `queue->pool[item_id]` before checking `item_id >= capacity`, so invalid IDs could form out-of-bounds pointers before validation. Correct stats depend on every get/remove/requeue path being balanced. Unsafely clearing queues while TX confirms arrive can expose stale generation handling.

Test signals: Queue capacity/overfull behavior, TTL expiration, link-id-specific draining, requeue after firmware retry, stale packet ID rejection, flush waiters, and mac80211 stop/wake transitions under parallel TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/queue.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/queue.h

Purpose: Public queue structures and function prototypes for CW1200 TX queue management.

Important APIs and types: Defines `cw1200_queue_skb_dtor_t`, `struct cw1200_queue`, `struct cw1200_queue_stats`, and `struct cw1200_txpriv`. Declares queue lifecycle, put/get/requeue/remove, skb lookup, lock/unlock, timestamp, and stats-empty functions. Inline helpers extract queue ID and generation from packet IDs.

Control flow: TX code constructs `cw1200_txpriv`, enqueues skbs, WSM selects frames, and confirmations use packet IDs to remove or requeue items.

State and persistence: Structures hold in-memory queue lists, pools, link maps, counters, timers, and locks for the lifetime of the device.

Dependencies and integration: Shared by main initialization, TX/RX, BH, STA/AP power-save, and debugfs status output.

Risks: Consumers must respect the packet-ID encoding and queue locking rules. `cw1200_txpriv` fields such as link ID, TID, and offset are used by multiple paths, so incorrect population can break AP power-save or direct probe work.

Test signals: Compile all queue users after API changes; runtime TX, requeue, flush, AP station sleep/wake, and direct probe paths validate semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/scan.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/scan.c

Purpose: Implements mac80211 hardware scan and direct-probe workarounds for CW1200 firmware.

Important APIs and functions: Provides `cw1200_hw_scan`, `cw1200_scan_work`, `cw1200_scan_timeout`, `cw1200_clear_recent_scan_work`, `cw1200_scan_complete_cb`, `cw1200_scan_failed_cb`, and `cw1200_probe_work`. Internal helpers include `cw1200_scan_start`, `cw1200_scan_restart_delayed`, and `cw1200_scan_complete`.

Control flow: `cw1200_hw_scan` builds a probe request template, takes `scan.lock`, sets scan request state, locks TX, and queues scan work. `cw1200_scan_work` chunks channels by band/flags/power, may force background scanning while joined, adjusts output power, starts firmware scans, and completes by restoring PM/listening/filter state and notifying mac80211. Timeout and firmware callbacks race through the delayed timeout work to serialize completion. `cw1200_probe_work` converts a pending raw probe request into a one-channel scan, edits SSID handling, removes the original TX queue entry, and fakes ACK on success.

State and persistence: `struct cw1200_scan` tracks request pointers, channel iterators, SSIDs, output power, status, atomic progress, direct-probe flag, and work items. `recent_scan` keeps the device awake briefly after scans.

Dependencies and integration: Depends on WSM scan/template/probe-responder commands, STA listening/filtering/unjoin logic, PM stay-awake, queues, and mac80211 scan completion APIs.

Risks: Scan state is protected by both a semaphore and `conf_mutex`; wrong ordering can deadlock. AP mode scans are rejected because firmware MiniAP mode can be corrupted. Direct probe mutates skb contents temporarily and must restore offsets. Delayed unjoin/link-loss handling depends on scan completion paths.

Test signals: Active/passive scans, joined background scans, AP scan rejection, scan timeout, firmware failure callback, P2P listening restart, delayed unjoin during scan, and direct probe request conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/scan.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/scan.h

Purpose: Scan state and scan-related API declarations for CW1200.

Important APIs and types: Defines `struct cw1200_scan` with semaphore, work items, cfg80211 request pointer, channel iterator pointers, WSM SSIDs, output power, status, in-progress atomic, direct-probe work, and direct-probe flag. Declares scan entry points and WSM callbacks.

Control flow: Main initialization sets up the work items and semaphore. Mac80211 calls `cw1200_hw_scan`; WSM callbacks call completion/failure functions; TX workaround code schedules `cw1200_probe_work`.

State and persistence: Scan state is per-device and reset across scan operations, not persisted.

Dependencies and integration: Includes `wsm.h` and Linux semaphore support; referenced from `cw1200_common`, `main.c`, `scan.c`, PM, and STA code.

Risks: The structure stores pointers into mac80211 scan requests, so lifetime is tied to scan completion. `scan.lock` is a semaphore rather than a mutex because some flows use trylock and cross-work ownership.

Test signals: Build all callers, then validate scan request lifetime, timeout cleanup, and direct probe interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/sta.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/sta.c

Purpose: Main mac80211 STA/AP control implementation for CW1200. It handles device start/stop, interface add/remove/change, configuration, filtering, keys, flush, CQM events, SDD parsing, join/unjoin, P2P listening, AP station power-save, beacon/TIM updates, and AP start.

Important APIs and functions: mac80211 callbacks include `cw1200_start`, `cw1200_stop`, `cw1200_add_interface`, `cw1200_remove_interface`, `cw1200_change_interface`, `cw1200_config`, `cw1200_configure_filter`, `cw1200_conf_tx`, `cw1200_get_stats`, `cw1200_set_key`, `cw1200_set_rts_threshold`, `cw1200_flush`, `cw1200_bss_info_changed`, `cw1200_sta_add`, `cw1200_sta_remove`, `cw1200_sta_notify`, `cw1200_set_tim`, and `cw1200_ampdu_action`. WSM/event callbacks include join complete, event handler, BSS loss work, suspend/resume indication, and CQM handling. Internal helpers parse SDD, set up MAC, join/unjoin, update listening/filtering, upload templates, and start AP mode.

Control flow: Start initializes default EDCA/UAPSD, MAC address, monitor baseline, CQM defaults, and firmware MAC config. Interface add moves from monitor to STA/IBSS/mesh/AP and calls setup. Config changes handle power, channel switch with flush/TX lock, PS mode, idle operational mode, and retry limits. BSS changes drive join state, association parameters, HT protection, ERP/slot time, ARP filters, beacon upload, AP start, and CQM thresholds. Join takes a TX lock, resolves BSS/SSID, configures block ACK and protected management policy, issues WSM join, waits for completion/timeout, uploads keys, and adjusts filtering. Unjoin resets firmware, clears events, disables block ACK, and restores passive/listening state. AP paths allocate link IDs, track sleeping STAs, update TIM and multicast delivery, and map firmware suspend/resume indications to mac80211 station notifications.

State and persistence: Mutates most of `cw1200_common`: mode, VIF, MAC, join status, keys, filters, association/BSS params, HT info, PM settings, CQM state, event queue, link ID database, asleep/PSPOLL masks, multicast/TIM state, beacon interval, delayed work, and SDD firmware reference. State is runtime-only except firmware/SDD files.

Dependencies and integration: Integrates mac80211/cfg80211 callbacks, WSM commands/MIBs, TX/RX queues, BH wakeups, scan locks, PM timers, debug counters, firmware SDD parsing, and AP station private data.

Risks: This file has dense locking across `conf_mutex`, `scan.lock`, TX lock, spinlocks, workqueues, and timers. Join/unjoin during scan is deferred and easy to regress. Key install assumes valid key lengths for some ciphers but not all peer-address presence cases. AP multicast/TIM state relies on firmware DTIM indications. `cw1200_ampdu_action` rejects mac80211 aggregation because firmware owns negotiation.

Test signals: STA connect/disconnect, failed join timeout, scan during pre-association, PS mode changes, channel switch, key install/remove for WEP/TKIP/CCMP/WAPI, CQM RSSI/BSS-loss events, P2P listen mode, AP start/stop, station sleep/awake, multicast buffering, beacon/TIM updates, and stop/remove cleanup under active work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/sta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/sta.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/sta.h

Purpose: Public prototypes for CW1200 mac80211 STA/AP operations, WSM callbacks, event handling, and internal STA helpers.

Important APIs and types: Declares mac80211 callback implementations for start/stop, interface management, config, filters, EDCA, stats, keying, RTS threshold, flush, multicast preparation, PM setting, TIM, STA add/remove/notify, BSS info changes, AMPDU action, and suspend/resume indications. Defines inline `cw1200_cqm_bssloss_sm` wrapper that serializes `__cw1200_cqm_bssloss_sm` with `bss_loss_lock`.

Control flow: `main.c` binds these declarations into `cw1200_ops`; WSM and workqueue code call the callback declarations to route firmware events into driver state transitions.

State and persistence: No state is defined here, but APIs operate heavily on `struct cw1200_common`.

Dependencies and integration: Shared by main, scan, PM, TX/RX, WSM, and STA implementation code.

Risks: The header exposes many internal work functions, so call context and locking expectations are implicit. The CQM inline wrapper assumes `priv->bss_loss_lock` is initialized.

Test signals: Compile-time consistency with `sta.c` and `main.c`; runtime coverage through mac80211 callback exercise and WSM event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/sta.h -->
