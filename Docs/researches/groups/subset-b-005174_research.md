# Research: subset-b-005174

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/map.c -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/map.c

Purpose: implements AMD Address Translation Library DRAM map discovery and validation. It reads Data Fabric address-map registers for DF2, DF3, DF3.5, DF4, and DF4.5, finds the normalized-address map that contains the current address, and derives interleave properties needed by the later normalized-to-system translation path.

Important APIs and functions: the public entry point is `get_address_map(struct addr_ctx *ctx)`. It calls `get_address_map_common()`, `get_global_map_data()`, `dump_address_map()`, and `validate_address_map()`. Revision-specific helpers include `df2_get_dram_addr_map()`, `df3_get_dram_addr_map()`, `df4_get_dram_addr_map()`, `df4p5_get_dram_addr_map()`, and `df3_6ch_get_dram_addr_map()`. Interleave helpers include `get_intlv_mode()`, `get_num_intlv_chan()`, `get_intlv_bit_pos()`, `get_num_intlv_dies()`, `get_num_intlv_sockets()`, and `calculate_intlv_bits()`.

Control flow: `get_address_map_common()` first obtains the coherent-station fabric ID, searches DRAM offset registers for the active map, reads the map registers, validates the address range, and subtracts the normalized offset from `ctx->ret_addr`. Then `get_global_map_data()` decodes interleave mode, optional DF3 6-channel remap data, interleave bit position, die/socket counts, and total interleave bits. `validate_address_map()` rejects inconsistent combinations such as unsupported bit positions, die counts, socket counts, or invalid DF revision/mode encodings.

State and persistence: all state is transient in `ctx->map` and `ctx->ret_addr`; no persistent storage is used. Global hardware topology and revision data comes from `df_cfg`. Remap arrays are initialized to `0xff` before valid remap entries are populated because zero is a legal target.

Dependencies and integration: depends on `internal.h`, `reg_fields.h` masks, `df_indirect_read_instance()`, `df_indirect_read_broadcast()`, `FIELD_GET`, `order_base_2()`, and ATL debug helpers. It feeds downstream ATL translation and MI300 handling by producing a validated `dram_addr_map`.

Risks: register offsets and bit masks are highly revision-specific; a bad `df_cfg.rev` or heterogeneous MI300 flag changes shift widths and map-register locations. `find_normalized_offset()` assumes offsets are monotonic and nonzero when enabled. Unsupported interleave modes return errors; new hardware modes require updates in both field decoding and channel-count validation.

Test signals: exercise known DF2/DF3/DF4/DF4.5 systems, invalid map-valid bits, offset-disabled maps, monotonic offset violations, remap-enable paths, DF3 6-channel remap, MI300 heterogeneous offset shifts, and every interleave mode accepted by `get_num_intlv_chan()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/prm.c -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/prm.c

Purpose: provides ATL plumbing for ACPI Platform Runtime Mechanism address translation. It lets newer platforms or firmware-backed implementations translate a UMC normalized address to a system physical address without using the in-kernel DF register decoder.

Important APIs and types: `struct norm_to_sys_param_buf` is the packed PRM parameter buffer containing `norm_addr`, `socket`, `bank_id`, and an `out_buf` pointer. `prm_umc_norm_to_sys_addr(u8 socket_id, u64 bank_id, unsigned long addr)` is the only exported-in-file function and calls `acpi_call_prm_handler(norm_to_sys_guid, &p_buf)`.

Control flow: the function builds the PRM buffer on the stack, points `out_buf` at local `ret_addr`, and invokes the firmware handler. A zero return means `ret_addr` is valid and returned. `-ENODEV` is logged at debug level as absent PRM support; other failures emit a once-only notice and the negative error is returned as an unsigned long error value.

State and persistence: no persistent state is owned here. The function uses stack-local request and response storage. The handler GUID is defined in `system.c` as `norm_to_sys_guid`.

Dependencies and integration: includes `internal.h` and `<linux/prmt.h>`. Called by `convert_umc_mca_addr_to_sys_addr()` in `umc.c` before the software `norm_to_sys_addr()` fallback. It also supports PRM-only systems detected in `system.c`.

Risks: the PRM ABI relies on packed layout and firmware documentation, so field order and pointer validity are critical. A returned negative error is cast through `unsigned long`; callers must use `IS_ERR_VALUE()`. Stack output storage assumes the handler writes synchronously during `acpi_call_prm_handler()`.

Test signals: verify absent-handler `-ENODEV`, firmware failure notice throttling, successful handler output, PRM-only fallback behavior in `umc.c`, and ABI conformance on platforms with AMD PRMT support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/prm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/reg_fields.h -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/reg_fields.h

Purpose: centralizes Data Fabric register field masks used by ATL address translation. It documents revision-specific register names, access types, and bit ranges for coherent-station IDs, fabric masks, DRAM base/limit, offset, interleave, remap, socket, die, node, and hash-control fields.

Important definitions: masks include `DF2_COH_ST_FABRIC_ID`, `DF4p5_COH_ST_FABRIC_ID`, `DF3_COMPONENT_ID_MASK`, `DF4_COMPONENT_ID_MASK`, destination fabric ID masks, `DF_ADDR_RANGE_VAL`, `DF2_BASE_ADDR`, `DF4_BASE_ADDR`, `DF_DRAM_HOLE_BASE_MASK`, `DF2_DRAM_LIMIT_ADDR`, `DF4_DRAM_LIMIT_ADDR`, hash-control bits, high-address offset masks, interleave address/channel/die/socket masks, `DF_LOG2_ADDR_64K_SPACE0`, DF major/minor revision fields, node/socket/die masks and shifts, and DF4 remap controls.

Control flow: this header has no executable flow. Its macros are consumed by `system.c` to determine DF revision and ID masks, by `map.c` to decode address maps, and by translation logic elsewhere in ATL to interpret register fields consistently.

State and persistence: no state is held. It is compile-time metadata expressed with `GENMASK()` and `BIT()` macros.

Dependencies and integration: included through ATL internal headers. It depends on Linux bitfield conventions and assumes the associated register comments remain synchronized with AMD DF documentation. It is the contract between low-level register reads and semantic fields in `df_cfg` and `ctx->map`.

Risks: wrong masks silently corrupt address translation. Several fields vary by DF revision while sharing similar register names, so copy/paste mistakes are high impact. `DF4_HI_ADDR_OFFSET` deliberately includes reserved bits to follow reference code; future hardware changes may need more precise masking. The comments contain a likely duplicated DF3 destination fabric ID row, which is harmless to compilation but a documentation review signal.

Test signals: build coverage for all ATL users, register-decoding unit tests with synthetic values per DF revision, MI300 offset decoding, remap select decoding, and comparisons against platform reference address translations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/reg_fields.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/system.c -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/system.c

Purpose: discovers and caches system-wide AMD Data Fabric topology data for ATL. It determines the DF revision, node/socket/die/component masks and shifts, number of coherent-station maps, DRAM hole base, MI300 quirks, and PRM-only operation.

Important APIs and functions: exports `const guid_t norm_to_sys_guid` and provides `determine_node_id()` and `get_df_system_info()`. Revision helpers include `determine_df_rev()`, `determine_df_rev_legacy()`, `df4_determine_df_rev()`, `df*_get_masks_shifts()`, `df4_get_fabric_id_mask_registers()`, `get_num_maps()`, `apply_node_id_shift()`, and `get_dram_hole_base()`.

Control flow: `get_df_system_info()` calls `determine_df_rev()`. Pre-DF4 detection probes legacy mask registers, DF4+ detection reads major/minor revision and device/vendor IDs. Zen4 server applies a socket-shift quirk. MI300 marks the platform heterogeneous and calls `get_umc_info_mi300()`. Unsupported future DF revisions require PRM handler availability and set `df_cfg.flags.prm_only`. Non-PRM paths then normalize ID shifts, set map count, read DRAM hole base, and dump the resulting config.

State and persistence: updates the global `df_cfg` cache. No durable persistence exists; data is collected at module/system initialization and reused by translation paths. `determine_df_rev()` is idempotent once `df_cfg.rev` is no longer `UNKNOWN`.

Dependencies and integration: uses DF indirect read helpers, masks from `reg_fields.h`, `<linux/prmt.h>`, AMD CPU/device IDs, ACPI PRM availability checks, and `get_umc_info_mi300()` from `umc.c`. Its output is consumed by `map.c`, `umc.c`, and the ATL decoder.

Risks: failed DF reads leave revision unknown and prevent software translation. The ID-shift quirk rewrites masks aggressively for a specific device ID. PRM-only systems require firmware handler support. MI300 initialization depends on SMN reads in `umc.c`.

Test signals: boot on DF2/DF3/DF3.5/DF4/DF4.5, Zen4 server quirk systems, MI300 systems, PRM-only future systems, PRM-absent failure, DRAM-hole read failure warning, and invalid socket/die inputs to `determine_node_id()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/umc.c -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/umc.c

Purpose: handles UMC-specific address translation inputs, especially MI300. It maps MCA UMC error addresses and IPIDs to normalized addresses, coherent-station instances, socket/die IDs, and ultimately system physical addresses. It also supports MI300 DRAM row retirement.

Important APIs and functions: `get_umc_info_mi300()` caches MI300 hash and bit-placement registers. `convert_umc_mca_addr_to_sys_addr(struct atl_err *err)` is the main translation entry used via RAS ATL registration. `amd_retire_dram_row(struct atl_err *a_err)` is exported. Important helpers include `get_coh_st_inst_id_mi300()`, `convert_dram_to_norm_addr_mi300()`, `_retire_row_mi300()`, `retire_row_mi300()`, `get_die_id()`, `get_coh_st_inst_id()`, and `get_addr()`.

Control flow: MI300 initialization reads UMC address hash, address configuration, column selection, and address selection registers from node 0 UMC 0, then stores decoded XOR and bit-shift values globally. For translation, the function derives socket from topology, die from topology or MI300 IPID high bits, coherent-station ID from IPID or MI300 map, and normalized address from MCA_ADDR or MI300 DRAM reconstruction. It tries PRM first and falls back to software `norm_to_sys_addr()` unless the platform is PRM-only.

State and persistence: `addr_hash` and `bit_shifts` are global runtime caches. No persistent storage is owned. Row retirement mutates the input address while iterating column permutations and row bit 13.

Dependencies and integration: depends on SMN register reads, topology helpers, page lookup, `memory_failure()`, PRM wrapper in `prm.c`, DF config from `system.c`, and the software ATL translation path.

Risks: MI300 tables and bit shifts are hardware-specific. `WARN_ON_ONCE()` catches unknown UMC IDs but still returns an index value. Row retirement can be expensive because it checks all column permutations twice. PRM return handling must distinguish valid high physical addresses from error values.

Test signals: MI300 SMN-read failure, known MI300 IPID-to-coherent-station mappings, hash enabled/disabled conversions, PRM success, software fallback, PRM-only failure, invalid/offline pages during row retirement, and duplicate row-bit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/umc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/fmpm.c -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/fmpm.c

Purpose: implements AMD FRU Memory Poison Manager. It records MI300 memory poison descriptors in CPER records stored through ACPI ERST, replays saved poison records at boot, retires affected DRAM rows, and exposes a debugfs view of FRU entries and translated system physical addresses.

Important APIs and types: core structures are `cper_sec_fru_mem_poison`, `cper_fru_poison_desc`, and packed `fru_rec`. Module entry and exit are `fru_mem_poison_init()` and `fru_mem_poison_exit()`. Key functions include `update_record_on_storage()`, `get_saved_records()`, `save_new_records()`, `update_fru_record()`, `fru_handle_mem_poison()`, `retire_mem_records()`, `save_spa()`, `fmpm_show()`, and `setup_debugfs()`. The module parameter `max_nr_entries` sizes each FRU record.

Control flow: init gates on AMD family 0x19, MI300A model range, PPIN support, ERST availability, and package count. It allocates one record per FRU/socket, initializes FRU metadata from CPU CPUID and PPIN, loads matching persistent records, writes new or grown records, creates `ras/fmpm/entries`, retires saved rows, and registers an MCE notifier. On memory-error notification, it retires the row, finds a FRU by PPIN, filters duplicates, appends a descriptor if capacity allows, translates and caches SPA, recalculates checksum, and writes the CPER record to ERST.

State and persistence: `fru_records` and `spa_entries` are runtime caches; ERST CPER records are persistent. `fmpm_update_mutex` serializes record updates and debugfs reads. Saved records with invalid checksum or absent FRU are cleared.

Dependencies and integration: uses x86 MCE notifier chain, CPER helpers, ERST, AMD topology/PPIN, ATL row retirement and address conversion, and RAS debugfs root.

Risks: ERST write failure fails init for new records or loses updates later. Fixed MI300 assumptions limit portability. `max_nr_entries` bounds descriptors; overflow only warns. Persistent records larger than current configuration force `-EINVAL`. Boot-time retirement occurs after dependencies initialize, leaving an early exposure window.

Test signals: ERST unavailable, invalid CPER checksum clearing, record growth, duplicate descriptor filtering with masked column/row13 bits, capacity overflow, debugfs formatting, notifier handling of non-memory errors, saved-record replay, and cleanup on failed init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/fmpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/cec.c -->
# sources/distributed-fs/ceph-client/drivers/ras/cec.c

Purpose: implements the RAS Correctable Errors Collector. It counts correctable DRAM errors per page frame, applies decay to approximate recency, and soft-offlines pages whose correctable error count reaches a configurable threshold.

Important APIs and functions: internal state is `struct ce_array ce_arr`, backed by one page of sorted `u64` entries. Main functions are `cec_add_elem()`, `cec_notifier()`, `do_spring_cleaning()`, `find_elem()`, `del_lru_elem_unlocked()`, `create_debugfs_nodes()`, and `cec_init()`. Boot option parsing is via `parse_cec_param()`.

Control flow: late init allocates the page array, creates debugfs controls under `ras/cec`, schedules delayed decay work, and registers an MCE notifier. The notifier only handles correctable memory errors with usable addresses. `cec_add_elem()` inserts or refreshes a PFN, sets max decay generation, increments count, soft-offlines through `memory_failure_queue()` when threshold is reached, otherwise triggers cleaning when enough updates have accumulated. Periodic work decays all entries and reschedules itself.

State and persistence: all collector data is volatile in `ce_arr`. `ce_mutex` protects the array, counters, threshold, and decay interactions. Debugfs knobs hold `decay_interval`, `action_threshold`, and optional debug insertion PFN. There is no persistence across reboot.

Dependencies and integration: uses x86 MCE helpers, RAS debugfs root, workqueues, memory failure infrastructure, and kernel debugfs attributes. `parse_ras_param()` in `ras.c` delegates `ras=cec_disable` handling here when enabled.

Risks: the page-sized array is intentionally simple but does O(n) memmove/delete. `del_lru_elem_unlocked()` returns `PFN(ca->array[min_idx])` after deletion, which is only diagnostic but worth review because the entry was shifted. Threshold setter stores the raw debugfs value before clamping the global action threshold. Intel defaults threshold to 2, which changes behavior by vendor.

Test signals: boot with `ras=cec_disable`, debugfs threshold and decay bounds, manual PFN insertion when `CONFIG_RAS_CEC_DEBUG`, duplicate PFN count increments, full-array eviction, threshold soft-offline, invalid PFN warning, and delayed decay rescheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/ras/debugfs.c

Purpose: provides the shared RAS debugfs root and a lightweight userspace-consumer signal. Other RAS components use this root for their own debugfs directories, and `ras_userspace_consumers()` reports whether the daemon trace file is open.

Important APIs and functions: `ras_get_debugfs_root()` returns the global root dentry. `ras_userspace_consumers()` returns `trace_count`. `ras_debugfs_init()` creates the top-level `ras` directory. `ras_add_daemon_trace()` creates the `daemon_active` file. `trace_open()` increments and `trace_release()` decrements the atomic count around a trivial `single_open()` file.

Control flow: `ras_init()` in `ras.c` calls `ras_debugfs_init()` before `ras_add_daemon_trace()`. Consumers such as CEC and FMPM call `ras_get_debugfs_root()` and skip debugfs setup if it returns NULL. Opening `daemon_active` does not emit content but marks an active userspace consumer until release.

State and persistence: state is process/runtime-only: `ras_debugfs_dir` and atomic `trace_count`. Nothing is persisted. The count is robust to concurrent open/release through atomics.

Dependencies and integration: depends on debugfs, seq_file helpers, and `linux/ras.h`. Exports functions for modules through GPL symbols. The header provides a stub only for the root getter when debugfs is disabled.

Risks: `ras_add_daemon_trace()` only checks `IS_ERR(fentry)` and not NULL, while many debugfs APIs return NULL for disabled or failed creation. A missing root returns `-ENOENT`, causing `ras_init()` to propagate failure. The empty read file is a presence/usage signal, not a data source.

Test signals: boot with debugfs enabled/disabled, verify `/sys/kernel/debug/ras/daemon_active`, concurrent opens and closes updating `ras_userspace_consumers()`, module users seeing NULL root gracefully, and init failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/ras/debugfs.h

Purpose: declares the RAS debugfs root accessor with a no-debugfs fallback. It is the small integration header used by RAS subcomponents that want to add debugfs files without directly owning the top-level root.

Important APIs: when `CONFIG_DEBUG_FS` is enabled, it declares `struct dentry *ras_get_debugfs_root(void)`. Otherwise it provides a static inline stub returning NULL.

Control flow: none beyond compile-time selection. Callers should test the returned pointer and skip debugfs creation when NULL.

State and persistence: no state is stored in the header. Runtime root state lives in `debugfs.c`.

Dependencies and integration: includes `<linux/debugfs.h>`. Used by `cec.c`, `amd/fmpm.c`, and other RAS code that creates debugfs nodes under `/sys/kernel/debug/ras`.

Risks: the header only stubs `ras_get_debugfs_root()`, not `ras_userspace_consumers()` or setup helpers; code using those must be guarded elsewhere. Callers that assume a non-NULL root will fail on kernels without debugfs.

Test signals: compile with and without `CONFIG_DEBUG_FS`, verify callers handle NULL root, and build modules that include the header without pulling debugfs-only symbols into no-debugfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/ras.c -->
# sources/distributed-fs/ceph-client/drivers/ras/ras.c

Purpose: provides core RAS initialization, tracepoint exports, ARM and non-standard CPER event logging, AMD ATL decoder indirection, and boot parameter routing for RAS features.

Important APIs and functions: when `CONFIG_AMD_ATL` is enabled, `amd_atl_register_decoder()`, `amd_atl_unregister_decoder()`, and `amd_convert_umc_mca_addr_to_sys_addr()` manage a global function pointer for AMD UMC normalized-address translation. `log_non_standard_event()` and `log_arm_hw_error()` export trace logging helpers. `ras_init()` initializes debugfs and daemon trace support. `parse_ras_param()` routes setup arguments such as CEC disable.

Control flow: AMD ATL registers a decoder callback once loaded; callers receive `-EINVAL` if no decoder is installed. Tracepoint definitions are created by defining `CREATE_TRACE_POINTS` before including `ras_event.h`. ARM CPER logging computes processor error info, context info, vendor-specific error data length, validates section length, maps MPIDR to logical CPU, and emits `trace_arm_event()`.

State and persistence: only the AMD decoder function pointer is mutable long-lived state. Debugfs state is initialized through `debugfs.c`. No persistent records are written here.

Dependencies and integration: uses Linux RAS trace events, CPER ARM structures, uuid/guid support, optional AMD ATL, optional ACPI extlog tracepoint exports, and CEC parameter parsing when configured.

Risks: the decoder pointer is not synchronized; comments assume it should never be unset except testing/debug, but unregister sets it NULL. ARM section parsing depends on firmware-provided lengths and clamps negative vendor data length after warnings. `ras_init()` returns debugfs daemon trace setup errors, so debugfs behavior can affect subsystem init status.

Test signals: ATL absent/present conversion, register/unregister behavior, ARM CPER records with short section lengths, non-standard event trace emission, `ras=cec_disable`, tracepoint symbol availability under extlog configs, and debugfs init return handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/88pg86x.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/88pg86x.c

Purpose: implements a simple I2C regulator driver for Marvell 88PG867/88PG868 two-buck converters. It registers two voltage regulators using regmap-backed voltage selector operations.

Important APIs and data: `pg86x_ops` uses `regulator_set_voltage_sel_regmap()`, `regulator_get_voltage_sel_regmap()`, and `regulator_list_voltage_linear_range()`. `pg86x_buck1_ranges` and `pg86x_buck2_ranges` describe selector-to-voltage mappings, including zero-volt reserved/off ranges. `pg86x_regulators[]` defines buck names, OF matches, selector registers `0x24` and `0x13`, masks, and voltage counts. `pg86x_i2c_probe()` initializes regmap and registers both regulators.

Control flow: the I2C driver probes asynchronously, creates an 8-bit register/8-bit value regmap, then loops over both descriptors and calls `devm_regulator_register()`. Any regmap or registration failure aborts probe.

State and persistence: the driver owns no private mutable state beyond devm-managed regmap/regulator devices. Hardware register state is managed through the regulator framework and I2C regmap; no suspend or persistent behavior is implemented.

Dependencies and integration: depends on I2C, OF match strings `marvell,88pg867` and `marvell,88pg868`, `REGMAP_I2C`, and regulator core. Kconfig selects `REGMAP_I2C`; Makefile maps `CONFIG_REGULATOR_88PG86X` to `88pg86x.o`.

Risks: `struct regulator_config config` never sets `config.regmap`, so regmap-backed ops depend on regulator core drvdata/regmap setup that appears missing in this file. The local `regmap` variable is initialized but not attached to config. No enable/disable ops are provided despite chip help mentioning separate enable pins.

Test signals: probe on both compatibles, verify `set_voltage_sel` reaches hardware, check regulator registration fails cleanly, inspect sysfs voltage table boundaries, and confirm whether missing `config.regmap` breaks voltage operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/88pg86x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/88pm800-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/88pm800-regulator.c

Purpose: registers buck and LDO regulators for the Marvell 88PM800 PMIC through the regulator framework, using the parent 88pm80x MFD power regmap.

Important APIs and data: `struct pm800_regulator_info` wraps a `regulator_desc` and max current. Macros `PM800_BUCK()` and `PM800_LDO()` build descriptors for five bucks and nineteen LDOs. Ops are split into `pm800_volt_range_ops` for buck linear ranges and `pm800_volt_table_ops` for LDO voltage tables. `pm800_get_current_limit()` exposes static current limits. `pm800_regulator_probe()` registers all or board-selected regulators.

Control flow: probe obtains parent `pm80x_chip` and optional platform data. If platform data declares regulators, it validates that non-NULL entries match `num_regulators` and only registers those entries. Otherwise it registers all IDs from `PM800_ID_RG_MAX`. It sets `config.dev` to `chip->dev`, `config.regmap` to `chip->subchip->regmap_power`, and `config.driver_data` to the descriptor wrapper before each registration.

State and persistence: descriptors and voltage tables are static. The driver has no runtime cache beyond regulator devices. Hardware enable and voltage state lives in PMIC registers via regmap.

Dependencies and integration: depends on MFD `88pm80x`, platform driver name `88pm80x-regulator`, regulator core, optional platform init data, OF regulator matching under `regulators`, and Makefile/Kconfig `CONFIG_REGULATOR_88PM800`.

Risks: board-data path indexes `pdata->regulators` and `pm800_regulator_info` by PM800 IDs; mismatched enum/table ordering would register wrong rails. `config.init_data` is not reset to NULL after a selected platform-data regulator, though the loop skips NULL entries in that path. Voltage/current limits are static and require datasheet accuracy.

Test signals: all-regulator registration, board-data subset registration, invalid `num_regulators`, buck voltage range endpoints, LDO table selectors, enable bit operations across enable registers, and current limit reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/88pm800-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/88pm8607.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/88pm8607.c

Purpose: supports Marvell 88PM8607 voltage regulators and 88PM8606 preregulator registration. It maps many table-based buck/LDO selectors to regulator framework operations and handles a BUCK3 slope-doubling quirk.

Important APIs and data: `struct pm8607_regulator_info` stores a descriptor, suspend voltage table pointer, and `slope_double`. Voltage tables cover BUCK1-3 and LDO1-14 variants with matching suspend tables. `pm8607_list_voltage()` wraps `regulator_list_voltage_table()` and doubles returned values for the BUCK3 quirk. Descriptor macros `PM8607_DVC()`, `PM8607_LDO()`, and `PM8606_PREG()` define regulators. `pm8607_regulator_probe()` selects the descriptor by platform resource or the PREG fallback.

Control flow: probe reads an `IORESOURCE_REG` resource. If present, it matches `res->start` to a PM8607 descriptor `vsel_reg`; if absent, it selects the single PM8606 PREG descriptor. For PM8607 BUCK3 with `chip->buck3_double`, it sets `slope_double`. It then chooses the main or companion regmap by chip ID, applies optional platform init data, registers one regulator, and stores the selected info as platform data.

State and persistence: static descriptor arrays and voltage tables define behavior. `slope_double` is mutable in the static descriptor entry, so it persists across device lifetime and would be shared if multiple devices existed. Hardware state is in PMIC registers.

Dependencies and integration: depends on `MFD_88PM860X=y`, platform devices created by the MFD core, resource-based regulator selection, regulator core regmap ops, and `subsys_initcall()` registration.

Risks: resource matching by register address is fragile if MFD resources drift. Static mutation of `slope_double` is not per-device. Several voltage tables contain zeros or repeated max values, so consumers must tolerate unavailable selectors. PREG is a current regulator with inverted enable semantics.

Test signals: PM8607 per-resource probe, PM8606 PREG probe without resource, BUCK3 double slope, main versus companion regmap selection, invalid resource address, table voltage listing with zeros/repeats, and enable/apply-bit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/88pm8607.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/88pm886-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/88pm886-regulator.c

Purpose: registers regulators for the Marvell 88PM886 PMIC. It creates a regulator-page I2C dummy client, initializes a regmap for that page, and registers sixteen LDOs plus five buck regulators.

Important APIs and data: `pm886_regulator_regmap_config` defines 8-bit registers/values and max register. Ops are split into table-based `pm886_ldo_ops` and linear-range `pm886_buck_ops`. Voltage tables `pm886_ldo_volt_table1/2/3` and buck ranges define selectors. `pm886_regulators[]` holds descriptors with OF matches, enable registers/masks, voltage select registers, and masks. `pm886_regulator_probe()` performs all registration.

Control flow: probe retrieves the parent `pm886_chip`, creates a dummy I2C device at the regulator page offset, initializes an I2C regmap for that page, sets `rcfg.regmap` and parent device, then iterates over every descriptor and registers it. `dev_err_probe()` is used for deferred or direct errors.

State and persistence: there is no private per-regulator mutable state. The dummy I2C client, regmap, and regulator devices are devm-managed. PMIC register contents hold actual enable/voltage state.

Dependencies and integration: depends on the 88PM886 MFD parent, I2C adapter/addressing, regulator core, regmap I2C, platform driver ID `88pm886-regulator`, Kconfig `REGULATOR_88PM886`, and Makefile object mapping.

Risks: the descriptor array omits explicit `.id` and `.owner`; modern regulator core can work without owner, but missing IDs may affect diagnostics or board constraints expecting numeric IDs. A failed dummy page client prevents all regulators. The code assumes `chip->client->addr + PM886_PAGE_OFFSET_REGULATORS` is valid on the bus.

Test signals: probe with valid and failing dummy I2C page, registration of all 21 rails, OF child matching under `regulators`, LDO selector masks and tables, buck range endpoints, enable masks across LDO_EN1/LDO_EN2/BUCK_EN, and deferred parent readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/88pm886-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/regulator/Kconfig

Purpose: defines the configuration menu for the Linux regulator subsystem and individual regulator drivers in this source tree. It controls whether the core framework, debug support, helper features, userspace consumers, netlink events, and vendor-specific drivers are built in, modular, or unavailable.

Important entries: top-level `menuconfig REGULATOR` selects `LINEAR_RANGES` and gates the entire file. Relevant entries for this work item include `REGULATOR_88PG86X`, `REGULATOR_88PM800`, `REGULATOR_88PM8607`, `REGULATOR_88PM886`, `REGULATOR_AAT2870`, and `REGULATOR_AB8500`. Each declares dependencies on its parent bus or MFD, for example I2C plus `REGMAP_I2C`, `MFD_88PM800`, `MFD_88PM860X=y`, `MFD_88PM886_PMIC`, `MFD_AAT2870_CORE`, or `AB8500_CORE`.

Control flow: Kconfig evaluation exposes entries only when dependencies are met. `if REGULATOR` scopes all child symbols so individual drivers cannot be selected without regulator framework support. `select` pulls helper libraries where needed, while `depends on` prevents incompatible builds.

State and persistence: Kconfig state persists in kernel build configuration files such as `.config`, not at runtime. It directly drives Makefile object selection.

Dependencies and integration: tightly paired with `drivers/regulator/Makefile` object lines and with parent subsystem Kconfig symbols in MFD, I2C, OF, GPIO, thermal, SPMI, and architecture menus. Help text documents module names and hardware capabilities for users configuring kernels.

Risks: incorrect dependencies can create build failures or hide valid compile-test coverage. `REGULATOR_88PM8607` requires `MFD_88PM860X=y`, preventing modular parent combinations. Help text typos do not affect builds but can mislead users. New drivers require synchronized Kconfig and Makefile changes.

Test signals: `olddefconfig` and `allmodconfig` coverage, selecting each work-item symbol with and without dependencies, module/built-in combinations, compile-test visibility where intended, and verifying object files appear only for enabled symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/Makefile -->
# sources/distributed-fs/ceph-client/drivers/regulator/Makefile

Purpose: maps regulator Kconfig symbols to object files and core framework components for kbuild. It is the build integration point for all regulator drivers in this tree.

Important entries: `obj-$(CONFIG_REGULATOR)` builds core framework objects such as `core.o`, `dummy.o`, `helpers.o`, `devres.o`, and `irq_helpers.o`. `obj-$(CONFIG_OF)` adds `of_regulator.o`. Work-item mappings include `88pg86x.o`, `88pm800-regulator.o`, `88pm8607.o`, `88pm886-regulator.o`, `aat2870-regulator.o`, and `ab8500-ext.o ab8500.o`. `ccflags-$(CONFIG_REGULATOR_DEBUG) += -DDEBUG` enables debug compilation.

Control flow: kbuild expands each `obj-$()` line based on the final Kconfig value. Built-in symbols produce built-in objects; modular symbols produce module objects. Multiple objects on one line, such as `REGULATOR_AB8500`, are linked together under the same config decision.

State and persistence: no runtime state. Build products are generated according to `.config`.

Dependencies and integration: must remain synchronized with Kconfig symbols and source filenames. Core objects are prerequisites for individual drivers through regulator framework APIs. Some object names differ from config names, making this file the authoritative mapping.

Risks: stale or missing object entries make selected drivers silently absent from builds. The line `obj-$(CONFIG_REGULATOR_MT6315)  += mt6316-regulator.o` appears suspicious because there is a separate `REGULATOR_MT6316` Kconfig entry; this could build MT6316 under the wrong symbol. Multi-object config lines require both source files to compile for a symbol.

Test signals: inspect `make V=1` object selection for each relevant config, build `REGULATOR_AB8500` to ensure both `ab8500-ext.o` and `ab8500.o` compile, enable `REGULATOR_DEBUG` and verify `-DDEBUG`, and run `allmodconfig`/`allyesconfig` for stale mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/aat2870-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/aat2870-regulator.c

Purpose: registers four AnalogicTech AAT2870 LDO regulators as platform children of the AAT2870 MFD core. It implements voltage selector, enable, disable, and status operations through MFD-provided read/update callbacks.

Important APIs and data: `struct aat2870_regulator` combines an `aat2870_data` pointer, descriptor, and computed enable/voltage register fields. `aat2870_ldo_ops` provides table voltage listing, ascending voltage mapping, selector set/get, enable/disable, and is-enabled. `aat2870_ldo_voltages[]` is a 16-entry table from 1.2 V to 3.3 V. `aat2870_get_regulator()` maps platform ID to descriptor and register bit layout. `aat2870_regulator_probe()` registers the selected LDO.

Control flow: each platform device has an ID corresponding to LDOA-D. Probe resolves the static descriptor, fills register addresses, shifts, and masks based on ID, stores the parent MFD data pointer, applies optional platform init data, and calls `devm_regulator_register()`. Init uses `subsys_initcall()` to register the platform driver.

State and persistence: descriptor entries are static and are mutated by `aat2870_get_regulator()` with per-ID register fields and parent data. This is acceptable for one device set but not naturally multi-instance safe. Hardware state lives in AAT2870 registers.

Dependencies and integration: depends on `MFD_AAT2870_CORE`, platform child IDs, parent `aat2870_data` callbacks, regulator core, and board platform data for constraints.

Risks: static descriptor mutation could cross-contaminate multiple AAT2870 instances. Invalid platform IDs fail probe. The voltage register pair and nibble shift math must match hardware layout. No OF matching is present; integration is MFD/platform-data oriented.

Test signals: probe LDOA-D IDs, invalid ID rejection, selector set/get for upper and lower nibbles, enable mask per LDO, parent read/update error propagation, voltage table mapping, and multi-instance review if hardware can appear more than once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/aat2870-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ab8500-ext.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/ab8500-ext.c

Purpose: supports AB8500 external fixed-voltage regulators, especially `VextSupply3`, through the regulator framework. It controls high-power, low-power, hardware-request, and off modes by updating AB8500 bank/register bitfields.

Important APIs and data: `ab8500_ext_regulator_info` stores descriptor data, register update location, masks, current mode value, and mode-specific values. `ab8500_ext_regulators[]` provides fixed-voltage constraints and consumer supply metadata. Regulator ops include enable, disable, is-enabled, set/get mode, set voltage validation, and fixed-voltage listing. `ab8500_ext_regulator_probe()` registers all three supplies.

Control flow: probe obtains the parent `ab8500`, applies a revision quirk for AB8500 2.x by inverting VextSupply3 LP/HP values, then iterates through all external regulator info entries. Each entry gets its device pointer, optional config from init-data driver data, regulator config, and devm registration. Enable selects HP if hardware request mode is required, otherwise the current requested mode. Disable selects hardware-request mode if configured, otherwise off. Set-mode updates hardware only when enabled and not forced by hardware request, then records the desired mode in `update_val`.

State and persistence: mode preference is held in mutable `update_val` fields in static regulator info. Hardware state persists in AB8500 registers until changed or reset. No file or firmware persistence is used.

Dependencies and integration: depends on `AB8500_CORE`, ABx500 register accessors, AB8500 revision helpers, platform driver name `ab8500-ext-regulator`, regulator constraints, and Makefile pairing with `ab8500.o` under `REGULATOR_AB8500`.

Risks: static mutation of regulator info and revision quirk is global, so multiple AB8500 instances would share modified state. `set_voltage` only accepts exact fixed constraints and does not use selectors. Hardware-request mode can make software disable mean "HW controlled" rather than off. Null constraint or info pointers return errors.

Test signals: AB8500 2.x VextSupply3 inversion, enable/disable register writes for HW-request and normal configs, mode changes while enabled/disabled, fixed-voltage list/set validation, missing parent rejection, and consumer supply linkage for SIM voltage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ab8500-ext.c -->
