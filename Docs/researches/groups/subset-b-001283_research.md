# subset-b-001283 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scpi.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scpi.c

## Purpose
This file implements the ARM System Control and Power Interface mailbox protocol driver. It exposes a global `struct scpi_ops` through `get_scpi_ops()` so clock, DVFS, sensor, OPP, and device power-state consumers can call SCP firmware without knowing the mailbox/shared-memory framing. It supports both standard `arm,scpi` and legacy `arm,scpi-pre-1.0` firmware command layouts.

## Important APIs, Types, And Functions
Key state lives in `struct scpi_drvinfo`, which records protocol/firmware versions, command table, priority bitmap, channels, cached DVFS data, and exported ops. `struct scpi_chan` owns one mailbox channel, split TX/RX shared-memory windows, pending RX list, reusable transfer pool, token counter, and locks. `struct scpi_xfer` is the per-command transaction object.

The central path is `scpi_send_message()`: it selects a channel, allocates an xfer, packs command metadata, sends through `mbox_send_message()`, waits up to `MAX_RX_TIMEOUT`, maps SCPI status values to Linux errno, and returns the xfer to the pool. Firmware-facing callbacks are `scpi_tx_prepare()` and `scpi_handle_remote_msg()`, with `scpi_process_cmd()` matching replies by token/command for standard mode or FIFO head for legacy mode.

The exported operations include `scpi_clk_get_range()`, `scpi_clk_get_val()`, `scpi_clk_set_val()`, `scpi_dvfs_get_idx()`, `scpi_dvfs_set_idx()`, `scpi_dvfs_get_info()`, `scpi_dvfs_add_opps_to_device()`, sensor queries, and device power-state getters/setters. `scpi_probe()` wires device-tree mailboxes and `shmem` nodes, maps shared memory, initializes channels, selects legacy behavior, queries capabilities, and populates child devices.

## Control Flow, State, And Persistence
The driver is mostly stateless across boots, but it persists runtime state in the singleton `scpi_info`. DVFS information is lazily cached per domain in `scpi_info->dvfs[]` and freed on remove. Transfer objects are preallocated per channel and reused under `xfers_lock`; RX completions are coordinated with `rx_pending` under `rx_lock`. Standard mode round-robins channels with `atomic_t next_chan`; legacy mode uses a command-priority bitmap to choose channel 0 or 1.

## Dependencies And Integration Points
The file depends on mailbox, OF address parsing, platform bus, `dev_pm_opp`, spinlocks/mutexes/completions, and little-endian shared-memory structures. Integration points are device tree compatibles `arm,scpi`, `arm,scpi-pre-1.0`, SCP shared-memory compatibles, sysfs version attributes, and the `linux/scpi_protocol.h` consumer API.

## Risks And Test Signals
Primary risks are protocol mismatch, incorrect shared-memory sizing, reply timeout cleanup, and legacy command ordering. The driver mitigates malformed firmware responses with length clipping and zero-fill of short RX payloads, and maps unsupported legacy commands to `-EOPNOTSUPP`. Useful tests are DT probe with multiple channels, standard and legacy command framing, timeout removal from `rx_pending`, DVFS OPP sorting/removal on failure, and sensor 32-bit legacy value handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_sdei.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_sdei.c

## Purpose
This file implements the ARM Software Delegated Exception Interface core driver. It discovers an SDEI firmware conduit, exposes event registration/enabling APIs, handles CPU hotplug and power-management masking, integrates GHES notifications, and preserves event registrations across suspend, hibernate, reboot, and panic paths.

## Important APIs, Types, And Functions
`sdei_firmware_call` abstracts the SMCCC SMC/HVC conduit selected by `sdei_get_conduit()`. `struct sdei_event` tracks an event number, priority, type, and per-event registered callback argument storage. Shared events use a single `struct sdei_registered_event`; private events allocate one per CPU. `sdei_events_lock` serializes public API mutation; `sdei_list_lock` protects the event list and reregister/reenable flags.

Public kernel APIs include `sdei_event_register()`, `sdei_event_unregister()`, `sdei_event_enable()`, `sdei_event_disable()`, `sdei_mask_local_cpu()`, `sdei_unmask_local_cpu()`, `sdei_register_ghes()`, `sdei_unregister_ghes()`, `sdei_event_handler()`, and `sdei_handler_abort()`. Low-level firmware calls funnel through `invoke_sdei_fn()`, which converts SDEI status codes to Linux errno and returns `-EIO` when the interface is disabled.

## Control Flow, State, And Persistence
Probe chooses HVC/SMC from DT `method` or ACPI PSCI policy, reads the SDEI version, resets the platform, obtains the arch entry point, and registers CPU PM, reboot, and CPU hotplug callbacks. Event registration creates state, queries event info, registers either once for shared events or on all CPUs for private events, then marks `reregister`. Enabling similarly calls shared firmware once or cross-calls all CPUs and marks `reenable`.

Persistence is explicit in the `reregister` and `reenable` flags. Hibernate freeze unregisters private hotplug state and shared events without destroying their records; thaw/restore reregister and re-enable saved shared events and re-add CPU hotplug for private events. Reboot and panic paths mask CPUs and reset firmware. `sdei_handler_abort()` attempts to finish active normal/critical events before a crash kernel takes over.

## Dependencies And Integration Points
The file depends on SMCCC, CPU hotplug, CPU PM notifiers, ACPI SDEI table discovery, OF platform matching, GHES, per-CPU storage, and arch-provided SDEI entry/abort helpers. It registers as an `arch_initcall` platform driver with `arm,sdei-1.0`; ACPI creates a platform device from `ACPI_SIG_SDEI`.

## Risks And Test Signals
Risk concentrates around concurrency and firmware state drift: list mutation must respect mutex-then-spinlock ordering, private event registration must be symmetric across CPUs, and suspend/restore must not leave stale firmware registrations. Test signals include conduit selection, version rejection, shared/private register-enable-disable-unregister lifecycles, hotplug down/up reregistration, hibernate freeze/thaw, GHES priority callback selection, and disabled-interface `-EIO` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_sdei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/broadcom/Kconfig

## Purpose
This Kconfig file defines the build-time selection model for Broadcom firmware/data helpers under `drivers/firmware/broadcom`: bcm47xx NVRAM access, bcm47xx SPROM fallback synthesis, and a BNXT OP-TEE firmware manager.

## Important Symbols
`BCM47XX_NVRAM` is a bool enabled for BCM47XX, BCM_5301X, or compile testing. It describes a text-like `name=value` flash partition reader. `BCM47XX_SPROM` is a bool depending on `BCM47XX_NVRAM` and selecting `GENERIC_NET_UTILS`; it provides SPROM fallback data to SSB/BCMA for SoC devices whose board configuration is stored in CFE/NVRAM rather than device-local SPROM. `TEE_BNXT_FW` is a tristate depending on Broadcom iProc with OP-TEE or compile-test TEE, defaulting to `ARCH_BCM_IPROC`, and builds the BNXT trusted-app client.

## Control Flow, State, And Persistence
There is no runtime control flow. The file persists build policy by constraining which C objects can be compiled and whether code is builtin or modular. The NVRAM/SPROM options are bools because the code is used early and by built-in bus fallback registration. The BNXT firmware manager can be a module through the tee client driver model.

## Dependencies And Integration Points
The symbols align directly with the sibling Makefile targets. SPROM depends on NVRAM because it reads NVRAM keys to synthesize `struct ssb_sprom`; BNXT depends on OP-TEE/TEE infrastructure and platform architecture support. The help text is the first integration contract for kernel configurators and defconfig maintainers.

## Risks And Test Signals
Mis-specified dependencies can produce link-time failures or silently omit early platform data. Useful validation is `olddefconfig` coverage for BCM47XX and BCM_5301X, compile-test builds for all three symbols, and ensuring `BCM47XX_SPROM` cannot be selected without the NVRAM provider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/broadcom/Makefile

## Purpose
This Makefile maps Broadcom firmware Kconfig symbols to object files. It is the build glue for the local NVRAM, SPROM, and BNXT TEE implementations.

## Important Targets
`obj-$(CONFIG_BCM47XX_NVRAM) += bcm47xx_nvram.o`, `obj-$(CONFIG_BCM47XX_SPROM) += bcm47xx_sprom.o`, and `obj-$(CONFIG_TEE_BNXT_FW) += tee_bnxt_fw.o` are the only build rules. Their simplicity means the Kconfig symbols fully define whether each feature is compiled and whether it is linked built-in or as a module.

## Control Flow, State, And Persistence
There is no runtime state. Build state flows from Kconfig into kbuild object inclusion. Because `BCM47XX_NVRAM` and `BCM47XX_SPROM` are bools, their objects are built-in when selected; `TEE_BNXT_FW` follows tristate module semantics.

## Dependencies And Integration Points
The Makefile integrates with the parent firmware directory build. It assumes each object supplies its own module metadata or initcall, and that dependency correctness is handled by `Kconfig`.

## Risks And Test Signals
Risk is low, but target names must stay synchronized with source filenames and Kconfig symbols. Test signals are compile-test matrix builds for each symbol and checking that changing `TEE_BNXT_FW=m` produces `tee_bnxt_fw.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/bcm47xx_nvram.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/broadcom/bcm47xx_nvram.c

## Purpose
This file provides early Broadcom bcm47xx-style NVRAM access. It locates a flash NVRAM blob, copies it into a static RAM buffer, and exports simple lookup helpers for `name=value` variables, GPIO aliases, and full contents.

## Important APIs, Types, And Functions
`struct nvram_header` describes the flash header with magic `FLSH`, length, and SDRAM fields. `nvram_buf[NVRAM_SPACE]` and `nvram_len` are the global cached copy. Initialization paths are `bcm47xx_nvram_init_from_iomem()` for a known mapped NVRAM start, `bcm47xx_nvram_init_from_mem()` for an early physical flash window, and internal `nvram_init()` for an MTD partition named `nvram`.

Lookup APIs are `bcm47xx_nvram_getenv()`, `bcm47xx_nvram_gpio_pin()`, and `bcm47xx_nvram_get_contents()`. `bcm47xx_nvram_find_and_copy()` scans likely NVRAM locations at flash-size ends plus 4 KiB/1 KiB embedded fallbacks. `bcm47xx_nvram_copy()` bounds the header length to the backing resource and static buffer.

## Control Flow, State, And Persistence
The first successful initialization persists data in `nvram_buf` for the life of the kernel. Reinitialization returns `-EEXIST`. Consumers can call lookup functions without explicit initialization; they lazily call `nvram_init()`, which uses MTD when available. Variables are parsed by walking null-terminated strings after the header until an empty entry or buffer end.

## Dependencies And Integration Points
The file depends on IO mapping, MTD reads, `linux/bcm47xx_nvram.h`, and exported GPL/non-GPL symbols used by board, SPROM, and platform code. It intentionally supports very early calls before normal platform devices are available.

## Risks And Test Signals
Risks include trusting flash header length, scanning false-positive magic values, lazy MTD availability, and global unsynchronized initialization. The code clamps oversize copies and null-terminates the buffer, but does not validate CRC. Test signals are direct iomem init with valid/invalid magic, flash scanning offsets, duplicate init, MTD fallback, getenv exact-name matching, GPIO search over `gpio0`..`gpio31`, and contents allocation length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/bcm47xx_nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/bcm47xx_sprom.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/broadcom/bcm47xx_sprom.c

## Purpose
This file synthesizes SSB/BCMA SPROM board data from Broadcom NVRAM variables. It exists for SoC and PCI devices whose calibration, MAC, board flag, antenna, power, temperature, and regulatory data are stored in bootloader flash variables rather than readable device SPROM.

## Important APIs, Types, And Functions
The primary exported-like internal API is `bcm47xx_fill_sprom(struct ssb_sprom *sprom, const char *prefix, bool fallback)`. It uses helper readers generated by `NVRAM_READ_VAL()` plus custom readers for split 32-bit values, LED duty cycle, MAC addresses, and alpha2 country code. `bcm47xx_sprom_fill_auto()` contains the large revision-mask-to-field mapping table for `struct ssb_sprom`.

Bus integration is through `bcm47xx_get_sprom_ssb()` and `bcm47xx_get_sprom_bcma()` when the corresponding subsystems are built in. `bcm47xx_sprom_apply_prefix_alias()` maps verbose PCI prefixes to compact NVRAM aliases like `0:` using `devpathN`. `bcm47xx_sprom_register_fallbacks()` registers fallback callbacks at `fs_initcall`.

## Control Flow, State, And Persistence
SPROM filling starts by reading Ethernet and board data, then `sromrev`, alpha2, optional LED timing, revision-specific power-path fields, and finally the auto table. Prefixing allows separate PCI/SoC devices to read namespaced NVRAM keys, with optional fallback to unprefixed keys. `mac_addr_used` is global state used to derive unique wireless MACs from `et0macaddr` when Broadcom default `00:90:4c` placeholders are detected. `bcm47xx_sprom_registered` prevents duplicate fallback registration.

## Dependencies And Integration Points
The file depends on `bcm47xx_nvram_getenv()`, SSB, BCMA, PCI bus numbering, ethernet address helpers, and generic parsing utilities. It integrates with `ssb_arch_register_fallback_sprom()` and `bcma_arch_register_fallback_sprom()` only when those buses are built-in, matching the early fallback requirement.

## Risks And Test Signals
Risk is concentrated in the huge key mapping table, revision bitmasks, prefix fallback behavior, MAC derivation overflow, and partial/invalid NVRAM values. Parse failures warn and leave defaults untouched, so tests should validate representative SPROM revisions 2/4/5/8/9, PCI prefix aliases, SoC `sb/<core>/` fallback, MAC placeholder replacement, allset filtering, and both SSB/BCMA registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/bcm47xx_sprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/tee_bnxt_fw.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/broadcom/tee_bnxt_fw.c

## Purpose
This file is a TEE client driver for Broadcom BNXT firmware management. It opens an OP-TEE trusted application session, invokes a secure fastboot command for firmware loading, and provides a coredump-copy helper that transfers secure coredump data through shared memory.

## Important APIs, Types, And Functions
`struct tee_bnxt_fw_private` stores the global device, TEE context, session ID, and 4 MiB shared-memory pool. Public exported functions are `tee_bnxt_fw_load()` and `tee_bnxt_copy_coredump()`. `prepare_args()` initializes `tee_ioctl_invoke_arg` and `tee_param` arrays for `TA_CMD_BNXT_FASTBOOT` and `TA_CMD_BNXT_COPY_COREDUMP`. `tee_bnxt_fw_probe()` opens the OP-TEE context, opens a session using the UUID from the tee bus device ID, allocates shared memory, and stores global state. Remove and shutdown release the shared memory, session, and context.

## Control Flow, State, And Persistence
Probe establishes the only persistent runtime state in `pvt_data`. `tee_bnxt_fw_load()` checks the context and invokes command 0 with no parameters. `tee_bnxt_copy_coredump()` loops over the requested size in chunks no larger than the shared-memory pool, passes offset/size to the TA, maps the returned shared memory with `tee_shm_get_va()`, copies to the caller buffer, and advances offset.

## Dependencies And Integration Points
The file depends on the TEE client framework, OP-TEE implementation ID matching, UUID device matching, and `linux/firmware/broadcom/tee_bnxt_fw.h` consumers. It registers a `tee_client_driver` with UUID `6272636D-2019-0716-4243-4D5F53434849`.

## Risks And Test Signals
The global singleton means multiple matching devices would overwrite state; exported calls fail with `-ENODEV` before probe or after remove. Both TA invocation failures and nonzero TA return codes collapse to `-EINVAL`, which hides exact TA error semantics. Coredump copying relies on `void *` arithmetic and repeated shared-memory VA lookup. Tests should cover probe error unwinding, no-context exported calls, fastboot success/failure, chunked coredump copies larger than 4 MiB, remove/shutdown idempotence expectations, and OP-TEE-only context matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/broadcom/tee_bnxt_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/Kconfig

## Purpose
This Kconfig file defines the Cirrus DSP firmware support library and its KUnit test build switches. It separates the production DSP library from test utilities and the test suite.

## Important Symbols
`FW_CS_DSP` is a hidden tristate defaulting to `n`; client drivers select or depend on it to build `cs_dsp.o`. `FW_CS_DSP_KUNIT_TEST_UTILS` is a tristate for shared test helper objects. `FW_CS_DSP_KUNIT_TEST` is a visible KUnit option, depends on `KUNIT`, `REGMAP`, and `FW_CS_DSP`, defaults to `KUNIT_ALL_TESTS`, and selects the utility module.

## Control Flow, State, And Persistence
There is no runtime flow. The file persists build relationships: tests require the library and regmap, while helper utilities can be built independently for tests. Because `FW_CS_DSP` is hidden, production enablement is driven by users of the library rather than direct menu selection.

## Dependencies And Integration Points
The symbols map to the sibling Makefiles. Test utilities import the `FW_CS_DSP` namespace and are used by KUnit files under `drivers/firmware/cirrus/test`.

## Risks And Test Signals
The key risk is build skew: tests need helper symbols and the production namespace available. Validation should include `KUNIT_ALL_TESTS=y`, module/builtin combinations where possible, and compile testing with `REGMAP` disabled to ensure dependency exclusion works.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/Makefile

## Purpose
This Makefile builds the Cirrus DSP firmware support library and descends into the KUnit test directory.

## Important Targets
`obj-$(CONFIG_FW_CS_DSP) += cs_dsp.o` builds the production library. `obj-y += test/` always includes the test subdirectory in kbuild traversal, while the test subdirectory's own Makefile gates actual object inclusion on Kconfig test symbols.

## Control Flow, State, And Persistence
There is no runtime state. Build state flows from `CONFIG_FW_CS_DSP` into object inclusion and from parent traversal to the test Makefile.

## Dependencies And Integration Points
This file integrates with `drivers/firmware/cirrus/Kconfig` and with test module construction under `cirrus/test`. The unconditional test directory traversal keeps test object rules visible without forcing test compilation.

## Risks And Test Signals
Risk is limited to build-graph drift. Test with `FW_CS_DSP=n`, `FW_CS_DSP=y`, and KUnit-enabled configurations to confirm `cs_dsp.o` and test objects appear only under the intended symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/cs_dsp.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/cs_dsp.c

## Purpose
This file is the Cirrus Logic DSP firmware support library. It initializes ADSP1, ADSP2, and HALO DSP descriptors; loads `.wmfw` firmware and `.bin` coefficient files; creates coefficient controls; manages boot/run/stop/power-down/hibernate transitions; exposes DSP memory access helpers; logs bus/watchdog faults; and supports write-sequence editing.

## Important APIs, Types, And Functions
The internal `struct cs_dsp_ops` abstracts core-specific behavior: firmware format validation, memory region-to-register mapping, algorithm table setup, status logging, watchdog stopping, memory/core enablement, locking, and start/stop. Public exports include initialization (`cs_dsp_adsp1_init()`, `cs_dsp_adsp2_init()`, `cs_dsp_halo_init()`), lifecycle (`cs_dsp_adsp1_power_up()`, `cs_dsp_adsp1_power_down()`, `cs_dsp_power_up()`, `cs_dsp_run()`, `cs_dsp_stop()`, `cs_dsp_power_down()`, `cs_dsp_remove()`), controls (`cs_dsp_get_ctl()`, `cs_dsp_coeff_read_ctrl()`, `cs_dsp_coeff_write_ctrl()`, acked-control write helpers), memory (`cs_dsp_read_raw_data_block()`, `cs_dsp_read_data_word()`, `cs_dsp_write_data_word()`, `cs_dsp_remove_padding()`), diagnostics, chunk formatting, and write-sequence helpers.

Firmware parsing is split between `cs_dsp_load()` for WMFW regions and `cs_dsp_load_coeff()` for WMDR/bin coefficient blocks. Algorithm discovery reads DSP memory headers in `cs_dsp_adsp1_setup_algs()`, `cs_dsp_adsp2_setup_algs()`, or `cs_dsp_halo_setup_algs()` and creates `struct cs_dsp_alg_region` entries that coefficient controls use for base fixups.

## Control Flow, State, And Persistence
`cs_dsp_common_init()` initializes list heads, `pwr_lock`, names, client ops, and debugfs defaults. Power-up loads firmware, sets up algorithms, loads coefficients, initializes readable control caches, syncs dirty controls, and marks `booted`. `cs_dsp_run()` enables core, calls client pre-run, syncs controls, optionally locks memory/MPU, starts core, marks `running`, and calls post-run. `cs_dsp_stop()` signals firmware shutdown through host-event controls, stops watchdog, logs status, calls stop callbacks, clears `running`, and disables/stops core while preserving loaded memory. `cs_dsp_power_down()` disables memory, clears firmware IDs, disables controls, and frees algorithm regions.

Runtime state is kept in the caller-owned `struct cs_dsp`: `booted`, `running`, `hibernating`, firmware IDs/names, control list, algorithm-region list, memory map, regmap, and callbacks. Coefficient controls persist cached values and dirty state across stop/hibernate boundaries, with volatile controls requiring live hardware access.

## Dependencies And Integration Points
The library depends on regmap, firmware blobs described by `linux/firmware/cirrus/wmfw.h`, public `linux/firmware/cirrus/cs_dsp.h`, debugfs, KUnit static stubs, vmalloc, and client-provided `cs_dsp_client_ops`. Exports use namespace `FW_CS_DSP` for most APIs. Debugfs exposes boot/run/hibernate state, firmware IDs, loaded filenames, and parsed controls.

## Risks And Test Signals
Risk is high because file-format parsing writes directly to device memory. Important defenses include magic/version/core checks, overflow checks on region/block lengths, DMA-safe scratch buffers, and lock assertions on control paths. Remaining risks include off-by-one address conversion across packed/unpacked memories, stale dirty caches, callback error rollback, unsupported control flags, and write-sequence terminator corruption. Test signals are the extensive KUnit suite using mock WMFW/bin builders and mock regmaps, plus hardware tests for lifecycle, hibernate resync, bus/watchdog diagnostics, debugfs, long-offset coefficient blocks, and malformed firmware rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/cs_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/cs_dsp.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/cs_dsp.h

## Purpose
This private header provides local declarations for the Cirrus DSP driver implementation. At present it only exposes the KUnit-visible message-rate hook to sibling compilation units when KUnit is enabled.

## Important APIs, Types, And Functions
The header guard is `FW_CS_DSP_H`. Under `IS_ENABLED(CONFIG_KUNIT)`, it declares `bool cs_dsp_can_emit_message(void);`, implemented in `cs_dsp.c` as a KUnit-static-stub-capable rate-limit gate for noisy error-path tests. No structs or production-only APIs are declared here; public APIs are in `linux/firmware/cirrus/cs_dsp.h`.

## Control Flow, State, And Persistence
There is no state. Its only behavioral impact is compile-time: KUnit builds can reference or stub `cs_dsp_can_emit_message()`, while non-KUnit builds avoid exposing the declaration.

## Dependencies And Integration Points
The header is included by `cs_dsp.c` and potentially local test-aware code. It depends on Kconfig's `CONFIG_KUNIT` and the function's `VISIBLE_IF_KUNIT`/`EXPORT_SYMBOL_IF_KUNIT` implementation.

## Risks And Test Signals
Risk is low. The main signal is that KUnit builds compile and can redirect `cs_dsp_can_emit_message()`, while non-KUnit builds do not leak unnecessary symbols or declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/cs_dsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/Makefile

## Purpose
This Makefile assembles the Cirrus DSP KUnit utility module and KUnit test module from multiple object files.

## Important Targets
`cs_dsp_test_utils-objs` groups helper objects: mock memory maps, bin builder, mock regmap, utility module metadata, and wmfw builder. `cs_dsp_test-objs` groups the actual KUnit suites covering bin loading, bin errors, callbacks, control parsing/cache/read-write, wmfw loading, wmfw errors, and suite registration. `obj-$(CONFIG_FW_CS_DSP_KUNIT_TEST_UTILS)` and `obj-$(CONFIG_FW_CS_DSP_KUNIT_TEST)` gate final object inclusion.

## Control Flow, State, And Persistence
There is no runtime control flow in this file. It persists the test composition contract: utility helpers can be built separately and the full test module links all listed suites.

## Dependencies And Integration Points
The file integrates with `drivers/firmware/cirrus/Kconfig`, KUnit, and exported namespaces from `cs_dsp.c` plus `FW_CS_DSP_KUNIT_TEST_UTILS`.

## Risks And Test Signals
Object ordering and completeness matter because tests reference helper symbols. Build tests should ensure both utility-only and full-test configurations link, and that adding a test source updates this object list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_bin.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_bin.c

## Purpose
This file builds synthetic WMDR/bin coefficient firmware images for Cirrus DSP KUnit tests. It lets tests construct valid or intentionally malformed coefficient payloads without external firmware files.

## Important APIs, Types, And Functions
`struct cs_dsp_mock_bin_builder` tracks the KUnit test context, vmalloc buffer, write cursor, and bytes used. `cs_dsp_mock_bin_init()` creates the builder, writes a `WMDR` header with requested format and firmware version, and registers buffer cleanup. `cs_dsp_mock_bin_get_firmware()` wraps the buffer in a KUnit-allocated `struct firmware`.

Block-building APIs are `cs_dsp_mock_bin_add_raw_block()`, `cs_dsp_mock_bin_add_info()`, `cs_dsp_mock_bin_add_name()`, `cs_dsp_mock_bin_add_patch()`, and `cs_dsp_mock_bin_add_patch_off32()`. They populate `struct wmfw_coeff_item` fields, enforce payload alignment for patch helpers, pad text blocks to 4-byte boundaries, and support long-offset block types by setting the extended type bits.

## Control Flow, State, And Persistence
The builder appends blocks sequentially into a 32 KiB vmalloc buffer. KUnit assertions guard buffer overflow and invalid version widths. The produced `struct firmware` points directly at builder-owned memory, so it remains valid for the test lifetime through KUnit cleanup actions.

## Dependencies And Integration Points
The file depends on KUnit resource management, `linux/firmware.h`, public cs_dsp test utilities, and WMFW/WMDR structure definitions. It exports helper symbols in namespace `FW_CS_DSP_KUNIT_TEST_UTILS`.

## Risks And Test Signals
Risks include builder pointer arithmetic on void pointers, mismatch between helper `type` arguments and parser expectations, and text helper currently routing both name and info through an info block path. Test signals are KUnit cases that load name/info blocks, normal and long-offset patches, payload alignment failures, and malformed raw blocks for parser error coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_bin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_mem_maps.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_mem_maps.c

## Purpose
This file provides mock DSP memory maps and XM algorithm-header helpers for Cirrus DSP KUnit tests. It models ADSP2 16-bit, ADSP2 32-bit, and HALO address layouts closely enough for firmware loading, coefficient patching, packed-memory math, and algorithm discovery tests.

## Important APIs, Types, And Functions
It exports region arrays and size arrays for HALO, ADSP2 32-bit, and ADSP2 16-bit DSPs. Utility functions include `cs_dsp_mock_count_regions()`, `cs_dsp_mock_size_of_region()`, `cs_dsp_mock_base_addr_for_mem()`, register-block length conversion helpers, `cs_dsp_mock_has_zm()`, packed-to-unpacked mapping, and packed-register count conversion.

The XM-header builder path uses static template headers for HALO and ADSP2, `cs_dsp_create_mock_xm_header()`, `cs_dsp_mock_xm_header_write_to_regmap()`, `cs_dsp_mock_xm_header_get_alg_base_in_words()`, `cs_dsp_mock_xm_header_get_fw_version()`, and `cs_dsp_mock_xm_header_drop_from_regmap_cache()`. Internal add functions populate algorithm descriptor lists and write the `0xbedead` terminator.

## Control Flow, State, And Persistence
Most helpers are pure calculations against `struct cs_dsp_test` and the configured `dsp->mem` pointer. XM-header builders allocate KUnit-owned blob data, copy a template for the target DSP type, append algorithm entries with optional auto-allocation of base addresses, and later write the blob into the mock regmap. Cache-drop helpers remove expected registers so tests can detect unexpected dirty writes.

## Dependencies And Integration Points
The file depends on KUnit assertions, regmap access, WMFW structures, and public cs_dsp test utility types. It exports namespace `FW_CS_DSP_KUNIT_TEST_UTILS` and is linked into `cs_dsp_test_utils`.

## Risks And Test Signals
Risks are arithmetic mismatches between mock and production `region_to_reg()` logic, address-unit confusion between ADSP2 16-bit register indexes and HALO byte addresses, and auto-allocation off-by-one behavior. Tests should validate base lookup, block sizes for each memory type, packed/unpacked conversion, algorithm header write/drop/readback, firmware version extraction, and expected failures for unsupported DSP or memory types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_mem_maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_regmap.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_regmap.c

## Purpose
This file creates cache-only mock regmaps for Cirrus DSP KUnit tests. It models valid address ranges, value widths, endian behavior, register defaults, and dirty-cache detection without allowing real bus IO.

## Important APIs, Types, And Functions
The mock `regmap_bus` implements read/write/gather_write callbacks that fail the KUnit test if actual bus access occurs. It defines regmap configs for ADSP2 32-bit, ADSP2 16-bit, and HALO, including access tables, defaults, strides, endian formats, and max registers. Exported constants expose mock system/core base addresses.

Utility APIs include `cs_dsp_mock_regmap_drop_range()`, `cs_dsp_mock_regmap_drop_regs()`, `cs_dsp_mock_regmap_drop_bytes()`, `cs_dsp_mock_regmap_drop_system_regs()`, `cs_dsp_mock_regmap_is_dirty()`, and `cs_dsp_mock_regmap_init()`.

## Control Flow, State, And Persistence
`cs_dsp_mock_regmap_init()` selects a config from `dsp->type` and `dsp->rev`, creates a devm regmap, and switches it to cache-only mode so production code writes accumulate in cache. Dirty checking temporarily disables cache-only and calls `regcache_sync()`; any remaining dirty entry triggers the mock bus write path and sets `priv->saw_bus_write`.

## Dependencies And Integration Points
The file depends on KUnit, regmap, WMFW memory types, and `struct cs_dsp_test`. It integrates with mock memory maps and firmware builders by providing the backing regmap used by `cs_dsp` production code during tests.

## Risks And Test Signals
Risks include stale or incomplete address ranges causing false failures, default registers masking expected writes, and dirty-check helpers dropping too much or too little. Test signals should cover initialization for each DSP type/revision, cache-only enforcement, system-register drop behavior, dirty detection after expected and unexpected writes, and access denial for out-of-range addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_utils.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_utils.c

## Purpose
This tiny file supplies module metadata for the Cirrus DSP KUnit utility module. Its existence lets multiple helper objects link into a named module with the right license and namespace import.

## Important APIs, Types, And Functions
There are no functions or data definitions. The file declares `MODULE_DESCRIPTION`, `MODULE_AUTHOR`, `MODULE_LICENSE`, and `MODULE_IMPORT_NS("FW_CS_DSP")`.

## Control Flow, State, And Persistence
There is no runtime state or control flow. Its build-time effect is module metadata and namespace import for the aggregate `cs_dsp_test_utils` object.

## Dependencies And Integration Points
It depends only on `linux/module.h`. The namespace import integrates the utility module with production `FW_CS_DSP` exports used by helper and test objects.

## Risks And Test Signals
Risk is low but namespace imports are required for modpost correctness. Test signals are successful builds of `CONFIG_FW_CS_DSP_KUNIT_TEST_UTILS=m/y` without missing namespace warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_wmfw.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_wmfw.c

## Purpose
This file builds synthetic WMFW firmware images for Cirrus DSP KUnit tests. It supports firmware headers, info/data blocks, and algorithm coefficient metadata blocks across WMFW format versions so parser tests can exercise both valid and malformed firmware without external files.

## Important APIs, Types, And Functions
`struct cs_dsp_mock_wmfw_builder` tracks KUnit context, selected format version, vmalloc buffer, write cursor, bytes used, current algorithm block header, and coefficient count. `cs_dsp_mock_wmfw_init()` creates the builder, chooses a default format version when negative, allocates a 128 KiB buffer, and initializes ADSP2/HALO headers via `cs_dsp_init_adsp2_halo_wmfw()`. `cs_dsp_mock_wmfw_get_firmware()` returns a `struct firmware` wrapper.

Block APIs include `cs_dsp_mock_wmfw_add_raw_block()`, `cs_dsp_mock_wmfw_add_info()`, `cs_dsp_mock_wmfw_add_data_block()`, `cs_dsp_mock_wmfw_start_alg_info_block()`, `cs_dsp_mock_wmfw_add_coeff_desc()`, and `cs_dsp_mock_wmfw_end_alg_info_block()`. They encode v1 fixed-string algorithm data or v2/v3 variable-length string formats, count coefficients, and fill region lengths.

## Control Flow, State, And Persistence
The builder appends data sequentially. Algorithm-info construction is stateful: `start_alg_info_block()` reserves and writes the algorithm header, repeated `add_coeff_desc()` calls append descriptors and increment `num_coeffs`, and `end_alg_info_block()` backfills region length and coefficient count. KUnit cleanup owns the vmalloc buffer lifetime.

## Dependencies And Integration Points
The file depends on KUnit resources, WMFW structure definitions, mock memory-map helpers for sizes, `linux/firmware.h`, and exported test utility namespace `FW_CS_DSP_KUNIT_TEST_UTILS`. It is used by WMFW load and error tests for `cs_dsp_load()` and coefficient-control parsing.

## Risks And Test Signals
Risks include encoding mismatches with production parser expectations, format-version-specific string padding mistakes, unchecked NULL optional strings in some descriptor paths, and buffer size assumptions. Test signals include format v1/v2/v3 algorithm blocks, zero/long strings, multiple coefficients, data blocks for each memory type, header size validation, and malformed lengths/strings used by error-path suites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_wmfw.c -->
