# Research: subset-b-003538

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_5_ppt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_5_ppt.c

### Purpose
`smu_v13_0_5_ppt.c` is the SMU13.0.5 power-play table backend for AMDGPU SWSMU. It wires the generic `smu_context` callbacks to the SMU13.0.5 firmware message ABI, allocates the firmware-facing tables needed by this ASIC, exposes sensors and GPU metrics, and implements the supported DPM, clock forcing, overdrive, watermarks, media power gating, gfx-off, and mode2 reset operations. The file marks the device as an APU-oriented backend in `smu_v13_0_5_set_ppt_funcs()` and uses a custom MP1 C2PMSG register layout for message control.

### Important APIs, Types, And Data
- `smu_v13_0_5_ppt_funcs` is the exported behavior table. It registers callbacks for SMC table init/fini, firmware status/version, VBIOS boot values, feature control, VCN/JPEG power gating, DPM table fetch, sensor reads, watermarks, GPU metrics, feature masks, driver table location, gfx-off, mode2 reset, DPM frequency limits, overdrive edits, sysfs clock-level emission, forced clock levels, performance level selection, and fine-grained GFX frequency defaults.
- `smu_v13_0_5_message_map` translates common `SMU_MSG_*` ids to `PPSMC_MSG_*` ids including VCN/JPEG power, GFX reset, table transfers, GFX clock queries, enabled-feature queries, GFX/VN soft min/max controls, driver interface version, and unload notification.
- `smu_v13_0_5_feature_mask_map` maps generic feature bits to SMU13.0.5 firmware feature ids. Some entries use reverse or half-reverse mappings for firmware bit layout differences.
- `smu_v13_0_5_table_map` declares WATERMARKS, SMU_METRICS, CUSTOM_DPM, and DPMCLOCKS as valid firmware tables.
- `smu_v13_0_5_dpm_features` is the DPM-running mask: CCLK, FCLK, LCLK, GFX, VCN, DCFCLK, SOCCLK, MP0CLK, and SHUBCLK DPM must be enabled for the file to report DPM running.
- `SMU_13_0_5_UMD_PSTATE_GFXCLK` comes from the companion header and supplies the synthetic middle GFX clock shown in clock-level output.

### Control Flow And Behavior
- Initialization enters through `smu_v13_0_5_set_ppt_funcs()`, which installs the callback table, feature/table maps, APU flag, SMU driver interface version, and MP1 message control registers. `smu_v13_0_5_init_msg_ctl()` assigns message, response, and argument registers and uses `smu_msg_v1_ops` with a timeout derived from `adev->usec_timeout`.
- `smu_v13_0_5_init_smc_tables()` initializes VRAM-backed SMU tables for watermarks, DPM clocks, and metrics, then allocates kernel shadow copies for DPM clocks, metrics, and watermarks. It also creates a cached driver table for `gpu_metrics_v2_1`. `smu_v13_0_5_fini_smc_tables()` frees those allocations and tears down the GPU metrics driver table.
- Runtime metrics are pulled through `smu_cmn_get_metrics_table()` into `SmuMetrics_t`. `smu_v13_0_5_get_smu_metrics_data()` translates individual `MetricsMember_t` values into AMDGPU units for clocks, activity, socket power, temperatures, throttling status, and voltages. `smu_v13_0_5_read_sensor()` maps public `amd_pp_sensors` requests onto that helper and reports 4-byte sensor values.
- `smu_v13_0_5_get_gpu_metrics()` fills a `gpu_metrics_v2_1` table from `SmuMetrics_t`, including temperatures, activity, socket/GFX/SOC power, clocks, throttle status, and a boot-time system clock counter. It updates the SMU driver-table cache timestamp before returning the structure size.
- DPM clock data is fetched by `smu_v13_0_5_set_default_dpm_tables()` from `SMU_TABLE_DPMCLOCKS`. Helpers then report current clocks, level counts, indexed DPM frequencies, DPM enablement, and min/max ultimate frequencies. If a clock's DPM feature is disabled, `smu_v13_0_5_get_dpm_ultimate_freq()` falls back to boot frequencies via `smu_v13_0_get_boot_freq_by_index()`.
- Frequency limits are applied by `smu_v13_0_5_set_soft_freq_limited_range()`. GFX/SCLK uses `SetHardMinGfxClk` and `SetSoftMaxGfxClk`; VCLK/DCLK uses packed VCN min/max messages and shifts VCLK values by `SMU_13_VCLK_SHIFT`.
- Sysfs clock-level output is produced by `smu_v13_0_5_emit_clk_levels()`. It prints OD SCLK/range, enumerates SOCCLK/VCLK/DCLK/MCLK DPM levels, and presents GFX/SCLK as min/current-or-UMD/max with an active marker.
- Clock forcing is intentionally narrow: `smu_v13_0_5_force_clk_levels()` supports VCLK and DCLK masks by translating selected indices to frequencies and setting a min/max range; other clock types return `-EINVAL`.
- Overdrive is only accepted when `smu_dpm.dpm_level` is `AMD_DPM_FORCED_LEVEL_MANUAL`. `smu_v13_0_5_od_edit_dpm_table()` validates min/max GFX SCLK edits against default limits, stages them in `smu->gfx_actual_*`, restores defaults, and commits by sending hard-min and soft-max GFX messages.
- Performance levels are translated in `smu_v13_0_5_set_performance_level()` into SCLK, VCLK, and DCLK min/max ranges. HIGH/LOW lock to ultimate max/min, AUTO restores full ranges, profile modes select standard/min/peak-style single frequencies, MANUAL and PROFILE_EXIT leave existing limits untouched, and PROFILE_MIN_MCLK is unsupported.
- `smu_v13_0_5_set_watermarks_table()` copies display read/write watermark ranges into the firmware `Watermarks_t` shadow and writes the table once through `smu_cmn_write_watermarks_table()`, tracked by `smu->watermarks_bitmap`.
- Media power transitions are simple firmware messages: VCN uses `PowerUpVcn`/`PowerDownVcn`, JPEG uses `PowerUpJpeg`/`PowerDownJpeg`. System feature shutdown sends `PrepareMp1ForUnload` unless entering S0ix.
- Reset support is mode2 only in this file: `smu_v13_0_5_mode2_reset()` sends `GfxDeviceDriverReset` with `SMU_RESET_MODE_2`.

### State And Persistence
- Persistent driver state lives in `smu->smu_table` shadow pointers, the GPU metrics driver table, `smu->watermarks_bitmap`, DPM clocks loaded from firmware, and `smu->gfx_default_*` / `smu->gfx_actual_*` frequency fields.
- The watermarks table is write-once per load in this implementation: after `WATERMARKS_LOADED` is set, future calls do not rewrite unless higher-level code clears the bitmap.
- Metrics caching is mostly delegated to common helpers; `get_gpu_metrics()` explicitly refreshes and updates the driver-table cache timestamp.
- The message controller mutex and register configuration are initialized once with the PPT backend and are used by common SMC messaging paths.

### Dependencies And Integration Points
- Depends on SMU13 common code (`smu_v13_0.*`, `smu_cmn.*`), SMU13.0.5 firmware headers (`smu13_driver_if_v13_0_5.h`, `smu_v13_0_5_ppsmc.h`, `smu_v13_0_5_pmfw.h`), AMDGPU device/runtime structures, and Linux kernel memory/time/sysfs helpers.
- Integrates with the AMDGPU powerplay layer through `pptable_funcs`; with firmware through SMC messages and VRAM tables; with sysfs through clock-level and overdrive callbacks; with display memory timing through watermark programming; and with reset paths through the mode2 reset callback.
- It intentionally uses common helpers for firmware version checks, feature masks, PP feature masks, VBIOS boot values, gfx-off control, and driver table location.

### Risks And Edge Cases
- `smu_v13_0_5_get_smu_metrics_data()` returns `UINT_MAX` for unsupported metrics but still reports success, so callers must understand that sentinel. Several sensors such as `SS_APU_SHARE` and `SS_DGPU_SHARE` request members not handled by the helper and will receive that sentinel with a successful return.
- DPM min/max logic for MCLK/UCLK/FCLK uses reversed DF pstate ordering: max is index 0 and min is the last enabled DF pstate. Regressions here would invert memory or fabric limits.
- `smu_v13_0_5_set_watermarks_table()` only writes the firmware table if it has not already been loaded. Dynamic watermark changes after the first load may be ignored unless external code resets `WATERMARKS_LOADED`.
- Clock forcing only handles VCLK/DCLK. User expectations for SCLK/MCLK forcing must be covered elsewhere or surfaced as unsupported.
- Overdrive staged values are stored in `smu_context`; failed commits can leave staged actual min/max values that differ from firmware if only one SMC message succeeds.
- Temperature and power unit conversions are specific to `SmuMetrics_t` layout and Q/unit conventions; changes in firmware metrics format require corresponding conversion updates.

### Test Signals
- Boot/probe tests should verify `smu_v13_0_5_set_ppt_funcs()` installs the correct function table, message registers, feature/table maps, `is_apu = true`, and `SMU13_0_5_DRIVER_IF_VERSION`.
- SMC table init/fini tests or fault injection should cover allocation failure paths and confirm all shadows and driver tables are freed.
- Sensor tests should compare GPU load, VCN load, power, edge/hotspot temperature, SCLK/MCLK, and voltages against known `SmuMetrics_t` inputs and verify unsupported sensors return `-EOPNOTSUPP` or the documented sentinel behavior.
- Clock sysfs tests should validate DPM level ordering, active markers, GFX min/mid/max output, and behavior when DPM features are disabled.
- Overdrive tests should cover manual-mode gating, min/max validation, restore defaults, commit ordering, and error propagation from each SMC message.
- Watermark tests should check range-count validation, row mapping for reader/writer sets, bitmap transitions, and single upload behavior.
- Reset and media tests should confirm expected SMC messages for mode2 reset and VCN/JPEG enable/disable transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_5_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_5_ppt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_5_ppt.h

### Purpose
`smu_v13_0_5_ppt.h` is the public header for the SMU13.0.5 PPT backend. It exposes the backend registration entry point and defines the SMU13.0.5 UMD pstate GFX clock value used by the implementation's clock-level and profile logic.

### Important APIs, Types, And Data
- `void smu_v13_0_5_set_ppt_funcs(struct smu_context *smu)` is the single externally visible function. ASIC selection code calls it to bind SMU13.0.5-specific `pptable_funcs`, feature maps, table maps, driver interface version, APU flag, and message-control registers into the `smu_context`.
- `SMU_13_0_5_UMD_PSTATE_GFXCLK` is defined as `700` MHz. The `.c` backend uses it as the synthetic standard/middle GFX clock displayed when the current GFX clock is neither the configured min nor max and as the default standard profile clock.
- The include guard is `__SMU_V13_0_5_PPT_H__`.

### Control Flow And Behavior
- This header has no control flow of its own. Its declaration is the linkage contract between ASIC dispatch/probe code and `smu_v13_0_5_ppt.c`.
- The macro constant influences `smu_v13_0_5_emit_clk_levels()` and `smu_v13_0_5_get_dpm_profile_freq()` by providing a fixed UMD pstate clock when firmware DPM tables do not provide a separate standard GFX point.

### State And Persistence
- The header stores no state. Persistent state is established by the implementation after `smu_v13_0_5_set_ppt_funcs()` is called.
- The macro is compile-time configuration; changing it changes user-visible clock-level output and standard profile behavior.

### Dependencies And Integration Points
- The declaration depends on `struct smu_context` being visible to users of the header, normally through existing AMDGPU SMU include ordering.
- It integrates with SMU ASIC selection code and with the SMU13.0.5 implementation file.

### Risks And Edge Cases
- Because `SMU_13_0_5_UMD_PSTATE_GFXCLK` is hard-coded, it can diverge from firmware or silicon-specific standard clocks. That affects sysfs presentation and profile-standard behavior.
- The header intentionally does not include a forward declaration for `struct smu_context`; include-order changes could expose that implicit dependency.

### Test Signals
- Build coverage should confirm consumers include this header in an order where `struct smu_context` is known.
- ASIC probe tests should verify that calling `smu_v13_0_5_set_ppt_funcs()` succeeds and the installed callbacks behave as expected.
- Clock-level/profile tests should verify the `700` MHz pstate appears only in the intended GFX standard/middle cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_5_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.c

### Purpose
`smu_v13_0_6_ppt.c` is the large SMU13.0.6-family PPT backend for AMDGPU SWSMU. It supports the base SMU13.0.6 path plus related 13.0.12 and 13.0.14 firmware/IP variants. It handles firmware/P2S table loading, capability discovery, SMU table allocation, DPM policy setup, metrics and PM metrics export, partition/XCP metrics, sensors, power limits, clock and overdrive controls, MP1 interrupts and throttling logging, SMU-mediated I2C, reset operations, HBM bad page/RMA messaging, and MCA/ACA RAS integration.

### Important APIs, Types, And Data
- `smu_v13_0_6_ppt_funcs` is the backend callback table installed by `smu_v13_0_6_set_ppt_funcs()`. It covers DPM initialization, clock tables, sensors, power limits, microcode/tables, firmware status/version, table locations, feature control, IRQ registration, thermal alerts, metrics, resets, I2C, RAS messaging, SDMA/VCN reset, post-init capability exposure, and RAS driver lookup.
- `smu_v13_0_6_message_map` maps generic SMU messages to PPSMC messages. It includes metrics/version queries, feature enable/disable, I2C, DPM min/max/frequency by index, PPT/fast PPT, reset, DRAM logging, bad page/RMA, XGMI power policy, determinism, thermal/CTF limits, MCA dump/count messages, PLPD policy, SDMA/VCN reset, and static metrics.
- `smu_v13_0_6_clk_map`, `smu_v13_0_6_feature_mask_map`, and `smu_v13_0_6_table_map` translate generic SMU clocks/features/tables into firmware ids. The clock map includes SOCCLK, FCLK, UCLK/MCLK, DCLK, VCLK, and LCLK. The table map covers PMSTATUSLOG, SMU_METRICS, and I2C_COMMANDS.
- `smu_v13_0_6_dpm_features` is the DPM-running mask for data calculation, GFXCLK, UCLK, SOCCLK, FCLK, LCLK, XGMI, and VCN DPM.
- `struct smu_v13_0_6_dpm_map` connects a clock type, feature bit, `smu_dpm_table`, and PPTable frequency array for default DPM table population.
- `struct mca_bank_ipid` and `struct mca_ras_info` describe MCA bank decoding and RAS block-specific error counting/validation behavior.
- `smu_v13_0_6_throttler_map` maps PMFW throttler bits to common SMU throttler bits for KFD SMI throttling events.
- Firmware blobs are declared for `amdgpu/smu_13_0_6.bin` and `amdgpu/smu_13_0_14.bin`.

### Control Flow And Behavior
- Backend selection calls `smu_v13_0_6_set_ppt_funcs()`. It installs the PPT functions, chooses either the 13.0.12 or 13.0.6 message/feature map based on `amdgpu_ip_version(MP1_HWIP)`, installs the clock/table maps, ignores strict SMU driver interface version matching, enables RAS-priority firmware capability, initializes common SMU13 message control, sets temperature helpers for 13.0.12, and registers MCA/ACA SMU helper tables.
- Firmware checking flows through `smu_v13_0_6_check_fw_version()`, which first calls the common firmware checker and then initializes the capability bitset. Capability setup is split among `smu_v13_0_6_init_caps()`, `smu_v13_0_12_init_caps()`, and `smu_v13_0_14_init_caps()`. These functions gate features by firmware version, program id, APU vs dGPU, SR-IOV VF status, physical XGMI node id, and IP version.
- `smu_v13_0_6_init_microcode()` loads the SMU firmware for non-SR-IOV and non-13.0.12 paths, finds a P2S table entry by id (`P2S_TABLE_ID_A`, `P2S_TABLE_ID_X`, or `P2S_TABLE_ID_3` depending on APU/dGPU/device variant), and registers it as `AMDGPU_UCODE_ID_P2S_TABLE`.
- `smu_v13_0_6_tables_init()` declares firmware tables for PM status log, SMU metrics, I2C commands, and PMFW system metrics, allocates a metrics buffer sized for all metrics versions, allocates a driver PPTable, initializes a `smu_v13_0_6_gpu_metrics` driver table, and delegates extra table setup to 13.0.12 helpers when appropriate. `smu_v13_0_6_init_smc_tables()` combines that with DPM context allocation.
- DPM context allocation creates `smu_13_0_dpm_context` and DPM policy storage. dGPU paths get a SOC pstate policy; all paths get XGMI per-link power-down policy. Policy changes are sent through `SetThrottlingPolicy`, `GmiPwrDnControl`, or `SelectPLPDMode`.
- Metrics retrieval is table-driven. `smu_v13_0_6_get_metrics_table()` sends `GetMetricsTable`, invalidates HDP, copies from the driver table backing store into `smu_table->metrics_table`, and caches for one jiffy unless bypassed. `smu_v13_0_6_get_pm_metrics()` returns raw PMFW metrics with a common header describing IP version, PMFW version, metrics version, and structure size.
- `smu_v13_0_6_setup_driver_pptable()` is the one-time PPTable synthesis path. It waits for metrics `AccumulationCounter` to become nonzero, queries metrics version, stores socket power, GFX min/max, clock frequency tables, XGMI max speed/width, AID/XCD serial numbers, and optional static metrics. Static metrics can set board voltage and PLDM version. `smu_v13_0_6_update_caps()` clears FAST_PPT if firmware support exists but the PPTable lacks PPT1 limits.
- DPM table setup in `smu_v13_0_6_set_default_dpm_table()` calls PPTable setup, removes SOC policy if unsupported, initializes policy state, fills fine-grained GFX min/max from firmware, and fills SOC/UCLK/FCLK/VCLK/DCLK tables from PPTable frequency arrays and firmware level counts.
- UMD pstate setup in `smu_v13_0_6_populate_umd_state_clk()` copies min/peak/current ranges for GFX, UCLK, SOC, and FCLK. It chooses standard GFX/UCLK/SOC entries from fixed level constants if the tables are deep enough, otherwise it falls back to minima.
- Clock-level output and clock forcing are split across `smu_v13_0_6_emit_clk_levels()`, `smu_v13_0_6_upload_dpm_level()`, and `smu_v13_0_6_force_clk_levels()`. Sysfs reporting supports OD SCLK/MCLK/FCLK plus DPM tables; forced levels are implemented for SCLK/GFX only, while MCLK/SOCCLK/FCLK forcing returns `-EINVAL`.
- Manual and determinism clock limiting is handled by `smu_v13_0_6_set_performance_level()`, `smu_v13_0_6_set_soft_freq_limited_range()`, and `smu_v13_0_6_usr_edit_dpm_table()`. Manual mode supports GFX min/max, UCLK max-only if `SET_UCLK_MAX` is present, and FCLK max-only. Determinism restores default GFX min/max then sends `EnableDeterminism` with the requested GFX clock.
- Sensor reads map activity, power, hotspot/memory temperature, SCLK/MCLK, VDDGFX, board voltage, node power metrics, and UBB/system power metrics to metrics-table helpers. During RAS interrupt handling, sensor reads return early.
- Power limit callbacks read current PPT from `GetPptLimit`, default/max from the synthesized PPTable, and delegate regular setting to common SMU13 code. FAST_PPT setting and querying are gated by `SMU_CAP(FAST_PPT)` and validated against PPTable PPT1 min/max/default.
- MP1 interrupt handling registers an IRQ source except in SR-IOV VF mode. The process callback acknowledges MP1 software interrupts, handles thermal throttling context ids, increments the throttle counter, stores PMFW-provided throttler status, and schedules throttling log work under a ratelimit. The log callback formats throttling causes and emits KFD SMI throttle events.
- SMU-mediated I2C is implemented as an `i2c_algorithm`. `smu_v13_0_6_i2c_xfer()` translates Linux `i2c_msg` arrays into `SwI2cRequest_t` byte commands with restart/stop flags, copies the request to the firmware table, sends `RequestI2cTransaction`, retries once on failure, and copies read data back from firmware output. Initialization registers one adapter per `MAX_SMU_I2C_BUSES` and exposes bus 0 for RAS and FRU EEPROM.
- Metrics export supports both whole-GPU and partition views. `smu_v13_0_6_get_gpu_metrics()` fills `smu_v13_0_6_gpu_metrics` with temperatures, activity, bandwidth, power, clocks, accumulated counters, PCIe, XGMI, JPEG/VCN, per-XCC busy, host-limit metrics, and firmware timestamp. `smu_v13_0_6_get_xcp_metrics()` fills a partition metrics structure for a selected XCP using instance masks from the XCP manager.
- Reset support includes mode1, mode2, link reset, SDMA reset, and VCN reset. Mode2 sends an async reset, waits, reloads PCI state, restores config space unconditionally for dGPU switch cases, and waits for firmware response. Mode1 encodes RAS fatal error status in the reset parameter. Link reset is available only for selected device variants. Post-init exposes link/SDMA/VCN reset feature caps if supported.
- RAS messaging is tightly filtered by `smu_v13_0_6_ras_send_msg()` to a whitelist of MCA/RAS table messages and is blocked in SR-IOV VF mode. HBM bad page count and RMA reason use dedicated SMU messages, gated by capabilities where needed.
- MCA support queries valid UE/CE bank counts, dumps MCA banks through SMU messages, decodes IPID into hardware IP, validates RAS block ownership, and counts errors using block-specific handlers for UMC, GFX, SDMA, MMHUB, XGMI WAFL, VCN, and JPEG. ACA support mirrors the bank count/dump/debug-mode flow and parses error code from SYND or STATUS depending on capability.

### State And Persistence
- Capability state is stored in `smu_13_0_dpm_context->caps`; most advanced behavior is gated by these bits after firmware version discovery.
- Long-lived driver state includes `smu_table->metrics_table`, `smu_table->driver_pptable`, the GPU metrics driver table, DPM context/tables/policies, `smu->pstate_table`, board voltage, firmware PLDM version, unique-id mappings, throttle status atomics, and registered I2C adapters.
- Metrics are cached in `smu_table->metrics_table` with a one-jiffy freshness check unless callers bypass the cache. GPU metrics driver-table cache time is updated when the soft metrics table is filled.
- The synthesized `PPTable_t` has an `Init` flag and is populated once from metrics/static metrics. It persists firmware-derived limits and serial numbers for later DPM, power, and identity operations.
- PMFW capability bits can be downgraded after table setup, notably FAST_PPT if PPT1 values are absent.
- I2C bus registration uses devm-managed adapter registration; fini clears EEPROM bus pointers but does not manually unregister devm adapters.

### Dependencies And Integration Points
- Depends on AMDGPU core, SMU13 common code, firmware loading APIs, ATOM firmware helpers, PCI config APIs, XGMI, RAS, MCA, ACA, UMC v12 ECC helpers, MP/NBIO/THM register headers, Linux I2C, and the 13.0.6 PMFW/PPSMC/driver interface headers.
- Integrates with SMU firmware through SMC messages and shared VRAM/GTT tables, with AMDGPU powerplay via `pptable_funcs`, with KFD through throttling SMI events, with XCP partition management for partition metrics, with RAS/MCA/ACA subsystems for error collection, with EEPROM users through SMU I2C adapters, and with reset/recovery paths through mode/link/engine reset callbacks.
- 13.0.12-specific behavior is delegated to symbols declared in the header, including metrics, table setup/fini, PMFW system metrics, temperature funcs, and RAS driver support.

### Risks And Edge Cases
- Capability gates are firmware-version dense. Mistakes in version thresholds, program id handling, or SR-IOV/APU branches can silently enable unsupported SMC messages or hide supported features.
- `smu_v13_0_6_setup_driver_pptable()` waits up to roughly 100 ms for nonzero accumulation counter; firmware that does not update this field can fail probe/table setup with `-ETIME`.
- PPTable synthesis reads metrics versions through macro-selected layouts. A firmware metrics layout mismatch can corrupt clock tables, power limits, serial numbers, or XGMI speed/width.
- `smu_v13_0_6_get_static_metrics_table()` uses the SMU metrics table size for static metrics copying. This relies on firmware/common table sizing matching the shared buffer layout.
- FAST_PPT paths reference `SMU_MSG_SetFastPptLimit` and `SMU_MSG_GetFastPptLimit` through common message ids, but this file's explicit message map excerpt does not show local map entries for those names; correctness depends on common map coverage or header enum alignment.
- I2C translation assumes all messages in a transaction share the first slave address because firmware request has one `SlaveAddress`. The adapter quirks require combined same-address transactions, but callers outside those quirks would be unsafe.
- `smu_v13_0_6_i2c_xfer()` allocates one `SwI2cRequest_t` and increments `NumCmds` per byte; correctness depends on I2C core enforcing max lengths from quirks before the transfer callback.
- Several reset and PCIe paths have TODO or workaround comments around register offsets, real-target confirmation, and PCI config restoration. They need hardware validation across switches and variants.
- RAS/MCA bank validation uses hard-coded IPID instance patterns and error-code arrays. New silicon variants or firmware error encodings may require updates to avoid dropping valid errors.
- Sensor reads return success with no data during a RAS interrupt (`amdgpu_ras_intr_triggered()` path), which can hide transient unavailability from callers.
- `smu_v13_0_6_get_enabled_mask()` treats `-EIO` as success with an empty mask when DPM capability is absent. That prevents failures on old firmware but can mask real communication problems when capability discovery is wrong.

### Test Signals
- Probe tests should cover 13.0.6, 13.0.12, 13.0.14, APU, dGPU, PF, and SR-IOV VF combinations and verify selected message/feature maps, capabilities, temp funcs, RAS funcs, I2C bus registration, and reset feature caps.
- Firmware-version matrix tests should validate each capability threshold, especially DPM, DPM_POLICY, PCIE_METRICS, MCA_DEBUG_MODE, PER_INST_METRICS, STATIC_METRICS, FAST_PPT, SYSTEM_POWER_METRICS, SDMA_RESET, and VCN_RESET.
- Table setup tests should fault-inject allocation failures, metrics copy failures, static metrics failures, and accumulation-counter timeout, confirming resources are cleaned up.
- Metrics tests should feed V0/V1/V2 metrics layouts and assert unit conversion, instance mapping, XGMI external-link ordering, PCIe fallback behavior, host-limit metrics gating, XCP partition filtering, and 13.0.12 delegation.
- Clock and OD tests should validate DPM table population, UMD pstate standard levels, manual-mode gating, determinism enable/disable, UCLK/FCLK max-only behavior, and unsupported forced clocks.
- Power tests should validate current/default/min/max PPT, FAST_PPT min/max/default/current queries, invalid FAST_PPT limits, and fallback to common power-limit handling.
- IRQ/throttling tests should simulate MP1 thermal interrupt entries, acknowledge registers, ratelimit behavior, throttle status storage, warning text composition, and KFD SMI event mapping.
- I2C tests should cover write, read, write-read combined transactions, restart/stop flag placement, retry-on-failure, DPM-disabled `-EBUSY`, max command lengths, and same-address quirks.
- Reset tests should cover mode1 fatal-error parameter encoding, mode2 async response timeout/retry behavior, PCI config restoration, link-reset variant gating, SDMA/VCN capability gating, and error propagation.
- RAS tests should cover whitelisted message enforcement, MCA bank count/dump, IPID decoding, per-block error counting, ACA SYND-vs-STATUS parsing, SR-IOV blocking, and hard-coded error-code array coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.h

### Purpose
`smu_v13_0_6_ppt.h` is the shared public and layer-2 internal header for the SMU13.0.6-family PPT backend. It defines UMD pstate level constants, the driver's synthesized PPTable shape, capability bits, sizing constants for multi-instance metrics, exported backend/helper prototypes, and macro-generated GPU and partition metric classes used by the implementation and 13.0.12 companion code.

### Important APIs, Types, And Data
- `smu_v13_0_6_set_ppt_funcs(struct smu_context *smu)` is the backend registration entry point.
- `smu_v13_0_6_cap_supported()`, `smu_v13_0_6_get_static_metrics_table()`, and `smu_v13_0_6_get_metrics_table()` are exported helpers for capability checks and metrics/static-metrics retrieval.
- The header declares a family of 13.0.12 helper APIs used by the 13.0.6 implementation when `MP1_HWIP` is IP 13.0.12: DPM-running detection, max/system metrics sizing, driver PPTable setup, metrics extraction, XCP metrics, table init/fini, NPM/system power sensors, feature/message maps, temp funcs, and RAS driver.
- `METRICS_LIST_e` identifies PMFW metric table layout variants V0, V1, and V2.
- `struct PPTable_t` is the driver-synthesized table storing max socket/node/PPT limits, GFX min/max, frequency tables for FCLK/UCLK/SOCCLK/VCLK/DCLK/LCLK, LCLK range, public serial number, and an `Init` flag.
- `enum smu_v13_0_6_caps` defines runtime capability bits: DPM, DPM policy, other-end PCIe metrics, UCLK max setting, PCIe metrics, MCA debug, per-instance metrics, CTF limits, RMA message, ACA syndrome, SDMA/VCN reset, static metrics, host-limit metrics, board voltage, PLDM version, temp/NPM/system power metrics, RAS EEPROM, FAST_PPT, temperature AID/XCD/HBM metrics, and an ALL sentinel.
- Sizing constants describe maximum XGMI links, GFX clocks/XCCs, clocks, VCN, JPEG rings, AIDs, and HBM stacks.
- `SMU_13_0_6_METRICS_FIELDS()` and `SMU_13_0_6_PARTITION_METRICS_FIELDS()` are field-list macros consumed by `DECLARE_SMU_METRICS_CLASS()` to generate strongly described metric structures and init helpers.

### Control Flow And Behavior
- This header does not execute logic directly, but it shapes how `smu_v13_0_6_ppt.c` compiles under `SWSMU_CODE_LAYER_L2`. When that macro is defined, it includes `smu_cmn.h` and declares macro-generated metric classes for whole-GPU and partition metrics.
- The UMD pstate constants define table indices used by the implementation to choose standard GFX, SOC, and memory clocks when enough DPM levels are available.
- `struct PPTable_t` acts as a persistent normalized view of values that SMU13.0.6 firmware exposes through metrics/static metrics rather than a traditional full PPTable.
- The metrics field macros define names, units, scalar/array type metadata, and array extents for metrics exported to userspace or other driver components.

### State And Persistence
- Header-defined state is structural. Runtime instances of `PPTable_t`, generated GPU metrics, and generated partition metrics are allocated and updated by the `.c` implementation.
- The capability enum values persist as bit positions in `smu_13_0_dpm_context->caps`; changing enum ordering is a compatibility risk inside the driver.
- The max-size constants constrain array storage and loops in metrics export code.

### Dependencies And Integration Points
- Depends on SMU common metric declaration machinery (`DECLARE_SMU_METRICS_CLASS`, `SMU_MATTR`, `SMU_MUNIT`, `SMU_MTYPE`) when compiled in layer-2 mode.
- Integrates with the SMU13.0.6 PPT implementation, SMU13.0.12 companion implementation, AMDGPU XCP partition metrics, RAS SMU driver selection, temperature helper dispatch, and firmware metrics table decoding.
- The exported 13.0.12 symbols allow this family backend to share one public header while routing IP-specific behavior to a companion implementation.

### Risks And Edge Cases
- The generated metrics structures depend on array extents matching firmware-provided arrays. Underestimating constants can truncate data; overestimating requires implementation loops to guard absent instances.
- `PPTable_t` includes `bool Init` after numeric fields; structure layout is internal driver memory, but careless serialization or firmware assumptions would be unsafe.
- Capability enum order must remain consistent with bit operations using `BIT_ULL(cap)`.
- UMD pstate constants are indices, not frequencies. If firmware DPM tables become shallower than expected, implementation must fall back to min values, as it currently does.
- 13.0.12 declarations in this header create tight cross-file coupling; build failures or ABI mismatches will show up in this shared backend even if base 13.0.6 paths do not use the helpers.

### Test Signals
- Build tests should cover both layer-2 compilation and consumers that only need the public prototypes.
- Static assertions or compile-time review should ensure metrics field arrays align with PMFW table definitions for XGMI, GFX/XCC, VCN, JPEG, AID, and HBM counts.
- Capability tests should verify every enum bit used by the implementation maps to the intended feature gate.
- Metrics export tests should verify generated `smu_v13_0_6_gpu_metrics` and `smu_v13_0_6_partition_metrics` structures initialize to the expected version/format and expose declared units/types.
- 13.0.12 integration tests should verify all declared helper symbols are provided and are selected correctly by `smu_v13_0_6_ppt.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.h -->
