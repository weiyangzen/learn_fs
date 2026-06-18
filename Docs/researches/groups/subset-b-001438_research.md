# subset-b-001438 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn10/dcn10_hubp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn10/dcn10_hubp.c

Purpose: implements the DCN 1.0 HUBP backend for AMD display. It programs HUBP surface addresses, tiling, pitch, pixel format, VM aperture/context0, DLG/TTU/requestor timing, viewport, cursor, blanking, underflow, clock, VTG selection, and the DCN10 `hubp_funcs` vtable used by higher display core code.

Important APIs and functions: `dcn10_hubp_construct` wires a `dcn10_hubp` to register tables, shifts/masks, instance id, context, and `dcn10_hubp_funcs`. Surface programming is split across `hubp1_program_surface_config`, `hubp1_dcc_control`, `hubp1_program_tiling`, `hubp1_program_size`, `hubp1_program_rotation`, `hubp1_program_pixel_format`, and `hubp1_program_surface_flip_and_addr`. Timing/request paths are `hubp1_program_requestor`, `hubp1_program_deadline`, `hubp1_setup`, and `hubp1_setup_interdependent`. State and debug paths include `hubp1_read_state_common`, `hubp1_read_state`, `hubp1_is_flip_pending`, `hubp1_clear_underflow`, `hubp1_set_flip_int`, and `hubp1_wait_pipe_read_start`. Cursor APIs are `hubp1_cursor_set_attributes`, `hubp1_cursor_set_position`, and `hubp1_get_cursor_pitch`.

Control flow: normal plane enable flows through the vtable into surface config, which enables/disables DCC, writes GFX9 tiling fields, computes luma/chroma pitch minus one, writes rotation/mirror, then maps `surface_pixel_format` enums to hardware format values and crossbar selection. A flip writes `SURFACE_FLIP_TYPE`, stereo flip bits, TMZ/DCC surface control bits, optional metadata addresses, then high address registers before low address registers because the low primary address write latches the update when update lock is not used. Setup writes requestor registers, deadline registers, and a vready workaround while OTG is locked. Interdependent setup writes prefetch, vblank, per-line delivery, TTU pre-delivery, and global TTU fields.

State and persistence behavior: this file persists software state in `struct hubp`, notably `request_address`, `curs_attr`, `curs_pos`, `mpcc_id`, `opp_id`, and cursor offload/reset fields. It also snapshots hardware into `struct dcn_hubp_state` for diagnostics. `hubp1_is_flip_pending` uses both the hardware pending bit and a comparison between earliest-in-use address and the cached requested graphics address. Blanking updates `mpcc_id` and `opp_id` to disconnected values. VM aperture helpers write shifted physical addresses and enable L1 TLB/system access.

Dependencies and integration points: depends on `reg_helper` macros for MMIO access, `dm_services` assertions/logging, `dce_calcs`, fixed-point conversion helpers, DML register structures (`_vcs_dpi_display_*`), `dc_plane_address`, `dc_tiling_info`, `plane_size`, DCC params, cursor structs, and the common `hubp` interface. It is the base implementation reused directly by DCN201/DCN21/DCN30 for many functions.

Risks: register write ordering is critical for flips; zero-address cases silently break out but still copy `request_address`, which can affect pending detection. `hubp1_program_size` asserts on zero chroma pitch because it can hang hardware. Pixel format mapping uses hard-coded hardware values and breaks to debugger on unknown formats. The vready workaround divides by `htotal` without a local zero guard. DCN1 VM aperture packing differs from later DCN, so readback shifts are easy to regress. Cursor position divides by pixel clock and relies on valid scaling ratios.

Test signals: useful validation includes register-readback tests for pitch/tiling/format/DCC fields, flip tests for graphics/video/stereo with meta and TMZ addresses, flip-pending behavior against earliest-in-use, cursor clipping/rotation/hotspot tests, blank/power-gated wait behavior, and underflow clear/readback. Kernel display tests should include modesets, page flips, cursor moves, NV12/video planes, DCC-enabled planes, and VM aperture programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn10/dcn10_hubp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn10/dcn10_hubp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn10/dcn10_hubp.h

Purpose: declares the DCN10 HUBP register model, field shift/mask model, state snapshots, concrete `dcn10_hubp` object, and exported DCN1 helper functions. It is the foundational header for later DCN20/DCN201/DCN21/DCN30 HUBP implementations.

Important APIs and types: `TO_DCN10_HUBP` casts the common `hubp` to `dcn10_hubp`. `HUBP_REG_LIST_DCN`, `HUBP_REG_LIST_DCN_VM`, and `HUBP_REG_LIST_DCN10` define register-address lists. `HUBP_COMMON_REG_VARIABLE_LIST`, `DCN_HUBP_REG_FIELD_BASE_LIST`, and `DCN_HUBP_REG_FIELD_LIST` generate register, shift, and mask structs. `struct dcn_mi_registers`, `struct dcn_mi_shift`, and `struct dcn_mi_mask` hold MMIO register offsets and field metadata. `struct dcn_hubp_reg_state` and `struct dcn_hubp_state` are diagnostic/readback containers. `struct dcn10_hubp` embeds `struct hubp` plus state and register metadata. Prototypes expose DCN1 programming routines and constructor.

Control flow role: this header does not execute logic, but it controls how implementation files bind symbolic registers and fields through `REG()` and `FN()` macros. The macro lists are consumed by ASIC-specific resource code to instantiate register tables and by C files to perform register writes without hard-coding offsets.

State and persistence behavior: `struct dcn_hubp_state` persists readback of DLG, TTU, requestor, pixel format, viewport, rotation, DCC, blank, clock, underflow, QoS, primary surface, meta address, and selected raw control registers. `struct dcn_hubp_reg_state` is a broader raw-register dump used by newer generations as well, so adding fields affects multiple DCN versions.

Dependencies and integration points: includes `hubp.h` and references DML register structures, fixed display enums, cursor enums, DCC parameters, VM parameters, and common AMD display types. Later headers include this file to reuse the common register list and state definitions.

Risks: macro-generated register/field lists must stay synchronized with actual hardware definitions and implementation reads/writes. Typos are ABI-like here: both legacy `PREFETCH_SETTINS` and newer `PREFETCH_SETTINGS` coexist for compatibility. `dcn_hubp_reg_state` contains fields from generations beyond DCN10, so consumers must check register availability before reading. Field-list omissions can compile but produce broken register programming when a function uses a missing mask/shift.

Test signals: compile coverage across all ASIC register table instantiations is important. Runtime signals include successful register access for every field used by DCN10 C code, read-state dumps with sane values, and no missing field initializers in ASIC-specific HUBP register definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn10/dcn10_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn20/dcn20_hubp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn20/dcn20_hubp.c

Purpose: implements DCN2.0 HUBP behavior. It extends DCN1 with compressed GFX10 tiling rules, VMID and updated aperture programming, DMDATA support, triple-buffer and GSL controls, cursor offload state caching, DCN2 request/deadline programming, readback, and DML validation diagnostics.

Important APIs and functions: `hubp2_construct` installs `dcn20_hubp_funcs`. VM and timing APIs are `hubp2_set_vm_system_aperture_settings`, `hubp2_program_requestor`, `hubp2_program_deadline`, `hubp2_vready_at_or_After_vsync`, `hubp2_setup`, and `hubp2_setup_interdependent`. Surface programming uses `hubp2_program_surface_config`, private `hubp2_program_tiling`, `hubp2_program_size`, `hubp2_program_rotation`, `hubp2_program_pixel_format`, `hubp2_dcc_control`, and `hubp2_program_surface_flip_and_addr`. Cursor and metadata paths are `hubp2_cursor_set_attributes`, `hubp2_cursor_set_position`, `hubp2_dmdata_set_attributes`, `hubp2_dmdata_load`, and `hubp2_dmdata_status_done`. Control/readback helpers include triple-buffer, GSL, blanking, flip pending, clock, VTG, underflow, read state, and `hubp2_validate_dml_output`.

Control flow: setup first evaluates vready timing, then programs requestor and deadline registers. Surface config enables DCC, programs DCN2 tiling with only active GFX10 fields, sets pitch including RGBE alpha/chroma handling, writes rotation and pixel format. Flip programming writes flip type, VMID, TMZ bits, optional meta addresses, and surface addresses in high-before-low order for graphics, video progressive, and stereo. DMDATA hardware mode uses `SURFACE_UPDATE_LOCK` while toggling update and writing the DMDATA address; software mode toggles SW update and streams words into the DMDATA buffer.

State and persistence behavior: like DCN10, the function caches `request_address`; it also caches cursor register images in `hubp->att`, `hubp->pos`, and `hubp->cur_rect`, which lets cursor offload paths avoid direct MMIO and supports PSR selective update damage tracking. `hubp2_read_state_common/read_state` populate `dcn_hubp_state`, including raw `DCHUBP_CNTL` and flip control when registers exist. Blank handling waits for no outstanding requests before setting blank but leaves `HUBP_TTU_DISABLE` as zero in `hubp2_set_blank_regs`.

Dependencies and integration points: builds on `dcn10_hubp.h` definitions and reuses selected DCN1 helpers (`hubp_reset`, viewport, init, in-blank, soft reset, flip interrupt). Integrates with DML-generated request/deadline/TTU structures, PSR stream/link state for cursor rectangles, DM logger for validation output, and the common `hubp_funcs` dispatch used by resource construction.

Risks: DML validation is debug logging only and has many manually duplicated register comparisons, so mismatched labels or omissions can mislead debugging. `hubp2_cursor_set_position` divides by `pixel_clk_khz`; callers must provide valid timing. Cursor offload must keep cached state and hardware writes coherent. DMDATA SW mode assumes `dmdata_sw_size / 4` words are available. Surface flip zero-address paths break out but still update cached request address. VM aperture uses 48:18 packing unlike DCN1 default-address programming.

Test signals: test page flips with VMID changes, immediate vs vsync flips, DCC/meta planes, video progressive planes, stereo planes, triple-buffer toggling, GSL enable, DMDATA HW/SW modes, cursor offload and normal cursor paths, PSR SU cursor rectangle updates, blank/unblank waits, and DML validation logs against known DML outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn20/dcn20_hubp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn20/dcn20_hubp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn20/dcn20_hubp.h

Purpose: declares the DCN2+ HUBP register and field model plus the DCN20 concrete object and exported helper APIs. It extends DCN10 with DMDATA, VMID, flip timing, triple-buffer, GSL, cursor0 register naming, and forward-compatible DCN21/DCN30/DCN32/DCN401/DCN42 fields.

Important APIs and types: `TO_DCN20_HUBP` casts to `struct dcn20_hubp`. `HUBP_REG_LIST_DCN2_COMMON` and `HUBP_REG_LIST_DCN20` define DCN2 register address sets. `HUBP_MASK_SH_LIST_DCN2_SHARE_COMMON`, `HUBP_MASK_SH_LIST_DCN2_COMMON`, and `HUBP_MASK_SH_LIST_DCN20` define field mappings. `DCN2_HUBP_REG_COMMON_VARIABLE_LIST`, `DCN21_HUBP_REG_COMMON_VARIABLE_LIST`, `DCN30_HUBP_REG_COMMON_VARIABLE_LIST`, and later lists extend the register struct for newer ASICs. `struct dcn_hubp2_registers`, `struct dcn_hubp2_shift`, and `struct dcn_hubp2_mask` intentionally include the broadest later-generation fields. `struct dcn20_hubp` embeds common `hubp`, state, and register metadata.

Control flow role: implementation files use this header to select generation-specific subsets from a common super-struct. DCN20 code consumes the DCN2 subset; DCN21 and DCN30 use the broader register/field lists while still storing pointers as `dcn_hubp2_*`.

State and persistence behavior: the header reuses `struct dcn_hubp_state` from DCN10 rather than defining a separate state object. Function prototypes expose persistent hardware features like triple buffering, DMDATA status, and register readback that higher layers invoke through `hubp_funcs`.

Dependencies and integration points: includes `../dcn10/dcn10_hubp.h`, so it is layered on top of the DCN1 register/state definitions. It is included by DCN20 C and later DCN generation implementations. Its forward declarations are used by resource code that constructs generation-specific HUBP instances.

Risks: because this header contains fields for multiple future generations, accidental use of a register absent on a given ASIC can compile but fail at runtime unless implementation checks `REG(field)`. Register and field lists must remain aligned with generated ASIC register headers. The super-struct approach increases coupling between old DCN20 code and later-generation additions.

Test signals: compile all ASIC variants that instantiate these lists, verify no missing initializers for DCN2/DCN21/DCN30 register tables, and exercise runtime paths that check optional registers. DMDATA, VMID, triple-buffer, GSL, and cursor field programming are key integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn20/dcn20_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn201/dcn201_hubp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn201/dcn201_hubp.c

Purpose: implements the DCN2.0.1 HUBP variant by composing DCN1 and DCN2 helpers behind a dedicated `hubp_funcs` table. It is a compatibility layer for hardware that has DCN2-style DMDATA/triple-buffer bits but lacks some full DCN2 requestor/PTE programming.

Important APIs and functions: `dcn201_hubp_construct` installs `dcn201_hubp_funcs`. Private wrappers are `hubp201_program_surface_config`, `hubp201_program_deadline`, `hubp201_program_requestor`, and `hubp201_setup`. The vtable maps many operations to DCN1 helpers (`hubp1_program_surface_flip_and_addr`, `hubp1_is_flip_pending`, `hubp1_set_blank`, DCC, viewport, clock, VTG, clear underflow, init, clear tiling) while using DCN2 helpers for setup interdependent timing, cursor attributes, DMDATA, triple-buffer, GSL, and read state.

Control flow: setup calls the DCN2 vready calculation, then the DCN201 requestor writer, then DCN1 deadline programming. The custom requestor writer programs DET buffer base and expansion modes but intentionally writes only chunk/min/meta/swath fields and comments that PTE programming is unnecessary. Surface config uses DCN1 tiling, size, pixel format, and DCC, and ignores rotation/horizontal mirror in this wrapper.

State and persistence behavior: constructor initializes base context, register metadata, instance id, invalid OPP, and disconnected MPCC. Runtime state persistence is inherited from called DCN1/DCN2 helpers: request address, cursor state, DMDATA state, and `dcn_hubp_state` readback.

Dependencies and integration points: includes both DCN10 and DCN20 headers through `dcn201_hubp.h`. It depends on the DCN201-specific register/field structs while delegating most behavior to shared DCN1/DCN2 functions. It integrates with common resource construction through `dcn201_hubp_construct`.

Risks: function composition is easy to misread: this variant uses DCN1 address flips with no VMID programming but DCN2 DMDATA and triple-buffer support. `hubp201_program_surface_config` accepts rotation and mirror parameters but does not call a rotation helper. Requestor programming omits PTE fields by design, so using a full DCN2 expectation would be wrong. Mixed DCN1 cursor position with DCN2 cursor attributes can regress if cached cursor state semantics diverge.

Test signals: run DCN201-specific modeset/plane tests that verify requestor fields exclude PTE programming, DMDATA works, triple-buffer toggles, flips use the expected DCN1 address path, and rotation/mirror behavior matches hardware support expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn201/dcn201_hubp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn201/dcn201_hubp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn201/dcn201_hubp.h

Purpose: declares the DCN201 HUBP register/field subset and concrete object. It captures a hybrid hardware surface: based on DCN common registers, with prefetch settings, cursor0, DMDATA, triple-buffer, vready, and limited flip-parameter support.

Important APIs and types: `TO_DCN201_HUBP` casts from `hubp`. `HUBP_REG_LIST_DCN201` defines the DCN201 register set, including common DCN registers, prefetch, flip control2, cursor registers, DMDATA registers, and selected flip parameters. `HUBP_MASK_SH_LIST_DCN201` defines fields, including DCN common fields, cursor fields, DMDATA fields, triple-buffer, vready, disable-stop-data-during-VM, and master update lock status. `struct dcn201_hubp_registers`, `struct dcn201_hubp_shift`, `struct dcn201_hubp_mask`, and `struct dcn201_hubp` provide the concrete register metadata and object. `dcn201_hubp_construct` is the exported constructor.

Control flow role: the header enables a narrow C implementation to bind DCN201-specific register tables while reusing DCN1/DCN2 helper functions. Its macro lists determine which shared helper calls can safely access registers on this ASIC.

State and persistence behavior: `struct dcn201_hubp` embeds common `struct hubp` and shared `dcn_hubp_state`; no extra persistent fields are introduced. State behavior therefore follows delegated DCN1/DCN2 helpers.

Dependencies and integration points: includes both `dcn10_hubp.h` and `dcn20_hubp.h`, making it an explicit bridge generation. Resource construction code supplies `dcn201_hubp_registers`, shifts, and masks.

Risks: the register list lacks some full DCN2 fields, so assigning a DCN2 helper that touches absent registers would be unsafe. Field-list omissions can break DMDATA or flip timing silently. The include guard closing comment references DCN20, which is cosmetic but can confuse maintenance.

Test signals: build-time register initialization for DCN201, plus runtime DMDATA, cursor, prefetch, triple-buffer, vready, and flip register tests on DCN201 hardware or register-model tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn201/dcn201_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn21/dcn21_hubp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn21/dcn21_hubp.c

Purpose: implements DCN2.1 HUBP specialization. It adds host-VM deadline workaround logic, DCN21 requestor field mapping, DCN21 aperture programming, a DMCUB-assisted video flip workaround path, expanded DML validation, viewport programming, init chicken-bit setup, and a DCN21 `hubp_funcs` table.

Important APIs and functions: exported functions include `apply_DEDCN21_142_wa_for_hostvm_deadline`, `hubp21_program_deadline`, `hubp21_program_requestor`, and `hubp21_construct`. Private functions include `hubp21_setup`, `hubp21_set_viewport`, `hubp21_set_vm_system_aperture_settings`, `hubp21_validate_dml_output`, `program_surface_flip_and_addr`, `dmcub_PLAT_54186_wa`, `hubp21_program_surface_flip_and_addr`, and `hubp21_init`.

Control flow: setup calls DCN2 vready logic, DCN21 requestor programming, then DCN21 deadline programming. The deadline path delegates common DCN2 programming and then applies DEDCN21-142 by only lowering host-VM deadline registers when the new value is more aggressive or the hardware value is uninitialized; chroma flip PTE/meta fields are always written. Requestor programming maps luma MPTE group size into `VM_GROUP_SIZE` and omits chroma MPTE group. Surface flip first stages desired register values in `surface_flip_registers`, then either sends a DMUB command for video progressive flips when `enable_dmcub_surface_flip` is set, or writes registers directly in order.

State and persistence behavior: the constructor initializes common object state. Flip paths cache `hubp->request_address`. `hubp21_init` writes `HUBPREQ_DEBUG` bit 26 for DEDCN21-133 before resetting software HUBP state. The workaround reads current host-VM deadline registers and preserves more aggressive existing values, so hardware state intentionally persists across mode switches rather than being blindly overwritten.

Dependencies and integration points: depends on DCN10/DCN20 helpers, `dc_dmub_srv.h`, `union dmub_rb_cmd`, and `dc_wake_and_execute_dmub_cmd` for firmware-mediated flips. Uses `ctx->dc->debug.enable_dmcub_surface_flip` as an integration switch. Shares DML structures and DM logger validation patterns with DCN20.

Risks: host-VM deadline workaround depends on comparing unsigned register values correctly; overly conservative values can underflow at transitions. DMUB video flip path only sends selected primary surface fields and relies on firmware implementation. Direct flip programming writes many meta/surface registers even when staged values are zero, unlike older per-address conditional writes. DML validation duplicates large DCN20 logic and can drift. The debug init write overwrites `HUBPREQ_DEBUG` with bit 26 rather than preserving other bits.

Test signals: test mode switches involving host VM and flips for underflow/corruption, validate DEDCN21-142 register behavior across increasing/decreasing deadline values, exercise direct and DMUB video flip paths, verify stereo/video/graphics flips, run DML validation logging, and confirm init chicken bit plus cursor/DMDATA inherited paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn21/dcn21_hubp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn21/dcn21_hubp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn21/dcn21_hubp.h

Purpose: declares the DCN21 HUBP register/field additions and concrete object. DCN21 extends DCN2 common support with extra flip and vblank parameters for host-VM deadlines and a `VM_GROUP_SIZE` requestor field.

Important APIs and types: `TO_DCN21_HUBP` casts from common `hubp`. `HUBP_REG_LIST_DCN21` adds `FLIP_PARAMETERS_3` through `FLIP_PARAMETERS_6` and `VBLANK_PARAMETERS_5/6` on top of DCN2 common registers. `HUBP_MASK_SH_LIST_DCN21_COMMON` maps common DCN/share/VM/cursor/DMDATA/flip/GSL/VMID fields plus DCN21 host-VM deadline fields. `HUBP_MASK_SH_LIST_DCN21` adds RB alignment. `struct dcn21_hubp` embeds common HUBP state and register pointers plus `PLAT_54186_wa_chroma_addr_offset`. Prototypes expose construction, host-VM deadline workaround, deadline programming, and requestor programming.

Control flow role: this header lets `dcn21_hubp.c` and later DCN30 code use DCN21 requestor/deadline helpers with the correct field names. The `VM_GROUP_SIZE` mapping is central because requestor programming stores luma MPTE group size there instead of `MPTE_GROUP_SIZE`.

State and persistence behavior: the extra `PLAT_54186_wa_chroma_addr_offset` field is persistent object state reserved for a platform workaround, though the shown C implementation does not use it directly. Other state is inherited from `struct hubp` and `dcn_hubp_state`.

Dependencies and integration points: includes DCN20 and DCN10 headers. The exported DCN21 helpers are reused by DCN30 setup paths, so changes here affect multiple generations.

Risks: the broad common mask list combines DCN2 behavior with DCN21-only fields; wrong ASIC table use can access missing registers. The declared workaround state field can become stale or unused unless kept aligned with DMUB/platform workaround code. Requestor field naming differences are easy to regress in validation or readback.

Test signals: compile all DCN21 register table instantiations; runtime tests should confirm host-VM deadline registers, VM group requestor field, DMDATA status, GSL/triple-buffer, VMID, and cursor register mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn21/dcn21_hubp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30/dcn30_hubp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30/dcn30_hubp.c

Purpose: implements DCN3.0 HUBP behavior using the DCN20 object layout and DCN21 request/deadline helpers where appropriate. It adds DCN3 surface address support for RGBE alpha and stereo alpha planes, NUM_PKRS tiling, newer DCC independent block fields, DMDATA VM timing, broad raw register readback, and DCN3 initialization.

Important APIs and functions: exported APIs include `hubp3_set_vm_system_aperture_settings`, `hubp3_program_surface_flip_and_addr`, `hubp3_program_tiling`, `hubp3_clear_tiling`, `hubp3_dcc_control`, `hubp3_dcc_control_sienna_cichlid`, `hubp3_dmdata_set_attributes`, `hubp3_program_surface_config`, `hubp3_read_state`, `hubp3_read_reg_state`, `hubp3_setup`, `hubp3_init`, and `hubp3_construct`. The private `hubp3_program_deadline` extends DCN2 deadline programming with `REFCYC_PER_VM_DMDATA`.

Control flow: VM aperture setup programs low/high 48:18 aperture addresses and enables L1 TLB. Surface flip writes flip type, conditionally updates VMID only for non-immediate flips, controls stereo sync bits, then programs address/meta registers for graphics, video progressive, stereo with alpha planes, and RGBE alpha. Surface config writes Sienna Cichlid-style DCC fields, DCN3 tiling including packetizer count, DCN2 pitch/rotation/pixel-format. Setup calls DCN2 vready, DCN21 requestor, and DCN3 deadline. Init writes the DEDCN21-133 debug bit, clears TTU disable, and resets software HUBP state.

State and persistence behavior: inherited `hubp` software state stores the requested address, cursor caches, blank IDs, and reset state. `hubp3_read_state` populates `dcn_hubp_state` and optionally stores raw `UCLK_PSTATE_FORCE`, `DCHUBP_CNTL`, and flip control. `hubp3_read_reg_state` dumps a large raw register snapshot into `dcn_hubp_reg_state`, including MALL, VMPG, DMDATA VM, flip, viewport, requestor, memory power, and read-line registers.

Dependencies and integration points: includes DCN30 header plus DCN20 and DCN21 headers. Reuses DCN2 cursor, blank, clock, VTG, triple-buffer, DMDATA load/status, GSL, underflow, in-blank, soft reset, and flip interrupt helpers. Uses DCN21 requestor programming, so DCN30 inherits `VM_GROUP_SIZE` semantics. The vtable exposes `hubp_read_reg_state` for diagnostics not present in earlier tables.

Risks: immediate flips skip VMID programming, so callers must ensure VMID state is correct for immediate updates. Stereo and RGBE alpha paths require alpha addresses and metadata to be valid; zero checks only guard top-level address pairs. `hubp3_dcc_control_sienna_cichlid` writes luma/chroma independent block sizes from DCC params, so wrong DCC metadata can corrupt fetch. `hubp3_read_reg_state` reads many registers unconditionally; it must only be used with register tables that define them. The init debug write may clobber other `HUBPREQ_DEBUG` bits.

Test signals: validate graphics, video, stereo-alpha, and RGBE-alpha flips; immediate flip VMID behavior; DCC luma/chroma independent block settings; NUM_PKRS tiling; DMDATA HW flips and VM timing; broad raw register dump paths; MALL/VMPG register availability; and inherited cursor/triple-buffer/GSL/blank behavior on DCN3 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30/dcn30_hubp.c -->
