# subset-b-004268 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sd.c

### Purpose
`sd.c` is the core SD memory-card attach, identification, capability decoding, speed negotiation, cache/power-extension, detection, suspend/resume, and bus-operation implementation for the MMC subsystem. It translates raw SD registers and SD application commands into `struct mmc_card` state, then registers the card with the MMC bus.

### Important APIs, Types, And Functions
The public/internal entry points are `mmc_attach_sd()`, `mmc_sd_get_cid()`, `mmc_sd_get_csd()`, `mmc_sd_setup_card()`, `mmc_sd_get_ro()`, `mmc_sd_get_max_clock()`, `mmc_sd_switch_hs()`, `mmc_decode_cid()`, `mmc_decode_scr()`, and exported `sd_type`. `mmc_sd_ops` implements the bus callbacks for remove, detect, runtime/system PM, alive, shutdown, hardware reset, cache status, and cache flush. Decoders and setup helpers populate `card->cid`, `card->csd`, `card->scr`, `card->ssr`, `card->sw_caps`, `card->ext_power`, `card->ext_perf`, `card->erase_size`, and read-only flags. UHS-I helpers include `mmc_sd_init_uhs_card()`, `sd_update_bus_speed_mode()`, `sd_select_driver_type()`, `sd_set_current_limit()`, `sd_set_bus_speed_mode()`, and `mmc_sd_use_tuning()`.

### Control Flow
Attach probes OCR with ACMD41, attaches `mmc_sd_ops`, narrows host voltage, and calls `mmc_sd_init_card()`. Initialization gets CID, allocates or reuses a card, invokes host quirks, assigns RCA, reads CSD/CID, selects the card, applies SD fixups, reads SCR/SSR/switch status, enables SPI CRC when needed, checks write-protect, then selects UHS-I or legacy high-speed timing. UHS-I setup switches to 4-bit mode, selects driver strength/current limit/bus speed, sets host timing/clock, and runs tuning for SDR50/SDR104 and optionally DDR50. Legacy setup switches high speed, sets clock, performs optional host tuning hooks, and enables 4-bit mode. New cards then read extension registers, enable cache when supported, optionally enable CQE/host software queue, and reject unresolved 3.3V operation when `MMC_CAP2_AVOID_3_3V` is set.

### State, Persistence, And Dependencies
Persistent kernel state is held on `host->card` and the card substructures decoded from raw SD registers. User-visible state appears through `sd_std_groups` sysfs attributes for raw CID/CSD/SCR/SSR, identity fields, OCR/RCA, erase sizes, DSR, and combo-card CIS metadata. Extension register writes persist on the card for cache enable, cache flush, and power-off notification until power/reset semantics clear them. Dependencies include `core.h`, `card.h`, `host.h`, `bus.h`, `mmc_ops.h`, `sd_ops.h`, SD/MMC public headers, PM runtime, sysfs, scatterlist, quirks, and host callbacks such as voltage switch, tuning, CQE, and `get_ro`.

### Integration Points
`sd.c` is reached from the MMC rescan path through `mmc_attach_sd()`. It uses command helpers from `sd_ops.c` and generic MMC operations, installs `mmc_sd_ops` into the bus layer, publishes `sd_type` for `mmc_alloc_card()`, and cooperates with block/card layers through erase/cache/CQE fields. PM callbacks coordinate with runtime PM and card power state, while cache callbacks integrate with block-layer flush handling.

### Risks
The initialization sequence is highly order-sensitive: changing when SCR/SSR/switch data is read can break UHS mode negotiation, erase geometry, or combo-card sysfs. Voltage-switch retry handling must preserve card identity and avoid leaving a card in 1.8V while the host believes it is at 3.3V. Cache and power-off-notify use CMD48/CMD49 extension registers plus busy polling; failures can lose data or hang suspend if not surfaced. The file as read contains a duplicated `__be32 *raw_ssr;` declaration in `mmc_read_ssr()` and a duplicated `mmc_sd_setup_card()` call in `mmc_sd_init_card()`, both strong build/review signals. Lifetime around `mmc_sd_remove()` keeps a temporary device reference while powering off after removal.

### Test Signals
Build this file with representative SD configs to catch duplicate declarations and signature drift. Runtime signals include SD, SDHC, SDXC, SDUC, SPI SD, UHS-I SDR12/25/50/104 and DDR50 attach, voltage-switch retry and fallback, read-only GPIO/switch behavior, sysfs attribute correctness, cache enable/flush, CQE enablement, card removal detection, runtime/system suspend/resume, hardware reset, and power-off-notify timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sd.h

### Purpose
`sd.h` is the internal SD memory-card contract between MMC core files. It exposes SD card type metadata and the core SD identification/setup helpers without leaking implementation details from `sd.c`.

### Important APIs, Types, And Functions
It declares `extern const struct device_type sd_type`, forward declares `struct mmc_host` and `struct mmc_card`, and declares `mmc_sd_get_cid()`, `mmc_sd_get_csd()`, `mmc_decode_scr()`, `mmc_sd_get_ro()`, `mmc_decode_cid()`, `mmc_sd_setup_card()`, `mmc_sd_get_max_clock()`, and `mmc_sd_switch_hs()`.

### Control Flow
The header has no runtime logic. `sd.c`, SDIO combo handling, and UHS-II legacy initialization include it to decode/register memory-card portions and to reuse high-speed/card setup operations.

### State, Persistence, And Dependencies
No state is stored here. It depends only on `linux/types.h` and opaque MMC card/host declarations, keeping the compile-time interface narrow.

### Integration Points
`sdio.c` and `sd_uhs2.c` use this header for combo-card memory setup, CID/CSD/SCR decoding, high-speed switching, and max-clock calculation. `sd_type` links SD card allocations to the SD sysfs attribute group.

### Risks
Any signature change affects several MMC core paths. The header intentionally omits attach and PM functions, so callers must continue using bus attach APIs rather than bypassing SD initialization.

### Test Signals
Compile coverage for SD-only, SDIO-combo, and UHS-II configurations validates the declarations. Runtime coverage is inherited from the implementation users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.c

### Purpose
`sd_ops.c` implements low-level SD and SD application command helpers used by card discovery and mode switching. It wraps APP_CMD sequencing, ACMD polling, SCR/SSR reads, SD switch commands, interface-condition checks, RCA retrieval, and SDUC extension-address handling.

### Important APIs, Types, And Functions
Key functions are `mmc_app_cmd()`, `mmc_app_set_bus_width()`, `mmc_send_app_op_cond()`, `mmc_send_ext_addr()`, `mmc_send_if_cond()`, `mmc_send_if_cond_pcie()`, `mmc_send_relative_addr()`, `mmc_app_send_scr()`, `mmc_sd_switch()`, and `mmc_app_sd_status()`. `struct sd_app_op_cond_busy_data` carries ACMD41 polling state for `__mmc_poll_for_busy()`.

### Control Flow
Most application commands first call `mmc_app_cmd()` then submit the real ACMD through `mmc_wait_for_app_cmd()`, which retries by reissuing APP_CMD each attempt. `mmc_send_app_op_cond()` builds ACMD41, polls until busy clears or the 2s timeout expires, and returns the OCR response. `mmc_send_if_cond*()` sends CMD8 and validates the test pattern, with the PCIe variant optionally initializing SD Express and updating `host->ios.timing`. SCR and SSR helpers allocate DMA-safe buffers, issue ADTC reads, convert big-endian SCR words, and return command/data errors. `mmc_sd_switch()` forms CMD6 function-group arguments and reads the 64-byte status buffer.

### State, Persistence, And Dependencies
The helpers mostly do not own state, but they mutate command responses, `host->uhs2_app_cmd` for UHS-II transport, `host->ios.timing` for SD Express probing, and card raw SCR storage. They depend on generic MMC command submission, scatterlists, SD/MMC constants, host/card structures, and `mmc_send_adtc_data()`.

### Integration Points
`sd.c`, `sdio.c`, and `sd_uhs2.c` call these helpers during attach, combo-card setup, bus-width switching, high-speed/UHS negotiation, status reads, and SD-TRAN over UHS-II. `mmc_app_cmd()` contains UHS-II awareness by marking the next packet as APP rather than sending legacy CMD55 directly.

### Risks
APP command retry semantics are subtle because APP_CMD must be resent for every attempt. SPI and native response layouts differ for OCR, R5/R7, and illegal-command checks. CMD8 PCIe probing changes host timing and calls host SD Express init, so failures must preserve legacy SD probing. SCR/SSR callers must pass heap/DMA-safe buffers, as the comments emphasize. UHS-II APP command state must be cleared by packet preparation or subsequent commands can be mislabeled.

### Test Signals
Exercise SDSC/SDHC/SDUC attach, SPI attach, cards that reject CMD8, ACMD41 timeout and retry behavior, APP command illegal-command handling, SCR/SSR DMA reads, CMD6 switch status parsing, SD Express-capable host probing, and UHS-II SD-TRAN APP command packaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.h

### Purpose
`sd_ops.h` declares internal SD command helpers for the MMC core.

### Important APIs, Types, And Functions
It declares helpers for SD APP bus width, ACMD41 OCR negotiation, CMD8 interface checks, SD Express CMD8 probing, RCA assignment, SCR and SSR reads, APP_CMD, SDUC extension address, and UHS-II request preparation: `mmc_app_set_bus_width()`, `mmc_send_app_op_cond()`, `mmc_send_if_cond()`, `mmc_send_if_cond_pcie()`, `mmc_send_relative_addr()`, `mmc_app_send_scr()`, `mmc_app_sd_status()`, `mmc_app_cmd()`, `mmc_send_ext_addr()`, and `mmc_uhs2_prepare_cmd()`.

### Control Flow
There is no runtime control flow. The declarations let higher-level attach/setup code call the low-level command wrappers in `sd_ops.c` and `sd_uhs2.c`.

### State, Persistence, And Dependencies
No state is stored. The header depends on `linux/types.h` and opaque declarations for `mmc_card`, `mmc_host`, and `mmc_request`.

### Integration Points
Included by SD, SDIO, and UHS-II implementation files to keep SD command construction centralized.

### Risks
Because `mmc_uhs2_prepare_cmd()` is declared here but implemented in `sd_uhs2.c`, non-UHS-II builds must still satisfy link/config expectations. Any prototype drift can break several attach paths.

### Test Signals
Compile matrix coverage with SD, SDIO, SD Express, and UHS-II options validates this header's exported internal surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd_uhs2.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sd_uhs2.c

### Purpose
`sd_uhs2.c` implements SD UHS-II attach, enumeration, configuration, legacy SD-TRAN initialization, PM, reset, and command-packet preparation. It bridges native UHS-II packets with the existing MMC request model and the SD memory-card setup flow.

### Important APIs, Types, And Functions
Public entry points are `mmc_attach_sd_uhs2()` and `mmc_uhs2_prepare_cmd()`. `sd_uhs2_ops` provides bus remove, detect, alive, suspend/resume, runtime PM, shutdown, and hardware reset callbacks. Core helpers include `sd_uhs2_power_up()`, `sd_uhs2_power_off()`, `sd_uhs2_phy_init()`, `sd_uhs2_dev_init()`, `sd_uhs2_enum()`, `sd_uhs2_config_read()`, `sd_uhs2_config_write()`, `sd_uhs2_go_dormant_state()`, `sd_uhs2_init_card()`, `sd_uhs2_legacy_init()`, and `sd_uhs2_reinit()`.

### Control Flow
`mmc_attach_sd_uhs2()` first checks host capability, powers off legacy SD, then tries UHS-II initialization at 52 MHz and 26 MHz. Attach powers up the host, initializes the PHY, sends DEVICE_INIT, enumerates a node ID, allocates a card, reads card configuration registers, writes negotiated generic/PHY/link settings, optionally enters dormant state for speed-range changes, sets `host->uhs2_sd_tran`, and runs legacy SD initialization through SD-TRAN. Legacy init resets the SD side, sends CMD8/ACMD41/CID/RCA/CSD/SCR, decodes SD identity, selects high power via CMD6 group 3 when possible, and checks write-protect. `mmc_uhs2_prepare_cmd()` converts an MMC request into UHS-II CCMD/DCMD metadata, handles APP tagging, multi-block half-duplex transfer mode, and payload length.

### State, Persistence, And Dependencies
State is stored in `host->ios`, `host->uhs2_caps`, `host->uhs2_sd_tran`, `host->uhs2_app_cmd`, `host->card`, and `card->uhs2_config`. Configuration writes change card link/PHY behavior and host UHS-II register settings through `host->ops->uhs2_control()`. Dependencies include UHS-II public constants, generic MMC/SD helpers, SD memory-card decoding, bus attach, PM runtime, and host UHS-II control operations such as `UHS2_SET_IOS`, `UHS2_PHY_INIT`, `UHS2_SET_CONFIG`, interrupt enable/disable, clock control, and dormant checks.

### Integration Points
This path is attempted before/alongside legacy SD probing on hosts with `MMC_CAP2_SD_UHS2`. It reuses `sd_type`, `mmc_decode_cid()`, `mmc_sd_get_csd()`, `mmc_decode_scr()`, `mmc_sd_get_ro()`, and `mmc_sd_switch()` for the SD-TRAN phase. Host drivers must provide UHS-II controls and request handling that understands `cmd->uhs2_cmd`.

### Risks
The sequence is spec-driven and fragile: DEVICE_INIT retry semantics, node ID assignment, configuration register endianness, dormant-state transitions, and config-complete polling must align with host hardware. `sd_uhs2_config_write()` assumes 2-lane full/half-duplex choices and hardcodes max retry to 3. PM suspend powers off rather than using hibernate, so resume must fully reinitialize and verify identity. Incorrect APP state handling can corrupt subsequent SD-TRAN commands. Removal lacks the graceful power-off-notify/cache handling found in `sd.c`.

### Test Signals
Use a UHS-II-capable host/card at both 52 MHz and 26 MHz retry frequencies, speed range A/B, half-duplex and full-duplex modes, dormant-state transitions, SD-TRAN legacy initialization, high-power CMD6 selection, card removal detection, runtime/system suspend/resume, hardware reset, and multi-block UHS-II command packet generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sd_uhs2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio.c

### Purpose
`sdio.c` implements SDIO card attach, common register decoding, SDIO function discovery, SDIO/combo-card speed and bus-width negotiation, runtime/system PM, reset, and detection. It turns a responding SDIO card into one MMC card device plus one driver-model child per function.

### Important APIs, Types, And Functions
The entry point is `mmc_attach_sdio()`. Important helpers are `sdio_read_fbr()`, `sdio_init_func()`, `sdio_read_cccr()`, `sdio_enable_wide()`, `sdio_disable_cd()`, `sdio_disable_wide()`, `sdio_enable_4bit_bus()`, `sdio_enable_hs()`, `mmc_sdio_get_max_clock()`, `sdio_select_driver_type()`, `sdio_set_bus_speed_mode()`, `mmc_sdio_init_uhs_card()`, `mmc_sdio_pre_init()`, `mmc_sdio_init_card()`, `mmc_sdio_reinit_card()`, and the `mmc_sdio_ops` bus callbacks. `sdio_type` defines card-level sysfs attributes for SDIO-only devices.

### Control Flow
Attach probes CMD5 OCR, installs SDIO bus ops, selects voltage, initializes the card, enables runtime PM when supported, initializes each function from OCR function count, registers the card, then registers each SDIO function. Initialization optionally requests 1.8V, distinguishes SDIO-only from SD combo by memory-present and CID behavior, applies host and SDIO fixups, assigns RCA, reads combo CSD/CID when needed, selects the card, reads CCCR/CIS, swaps an old card back in on resume if vendor/device match, sets up combo memory via `mmc_sd_setup_card()`, disables CD pull-up if requested, and chooses UHS-I or legacy high-speed/4-bit operation.

### State, Persistence, And Dependencies
State lands in `host->card`, `card->cccr`, `card->cis`, `card->sdio_func[]`, `card->sdio_funcs`, `card->sw_caps`, `card->scr`, `card->type`, `host->pm_flags`, and runtime PM state on the card and functions. Sysfs exposes vendor/device/revision/info/OCR/RCA at the card level. Dependencies include SDIO ops, CIS parsing, SD memory helpers for combo cards, quirks, bus registration, PM runtime, and host capabilities for voltage, 4-bit, high speed, UHS, power-off-card, IRQ wake, and retuning.

### Integration Points
`mmc_attach_sdio()` is called from the MMC rescan path. It creates function devices via `sdio_alloc_func()` and `sdio_add_func()` from `sdio_bus.c`, reads tuple data through `sdio_cis.c`, and uses `sdio_irq.c` indirectly for IRQ restart after resume. Function drivers bind through the SDIO bus and use exported APIs from `sdio_io.c` and `sdio_irq.c`.

### Risks
Probe ordering is sensitive because function devices are initialized before they are registered, while runtime PM is held until after registration. Resume identity matching for SDIO-only devices relies on CIS vendor/device rather than CID. Voltage-switch fallback must reset/reprobe cleanly or UHS-capable cards can be left inaccessible. PM paths remove removable cards that lack function PM callbacks but keep non-removable cards despite missing ops. Multi-function hardware reset is asynchronous through rescan so all drivers see removal, while single-function reset is immediate. Keeping power with wake SDIO IRQ forces 1-bit mode and later retune-safe 4-bit restoration.

### Test Signals
Cover SDIO-only, SD combo, nonstandard SDIO quirks, multi-function cards, function registration failure cleanup, runtime PM power-off-card, missing suspend/resume callbacks, keep-power wake IRQ, UHS-I SDR/DDR, 1.8V fallback, software reset, hardware reset with one versus multiple probed functions, and card removal during function probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.c

### Purpose
`sdio_bus.c` implements the Linux driver model bus for SDIO functions. It matches `struct sdio_driver` tables to `struct sdio_func` devices, manages probe/remove/shutdown, sysfs/modalias/uevents, function allocation, and function device add/remove.

### Important APIs, Types, And Functions
Public/internal APIs are `sdio_register_bus()`, `sdio_unregister_bus()`, `__sdio_register_driver()`, `sdio_unregister_driver()`, `sdio_alloc_func()`, `sdio_add_func()`, and `sdio_remove_func()`. Core helpers include `sdio_match_one()`, `sdio_match_device()`, `sdio_bus_match()`, `sdio_bus_uevent()`, `sdio_bus_probe()`, `sdio_bus_remove()`, `sdio_bus_shutdown()`, `sdio_release_func()`, `sdio_acpi_set_handle()`, and `sdio_set_of_node()`.

### Control Flow
Bus registration installs a `bus_type` named `sdio`. When a function device is added, matching compares class/vendor/device against the driver's ID table and emits SDIO uevent variables plus modalias. Probe attaches PM domain, increments the card's probed-function count, powers the function when power-off-card is supported, claims the host, sets a default block size, releases the host, and calls the function driver's `probe()`. Remove powers the function, calls driver `remove()`, decrements the probed count, warns and releases leaked IRQ handlers, and drops runtime PM references. Function allocation initializes a device, takes a reference on the parent card because tuples can point there, allocates an aligned tmp buffer, and defers freeing to `sdio_release_func()`.

### State, Persistence, And Dependencies
State is in the device model, `func->dev`, `func->tmpbuf`, `func->info`, `func->tuples`, `func->card`, `func->irq_handler`, `func->present`, OF/ACPI companion data, and `card->sdio_funcs_probed`. Dependencies include device core, PM runtime/domains, ACPI, OF, MMC card/host types, SDIO CIS freeing, and SDIO I/O helpers for block-size setup.

### Integration Points
`sdio.c` allocates and registers function devices through this file. SDIO function drivers register with `sdio_register_driver()` wrappers, bind through this bus, and use modalias `sdio:cXXvXXXXdXXXX` for module autoloading. OF child matching uses function number; ACPI address combines host slot number and function number.

### Risks
Runtime PM usage-count balancing is delicate across probe failure, remove, and card power-off. A driver that forgets `sdio_release_irq()` is repaired with a warning, but IRQ release occurs during remove and can still expose ordering issues. Tuple lifetime depends on the card reference taken during function allocation. `sdio_add_func()` can fail after OF/ACPI association; cleanup must call `sdio_remove_func()`.

### Test Signals
Test driver autoload modaliases, sysfs attributes, OF/ACPI enumeration, probe failure at block-size setup and driver probe, remove with leaked IRQ handler, runtime PM-enabled and disabled hosts, multi-function probed count changes, and function add/remove error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.h

### Purpose
`sdio_bus.h` declares the internal SDIO bus and function-device lifecycle helpers.

### Important APIs, Types, And Functions
It forward declares `struct mmc_card` and `struct sdio_func`, then exposes `sdio_alloc_func()`, `sdio_add_func()`, `sdio_remove_func()`, `sdio_register_bus()`, and `sdio_unregister_bus()`.

### Control Flow
The header has no runtime logic. Callers allocate functions during card initialization, add them after card registration, remove them during teardown, and register/unregister the bus from MMC core init/exit paths.

### State, Persistence, And Dependencies
No state is stored. It is a narrow compile-time interface to `sdio_bus.c`.

### Integration Points
`sdio.c` uses the function lifecycle helpers; MMC core initialization uses bus registration. Keeping this contract small prevents function drivers from depending on private bus internals.

### Risks
Misordered use of these helpers can create device-model lifetime bugs, especially adding function devices before the parent card exists or removing without dropping function/card references.

### Test Signals
Compile coverage and SDIO attach/remove tests validate this header's declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.c

### Purpose
`sdio_cis.c` reads and parses SDIO Card Information Structure tuples for the common function and individual SDIO functions. It extracts identity, revision, info strings, block size, max transfer rate, enable timeout, and preserves unknown/vendor tuples for function drivers.

### Important APIs, Types, And Functions
Public/internal APIs are `sdio_read_common_cis()`, `sdio_free_common_cis()`, `sdio_read_func_cis()`, and `sdio_free_func_cis()`. Tuple parsers include `cistpl_vers_1()`, `cistpl_manfid()`, `cistpl_funce_common()`, `cistpl_funce_func()`, `cistpl_funce()`, and dispatcher `cis_tpl_parse()`. `struct cis_tpl` maps tuple codes to minimum lengths and parsers.

### Control Flow
`sdio_read_cis()` reads the three-byte CIS pointer from CCCR/FBR space, walks tuples until 0xff/end, allocates storage for each tuple, reads tuple payload bytes with CMD52, parses known tuples, queues unknown or intentionally unparsed tuples, and advances the pointer. Common CIS data populates `card->cis`, card revision, and card info strings. Function CIS data populates `func->vendor`, `func->device`, revision, info strings, `func->max_blksize`, and `func->enable_timeout`; missing function vendor/device falls back to card CIS values. Function tuple lists are terminated by the common tuple list so drivers can see both.

### State, Persistence, And Dependencies
State is in allocated info-string arrays and linked `struct sdio_func_tuple` lists owned by the card or function. It depends on SDIO register constants, `mmc_io_rw_direct()`, `jiffies`, SDIO revision values, and MMC card/function structures.

### Integration Points
`sdio.c` calls common CIS reading before function initialization and function CIS reading inside `sdio_init_func()`. `sdio_bus.c` frees function CIS data on device release. Function drivers, including `sdio_uart.c`, inspect queued tuples for device-specific data.

### Risks
CIS parsing reads byte-by-byte and trusts tuple links enough to allocate `sizeof(*tuple) + tpl_link`; malformed cards can cause long reads, warnings, or memory pressure. The per-loop timeout is scoped inside the tuple loop and only affects unknown tuple warning behavior, not a global CIS traversal timeout. Function tuple lists share the common tuple tail, so free logic must stop before freeing card-owned tuples. Broken SDIO 1.1 CIS lengths are special-cased by downgrading parsing to SDIO 1.0 semantics.

### Test Signals
Use cards with valid common/function CIS, absent optional function vendor/device, unknown/vendor tuples, tuple 0x91 for UART/GPS, broken SDIO 1.1 FUNCE length, malformed short tuples, duplicate CIS reads, and cleanup after partial attach failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.h

### Purpose
`sdio_cis.h` declares the internal SDIO CIS read/free helpers used by SDIO card setup and function release.

### Important APIs, Types, And Functions
It declares `sdio_read_common_cis()`, `sdio_free_common_cis()`, `sdio_read_func_cis()`, and `sdio_free_func_cis()` for `struct mmc_card` and `struct sdio_func`.

### Control Flow
There is no runtime logic. The read helpers are called during attach before function devices are registered; free helpers are called during card/function teardown.

### State, Persistence, And Dependencies
No state is stored. It forwards opaque MMC/SDIO types and leaves ownership rules to `sdio_cis.c`.

### Integration Points
`sdio.c` reads CIS data, and `sdio_bus.c` releases function CIS allocations. This header keeps tuple parsing private to the core while still exposing lifecycle operations.

### Risks
Callers must pair reads with frees along all error paths. Function CIS can reference the card tuple list, so freeing in the wrong order can corrupt shared tuple tails.

### Test Signals
Compile and attach/remove tests for SDIO function discovery validate correct use of the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_io.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_io.c

### Purpose
`sdio_io.c` provides the exported SDIO function-driver API for claiming the host, enabling/disabling functions, setting block size, doing CMD52/CMD53 I/O, querying PM capabilities, setting suspend flags, and managing retuning around SDIO transactions.

### Important APIs, Types, And Functions
Exports include `sdio_claim_host()`, `sdio_release_host()`, `sdio_enable_func()`, `sdio_disable_func()`, `sdio_set_block_size()`, `sdio_align_size()`, `sdio_readb()`, `sdio_writeb()`, `sdio_writeb_readb()`, `sdio_memcpy_fromio()`, `sdio_memcpy_toio()`, `sdio_readsb()`, `sdio_writesb()`, `sdio_readw()`, `sdio_writew()`, `sdio_readl()`, `sdio_writel()`, `sdio_f0_readb()`, `sdio_f0_writeb()`, `sdio_get_host_pm_caps()`, `sdio_set_host_pm_flags()`, `sdio_retune_crc_disable()`, `sdio_retune_crc_enable()`, `sdio_retune_hold_now()`, and `sdio_retune_release()`. Internal helpers include `sdio_max_byte_size()`, `_sdio_align_size()`, and `sdio_io_rw_ext_helper()`.

### Control Flow
Function enable sets the function bit in `IOEx`, then polls `IORx` until ready or `func->enable_timeout`. Block size writes low/high FBR block-size bytes and updates `func->cur_blksize`. Bulk transfer helper chooses block mode when multi-block is supported and the transfer exceeds byte-mode limits, splits at host/card limits, then writes the remainder in byte mode; FIFO helpers use fixed address while memcpy helpers increment the address. Scalar 16/32-bit helpers marshal through `func->tmpbuf` in little-endian form. F0 writes are restricted to vendor CCCR range unless a card quirk allows lenient writes.

### State, Persistence, And Dependencies
State changes include function enable bits, FBR block-size registers, `func->cur_blksize`, host PM flags, host retune suppression fields, and card/host command state. Dependencies include SDIO ops CMD52/CMD53 helpers, MMC host/card structures, retune helpers, card quirks, and exported GPL symbols for function drivers.

### Integration Points
All SDIO function drivers depend on this API after binding through `sdio_bus.c`. `sdio_bus_probe()` uses `sdio_set_block_size()` before calling driver probe. `sdio_uart.c` uses claim/release, scalar I/O, enable/disable, and IRQ helpers.

### Risks
Most APIs assume the caller has claimed the host where documented; misuse can race with other functions or PM. `sdio_writeb_readb()` does not guard `func == NULL` unlike `sdio_readb()`/`sdio_writeb()`. `func->tmpbuf` serializes 16/32-bit helpers per function only if callers respect host claiming. Transfer splitting must honor `max_blk_count`, `max_blk_size`, multi-block support, byte-mode 512 quirks, and address-increment semantics. PM flags are ORed without locking based on serialized suspend callbacks.

### Test Signals
Exercise enable timeout, disable, default/custom block sizes, byte-mode 512 quirk, multi-block CMD53 splitting, FIFO versus incrementing address transfers, 8/16/32-bit endian reads/writes, F0 vendor-range enforcement, PM flag validation, and retune hold/CRC disable around noisy power-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_irq.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_irq.c

### Purpose
`sdio_irq.c` implements SDIO interrupt registration, dispatch, polling/threaded IRQ handling, workqueue signaling, and host IRQ enable/disable integration for SDIO function drivers.

### Important APIs, Types, And Functions
Exports are `sdio_signal_irq()`, `sdio_claim_irq()`, and `sdio_release_irq()`. Internal functions include `sdio_get_pending_irqs()`, `process_sdio_pending_irqs()`, `sdio_run_irqs()`, `sdio_irq_work()`, `sdio_irq_thread()`, `sdio_card_irq_get()`, `sdio_card_irq_put()`, and `sdio_single_irq_set()`.

### Control Flow
Claiming an IRQ reads `IENx`, enables the function bit plus master enable, records the handler, starts a kthread or enables host IRQs depending on host capabilities, and updates the single-IRQ fast path. The IRQ thread claims the host, processes pending interrupts, releases the host, backs off on errors, adapts polling frequency for non-SDIO-IRQ hosts, and enables host SDIO IRQs while sleeping. Workqueue mode handles `MMC_CAP2_SDIO_IRQ_NOTHREAD` by scheduling `sdio_irq_work()`. Dispatch skips suspended cards, optionally calls a single registered handler directly when an IRQ was signaled, otherwise reads `INTx` and invokes handlers for pending function bits. Release clears the handler, decrements host IRQ use, disables function/master bits when appropriate, and stops thread/host IRQs on the last user.

### State, Persistence, And Dependencies
State is in `host->sdio_irqs`, `host->sdio_irq_thread`, `host->sdio_irq_pending`, `host->sdio_irq_thread_abort`, `card->sdio_single_irq`, and each `func->irq_handler`. Hardware-visible state is in CCCR `IENx` and `INTx`, plus host controller SDIO IRQ enable/ack callbacks. Dependencies include kthreads, wait/scheduler APIs, CMD52 helpers, host/card quirks, and MMC host claim/release.

### Integration Points
Function drivers call this API while the host is claimed. `sdio_bus_remove()` warns and releases leaked handlers. `sdio.c` restarts IRQ processing after resume. Host drivers can either provide native SDIO IRQ signaling or rely on polling.

### Risks
Handlers run with the host already claimed and must not call `sdio_claim_host()` recursively. Single-IRQ fast path assumes a signaled IRQ maps to the only registered handler without reading `INTx`. Polling broken cards may need dummy reads to avoid fake interrupts. Suspend blocks processing and cancels work, but race windows around resume and pending flags must be tested. Last-user release must stop the kthread and disable host IRQs without leaving master enable set.

### Test Signals
Test native SDIO IRQ, no-native polling, NOTHREAD workqueue mode, one-function fast path, multiple function handlers, pending bit with missing handler/function, claim busy, release last handler, card suspend/resume with pending IRQs, and driver removal with leaked IRQ handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.c

### Purpose
`sdio_ops.c` implements low-level SDIO command helpers for CMD5, CMD52, CMD53, and SDIO reset. It is the transport layer below SDIO card attach and exported function-driver I/O APIs.

### Important APIs, Types, And Functions
The APIs are `mmc_send_io_op_cond()`, `mmc_io_rw_direct()`, `mmc_io_rw_extended()`, and `sdio_reset()`. `mmc_io_rw_direct_host()` is the host-based CMD52 helper used before a `struct mmc_card` exists.

### Control Flow
CMD5 polls up to 100 times with 10 ms delays unless probing with OCR zero, returning the R4 OCR from the SPI/native response slot. CMD52 validates function number and 17-bit address, encodes read/write and RAW flag, submits the command, decodes native R5 error/function/out-of-range bits, and returns the byte response. CMD53 validates address, builds block or byte mode arguments, maps the caller buffer into one or more scatterlist entries based on `host->max_seg_size`, submits pre/post request hooks around `mmc_wait_for_req()`, decodes command/data/R5 errors, and frees dynamic scatterlists. Reset reads CCCR_ABORT if possible, sets bit 3, and writes it back.

### State, Persistence, And Dependencies
The helpers mutate only command/request structures, host pre/post request state, and SDIO CCCR registers. Dependencies include scatterlists, SDIO/MMC constants, generic command submission, host limits, and card/host response layout helpers.

### Integration Points
`sdio.c` uses CMD5 and reset during attach/reinit. `sdio_io.c`, `sdio_cis.c`, `sdio_bus.c`, and `sdio_irq.c` build higher-level APIs on CMD52/CMD53.

### Risks
SPI response slots differ from native response slots. CMD53 scatterlist splitting by `max_seg_size` must match host DMA expectations and preserve buffer lifetime through pre/post hooks. Byte mode uses `blocks == 0` but sets `data.blocks` to 1 because host drivers expect at least one block. Reset before a card object exists depends on the host helper, not `mmc_card`.

### Test Signals
Exercise CMD5 probe and ready timeout, CMD52 invalid function/address and R5 errors, CMD53 byte and block mode, multi-segment DMA splitting, SPI/native response decoding, reset on cards that fail the initial abort read, and host pre/post request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.h

### Purpose
`sdio_ops.h` declares internal SDIO transport helpers and a small predicate for commands that keep SDIO I/O busy.

### Important APIs, Types, And Functions
It declares `mmc_send_io_op_cond()`, `mmc_io_rw_direct()`, `mmc_io_rw_extended()`, `sdio_reset()`, and `sdio_irq_work()`. The inline `sdio_is_io_busy()` returns true for CMD53 and for CMD52 operations except accesses to `SDIO_CCCR_ABORT` or `SDIO_CCCR_SUSPEND`.

### Control Flow
There is no standalone runtime flow beyond the inline predicate. The predicate decodes the address from command arguments and classifies SDIO I/O commands for host/core busy handling.

### State, Persistence, And Dependencies
No state is stored. It depends on `linux/types.h`, SDIO constants, and opaque `mmc_host`, `mmc_card`, and `work_struct`.

### Integration Points
SDIO attach, CIS parsing, IRQ handling, exported I/O APIs, and host/core request handling include this header for transport operations and busy classification.

### Risks
The inline predicate must stay aligned with SDIO command argument layout; incorrect classification can break retune, runtime PM, or command scheduling around SDIO I/O. Prototype changes affect many MMC core files.

### Test Signals
Compile coverage plus tests for CMD52 abort/suspend versus normal CMD52 and CMD53 paths validate the predicate and declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_uart.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_uart.c

### Purpose
`sdio_uart.c` is an SDIO function driver that exposes SDIO UART/GPS functions as Linux TTY devices named `ttySDIO*`. It implements a sleeping, SDIO-access-safe serial driver for 16550A-like register sets that cannot use the regular 8250 infrastructure.

### Important APIs, Types, And Functions
The key type is `struct sdio_uart_port`, which embeds `struct tty_port`, points to `struct sdio_func`, protects function lifetime with `func_lock`, stores IRQ recursion state, register offset, TX FIFO, write lock, modem/control state, error counters, UART clock, IER/LCR, and status masks. Major flows are `sdio_uart_probe()`, `sdio_uart_remove()`, `sdio_uart_init()`, `sdio_uart_exit()`, `sdio_uart_activate()`, `sdio_uart_shutdown()`, `sdio_uart_irq()`, RX/TX helpers, TTY operations, and modem/termios helpers.

### Control Flow
Module init allocates/registers a dynamic TTY driver, then registers an SDIO driver for UART and GPS classes. Probe currently rejects generic UART class as unsupported, parses GPS tuple 0x91/SUBTPL_SIOREG for register offset and clock, initializes a tty port, assigns a free port index, and registers a TTY device. Opening a tty activates the port: resets TX FIFO, claims SDIO host, enables the function, claims SDIO IRQ, clears FIFOs/interrupt status, initializes LCR/IER/modem state, applies termios, raises RTS/DTR when baud is nonzero, checks CTS flow control, clears TTY I/O error, and kicks the IRQ handler. IRQ handling reads IIR/LSR, drains RX into tty flip buffers, handles modem deltas, and transmits queued bytes. Shutdown disables RX/IRQs, clears modem control, flushes FIFOs, disables the function, and releases the host. Remove unregisters the tty device, nulls `port->func`, hangs up users, releases IRQ, disables the function, and drops references.

### State, Persistence, And Dependencies
State is in the global `sdio_uart_table`, per-port kfifo, tty references, SDIO function driver data, UART registers accessed via CMD52, modem counters, and TTY device nodes. Dependencies include SDIO core APIs, TTY core, kfifo, serial register constants, SDIO IDs/classes, module infrastructure, and tuple data provided by `sdio_cis.c`.

### Integration Points
The driver binds through `sdio_bus.c`, uses `sdio_io.c` and `sdio_irq.c`, and exposes standard tty operations to userspace. It depends on the MMC/SDIO core to supply function devices, tuple lists, host locking, and IRQ dispatch.

### Risks
SDIO register access can sleep, so all TTY callbacks must avoid spinlock-only assumptions. Lifetime is delicate: `port->func` is nulled under `func_lock` during removal while tty users may still hold port references. IRQ recursion is explicitly guarded with `in_sdio_uart_irq` because direct IRQ kicks can re-enter through tty echo/flow control. TX uses a page-sized kfifo and short 16-byte bursts, so throughput depends on IRQ cadence. Generic SDIO UART class returns `-ENOSYS`, leaving only GPS tuple-described devices usable. Modem delta reads may consume bits before `sdio_uart_check_modem_status()`, as noted by a FIXME.

### Test Signals
Test GPS-class probe with valid/invalid tuple 0x91, tty open/close/hangup, termios baud/format/flow-control changes, RX parity/frame/break/overrun handling, TX wakeup and XON/XOFF, CTS/DCD modem changes, removal while tty is open, IRQ recursion, suspend/remove through SDIO core, and unsupported UART-class binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/slot-gpio.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/slot-gpio.c

### Purpose
`slot-gpio.c` provides generic GPIO descriptor helpers for MMC slot card-detect and write-protect pins. It lets host drivers request CD/RO GPIOs, read them through MMC host ops, wire card-detect IRQs, configure wake, and fall back to polling.

### Important APIs, Types, And Functions
The private `struct mmc_gpio` stores CD/RO descriptors, labels, debounce, ISR, and IRQ number. Exported APIs are `mmc_gpio_alloc()`, `mmc_gpio_set_cd_irq()`, `mmc_gpio_get_ro()`, `mmc_gpio_get_cd()`, `mmc_gpiod_request_cd_irq()`, `mmc_gpio_set_cd_wake()`, `mmc_gpiod_request_cd()`, `mmc_gpiod_set_cd_config()`, `mmc_host_can_gpio_cd()`, `mmc_gpiod_request_ro()`, and `mmc_host_can_gpio_ro()`. The default IRQ handler is `mmc_gpio_cd_irqt()`.

### Control Flow
Host setup calls `mmc_gpio_alloc()` to allocate devm-managed context and labels. CD/RO request helpers acquire input descriptors, set debounce, adjust active-low polarity based on override and host caps, and store descriptors. `mmc_gpiod_request_cd_irq()` uses an explicit IRQ or `gpiod_to_irq()` unless polling is requested, installs a threaded edge IRQ, stores the result in `host->slot.cd_irq`, and sets `MMC_CAP_NEEDS_POLL` on failure. The default IRQ handler marks `host->trigger_card_event` and schedules debounced `mmc_detect_change()`. Read helpers use sleeping or non-sleeping GPIO access depending on descriptor capability. Wake toggles `enable_irq_wake()`/`disable_irq_wake()` when `MMC_CAP_CD_WAKE` is set.

### State, Persistence, And Dependencies
State is in `host->slot.handler_priv`, `host->slot.cd_irq`, `host->slot.cd_wake_enabled`, host caps, and devm-managed GPIO/IRQ resources. Dependencies include GPIO consumer descriptors, IRQ APIs, jiffies, MMC host structures, module exports, and pinconf-style GPIO config.

### Integration Points
Host drivers use this file to implement `get_cd`/`get_ro` host ops and to request card-detect IRQs before or after `mmc_add_host()`. The detection work feeds the MMC rescan path that eventually reaches SD/SDIO attach code.

### Risks
Calling request helpers without `mmc_gpio_alloc()` leaves `ctx` null; most read paths handle that, but config helpers assume a valid descriptor. Debounce fallback converts microseconds to milliseconds and can become zero for sub-millisecond values. Polarity toggling can be confusing when both `override_active_level` and `MMC_CAP2_CD_ACTIVE_HIGH` are used. IRQ failure silently forces polling, which changes detection latency and power behavior.

### Test Signals
Test CD/RO GPIO request success/failure, active-high and active-low polarity, debounce hardware support and fallback, card insert/remove IRQ scheduling, explicit platform IRQ, polling fallback, wake enable/disable, pin config, and hosts without CD/RO GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/slot-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/slot-gpio.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/core/slot-gpio.h

### Purpose
`slot-gpio.h` declares the internal allocation hook for the MMC core slot GPIO helper.

### Important APIs, Types, And Functions
It forward declares `struct mmc_host` and declares `mmc_gpio_alloc(struct mmc_host *host)`.

### Control Flow
There is no runtime logic. Host/core setup calls the allocation function before using the public GPIO helper APIs from `linux/mmc/slot-gpio.h`.

### State, Persistence, And Dependencies
No state is stored. The header keeps the private allocation contract separate from public GPIO helper declarations.

### Integration Points
Used by MMC host/core code that initializes `host->slot.handler_priv` for the exported slot GPIO helpers.

### Risks
If allocation is skipped, later helper calls may return `-ENOSYS`, force polling, or dereference missing context in less defensive paths.

### Test Signals
Compile coverage and host initialization tests should verify `mmc_gpio_alloc()` is called before CD/RO helpers are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/slot-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/Kconfig

### Purpose
`drivers/mmc/host/Kconfig` defines the configuration menu for MMC/SD/SDIO host controller drivers and related host-side features. It controls which host drivers and support layers are buildable for a kernel configuration.

### Important APIs, Types, And Functions
This is declarative Kconfig rather than C. Important symbols include generic/debug/support options such as `MMC_DEBUG`, `MMC_SDHCI`, `MMC_SDHCI_IO_ACCESSORS`, `MMC_SDHCI_UHS2`, `MMC_SDHCI_PLTFM`, `MMC_CQHCI`, `MMC_HSQ`, and `MMC_SDHCI_EXTERNAL_DMA`; bus/platform families such as PCI, ACPI, OF/platform SDHCI, DesignWare, TMIO/SDHI, SPI, USB, PCI readers, and many SoC-specific controllers; and test/support choices such as `MMC_SDHCI_OF_ASPEED_TEST`.

### Control Flow
Kconfig dependency and selection flow determines menu visibility and build graph. For example SDHCI derivatives depend on `MMC_SDHCI` or `MMC_SDHCI_PLTFM`; some select `MMC_CQHCI`, `MMC_HSQ`, `MMC_SDHCI_IO_ACCESSORS`, DMA helpers, clocks/regulators/regmap, or platform-specific support. Tristate symbols allow built-in or module host drivers, while bool helper symbols are selected by concrete drivers.

### State, Persistence, And Dependencies
The persistent artifact is the kernel `.config`, which feeds Makefile object selection and preprocessor conditionals. Dependencies encode architecture, bus, DMA, OF/ACPI, PCI/USB, regulator, clock, reset, GPIO, thermal, KUnit, and compile-test availability.

### Integration Points
The symbols here map directly to object rules in `drivers/mmc/host/Makefile` and to feature checks throughout host drivers. Core SD/SDIO behavior depends indirectly on selected host capabilities such as SDHCI, UHS-II, CQHCI, HSQ, DMA, GPIO, and retuning support.

### Risks
Incorrect `depends on` or `select` relationships can create impossible builds, missing helper objects, or drivers visible on unsupported platforms. Silent helper symbols such as `MMC_SDHCI_IO_ACCESSORS` and `MMC_SDHCI_EXTERNAL_DMA` are easy to misuse. Selecting CQHCI/HSQ/UHS2 changes interactions with core SD and SDIO attach paths, so host capabilities must match actual hardware.

### Test Signals
Run Kconfig/compile matrix coverage for allmodconfig, allyesconfig, randconfig, COMPILE_TEST, key architectures, SDHCI PCI/ACPI/OF, UHS-II, CQHCI/HSQ, KUnit ASPEED tests, and module versus built-in combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/Makefile -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/Makefile

### Purpose
`drivers/mmc/host/Makefile` maps MMC host Kconfig symbols to compiled object files and composite driver objects.

### Important APIs, Types, And Functions
The file contains kbuild object rules such as `obj-$(CONFIG_MMC_SDHCI) += sdhci.o`, platform-specific SDHCI objects, DesignWare objects, TMIO/SDHI objects, USB/PCI reader objects, CQHCI/HSQ objects, and SoC-specific drivers. Composite objects include `armmmci-y`, `sdhci-pci-y`, `octeon-mmc-objs`, `thunderx-mmc-objs`, `meson-mx-sdhc-objs`, `cqhci-y`, `cqhci-$(CONFIG_MMC_CRYPTO)`, and `sdhci-xenon-driver-y`.

### Control Flow
Kbuild includes objects when the corresponding `CONFIG_` symbol is `y` or `m`. Composite assignments collect multiple `.o` files into one module/built-in object. A small conditional adds `-DDEBUG` to `cb710-mmc` when `CONFIG_CB710_DEBUG=y`.

### State, Persistence, And Dependencies
The Makefile stores no runtime state. Its persistent outputs are built objects/modules determined by `.config`. It depends on Kconfig symbol names remaining synchronized with driver source files and module composition.

### Integration Points
This file is the build counterpart to host `Kconfig`. Selected host drivers provide `struct mmc_host_ops` and capabilities consumed by the SD/SDIO core files researched in this subset. Missing or stale object rules directly affect whether hardware support exists in the kernel image/modules.

### Risks
Symbol/object mismatches cause selected drivers not to build or stale objects to be referenced. Composite driver ordering and conditional additions must include all required companion files, such as PCI SDHCI vendor pieces, CQHCI crypto support, and Xenon PHY support. Duplicate or obsolete config names can hide build gaps until a specific config is tested.

### Test Signals
Validate with `make drivers/mmc/host/` under allmodconfig/allyesconfig/randconfig, module install checks for expected names, config-symbol-to-object audits, and targeted builds for composite drivers such as `sdhci-pci`, `cqhci`, `armmmci`, `sdhci-xenon-driver`, and Renesas SDHI variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/Makefile -->
