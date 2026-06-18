# subset-b-006548 Research

Grouped research for `subset-b-006548`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4.c

Purpose: Implements the SOF IPC4 core transport glue: message logging, TX serialization, reply status conversion, large config set/get chunking, firmware-ready processing, notification dispatch, IPC4 PM callbacks, and the exported `ipc4_ops` table used by the SOF core.

Important APIs and state: `ipc4_ops` wires `.init`, `.exit`, `.post_fw_boot`, `.tx_msg`, `.rx_msg`, `.set_get_data`, `.get_reply`, `.pm`, `.fw_loader`, `.tplg`, `.pcm`, and tracing callbacks. `sof_ipc4_check_reply_status()` maps firmware status codes to Linux errno. `sof_ipc4_tx_msg()` forces D0 unless `no_pm`, takes `ipc->tx_mutex`, sends with `sof_ipc_send_msg()`, and waits through `ipc4_wait_tx_done()`. `sof_ipc4_set_get_data()` handles IPC4 module large config transfers across `SOF_IPC4_MSG_MAX_SIZE` chunks. Persistent IPC4 private state includes `pipeline_state_mutex`, `fw_lib_xa`, `libraries_restored`, mailbox/debug/info box offsets, max payload size, and the reusable reply buffer.

Control flow: init reads platform mailbox/window offsets, sizes the DSP/host/debug/FW info boxes, and initializes library xarray state. TX validates sizes, optionally resumes the DSP, serializes, writes payloads, waits for completion, copies reply header/payload, and resets dump flags. Large config GET may preserve a TX payload for control params, then accumulates returned blocks while checking firmware-reported total size. RX accepts IPC4 notifications only, handles FW_READY boot state transitions, log-buffer position updates, exceptions via `snd_sof_dsp_panic()`, resource/module notifications, and ALSA kcontrol updates. Post boot completes split-release and queries configuration on first boot, otherwise reloads libraries.

Dependencies and integration: Depends on `ipc4-priv.h`, topology, telemetry, IPC4 firmware-register definitions, SOF ops, firmware libraries, mailbox IO, debugfs exception nodes, and IPC4 loader/topology/PCM/tracing ops. Platform drivers must provide mailbox/window offsets and mailbox data callbacks. The mic privacy notifier sends a basefw large-config SET only after `SOF_FW_BOOT_COMPLETE`.

Risks: Reply status translation collapses many firmware errors to `-EINVAL`, which can hide precise failure classes. Large-config chunking is sensitive to payload size, FIRST/LAST block flags, firmware total size reporting, and preserved TX payload lifetime. FW_READY behavior differs on first versus later boots, so library restore and context-save paths can regress across suspend/resume. Notification payload reallocation must handle malformed `event_data_size`.

Test signals: Exercise IPC timeout, reply error, unknown status, large SET/GET across one and multiple chunks, controls that need TX payload for GET, FW_READY success/failure, module notification with extra payload, exception notification, log position update, library reload after resume, and mic privacy notification while booted and unbooted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/loader.c

Purpose: Provides generic SOF firmware loading and run sequencing shared by platform drivers. It requests the base firmware, handles extended-manifest offseting, validates and copies firmware to DSP memory, starts the DSP, waits for firmware-ready, and releases the base firmware.

Important APIs and state: `snd_sof_load_firmware_raw()` populates `sdev->basefw.fw` and `basefw.payload_offset`. `snd_sof_load_firmware_memcpy()` validates through IPC-specific loader ops, resets the DSP, and calls `load_fw_to_dsp`. `snd_sof_run_firmware()` initializes `boot_wait`, creates first-boot debugfs firmware version storage, runs platform pre/run/post callbacks, waits on `sdev->fw_state`, and marks `SOF_FW_BOOT_COMPLETE`. `snd_sof_fw_unload()` releases `basefw.fw`.

Control flow: raw load builds `fw_path/fw_filename`, calls `request_firmware()`, then lets `fw_loader->parse_ext_manifest()` decide whether to skip an extended manifest. memcpy load calls raw load, validates the SOF firmware header, resets the DSP, and invokes the IPC loader's load path. run firmware resets dump flags, calls `snd_sof_dsp_pre_fw_run()`, starts the DSP with `snd_sof_dsp_run()`, waits up to `boot_timeout` for state to move past `SOF_FW_BOOT_IN_PROGRESS`, handles ready failure or timeout dumps, performs post-run, then IPC post-boot.

Dependencies and integration: Uses `sdev->ipc->ops->fw_loader` for manifest parsing, validation, and DSP load; `ops.h` for DSP reset/run/pre/post wrappers; SOF debugfs and firmware state helpers; platform probe paths choose this loader via `.load_firmware`.

Risks: The firmware pointer is cached, so callers must release on validation/load errors to avoid stale state. Boot wait depends on asynchronous IPC RX updating `fw_state`; missing mailbox IRQs surface as generic `-EIO`. Manifest offset errors corrupt firmware load addresses. Debugfs creation is fatal on allocation failure during first boot.

Test signals: Missing firmware, invalid extended manifest, invalid SOF header, DSP reset failure, loader failure cleanup, boot timeout, FW_READY failure, post-fw-run failure, IPC post-boot failure, and successful unload/reload across suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/Kconfig

Purpose: Defines build-time enablement for SOF on MediaTek audio DSP platforms.

Important symbols: `SND_SOC_SOF_MTK_TOPLEVEL` is the user-visible ARM64/compile-test gate and depends on `SND_SOC_SOF_OF`. `SND_SOC_SOF_MTK_COMMON` is a non-user-selectable tristate selected by SoC drivers; it selects SOF OF device support, core SOF, IPC3, Xtensa support, and compressed audio. `SND_SOC_SOF_MT8186` and `SND_SOC_SOF_MT8195` are user-visible tristates for MT8186 and MT8195 and both depend on `MTK_ADSP_IPC`.

Control flow and integration: Enabling a SoC option selects the shared common object and pulls the appropriate subdirectory from the Makefiles. Both SoC drivers are IPC3-only in their descriptors, so selecting IPC3 here matches runtime capability.

State and persistence: No runtime state; this is build configuration that controls which modules are compiled and which dependencies are forced into the kernel/module build.

Risks: Missing `MTK_ADSP_IPC` prevents SoC options even if device tree matches. Common selects `SND_SOC_SOF_COMPRESS`, which may expand build surface. Adding IPC4 MediaTek support would require revisiting the forced IPC3 select and SoC descriptors.

Test signals: Kconfig allmodconfig/allyesconfig coverage, ARM64 and COMPILE_TEST builds, dependency visibility when `MTK_ADSP_IPC=n`, and module link checks for common plus each SoC object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/Makefile

Purpose: Connects MediaTek SOF Kconfig symbols to object directories.

Important build rules: `CONFIG_SND_SOC_SOF_MTK_COMMON` builds `mtk-adsp-common.o`; `CONFIG_SND_SOC_SOF_MT8195` descends into `mt8195/`; `CONFIG_SND_SOC_SOF_MT8186` descends into `mt8186/`.

Control flow and integration: The common object exports helpers consumed by both SoC subdrivers. Subdirectory Makefiles build SoC-specific platform, clock, and loader units into their module objects.

State and persistence: No runtime state. Build output shape determines module composition and namespace import requirements in the SoC drivers.

Risks: A SoC object depends on common exports, so disabling or misselecting `SND_SOC_SOF_MTK_COMMON` causes unresolved symbols. Directory order is simple but new SoCs must add both Kconfig and Makefile entries.

Test signals: Module build with common only, MT8186 only, MT8195 only, and both SoCs; `modpost` namespace/import checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/adsp_helper.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/adsp_helper.h

Purpose: Defines shared MediaTek ADSP private data carried by SOF platform drivers and common IPC helpers.

Important types: `struct mtk_adsp_chip_info` stores physical/virtual SRAM, DRAM, config, secure, and bus register mappings, sizes, boot address, and AP/DSP DRAM offset. `struct adsp_priv` stores the owning device, `snd_sof_dev`, MediaTek IPC handle, child IPC platform device, chip info, clock array, optional address conversion callbacks, and private extension data.

Control flow and integration: MT8186 and MT8195 probes allocate `adsp_priv`, attach it to `sdev->pdata->hw_pdata`, fill `mtk_adsp_chip_info` from device-tree resources/reserved memory, register `mtk-adsp-ipc`, and set IPC callback data through this structure. Clock helpers store `struct clk **clk` here.

State and persistence: Lifetime is devm-managed by the platform device except for the child IPC platform device, which remove paths unregister explicitly. The register and memory mappings persist for the SOF device lifetime.

Risks: Both SoC drivers assume `hw_pdata` points to a valid `adsp_priv` before clock/common helpers run. Address conversion callbacks are declared but not populated by these files, so future users must check null. Resource fields differ by SoC; common code must not assume secure/bus registers always exist.

Test signals: Probe allocation failures, absent resources, child IPC registration/defer, clock helper access before initialization, and remove path with partially initialized private data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/adsp_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/Makefile

Purpose: Builds the MT8186/MT8188 SOF platform module.

Important build rules: `snd-sof-mt8186-y` is composed of `mt8186.o`, `mt8186-clk.o`, and `mt8186-loader.o`; `CONFIG_SND_SOC_SOF_MT8186` builds `snd-sof-mt8186.o`.

Control flow and integration: The object split mirrors platform responsibilities: probe/ops/device table in `mt8186.c`, clock acquisition and gating in `mt8186-clk.c`, and HIFIxDSP boot/reset sequencing in `mt8186-loader.c`.

State and persistence: No runtime state in the Makefile; module composition determines which symbols are linked internally.

Risks: Missing any object breaks the `snd_sof_dsp_ops` callbacks or boot sequence. MT8188 support is compiled into the same module, so changes for one SoC can affect the other.

Test signals: Build `CONFIG_SND_SOC_SOF_MT8186=m/y`, verify module exports/import namespaces, and probe both `mediatek,mt8186-dsp` and `mediatek,mt8188-dsp` compatible tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-clk.c

Purpose: Handles MT8186 ADSP clock lookup and on/off sequencing.

Important APIs: `mt8186_adsp_init_clock()` allocates `priv->clk` and resolves `"audiodsp"` and `"adsp_bus"`. `mt8186_adsp_clock_on()` enables both clocks, then writes `ADSP_CK_EN` and `ADSP_UART_CTRL` bits for UART, DMA, timer, core debug, core clock, UART bus clock gate, and UART reset. `mt8186_adsp_clock_off()` clears those registers and disables clocks in reverse order.

Control flow: Enable first prepares `audiodsp`, then `adsp_bus`, rolling back `audiodsp` if the second enable fails. Clock-on performs register writes only after both clocks are active. Clock-off clears hardware enable bits before disabling the Linux clock handles.

Dependencies and integration: Uses `adsp_priv` from `sdev->pdata->hw_pdata`, common SOF register IO, and MT8186 register definitions. Called from MT8186 probe, suspend, resume, remove, and error paths.

State and persistence: Clock handles are devm-managed; enable state is runtime state balanced manually by probe/resume versus suspend/remove/error unwind.

Risks: Unbalanced clock off on partially enabled paths would call disable on disabled clocks; current helper rollback covers the second-enable failure. Register writes require mapped DSP_REG_BAR and clocks already active. Device tree clock names must match exactly.

Test signals: Missing clock names, failure enabling each clock, probe error unwind after clock on, suspend/resume cycles, and register traces showing enable bits cleared on removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-clk.h

Purpose: Declares MT8186 clock identifiers and clock helper prototypes.

Important APIs/types: `enum adsp_clk_id` defines `CLK_TOP_AUDIODSP`, `CLK_TOP_ADSP_BUS`, and `ADSP_CLK_MAX`. Prototypes expose `mt8186_adsp_init_clock()`, `mt8186_adsp_clock_on()`, and `mt8186_adsp_clock_off()`.

Control flow and integration: The enum indexes the `priv->clk` array allocated by `mt8186-clk.c`. `mt8186.c` calls these helpers during probe, suspend, resume, remove, and error unwinding.

State and persistence: No state in the header, but enum order is an ABI internal to this driver and must match the `adsp_clks[]` name table.

Risks: Adding clocks requires updating the enum and name table together. Callers assume init ran before on/off.

Test signals: Compile coverage for all callers and runtime probe with both required clocks present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-loader.c

Purpose: Implements MT8186/MT8188 HIFIxDSP boot and shutdown register sequencing.

Important APIs: `mt8186_sof_hifixdsp_boot_sequence()` stalls the core, enables mailbox 0/1 IRQs, writes alternate vector address/select bits, asserts reset, delays, releases reset, and clears RUNSTALL. `mt8186_sof_hifixdsp_shutdown()` stalls the core and asserts reset.

Control flow and integration: `mt8186_run()` in `mt8186.c` calls boot with `SRAM_PHYS_BASE_FROM_DSP_VIEW` after firmware has been loaded to SRAM. Suspend/remove paths call shutdown before SRAM/clock power down.

State and persistence: Hardware reset, RUNSTALL, mailbox IRQ enable, and boot vector registers persist until changed or power-gated.

Risks: Sequencing is timing-sensitive; changing reset polarity or delay can prevent FW_READY. Mailbox IRQ enable is limited to channels 0 and 1. The header deliberately sets both MT8186 and MT8188 ALTVECSEL bits to simplify shared support, which depends on documented ignored bits.

Test signals: Boot-to-FW_READY, shutdown during suspend/remove, mailbox interrupt delivery after boot, and MT8186/MT8188 coverage for alternate vector selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186.c

Purpose: Provides the SOF OF platform driver and DSP ops for MT8186 and MT8188 MediaTek audio DSPs.

Important APIs/state: `platform_parse_resource()` initializes reserved DRAM, cfg/sram/sec/bus resources, and validates 4 KiB DRAM alignment plus shared-buffer tail size. `mt8186_dsp_probe()` allocates `adsp_priv`, maps SRAM/DRAM and register BARs, sets `mmio_bar`/`mailbox_bar`, initializes DRAM remap, clocks, SRAM power, and child `mtk-adsp-ipc`. `sof_mt8186_ops` supplies SOF core callbacks for run, IO, mailbox, IPC, stream ops, firmware load, Xtensa dumps, DAI drivers, debugfs, PM, and PCM capabilities. MT8188 clones MT8186 ops but swaps DAI drivers and descriptors in `sof_mt8188_ops_init()`.

Control flow: Probe parses resources, ioremaps IRAM and DRAM into SOF BARs, maps config/secure/bus registers to driver BAR slots, writes DRAM remap registers, enables clocks and SRAM, registers the IPC child, then connects MediaTek IPC callbacks. Run boots from DSP-view SRAM. Suspend shuts down the DSP, powers SRAM off, and disables clocks; resume reverses clock/SRAM power. Remove unregisters IPC and powers down. Shutdown delegates to generic SOF suspend.

Dependencies and integration: Uses SOF OF probe/remove/shutdown, common MediaTek IPC helpers, MTK ADSP IPC firmware driver, SOF IPC3, Xtensa arch ops, generic SOF stream helpers, and device-tree reserved memory/resources. OF compatibles are `mediatek,mt8186-dsp` and `mediatek,mt8188-dsp`.

Risks: Resource ordering and reserved-memory index are hard requirements. DRAM remap writes are verified but offset arithmetic uses SoC constants. Error unwind must balance SRAM and clocks after IPC child failures. MT8188 shares most MT8186 hardware sequencing, so SoC-specific differences beyond DAI/topology/firmware name may be missed.

Test signals: Probe with missing/misaligned/undersized memory, absent cfg/sram/sec/bus resources, remap verification failure, clock and IPC defer failures, FW boot on both compatibles, PCM open/hw_params/pointer/close, suspend/resume/remove, and debug dump after panic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186.h

Purpose: Centralizes MT8186/MT8188 DSP BAR identifiers, register offsets, bit definitions, memory-map constants, and boot/shutdown prototypes.

Important definitions: BAR slots cover DSP config, secure, and bus registers. Register macros include reset, RUNSTALL, mailbox IRQ enable, debug/fault registers, clock/UART control, alternate vector registers, SRAM pool powerdown, DRAM remap, mailbox offset/size, DRAM size, DSP-view SRAM/DRAM bases, remap mask/shift, and shared DRAM tail sizes.

Control flow and integration: `mt8186.c`, `mt8186-clk.c`, and `mt8186-loader.c` use these constants for resource mapping, remap verification, clock gating, boot vector selection, reset, panic dump, and mailbox offsets.

State and persistence: Defines hardware register state manipulated by runtime code; no software state.

Risks: Constants must match SoC manuals and firmware memory layout. `DSP_DRAM_SIZE` comment disagrees with `0xA00000`, so code should rely on reserved-memory resource size rather than that macro. Setting both ALTVECSEL bits is intentional for MT8186/MT8188 but depends on ignored-bit behavior.

Test signals: Register access smoke tests, FW memory layout validation, mailbox offset compatibility with firmware `memory.h`, and boot on both MT8186 and MT8188.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/Makefile

Purpose: Builds the MT8195 SOF platform module.

Important build rules: `snd-sof-mt8195-y` combines `mt8195.o`, `mt8195-clk.o`, and `mt8195-loader.o`; `CONFIG_SND_SOC_SOF_MT8195` builds `snd-sof-mt8195.o`.

Control flow and integration: The object split separates platform driver/DSP ops, clock tree control, and HIFIxDSP boot/reset sequencing.

State and persistence: No runtime state; it defines link composition for the module.

Risks: Dropping any object breaks callbacks referenced from `mt8195.c`. The module depends on common MediaTek SOF helpers from the parent Makefile.

Test signals: Build as module and built-in, verify namespace imports and no unresolved `adsp_clock_*` or boot-sequence symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-clk.c

Purpose: Resolves and controls the MT8195 ADSP clock tree.

Important APIs: `mt8195_adsp_init_clock()` resolves six clocks: `adsp_sel`, `clk26m_ck`, `audio_local_bus`, `mainpll_d7_d2`, `scp_adsp_audiodsp`, and `audio_h`. `adsp_clock_on()` calls `adsp_default_clk_init(true)`, which sets parents for DSP select, audio local bus, and audio_h, then enables the required clocks. `adsp_clock_off()` disables the same clock stack via `adsp_default_clk_init(false)`.

Control flow: Enable changes parents before preparing clocks, then enables mainpll, adsp, audio local bus, scp adsp, and audio_h with rollback labels for each failure. Disable unwinds in reverse order.

Dependencies and integration: Uses `adsp_priv->clk` and MT8195 constants. Called from MT8195 probe, suspend, resume, remove, and probe error unwinding. It includes `linux/string_choices.h` for on/off debug text.

State and persistence: Clock handles are devm-managed; parent selection and enable state persist across runtime until explicit off or clock framework reset.

Risks: Parent setting failures before enable must leave prior parents as-is. Clock names and topology must match device tree/clock provider. Off path calls the same helper with `enable=false`, so future parent-reset expectations would need extra code.

Test signals: Missing clocks, parent-set failure, enable failure at each stage with rollback, suspend/resume cycles, and audio stability after repeated clock parent changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-clk.h

Purpose: Declares MT8195 ADSP clock IDs and clock helper prototypes.

Important APIs/types: `enum adsp_clk_id` indexes `CLK_TOP_ADSP`, `CLK_TOP_CLK26M`, `CLK_TOP_AUDIO_LOCAL_BUS`, `CLK_TOP_MAINPLL_D7_D2`, `CLK_SCP_ADSP_AUDIODSP`, `CLK_TOP_AUDIO_H`, and `ADSP_CLK_MAX`. Prototypes expose `mt8195_adsp_init_clock()`, `adsp_clock_on()`, and `adsp_clock_off()`.

Control flow and integration: Enum order must match `adsp_clks[]` in `mt8195-clk.c`; `mt8195.c` uses the prototypes for probe and PM.

State and persistence: Header-only definitions; runtime state lives in `adsp_priv->clk` and the clock framework.

Risks: Generic helper names `adsp_clock_on/off` are local to the module but less SoC-specific than MT8186 names, so future shared code must avoid symbol confusion.

Test signals: Compile coverage and clock array bounds checks through probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-loader.c

Purpose: Implements MT8195 HIFIxDSP boot and shutdown register sequencing.

Important APIs: `sof_hifixdsp_boot_sequence()` writes `DSP_ALTRESETVEC`, asserts RUNSTALL and STATVECTOR_SEL, toggles DReset/BReset with a 1 us delay, enables PDebug, and releases RUNSTALL. `sof_hifixdsp_shutdown()` asserts RUNSTALL and D/B reset.

Control flow and integration: `mt8195_run()` calls boot with `SRAM_PHYS_BASE_FROM_DSP_VIEW`; suspend and remove paths use shutdown before SRAM/clock poweroff.

State and persistence: Alters reset, runstall, alternate reset vector, stat-vector selection, and pdebug register state.

Risks: Reset polarity and delay are vendor-sequenced; reordering can prevent boot. PDebug must be enabled before crash diagnostics are useful. The boot vector assumes firmware is loaded at the DSP-view SRAM base.

Test signals: FW_READY after boot, debug register availability after boot, shutdown during suspend, and recovery after repeated run/shutdown cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195.c

Purpose: Provides the MT8195 SOF OF platform driver and DSP ops.

Important APIs/state: `platform_parse_resource()` initializes reserved DRAM, cfg register, and SRAM resources, validating DRAM alignment and shared-buffer tail size. `mt8195_dsp_probe()` allocates `adsp_priv`, initializes clocks, powers SRAM, programs DRAM remap through SYS AO, maps IRAM/DRAM and DSP_REG_BAR, sets mailbox defaults, registers child `mtk-adsp-ipc`, and wires IPC ops. `sof_mt8195_ops` connects SOF core callbacks for run, IO, mailbox, IPC, stream ops, firmware loading, Xtensa dumps, DAI drivers, debugfs, PM, and PCM caps.

Control flow: Probe powers clocks and SRAM before remap and memory mapping; failure unwinds SRAM and clocks. Run boots from DSP-view SRAM. Suspend polls `DSP_RESET_SW` until `ADSP_PWAIT` or timeout, logs PC if not idle, shuts down DSP, powers SRAM off, and disables clocks. Resume powers clocks and SRAM. Remove unregisters IPC, powers SRAM off, and disables clocks. OF machine table selects Google Tomato/Dojo or generic MT8195 topology; descriptor is IPC3-only with 1000 ms IPC timeout.

Dependencies and integration: Uses SOF OF helpers, common MediaTek IPC helpers, MTK ADSP IPC, Xtensa arch ops, reserved memory, clock framework, and MT8195-specific clock/loader files.

Risks: `adsp_sram_power_on()` and `adsp_memory_remap_init()` use direct physical ioremap/devm_ioremap of SYS AO addresses, so address constants must remain valid. Suspend powers off even after idle timeout, risking context loss if firmware is wedged. Probe maps only cfg as DSP_REG_BAR, unlike MT8186's sec/bus bars. Error returns sometimes normalize to `-EINVAL`, losing provider-specific causes.

Test signals: DT resource failures, clock parent/enable failures, SYS AO remap/write verification failure, IPC child probe defer, FW boot for all machine compatibles, suspend idle timeout path, resume after D3, PCM pointer updates, and panic dump contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195.h

Purpose: Defines MT8195 DSP register addresses, bitfields, memory layout, BAR indexes, suspend timing, and boot/shutdown prototypes.

Important definitions: Includes DSP config/debug/reset/GPR/mailbox offsets, SYS AO SRAM pool and EMI remap physical addresses, mailbox offset/size, DRAM/SRAM DSP-view bases, DRAM remap mask/shift, shared DRAM tail sizes, BAR slots, and suspend idle poll interval/timeout.

Control flow and integration: Used by `mt8195.c` for resource setup, remap, suspend polling, debug dump, and mailbox offsets; by `mt8195-loader.c` for boot/reset sequencing; by `mt8195-clk.c` indirectly for SoC context.

State and persistence: Header constants describe hardware state written by runtime code.

Risks: Direct physical register constants (`DSP_SYSAO_BASE`, `ADSP_SRAM_POOL_CON`, `DSP_EMI_MAP_ADDR`) bypass named platform resources. Mismatch with firmware memory map breaks mailbox and shared buffer access. BAR indexes for mailbox registers are defined but this driver mainly uses DRAM mailbox via SOF block type.

Test signals: Register access validation on real MT8195, mailbox offset compatibility with firmware, suspend idle poll behavior, and debug dump register correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mtk-adsp-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mtk-adsp-common.c

Purpose: Provides shared MediaTek ADSP SOF helpers for panic dumps, mailbox IPC send/reply/request handling, BAR mapping, and PCM stream pointer behavior.

Important APIs: `mtk_adsp_dump()` reads Xtensa oops, panic info, and stack from mailbox/debug offsets and prints with `sof_print_oops_and_stack()`. `mtk_adsp_send_msg()` writes a SOF IPC message to `host_box.offset` then rings `mtk_adsp_ipc_send()`. `mtk_adsp_handle_reply()` processes replies under `sdev->ipc_lock`. `mtk_adsp_handle_request()` distinguishes panic magic from normal RX, invokes `snd_sof_ipc_msgs_rx()`, and sends a response doorbell. `mtk_adsp_get_bar_index()` maps firmware block type to BAR index. `mtk_adsp_stream_pcm_hw_params()` enables continuous position updates; `mtk_adsp_stream_pcm_pointer()` reads `sof_ipc_stream_posn` through IPC message data and converts host bytes to frames.

Control flow: IPC send is mailbox write then AP-to-ADSP request. Reply interrupt enters SOF reply processing. Request interrupt reads panic code from debug box, handles fatal panic or normal RX, then acknowledges DSP. Pointer lookup finds the SOF PCM by DAI ID, reads stream position for the stream, caches it, and returns frames.

Dependencies and integration: Consumed by MT8186/MT8195 `snd_sof_dsp_ops`; depends on `mtk-adsp-ipc`, SOF mailbox helpers, Xtensa oops structures, SOF client audio lists, and ALSA PCM conversion.

Risks: Panic detection assumes debug box offset +4 contains a panic code. `mtk_adsp_get_registers()` rejects oversized architecture headers but does not zero partial outputs. Pointer lookup returns 0 on missing PCM or read failure, which can hide hardware stalls. IPC response send failure only logs.

Test signals: Panic magic and normal request interrupts, reply completion, mailbox write ordering, malformed oops header, PCM pointer with valid/missing DAI, and continuous position update validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mtk-adsp-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mtk-adsp-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mtk-adsp-common.h

Purpose: Declares shared MediaTek ADSP helper APIs and dump-size constants.

Important definitions: `EXCEPT_MAX_HDR_SIZE` caps the firmware exception header at `0x400`; `MTK_ADSP_STACK_DUMP_SIZE` requests 32 stack words. Prototypes cover dump, IPC send/reply/request, BAR mapping, stream hw_params, and stream pointer.

Control flow and integration: MT8186/MT8195 ops tables reference these functions directly. The header relies on included users already knowing `snd_sof_dev`, `snd_sof_ipc_msg`, `mtk_adsp_ipc`, `snd_pcm_substream`, and stream parameter types.

State and persistence: No state; constants control dump parsing bounds.

Risks: Header does not include all type declarations itself, so include order matters. Changing dump sizes affects panic log completeness and mailbox read length.

Test signals: Compile with both SoC drivers and panic dump coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mtk-adsp-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/nocodec.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/nocodec.c

Purpose: Implements the dummy/no-codec ASoC machine driver used when SOF runs without a real codec-specific machine driver.

Important APIs/state: Static `sof_nocodec_card` is named `nocodec` with topology shortname `sof-nocodec`. `sof_nocodec_bes_setup()` builds one BE DAI link per SOF DAI driver using dummy codec, parent platform name, DAI IDs, playback/capture-only flags, and `sof_pcm_dai_link_fixup`. `sof_nocodec_probe()` receives `snd_soc_acpi_mach` platform data, creates links from `mach_params.dai_drivers`, and registers the card.

Control flow: Probe sets card device and marks topology shortname created, allocates BE links and two link components per DAI, fills CPU/platform/codec references, then registers with devm ASoC card registration. The platform driver is named `sof-nocodec`.

Dependencies and integration: Depends on SOF core creating a platform device with machine params, ASoC dummy codec, SOF PCM fixup, and `snd_soc_pm_ops`.

State and persistence: Link allocations are devm-managed. The static card is shared by module instance, so probe assumes one active device.

Risks: Static `snd_soc_card` can be problematic if multiple no-codec devices probe. DAI link names are generated `NoCodec-%d`; topology must match expected DAIs. No FE links are created here; this only supplies BEs for SOF topology integration.

Test signals: No-codec boot with each platform DAI set, playback-only/capture-only link flags, topology loading with `sof-nocodec`, and multi-device probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/nocodec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ops.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ops.c

Purpose: Implements non-inline SOF operation helpers for PCI/register bit updates and DSP panic handling.

Important APIs: `snd_sof_pci_update_bits()` updates PCI config dword bits under `sdev->hw_lock`. `snd_sof_dsp_update_bits_unlocked()`, `snd_sof_dsp_update_bits64_unlocked()`, locked 32/64-bit variants, and `snd_sof_dsp_update_bits_forced()` perform MMIO read-modify-write through ops wrappers. `snd_sof_dsp_panic()` records/validates panic offset, dumps debug information, marks fatal panics as `SOF_FW_CRASHED`, and notifies tracing.

Control flow: Update helpers compute `(old & ~mask) | (value & mask)`, skip writes if unchanged except forced update, and lock only in public locked variants. Panic handling stores `dsp_oops_offset` if unset, warns if offsets disagree, resets dump state, performs fatal or recoverable dump, and on fatal sets firmware state crashed and calls `sof_fw_trace_fw_crashed()`.

Dependencies and integration: Used by platform drivers, loader, PM, IPC exception paths, and MediaTek boot/clock code. Depends on PCI devices for PCI update, SOF MMIO ops for DSP update, `hw_lock`, and debug dump callbacks.

State and persistence: Mutates hardware registers, `dsp_oops_offset`, `dbg_dump_printed`, and firmware state.

Risks: Unlocked helpers require caller-side locking. PCI helper assumes `sdev->dev` is a PCI device. Panic offset disagreement may indicate firmware/kernel layout mismatch but only warns. Forced update is needed for RWC registers, but using normal update on RWC bits can lose events.

Test signals: Register bit updates with changed/unchanged values, 64-bit registers, forced RWC writes, concurrent callers, fatal and recoverable panic paths, and PCI-only helper use on PCI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ops.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ops.h

Purpose: Defines the central inline dispatch layer from generic SOF code to platform-specific `snd_sof_dsp_ops`.

Important APIs: Probe/remove/shutdown wrappers, DSP run/stall/reset, core get/put reference counting, pre/post FW run, platform extended manifest parsing, BAR/mailbox/window lookup, suspend/resume/runtime PM, clock setting, power state serialization, MMIO and mailbox IO, block IO, IPC send/data, PCM platform ops, firmware load, machine driver hooks, chain DMA query, and `snd_sof_dsp_read_poll_timeout()`.

Control flow and state: Most wrappers check optional callbacks and return 0/default when absent. Mandatory operations are expected to be verified during probe. Core get/put validates core index, reference counts `sdev->dsp_core_ref_count`, calls platform power callbacks only on 0-to-1 and 1-to-0 transitions, and maintains `enabled_cores_mask`. `snd_sof_dsp_set_power_state()` serializes with `power_state_access`. Register IO falls back to raw read/write accessors if ops are absent.

Dependencies and integration: Included across SOF core, IPC, PM, PCM, topology, and platform drivers. It is the compatibility layer that lets PCI, OF, ACPI, Intel, AMD, and MediaTek drivers plug into common SOF flows.

Risks: Default no-op behavior can hide missing optional callbacks. Core put pre-decrements refcount and does not guard underflow if callers are imbalanced. Raw read/write fallbacks assume `sdev->bar[bar]` is valid. Poll macro reads once more on timeout and returns based on final condition, so side-effect registers need care.

Test signals: Probe validation for mandatory ops, core refcount balance including errors, power-state serialization, fallback IO paths, optional callback absence, mailbox/window offset errors, and poll timeout/success behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/pcm.c

Purpose: Implements the ALSA PCM component layer that bridges ASoC PCM operations to SOF topology widgets, IPC-specific PCM ops, and platform DMA ops.

Important APIs/state: `snd_sof_pcm_period_elapsed()` schedules work to call ALSA period elapsed outside IRQ-sensitive IPC timing. `sof_pcm_hw_params()`, `prepare()`, `trigger()`, `hw_free()`, `open()`, `close()`, `pointer()`, `ack()`, `delay()`, and `pcm_new()` populate the `snd_soc_component_driver` in `snd_sof_new_platform_drv()`. State lives in `snd_sof_pcm`: `stream[].list`, `platform_params`, saved `params`, `prepared`, `setup_done`, `pending_stop`, `suspend_ignored`, page tables, and position data.

Control flow: Open sets runtime hardware from platform ops and topology caps, then opens platform DMA. Hw_params boots DSP if needed, handles repeated params by freeing previous setup, calls platform hw_params, prepares connected DAPM widgets, configures host widget DMA, creates page tables when the buffer changes, and saves params. Prepare recreates hw_params after resume/xrun if needed, sets up widgets/routes/pipelines, and calls IPC hw_params. Trigger decides whether IPC or platform DMA starts/stops first, handles D0i3 suspend-ignore and DSPless reset, and may defer STOP cleanup via `pending_stop`. Hw_free stops/free IPC and DMA, frees widgets, unprepares DAPM lists, and cancels period work.

Dependencies and integration: Uses SOF topology/widget helpers, IPC-specific PCM ops, platform PCM ops in `ops.h`, ALSA runtime constraints, DAPM connected-widget walking, PM runtime for topology probe, and SOF page-table helpers.

Risks: Prepared/setup/list flags must remain balanced across repeated hw_params, xruns, suspend, and errors. Trigger ordering differs by IPC ops and can deadlock or underrun if wrong. Period elapsed is delayed to avoid IPC timeout while IRQ thread still handles a previous IPC. BE no-pcm paths are no-ops.

Test signals: Open/close, repeated hw_params without hw_free, buffer_changed page table creation, prepare after xrun, START/STOP/PAUSE/SUSPEND trigger order for IPC3 and IPC4, D0i3-compatible stream suspend-ignore, DSPless mode, pointer fallback paths, topology probe failure, and BE DAI fixup fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/pm.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/pm.c

Purpose: Implements SOF firmware boot orchestration and runtime/system power-management flows.

Important APIs/state: `snd_sof_boot_dsp_firmware()` serializes boot with `dsp_fw_boot_mutex`, loads/runs firmware, resumes trace, restores pipelines, resumes clients, and calls IPC context restore. `sof_resume()` and `sof_suspend()` drive platform PM callbacks, firmware state transitions, trace suspend/resume, pipeline tear-down/setup, D0/D3 target selection, and on-demand boot. Exported wrappers provide runtime/system suspend/resume/idle, prepare/complete, and power-down notification. Module parameter `on_demand_boot` can override descriptor behavior.

Control flow: Power target maps S3/S4/S5 to D3, S0ix to D0 only if streams ignored suspend, and runtime to D3. Resume skips first boot, powers platform, handles DSPless, resumes trace only for D0 substate resume, optionally defers boot for on-demand mode, otherwise boots firmware. Suspend tears down pipelines if old state is D0, skips firmware notifications when not complete, sets hw_params-upon-resume for system suspend, suspends trace and clients, sends ctx_save unless staying in D0, calls platform suspend, and resets FW state/enabled cores on D3. Prepare derives suspend target from ACPI when enabled.

Dependencies and integration: Uses IPC PM ops, topology ops, platform DSP ops, trace helpers, SOF clients, ACPI target states, and PCM suspend-ignore state from `sof-audio.c`.

Risks: Firmware state is central; incorrect transitions can cause double boot or lost resume. `ctx_save` `-EBUSY/-EAGAIN` is propagated only for runtime PM; other errors continue to power down. On-demand boot defers firmware until PCM hw_params. Pipeline tear-down is attempted before state checks when old hardware state is D0. Debugfs cache is conditional and only captures D0-only entries when enabled.

Test signals: Runtime suspend/resume, S0ix with and without suspend-ignored streams, S3/S4/S5 targets, on-demand boot override, DSPless mode, ctx_save busy/error paths, crashed/boot-failed prepare behavior, trace suspend/resume failures, and pipeline restore failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-acpi-dev.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-acpi-dev.c

Purpose: Provides common ACPI platform-device probe/remove and PM ops for SOF ACPI drivers.

Important APIs/state: Exports namespace PM ops `sof_acpi_pm` with SOF system and runtime PM callbacks. Module params `fw_path` and `tplg_path` are deprecated overrides forwarded into `ipc_file_profile_base`; `sof_acpi_debug` can disable runtime PM with `SOF_ACPI_DISABLE_PM_RUNTIME`. `sof_acpi_probe()` allocates `snd_sof_pdata`, validates descriptor ops, sets descriptor/device/default IPC profile paths, installs a probe-complete callback, and calls `snd_sof_device_probe()`. `sof_acpi_remove()` disables runtime PM unless debug-disabled and removes the SOF device.

Control flow: Successful core probe calls `sof_acpi_probe_complete()`, which configures autosuspend delay, enables autosuspend, and enables runtime PM unless disabled by debug flag.

Dependencies and integration: Used by ACPI-specific SOF platform modules with matching descriptors. Depends on SOF core device probe/remove, ACPI PM, runtime PM, Intel ACPI matching headers, and platform descriptors.

Risks: Deprecated module params still affect firmware/topology path selection. Runtime PM disable debug flag changes power behavior and can mask suspend bugs. Probe fails if descriptor lacks ops before reaching SOF core validation.

Test signals: ACPI probe with valid/invalid desc, runtime PM enable/disable flag, deprecated path overrides, remove after partial probe, and system/runtime PM callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-acpi-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-acpi-dev.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-acpi-dev.h

Purpose: Declares the shared SOF ACPI PM/probe/remove interface.

Important APIs: `extern const struct dev_pm_ops sof_acpi_pm`, `sof_acpi_probe(struct platform_device *, const struct sof_dev_desc *)`, and `sof_acpi_remove(struct platform_device *)`.

Control flow and integration: ACPI platform drivers include this header to delegate common SOF setup/teardown and to attach the shared PM ops table.

State and persistence: No state. The implementation stores runtime state in `snd_sof_pdata` and SOF device data.

Risks: Header depends on callers having platform device and descriptor types visible through other includes. Namespace export in the C file means module users must import `SND_SOC_SOF_ACPI_DEV`.

Test signals: Compile/link of ACPI platform drivers and module namespace import checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-acpi-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-audio.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-audio.c

Purpose: Implements SOF topology runtime orchestration for widgets, routes, pipelines, D0i3 stream checks, and object lookup helpers.

Important APIs/state: Exports `sof_widget_setup()`, `sof_widget_free()`, `snd_sof_dsp_only_d0i3_compatible_stream_active()`, DAI parameter getters, and lookup helpers. Internal state includes widget `use_count`, `prepared`, `setup_mutex`, route `setup`, pipeline `complete`, core masks/refcounts, PCM stream pipeline lists, and DAPM widget lists.

Control flow: Widget setup increments use count, recursively sets up dynamic scheduler widgets, powers required DSP cores, calls IPC widget setup, sends DAI config, and restores kcontrols. Free decrements use count, resets/free routes, frees DAI config and widget, powers down scheduler cores, clears pipeline completion, and frees dynamic scheduler references. Widget-list prepare walks connected DAPM paths from AIF/DAI starts, skips virtual and aggregated DAI widgets, runs IPC prepare/unprepare, then setup creates widgets, routes, and completes pipelines. Route setup ignores virtual widgets and only binds routes whose endpoints are set up. Error paths free and unprepare already processed widgets.

Dependencies and integration: Used by PCM hw_params/prepare/hw_free and PM pipeline restore/tear-down. Depends on ASoC DAPM path walking, IPC topology ops, DSP core get/put wrappers, tracepoints, and topology-loaded lists on `sdev`.

Risks: Recursive DAPM walking must avoid cycles with `p->walking`. Use count and prepared flags must stay balanced across errors, aggregated DAI skips, and repeated hw_params. Dynamic pipeline widgets recursively reference scheduler widgets; missing `spipe` or `pipe_widget` is fatal. Direction-valid logic controls loopback/cross-direction routes and can skip required connections if topology is wrong.

Test signals: Dynamic/static pipelines, aggregated DAIs, virtual widgets, same-direction and cross-direction routes, setup failure unwind, DAI config hw_params/free, kcontrol restore, D0i3-compatible stream detection, lookup by name/component, and DAI MCLK/BCLK/TDM param retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-audio.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-audio.h

Purpose: Defines the core SOF audio/topology data model and IPC-facing operation tables used by PCM, topology, controls, and PM code.

Important APIs/types: Defines `SOF_AUDIO_PCM_DRV_NAME`, widget classification macros, DAI param constants, mixer volume mapping helpers, `struct sof_ipc_pcm_ops`, `sof_ipc_tplg_control_ops`, `sof_ipc_tplg_widget_ops`, `sof_ipc_tplg_ops`, topology token descriptors, `snd_sof_pcm_stream`, `snd_sof_pcm`, `snd_sof_control`, `snd_sof_dai_link`, `snd_sof_widget`, `snd_sof_pipeline`, `snd_sof_route`, and `snd_sof_dai`. It declares kcontrol, topology load, stream position, widget/route/PCM helpers, token parsers, and PM helpers.

Control flow and integration: IPC implementations fill the ops tables to customize PCM hw_params/trigger/pointer, control IO, widget prepare/setup/free, DAI config, route setup, pipeline completion, manifest parsing, and pipeline restore/tear-down. Runtime code stores topology-derived objects on `snd_sof_dev` lists and uses the declared helpers to find and operate on them.

State and persistence: Structures hold long-lived topology state, runtime PCM state, control cache/dirty state, dynamic widget IDs, pin bindings, queue ID allocators, pipeline counters, route queue IDs, and private IPC-specific data. Most objects live until topology/component removal, while prepared/setup/use-count fields change per stream lifecycle.

Risks: Many fields are touched by both generic and IPC-specific code through `private` pointers, so ownership boundaries must be respected. `snd_sof_find_spcm_dai()` matches DAI link ID to topology `dai_id`; mismatch breaks PCM lookup. Volume conversion assumes monotonic volume maps. Pin binding arrays must match IPC4 max pin constraints.

Test signals: Compile all IPC backends against ops structs, topology token parsing, PCM lookup by DAI/name/component, kcontrol dirty/update paths, volume map boundary values, queue ID allocation, and CONFIG_SND_SOC_SOF_COMPRESS on/off stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-flood-test.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-flood-test.c

Purpose: Auxiliary SOF client that exposes debugfs-triggered IPC flood tests for measuring IPC latency and stress behavior.

Important APIs/state: `struct sof_ipc_flood_priv` stores debugfs root, backward-compatible symlinks, and a result buffer. Debugfs files `ipc_flood_count` and `ipc_flood_duration_ms` share `sof_ipc_flood_fops`; aux num selects count or duration mode. `sof_debug_ipc_flood_test()` sends repeated `SOF_IPC_GLB_TEST_MSG | SOF_IPC_TEST_IPC_FLOOD` commands and records min/max/average response times.

Control flow: Open rejects crashed firmware and takes a debugfs active reference. Write parses user count/duration, clamps to 10000 IPCs or 1000 ms, resumes runtime PM, boots DSP, runs the test through no-reply IPC sends, autosuspends, and returns count on success. Read returns the last formatted result. Probe creates per-device debugfs files and symlinks for auxdev id 0, then enables runtime PM; remove disables PM and removes debugfs.

Dependencies and integration: Uses SOF client APIs, auxiliary bus, debugfs, runtime PM, IPC test command support in firmware, and generic auxiliary PM behavior.

Risks: Flooding is bounded but still stresses firmware and can perturb active audio. Result buffer is shared per client without explicit serialization. `ktime_get_ns() + duration * NSEC_PER_MSEC` is simple and bounded by clamp. Open-time crashed check does not prevent crash during write.

Test signals: Count and duration writes, zero values, clamp limits, firmware crashed open, runtime PM resume errors, DSP boot errors, IPC failure mid-test, readback formatting, symlink creation/removal for id 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-flood-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-kernel-injector.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-kernel-injector.c

Purpose: Auxiliary SOF client exposing a debugfs file that injects a user-provided IPC buffer into the kernel RX path, useful for testing kernel-side IPC message handling.

Important APIs/state: `struct sof_msg_inject_priv` stores the `kernel_ipc_msg_inject` debugfs dentry, maximum message size, and kernel buffer. `sof_kernel_msg_inject_dfs_write()` copies user data into the buffer, resumes PM, boots DSP, and calls `sof_client_ipc_rx_message(cdev, hdr, buffer)`.

Control flow: Open takes a debugfs active reference. Write only acts at offset 0, uses `simple_write_to_buffer()` with max payload size, requires full copy, resumes runtime PM, boots DSP, injects the message into RX handling, and autosuspends. Probe allocates state and buffer sized by `sof_client_get_ipc_max_payload_size()`, creates debugfs, and enables runtime PM as active/idle. Remove disables PM and removes debugfs.

Dependencies and integration: Uses SOF client IPC/RX APIs, auxiliary bus, debugfs, runtime PM, and firmware/header layout only enough to treat the buffer as `sof_ipc_cmd_hdr`.

Risks: This is intentionally powerful test/debug functionality; malformed buffers exercise kernel IPC parsers. Unlike the message injector, open does not check firmware crashed state. Write ignores return from `sof_client_ipc_rx_message()` because it is void and returns `count` after PM put even if injection caused parser errors.

Test signals: Oversized writes, partial copy failure, PM resume/boot failure, malformed headers through RX parser, debugfs lifetime, and module unload during open file handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-kernel-injector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-msg-injector.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-msg-injector.c

Purpose: Auxiliary SOF client exposing debugfs `ipc_msg_inject` to send arbitrary IPC messages to firmware and read back replies, with IPC3 and IPC4-specific buffer handling.

Important APIs/state: `struct sof_msg_inject_priv` stores debugfs file, max message size, IPC type, TX buffer, and RX buffer. IPC3 fops treat buffers as normal SOF IPC headers/replies. IPC4 fops copy a 64-bit IPC4 header plus optional payload into `struct sof_ipc4_msg`, preserve `data_ptr`, and read back header plus large-config payload when applicable.

Control flow: Open rejects crashed firmware and takes a debugfs reference. Write copies user data into TX storage, zeroes reply storage, resumes PM, boots DSP, sends with `sof_client_ipc_tx_message()`, autosuspends, and returns bytes or error. IPC4 write requires at least header size and initializes RX data capacity before send. Read returns IPC3 reply size or IPC4 header/payload, respecting file offset and user count. Probe chooses fops by `sof_client_get_ipc_type()`, allocates extra space for IPC4 containers, initializes IPC4 data pointers, creates debugfs, and enables runtime PM.

Dependencies and integration: Uses SOF client IPC wrappers, IPC4 header macros, debugfs, auxiliary bus, runtime PM, and firmware support for arbitrary messages.

Risks: Debugfs allows privileged users to send malformed or destructive IPCs. IPC4 data size validation checks payload against max message size but allocated IPC4 buffer includes header plus max payload. Read offset arithmetic copies IPC4 payload at `buffer + *ppos`, which follows header-only offset semantics and must stay consistent. Static `fops` in probe is assigned per probe but values are immutable pointers.

Test signals: IPC3 and IPC4 writes/reads, short IPC4 header, oversized payload, large-config GET reply payload, firmware crash rejection, PM and boot failures, IPC error propagation, and debugfs remove with open files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-msg-injector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes-ipc3.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes-ipc3.c

Purpose: Implements IPC3-specific probe control operations for the SOF probes client.

Important APIs/types: Defines packed IPC3 probe DMA, info, add, and remove payload structs. `ipc3_probe_ops` exposes `.init`, `.deinit`, `.points_info`, `.points_add`, and `.points_remove`. Init sends one extractor DMA descriptor; deinit sends `SOF_IPC_PROBE_DEINIT`. Info supports active probe info only. Add/remove send flexible arrays of `sof_probe_point_desc` or buffer IDs.

Control flow: Each operation allocates the exact variable-size message with `struct_size()`, fills SOF IPC global probe command headers, sends via SOF client IPC, and frees temporary memory. Info allocates a max-size reply buffer, requests DMA or point info, validates reply/error, duplicates returned entries, and returns element count.

Dependencies and integration: Consumed by generic `sof-client-probes` code when the client IPC type is IPC3. Uses SOF IPC3 command IDs, SOF client max payload size, and generic probe point descriptors.

Risks: Info only supports `PROBES_INFO_ACTIVE_PROBES`; available probes returns `-EOPNOTSUPP`. Flexible-array copy sizes must match message struct layout. Reply `rhdr.error` is checked but not converted separately if `ret` is already negative. Init/deinit lifetime must be matched by higher-level client.

Test signals: Init/deinit pairing, active DMA/point info, no elements, reply error, allocation failures, add/remove multiple points, and unsupported available-probe query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes-ipc3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes-ipc4.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes-ipc4.c

Purpose: Implements IPC4-specific probe module control operations for the SOF probes client.

Important APIs/state: Defines IPC4 DMA/node types, runtime param IDs, probe gateway config, probe point encoding helpers, and IPC4 probe info structs. `sof_ipc4_probe_get_module_info()` locates and caches the probe module manifest entry by hard-coded UUID in `sof_probes_priv->ipc_priv`. `ipc4_probe_ops` exposes init/deinit/info/print/add/remove.

Control flow: Init builds `MOD_INIT_INSTANCE` for the probe module, with host-input DMA node derived from `stream_tag - 1`, buffer size, invalid pipeline ID, core 0, and config size. Deinit sends `MOD_DELETE_INSTANCE`. Points info sends large-config GET for active or available points, allocates max payload, converts returned IPC4 points to generic descriptors, and frees the IPC buffer. Point print resolves the module/instance to a widget and formats type/index/connection text. Add converts generic descriptors to IPC4 points and sends large-config SET for `SOF_IPC4_PROBE_POINTS`; remove sends large-config SET for disconnect IDs.

Dependencies and integration: Depends on IPC4 manifest/module lookup helpers, SOF client large config `set_get_data`, IPC4 header macros, topology widget lookup by module ID/instance, and generic probes client descriptors.

Risks: Probe module UUID is hard-coded; firmware manifest changes break probing. `stream_tag - 1` assumes valid nonzero stream tags. Info trusts returned `num_elems` to size allocation from the max payload buffer. Point printing can continue with unknown widget but logs an error. Init uses invalid pipeline ID and core 0, so multi-core/pipeline probe support would need changes.

Test signals: Probe module found/missing, init/deinit, active and available point info, malformed num_elems, add/remove multiple probe points, point print for known/unknown widgets, stream tag boundary, and IPC4 large-config failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes-ipc4.c -->
