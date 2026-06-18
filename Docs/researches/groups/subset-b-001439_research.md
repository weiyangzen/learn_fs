# subset-b-001439 Research

Grouped research report for AMD display HUBP and HWSS files. Each file section preserves the original source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30/dcn30_hubp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30/dcn30_hubp.h

Purpose: declares the DCN 3.0 HUBP interface and register field inventory used by AMDGPU Display Core to program plane fetch, tiling, DCC, VM, cursor, flip, DLG, TTU, and dmdata behavior. It extends DCN 2.0/2.1 HUBP definitions and is the base contract reused by later DCN 3.x HUBP implementations.

Important APIs and types: `HUBP_REG_LIST_DCN30()` appends `DCN_DMDATA_VM_CNTL` to the DCN 2.1 register list. `HUBP_MASK_SH_LIST_DCN30_BASE()` and `HUBP_MASK_SH_LIST_DCN30()` enumerate the register fields expected in generated shift/mask tables, including surface address, meta address, DCC, cursor, VMID, flip, vblank, and TTU fields. Exported function declarations include `hubp3_construct()`, VM aperture programming, surface flip/address programming, surface config, DLG/TTU/RQ setup, tiling, DCC, dmdata, state reads, init, tiling clear, read-line, and underflow status helpers.

Control flow: this header has no runtime flow, but it controls compile-time expansion of register tables and function pointer wiring in ASIC-specific resource code. Implementations in DCN 3.x source files call the declared helpers to update hardware through `reg_helper` macros, usually after resource construction installs a `hubp_funcs` table.

State and persistence: persistent state is hardware register state and cached `struct hubp`/`struct dcn20_hubp` fields updated by the implementations. The header exposes fields for address latching, underflow, outstanding request status, cursor state, VM fault status, and flip pending status, so omissions in the mask list can make apparently valid code write the wrong bits or skip diagnostics.

Dependencies and integration points: depends on `dcn20_hubp.h` and `dcn21_hubp.h`, plus shared DC plane, tiling, DCC, vm aperture, and DML register structs referenced by prototypes. It is consumed by DCN generation resource constructors and later HUBP variants (`dcn31`, `dcn32`, `dcn35`, `dcn42`) that compose its masks or reuse `hubp3_*` helpers.

Risks and test signals: register list drift is the main risk; generated ASIC tables must match the silicon register spec exactly. Fields such as address high/low ordering, TMZ, DCC enable, VMID, and flip/update locks have direct display correctness and hang risk. There are no local unit tests; build coverage, ASIC bring-up, Display Core register readback, underflow counters, flip tests, cursor tests, and DCC/tiling display validation are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30/dcn30_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.c

Purpose: implements the DCN 3.1 HUBP specialization. It mostly reuses DCN 3.0 helpers while adding unbounded request mode, HUBP soft reset, optimized blank programming, DET segment allocation error readback, and DCN 3.1 function table construction.

Important APIs and functions: `hubp31_set_unbounded_requesting()` updates `HUBP_UNBOUNDED_REQ_MODE` and forces `CURSOR_REQ_MODE` to 1. `hubp31_soft_reset()` writes `HUBP_SOFT_RESET`. `hubp31_program_extended_blank_value()` exposes the static `hubp31_program_extended_blank()` wrapper for `MIN_DST_Y_NEXT_START`. `hubp31_get_det_config_error()` reads `HUBP_SEG_ALLOC_ERR_STATUS`. `hubp31_construct()` initializes the base object, register/shift/mask pointers, instance id, and function table.

Control flow: construction installs `dcn31_hubp_funcs`. Runtime calls arrive through `struct hubp_funcs`: surface flips and configs route to `hubp3_*`, cursor and dmdata logic largely route to DCN 2.x/3.0 helpers, while DCN 3.1 specific entries handle unbounded requesting, soft reset, extended blank, and DET error readback. The functions are thin hardware register transactions with no allocation or retry logic.

State and persistence: writes persist in HUBP registers until reprogrammed or reset. `hubp31_construct()` stores immutable register table pointers in `struct dcn20_hubp` and sets `opp_id` invalid plus `mpcc_id` to `0xf`. `hubp31_get_det_config_error()` is read-only diagnostic state. Cursor request mode is forced whenever unbounded requesting is toggled, which is an intentional side effect.

Dependencies and integration points: includes `dm_services.h`, `dce_calcs.h`, `reg_helper.h`, conversion helpers, and `dcn31_hubp.h`. It depends heavily on DCN 2.x and DCN 3.0 helper functions. Display resource code for DCN 3.1 constructs these objects and higher-level HWSS/plane programming accesses them through the function table.

Risks and test signals: incorrect function table wiring can silently regress inherited behavior. Soft reset and unbounded request mode affect live request scheduling, so misuse can cause blanking, fetch stalls, or cursor timing problems. DET error status only works if the header mask list matches the register spec. Signals include DCN 3.1 build coverage, modeset/flip tests, cursor tests, SubVP or unbounded-request paths, register readback for `HUBP_SEG_ALLOC_ERR_STATUS`, and underflow monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.h

Purpose: declares the DCN 3.1 HUBP register field set and public entry points. It extends the DCN 3.0 mask list with DCN 3.1 fields for unbounded requesting, soft reset, cursor request mode, and segment allocation error status.

Important APIs and definitions: `HUBP_MASK_SH_LIST_DCN31()` expands a full HUBP field list for generated register shift/mask tables. New or notable fields versus DCN 3.0 include `HUBP_UNBOUNDED_REQ_MODE`, `HUBP_SOFT_RESET`, `CURSOR_REQ_MODE`, and `HUBP_SEG_ALLOC_ERR_STATUS`. The header declares `hubp31_construct()`, `hubp31_soft_reset()`, `hubp31_set_unbounded_requesting()`, `hubp31_program_extended_blank_value()`, and `hubp31_get_det_config_error()`.

Control flow: no executable code is present, but the macro establishes the compile-time register contract consumed by DCN 3.1 resource files and by the implementation in `dcn31_hubp.c`. Later variants include this header to reuse DCN 3.1 function declarations and field coverage.

State and persistence: the exposed fields control persistent hardware state for request scheduling, reset, blank timing, cursor fetching, and DET allocation diagnostics. The public functions write or read those fields through `reg_helper` macros in the `.c` implementation.

Dependencies and integration points: includes DCN 2.0, DCN 2.1, and DCN 3.0 HUBP headers. It is used by `dcn32_hubp.h`, `dcn35_hubp.h`, `dcn401_hubp.h`, and `dcn42_hubp.h` either directly or indirectly, making it part of the shared DCN 3.x/4.x compatibility layer.

Risks and test signals: because this header duplicates a large field inventory, merge conflicts or register-spec changes can drop a needed field. Missing cursor or reset masks produce runtime register corruption rather than compile errors if table layouts still compile. Test signals are build warnings, generated register table validation, modeset with soft reset, cursor timing validation, DET allocation error injection/readback, and unbounded-request display scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.c

Purpose: implements DCN 3.2 HUBP behavior for pstate forcing, MALL selection, SubVP buffering, phantom pipe post-enable, cursor attribute programming with MALL cursor caching, initialization, and function table construction.

Important APIs and functions: `hubp32_update_force_pstate_disallow()` and `hubp32_update_force_cursor_pstate_disallow()` program data and cursor UCLK pstate force bits. `hubp32_update_mall_sel()` writes `USE_MALL_SEL` and cursor caching. `hubp32_prepare_subvp_buffering()` toggles `FORCE_ONE_ROW_FOR_FRAME` and `CURSOR_REQ_MODE`. `hubp32_phantom_hubp_post_enable()` disables GSL, blanks HUBP, and waits for no outstanding requests when the block is live. `hubp32_cursor_set_attributes()` computes cursor pitch, lines per chunk, rounded memory size, and whether to use MALL for cursor. `hubp32_construct()` installs `dcn32_hubp_funcs`.

Control flow: callers use function table hooks installed during construction. Pstate and MALL helpers are direct register updates. SubVP buffering also changes cursor fetch timing so cursor requests start early enough to avoid SubVP regions. Phantom post-enable reads back `DCHUBP_CNTL`; if the HUBP appears ungated, it waits for `HUBP_NO_OUTSTANDING_REQ`. Cursor attributes program address, size, control, settings, and cache mirrored software state unless cursor offload is active.

State and persistence: the file persists pstate force, MALL select, cursor request mode, blank state, and cursor registers in hardware. It also updates `hubp->curs_attr`, `hubp->att`, `hubp->cur_rect`, and `hubp->use_mall_for_cursor`. Cursor MALL use is derived from a 16 KiB threshold after width rounding and format byte-depth calculation.

Dependencies and integration points: includes `dcn32_hubp.h` and reuses DCN 3.1, DCN 3.0, and DCN 2.x helpers. It integrates with DCN 3.2 MALL/SubVP programming, clock manager pstate decisions, cursor programming, and phantom pipe enable flows used by display mode validation and commit paths.

Risks and test signals: pstate force bits and SubVP/MALL programming are latency-sensitive; wrong sequencing can cause underflow, flicker, or memory-clock transition failures. Cursor size arithmetic and the MALL threshold must match hardware cache behavior. `hubp32_init()` writes `HUBPREQ_DEBUG_DB` but the function table uses `hubp3_init`, so init behavior should be checked in call sites. Useful signals include DCN 3.2 modeset, SubVP, MALL static screen, pstate switching, large cursor, cursor offload, phantom pipe, and underflow tests with register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.h

Purpose: declares DCN 3.2 HUBP additions over DCN 3.1, focused on MALL, virtual memory page buffer configuration, SubVP buffering, and UCLK pstate forcing.

Important APIs and definitions: `HUBP_MASK_SH_LIST_DCN32()` composes `HUBP_MASK_SH_LIST_DCN31()` and adds `USE_MALL_SEL`, `USE_MALL_FOR_CURSOR`, `VMPG_SIZE`, `PTE_BUFFER_MODE`, `BIGK_FRAGMENT_SIZE`, `FORCE_ONE_ROW_FOR_FRAME`, and data/cursor `UCLK_PSTATE_FORCE` fields. Public declarations cover pstate forcing, MALL select, SubVP preparation, phantom post-enable, cursor attributes, init, and construction.

Control flow: this is a declaration-only file. The function prototypes become optional `hubp_funcs` entries in `dcn32_hubp.c` and are reused by DCN 4.0.1/4.2 where compatible.

State and persistence: the listed fields program persistent hardware controls for memory-cache residency, cursor cache use, virtual memory request buffering, and pstate transition suppression. They directly affect display fetch behavior during power and memory-clock changes.

Dependencies and integration points: includes DCN 2.0, 2.1, 3.0, and 3.1 HUBP headers. Later HUBP generations include or call these helpers for MALL and SubVP support. The declarations connect to DML and HWSS decisions about static-screen caching, SubVP, and memory-clock transitions.

Risks and test signals: mask list mistakes affect multiple generations because later code reuses these helpers. Pstate and MALL fields are power/performance critical and can create intermittent underflows. Signals include register table builds, DCN 3.2 and later boot, SubVP/MALL validation, cursor cache behavior, and memory-clock transition stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.c

Purpose: implements DCN 3.5 HUBP specialization. It adds fine-grain clock gating control and a DCN 3.5 pixel-format programming path while reusing most DCN 3.x HUBP behavior.

Important APIs and functions: `hubp35_set_fgcg()` toggles `HUBP_FGCG_REP_DIS` with inverted enable semantics. `hubp35_init()` runs `hubp3_init()` and applies the Display Core debug fine-grain clock-gating setting for DCHUB. `hubp35_program_pixel_format()` maps AMD `surface_pixel_format` values to hardware `SURFACE_PIXEL_FORMAT` encodings and programs color channel crossbar fields. `hubp35_program_surface_config()` sequences DCC, tiling, size, rotation, and pixel format. `hubp35_construct()` installs the DCN 3.5 function table and casts DCN 3.5 shift/mask structs to the base DCN 2.0 pointers.

Control flow: after construction, Display Core calls through `dcn35_hubp_funcs`. Surface configuration first controls DCC with `hubp3_dcc_control_sienna_cichlid()`, then tiling, size, rotation, and format. Format programming adjusts crossbar source selection for ABGR-like formats, handles graphics, video, RGBE, and special float/fix formats, and breaks to debugger on unsupported formats.

State and persistence: writes persist in HUBP clock and surface config registers. The function table and register pointers persist in the HUBP object. Pixel format and crossbar writes determine the interpretation of fetched memory; incorrect values persist until a later plane update.

Dependencies and integration points: depends on `dcn35_hubp.h`, `reg_helper`, and inherited DCN 2.x/3.x helpers. It integrates with display debug flags (`enable_fine_grain_clock_gating.bits.dchub`), plane programming, DCC, tiling, and cursor/dmdata inherited from older generations.

Risks and test signals: pixel format mappings are high risk because a wrong numeric encoding or crossbar selection creates color corruption for specific formats. FGC Gating can expose race conditions if clocks gate while registers are still needed. Signals include format sweep tests, RGBE/alpha plane tests, video plane validation, DCC+rotation combinations, clock-gating enabled/disabled boots, and register readback after plane programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.h

Purpose: declares DCN 3.5 HUBP extensions, mainly the additional fine-grain clock gating field and typed shift/mask wrappers that extend the DCN 3.2 register field list.

Important APIs and types: `HUBP_MASK_SH_LIST_DCN35()` composes DCN 3.2 fields and adds `HUBP_FGCG_REP_DIS`. `DCN35_HUBP_REG_FIELD_VARIABLE_LIST(type)` embeds `DCN32_HUBP_REG_FIELD_VARIABLE_LIST(type)` and appends the FGC field. `struct dcn35_hubp2_shift` and `struct dcn35_hubp2_mask` provide generation-specific shift/mask layouts. Prototypes declare construction, FGC control, pixel format programming, surface config, and init.

Control flow: no executable flow exists here. The typed mask/shift structs are used by `dcn35_hubp.c` to safely access the added field before casting to base structures for inherited helpers.

State and persistence: the additional state is the `HUBP_FGCG_REP_DIS` bit in `HUBP_CLK_CNTL`, which controls fine-grain clock-gating repeat disable behavior. Surface state is programmed by declared functions in the implementation.

Dependencies and integration points: includes DCN 3.1 and DCN 3.2 HUBP headers. It is also included by DCN 4.2, which reuses the DCN 3.5 mask base for a different later-generation path.

Risks and test signals: struct layout must remain compatible with inherited DCN 3.2 field lists. If `HUBP_FGCG_REP_DIS` is missing or shifted incorrectly, power management can malfunction without obvious compile-time errors. Signals include generation-specific register table builds, clock-gating tests, DCN 3.5 plane bring-up, and checking that inherited DCN 3.2 fields still map correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn401/dcn401_hubp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn401/dcn401_hubp.c

Purpose: implements DCN 4.0.1 HUBP behavior. It adapts the HUBP function table to DML2 register payloads, adds 3D LUT fast-load programming, MALL prefetch configuration, MCACHE ID/split-coordinate programming, DCN4 address programming, and expanded state readback.

Important APIs and functions: 3D LUT helpers program address, DLG parameter, enable, done status, crossbar, width, format, addressing mode, mode, bias, scale, and TMZ. `hubp401_update_mall_sel()` sets MALL selection and prefetch command defaults. `hubp401_vready_at_or_After_vsync()` computes whether vready lands at or after vsync from DML2 global sync and timing. `hubp401_program_requestor()` and `hubp401_program_deadline()` translate DML2 RQ/DLG/TTU structs into registers. `hubp401_setup()` and `_setup_interdependent()` split dependent/interdependent timing programming. `hubp401_program_surface_flip_and_addr()` writes graphics, video, stereo, and RGBEA addresses. Other helpers clear tiling, control DCC, program tiling/size/surface config, viewport, MCACHE IDs, flip interrupt, blank status, cursor position, state readback, unbounded request mode, and construction.

Control flow: construction installs `dcn401_hubp_funcs`, whose key difference from older generations is using `hubp_setup2` and `hubp_setup_interdependent2` for DML2 payloads. Setup computes vready/vsync state, requestor sizes, and deadline values while the OTG is assumed locked and double-buffered registers are used. Surface flip programs flip type and VMID, handles stereo mode bits, writes high address before low address so hardware latches correctly, and caches `hubp->request_address`. State readback mirrors many requestor, DLG, TTU, surface, and control registers into `dcn_hubp_state`.

State and persistence: this file directly persists HUBP timing, requestor, surface, cursor, MALL, MCACHE, 3D LUT, DCC, tiling, viewport, VMID, and underflow-related control state. It also caches cursor position rectangles and request addresses in software. Several operations rely on register double buffering and correct write ordering.

Dependencies and integration points: includes `dcn401_hubp.h`, `reg_helper`, conversion helpers, and ASIC id definitions. It depends on DML2 types from `dml_top_dchub_registers.h` and inherited helpers from DCN 2.x/3.x. It integrates with DCN4 HWSS setup, DML2 mode programming, color management 3D LUT DMA, MALL/MCACHE, cursor scaling, and plane commit/flip paths.

Risks and test signals: this file has high hardware risk. Address write ordering, zero-address guards, VMID programming, DCC/TMZ bits, and DML2 register translation can cause hangs, corruption, or underflow. The readback code appears to read `PRIMARY_SURFACE_ADDRESS` into both low and high cached fields for the high register path, which should be checked against the register helper call. Useful signals include DCN4 build coverage, DML2 modeset validation, 3D LUT DMA tests, stereo/RGBEA/video plane flips, cursor scaling/ODM, MCACHE/MALL scenarios, register readback comparison, underflow counters, and pstate transition stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn401/dcn401_hubp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn401/dcn401_hubp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn401/dcn401_hubp.h

Purpose: declares the DCN 4.0.1 HUBP register/mask inventory and public functions. It bridges legacy HUBP infrastructure to DML2 DCHUB register payloads and adds 3D LUT fast-load and MCACHE fields.

Important APIs and definitions: `HUBP_3DLUT_FL_REG_LIST_DCN401()` lists 3D LUT fast-load registers. `HUBP_MASK_SH_LIST_DCN401()` enumerates DCN4 HUBP fields, including inherited surface/cursor/DLG/TTU/VM fields, MALL prefetch fields, 3D LUT fields, viewport MCACHE split, MCACHE ID config, read-line, and DET allocation status. Prototypes cover setup, interdependent setup, flip/address programming, DCC, tiling, size, surface config, viewport, MCACHE, flip interrupt, blank, cursor position, read state, construct, init, 3D LUT helpers, clear tiling, vready/vsync, requestor, and deadline programming.

Control flow: declaration-only, but it defines which functions can be placed in DCN4 `hubp_funcs`. `hubp401_setup()` consumes `struct dml2_dchub_per_pipe_register_set`, global sync programming, and timing, making it a key interface between DML2 calculations and register programming.

State and persistence: the mask list covers all persistent hardware state written by `dcn401_hubp.c`: plane addresses, formats, DCC, tiling, pstate/MALL, DLG/TTU timing, VM settings, 3D LUT DMA, MCACHE, and diagnostics. The header also pulls in DML2 register definitions, so type compatibility is part of the ABI inside Display Core.

Dependencies and integration points: includes DCN 2.0/2.1/3.0/3.1/3.2 HUBP headers and DML2 DCHUB register definitions. It is included by `dcn42_hubp.c` for reused DCN4 helpers. Integration points include color management, DML2, HWSS, resource construction, and register table generation.

Risks and test signals: the macro is large and generation-specific, so register-spec drift is likely during bring-up. Some fields from earlier DCN3 meta programming are intentionally reduced or changed for DCN4, and consumers must not assume old DCC/meta behavior. Signals include compile coverage for generated tables, DML2 modeset tests, 3D LUT fast-load tests, MCACHE/MALL scenarios, and per-register readback validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn401/dcn401_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn42/dcn42_hubp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn42/dcn42_hubp.c

Purpose: implements DCN 4.2 HUBP specialization. It combines DCN 3.5 style surface format/FGCG behavior with DCN 4.0.1 DML2 setup and 3D LUT fast-load support, while adding DCN 4.2 requestor meta chunk programming, MPC-width handling, new 3D LUT crossbar field names, and metadata address programming during flips.

Important APIs and functions: static `hubp42_set_fgcg()`, `hubp42_init()`, and `hubp42_program_pixel_format()` mirror DCN 3.5 behavior. `hubp42_program_deadline()` is a DCN4 deadline writer with `HUBPREQ_DEBUG_DB` set to 0. `hubp42_program_requestor()` programs luma/chroma request sizes including meta chunk and minimum meta chunk fields. `hubp42_setup()` calls DCN4 vready logic, DCN4.2 requestor, and DCN4.2 deadline programming. `hubp42_program_3dlut_fl_crossbar()` uses R/G/B field names, while `hubp42_program_3dlut_fl_config()` programs `HUBP_3DLUT_MPC_WIDTH` before delegating to DCN4.0.1 config. `hubp42_program_surface_flip_and_addr()` writes primary/secondary meta addresses in addition to surface addresses. `hubp42_read_state()` extends DCN4 readback with fast-load registers.

Control flow: construction installs `dcn42_hubp_funcs`. Plane surface config uses DCN 3.x DCC/tiling/size/rotation helpers plus the DCN 4.2 pixel-format routine. Setup uses DML2 per-pipe registers. Flip/address programming follows the required high-before-low address order and writes optional meta addresses when present for graphics, video, stereo, and RGBEA planes. Readback first calls `hubp401_read_state()` and then reads DCN4.2-specific 3D LUT fields.

State and persistence: persists FGC clock gating, timing, requestor size, meta chunk, surface, meta surface, DCC/TMZ, VMID, stereo, 3D LUT, and cursor state in hardware. Caches `hubp->request_address` and relies on inherited cursor software state. The function table contains duplicate `.hubp_program_3dlut_fl_config` initializers; the later assignment to `hubp401_program_3dlut_fl_config` overrides the earlier DCN4.2 wrapper in standard C initializer semantics, which risks losing MPC-width programming.

Dependencies and integration points: includes `dcn401_hubp.h`, `dcn42_hubp.h`, and `reg_helper`. It reuses many DCN4.0.1 helpers, DCN3 helpers, and DML2 register structures. Integration points include DCN4.2 HWSS, 3D LUT DMA, plane flips with meta/DCC, DML2 requestor/deadline programming, and Display Core debug FGC flags.

Risks and test signals: the duplicate function-table initializer is a concrete risk for 3D LUT MPC width support. Metadata address handling has subtle guard conditions, including video checking `luma_meta_addr` before programming both luma and chroma meta addresses. Address ordering and TMZ/meta bits can cause corruption or hangs. Signals include compiler warnings for overridden initializers, 3D LUT size 17 and 33 tests, DCC/meta plane flips for graphics/video/stereo/RGBEA, DML2 timing validation, register readback of fast-load fields, and clock-gating enabled/disabled modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn42/dcn42_hubp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn42/dcn42_hubp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn42/dcn42_hubp.h

Purpose: declares DCN 4.2 HUBP additions over the DCN 3.5 base, focused on 3D LUT fast-load fields with DCN4.2 naming and MPC-width support.

Important APIs and definitions: `HUBP_MASK_SH_LIST_DCN42()` composes `HUBP_MASK_SH_LIST_DCN35()` and adds `_3DLUT_FL_CONFIG`, `_3DLUT_FL_BIAS_SCALE`, `HUBP_3DLUT_CONTROL`, address, and DLG fields. DCN4.2-specific fields include `HUBP_3DLUT_MPC_WIDTH` and `HUBP_3DLUT_CROSSBAR_SEL_R/G/B`. The header forward-declares `struct dml2_display_rq_regs` and declares construction, 3D LUT crossbar/config programming, state readback, requestor programming, and setup.

Control flow: no runtime control flow exists here. The definitions allow DCN4.2 resource code to build shift/mask tables and call DCN4.2 setup/requestor/readback paths while reusing DCN3.5 and DCN4.0.1 helpers.

State and persistence: the declared fields persist 3D LUT fast-load enable, done, addressing, width, MPC width, TMZ, crossbar, address, DLG cadence, bias, scale, format, and mode. Requestor and setup prototypes expose DML2-driven timing state programming.

Dependencies and integration points: includes `dcn35_hubp.h`, but the implementation also includes `dcn401_hubp.h` to reuse DCN4 helper implementations. This header is part of the DCN4.2 color management and DML2 integration surface.

Risks and test signals: relying on the DCN3.5 mask base while adding DCN4.2 fields can hide differences from DCN4.0.1. Field renames from `CROSSBAR_SELECT_*` to `CROSSBAR_SEL_*` require matching generated registers. Signals include DCN4.2 register table builds, 3D LUT fast-load readback, DML2 setup builds, and compiler diagnostics for prototype mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn42/dcn42_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/Makefile

Purpose: lists the hardware sequencer source objects included in AMD Display Core builds. It selects DCE generation files unconditionally or under SI support, and DCN generation files under floating-point Display Core support.

Important build logic: `CONFIG_DRM_AMD_DC_SI` gates `dce60_hwseq.o`. DCE80, shared DCE, DCE100, DCE110, DCE112, and DCE120 objects are added to `AMD_DISPLAY_FILES`. `CONFIG_DRM_AMD_DC_FP` gates DCN objects from DCN1.0 through DCN4.2, each adding both `*_hwseq.o` and `*_init.o` where present. Paths are formed with `$(addprefix $(AMDDALPATH)/dc/hwss/<generation>/,...)`.

Control flow: this is build-system flow only. Kbuild includes the selected object paths in the AMD display driver. The ordering groups legacy DCE first, then DCN generations, with newer entries including DCN35, DCN351, DCN401, and DCN42.

State and persistence: no runtime state. The file persists build membership: missing an object prevents the corresponding generation's hardware sequencer code from being linked, while stale entries break builds when files are renamed or config gates change.

Dependencies and integration points: depends on top-level AMDGPU Display Core Kbuild variables such as `AMDDALPATH`, `AMD_DISPLAY_FILES`, `CONFIG_DRM_AMD_DC_SI`, and `CONFIG_DRM_AMD_DC_FP`. It integrates all `dc/hwss/*` generation folders into the kernel module build.

Risks and test signals: wrong gating can either omit required ASIC support or include FP-dependent DCN code in unsupported builds. Object list drift is likely when adding new generations. Signals include allmodconfig/allyesconfig kernel builds, `CONFIG_DRM_AMD_DC_FP=n` builds, SI-specific builds, and link checks that generation constructors referenced by resource code are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce/dce_hwseq.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce/dce_hwseq.c

Purpose: implements shared DCE hardware sequencer helpers for front-end clock control, pipe update locking, blender mode programming, light sleep or SRAM power-up handling, CRTC clock-source selection, and LUT-use decisions.

Important APIs and functions: `dce_enable_fe_clock()` toggles `DCFE_CLOCK_ENABLE`. `dce_pipe_control_lock()` coordinates vertical update locks for DCP graphics, scaler, blender, and update lock mode, avoiding locking an already blanked pipe and applying a CRTC hblank write workaround when unlocking. `dce60_pipe_control_lock()` is a no-op for SI/DCE6 because that register is absent. `dce_set_blender_mode()` programs feedthrough, blend mode, alpha mode, and multiplied mode. `dce_clock_gating_power_up()` either calls placeholder light-sleep enable helpers or disables SRAM shutdown and enables underlay clock. `dce_crtc_switch_to_clk_src()` selects DP DTO, combo PHY PLL, or legacy PLL pixel-rate sources. `dce_use_lut()` returns true only for ARGB8888/ABGR8888.

Control flow: all functions are direct hardware register updates through `reg_helper`. `dce_pipe_control_lock()` first checks blank state through the timing generator, reads current lock register, modifies relevant fields, conditionally writes blender-specific fields if masks exist, and performs a workaround on unlock. Clock-source switching branches on `clock_source->id` and logs an error for unknown ids.

State and persistence: persistent state is hardware clock, update lock, blender, memory power, underlay clock, and pixel-rate source registers. No heap or file state is used. The helpers may leave update locks set until a matching unlock call, so sequencing discipline is critical.

Dependencies and integration points: includes `dce_hwseq.h`, `reg_helper.h`, private HW sequencer definitions, and core types. It integrates with DCE generation constructors, timing generators, blender programming, clock source programming, and surface format paths.

Risks and test signals: update locks can deadlock visual updates if not released; clock-source selection errors can blank displays; placeholder light-sleep helpers indicate incomplete power optimization. Mask checks handle generation differences, but missing masks can silently skip fields. Signals include DCE modeset, pipe lock/unlock stress, blanked-pipe update tests, multi-plane blending, DP and PLL clock-source switching, SI builds, and format LUT validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce/dce_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce/dce_hwseq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce/dce_hwseq.h

Purpose: defines shared DCE/DCN hardware sequencer register lists, mask/shift lists, register storage structs, field storage structs, blender modes, and public helper prototypes. It is the central compile-time register contract for many AMD Display Core hardware sequencer generations.

Important APIs and types: register-list macros cover DCE6/8/10/11/12, VG20, and DCN1/2/2.01/2.1/3.0/3.01/3.02/3.03 variants, selecting clock, blender, pixel-rate, PHYPLL, DCHUB, MMHUB, power-domain, VGA, CRC, audio, HPO, ODM, DMU, and memory power registers. `struct dce_hwseq_registers` stores resolved register addresses. Mask/shift macros such as `HWSEQ_DCE10_MASK_SH_LIST()`, `HWSEQ_DCN_MASK_SH_LIST()`, and generation-specific DCN lists define field mappings. `struct dce_hwseq_shift` and `struct dce_hwseq_mask` aggregate all supported field names through `HWSEQ_*_REG_FIELD_LIST` macros. `enum blnd_mode` and function prototypes expose helper behavior implemented in `dce_hwseq.c`.

Control flow: no executable code is present, but macro composition controls which fields each ASIC generation can access. Resource files instantiate these macros into concrete register tables; `reg_helper` consumers then use `hws->regs`, `hws->shifts`, and `hws->masks` at runtime.

State and persistence: this header describes persistent hardware register state: clock enables, pixel-rate sources, blender update locks, VM aperture and page-table registers, power-gating domains, global timers, CRC controls, VGA disable state, audio DTO, HPO clocks, and DCN power management fields. The C structs hold register addresses and masks, not runtime hardware values.

Dependencies and integration points: includes `dc_types.h` and forward declares `dce_hwseq`, `pipe_ctx`, and `clock_source`. It is consumed by many DCE/DCN HWSS generation files and by register table definitions generated from ASIC headers. It is also related to the `hwss/Makefile` because each compiled generation relies on these common declarations.

Risks and test signals: this file is large, macro-heavy, and generation-sensitive. Duplicate entries, missing fields, or stale register names can compile for one ASIC and fail or misprogram another. Comments note temporary direct MMHUB reads instead of GVM-owned data, which is an architectural risk. Signals include broad AMDGPU build matrices, per-ASIC register table validation, power-gating tests across domains, VGA disable validation, CRC debug tests, clock-source switching, and static analysis for duplicate macro fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce/dce_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.c

Purpose: implements DCE 10.0 hardware sequencer specialization. It customizes display power gating, bandwidth preparation/optimization, construction, and DCC/tiling reset behavior on top of DCE 11.0 shared sequencing.

Important APIs and functions: `dce100_enable_display_power_gating()` maps generic pipe gating control to BIOS command table actions, calls `dc_bios->enable_disp_power_gating()`, and resets `MASTER_UPDATE_MODE` to 0 because BIOS sets it to 2. `dce100_prepare_bandwidth()` and `dce100_optimize_bandwidth()` set safe display marks then update clocks with optimize false or true. `dce100_hw_sequencer_construct()` starts from `dce110_hw_sequencer_construct()` and overrides function pointers. `dce100_reset_surface_dcc_and_tiling()` clears mem-input tiling when requested and forces an immediate surface flip/address program.

Control flow: power gating skips BIOS calls for `PIPE_GATING_CONTROL_INIT` on nonzero controllers, otherwise calls BIOS with controller id plus one and the mapped action. Bandwidth functions delegate to DCE110 watermark logic then clock manager. Reset surface flow exits if no mem input, optionally clears tiling through `mem_input_clear_tiling`, then calls `mem_input_program_surface_flip_and_addr()` with immediate flip.

State and persistence: persists BIOS-programmed pipe power state, CRTC `MASTER_UPDATE_MODE`, display watermark/clock state through delegated helpers, mem-input tiling state, and surface address latches. It mutates `dc->hwseq->funcs` and `dc->hwss` function tables during construction.

Dependencies and integration points: includes Display Core services/types, clock manager, resource definitions, `dce100_hwseq.h`, DCE110 HWSS, and DCE10 register headers. It integrates with BIOS command tables, clock manager, mem-input/HUBP-style plane resources, and the DCE110 base sequencer.

Risks and test signals: BIOS command table side effects require the explicit `MASTER_UPDATE_MODE` repair; removing it can break update sequencing. Immediate flips after clearing tiling are necessary to avoid stale framebuffer interpretation but can be visible if called at the wrong time. Signals include DCE10 modeset, suspend/resume and power-gating tests, bandwidth/clock transition validation, tiling clear with immediate flip, and BIOS table failure-path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.h

Purpose: declares the public DCE 10.0 hardware sequencer entry points used by resource construction and HWSS function tables.

Important APIs: declares `dce100_hw_sequencer_construct()`, `dce100_prepare_bandwidth()`, `dce100_optimize_bandwidth()`, `dce100_enable_display_power_gating()`, and `dce100_reset_surface_dcc_and_tiling()`. It forward declares `struct dc` and `struct dc_state` and includes `core_types.h` plus `hw_sequencer_private.h` for `pipe_ctx`, `dc_plane_state`, and pipe gating types.

Control flow: declaration-only. The implementation in `dce100_hwseq.c` installs these functions into `dc->hwseq->funcs` and `dc->hwss` after constructing the DCE110 base sequencer.

State and persistence: no local state. Declared functions mutate hardware power gating, clocks/watermarks, mem-input tiling, and surface address state when called.

Dependencies and integration points: used by DCE10 resource construction and by code that needs DCE100-specific HWSS overrides. It sits between shared DCE110 behavior, BIOS command tables, clock manager, and plane mem-input resources.

Risks and test signals: prototype drift breaks function table assignment or hides ABI changes in common HWSS code. Because the declared functions touch power and immediate flips, validation should include DCE10 build coverage, power-gating paths, bandwidth transitions, and clear-DCC/tiling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.h -->
