# subset-b-001453 Research

Grouped research for the requested AMD Display Core OPTC, power-gating, resource, and OS glue files. Each section preserves the source path as its document title and is wrapped for deterministic split into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.c

## Purpose
Implements the DCN 3.1 OPTC timing-generator operations used by AMD Display Core for enabling/disabling OTG, ODM combine setup, DRR programming, ODM reset, and register-state readback. The file installs a `timing_generator_funcs` vtable in `dcn31_timing_generator_init()` and mostly reuses DCN1/DCN2/DCN3 helpers while overriding DCN31-specific ODM, DRR, disable, and diagnostics behavior.

## Important APIs, Types, and Functions
Key exported functions are `dcn31_timing_generator_init()`, `optc31_immediate_disable_crtc()`, `optc31_set_drr()`, `optc3_init_odm()`, `optc31_read_otg_state()`, and `optc31_read_reg_state()`. Static vtable functions include `optc31_set_odm_combine()`, `optc31_enable_crtc()`, and `optc31_disable_crtc()`. The code operates on `struct timing_generator`, downcasts through `DCN10TG_FROM_TG()` to `struct optc`, and uses register helper macros (`REG_UPDATE`, `REG_SET`, `REG_GET`, `REG_WAIT`, sequenced register writes).

## Control Flow and State
Enable flow selects the local OPP source, enables VTG, then enables `OTG_MASTER_EN` through a register sequence. Disable flow clears all ODM segment sources to `0xf`, clears `OPTC_MEM_SEL`, disables `OTG_MASTER_EN` and VTG, waits for `OTG_BUSY == 0`, and clears underflow. Immediate disable differs by forcing disable point 0 and skipping the wait in diagnostic environment. ODM combine computes `OPTC_MEM_SEL` from segment width and OPP count, programs two- or four-segment source selection, sets segment width, and records `optc1->opp_count`. DRR programming sets mid/min/max vertical totals, configures TRIGA manual trigger masking, and clears min/max selection when disabled. Readback functions snapshot live OTG status/timing fields and a broad `dcn_optc_reg_state` register dump for diagnostics.

## Dependencies and Integration Points
Includes `dcn30_optc.h`, `reg_helper.h`, `dc.h`, and `dcn_calc_math.h`; the vtable references helpers from DCN10/DCN20/DCN30 (`optc1_*`, `optc2_*`, `optc3_*`). Resource files create OPTC instances, assign generated register/shift/mask tables from the matching header, and call this init function to bind behavior.

## Risks and Test Signals
Risks center on incorrect ODM memory-mask allocation, disable waits timing out, DRR off-by-one programming, and stale register-state mappings. Useful tests are display mode enable/disable, ODM 2:1 and 4:1 modes, VRR/DRR transitions with manual trigger, CRC and underflow debug checks, suspend/resume, and register-readback validation against hardware traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.h

## Purpose
Defines the DCN 3.1 OPTC register list, field shift/mask list, and public entry points consumed by DCN31 resource construction and later generation OPTC implementations. It is a hardware contract header rather than an algorithmic module.

## Important APIs, Types, and Macros
`OPTC_COMMON_REG_LIST_DCN3_1(inst)` maps the OTG, ODM, VTG, GSL, CRC, DSC, DWB, DRR, and interrupt registers for one OPTC instance. `OPTC_COMMON_MASK_SH_LIST_DCN3_1(mask_sh)` enumerates field masks and shifts needed by `reg_helper` calls, including update locks, timing registers, CRC windows, GSL, DSC format, ODM segment source fields, memory selection, DRR trigger windows, and update-pending fields. Public prototypes export `dcn31_timing_generator_init()`, `optc31_immediate_disable_crtc()`, `optc31_set_drr()`, `optc3_init_odm()`, `optc31_read_otg_state()`, and `optc31_read_reg_state()`.

## Control Flow and State
The header has no runtime control flow. Its state significance is the fixed mapping between generated ASIC register names and the `struct optc` register/shift/mask tables. Consumers rely on these macro expansions to populate static register tables; if a field is missing here, code paths reading or writing it will either fail to compile or silently use an incompatible generation-specific table.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h` for base OPTC types, register-table structures, and shared function prototypes. DCN314, DCN32, DCN35, DCN401, and DCN42 implementation files reuse functions declared here, especially DRR and readback helpers. Resource generation code pairs this header's lists with ASIC-specific register definitions.

## Risks and Test Signals
Primary risk is register drift: wrong field names, duplicate register entries, or omitted masks can corrupt timing, CRC, ODM, or update-lock behavior. Build coverage catches many issues through macro expansion. Runtime signals include successful mode-set, CRC capture, DRR, GSL, DSC, and interrupt programming on DCN31 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn314/dcn314_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn314/dcn314_optc.c

## Purpose
Implements DCN 3.14 timing-generator behavior. It derives from DCN31 but changes ODM memory allocation for the DCN314 memory organization and uses a compact vtable tailored to this ASIC generation.

## Important APIs, Types, and Functions
The public function is `dcn314_timing_generator_init()`. Static overrides are `optc314_set_odm_combine()`, `optc314_enable_crtc()`, `optc314_disable_crtc()`, `optc314_phantom_crtc_post_enable()`, `optc314_set_odm_bypass()`, and `optc314_set_h_timing_div_manual_mode()`. The vtable also imports `optc31_immediate_disable_crtc()`, `optc31_set_drr()`, `optc3_init_odm()`, and DCN31 readback helpers.

## Control Flow and State
ODM combine computes active width as `segment_width * opp_cnt`, derives an ODM memory count in 2048-pixel chunks, and selects memory bitmasks for two or four OPP paths. It programs `OPTC_DATA_SOURCE_SELECT`, `OPTC_WIDTH_CONTROL`, and `OTG_H_TIMING_CNTL`, then updates `optc1->opp_count`. Enable and disable mirror the DCN31 flow, but disable does not clear ODM source/memory registers and does not clear underflow in this file. Phantom enable immediately disables the OTG and waits for busy to clear. ODM bypass selects the local OPTC instance, masks unused segments, restores horizontal timing division from pixel-container mode, clears ODM memory, and records one OPP.

## Dependencies and Integration Points
Includes DCN30 and DCN31 OPTC headers for shared implementations, `reg_helper.h` for MMIO access, and `dc.h`. Its vtable is selected by DCN314 resource initialization and participates in the same Display Core `timing_generator` polymorphic API as older generations.

## Risks and Test Signals
Risk areas are the memory mask thresholds for 4K/8K/12K paths, the less aggressive disable sequence compared with DCN31/DCN32, and manual horizontal timing division control. Tests should cover single-pipe bypass, ODM 2:1/4:1, phantom pipe enable/disable, VRR/DRR via inherited DCN31 logic, and mode-set teardown on real DCN314 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn314/dcn314_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn314/dcn314_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn314/dcn314_optc.h

## Purpose
Provides DCN 3.14 OPTC register and field metadata plus the timing-generator init prototype. It adapts the DCN31 register model to DCN314 by defining the exact register list and mask/shift expansion needed by the DCN314 resource tables.

## Important APIs, Types, and Macros
`OPTC_COMMON_REG_LIST_DCN3_14(inst)` lists OTG timing/update-lock/status, ODM input/memory/format, VTG, GSL, CRC, DSC, DRR, pipe update, and interrupt destination registers. `OPTC_COMMON_MASK_SH_LIST_DCN3_14(mask_sh)` supplies the field names used by `REG_GET/SET/UPDATE`, including `OTG_CURRENT_MASTER_EN_STATE` absence compared with some newer headers, ODM segment fields, `OTG_H_TIMING_DIV_MODE_MANUAL`, and pipe update status fields. The only prototype is `dcn314_timing_generator_init()`.

## Control Flow and State
The header only defines compile-time register tables. Its state behavior is indirect: it controls which fields the DCN314 implementation can persist into hardware registers and which readback/update paths can be wired into the vtable.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h`. The DCN314 implementation relies on this header, while resource construction supplies generated arrays using these macro expansions. Shared helper functions from DCN10/DCN20/DCN30/DCN31 assume these masks are consistent with the fields they access.

## Risks and Test Signals
The main risk is mismatch between this register contract and the ASIC register headers. Build failures catch missing symbols, but incorrect field selection can surface only as timing, ODM, CRC, DRR, or interrupt malfunction. Regression signals include successful compilation for DCN314 configs and hardware mode-set/VRR/CRC tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn314/dcn314_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.c

## Purpose
Implements DCN 3.2 OPTC operations, extending the DCN31/DCN314 model with ODM segment query/wait support, DMUB-assisted DRR manual trigger for FAMS/memory-clock switching, phantom OTG disable, and richer double-buffer pending hooks.

## Important APIs, Types, and Functions
Public functions are `dcn32_timing_generator_init()`, `optc32_set_h_timing_div_manual_mode()`, `optc32_get_odm_combine_segments()`, `optc32_set_odm_bypass()`, and `optc32_wait_odm_doublebuffer_pending_clear()`. Static generation-specific functions include `optc32_set_odm_combine()`, enable/disable, phantom helpers, `optc32_setup_manual_trigger()`, and `optc32_set_drr()`.

## Control Flow and State
ODM combine uses the 2048-pixel memory-count scheme and programs memory mask, segment sources, segment width, horizontal timing division, and `opp_count`. Segment readback converts `OPTC_NUM_OF_INPUT_SEGMENT` values 0, 1, and 3 into 1, 2, and 4 segments, treating value 2 as invalid. Disable clears ODM source/memory, disables OTG/VTG, and waits longer than DCN31 for `OTG_BUSY`. DRR sets min/max and optional midpoint, then either sends a DMUB manual-trigger command when `mclk_sw` is supported and FAMS is enabled, or programs TRIGA mask bits locally.

## Dependencies and Integration Points
Depends on `dc_dmub_srv.h` for DMUB commands and on DCN31 readback helpers. The vtable wires shared DCN3 helpers for locks, DSC, GSL, pending status, and timing readback. Resource code selects this init for DCN32-family OPTCs.

## Risks and Test Signals
Risks include disagreement between software ODM segment count and register encoding, DMUB capability gating for DRR, and timeouts on ODM double-buffer pending. Tests should include FAMS enabled/disabled VRR transitions, ODM combine and bypass, phantom pipe teardown, and update-pending polling under rapid mode updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.h

## Purpose
Defines DCN 3.2 OPTC field metadata and declares DCN32-specific helper functions. It is intentionally mask/shift focused because DCN32 reuses the DCN31 register list shape while adding fields needed for current master state, OPTC double-buffer pending, manual timing division, and pipe update status.

## Important APIs, Types, and Macros
`OPTC_COMMON_MASK_SH_LIST_DCN3_2(mask_sh)` expands field mappings for timing, update lock, CRC, GSL, ODM data source, memory, DSC, DRR, pipe update, and interrupt-destination fields. Notable DCN32 fields include `OTG_CURRENT_MASTER_EN_STATE`, `OPTC_DOUBLE_BUFFER_PENDING`, `OTG_H_TIMING_DIV_MODE_MANUAL`, and the pipe pending bits. Prototypes expose `dcn32_timing_generator_init()`, ODM bypass/segment helpers, horizontal timing manual mode, and ODM double-buffer wait.

## Control Flow and State
The header has no executable flow. It controls which hardware fields are available to the DCN32 vtable and inherited helper paths. The pending and manual-mode fields support synchronization decisions during ODM and timing changes.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h`; later DCN35, DCN401, and DCN42 files include this header to reuse exported helpers and the field-list baseline. Register tables generated from this macro are consumed by `struct optc` initialization.

## Risks and Test Signals
Bad field mapping can break lock status, double-buffer polling, ODM setup, or CRC reads. Compile tests check symbol availability; functional tests should exercise update locks, ODM reconfiguration, DRR, and pipe update pending telemetry on DCN32 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.c

## Purpose
Implements DCN 3.5 OPTC operations. It builds on DCN32 with enhanced CRC support, long-vtotal handling, fine-grain clock-gating control, stronger disable wait semantics, and defensive null/function checks around DRR paths.

## Important APIs, Types, and Functions
Public APIs are `dcn35_timing_generator_init()`, `dcn35_timing_generator_set_fgcg()`, `optc35_set_drr()`, `optc35_set_long_vtotal()`, `optc35_configure_crc()`, and `optc35_wait_otg_disable()`. Static functions include `optc35_set_odm_combine()`, enable/disable, phantom post-enable, `optc35_get_crc()`, and manual-trigger setup.

## Control Flow and State
The ODM path follows DCN32 memory allocation and records `opp_count`. Disable clears ODM mappings and memory, disables OTG/VTG, waits for both `OTG_BUSY` and `OTG_CURRENT_MASTER_EN_STATE`, then clears underflow. CRC configuration rejects disabled CRTCs, clears/reset controls when requested, programs per-engine window A/B boundaries, enables optional CRC window double buffering, and writes polynomial mode when available. CRC readback selects CRC32 registers when all CRC32 masks exist, otherwise uses legacy 16-bit result registers. DRR programs min/max/mid and uses DMUB manual-trigger commands when memory-clock switching is active; long-vtotal splits very large vertical totals across `OTG_V_COUNT_STOP_CONTROL` and `OTG_V_COUNT_STOP_CONTROL2`.

## Dependencies and Integration Points
Includes DCN31/DCN32 headers and `dc_dmub_srv.h`. The vtable reuses DCN32 ODM bypass/manual-mode helpers, DCN31 readback, and DCN3 base helpers. Initialization sets timing limits, `max_frame_count`, and OPTC fine-grain clock gating based on `dc->debug.enable_fine_grain_clock_gating.bits.optc`.

## Risks and Test Signals
Risks include CRC32/CRC16 capability detection via nonzero masks, long-vtotal edge cases where min exceeds max hardware count, FAMS/DMUB trigger behavior, and clock-gating side effects. Test signals include CRC engine 0/1 captures, CRC polynomial selection on DCN3.6-style masks, VRR and long-vblank modes, ODM 2:1/4:1, and disable underflow cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.h

## Purpose
Defines DCN3.5 and DCN3.6 OPTC field extensions over the DCN3.2 baseline and declares DCN35 public timing-generator helpers.

## Important APIs, Types, and Macros
`OPTC_COMMON_MASK_SH_LIST_DCN3_5(mask_sh)` composes `OPTC_COMMON_MASK_SH_LIST_DCN3_2()` and adds CRC window double-buffering, CRC engine 1-3 legacy result fields, CRC window readback fields, `OPTC_FGCG_REP_DIS`, long-vtotal stop-control fields, and additional pipe update status fields. `OPTC_COMMON_MASK_SH_LIST_DCN3_6(mask_sh)` further adds CRC polynomial selection and 32-bit CRC result fields. Prototypes expose init, fine-grain clock gating, DRR, long-vtotal, CRC configuration, and OTG-disable wait helpers.

## Control Flow and State
The header has no runtime flow. It defines the hardware state surface that DCN35 code can access: CRC windows/results, clock gating, and long vertical-total counters. These fields directly affect display validation and debug behavior because the implementation checks mask presence before enabling newer CRC paths.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h` and `dcn32/dcn32_optc.h`. DCN42 reuses `optc35_configure_crc()`, `optc35_set_long_vtotal()`, and `dcn35_timing_generator_set_fgcg()` while supplying a different field list.

## Risks and Test Signals
Risk is mainly feature-flag drift: fields added to the macro imply hardware support that implementation paths may use. Tests should compile DCN35/DCN36 style tables and run CRC window, CRC32, long-vtotal, and FGC clock-gating scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn401/dcn401_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn401/dcn401_optc.c

## Purpose
Implements DCN 4.01 OPTC behavior. Compared with DCN3.x, it adds a more general ODM memory allocator, 3:1 ODM combine support with last-segment width, FAMS2-aware DRR programming through DMUB, P-state keepout programming, vupdate keepout helpers, and update-lock status waiting.

## Important APIs, Types, and Functions
Public functions include `dcn401_timing_generator_init()`, `optc401_set_drr()`, `optc401_set_vtotal_min_max()`, `optc401_setup_manual_trigger()`, `optc401_program_global_sync()`, enable/disable/phantom helpers, ODM bypass/combine, horizontal timing manual mode, out-mux selection, vupdate keepout, and update-lock wait. `decide_odm_mem_bit_map()` is a static allocator for shared ODM memory bits.

## Control Flow and State
`decide_odm_mem_bit_map()` computes required memory in even pairs from active width, allocates first preferred memory per OPP, then second preferred memory for active OPPs, then second preferred memory from inactive OPPs, and asserts allocation completeness. ODM combine supports 2, 3, and 4 input segments; 3:1 programs `OPTC_WIDTH_CONTROL2.OPTC_SEGMENT_WIDTH_LAST` and uses horizontal timing divide by 4 because the hardware packs four pixels per transfer. Disable clears ODM selection/memory, disables OTG/VTG, waits for `OTG_CURRENT_MASTER_EN_STATE == 0`, then waits for `OTG_BUSY == 0`. DRR either calls `dc_dmub_srv_fams2_drr_update()` when FAMS2 is enabled, uses FAMS1 DMUB commands for vtotal updates, or writes registers locally. Global sync stores offsets in `optc1` and programs startup/update/ready and P-state keepout registers.

## Dependencies and Integration Points
Depends on DCN31/DCN32 helpers, `dc_dmub_srv.h`, and shared `reg_helper` MMIO macros. DCN42 reuses many DCN401 functions directly. The vtable supplies Display Core with timing, ODM, DRR, sync, pending, and update-lock behavior for DCN401 resources.

## Risks and Test Signals
Risks include ODM memory double allocation across OPTCs, incorrect 3:1 active width or last-segment handling, FAMS/FAMS2 gating mismatches, and P-state keepout off-by-one values. Tests should cover 2:1/3:1/4:1 ODM, wide modes such as 11520x2160, FAMS1/FAMS2/disabled VRR paths, global sync with nonzero `vstartup_start`, HPO/DIO output mux, and update-lock wait timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn401/dcn401_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn401/dcn401_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn401/dcn401_optc.h

## Purpose
Defines the DCN401 OPTC field list and declares the generation-specific functions implemented in `dcn401_optc.c`. It captures the expanded DCN4 register surface used for ODM 3:1, FAMS/FAMS2 DRR, P-state keepout, and update-lock handling.

## Important APIs, Types, and Macros
`OPTC_COMMON_MASK_SH_LIST_DCN401(mask_sh)` maps standard OTG timing/update-lock/status fields plus `OPTC_DOUBLE_BUFFER_PENDING`, ODM segment 0-3 selection, `OPTC_WIDTH_CONTROL2.OPTC_SEGMENT_WIDTH_LAST`, `OTG_H_TIMING_DIV_MODE_MANUAL`, `OTG_PSTATE_REGISTER` fields, pipe-update status, and interrupt destination. Prototypes cover init, DRR/min-max/manual-trigger, global sync, CRTC/phantom enable/disable, ODM bypass/combine, out mux, update-lock wait, and vupdate keepout.

## Control Flow and State
No runtime flow is present. The macro controls register-table state for DCN401 and determines which fields shared helpers can access. The function prototypes allow DCN42 and resource modules to reuse DCN401 logic without duplicating declarations.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h`. DCN401 resources instantiate these tables; DCN42 includes and calls this API for most base behavior. The fields must match the generated ASIC headers consumed by `reg_helper`.

## Risks and Test Signals
Risks are missing or incorrect masks for new DCN4 functionality, especially `OPTC_SEGMENT_WIDTH_LAST`, P-state fields, and update-lock status. Build coverage and DCN401/DCN42 hardware mode-set tests are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn401/dcn401_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn42/dcn42_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn42/dcn42_optc.c

## Purpose
Implements DCN 4.2 OPTC behavior by composing DCN401/DCN35 logic with DCN42-specific CRC register layout, PWA frame-sync controls, RSMU underflow handling, double-buffer initialization, and custom lock double-buffer programming.

## Important APIs, Types, and Functions
Public functions are `dcn42_timing_generator_init()`, `optc42_enable_pwa()`, `optc42_disable_pwa()`, `optc42_tg_init()`, `optc42_clear_optc_underflow()`, `optc42_is_optc_underflow_occurred()`, `optc42_disable_crtc()`, and `optc42_lock_doublebuffer_enable()`. The static `optc42_get_crc()` reads DCN42's split red/green/blue CRC registers. The vtable delegates most base operations to DCN401 and DCN35 helpers.

## Control Flow and State
CRC readback first checks `OTG_CRC_EN`, then reads engine 0 or 1 results from separate R/G/B registers. PWA enable checks the debug option `enable_otg_frame_sync_pwa`, then programs enable, vcount mode, and line offset; disable clears the enable bit. Underflow clear writes both `OPTC_INPUT_GLOBAL_CONTROL.OPTC_UNDERFLOW_CLEAR` and `OPTC_RSMU_UNDERFLOW.OPTC_RSMU_UNDERFLOW_CLEAR`; status reports either normal or RSMU underflow. Disable delegates to `optc401_disable_crtc()` then clears DCN42 underflow. TG init enables DRR timing double-buffer mode 2 and clears underflow. The custom lock-doublebuffer routine computes blanking positions, programs lock window/update position/vupdate keepout, enables global update lock, and emits a trace event.

## Dependencies and Integration Points
Includes DCN35 and DCN401 headers for reused functions plus `dc_trace.h` for lock/unlock tracing. The vtable uses DCN401 for enable, ODM, DRR, global sync, output mux, vupdate keepout, and update-lock wait; DCN35 for long-vtotal, CRC configuration, wait OTG disable, and FGC clock gating.

## Risks and Test Signals
Risks include CRC field-name mismatches for engine 1, PWA debug gating, RSMU underflow not being cleared on all disable paths, and lock-window arithmetic when `h_blank_start` is small. Tests should cover CRC engine 0/1, PWA enable/disable with debug flag, underflow injection/clear, global update lock tracing, ODM/DCN401 inherited paths, and FGC clock-gating toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn42/dcn42_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn42/dcn42_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn42/dcn42_optc.h

## Purpose
Defines the DCN42 OPTC field list and public function declarations for DCN42 timing-generator behavior. It combines DCN4 timing/ODM/P-state concepts with DCN42-only RSMU underflow, split CRC result registers, PWA frame-sync fields, and FGC clock-gating control.

## Important APIs, Types, and Macros
`OPTC_COMMON_MASK_SH_LIST_DCN42(mask_sh)` enumerates standard OTG timing, update lock, VTG, GSL, ODM, DSC, DRR, P-state, pipe update, and interrupt fields. DCN42 additions include `OPTC_RSMU_UNDERFLOW_*`, split CRC0/CRC1 R/G/B registers, `OTG_DRR_TIMING_DBUF_UPDATE_PENDING`, PWA frame-sync fields, and `OPTC_FGCG_REP_DIS`. Prototypes expose init, PWA, TG init, underflow, disable, and lock-doublebuffer helpers.

## Control Flow and State
The header is declarative. It defines the field state that DCN42 implementation can read/write and that reused DCN35/DCN401 helpers expect to find in the `struct optc` masks.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h`. Resource construction uses this macro to build the generation-specific register table, while the implementation includes DCN35/DCN401 headers for behavior reuse.

## Risks and Test Signals
Risk areas are incorrect RSMU or PWA field mappings and CRC engine field mismatches. Build tests catch missing symbols; hardware tests should verify PWA frame sync, underflow reporting, CRC readback, double-buffer pending, and inherited ODM/DRR behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn42/dcn42_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/os_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/os_types.h

## Purpose
Provides Linux kernel OS abstraction glue for AMD Display Core. It pulls in kernel allocation, delay, byte-order, DRM logging, and optional DC FPU headers, then defines debug/assertion/logging macros used throughout DC code.

## Important APIs, Types, and Macros
Includes Linux headers for `slab`, `kgdb`, `delay`, `mm`, `vmalloc`, endian helpers, DRM DP helpers, DRM device, and DRM print. Defines `BIGENDIAN_CPU` or `LITTLEENDIAN_CPU` from architecture macros, undefines `FRAME_SIZE`, maps `dm_output_to_console()` to `DRM_DEBUG_KMS`, maps `dm_error()` to `DRM_ERROR`, and conditionally includes `amdgpu_dm/dc_fpu.h` under `CONFIG_DRM_AMD_DC_FP`. Debug macros are `dc_breakpoint()`, `ASSERT_CRITICAL()`, `ASSERT()`, `BREAK_TO_DEBUGGER()`, and `DC_ERR()`.

## Control Flow and State
The file has no persistent state. Runtime behavior comes from macros: assertions warn and optionally break into kgdb when `CONFIG_DEBUG_KERNEL_DC` is enabled; otherwise breakpoints are no-ops after logging. `ASSERT()` uses `WARN_ON_ONCE`, while `ASSERT_CRITICAL()` uses `WARN_ON`, changing repeat behavior.

## Dependencies and Integration Points
This header is widely included by Display Core modules and underlies many failure paths seen in OPTC, PG, and resource code. It binds DC's platform-neutral style to Linux DRM and kernel diagnostics.

## Risks and Test Signals
Risks include assertion side effects in production kernels, excessive logging, and build breaks when optional FPU configuration changes. Test signals are kernel builds across endian/config variants, DC debug assertions behaving as expected, and DRM logs containing actionable function/line information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/os_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/Makefile

## Purpose
Adds AMD Display Core power-gating controller objects to the kernel build. It currently includes DCN35 and DCN42 power-gating controllers when floating-point Display Core support is enabled.

## Important APIs, Types, and Variables
The Makefile is guarded by `ifdef CONFIG_DRM_AMD_DC_FP`. It defines `PG_DCN35 = dcn35_pg_cntl.o`, expands it through `AMD_DAL_PG_DCN35 = $(addprefix $(AMDDALPATH)/dc/pg/dcn35/,$(PG_DCN35))`, and appends to `AMD_DISPLAY_FILES`. The same pattern is used for `PG_DCN42 = dcn42_pg_cntl.o`.

## Control Flow and State
Build inclusion is conditional and declarative. When the config symbol is absent, no PG controller objects from this directory are appended. When present, both generation-specific object files are compiled into the AMD display file list.

## Dependencies and Integration Points
Depends on outer AMDGPU/DC Makefiles defining `AMDDALPATH`, `AMD_DISPLAY_FILES`, and the kernel config symbol. It integrates the PG controller implementations used by DCN35/DCN42 resource paths and power-management sequences.

## Risks and Test Signals
Risks are missing object inclusion for a new generation, stale config guards, or wrong path prefixes. Test signals include kernel build coverage with `CONFIG_DRM_AMD_DC_FP=y`, link presence of `pg_cntl35_create()` and `pg_cntl42_create()`, and resource code resolving PG controller symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn35/dcn35_pg_cntl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn35/dcn35_pg_cntl.c

## Purpose
Implements the DCN35 power-gating controller. It controls PG domains for DSC, HUBP/DPP, HPO, IO clocks, plane/OTG aggregate resources, and DWB bookkeeping, while maintaining software-visible power state arrays in `struct pg_cntl`.

## Important APIs, Types, and Functions
Public functions include per-domain controls (`pg_cntl35_dsc_pg_control()`, `pg_cntl35_hubp_dpp_pg_control()`, `pg_cntl35_hpo_pg_control()`, `pg_cntl35_io_clk_pg_control()`, `pg_cntl35_plane_otg_pg_control()`, `pg_cntl35_mpcc_pg_control()`, `pg_cntl35_opp_pg_control()`, `pg_cntl35_optc_pg_control()`, `pg_cntl35_dwb_pg_control()`), `pg_cntl35_init_pg_status()`, `pg_cntl35_create()`, and `dcn_pg_cntl_destroy()`. Static helpers read domain status and print debug summaries.

## Control Flow and State
Each hardware PG control computes `DOMAIN_POWER_GATE` from `power_on`, checks debug flags and `idle_optimizations_allowed`, reads current `DOMAIN_PGFSM_PWR_STATUS`, avoids redundant transitions, enables `DC_IP_REQUEST_CNTL.IP_REQUEST_EN` if needed, writes the domain config, and polls for target status. DSC uses domains 16-19; HUBP/DPP use domains 0-3; IO clock uses domain 22; memory status uses domain 23; plane/OTG aggregate uses domain 24; HPO uses domain 25. Plane/OTG power-down only proceeds when MPCC, OPP, OPTC, stream, and DWB state indicate all related resources are disabled. Software state is cached in `pg_pipe_res_enable` and `pg_res_enable`.

## Dependencies and Integration Points
Includes `reg_helper.h`, `core_types.h`, `dcn35_pg_cntl.h`, and `dccg.h`. The `pg_cntl35_funcs` vtable is consumed by higher-level DC power management. It relies on `dc->debug` flags, `dc->res_pool->pipe_count`, and `dc->current_state` stream mappings.

## Risks and Test Signals
Risks include stale cached state blocking power-down, domain-number mismatches, skipped power-on when debug flags are intended only for power-down, and polling timeouts. Tests should exercise each domain, debug disable flags, idle optimization gating, all-pipe-off aggregate PG, and status initialization after boot/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn35/dcn35_pg_cntl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn35/dcn35_pg_cntl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn35/dcn35_pg_cntl.h

## Purpose
Defines DCN35 power-gating register tables, field masks, controller storage, and public PG control prototypes.

## Important APIs, Types, and Macros
`PG_CNTL_REG_LIST_DCN35()` lists domains 0-3, 16-19, 22-25 config/status registers and `DC_IP_REQUEST_CNTL`. `PG_CNTL_MASK_SH_LIST_DCN35(mask_sh)` maps `DOMAIN_POWER_FORCEON`, `DOMAIN_POWER_GATE`, `DOMAIN_DESIRED_PWR_STATE`, `DOMAIN_PGFSM_PWR_STATUS`, and `IP_REQUEST_EN` fields for each domain. `struct pg_cntl_shift`, `struct pg_cntl_mask`, `struct pg_cntl_registers`, and `struct dcn_pg_cntl` hold generated table data and the embedded base controller. Prototypes expose all DCN35 PG operations, create, init-status, and destroy.

## Control Flow and State
The header has no runtime flow but defines the state layout used by `dcn35_pg_cntl.c`. The base `struct pg_cntl` stores software resource state; this header adds immutable register/field table pointers.

## Dependencies and Integration Points
Includes `pg_cntl.h` for the base API and resource enum definitions. DCN35 resource code passes generated register/shift/mask instances into `pg_cntl35_create()`.

## Risks and Test Signals
Risks are incorrect domain coverage or shift/mask mapping, especially because many domains share the same field names. Build tests catch missing symbols; hardware tests should confirm every listed PG domain can report status and transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn35/dcn35_pg_cntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn42/dcn42_pg_cntl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn42/dcn42_pg_cntl.c

## Purpose
Implements the DCN42 power-gating controller. It extends the DCN35 model with explicit memory and DIO domains, DCCG clock interactions, global FGC gating suppression around some power-on transitions, and DCN42-specific resource state bookkeeping.

## Important APIs, Types, and Functions
Public controls include `pg_cntl42_dsc_pg_control()`, `pg_cntl42_hubp_dpp_pg_control()`, `pg_cntl42_hpo_pg_control()`, `pg_cntl42_io_clk_pg_control()`, `pg_cntl42_plane_otg_pg_control()`, `pg_cntl42_mpcc_pg_control()`, `pg_cntl42_opp_pg_control()`, `pg_cntl42_optc_pg_control()`, `pg_cntl42_mem_pg_control()`, `pg_cntl42_dio_pg_control()`, `pg_cntl42_init_pg_status()`, `pg_cntl42_create()`, and `dcn42_pg_cntl_destroy()`.

## Control Flow and State
Control functions follow the same status-check, skip-flag, IP-request-enable, config-write, and status-poll pattern as DCN35. DSC power-on enables DSC clocks through DCCG before PG changes and disables them after power-down. DSC, HUBP/DPP, HPO, and DIO power-on temporarily disable global FGC gating when supported, then restore it. IO clock domain 22 tracks DCCG, DCOH, and DCIO; memory domain 23 tracks DCHUBBUB and DCHVM; plane/OTG domain 24 waits for all stream/MPCC/OPP/OPTC state to be off before gating; DIO domain 26 is separate from IO clock control. `pg_res_enable` and `pg_pipe_res_enable` are initialized from hardware status in `pg_cntl42_init_pg_status()`.

## Dependencies and Integration Points
Includes `reg_helper.h`, `core_types.h`, `dcn42_pg_cntl.h`, and `dccg.h`. The vtable omits a debug print hook and adds `mem_pg_control` and `dio_pg_control`. Higher-level DC power management calls these through `struct pg_cntl_funcs`.

## Risks and Test Signals
Risks include DCCG callback NULL handling, global FGC gating not being restored, mismatched software cached state, domain 26 DIO sequencing, and power-down dependency checks that are too strict or too weak. Tests should cover each domain, DSC clock enable/disable, DIO and IO clock separation, memory power gating, aggregate plane/OTG gating, debug flag bypass, and resume status reconstruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn42/dcn42_pg_cntl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn42/dcn42_pg_cntl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn42/dcn42_pg_cntl.h

## Purpose
Defines DCN42 power-gating register/field tables, controller storage, and public prototypes. It is the register contract for `dcn42_pg_cntl.c`.

## Important APIs, Types, and Macros
`PG_CNTL_REG_LIST_DCN42()` lists config/status registers for domains 0-3, 16-19, 22-26 plus `DC_IP_REQUEST_CNTL`. `PG_CNTL_MASK_SH_LIST_DCN42(mask_sh)` maps force-on, power-gate, desired state, FSM status, and IP request fields for all domains. `struct pg_cntl_shift`, `struct pg_cntl_mask`, `struct pg_cntl_registers`, and `struct dcn_pg_cntl` carry table data and the base controller. Prototypes expose all DCN42 PG control functions, create, init-status, and both `dcn42_pg_cntl_destroy()` and generic `dcn_pg_cntl_destroy()`.

## Control Flow and State
The header is declarative. Runtime state is the embedded `struct pg_cntl` plus immutable pointers to generated register/field tables. Domain 26 coverage is the notable expansion over DCN35.

## Dependencies and Integration Points
Includes `pg_cntl.h`. DCN42 resource initialization supplies generated tables and receives a `struct pg_cntl *` with the DCN42 function table attached.

## Risks and Test Signals
Risks include domain list mismatch with implementation switch statements and wrong field mapping for new DIO controls. Build tests and hardware PG transition tests for domains 22, 23, 24, 25, and 26 are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn42/dcn42_pg_cntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/Makefile

## Purpose
Builds AMD Display Core resource-pool implementations for DCE and DCN ASIC generations. Resource files describe hardware capabilities and factories for clocks, pipes, links, encoders, and validation functions.

## Important APIs, Types, and Variables
The Makefile appends generation-specific object paths to `AMD_DISPLAY_FILES` through variables such as `RESOURCE_DCE100`, `AMD_DAL_RESOURCE_DCE100`, `RESOURCE_DCN32`, `RESOURCE_DCN401`, and `RESOURCE_DCN42`. DCE60 is gated by `CONFIG_DRM_AMD_DC_SI`. DCN resources are gated by `CONFIG_DRM_AMD_DC_FP`. DCN42 includes both `dcn42_resource.o` and `dcn42_resource_fpu.o` with per-file FPU compile flags using `CFLAGS_...` and `CFLAGS_REMOVE_...`.

## Control Flow and State
Build flow is declarative. DCE80 through DCE120 and DCE100 are always added outside the DCN FP guard, while newer DCN generations are included only under FP-enabled Display Core builds. The FPU flag override isolates DCN42 floating-point code from non-FPU build flags.

## Dependencies and Integration Points
Depends on the outer AMDGPU build system for `AMDDALPATH`, `AMD_DISPLAY_FILES`, `CC_FLAGS_FPU`, and `CC_FLAGS_NO_FPU`. Resource objects created here bind ASIC discovery to the rest of Display Core.

## Risks and Test Signals
Risks include missing a generation object, stale config gating, incorrect FPU flag application, or object order assumptions. Test signals are full kernel builds for SI, non-FP, FP, and DCN42 configurations and link-time resolution of each generation's create-resource-pool symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.c

## Purpose
Constructs and validates the DCE 10.0 Display Core resource pool. It defines register tables, hardware caps, object factories, resource validation callbacks, link/stream encoder selection, and teardown for the DCE100 generation.

## Important APIs, Types, and Functions
The public entry point is `dce100_create_resource_pool()`. Other exported functions are `dce100_validate_bandwidth()`, `dce100_validate_global()`, `dce100_add_stream_to_ctx()`, `dce100_validate_plane()`, and `dce100_find_first_free_match_stream_enc_for_link()`. Static factories create timing generators, stream encoders, audio, memory inputs, transforms, IPPs, link encoders, panel controls, OPPs, AUX engines, I2C engines, clock sources, and HW sequencer storage. `dce100_res_pool_funcs` binds the public resource callbacks.

## Control Flow and State
Construction allocates `struct dce110_resource_pool`, sets BIOS scratch registers, resource caps, function table, and underlay state, then creates DP and pixel clock sources based on BIOS external DP clock availability. It allocates DMCU, ABM, IRQ service, six pipe resources (TG, MI, IPP, transform, OPP), six AUX/I2C engines, plane caps, and common virtual/resource constructs, then constructs the hardware sequencer. On any failure it jumps to `res_create_fail`, destructs partially allocated objects, and returns NULL. Destruction walks all arrays and frees each resource, including clocks, audios, ABM, DMCU, and IRQ service. Bandwidth validation rejects streams whose pixel clock exceeds max supported display clock and fills legacy bandwidth context clocks. Global validation rejects more than one plane per stream and video formats. Stream add maps pool resources, maps clocks, and builds pipe HW params and info frames. Stream encoder selection prefers matching engine, falls back to the first free encoder for DisplayPort MST cases.

## Dependencies and Integration Points
Includes broad DCE components: link/stream encoders, DCE110 resources/timing/IRQ, DCE IP blocks, panel, DMCU, AUX, ABM, I2C, DCE100 HW sequence, and generated register headers. This file is compiled through `dc/resource/Makefile` and selected by ASIC resource creation code for DCE100 devices.

## Risks and Test Signals
Risks include partial-construction cleanup leaks, register-table index mismatches, wrong clock-source selection when BIOS external clock data changes, validation limits rejecting valid formats or accepting unsupported ones, and MST encoder fallback behavior. Tests should cover allocation-failure paths, mode-set on all six pipes, DP/HDMI/VGA link creation, MST stream encoder allocation, plane format validation, bandwidth pixel-clock boundaries, suspend/resume teardown/recreate, and hotplug AUX/I2C behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.h

## Purpose
Declares the DCE100 resource-pool factory and validation/resource helper APIs. It is the external contract for `dce100_resource.c`.

## Important APIs and Types
Forward declarations cover `struct dc`, `struct resource_pool`, and `struct dc_validation_set`. Prototypes expose `dce100_create_resource_pool()`, `dce100_validate_plane()`, `dce100_validate_global()`, `dce100_validate_bandwidth()`, `dce100_add_stream_to_ctx()`, and `dce100_find_first_free_match_stream_enc_for_link()`.

## Control Flow and State
The header has no executable flow. It allows the ASIC selection layer and shared resource code to create a DCE100 pool and call generation-specific validation and mapping helpers. Persistent state is owned by the returned `struct resource_pool`.

## Dependencies and Integration Points
Relies on common Display Core type definitions being visible to includers. The implementation uses these declarations in the resource function table and external ASIC initialization paths.

## Risks and Test Signals
Risks are signature drift from common resource interfaces or missing declarations when helper functions are referenced by other DCE generations. Build coverage is the primary signal; runtime signals come from successful DCE100 resource creation and validation callback use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.h -->
