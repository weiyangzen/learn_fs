# Research: subset-b-001437

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn30/dcn30_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn30/dcn30_hubbub.h

## Purpose

`dcn30_hubbub.h` is the DCN 3.0 Hubbub interface header. It extends the DCN2.1 Hubbub register model with DCN3 watermark, VM fault, urgent bandwidth, trip-to-memory, and p-state-control fields, and declares the DCN3 shared Hubbub construction and programming entry points consumed by ASIC-specific Hubbub implementations.

## Important APIs, Types, And Functions

- `HUBBUB_REG_LIST_DCN3AG(id)` and `HUBBUB_MASK_SH_LIST_DCN3AG(mask_sh)` alias the DCN2.1 register and mask/shift lists for the AG variant.
- `HUBBUB_REG_LIST_DCN30(id)` combines common DCN2.0 registers, self-refresh watermark registers, fractional urgent bandwidth registers for sets A-D, and refcycle-per-trip registers for sets A-D.
- `HUBBUB_MASK_SH_LIST_DCN30(mask_sh)` defines field bindings for global timer refdiv, VM framebuffer/AGP apertures, urgent and VM-row watermarks, DCHUBBUB memory trip metrics, VM fault reporting and interrupt controls, and stutter/self-refresh masks.
- Exported functions include `hubbub3_construct`, `hubbub3_init_dchub_sys_ctx`, `hubbub3_dcc_support_swizzle`, `hubbub3_get_dcc_compression_cap`, `hubbub3_program_watermarks`, `hubbub3_force_wm_propagate_to_pipes`, `hubbub3_force_pstate_change_control`, `hubbub3_init_watermarks`, and `hubbub3_read_reg_state`.

## Control Flow

This header does not execute control flow directly. It supplies the generation-specific register maps that C files expand into `struct dcn_hubbub_registers`, `struct dcn_hubbub_shift`, and `struct dcn_hubbub_mask` tables, then declares the functions that operate on those tables. Runtime control flow enters through a generation constructor, installs a `struct hubbub_funcs` table, and later calls the declared helpers through DC resource and HWSS paths.

## State And Persistence Behavior

No state is owned by the header. Its macros determine which MMIO registers and fields can be addressed by DCN3 Hubbub code. The declared functions mutate in-memory `struct dcn20_hubbub` cache fields and hardware registers in their implementation files, especially watermarks, VM aperture registers, DCC capability outputs, p-state force bits, and register-state snapshots.

## Dependencies And Integration Points

The header depends on `dcn21/dcn21_hubbub.h` for base Hubbub macros, structs, and inherited function declarations. It integrates with AMD Display Core resource construction, ASIC register table generation, Hubbub function-table dispatch, DCC capability checks used by surface validation, watermark programming used by bandwidth/DML decisions, and VM aperture setup used during display init.

## Risks And Edge Cases

- Macro expansion order is critical: missing or duplicate register fields can silently misalign generated register tables with later `REG_*` calls.
- DCN30 still inherits many DCN2.1 definitions; ASIC variants must verify that reused field names are valid for their register headers.
- VM fault and watermark fields are exposed here but only safe when the selected C implementation uses matching masks and shifts.
- The header declares shared functions used by later generations; signature drift would break multiple ASIC implementations at compile time.

## Test Signals

Build coverage is the main signal: register-table expansion errors, missing field names, and function prototype mismatches fail kernel compilation. Runtime signals include successful display init, DCC capability selection, watermark programming without register access faults, VM aperture setup, and debug reads from `hubbub3_read_reg_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn30/dcn30_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn301/dcn301_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn301/dcn301_hubbub.c

## Purpose

`dcn301_hubbub.c` constructs the DCN3.01 Hubbub object. It is intentionally small: it selects a DCN3.01 `hubbub_funcs` table that mostly reuses DCN2/DCN2.1/DCN3 helpers, wires register/mask/shift tables into `struct dcn20_hubbub`, and sets the generation-specific p-state debug index and detile-buffer size.

## Important APIs, Types, And Functions

- `hubbub301_funcs`: static `struct hubbub_funcs` table. It maps core operations to `hubbub2_update_dchub`, `hubbub21_init_dchub`, `hubbub2_init_vm_ctx`, `hubbub3_dcc_support_swizzle`, `hubbub2_dcc_support_pixel_format`, `hubbub3_get_dcc_compression_cap`, `hubbub21_wm_read_state`, `hubbub2_get_dchub_ref_freq`, `hubbub3_program_watermarks`, self-refresh/p-state helpers, watermark propagation, watermark init, and `hubbub2_read_state`.
- `hubbub301_construct(...)`: exported constructor that initializes context, function table, register table pointers, masks, shifts, `debug_test_index_pstate`, and `detile_buf_size`.

## Control Flow

Construction is linear. The caller provides prebuilt register/mask/shift tables. `hubbub301_construct` stores the context and table pointers, assigns `&hubbub301_funcs` to `hubbub3->base.funcs`, sets `debug_test_index_pstate` to `0xB`, and fixes the detile buffer size at 184 KiB. All later runtime behavior is dispatched through the function table to inherited helpers.

## State And Persistence Behavior

The file mutates only the in-memory Hubbub object during construction. Persistent effects happen later through the installed callbacks, which program DCHUB, VM context, watermarks, self-refresh, p-state force, and DCC capability outputs. There is no on-disk persistence.

## Dependencies And Integration Points

The implementation includes `dm_services.h`, `dcn301_hubbub.h`, and `reg_helper.h`, and it depends on inherited helpers from DCN1, DCN2, DCN2.1, and DCN3. It integrates with the resource pool constructor for the DCN3.01 ASIC path and with hardware sequencing through `struct hubbub_funcs`.

## Risks And Edge Cases

- The function table deliberately mixes generations; a helper that assumes different register availability would fail only at runtime unless covered by build-time register tables.
- `hubbub21_init_dchub` is selected rather than the DCN3 sys-context init helper, so DCN3.01 VM/HVM behavior depends on the header-supplied register list and inherited DCN2.1 expectations.
- `detile_buf_size` is hard-coded to 184 KiB, so DCC capability decisions rely on that value matching hardware.
- The duplicated `REG`, `CTX`, and `FN` macro definitions are harmless but increase maintenance noise.

## Test Signals

Compile tests catch missing callback symbols and struct layout drift. Runtime validation should confirm DCN3.01 display init, VM context programming, DCC capability decisions for tiled and linear surfaces, watermark programming, p-state verification through debug index `0xB`, and register reads through `hubbub2_read_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn301/dcn301_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn301/dcn301_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn301/dcn301_hubbub.h

## Purpose

`dcn301_hubbub.h` declares the DCN3.01 Hubbub register and field list. It extends the DCN3.0 list with HVM/DCHVM registers and exposes the `hubbub301_construct` constructor used by DCN3.01 resource construction.

## Important APIs, Types, And Functions

- `HUBBUB_REG_LIST_DCN301(id)` expands `HUBBUB_REG_LIST_DCN30(id)` and appends `HUBBUB_HVM_REG_LIST()`.
- `HUBBUB_MASK_SH_LIST_DCN301(mask_sh)` expands the DCN3.0 mask/shift list and adds HVM fields: `HOSTVM_INIT_REQ`, GPUVM return power request/force/status bits, HVM clock gate disable bits, transaction request/response clock-request modes, RIOMMU prefetch/power status, RIOMMU active, and host VM prefetch done.
- `hubbub301_construct(...)` is the generation constructor prototype.

## Control Flow

The header has no executable control flow. Its macros are expanded during register-table construction. The constructor declared here is called by ASIC resource setup, after which all operational flow uses the function table installed by `dcn301_hubbub.c`.

## State And Persistence Behavior

The header owns no state. Its field coverage enables later code to mutate DCHVM/HVM hardware state, especially host VM initialization, RIOMMU prefetch, GPUVM retention power behavior, and HVM clock gating. Those effects are hardware-register side effects, not persisted file state.

## Dependencies And Integration Points

It includes `dcn30/dcn30_hubbub.h`, inheriting the DCN3.0 register model. It integrates with register generation for DCN3.01 ASICs and with any inherited helper that needs HVM fields, such as DCHVM initialization or VM-related power management.

## Risks And Edge Cases

- HVM fields must exist in the ASIC register headers; otherwise macro expansion breaks the build.
- The constructor implementation chooses inherited DCN2.1/DCN3 callbacks, so this header must expose the exact extra HVM fields those callbacks expect.
- If a platform lacks HVM support but uses this register list, runtime code must avoid calling HVM-specific helpers or handle inactive RIOMMU status safely.

## Test Signals

Build coverage validates macro expansion. Runtime tests should check DCN3.01 VM aperture setup, host VM init requests, RIOMMU active/prefetch status transitions, and power/clock gating interactions when display init enables DCHVM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn301/dcn301_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.c

## Purpose

`dcn31_hubbub.c` implements DCN3.1 Hubbub behavior. It programs configurable return buffer resources, watermarks, DCC capability limits, VM aperture/VMID setup, DCHUB reference clock reporting, p-state allow verification, and basic Hubbub initialization. It installs these operations through a DCN3.1 `struct hubbub_funcs`.

## Important APIs, Types, And Functions

- CRB/DET helpers: `dcn31_init_crb`, `dcn31_program_det_size`, `dcn31_wait_for_det_apply`, and `dcn31_program_compbuf_size`.
- Watermark helpers: `convert_and_clamp`, `hubbub31_program_urgent_watermarks`, `hubbub31_program_stutter_watermarks`, `hubbub31_program_pstate_watermarks`, and `hubbub31_program_watermarks`.
- DCC helpers: `hubbub3_get_blk256_size`, `hubbub31_det_request_size`, and `hubbub31_get_dcc_compression_cap`.
- VM and clock helpers: `hubbub31_init_dchub_sys_ctx`, `hubbub31_get_dchub_ref_freq`, and `hubbub31_verify_allow_pstate_change_high`.
- Public lifecycle: `hubbub31_init` and `hubbub31_construct`.
- `hubbub31_funcs`: function table selecting the DCN3.1 implementations and inherited DCN1/DCN2/DCN3 helpers.

## Control Flow

`hubbub31_construct` first calls `hubbub3_construct`, then replaces the function table with `hubbub31_funcs`, stores byte-sized DET/pixel chunk values, computes CRB segment capacity using 64 KiB segments, and sets p-state debug index `0x6`.

CRB initialization reads current DET0-DET3 and compbuf segment counts from hardware, programs reserved compbuf space from `pixel_chunk_size`, and sets debug DET depth. DET programming rounds requested KiB up to 64 KiB segments, writes the per-HUBP DET register, updates cached segment counts, and asserts that all DET plus compbuf segments fit within `crb_size_segs`. Compbuf growth waits for all current DET sizes to apply before increasing the compbuf register.

Watermark programming follows a safe-to-lower policy. Each set A-D is updated immediately when `safe_to_lower` is true or the new value is higher than the cached value; lower unsafe values leave hardware unchanged and return `wm_pending = true`. Urgent programming handles urgency, fractional urgent flip/nominal bandwidth, and refcycles per trip. Stutter programming handles normal and Z8 self-refresh enter/exit watermarks. P-state programming handles DRAM clock change watermarks. `hubbub31_program_watermarks` composes those helpers and toggles self-refresh according to `disable_stutter`.

DCC capability calculation validates global DCC debug policy, pixel format support, swizzle support, and detile-buffer request sizing. It picks a DCC control mode based on scan direction, segment order, 128B request need, and a 64KB_R_X exception, then fills the RGB DCC capability fields.

VM setup writes framebuffer and AGP aperture registers, initializes VMID 0 and VMID 15 from GART config when present, invokes optional DCHVM init, and returns `NUM_VMID` as 16. P-state verification polls a debug bit for up to 100 us; on timeout it forces allow-pstate-change high to avoid a hang and logs the debug data.

## State And Persistence Behavior

The file maintains cached hardware state in `struct dcn20_hubbub`: DET segment sizes, compbuf segment size, watermark values, `detile_buf_size`, `pixel_chunk_size`, `crb_size_segs`, and `debug_test_index_pstate`. It writes VM aperture, watermark, DET, compbuf, clock, SDPIF, DCHVM, and p-state force registers. Static locals in `hubbub31_verify_allow_pstate_change_high` retain the last forced-pstate workaround and max sampled wait across calls.

## Dependencies And Integration Points

It depends on DCN3/DCN3.1 headers, `dm_services.h`, `reg_helper.h`, `struct hubbub`, `struct dcn20_hubbub`, `union dcn_watermark_set`, DCC surface types, VMID setup from DCN2, and inherited DCN1/DCN2/DCN3 helpers. It integrates with DML bandwidth output, DC resource construction, plane validation/DCC capability checks, HWSS watermark propagation, DCHVM initialization, and display init sequencing.

## Risks And Edge Cases

- The p-state watermark state B lower path sets `wm_pending = false` rather than true, unlike the other states, which can hide a pending unsafe lower.
- `convert_and_clamp` asserts on watermark overflow and clamps; bad DML inputs may mask underflow risk after the assert.
- DET and compbuf sizing depends on cached segment counts matching hardware current registers.
- Unsupported `bytes_per_element` in block-size calculation leaves zero dimensions and can corrupt DCC request decisions if upstream pixel-format filtering fails.
- P-state verification forces a hardware override on timeout; that is a hang-avoidance workaround with power-management side effects.
- DCC capability only fills RGB capability fields and assumes the input is not a dual-plane DCN4-style case.

## Test Signals

Build tests catch register field and callback mismatches. Runtime signals include successful init with 16 VMIDs, CRB config assertions or warnings, DCC capability results across swizzles/formats/scan directions, bandwidth logs for A-D watermarks, p-state warning logs, self-refresh state changes, and no stalls in DET apply waits or p-state polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.h

## Purpose

`dcn31_hubbub.h` defines the DCN3.1 Hubbub register and field map and declares the DCN3.1 constructor and initialization helpers. It builds on DCN3.0/DCN2.1 and adds HVM, DET, compbuf, SDPIF, clock, memory-power, and Z8 self-refresh watermark fields.

## Important APIs, Types, And Functions

- `HUBBUB_REG_LIST_DCN31(id)` appends DCHVM registers, DET0-DET3 controls, compbuf controls, reserved compbuf space, debug, clock, SDPIF, memory power, and Z8 watermark registers.
- `HUBBUB_MASK_SH_LIST_DCN31(mask_sh)` binds VM aperture fields, HVM/RIOMMU fields, urgent bandwidth fields, DET/compbuf fields, Z8 watermark fields, VM fault fields, clock gate fields, SDPIF control, and DET memory power low-speed mode.
- Prototypes: `hubbub31_init_dchub_sys_ctx`, `hubbub31_init`, and `hubbub31_construct`.

## Control Flow

The header contributes register metadata only. Runtime flow is implemented in `dcn31_hubbub.c`, where the constructor installs `hubbub31_funcs`; the declared init and sys-context functions are invoked by display init and VM setup paths.

## State And Persistence Behavior

No state is stored in the header. Its macros enable DCN3.1 code to cache and program DET, compbuf, watermark, HVM, VM fault, SDPIF, clock, and memory-power register state through `struct dcn20_hubbub`.

## Dependencies And Integration Points

The file includes `dcn21/dcn21_hubbub.h` and relies on DCN common Hubbub macro families. It integrates with generated ASIC register tables, DCN3.1 resource construction, DCHVM setup, DCC capability decisions, watermark programming, and debug register-state reads.

## Risks And Edge Cases

- Register-list duplication or omission affects every `REG_*` call in the C file.
- The header exposes only DET0-DET3 fields, so code is tied to four tracked DET instances.
- Z8 watermark fields must align with the `union dcn_watermark_set` layout used by DCN3.1 programming.
- HVM fields are present even when RIOMMU init may not become active; callers must handle inactive status.

## Test Signals

Compilation validates field names and prototypes. Runtime checks include DET/compbuf programming, HVM init, Z8 watermark writes, SDPIF ownership programming, clock-gate debug paths, and VM fault status read/clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn32/dcn32_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn32/dcn32_hubbub.c

## Purpose

`dcn32_hubbub.c` implements DCN3.2 Hubbub programming. It extends DCN3.1-style CRB and watermark handling with SDPIF request-rate controls, UCLK/FCLK split p-state watermarks, USR retraining watermarks and force control, MALL status reporting, and DCN3.2-specific init behavior.

## Important APIs, Types, And Functions

- CRB and request controls: `dcn32_init_crb`, `hubbub32_set_sdp_control`, `hubbub32_set_request_limit`, `dcn32_program_det_size`, and `dcn32_program_compbuf_size`.
- Watermarks: `hubbub32_program_urgent_watermarks`, `hubbub32_program_stutter_watermarks`, `hubbub32_program_pstate_watermarks`, `hubbub32_program_usr_watermarks`, `hubbub32_program_watermarks`, `hubbub32_init_watermarks`, and `hubbub32_wm_read_state`.
- Runtime controls: `hubbub32_force_usr_retraining_allow`, `hubbub32_force_wm_propagate_to_pipes`, `hubbub32_get_mall_en`, and `hubbub32_init`.
- Lifecycle: `hubbub32_construct` and `hubbub32_funcs`.

## Control Flow

Construction directly initializes the Hubbub object, installs `hubbub32_funcs`, records register tables, sets p-state debug index `0xB`, stores detile and pixel-chunk sizes, and computes CRB segment capacity with 64 KiB segments.

CRB init reads current DET/compbuf segment state, programs compbuf reserved space, and uses a larger debug DET depth than DCN3.1. DET programming rounds KiB to segments and writes per-HUBP DET registers; if the sum exceeds CRB capacity, it logs a warning instead of immediately asserting because seamless ODM transitions can temporarily overcommit. Compbuf growth waits for DET current registers and asserts capacity before programming.

Watermark flow is split into urgent, stutter, p-state, and USR phases. Urgent programming is similar to DCN3.1. Stutter watermarks program normal SR enter/exit for sets A-D with 16-bit clamp values. P-state programming writes UCLK and FCLK watermark registers separately. USR programming writes retraining watermarks for sets A-D. The top-level `hubbub32_program_watermarks` optionally disables stutter and hands SDPIF control to DF before unsafe watermark raises on selected GC 11.0.0/11.0.3 revisions, restores self-refresh and SDPIF ownership after safe lowering, and enforces the debug `force_usr_allow` value.

Initialization sets optional clock-gate disables, gives SDPIF control to DC, sets max outstanding SDPIF requests to 512, and programs min/max DF outstanding requests to 512. MALL status reads `MALL_IN_USE` and `MALL_PREFETCH_COMPLETE` and reports true only when both are set.

## State And Persistence Behavior

The file caches DET, compbuf, watermark, request-limit, detile, pixel-chunk, and CRB segment state in `struct dcn20_hubbub`. It mutates hardware registers for watermarks, SDPIF control and outstanding requests, DCHUBBUB request limits, USR force, MALL status reads, clock gates, and self-refresh control. There is no file persistence.

## Dependencies And Integration Points

It depends on DCN30/DCN32 headers, `dm_services.h`, `reg_helper.h`, ASIC revision helpers from `dal_asic_id.h`, inherited Hubbub helpers, DML-generated `union dcn_watermark_set`, and DC debug flags. It integrates with display init, bandwidth/watermark programming, MALL/SubVP checks, power management, and resource construction for DCN3.2 ASICs.

## Risks And Edge Cases

- `hubbub32_set_request_limit` comments say the field is 24 bits, but the code clamps/asserts against `0xFFF`; hardware field width should be verified.
- Request-limit inputs that compute zero skip programming after an assertion, leaving old hardware state.
- Watermark lowering while `safe_to_lower` is false depends on `wm_pending` being honored by callers.
- SDPIF handoff for `disable_stutter_for_wm_program` is ASIC-revision gated; new revisions needing the workaround must be added explicitly.
- Init comments note zero frame buffer mode must restore outstanding limits, but this file only programs the normal mode values.
- DET overcommit is only warned in `dcn32_program_det_size`; compbuf programming still asserts on over-capacity.

## Test Signals

Useful tests include kernel builds, register-table coverage, CRB programming during ODM changes, watermark raise/lower sequencing, USR force toggling, GC 11.0.0/11.0.3 stutter-disable handoff, MALL prefetch/in-use status reads, zero frame buffer mode transitions, and bandwidth log validation for urgent, stutter, UCLK, FCLK, and USR sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn32/dcn32_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn32/dcn32_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn32/dcn32_hubbub.h

## Purpose

`dcn32_hubbub.h` declares the DCN3.2 Hubbub field map and exported helper prototypes. It expands DCN3-era Hubbub coverage with global timer enable, soft reset, watermark-change control, request limiting, USR retraining, UCLK/FCLK p-state watermarks, SDPIF controls, MALL status fields, and CRB/DET/compbuf fields.

## Important APIs, Types, And Functions

- `HUBBUB_MASK_SH_LIST_DCN32(mask_sh)` lists all field masks and shifts needed by DCN3.2 Hubbub C code, including self-refresh/p-state force, request outstanding limits, urgent watermarks, VM aperture, DET/compbuf, USR retraining, UCLK/FCLK p-state, VM fault status, SDPIF rate/max outstanding, memory power, and MALL status.
- Exported functions include `hubbub32_program_urgent_watermarks`, `hubbub32_program_stutter_watermarks`, `hubbub32_program_pstate_watermarks`, `hubbub32_program_usr_watermarks`, `hubbub32_force_usr_retraining_allow`, `hubbub32_force_wm_propagate_to_pipes`, `hubbub32_init`, `dcn32_program_det_size`, `dcn32_program_compbuf_size`, `hubbub32_set_request_limit`, `hubbub32_get_mall_en`, and `hubbub32_construct`.

## Control Flow

The header has no runtime control flow. It enables generation-specific C files to build a `hubbub_funcs` table and exposes helpers reused by later DCN35/DCN42 implementations.

## State And Persistence Behavior

No state is persisted here. The declared helpers update cached `struct dcn20_hubbub` watermarks and CRB segment fields and write DCHUBBUB registers at runtime.

## Dependencies And Integration Points

It includes `dcn21/dcn21_hubbub.h`. It is consumed by DCN3.2 resource construction and later-generation files that reuse DCN3.2 watermark, DET, request-limit, MALL, and USR helpers.

## Risks And Edge Cases

- This header declares only a mask/shift list, so the matching register list must come from ASIC-specific resource files or inherited macros; mismatches break `REG_*` access.
- Later generations reuse prototypes from this header but may have different register semantics.
- MALL and USR fields are optional by hardware generation; function-table selection must match field availability.

## Test Signals

Compile-time macro expansion is the first signal. Runtime tests should exercise USR retraining, UCLK/FCLK watermarks, MALL status reads, SDPIF rate-limit programming, DET/compbuf programming, VM faults, and self-refresh/p-state force controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn32/dcn32_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn35/dcn35_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn35/dcn35_hubbub.c

## Purpose

`dcn35_hubbub.c` implements DCN3.5 Hubbub behavior by reusing much of DCN3.2 and adding DCN3.5-specific CRB depth, Z8 stutter watermarks, reference-clock bring-up handling, QoS/DF threshold programming, fine-grain clock gating control, and DCHVM/RIOMMU initialization.

## Important APIs, Types, And Functions

- CRB helpers: `dcn35_init_crb` and `dcn35_program_compbuf_size`.
- Watermark helpers: `hubbub35_program_stutter_z8_watermarks`, `hubbub35_program_watermarks`, `hubbub35_init_watermarks`, and `hubbub35_wm_read_state`.
- Clock/init helpers: `hubbub35_get_dchub_ref_freq`, `hubbub35_set_fgcg`, `hubbub35_init`, and `dcn35_dchvm_init`.
- Lifecycle: `hubbub35_construct` and `hubbub35_funcs`.

## Control Flow

Construction assigns the DCN3.5 function table, stores register table pointers, sets debug p-state index `0xB`, and computes detile, pixel-chunk, and CRB segment sizes with 64 KiB segments.

CRB initialization reads DET0-DET3 and compbuf current sizes, programs reserved compbuf space for 64B and ZS chunks, and sets DET depth to `0x5FF`. Compbuf programming follows the DCN3.x pattern: only grow when safe, wait for DET current values before growth, assert total CRB capacity, update the compbuf register, cache the segment count, and check `CONFIG_ERROR`.

Watermark programming calls DCN3.2 urgent, stutter, p-state, and USR helpers, then programs DCN3.5 Z8 stutter enter/exit watermarks for sets A-D. It writes saturation and DF outstanding thresholds, sets host VM QoS commit threshold, optionally restores self-refresh, and applies the debug USR force. Watermark initialization and readback copy/read all normal, UCLK/FCLK, USR, and Z8 sets.

`hubbub35_get_dchub_ref_freq` reads global timer refdiv/enable and returns 24 MHz or 12 MHz; if disabled, it programs refdiv/enable as a bring-up workaround and asserts critical. `hubbub35_init` applies debug clock-gate disables, sets fine-grain clock gating from debug flags, gives SDPIF control to DC, sets max outstanding to 256, programs DF outstanding limits, and clears cached p-state watermark state for set A. `dcn35_dchvm_init` requests HOSTVM init, polls RIOMMU active, disables memory/clock gating while prefetching, requests RIOMMU prefetch, waits for completion, restores gating, and marks `hubbub->riommu_active`.

## State And Persistence Behavior

State is cached in `struct dcn20_hubbub` and `struct hubbub`: DET/compbuf segment sizes, watermark caches, detile/pixel/CRB sizes, debug p-state index, and `riommu_active`. Hardware side effects include DCHUBBUB watermarks, DF/QoS thresholds, SDPIF controls, clock gates, compbuf/DET registers, global timer enable/refdiv, DCHVM/RIOMMU registers, and self-refresh/USR force controls.

## Dependencies And Integration Points

The file includes DCN30, DCN31, DCN32, and DCN35 headers plus register helpers. It integrates with DCN3.5 resource construction, DML bandwidth programming, DCHVM host-VM startup, power management, fine-grain clock gating debug policy, and inherited DCC/VM/watermark support.

## Risks And Edge Cases

- `hubbub35_program_stutter_z8_watermarks` ignores `safe_to_lower` for set A enter, unlike most other watermark fields.
- Reference-clock disabled handling both mutates hardware and asserts critical; this is useful for bring-up but noisy if a platform intentionally starts disabled.
- DCHVM init silently leaves `riommu_active` false after 100 polling attempts; callers must tolerate inactive host VM acceleration.
- The commented-out request-limit implementation means DCN3.5 does not expose a request-limit callback in the function table.
- `hubbub35_init` clears only set A `cstate_pstate` cached state, which could interact with later safe-to-lower comparisons.

## Test Signals

Signals include successful DCHVM init with `riommu_active`, HOSTVM prefetch completion, watermark readback including Z8 fields, DF/QoS threshold register values, fine-grain clock-gating toggles, global timer enable/refdiv state, compbuf config-error assertions, and display power-management tests covering stutter, Z8, UCLK/FCLK, and USR behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn35/dcn35_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn35/dcn35_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn35/dcn35_hubbub.h

## Purpose

`dcn35_hubbub.h` defines the DCN3.5 Hubbub register and mask/shift list and declares DCN3.5 helper functions. It extends DCN3.2 with DCHVM/RIOMMU fields, Z8 self-refresh watermarks, host VM QoS thresholds, fine-grain clock gating, and DCN3.5 init/readback helpers.

## Important APIs, Types, And Functions

- `HUBBUB_REG_LIST_DCN35(id)` enumerates DCHUBBUB watermarks, VM aperture/fault registers, DET/compbuf, USR/UCLK/FCLK registers, SDPIF/clock/memory power, DCHVM/HVM registers, Z8 watermarks, and QoS force.
- `HUBBUB_MASK_SH_LIST_DCN35(mask_sh)` inherits DCN3.2 fields and adds HVM, compbuf, fine-grain clock gating, Z8 watermarks, legacy cstate/deepsleep, host VM QoS commit threshold, and DF min outstanding commit threshold fields.
- Declared functions include `hubbub35_construct`, `hubbub35_wm_read_state`, `hubbub35_get_dchub_ref_freq`, `hubbub35_program_watermarks`, `hubbub35_init_watermarks`, `dcn35_program_compbuf_size`, `dcn35_init_crb`, `hubbub35_init`, and `dcn35_dchvm_init`.

## Control Flow

The header supplies register metadata and prototypes only. Runtime flow is in `dcn35_hubbub.c`, where `hubbub35_construct` installs a DCN3.5 function table and the declared helpers are invoked during init, bandwidth programming, readback, and DCHVM setup.

## State And Persistence Behavior

The header owns no state. Its fields enable runtime mutation of watermark caches, DET/compbuf caches, global timer state, DCHVM state, QoS thresholds, and clock gating through the C implementation.

## Dependencies And Integration Points

It includes `dcn32/dcn32_hubbub.h`, inheriting DCN3.2 field coverage and helper prototypes. It integrates with ASIC register-table generation, DCN3.5 resource construction, DML watermark paths, DCHVM host-VM init, and debug clock-gating policy.

## Risks And Edge Cases

- `HUBBUB_REG_LIST_DCN35` contains repeated compbuf/debug/clock register entries, which may be accepted by table-generation macros but is a maintenance hazard.
- The header exposes HVM fields and DCHVM init prototype even though RIOMMU activity is runtime-dependent.
- Z8 fields must remain consistent with `hubbub35_wm_read_state` and `hubbub35_program_stutter_z8_watermarks`.

## Test Signals

Build tests validate macro expansion and function prototypes. Runtime tests should verify Z8 watermark write/read, DCHVM init, QoS threshold programming, fine-grain clock gating, compbuf config-error checks, and inherited DCN3.2 watermark/DCC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn35/dcn35_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401/dcn401_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401/dcn401_hubbub.c

## Purpose

`dcn401_hubbub.c` implements DCN4.01 Hubbub support. It introduces DCN4-style A/B watermark programming, dual-plane address-v3 DCC capability calculation, segment-based DET/compbuf APIs, long DET update waits, and a DML2 arbiter hook for timeout and SDPIF rate-limit behavior.

## Important APIs, Types, And Functions

- CRB and segment helpers: `dcn401_init_crb`, `dcn401_program_det_segments`, `dcn401_program_compbuf_segments`, and `dcn401_wait_for_det_update`.
- Watermarks: `hubbub401_program_urgent_watermarks`, `hubbub401_program_stutter_watermarks`, `hubbub401_program_pstate_watermarks`, `hubbub401_program_usr_watermarks`, `hubbub401_program_watermarks`, `hubbub401_init_watermarks`, and `hubbub401_wm_read_state`.
- DCC capability: `hubbub401_dcc_support_swizzle`, `hubbub401_dcc_support_pixel_format`, `hubbub401_get_blk256_size`, `hubbub401_det_request_size`, and `hubbub401_get_dcc_compression_cap`.
- Arbiter: `dcn401_program_arbiter`.
- Lifecycle: `hubbub401_construct` and `hubbub4_01_funcs`.

## Control Flow

Construction installs `hubbub4_01_funcs`, stores context and register tables, and computes detile/pixel/CRB segment fields. CRB init reads DET0-DET3 and compbuf current segment counts and programs 64B reserved compbuf space.

Watermark programming uses `watermarks->dcn4x` rather than the older DCN3 fields. DCN4.01 programs only sets A and B for urgent, stutter, p-state, and USR values. Urgent watermarks include fractional MALL bandwidth and separate refcycles per metadata trip. Stutter programming mirrors A/B SR enter/exit values into three additional watermark tiers because dGPU Z states are not applicable. P-state programming includes UCLK/FCLK and TEMP_READ/PPT secondary watermark registers. The top-level function composes the phases, restores self-refresh based on debug `disable_stutter`, and applies USR force.

DCC flow first checks global disable and optional plane-width limits, clamps dimensions by format family, determines plane0/plane1 bytes per element, validates address-v3 swizzle/pitch support, computes whether 128B requests are needed for each plane and scan direction, then enables the most permissive valid DCC controls. Dual-plane formats evaluate luma and chroma separately and include P010 3:2 packing adjustment.

Segment programming writes DET size segments directly per HUBP and warns if DET plus compbuf segments exceed CRB capacity. Compbuf segment programming only grows when safe, waits for DET current values before growth, asserts capacity, and updates the cached segment count. DET update waiting can wait up to 100000 iterations, described as one vupdate at 10 Hz. `dcn401_program_arbiter` programs p-state stall threshold and bit 5 of `DCHUBBUB_HW_DEBUG` according to `allow_sdpif_rate_limit_when_cstate_req`, deferring unsafe lowers with `wm_pending`.

## State And Persistence Behavior

Cached state lives in `struct dcn20_hubbub`: watermark `dcn4x` fields, DET/compbuf segment sizes, detile/pixel/CRB values, and `allow_sdpif_rate_limit_when_cstate_req`. Hardware side effects include DCHUBBUB watermark, MALL bandwidth, metadata-trip, SR tier, p-state, USR, DET, compbuf, timeout, HW debug, SDPIF request-limit, self-refresh, and VM registers.

## Dependencies And Integration Points

The file depends on DCN30 and DCN401 headers, register helpers, DML2 arbiter register structs, DC DCC surface parameters, DC debug flags, inherited DCN2/DCN3 helpers, and DCN4 watermark union layout. It integrates with DCN4.01 resource construction, DML2 bandwidth/arbiter programming, plane validation for DCC, display init, and HWSS power/watermark sequencing.

## Risks And Edge Cases

- DCN4.01 supports only A/B watermark sets in this implementation; callers must not expect C/D fields to be programmed.
- DCC linear swizzle support requires `plane_pitch * bpe` to be 256-byte aligned.
- `hubbub401_det_request_size` assumes valid nonzero BPE values; unsupported formats must be filtered first.
- `DCC_HALF_REQ_DISALBE` is enforced only in the single-plane path, not the dual-plane path.
- `dcn401_program_arbiter` treats any lower `allow_sdpif_rate_limit_when_cstate_req` as pending when unsafe, even though it is a boolean-like field.
- Long DET waits can stall modeset/update paths on hardware that never applies the new current size.

## Test Signals

Test signals include DCN4.01 kernel builds, DML2 watermark/arbiter programming, DCC validation for single-plane, YUV420, P010, RGBE alpha, linear and 2D swizzles, plane-width-limit behavior, DET/compbuf segment warnings, DET apply wait completion, and readback of A/B watermarks plus SR tier registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401/dcn401_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401/dcn401_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401/dcn401_hubbub.h

## Purpose

`dcn401_hubbub.h` declares the DCN4.01 Hubbub constants, field map, DCC helper APIs, segment programming APIs, arbiter API, and constructor. It shifts the interface toward DCN4 watermarks, address-v3 DCC, DML2 arbiter integration, and segment-based CRB programming.

## Important APIs, Types, And Functions

- Constants: `DCN4_01_CRB_SIZE_KB`, `DCN4_01_DEFAULT_DET_SIZE`, and `DCN4_01_CRB_SEGMENT_SIZE_KB`.
- `HUBBUB_MASK_SH_LIST_DCN4_01(mask_sh)` covers global timer, soft reset, self-refresh/p-state force, urgent A/B, SR A/B plus SR tiers 1-3, VM aperture, urgent flip/nom/MALL, refcycles to memory/meta, DET/compbuf, USR, UCLK/FCLK secondary watermarks, VM fault, SDPIF, memory power, timeout detection, ROB status, debug, and cstate swath check fields.
- Declared DCN4.01 APIs include watermark programming, address-v3 DCC support functions, two-plane DCC capability, `dcn401_program_arbiter`, `hubbub401_construct`, DET/compbuf segment programming, DET update waiting, and CRB init.

## Control Flow

The header has no executable control flow. Its field list enables `dcn401_hubbub.c` to build a function table and drive DCN4.01 register programming from DML2 and display init paths.

## State And Persistence Behavior

No state is stored in the header. The declared functions mutate cached Hubbub state and DCHUBBUB registers for DCN4.01 watermarks, DCC capability outputs, timeout/debug controls, DET/compbuf segment state, and VM behavior.

## Dependencies And Integration Points

It includes `dcn32/dcn32_hubbub.h` for inherited base types and helpers, and it introduces APIs used by DCN4.01 resource construction, DML2 display arbiter code, DCC plane validation, and HWSS resource programming.

## Risks And Edge Cases

- Header and implementation must agree on A/B-only DCN4.01 watermark coverage; C/D fields are not exposed here.
- Timeout and ROB status fields are hardware-debug-sensitive; accidental writes through a reused helper could affect diagnostics.
- Address-v3 DCC APIs have different swizzle enum and pixel-format signatures from older DCC helpers, so function-table selection must be correct.
- Segment units are not KiB in the public DET/compbuf segment functions; callers must convert before calling.

## Test Signals

Build coverage should validate every field macro. Runtime signals include DML2 arbiter writes, timeout threshold programming, ROB status handling, DCC capability for address-v3 swizzles, DET/compbuf segment apply, A/B watermark readback, and VM fault reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401/dcn401_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.c

## Purpose

`dcn42_hubbub.c` implements DCN4.2 Hubbub support. It reuses many DCN3.5 and DCN4.01 helpers but restores A-D watermark programming, adds DCN4.2-specific self-refresh semantics, fixed SDPIF request-limit programming, and an arbiter variant where p-state stall threshold is left to firmware.

## Important APIs, Types, And Functions

- Watermark helpers: `hubbub42_program_urgent_watermarks`, `hubbub42_program_stutter_watermarks`, `hubbub42_program_pstate_watermarks`, `hubbub42_program_usr_watermarks`, `hubbub42_program_stutter_z8_watermarks`, and `hubbub42_program_watermarks`.
- Runtime controls: `hubbub42_allow_self_refresh_control`, `hubbub42_set_sdp_control`, `hubbub42_set_request_limit`, and `dcn42_program_arbiter`.
- Lifecycle: `hubbub42_construct` and `hubbub42_funcs`.

## Control Flow

Construction initializes the Hubbub object, installs `hubbub42_funcs`, stores register tables, and computes detile, pixel-chunk, and CRB segment counts with 64 KiB segments.

Top-level watermark programming optionally hands SDPIF control to DF and disables self-refresh before unsafe watermark raises when `disable_stutter_for_wm_program` is set. It then programs urgent, stutter, UCLK/FCLK p-state, USR, and Z8 stutter watermarks for sets A-D using `watermarks->dcn4x`. It writes saturation and DF/QoS thresholds, restores self-refresh when safe or forced by debug settings, restores SDPIF control after safe lowering, and applies USR force.

`hubbub42_allow_self_refresh_control` differs from the inherited helper by forcing value 0 and enabling the force bit only when self-refresh should be disallowed. `hubbub42_set_request_limit` ignores memory-channel inputs and programs a fixed `SDPIF_REQUEST_RATE_LIMIT` value of 96. `dcn42_program_arbiter` mirrors DCN4.01 bit-5 debug handling for `allow_sdpif_rate_limit_when_cstate_req` but intentionally does not program the p-state stall threshold because firmware handles it.

The function table reuses DCN31 VM sys-context init, older DCC support (`hubbub3_get_dcc_compression_cap`), DCN35 watermark read/init/refclock and DCHVM init, and DCN401 segment CRB helpers.

## State And Persistence Behavior

The file updates cached DCN4x watermark fields for sets A-D, `allow_sdpif_rate_limit_when_cstate_req`, detile/pixel/CRB sizes, and inherited DET/compbuf caches. It writes DCHUBBUB watermark, p-state, USR, Z8, self-refresh force, SDPIF control/rate-limit, DF outstanding, QoS, debug, DET/compbuf, DCHVM, and VM registers through reused helpers.

## Dependencies And Integration Points

It depends on DCN30, DCN31, DCN32, DCN35, DCN401, and DCN42 headers, plus register helpers. It integrates with DCN4.2 resource construction, DML/DML2 watermark and arbiter programming, power management, DCHVM init, older DCC validation paths, and DC debug stutter/USR controls.

## Risks And Edge Cases

- The fixed SDPIF request limit of 96 ignores topology and memory-channel parameters; platforms with different fabric characteristics need validation.
- The function table uses older DCC helpers rather than DCN401 address-v3 two-plane DCC helpers; this must match DCN4.2 hardware/register expectations.
- `dcn42_program_arbiter` does not program p-state stall threshold, so firmware availability becomes part of correctness.
- The top-level watermark path marks pending before unsafe raises when stutter-for-WM is disabled, even if all later writes succeed; callers must interpret this consistently.
- Self-refresh force semantics differ from inherited helpers and should be tested with debug `disable_stutter` and normal stutter transitions.

## Test Signals

Runtime tests should cover A-D urgent/stutter/UCLK/FCLK/USR/Z8 watermarks, stutter disable during unsafe raises, SDPIF control restoration after safe lowering, fixed request-limit register value, firmware-owned p-state stall behavior, DCHVM init, DCN401 segment DET/compbuf helpers, and inherited DCC capability behavior on DCN4.2 surfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.h

## Purpose

`dcn42_hubbub.h` declares the DCN4.2 Hubbub constants, register list, field list, and constructor. It exposes a larger 1792 KiB CRB configuration, A-D DCN4x watermark registers, DCHVM fields, Z8 watermarks, timeout/status fields, and DCN4.2-specific control bits.

## Important APIs, Types, And Functions

- Constants: `DCN42_CRB_SIZE_KB`, `DCN42_DEFAULT_DET_SIZE`, and `DCN42_CRB_SEGMENT_SIZE_KB`.
- `HUBBUB_REG_LIST_DCN42(id)` enumerates A-D urgent/stutter/frac/refcycle/p-state/USR/Z8 watermarks, VM aperture/fault registers, DET/compbuf, SDPIF, clock, memory power, DCHVM, host VM QoS, and QoS force registers.
- `HUBBUB_MASK_SH_LIST_DCN4_2(mask_sh)` inherits DCN3.2 fields and adds HVM, compbuf, FGCg, A-D watermark fields, deep-sleep force, QoS thresholds, VM fault, timeout detection, ROB overflow, urgent zero-size request enable, and cstate swath check fields.
- `hubbub42_construct(...)` initializes the runtime object.

## Control Flow

No executable control flow exists in the header. Its macros are expanded into register/mask/shift tables for the C implementation, and the constructor is called by DCN4.2 resource construction.

## State And Persistence Behavior

The header owns no state. Its field coverage permits `dcn42_hubbub.c` and reused helpers to mutate A-D watermark caches, self-refresh/deep-sleep force registers, DCHVM state, DET/compbuf segment state, timeout/debug fields, and VM fault state.

## Dependencies And Integration Points

It includes `dcn32/dcn32_hubbub.h` and is consumed by DCN4.2 ASIC resource code. It bridges older DCN3.2-style helper declarations with newer DCN4.2 register coverage and reused DCN35/DCN401 functions.

## Risks And Edge Cases

- The mask list contains repeated groups inherited from DCN3.2 and explicitly redeclared A-D fields; register-table generation must tolerate this and keep the intended field mapping.
- DCN42 exposes both DCFCLK deep-sleep force and self-refresh force fields; power-management tests must distinguish them.
- Timeout/status fields include diagnostic clear/status bits, so accidental writes can hide hardware faults.
- Constructor only declared here; all behavior depends on function-table choices in `dcn42_hubbub.c`.

## Test Signals

Builds validate macro fields and constructor linkage. Runtime checks should verify A-D watermark programming/readback, DCHVM init, deep-sleep and self-refresh force behavior, timeout/status register access, fixed CRB segment sizing, and SDPIF/debug field programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/Makefile

## Purpose

`dc/hubp/Makefile` contributes HUBP generation-specific object files to the AMD Display Core build when `CONFIG_DRM_AMD_DC_FP` is enabled. It lists the HUBP implementation object for each supported DCN generation and appends their source-tree paths to `AMD_DISPLAY_FILES`.

## Important APIs, Types, And Functions

- `ifdef CONFIG_DRM_AMD_DC_FP`: gates all HUBP object inclusion behind the floating-point AMD DC build option.
- Generation variables: `HUBP_DCN10`, `HUBP_DCN20`, `HUBP_DCN201`, `HUBP_DCN21`, `HUBP_DCN30`, `HUBP_DCN31`, `HUBP_DCN32`, `HUBP_DCN35`, `HUBP_DCN401`, and `HUBP_DCN42`.
- Path variables: `AMD_DAL_HUBP_DCN* = $(addprefix $(AMDDALPATH)/dc/hubp/<generation>/,$(HUBP_DCN*))`.
- Build integration: repeated `AMD_DISPLAY_FILES += $(AMD_DAL_HUBP_DCN*)`.

## Control Flow

Make evaluation is straightforward. If `CONFIG_DRM_AMD_DC_FP` is set, each generation declares a one-object list, prefixes it with the corresponding HUBP subdirectory under `$(AMDDALPATH)`, and appends that full object path to the global `AMD_DISPLAY_FILES` aggregate. If the config is unset, the file contributes no objects.

## State And Persistence Behavior

The Makefile mutates only build-system variables during make evaluation. It does not persist runtime state and has no direct hardware side effects. Its effects are reflected in which HUBP object files are compiled and linked into the AMD display driver.

## Dependencies And Integration Points

It depends on the parent AMD display make infrastructure defining `AMDDALPATH`, `AMD_DISPLAY_FILES`, and `CONFIG_DRM_AMD_DC_FP`. It integrates with generation-specific HUBP C files under `dc/hubp/dcn10`, `dcn20`, `dcn201`, `dcn21`, `dcn30`, `dcn31`, `dcn32`, `dcn35`, `dcn401`, and `dcn42`.

## Risks And Edge Cases

- Adding a new HUBP generation requires adding both the object variable and `AMD_DISPLAY_FILES` append; missing either silently omits the implementation from the build.
- The file assumes one object per generation. Multi-file generation implementations would need variable expansion changes.
- Paths depend on `AMDDALPATH` being correct in the parent Makefile.
- All entries are gated by `CONFIG_DRM_AMD_DC_FP`; configurations without it will not compile these HUBP implementations.

## Test Signals

Build logs and `make V=1` output should show the expected HUBP object paths in `AMD_DISPLAY_FILES`. Kernel builds for DCN10 through DCN42 ASIC support catch missing objects, stale paths, and linker errors for missing HUBP constructors or function tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/Makefile -->
