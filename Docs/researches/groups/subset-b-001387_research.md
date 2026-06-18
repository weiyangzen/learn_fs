# subset-b-001387 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.h

## Purpose
This header declares the DCN 3.5 display clock manager interface and the DCN 3.5 specific `clk_mgr_internal` wrapper used by AMD Display Core. It is the public contract between generic clock-manager selection code, DCN 3.5 clock-manager implementation files, and the DCN 3.5 SMU mailbox layer.

## Important APIs, Types, And Functions
`struct clk_mgr_dcn35` embeds `struct clk_mgr_internal` and adds `smu_wm_set`, so all generic clock-manager function table consumers can treat the object as a base clock manager while DCN 3.5 code can keep SMU watermark table state. `struct dcn35_smu_watermark_set` couples a CPU-visible `struct dcn35_watermarks *` with a GPU memory controller address for SMU table transfer. `struct dcn35_ss_info_table` stores spread-spectrum divider and per-clock-source percentages.

Declared entry points include `dcn35_init_clocks`, `dcn35_update_clocks`, `dcn35_clk_mgr_construct`, `dcn351_clk_mgr_construct`, `dcn35_clk_mgr_destroy`, `dcn35_are_clock_states_equal`, and `dcn35_disable_otg_wa`. The separate DCN 3.5 and DCN 3.5.1 constructors indicate shared structure with variant-specific setup.

## Control Flow And Integration
Generic clock-manager creation in `clk_mgr.c` selects this family and calls a constructor. Runtime display validation later calls the function table installed by the implementation, which uses these declarations for clock initialization, clock updates, and teardown. The header intentionally forward-declares `struct dcn35_watermarks`; the concrete SMU watermark layout is owned by `dcn35_smu.h`.

## State And Persistence
State is held in the live `clk_mgr_dcn35` allocation and in GPU memory referenced by `smu_wm_set`. There is no durable storage; persistence is limited to driver lifetime and SMU-visible memory until freed by destroy paths.

## Dependencies
The header depends on `clk_mgr_internal.h` for base clock-manager types and on common Display Core types such as `dc_context`, `dc_state`, `dc_clocks`, `dccg`, and `pp_smu_funcs` through included or transitive declarations.

## Risks
The most important risk is lifetime correctness for `smu_wm_set`: the SMU receives a physical address, so stale or freed memory would corrupt firmware interactions. The header also exposes variant constructors with identical object type, so implementation selection must match ASIC revision.

## Test Signals
Useful signals are successful display bring-up on DCN 3.5/3.5.1, SMU watermark transfer logs, no leaks across clock-manager destroy, and trace/assert coverage around `dcn35_update_clocks` and OTG disable workaround paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_smu.c

## Purpose
This file implements the DCN 3.5 DAL/VBIOS SMU mailbox wrapper. It converts display clock-manager requests into PMFW messages for clock programming, watermark and DPM table transfers, display idle optimizations, Z-state policy, DTB/DPREF queries, IPS support, and host-router bandwidth notification.

## Important APIs, Types, And Functions
The central helpers are `dcn35_smu_wait_for_response` and `dcn35_smu_send_msg_with_param`. They poll `MP1_SMN_C2PMSG_91`, write arguments to `MP1_SMN_C2PMSG_83`, and trigger messages through `MP1_SMN_C2PMSG_67`. Public wrappers include `dcn35_smu_set_dispclk`, `dcn35_smu_set_dppclk`, `dcn35_smu_set_hard_min_dcfclk`, `dcn35_smu_set_min_deep_sleep_dcfclk`, `dcn35_smu_set_dprefclk`, `dcn35_smu_get_dprefclk`, `dcn35_smu_get_dtbclk`, `dcn35_smu_set_dtbclk`, `dcn35_smu_set_zstate_support`, `dcn35_smu_transfer_dpm_table_smu_2_dram`, `dcn35_smu_transfer_wm_table_dram_2_smu`, `dcn35_smu_exit_low_power_state`, `dcn35_smu_get_ips_supported`, and `dcn35_smu_notify_host_router_bw`.

## Control Flow And Integration
Each exported function first checks `clk_mgr->smu_present` where firmware is required, then sends one message with an integer parameter. Clock requests are converted from kHz to MHz with ceiling semantics, and firmware return values are converted back to kHz. Table transfer wrappers rely on callers to program high and low DRAM address registers first. Z-state support maps Display Core enum values to bitfields for Z8, Z9, and Z10 support.

## State And Persistence
The file does not own long-lived heap state. Its persistent effects are PMFW state changes: hard minimum clocks, deep sleep DCFCLK, idle optimization flags, PME workaround state, DTB clock enablement, and SMU table contents. The wait loop honors `debug.disable_timeout` by extending retry count, which can intentionally make firmware waits unbounded for debug.

## Dependencies
It depends on register helpers, MP 14 register offsets and masks, `clk_mgr_internal`, Display Core logging, and the SMU table/message IDs from `dcn35_smu.h`. It integrates with `dcn35_clk_mgr.c`, which calls these wrappers during initialization, display commits, watermark notification, low-power transitions, and DPIA host-router bandwidth updates.

## Risks
Timeout and error handling is assert-heavy. A failed watermark transfer is downgraded to a warning, but many other failures assert and continue to read the argument register, so incorrect firmware behavior can propagate bogus clock values. Message IDs are locally defined with a TODO about real headers, creating interface drift risk. Unit conversion by ceiling avoids underclocking but can increase power.

## Test Signals
Look for `DC_LOG_SMU` traces showing requested and actual clock values, warnings on non-OK responses, successful IPS query/exit flows, and no display underflow during clock changes. Firmware interface tests should cover busy, failed, timeout, and successful response register sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_smu.h

## Purpose
This header defines the DCN 3.5 PMFW driver interface subset consumed by the display clock manager. It supplies table layouts, DPM level constants, watermark structures, display idle optimization encoding, and prototypes for the SMU mailbox wrapper.

## Important APIs, Types, And Functions
The file defines `PMFW_DRIVER_IF_VERSION 4`, `DSPCLK_e`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, `Watermarks_t`, `DpmClocks_t_dcn35`, and `DpmClocks_t_dcn351`. DCN 3.5.1 splits VCN clock arrays into VCN0 and VCN1 fields, while DCN 3.5 has single VCN arrays. `MemPstateTable_t` describes UCLK, memory clock, voltage, and WCK ratio. `struct dcn35_smu_dpm_clks` and `struct dcn351_smu_dpm_clks` pair table pointers with GPU addresses.

The function prototypes cover SMU versioning, clock programming, table transfer, display idle optimization, PHY reference clock powerdown, PME workaround, Z-state policy, DTB/DPREF queries, IPS low-power handling, and DPIA host router bandwidth notification.

## Control Flow And Integration
Clock-manager constructors allocate GPU memory for DPM and watermark tables, use the DRAM address setters declared here, and request SMU table transfers using `TABLE_DPMCLOCKS` or `TABLE_WATERMARKS`. Runtime clock updates call the per-clock setters and low-power helpers. The header is shared by the C wrapper and by DCN 3.5 clock-manager implementation code.

## State And Persistence
The structures describe firmware-owned or shared-memory state. `WatermarkRowGeneric_t` persists until overwritten in SMU table memory. `DpmClocks_t_*` is a snapshot transferred from SMU into driver memory. `display_idle_optimization` encodes PMFW policy bits for display idle handling.

## Dependencies
It depends on `os_types.h` and Display Core's `clk_mgr_internal` and `dcn_zstate_support_state` declarations through users. It must remain binary-compatible with PMFW, so field ordering, sizes, and table constants are dependency boundaries.

## Risks
The file embeds a PMFW interface copy. Any mismatch with firmware table version, array counts, or structure packing can corrupt clock table parsing or watermark transfer. The TODO near `display_idle_optimization` says the type was taken from another ASIC and may be incorrect, which is a direct firmware-contract risk.

## Test Signals
Validation should compare SMU-reported DPM tables against expected ASIC data, verify DCN 3.5 versus DCN 3.5.1 table parsing, and confirm that watermark rows sent through shared memory are accepted by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_smu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dalsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dalsmc.h

## Purpose
This header defines the DCN 4.01 DAL-to-SMC message namespace used by the clock-manager SMU message wrapper. It is a compact contract for response codes, message IDs, and FCLK switch policy values.

## Important APIs, Types, And Functions
`DALSMC_VERSION` is defined as `0x1` and is checked at runtime by `dcn401_smu_check_msg_header_version`. Response constants include OK, Failed, UnknownCmd, CmdRejectedPrereq, and CmdRejectedBusy. Message IDs cover version checks, DRAM address setup, table transfer, hard minimum clock programming, DPM queries, display count, FCLK/UCLK p-state allow, CAB/UCLK policy, DMCUB wait behavior, DRR status, active/idle/SubVP UCLK/FCLK hardmins, and UMC channel query. `FclkSwitchAllow_e` names allow/disallow values.

## Control Flow And Integration
`dcn401_clk_mgr_smu_msg.c` includes this file and passes these IDs to `dcn401_smu_send_msg_with_param`. During `dcn401_init_clocks`, version messages validate that firmware and driver agree. During updates, the clock manager uses the hardmin, p-state, DMCUB wait, DRR, and display-count messages to synchronize PMFW with the Display Core mode state.

## State And Persistence
The header declares no state. Its constants control persistent firmware-side settings after messages are sent, such as p-state allow policy, hardmins, and watermark table ownership.

## Dependencies
It has no included dependencies and is consumed by the DCN 4.01 SMU message wrapper plus `dcn401_smu14_driver_if.h` table definitions.

## Risks
Message ID drift is the main risk. Since callers use numeric IDs directly, any mismatch between this header and PMFW can silently send a valid command with the wrong meaning. The version check catches only header version agreement, not semantic changes behind reused IDs.

## Test Signals
Firmware bring-up should assert that `DALSMC_MSG_GetMsgHeaderVersion` returns `DALSMC_VERSION`, every required message returns OK on supported ASIC revisions, and unsupported messages fail gracefully without corrupting clock-manager cached state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dalsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c

## Purpose
This file implements the DCN 4.01 clock manager. It initializes DPM clock tables from SMU, builds watermark ranges, programs display and bandwidth clocks, sequences PMFW and DCCG operations, exposes clock-manager function pointers, and constructs/destroys the DCN 4.01 clock-manager object.

## Important APIs, Types, And Functions
Key internal helpers include `dcn401_init_single_clock`, `dcn401_build_wm_range_table`, `dcn401_build_update_bandwidth_clocks_sequence`, `dcn401_build_update_display_clocks_sequence`, `dcn401_execute_block_sequence`, `dcn401_set_hard_min_by_freq_optimized`, `dcn401_update_clocks_update_dpp_dto`, `dcn401_update_clocks_update_dtb_dto`, `dcn401_update_clocks_update_dentist`, `dcn401_notify_wm_ranges`, `dcn401_get_memclk_states_from_smu`, and `dcn401_get_max_clock_khz`. The exported construction path is `dcn401_clk_mgr_construct`; teardown is `dcn401_clk_mgr_destroy`.

The file uses `struct dcn401_clk_mgr_block_sequence` from the header to queue clock operations before execution. The function table `dcn401_funcs` integrates it with generic Display Core clock-manager operations.

## Control Flow And Integration
Initialization probes SMU with `dcn401_smu_get_smu_version`, checks driver and message header versions, queries DPM levels for DCFCLK, SOCCLK, DTBCLK, DISPCLK, DPPCLK, UCLK, and FCLK, applies debug minimum overrides, computes DC-mode limits, and updates the bandwidth bounding box. Watermark initialization creates PMFW rows for normal and dummy p-state ranges.

Runtime updates are split into bandwidth and display sequences. Bandwidth sequencing updates display count, UCLK/FCLK p-state support, DCFCLK, deep-sleep DCFCLK, FW-assisted memory switching, CAB ways, active/idle UCLK/FCLK hardmins, and SubVP prefetch hardmins. Display sequencing handles DTBCLK hardmin and DTO updates, DPPCLK and DISPCLK hardmins, dentist programming, DPP DTO ordering, and PSR wait-loop updates. The sequence executor then performs SMU, DCCG, dentist, and DMCU operations in the computed order.

## State And Persistence
The clock manager caches current `dc_clocks`, `smu_present`, `dpm_present`, `smu_ver`, DPM tables in `bw_params`, boot snapshot clocks, spread-spectrum state, and a GART-allocated `wm_range_table`. Firmware-side persistent state includes hardmins, p-state allow settings, DMCUB wait policy, DRR status, display count, CAB ways, and watermark rows.

## Dependencies
The implementation depends on DCCG, generic clock-manager helpers, DC state/resource helpers, link service, atom firmware spread-spectrum queries, DCN 4.1 register definitions, and `dcn401_clk_mgr_smu_msg.c` wrappers. It also uses Display Core debug flags such as `force_min_dcfclk_mhz`, `disable_dtb_ref_clk_switch`, `force_subvp_df_throttle`, `min_disp_clk_khz`, and `min_dpp_clk_khz`.

## Risks
The block sequence has a fixed maximum size of 30; future additions can overflow if not audited. `dcn401_set_hard_min_by_freq_optimized` intentionally floors then ceils to balance power and correctness, so firmware return values must be reliable. Some FCLK p-state messages are commented as unsupported, making policy asymmetric with UCLK. Hardmin acknowledgements wait up to one second, which can stall commit paths. Watermark table allocation and physical address transfer require strict lifetime handling.

## Test Signals
Good signals include correct DPM table population, SMU version/header validation logs, no underflow when raising/lowering DPPCLK and DISPCLK, correct ordering for DPP DTO versus global clock changes, successful watermark transfer, correct DC-mode softmax behavior, and AutoDPM test logs matching expected hardware readbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.h

## Purpose
This header declares the DCN 4.01 clock-manager object, its deferred block-sequence model, and its public constructor/destructor and helper entry points.

## Important APIs, Types, And Functions
`DCN401_CLK_MGR_MAX_SEQUENCE_SIZE` bounds the number of queued clock operations. `union dcn401_clk_mgr_block_sequence_params` stores typed parameter sets for display count updates, hardmin requests, idle/active hardmins, p-state support, CAB ways, DMCUB wait, DRR status, DPP/DTB DTO updates, dentist updates, and PSR wait-loop changes. `enum dcn401_clk_mgr_block_sequence_func` identifies each action. `struct dcn401_clk_mgr` embeds `clk_mgr_internal` and owns the sequence array.

Public declarations include `dcn401_init_clocks`, `dcn401_is_dc_mode_present`, `dcn401_clk_mgr_construct`, `dcn401_clk_mgr_destroy`, and `dcn401_get_max_clock_khz`.

## Control Flow And Integration
The implementation builds a sequence of enum-plus-parameter entries, then executes it through a switch. This header is therefore the contract between sequence construction and sequence execution. Generic Display Core uses the constructor to obtain a `clk_mgr_internal *`, while the implementation uses `TO_DCN401_CLK_MGR`-style container access to reach the embedded sequence.

## State And Persistence
The sequence array is transient per update call, but it lives in the clock-manager object. Pointers stored in sequence params, such as response fields and `dc_state *`, must remain valid until execution completes.

## Dependencies
It relies on Display Core types such as `clk_mgr_internal`, `dc_state`, `dc_context`, `dccg`, and `dmcu` through included or transitive headers. The enum values align tightly with functions in `dcn401_clk_mgr.c`.

## Risks
The union allows stale fields if a sequence entry is mis-tagged. The fixed maximum can be exceeded if update logic grows without checking `num_steps`. Because some params carry pointers into live clock state, delayed or reused execution would be unsafe; the current design assumes immediate same-thread execution.

## Test Signals
Tests should stress mode changes that trigger many simultaneous sequence entries: display-off/on, p-state support flips, SubVP, FAMS enable/disable, DTB changes, and DPPCLK lowering. Instrumenting `num_steps` against the maximum is useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr_smu_msg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr_smu_msg.c

## Purpose
This file implements the DCN 4.01 SMU/DAL message transport and typed wrappers used by the DCN 4.01 clock manager. It owns register-level message submission, response polling, optional delay accounting, and all PMFW command encodings.

## Important APIs, Types, And Functions
Core helpers are `dcn401_smu_wait_for_response`, `dcn401_smu_send_msg_with_param`, `dcn401_smu_wait_for_response_delay`, and `dcn401_smu_send_msg_with_param_delay`. Public wrappers include version checks, p-state messages, CAB for UCLK, DRAM address setters, watermark transfer, PME workaround, hardmin programming, DMCUB wait control, DRR status, idle/active/SubVP UCLK/FCLK hardmins, deep-sleep DCEF clock, display count, UMC channel query, DPM frequency query, and DC-mode max DPM query.

## Control Flow And Integration
The transport waits until `DAL_RESP_REG` is nonzero, clears it, writes `DAL_ARG_REG`, writes the message ID to `DAL_MSG_REG`, then waits for `DALSMC_Result_OK`. For hardmin requests, it sends `DALSMC_MSG_SetHardMinByFreq` and then polls `DALSMC_MSG_ReturnHardMinStatus` until the bit for the requested PPCLK is set or a one-second software limit is reached. Idle, active, and SubVP UCLK/FCLK hardmins pack FCLK in bits 31:16 and UCLK in bits 15:0.

## State And Persistence
No heap state is owned. Persistent effects are firmware-side settings: clock hardmins, p-state allow policies, display count, watermark table contents, DMCUB wait policy, DRR state, and CAB ways. Delay-accounting helpers only accumulate local timing for hardmin polling.

## Dependencies
It includes `dalsmc.h` for message IDs and `dcn401_smu14_driver_if.h` for table/version constants. It depends on register helpers, Display Core trace macros, and `clk_mgr_internal` for context and logging.

## Risks
The first wait result before sending is ignored, so a stuck or invalid response register may still lead to a new message attempt. Generic failures return `false` but many higher-level callers do not fully recover cached state. Hardmin status polling uses bit positions based on `PPCLK_e`, so enum drift would break acknowledgement detection. Temporary defines for missing message IDs suggest header synchronization risk.

## Test Signals
Tracepoints `TRACE_SMU_MSG_ENTER` and `TRACE_SMU_MSG_EXIT` should show every transaction. Tests should cover version mismatch, hardmin timeout, non-OK transfer response, DPM query levels including fine-grained mode, and packed UCLK/FCLK parameter correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr_smu_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr_smu_msg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr_smu_msg.h

## Purpose
This header declares the DCN 4.01 SMU message wrapper interface consumed by `dcn401_clk_mgr.c`.

## Important APIs, Types, And Functions
It forward-declares `struct clk_mgr_internal` and declares bool-returning version checks, void setters for p-state/CAB/table/PME/display-count policy, hardmin setters and queries, and DPM information queries. Important functions include `dcn401_smu_get_smu_version`, `dcn401_smu_check_driver_if_version`, `dcn401_smu_check_msg_header_version`, `dcn401_smu_set_hard_min_by_freq`, `dcn401_smu_set_idle_uclk_fclk_hardmin`, `dcn401_smu_set_active_uclk_fclk_hardmin`, `dcn401_smu_set_subvp_uclk_fclk_hardmin`, `dcn401_smu_get_dpm_freq_by_index`, and `dcn401_smu_get_dc_mode_max_dpm_freq`.

## Control Flow And Integration
The clock manager includes this header and never touches DAL mailbox registers directly. Initialization uses the version and DPM query functions. Runtime clock updates use hardmin, p-state, CAB, display count, DMCUB wait, and DRR declarations. Watermark notification uses DRAM address setters and the table transfer function.

## State And Persistence
The header itself has no state. Its API methods operate on `clk_mgr_internal`, using cached SMU presence/version state and mutating firmware-side clock/power policy.

## Dependencies
The declarations depend on `os_types.h` and `core_types.h` for integer, bool, and Display Core type definitions. Implementations depend on `dalsmc.h` and `dcn401_smu14_driver_if.h`.

## Risks
Some functions return void even though the underlying transport can fail. Callers therefore cannot always distinguish accepted from dropped firmware policy changes. In contrast, hardmin and query functions return values but use zero as failure in several paths, which can collide with valid disabled/lowest states.

## Test Signals
Compile-time coverage catches signature drift between clock manager and wrapper. Runtime tests should verify that void setters still generate trace events and that failure injection does not leave clock-manager cached state inconsistent with firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr_smu_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_smu14_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_smu14_driver_if.h

## Purpose
This header is a stripped-down SMU 14 driver interface for DCN 4.01 DAL clock-manager needs. It defines PPCLK identifiers, watermark table layout, table type IDs, and the driver interface version checked at runtime.

## Important APIs, Types, And Functions
`SMU14_DRIVER_IF_VERSION` is `0x1`. `PPCLK_e` enumerates clocks with DPM descriptors: GFXCLK, SOCCLK, UCLK, FCLK, DCLK/VCLK, DISPCLK, DPPCLK, DPREFCLK, DCFCLK, DTBCLK, and count. `WatermarkRowGeneric_t` carries a watermark setting and flags. `WatermarksExternal_t` wraps watermark rows plus spare and SMU internal padding. Table IDs include PMFW PPTABLE, combo PPTABLE, watermarks, metrics, driver config, activity monitor coefficients, overdrive, I2C commands, driver info, ECC info, and count.

## Control Flow And Integration
`dcn401_clk_mgr.c` uses `PPCLK_e` to select DPM levels and hardmins. `dcn401_clk_mgr_smu_msg.c` uses `SMU14_DRIVER_IF_VERSION` to validate firmware compatibility and uses `TABLE_WATERMARKS` when transferring the watermark table. Watermark rows are populated by `dcn401_notify_wm_ranges`.

## State And Persistence
The structures describe shared-memory table layout. Firmware reads `WatermarksExternal_t` after the driver writes it into GART memory and sends the DRAM address through SMU messages.

## Dependencies
The header is intentionally standalone apart from fixed-width integer types provided by the compile environment. It is a firmware ABI boundary and must align with SMU expectations.

## Risks
Because it is explicitly stripped down, future code may need fields not present here and duplicate or redefine firmware data elsewhere. `PPCLK_e` numeric values are used in packed SMU parameters and hardmin acknowledgement masks, so changing order is ABI-breaking.

## Test Signals
Version check success, valid watermark transfer, correct DPM queries per `PPCLK_e`, and hardmin status bit matching are the main signals. ABI tests should assert structure sizes and enum numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_smu14_driver_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c

## Purpose
This file implements the DCN 4.2 clock manager. It initializes clock state, reads SMU DPM tables, programs display and bandwidth clocks through PMFW, updates DPP DTOs, handles low-power display idle policy, manages watermark ranges, exposes FPGA and production function tables, and constructs/destroys the DCN 4.2 clock-manager object.

## Important APIs, Types, And Functions
Major functions include `dcn42_update_clocks`, `dcn42_init_clocks`, `dcn42_get_smu_clocks`, `dcn42_get_dpm_table_from_smu`, `dcn42_notify_wm_ranges`, `dcn42_build_watermark_ranges`, `dcn42_update_clocks_update_dpp_dto`, `dcn42_update_clocks_update_dtb_dto`, `dcn42_get_clock_freq_from_clkip`, `dcn42_dump_clk_registers`, `dcn42_set_low_power_state`, `dcn42_update_clocks_fpga`, `dcn42_get_max_clock_khz`, and `dcn42_clk_mgr_construct`.

## Control Flow And Integration
Construction sets register tables, DCCG, SMU presence/version, default DPREF/DTB clocks, BIOS-derived memory parameters, and SMU-derived DPM tables. Initialization resets live clock state, configures DP DTO source clock based on spread spectrum, dumps boot clocks, and tracks whether DTBCLK is enabled.

Runtime `dcn42_update_clocks` first handles Z-state and DTB enable/disable based on `safe_to_lower`, active display detection, and low-power transition state. It then updates DCFCLK and deep-sleep DCFCLK, clamps debug minimums, programs DISPCLK with the DCN 3.5 OTG workaround, manages DPPCLK lowering/raising order relative to DPP DTOs, optionally updates DTB DTO state, and notifies DMCUB with the latest clocks.

SMU clock-table retrieval allocates a GART buffer, transfers `DpmClocks_t_dcn42` from PMFW, logs levels, populates the bandwidth clock table, reverses memory p-state order into ascending table entries, sets WCK ratios, and installs a fixed DTBCLK level.

## State And Persistence
The live clock state is stored in `clk_mgr_base->clks`; bandwidth limits are stored in the static `dcn42_bw_params` object. Watermark notification allocates a GART table, sends it to SMU, and frees it immediately after transfer. Firmware-side persistent state includes clock hardmins, DTB enablement, display idle optimization bits, watermark table contents, and Z-state policy. FPGA mode mutates clock values locally and pushes them through `dm_set_dcn_clocks`.

## Dependencies
The file depends on DCCG, DCE/DCN clock helpers, DCN 4.2 and CLK 15 register headers, `dcn42_smu.c`, DMUB command infrastructure, link service, BIOS integrated info, and DC debug/config flags. It also reuses `dcn35_disable_otg_wa`, showing cross-generation workaround dependency.

## Risks
The production path uses a static `dcn42_bw_params`, which is simple but sensitive to multi-device assumptions. `dcn42_notify_wm_ranges` skips if `WM_A` is already valid, so stale watermark state can suppress resend. DTB DTO update is a no-op for DCN 4.2, but state still tracks DTB enable and reference clock. The constructor calls `dcn42_get_smu_clocks` both inside integrated-info handling and again after setting `bw_params`, so repeated transfers should be harmless but are worth monitoring. Low-power exit is currently empty.

## Test Signals
Validate SMU table parsing, active display detection, low-power idle optimization, DPP DTO cleanup for inactive pipes, DMCUB clock notification, watermark transfer acceptance, DTB enable behavior on hardware with and without DTB, and FPGA clock update behavior. Hardware readback via CLKIP counters is a key diagnostic signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.h

## Purpose
This header declares the DCN 4.2 clock-manager object and public helper surface used by clock-manager selection, SMU table handling, watermark notification, low-power transitions, and FPGA/prod clock update paths.

## Important APIs, Types, And Functions
`DCN42_CLKIP_REFCLK` defines the 48 MHz reference used by CLKIP counter conversion. `struct clk_mgr_dcn42` embeds `clk_mgr_internal` and owns a `dcn42_smu_watermark_set`. `struct dcn42_ss_info_table` contains spread-spectrum lookup information. Public functions include `dcn42_init_clocks`, `dcn42_update_clocks`, `dcn42_clk_mgr_construct`, `dcn42_clk_mgr_destroy`, `dcn42_init_single_clock`, `dcn42_convert_wck_ratio`, `dcn42_build_watermark_ranges`, `dcn42_notify_wm_ranges`, `dcn42_set_low_power_state`, `dcn42_get_max_clock_khz`, `dcn42_get_smu_clocks`, and `dcn42_update_clocks_fpga`.

## Control Flow And Integration
`clk_mgr.c` constructs this manager for DCN 4.2 ASICs. The implementation installs either production or FPGA function tables. External code can query SMU presence, maximum clocks, active display state, and dentist DISPCLK. The header also exposes DPP/DTB DTO update helpers, allowing related code to coordinate DTO programming with clock changes.

## State And Persistence
The object carries base clock-manager state plus SMU watermark memory state. The global `dcn42_ss_info_table` is declared extern and used for spread-spectrum lookup. SMU DPM table transfer uses `struct dcn42_smu_dpm_clks`, forward-declared here to avoid including the full SMU table header in all consumers.

## Dependencies
It depends on `clk_mgr_internal.h` and Display Core types such as `dc`, `dc_state`, `clk_bw_params`, `clk_type`, and `dccg`. It is tightly paired with `dcn42_clk_mgr.c` and `dcn42_smu.h`.

## Risks
The header declares `dcn42_has_active_display` twice, a minor maintenance smell. The broad helper surface exposes internals that could be called out of intended ordering. Since watermark state includes a physical address, constructor/destructor and notify paths must agree on ownership.

## Test Signals
Build tests catch duplicate or mismatched prototypes. Runtime tests should exercise constructor selection, production versus FPGA function tables, helper calls from clock update paths, and destroy behavior after watermark notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_smu.c

## Purpose
This file implements the DCN 4.2 PMFW/DAL mailbox wrapper. It programs PMFW display clocks, hard minimum DCFCLK, deep-sleep DCFCLK, DPPCLK, display idle policy, PME workaround, DRAM table addresses, DPM/watermark table transfers, Z-state support, DTB enablement, and DPREF/DTB clock queries.

## Important APIs, Types, And Functions
The low-level helpers are `dcn42_smu_wait_for_response` and `dcn42_smu_send_msg_with_param`. They use MP 15 registers `MP1_SMN_C2PMSG_71`, `72`, and `73` via `DAL_MSG_REG`, `DAL_RESP_REG`, and `DAL_ARG_REG`. Public wrappers include `dcn42_smu_get_pmfw_version`, `dcn42_smu_set_dispclk`, `dcn42_smu_set_dppclk`, `dcn42_smu_set_hard_min_dcfclk`, `dcn42_smu_set_min_deep_sleep_dcfclk`, `dcn42_smu_set_display_idle_optimization`, `dcn42_smu_enable_phy_refclk_pwrdwn`, `dcn42_smu_enable_pme_wa`, `dcn42_smu_transfer_dpm_table_smu_2_dram`, `dcn42_smu_transfer_wm_table_dram_2_smu`, `dcn42_smu_set_zstate_support`, `dcn42_smu_get_dprefclk`, `dcn42_smu_get_dtbclk`, and `dcn42_smu_set_dtbclk`.

## Control Flow And Integration
Before sending, the wrapper waits until the response register is not `CmdRejectedBusy`, writes busy to clear it, writes the parameter, triggers the message, and waits for a non-busy result. Clock setters convert kHz requests to MHz and return firmware response values in kHz. Table transfers assume the high and low DRAM address messages have already been sent. Z-state support uses the same Z8/Z9/Z10 bit encoding as DCN 3.5.

## State And Persistence
The file owns no heap state. Its effects persist in PMFW until changed: clock hardmins, idle optimization flags, PME restore, table contents, Z-state policy, and DTB state. Debug `disable_timeout` can extend the wait loop indefinitely.

## Dependencies
It depends on MP 15 register headers, register helpers, `dcn42_smu.h`, Display Core logging, and `clk_mgr_internal`. `dcn42_clk_mgr.c` is the main caller.

## Risks
The response model differs from DCN 3.5: busy is `CmdRejectedBusy`, and any other value exits the wait loop. If firmware returns a prereq or unknown-command code before send, the code logs a warning but still sends. Failed watermark transfer is warned and reset to OK, while other failed commands rely on warnings/asserts rather than structured recovery. There is an unused `dcn42_dpia_host_router_bw` union, suggesting copied or incomplete functionality.

## Test Signals
Check PMFW version detection, busy retry behavior, failed watermark transfer warning, correct clock unit conversions, DTB on/off transitions, Z-state bit parameters, and logs showing requested versus actual clock values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_smu.h

## Purpose
This header defines the DCN 4.2 PMFW interface subset used by the display clock manager, including DPM and watermark table layouts plus SMU wrapper prototypes.

## Important APIs, Types, And Functions
`PMFW_DRIVER_IF_VERSION` is `7`. The file defines clock table sizes, `DSPCLK_e`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, `Watermarks_t`, `WCK_RATIO_e`, `MemPstateTable_t`, and `DpmClocks_t_dcn42`. `DpmClocks_t_dcn42` contains DCFCLK, DISPCLK, DPPCLK, SOCCLK, VCN, VPE, FCLK frequency/voltage, SOC voltage, memory p-state table, enabled level counts, and min/max GFX clocks. `struct dcn42_smu_dpm_clks` couples a DPM table pointer with a GPU address.

Function prototypes expose PMFW version query, clock setters, display idle optimization, PHY refclk powerdown, PME workaround, DRAM address setup, DPM and watermark transfer, Z-state control, DTB control, and DPREF/DTB queries.

## Control Flow And Integration
`dcn42_clk_mgr.c` allocates a `DpmClocks_t_dcn42` buffer, transfers it from SMU through the declared address and transfer functions, and maps it into bandwidth parameters. Watermark notification builds `struct dcn42_watermarks` and transfers it through the same address protocol. Runtime updates call the declared setters for clock and power policy changes.

## State And Persistence
The structures model shared firmware state. `DpmClocks_t_dcn42` is a point-in-time snapshot from PMFW. `dcn42_watermarks` is written by the driver and consumed by firmware. `display_idle_optimization` encodes display-off and S0i2 readiness state.

## Dependencies
It includes `os_types.h` and relies on Display Core users to supply `clk_mgr_internal` and `dcn_zstate_support_state`. It is an ABI boundary with PMFW and must remain layout-compatible.

## Risks
The header contains some copied/commented artifacts and sparse comments around throttler status, suggesting the interface may still be evolving. `DpmClocks_t_dcn42` parsing assumes firmware level counts are trustworthy except where implementation clamps memory p-states. Incorrect WCK ratio values fall back to 1:1 in the clock manager, which can mask firmware data issues.

## Test Signals
Validate `PMFW_DRIVER_IF_VERSION`, table sizes, DPM level counts, memory p-state order and WCK ratios, watermark row encoding, and that DPREF/DTB query functions return sensible nonzero values on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_smu.h -->
