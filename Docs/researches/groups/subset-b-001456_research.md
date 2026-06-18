# subset-b-001456 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c

## Purpose
This file builds the AMD Display Core resource pool for DCN 3.0.1 / Vangogh. It binds generated register-offset tables to hardware object constructors, publishes `dcn301_create_resource_pool()`, and installs the DCN301 `resource_funcs` vtable used by mode validation, pipe allocation, DML population, link encoder creation, writeback, and destruction.

## Important APIs, Types, And Functions
`res_cap_dcn301` defines a 4 pipe/OTG/OPP/audio/stream-encoder pool, 1 DWB, 4 DDC engines, 16 VMIDs, 2 MPC 3D LUTs, and 3 DSC blocks. `plane_cap`, `debug_defaults_drv`, and `config_defaults` seed global DC capabilities. Factory helpers allocate and construct DPP, OPP, AUX, I2C, MPC, Hubbub, DIO, timing generator, link encoder, panel control, audio, VPG, AFMT, stream encoder, HWSEQ, HUBP, DWB, MMHUBBUB, DSC, and clock-source objects. `dcn301_resource_construct()` is the core initializer; `dcn301_destruct()` and `dcn301_destroy_resource_pool()` release every sub-object.

## Control Flow
Pool creation allocates `struct dcn301_resource_pool`, then calls `dcn301_resource_construct()`. Construction sets BIOS scratch registers, adjusts PLL count for a specific Vangogh device ID, assigns resource caps/functions, hardcodes display and color capabilities, reads LTTPR flags from VBIOS, initializes VM helpers, creates clock sources and DCCG, initializes the Vangogh DML/SOC bounding box, applies watermark ranges through PP/SMU when enabled, reads disabled pipe fuses, initializes DML, IRQ service, Hubbub, DIO, per-pipe HUBP/DPP/OPP/TG sets for unfused pipes, ABM, MPC, DSC, writeback, AUX/I2C, and common resources via `resource_construct()`. Failure jumps to `create_fail`, which destructs partial state.

## State And Persistence
The file mutates persistent in-memory DC state: `dc->caps`, `dc->debug`, `dc->check_config`, `dc->cap_funcs`, `dc->dml`, `dc->vm_helper`, `ctx->dc_bios->regs`, and `dcn3_01_ip` / `dcn3_01_soc`. Pipe fuse handling reduces `dcn3_01_ip.max_num_dpp` and `max_num_otg`, then updates `pool->base.pipe_count`, `timing_generator_count`, and `mpcc_count` to the live hardware count. The code does not persist to disk; persistence is kernel object lifetime plus hardware/firmware-visible registers and SMU watermark programming.

## Dependencies And Integration Points
The implementation depends on DC core resource helpers, DCE/DIO/DMUB objects, IRQ service `dal_irq_service_dcn30_create()`, generated Vangogh/DCN301/NBIO/DPCS register headers, DML/FPU wrappers, VBIOS callbacks, PP/SMU watermark callbacks, and generic VM helper initialization. `dcn301_res_pool_funcs` integrates DCN301 with common DC algorithms: DCN30 bandwidth validation, DCN301 watermark/DLG calculation, DML pipe population, pipe allocation/release, stream add/remove, DSC attachment, writeback DML population, MCIF arbitration, post-blend 3D LUT management, unknown-plane patching, tiling defaults, and startup selection.

## Risks
Key risks are register-table drift, mismatched resource counts, and partial-construction leaks. The destructor destroys IRQ service inside the per-pipe loop after checking `pool->base.irqs`, so the pointer must be nulled by `dal_irq_service_destroy()` to avoid repeated destruction. `init_soc_bounding_box()` logs invalid ASIC revisions but its return value is not enforced by construction. `dcn3_01_ip` is global and is patched for fuses, so repeated initialization paths must not accidentally compound reductions. Watermark programming depends on non-null PP/SMU hooks.

## Test Signals
Useful signals include successful driver probe on Vangogh, no `DC: failed to create ...` logs, correct pipe count when fuses disable pipes, DCN30 validation passing for single/multi-display modes, no DML underflow warnings, working AUX/I2C/DDC, PSR/ABM behavior through DMUB ABM, DSC modes using up to 3 DSCs, DWB creation, and clean unload with KASAN/KMEMLEAK enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.h

## Purpose
This header exposes the DCN301 resource-pool constructor and the minimal DCN301-specific pool wrapper used by the implementation file. It is the public include boundary for other Display Core initialization code that needs to create a Vangogh/DCN3.0.1 resource pool.

## Important APIs, Types, And Functions
The header forward-declares `struct dc`, `struct resource_pool`, and DML pipe parameter structures. It declares external DML globals `dcn3_01_ip` and `dcn3_01_soc`, which the C file patches during initialization. `struct dcn301_resource_pool` embeds `struct resource_pool base`, allowing DC core code to treat it polymorphically. `dcn301_create_resource_pool(const struct dc_init_data *init_data, struct dc *dc)` is the only exported constructor.

## Control Flow
Consumers include this header, call `dcn301_create_resource_pool()`, and receive a `struct resource_pool *`. The actual allocation, capability setup, object construction, and cleanup are hidden in `dcn301_resource.c`; the header provides no inline logic.

## State And Persistence
The header itself stores no state. It defines the structural relationship between the DCN301-specific allocation and generic `resource_pool` lifetime, and exposes mutable DML globals owned elsewhere in the DCN301/DML code.

## Dependencies And Integration Points
The dependency on `core_types.h` brings in `struct dc_init_data` and DC type definitions. Integration is with ASIC-family resource selection code that chooses the DCN301 constructor based on detected hardware, and with DML/FPU code that provides `dcn3_01_ip` and `dcn3_01_soc`.

## Risks
Because no `TO_DCN301_RES_POOL` macro is exported here, only the C file's private macro should downcast the base pointer. Changes to the embedded `base` layout or constructor signature would ripple into DC creation code. The extern DML globals are mutable and must remain aligned with the C file's initialization assumptions.

## Test Signals
Compile coverage is the primary signal: the selected ASIC init path must include the header and link against `dcn301_create_resource_pool()`. Runtime probe should return a non-null pool and later destroy it through the installed `resource_funcs.destroy` callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c

## Purpose
This file constructs the DCN 3.0.2 resource pool for Dimgrey Cavefish-class hardware. It is similar to DCN30 but sets DCN302 register tables, five display pipes, DMUB PSR support, OEM DDC service support, panel defaults, and DCN302-specific bandwidth-bounding-box updates.

## Important APIs, Types, And Functions
`res_cap_dcn302` advertises 5 timing generators, OPPs, planes, audio blocks, stream encoders, DDC engines, and DSC blocks, plus 1 DWB and 16 VMIDs. Static factories create DIO, Hubbub, VPG, AFMT, audio, stream encoders, clock sources, HWSEQ, HUBP, DPP, OPP, TG, MPC, DSC, DWB, MMHUBBUB, AUX, I2C, link encoders, and panel controls. `dcn302_update_bw_bounding_box()` wraps `dcn302_fpu_update_bw_bounding_box()`. `dcn302_resource_construct()` and `dcn302_resource_destruct()` own lifecycle, and `dcn302_create_resource_pool()` is the external constructor.

## Control Flow
The constructor allocates a generic `struct resource_pool`, sets BIOS register pointers, assigns `res_cap_dcn302` and `dcn302_res_pool_funcs`, fills global DC caps and color capabilities, reads VBIOS LTTPR state, installs production debug defaults, initializes VM helpers, creates five PHY PLL clock sources plus a DP DTO source, creates DCCG, initializes the Dimgrey Cavefish SOC/IP bounding box, initializes DML, creates IRQ/Hubbub/DIO, then creates per-pipe HUBP/DPP and per-resource OPP/TG arrays. It also creates DMUB PSR, ABM per timing generator, MPC, all DSCs, writeback, AUX/I2C, common resources via `resource_construct()`, HW sequencer, plane caps, and optionally an OEM DDC service from VBIOS firmware info.

## State And Persistence
State is stored in `dc->caps`, `dc->debug`, `dc->check_config`, `dc->dml`, `dc->cap_funcs`, `pool` arrays, optional `pool->oem_device`, and global `dcn3_02_ip` / `dcn3_02_soc`. `init_soc_bounding_box()` patches DML state with VBIOS SOC BB info and `dc->config.clamp_min_dcfclk`. No disk state is written.

## Dependencies And Integration Points
The file integrates generated DCN302/NBIO/DPCS register headers, DML/FPU code, DCN30 base hardware blocks, DMUB PSR/ABM, link service OEM DDC creation, IRQ service `dal_irq_service_dcn302_create()`, and the common resource construction framework. `dcn302_res_pool_funcs` connects common DC code to DCN30 validation, DML pipe and writeback population, MCIF arbitration, DSC attachment, post-blend LUT management, panel defaults, bounding-box updates, tiling defaults, and pipe allocation.

## Risks
`init_soc_bounding_box()` can return false for unexpected ASIC revisions, but construction continues after calling it. Destruction calls IRQ destroy inside the pipe loop and relies on pointer nulling. The OEM DDC service is only destroyed if it was created and if link service callbacks remain valid. Resource counts must match register arrays exactly; mismatches would index beyond static arrays. The `num_mpc_3dlut` comment in capability setup says 3 while caps say 2, which is a documentation drift risk.

## Test Signals
Probe on Dimgrey Cavefish should create five pipes and five DSCs without error logs. Mode validation should use DCN30 validation and DCN302 FPU bounding-box updates. PSR default policy should be visible through panel defaults. OEM I2C firmware configurations should create and destroy `pool->oem_device`. Hotplug/AUX/I2C, DSC, DWB, and multi-display 8K limits are important runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.h

## Purpose
This header declares the DCN302 resource-pool entry points and exposes the DCN302 DML IP/SOC bounding-box globals used by the implementation.

## Important APIs, Types, And Functions
It includes `core_types.h`, declares extern `dcn3_02_ip` and `dcn3_02_soc`, exposes `dcn302_create_resource_pool(const struct dc_init_data *init_data, struct dc *dc)`, and exposes `dcn302_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)`.

## Control Flow
ASIC initialization calls `dcn302_create_resource_pool()` after matching DCN302 hardware. Clock-manager or bandwidth code can call `dcn302_update_bw_bounding_box()` when clock/bandwidth parameters change. All actual control flow lives in the C file.

## State And Persistence
The header does not own state but exposes mutable DML globals and the update hook that mutates `dc->dml`/SOC bounding-box data through FPU code.

## Dependencies And Integration Points
The declarations integrate the DCN302 resource implementation with Display Core initialization, clock-bandwidth update paths, and DML/FPU providers for `dcn3_02_ip` and `dcn3_02_soc`.

## Risks
The header exports an update function that assumes the DCN302 FPU implementation and global bounding-box structures are linked. Misusing it for another ASIC family would patch the wrong DML tables.

## Test Signals
Build/link checks should ensure both exported symbols resolve. Runtime signal is a non-null resource pool and successful bounding-box refresh when `clk_bw_params` are updated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c

## Purpose
This file constructs the DCN 3.0.3 resource pool for Beige Goby-class hardware. It is a smaller DCN30-derived implementation with two display pipes and DCN303-specific register tables, IRQ service, FPU bounding-box update, and bandwidth defaults.

## Important APIs, Types, And Functions
`res_cap_dcn303` declares 2 timing generators, OPPs, video planes, audio blocks, stream encoders, DDC engines, and DSC blocks, plus 1 DWB, 16 VMIDs, and 1 MPC 3D LUT. The implementation provides factories for all pool hardware objects and installs `dcn303_res_pool_funcs`. Exported `dcn303_update_bw_bounding_box()` wraps `dcn303_fpu_update_bw_bounding_box()`, and `dcn303_create_resource_pool()` allocates the generic pool.

## Control Flow
`dcn303_resource_construct()` sets BIOS scratch registers, assigns caps/functions, fills display/color caps, enables `dc_mode_clk_limit_support`, reads LTTPR VBIOS state, applies debug/config defaults, initializes VM helpers, creates two PHY PLL sources and one DP DTO source, creates DCCG, initializes DCN303 SOC/IP data, initializes DML, creates DCN303 IRQ service, Hubbub, DIO, two HUBP/DPP pairs, two OPPs, two TGs, PSR, ABMs, MPC, DSCs, writeback resources, AUX/I2C, and common stream/audio/LUT resources. It constructs the HW sequencer, applies plane caps, sets max ODM combine factor, and optionally creates OEM DDC service.

## State And Persistence
The file mutates `dc->caps`, `dc->config`, `dc->debug`, `dc->check_config`, `dc->dml`, `dc->cap_funcs`, `pool` object arrays, `pool->psr`, `pool->oem_device`, and `dcn3_03_ip` / `dcn3_03_soc`. There is no durable disk persistence.

## Dependencies And Integration Points
Dependencies include Sienna Cichlid/Beige Goby register headers, DCN303 DCCG/IRQ/FPU code, DCN30 block constructors, DCE AUX/I2C/audio/panel-control implementations, DMUB PSR/ABM, DML, link service, and common resource helpers. The installed resource vtable mostly uses DCN30 algorithms, with DCN303-specific bounding-box update and panel defaults.

## Risks
The invalid bounding-box log string contains `/n` instead of `\n`, reducing log readability. As in DCN302, `init_soc_bounding_box()` failure is not fatal. Resource counts are small; any accidental reuse of DCN302 five-instance tables would overrun, while missing Beige Goby register coverage would fail construction. The destructor relies on common destroy functions and pointer nulling for repeated/partial cleanup safety.

## Test Signals
Expected signals are two working pipes, two DSC instances, successful Beige Goby probe, DCN303 IRQ creation, PSR/ABM allocation, correct OEM DDC behavior, successful DCN30 mode validation using DCN303 DML tables, and clean unload. Multi-display tests should emphasize two-pipe limits, DSC use, DWB, and clock-limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.h

## Purpose
This header declares the DCN303 resource constructor and bandwidth-bounding-box update hook for Beige Goby / DCN3.0.3 resource setup.

## Important APIs, Types, And Functions
It includes `core_types.h`, declares extern DML globals `dcn3_03_ip` and `dcn3_03_soc`, declares `dcn303_create_resource_pool(const struct dc_init_data *init_data, struct dc *dc)`, and declares `dcn303_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)`.

## Control Flow
Display Core ASIC selection calls the constructor; bandwidth/clock update paths call the update hook. The header contributes declarations only.

## State And Persistence
No direct state is stored. The extern DML symbols are mutable global state owned by DCN303 DML code and patched by the C implementation.

## Dependencies And Integration Points
The header is a narrow boundary between ASIC init code, resource construction, and DCN303 FPU/DML code. It depends on `core_types.h` for DC and clock-bandwidth type definitions.

## Risks
Because DCN302 and DCN303 headers have nearly identical APIs, wiring the wrong constructor or update hook would compile but initialize the wrong resource shape. The DML externs must match the DCN303 implementation.

## Test Signals
Compile/link checks for exported symbols, plus runtime probe selecting DCN303 and using two-pipe caps, are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c

## Purpose
This file constructs and manages the DCN 3.1 resource pool for Yellow Carp-class APUs. It extends DCN30-style resources with DP 2.0/HPO encoders, DPIA/USB4 support, DMUB PSR and Replay objects, DCN31 DML population and validation wrappers, DET-buffer policy, and encoder-switch state updates.

## Important APIs, Types, And Functions
`res_cap_dcn31` declares 4 OTGs/OPPs/planes, 5 audio/stream/dig-link/DDC resources, 4 HPO DP stream encoders, 2 HPO DP link encoders, 5 PLLs, 1 DWB, 16 VMIDs, 2 3D LUTs, and 3 DSCs. Public functions include `dcn31_validate_bandwidth()`, `dcn31_calculate_wm_and_dlg()`, `dcn31_populate_dml_pipes_from_context()`, `dcn31_populate_dml_writeback_from_context()`, `dcn31_set_mcif_arb_params()`, `dcn31_get_det_buffer_size()`, `dcn31_create_resource_pool()`, and `dcn31_update_dc_state_for_encoder_switch()`. Static factories create DCN31 HUBP/Hubbub/TG/DCCG/DIO/link/HPO/audio/VPG/AFMT/APG/HWSEQ objects.

## Control Flow
`dcn31_create_resource_pool()` allocates `struct dcn31_resource_pool` and calls `dcn31_resource_construct()`. Construction sets BIOS registers, caps/functions, APU and DP2/HPO capabilities, color caps, host-router/DPIA counts, LTTPR defaults, debug/config defaults, VM helpers, five pixel PLL sources with B0-specific PLL remapping, a DP DTO source, DCCG, IRQ, Hubbub, DIO, per-pipe HUBP/DPP, OPP, TG, PSR, Replay, ABM, MPC, DSC, DWB/MMHUBBUB, AUX/I2C, optional USB4 DPIA counts for Yellow Carp B0 and GC 11.0.1, common resources, HW sequencer, plane caps, and `dc->dcn_ip->max_num_dpp`.

## State And Persistence
State lives in the resource pool arrays, HPO encoder arrays, `dc->caps`, `dc->config`, `dc->debug`, `dc->dml`, `dc->cap_funcs`, and `dc->dcn_ip`. `dcn31_populate_dml_pipes_from_context()` mutates DML pipe parameters: GPUVM/hostVM flags, immediate flip, unbounded request mode, vfront porch, DCC rate, DSC input bpc, and DET buffer size. It adjusts DET size for single non-video planes, CRB allocation policy, and multi-stream upscale cases. No filesystem persistence exists.

## Dependencies And Integration Points
The file depends on Yellow Carp/DCN312/NBIO/DPCS/MMHUB register headers, DCN31 DCCG/Hubbub/HUBP/OPTC/HPO/APG/link/panel code, DCN30 base blocks, DCN31 FPU code, link encoder configuration, DMUB PSR/Replay/ABM, DML, and common DC resource helpers. `dcn31_res_pool_funcs` wires the pool to DP2 encoder assignment/unassignment, bandwidth validation, DML population, writeback/MCIF wrappers, DET query, encoder-switch update, tiling defaults, and pipe pixel-clock parameter building.

## Risks
The constructor has many hardware-revision branches, especially PLL remapping and DPIA count assignment, so ASIC ID drift is risky. HPO stream encoder VPG/APG mapping must match register block numbering. `dcn31_validate_bandwidth()` allocates a pipe array and depends on FPU sections around validation; non-FPU builds only warn/assert for encoder-switch updates. Destruction handles many nested objects, including HPO VPG/APG children, and relies on pointer nulling. DET policy affects underflow risk and is sensitive to format/upscale decisions.

## Test Signals
Signals include probe on Yellow Carp A0/B0, DP1 to DP2 retraining with audio rebuilt, HPO stream/link encoder allocation, DPIA/USB4 displays, PSR and Replay object creation, DML validation under multi-stream/upscaled/immediate-flip cases, expected DET buffer size changes, DSC on eDP/DP, and clean unload. KASAN/KMEMLEAK and mode-validation tracing are valuable for constructor/destructor and bandwidth paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.h

## Purpose
This header is the public interface for DCN31 resource construction and resource-specific helper operations. It also carries temporary B0-specific PHY PLL pixel-clock register definitions used before switching fully to DCN313 headers.

## Important APIs, Types, And Functions
`TO_DCN31_RES_POOL()` downcasts a generic pool to `struct dcn31_resource_pool`, which embeds `struct resource_pool base`. It declares extern `dcn3_1_ip`. Public APIs include resource creation, bandwidth validation, watermark/DLG calculation, DML pipe population, writeback DML population, MCIF arbitration setup, DET-buffer query, and `dcn31_update_dc_state_for_encoder_switch()` for DP1/DP2 encoder-rate transitions.

## Control Flow
The header enables other DC code to call DCN31-specific validation/population helpers through either direct declarations or the `resource_funcs` table installed by the C file. The encoder-switch function is called when a link changes mode/rate and needs current-state pipe pixel-clock and audio output updates.

## State And Persistence
No state is allocated by the header. It defines access to the DCN31 wrapper pool and exposes the mutable DML IP global. The temporary register constants encode hardware register addresses, shifts, and masks used by implementation code.

## Dependencies And Integration Points
It depends on `core_types.h` for DC core structures and integrates with DML, resource construction, link training/retraining, writeback, MCIF arbitration, and DET policy code. The register constants bridge missing/generated header coverage for Yellow Carp B0 PHY PLL resync controls.

## Risks
Temporary register definitions can become stale when generated headers change. Direct exports of many helpers increase the chance of cross-generation misuse. The downcast macro requires that the generic pointer really point to `struct dcn31_resource_pool`.

## Test Signals
Compile coverage should catch signature drift. Runtime signals include correct resource creation, validation callbacks, DET query behavior, and successful DP encoder switching with pixel-rate/audio recalculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c

## Purpose
This file constructs the DCN 3.1.4 resource pool. It is a DCN31-derived implementation with DCN314 register tables, four-pipe display resources, five audio/stream/link/DDC resources, four DSCs, DP2/HPO and DPIA support, seamless ODM/z-state defaults, DCN314 DML population and bounding-box updates, and a DCN314-specific bandwidth validation mode.

## Important APIs, Types, And Functions
`res_cap_dcn314` declares 4 OTGs/OPPs/planes/HPO streams/DSCs, 5 audio/stream/dig-link/DDC/PLL resources, 2 HPO DP link encoders, 1 DWB, 16 VMIDs, and 2 MPC 3D LUTs. `dcn314_validate_bandwidth()` is exported and calls `dcn30_internal_validate_bw()` with self-refresh-only support disabled. `dcn314_create_resource_pool()` allocates `struct dcn314_resource_pool`. Static functions create DCN31-derived DPP/OPP/AUX/I2C/MPC/Hubbub/TG/link/HPO/panel/audio/VPG/AFMT/APG resources plus DCN314 DIO, DSC, DCCG, HWSEQ, stream encoders, DML pipe population, and bounding-box updates.

## Control Flow
Construction sets BIOS registers, assigns caps/functions, enables 4-to-1 MPC, DP HPO, eDP DSC, seamless ODM, z-state support, color caps, host-router/DPIA counts, LTTPR awareness, debug defaults, then deliberately disables pipe power gating and root-clock optimization. It initializes VM helpers, creates five PLL clock sources and a DP DTO source, creates DCCG314, DCN314 IRQ service, Hubbub, DIO, per-pipe HUBP/DPP, OPP, TG, PSR, Replay, ABM, MPC, all four DSCs, DWB/MMHUBBUB, AUX/I2C, sets `usb4_dpia_count = 4`, delegates common resources to `resource_construct()`, constructs the DCN314 HW sequencer, applies plane caps, and updates `dc->dcn_ip->max_num_dpp`.

## State And Persistence
State is in the pool, `dc->caps`, `dc->config`, `dc->debug`, `dc->check_config`, `dc->dml`, `dc->cap_funcs`, and `dc->dcn_ip`. `dcn314_populate_dml_pipes_from_context()` and `dcn314_update_bw_bounding_box()` delegate to DCN314 FPU helpers. Debug defaults encode memory low-power, root-clock optimization, z-state, PSR/Replay skip behavior, p-state, and minimum display clock policy. There is no disk persistence.

## Dependencies And Integration Points
The file uses DCN314 init/DCCG/IRQ/FPU headers, DCN31 HPO/APG/link/panel infrastructure, DCN30 base blocks, DML, DMUB PSR/Replay/ABM, generated register headers, link encoder config, and common DC resource code. `dcn314_res_pool_funcs` integrates DCN314 with DCN31-style encoder assignment, panel defaults, DET buffer query, DP encoder switching, pipe pixel-clock parameter building, and DCN314-specific DML/bounding-box callbacks.

## Risks
The implementation intentionally overrides debug defaults by disabling DPP/HUBP power gating and root-clock optimization after applying production defaults, which can surprise power-management expectations. HPO VPG mapping differs from comments by using offset `+5` while documenting actual VPG 6-9 mapping. `dcn314_get_preferred_eng_id_dpia()` indexes a fixed four-entry table without local bounds checking, relying on callers to pass valid DPIA indexes. Validation disables self-refresh-only support, so behavior differs from DCN31.

## Test Signals
Important signals are DCN314 probe, four-pipe/four-DSC operation, DP2/HPO displays, four DPIA/USB4 ports, correct preferred encoder selection for DPIA indexes 0-3, PSR/Replay behavior, seamless ODM boot, z-state transitions, validation failures/successes under self-refresh and full-programming modes, and clean unload with HPO nested objects released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.h

## Purpose
This header declares the public DCN314 resource interfaces and wrapper type used by the DCN314 implementation and ASIC initialization code.

## Important APIs, Types, And Functions
It includes `core_types.h`, declares extern `dcn3_14_ip` and `dcn3_14_soc`, defines `TO_DCN314_RES_POOL()` for downcasting from `struct resource_pool`, defines `struct dcn314_resource_pool { struct resource_pool base; }`, declares `dcn314_validate_bandwidth()`, and declares `dcn314_create_resource_pool()`.

## Control Flow
ASIC resource selection calls `dcn314_create_resource_pool()`. The resource vtable installed by the C file can call back into `dcn314_validate_bandwidth()` for mode validation. No inline logic exists in the header.

## State And Persistence
The header does not allocate state. It exposes the DCN314 wrapper shape and mutable DML IP/SOC globals used during resource construction and validation.

## Dependencies And Integration Points
The header integrates DCN314 resource code with DC core initialization, validation callers, and DCN314 DML/FPU providers. The downcast macro is used by destruction and internal code that needs the wrapper allocation.

## Risks
The downcast macro assumes the pool pointer came from `dcn314_create_resource_pool()`. The validation declaration is generation-specific; wiring it into the wrong resource table would apply DCN314 validation semantics, including no self-refresh-only support, to another ASIC.

## Test Signals
Build/link signals should confirm the constructor and validation symbols resolve. Runtime probe should return a non-null pool, and validation callbacks should report `DC_OK` or `DC_FAIL_BANDWIDTH_VALIDATE` through the DCN314 path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.h -->
