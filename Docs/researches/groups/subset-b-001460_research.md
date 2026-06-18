# Research: subset-b-001460

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c

## Purpose

`dcn42_resource.c` builds the AMD Display Core DCN 4.2 resource pool. It binds DCN42 register maps, capability tables, debug defaults, hardware block factories, bandwidth validation hooks, and DML2 setup into the generic `resource_pool` interface used by Display Core commits.

## Important APIs, Types, And Functions

- `dcn42_create_resource_pool(init_data, dc)`: exported allocator and constructor entry point.
- `dcn42_resource_construct(num_virtual_links, dc, pool)`: initializes caps, debug/config defaults, register tables, hardware objects, link/DDC/AUX resources, DML2 callbacks, and SPL/sharpness defaults.
- `dcn42_resource_destruct(pool)` and `dcn42_destroy_resource_pool(pool)`: release every object allocated into the pool.
- Object factories: `dcn42_hubbub_create`, `dcn42_hubp_create`, `dcn42_dpp_create`, `dcn42_mpc_create`, `dcn42_opp_create`, `dcn42_timing_generator_create`, `dcn42_link_encoder_create`, `dcn42_stream_encoder_create`, HPO DP encoder factories, DSC/DWB/MMHUBBUB/AUX/I2C/clock-source creators.
- Bandwidth and programming hooks: `dcn42_validate_bandwidth`, `dcn42_update_bw_bounding_box`, `dcn42_prepare_mcache_programming`, and `dcn42_build_pipe_pix_clk_params`.
- Static contracts: `res_cap_dcn42`, `plane_cap`, `debug_defaults_drv`, `config_defaults`, `dcn42_res_pool_funcs`, and `res_create_funcs`.

## Control Flow

Construction initializes BIOS and block register structures, reads pipe fuses from `CC_DC_PIPE_DIS`, reduces the usable pipe count for harvested pipes, asserts impossible pipe-0/full-DCN harvest cases, and installs `dcn42_res_pool_funcs`. It then fills `dc->caps`, color pipeline capabilities, debug defaults, SPL/sharpness ranges, panel/LTTPR options, and DML2 configuration.

Hardware allocation proceeds in a fixed order: clock sources and DP DTO source, DCCG, power-gate control, IRQ service, HUBBUB/VMIDs, per-pipe HUBP/DPP/OPP/TG/ABM, PSR and Replay DMUB objects, MPC, DSCs, DWB/MMHUBBUB, AUX/I2C engines, DPIA counts, and generic `resource_construct` for audio, HWSEQ, stream encoders, HPO encoders, virtual links, and LUT resources. Any allocation failure jumps to `create_fail`, calls the destructor, and returns false.

Bandwidth validation enters the floating-point section, calls `dml2_validate`, and, for validate-and-programming mode, calls `dcn42_decide_zstate_support`. MCACHE programming is prepared only when DML 2.1 is enabled and chooses DC-power-source DML state when appropriate.

## State And Persistence Behavior

There is no on-disk persistence. The file mutates in-memory `dc`, `dc->caps`, `dc->config`, `dc->debug`, `dc->dml2_options`, `dc->dcn_ip`, and every resource pointer under `pool->base`. Durable effects occur later through the block objects' register programming callbacks. Register-table globals are process/static data initialized from per-ASIC offset arrays.

## Dependencies And Integration Points

The file integrates many AMD DC block implementations: DCE/DCE110 clock, AUX, I2C, audio, HWSEQ; DCN20/30/31/32/35/401/42 HUBBUB, HUBP, DPP, MPC, OPP, OPTC, DSC, DCCG, PG control, DWB, MMHUBBUB, stream/link encoders, HPO encoders, ABM/PSR/Replay, link encoder assignment, VM helper, DML2, and SPL. It is the ASIC-specific provider behind generic resource and commit code.

## Risks And Edge Cases

- `dcn42_create_resource_pool` allocates `sizeof(struct dcn401_resource_pool)` for a `struct dcn42_resource_pool *`; this relies on compatible layout/size and is easy to break if the structs diverge.
- Many arrays are sized for fixed block counts; invalid instance numbers can index static register arrays.
- The destructor must stay in lockstep with construction order to prevent leaks after partial construction.
- `dcn42_link_enc_create_minimal` uses an off-by-one-looking bounds check with `>` rather than `>=`.
- Pipe fuse handling asserts but still must avoid mapping logical pipe indices to disabled physical instances.
- DML2, FPU wrappers, MCACHE, SPL, SubVP, and z-state decisions depend on `dc->debug` and BIOS/SMU-provided runtime values.

## Test Signals

Build tests catch missing register fields, changed constructor signatures, and function-table mismatches. Runtime signals include `dm_error` allocation messages, `BREAK_TO_DEBUGGER`, pipe-fuse asserts, failed `dml2_validate`, incorrect display caps, link/AUX/I2C failures, and regressions in DSC, SubVP, MCACHE, SPL sharpness, and z-state behavior on DCN42 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h

## Purpose

`dcn42_resource.h` declares the public DCN42 resource-pool interface and the register-list macros used by `dcn42_resource.c` to populate per-block MMIO address tables. It is mostly an ASIC register mapping header for DPP, stream encoders, HPO DP, DCCG, audio, OPTC, clock sources, ABM, and HUBP.

## Important APIs, Types, And Functions

- `struct dcn42_resource_pool { struct resource_pool base; }`: DCN42 concrete pool wrapper.
- `TO_DCN42_RES_POOL(pool)`: container conversion helper.
- Exported functions: `dcn42_create_resource_pool`, `dcn42_validate_bandwidth`, `dcn42_prepare_mcache_programming`, and `dcn42_get_power_profile`.
- Register macros: `DPP_REG_LIST_DCN42_COMMON_RI`, `SE_DCN42_REG_LIST_RI`, `DCN42_HPO_DP_STREAM_ENC_REG_LIST_RI`, `DCN42_HPO_DP_LINK_ENC_REG_LIST_RI`, `VPG_DCN42_REG_LIST_RI`, `DCCG_REG_LIST_DCN42_RI`, `DCN42_AUD_COMMON_MASK_SH_LIST`, `OPTC_COMMON_REG_LIST_DCN42_RI`, `CS_COMMON_REG_LIST_DCN42_RI`, `ABM_DCN42_REG_LIST_RI`, and `HUBP_REG_LIST_DCN42_RI`.

## Control Flow

The header has no executable control flow. Its macro expansions are invoked by the C file with `REG_STRUCT` rebound to different static register arrays. The expanded code assigns MMIO offsets for each hardware instance and mask/shift fields for register programming helpers.

## State And Persistence Behavior

No runtime state is stored here. The header defines how stateful C objects map hardware registers. Changes to the macros affect the register tables embedded in resource-pool objects and therefore every subsequent hardware programming path.

## Dependencies And Integration Points

The header depends on `core_types.h` and the register helper macro vocabulary supplied by the including C file and generated ASIC offset/mask headers. Its exported prototypes are consumed by DCN42 init code, resource callbacks, DML2 validation paths, and MCACHE/z-state programming flows.

## Risks And Edge Cases

- Macro definitions depend on names such as `SRI_ARR`, `SR`, and `REG_STRUCT` being defined before expansion.
- Duplicated or missing register entries can silently program the wrong register table.
- Instance counts in macros must match `res_cap_dcn42` and the generated offset headers.
- The header declares `dcn42_get_power_profile`, while the resource function table uses `dcn401_get_power_profile`; mismatched declarations can confuse call-site expectations if not kept intentional.

## Test Signals

Compiler coverage detects missing register symbols and type mismatches. Real validation requires display bring-up, scaler/color/cursor/ISHARP programming, audio/HDMI/DP packet tests, HPO DP training, ABM, DCCG clock gating, and CRC or visual tests that exercise registers listed here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.c

## Purpose

`dcn42_resource_fpu.c` holds the floating-point-gated DCN42 z-state policy helper. It updates DML bandwidth clock state with whether Z8 is allowed for the current display context.

## Important APIs, Types, And Functions

- `dcn42_decide_zstate_support(dc, context)`: exported helper called from `dcn42_validate_bandwidth` during validate-and-programming.
- Uses `enum dcn_zstate_support_state`, `context->bw_ctx.bw.dcn.clk.zstate_support`, stream/plane counts, eDP link PSR settings, Replay settings, and DML-reported z-state capability.

## Control Flow

The function asserts floating point is enabled, counts active plane states across the resource pool's pipe contexts, and defaults to `DCN_ZSTATE_SUPPORT_DISALLOW`. Empty display or no-plane contexts allow Z8 only. A single eDP stream can allow Z8 when PSR or Replay is enabled, otherwise it follows DML's computed `zstate_support`. DCN42 explicitly has no Z10 path.

## State And Persistence Behavior

The only persistent in-memory mutation is `context->bw_ctx.bw.dcn.clk.zstate_support`. The helper also logs z-state and stutter efficiency information through SMU logging when evaluating eDP.

## Dependencies And Integration Points

It depends on `dc.h`, `dcn42_resource_fpu.h`, `dc_assert_fp_enabled`, Display Core stream/link structures, PSR/Replay panel state, and the bandwidth context produced by DML2. It is integrated into the DCN42 validation/programming path, not mode enumeration.

## Risks And Edge Cases

- The function dereferences `context->streams[0]->sink->link` in the single-eDP path; callers must supply a fully populated stream/sink.
- Plane counting across `dc->res_pool->pipe_count` assumes the context pipe array is initialized for that many entries.
- Incorrect PSR/Replay state can allow or disallow low-power residency unexpectedly.
- It overwrites the DML boolean-like z-state output with a support enum value.

## Test Signals

Useful tests cover no-stream, no-plane, single eDP with PSR, eDP with Replay, eDP without PSR/Replay using DML output, non-eDP active stream, and multi-stream cases. Runtime signals are SMU z-state log lines and observed Z8 residency/power behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.h

## Purpose

`dcn42_resource_fpu.h` declares the FPU-only DCN42 z-state support decision helper.

## Important APIs, Types, And Functions

- Include guard `_DCN42_RESOURCE_FPU_H_`.
- Includes `core_types.h`.
- Declares `void dcn42_decide_zstate_support(struct dc *dc, struct dc_state *context);`.

## Control Flow

No executable control flow is present. The header exposes a helper implemented in the paired C file so non-FPU resource code can call it inside `DC_FP_START`/`DC_FP_END`.

## State And Persistence Behavior

The header itself stores no state. The declared function mutates the bandwidth context in `struct dc_state`.

## Dependencies And Integration Points

It integrates `dcn42_resource.c` with the FPU compilation unit. Consumers must call the helper only with floating-point access enabled, matching kernel AMDGPU display FPU rules.

## Risks And Edge Cases

The main risk is misuse from a non-FPU-safe context. Signature drift between this header and the implementation would break the resource validation path at build time.

## Test Signals

Compiler coverage verifies declaration consistency. Runtime z-state validation on DCN42 confirms the call path is entered only inside the FPU guard and produces expected Z8 decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/Makefile

## Purpose

This Makefile adds the SoC/IP translator component to AMD Display builds and applies FPU compiler flags to translator implementation files because DML bounding-box values use floating-point data.

## Important APIs, Types, And Functions

- `soc_and_ip_translator_ccflags := $(CC_FLAGS_FPU)`.
- `soc_and_ip_translator_rcflags := $(CC_FLAGS_NO_FPU)`.
- Per-object `CFLAGS_...` and `CFLAGS_REMOVE_...` for DCN401 and DCN42 translators.
- `soc_and_ip_translator` object list and `AMD_DISPLAY_FILES += $(AMD_DAL_soc_and_ip_translator)`.

## Control Flow

Kbuild evaluates the object list, prefixes each object with `$(AMDDALPATH)/dc/soc_and_ip_translator/`, removes no-FPU flags from the generation-specific translator objects, adds FPU flags, and appends the component objects to the global display build list.

## State And Persistence Behavior

No runtime state exists. The build state affected is object inclusion and compiler flag selection.

## Dependencies And Integration Points

It depends on AMD Display's Kbuild variables `AMDDALPATH`, `AMD_DISPLAY_FILES`, `CC_FLAGS_FPU`, and `CC_FLAGS_NO_FPU`. It integrates the generic translator plus `dcn401` and `dcn42` implementations into the driver.

## Risks And Edge Cases

- Forgetting FPU flags can break kernel FPU rules or compile-time constraints around floating-point constants.
- Adding a new translator without matching flag entries may compile it with no-FPU flags despite using floating-point data.
- Path variable changes must preserve the exact object keys used by Kbuild.

## Test Signals

Kernel build output should include `soc_and_ip_translator.o`, `dcn401_soc_and_ip_translator.o`, and `dcn42_soc_and_ip_translator.o` with the intended FPU flags. Link failures or floating-point compiler diagnostics indicate configuration drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.c

## Purpose

`dcn401_soc_and_ip_translator.c` supplies DCN4.01 DML2 SoC bounding-box and IP-capability data. It starts from static bounding-box tables, then overlays runtime SMU clock tables, VBIOS latency values, and software policy overrides.

## Important APIs, Types, And Functions

- `dcn401_get_soc_bb(soc_bb, dc, config)`: exported full bounding-box construction.
- `dcn401_update_soc_bb_with_values_from_clk_mgr`, `dcn401_update_soc_bb_with_values_from_vbios`, and `dcn401_update_soc_bb_with_values_from_software_policy`: reusable update layers.
- `dcn401_convert_dc_clock_table_to_soc_bb_clock_table(...)`: maps `clk_bw_params` to `dml2_soc_state_table`, optionally clipped by DC-mode clock limits.
- `dcn401_construct_soc_and_ip_translator(...)`: installs function table callbacks.
- Static `dcn401_get_ip_caps(ip_caps)` returns `dml2_dcn401_max_ip_caps`.

## Control Flow

`dcn401_get_soc_bb` copies default DCN401 SoC and QoS tables, then applies updates in priority order: clock manager values, VBIOS values, and software policy overrides. Clock-table conversion independently handles DCFCLK, FCLK, UCLK, DISPCLK, DPPCLK, DTBCLK, and SOCCLK, filling unused entries with zero and truncating values when `config->use_clock_dc_limits` is active.

## State And Persistence Behavior

The file writes only caller-provided `struct dml2_soc_bb` and `struct dml2_ip_capabilities` outputs. It reads runtime state from `dc->clk_mgr`, `dc->caps`, `dc->res_pool`, `dc->ctx->dc_bios`, and `dc->bb_overrides`. No state is retained between calls.

## Dependencies And Integration Points

It depends on DCN4 bounding-box headers, DML2 SoC/IP structures, `clk_mgr`, BIOS `bb_info`, and the generic `soc_and_ip_translator` function-table interface. DCN42 reuses the VBIOS and software-policy update helpers.

## Risks And Edge Cases

- Clock entries are assumed sorted ascending for DC-limit clipping logic.
- Null `bw_params` is handled, but `dc->clk_mgr` and its function table are assumed valid.
- DC-mode clipping can reduce `num_clk_values`; consumers must tolerate shortened tables.
- Unit conversions mix MHz to kHz and 100 ns/ns to microseconds; mistakes directly affect DML validation.
- Software overrides intentionally supersede VBIOS values, so bad overrides can destabilize watermark and p-state decisions.

## Test Signals

Tests should compare generated SoC tables against known SMU/VBIOS inputs, including DC-limit clipping boundaries and zero/empty clock tables. Runtime signals include DML validation changes, watermark/p-state regressions, and display mode acceptance differences when BIOS or debug overrides change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.h

## Purpose

This header declares the DCN401 SoC/IP translator constructor and reusable bounding-box update helpers.

## Important APIs, Types, And Functions

- `dcn401_construct_soc_and_ip_translator`.
- `dcn401_get_soc_bb`.
- `dcn401_update_soc_bb_with_values_from_clk_mgr`.
- `dcn401_update_soc_bb_with_values_from_vbios`.
- `dcn401_update_soc_bb_with_values_from_software_policy`.

## Control Flow

The header contains declarations only. It enables generic factory code and newer DCN translator implementations to call DCN401 update stages.

## State And Persistence Behavior

No state is stored here. The declared helpers populate caller-owned DML2 bounding-box structures from runtime DC state.

## Dependencies And Integration Points

Includes `core_types.h`, `dc.h`, `clk_mgr.h`, `soc_and_ip_translator.h`, and DML2 SoC parameter types. It is included by the generic translator factory and by the DCN42 translator to reuse VBIOS/software-policy code.

## Risks And Edge Cases

Because these helpers are reusable across revisions, changing their signatures or semantics can break DCN42 and any future translator that inherits DCN401 update behavior. FPU use must remain aligned with the Makefile flags and caller contexts.

## Test Signals

Build coverage verifies declarations across generic, DCN401, and DCN42 translation units. Functional validation comes from matching DML2 SoC outputs for DCN401 and DCN42 when shared update layers are exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn42/dcn42_soc_and_ip_translator.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn42/dcn42_soc_and_ip_translator.c

## Purpose

`dcn42_soc_and_ip_translator.c` provides the DCN4.2 implementation of the DML2 SoC/IP translator. It builds a DCN42 bounding box from static tables, runtime SMU clocks, memory type, VBIOS latencies, and software overrides.

## Important APIs, Types, And Functions

- `dcn42_get_soc_bb(soc_bb, dc, config)`: exported DCN42 SoC bounding-box constructor.
- `dcn42_construct_soc_and_ip_translator(...)`: installs DCN42 function callbacks.
- `dcn42_convert_dc_clock_table_to_soc_bb_clock_table(...)`: maps SMU clock tables into DML2 state tables and vmin limits.
- `dcn42_update_soc_bb_with_values_from_clk_mgr(...)`: overlays DPREFCLK, VCO speed, MALL allocation, SMU clocks, and DDR5 power-management parameters.
- `dcn42_get_ip_caps(ip_caps)`: returns `dml2_dcn42_max_ip_caps`.

## Control Flow

`dcn42_get_soc_bb` copies `dml2_socbb_dcn42` and DCN42 QoS defaults, then applies updates. Clock conversion handles DCN42-specific FCLK/DCFCLK pairing: it fills FCLK with the first active value that reaches at least twice the current DCFCLK, because PMFW tables may contain inactive zero levels. UCLK includes WCK ratio. DISPCLK and DPPCLK are represented as fine-grain two-entry tables from zero to max. VBIOS and software-policy updates are delegated to the DCN401 helpers.

## State And Persistence Behavior

The file writes only the supplied output structures. It reads `dc->clk_mgr`, `dc->caps.mall_size_total`, `dc->clk_mgr->bw_params`, VRAM type, BIOS data, and software overrides. No translator-private mutable state is retained.

## Dependencies And Integration Points

It depends on DCN42 bounding-box headers, DCN401 shared helpers, DML2 SoC/IP structures, and the generic translator function table. It is selected by `soc_and_ip_translator.c` for `DCN_VERSION_4_2` and feeds DML2 validation used by the DCN42 resource pool.

## Risks And Edge Cases

- `dcn42_update_soc_bb_with_values_from_clk_mgr` reads `dc->clk_mgr->bw_params->vram_type` after the SMU-present check path; a null `bw_params` would be unsafe.
- FCLK selection assumes enough valid table entries to find an active value for each DCFCLK level.
- Fine-grain DISPCLK/DPPCLK collapse changes DML search behavior and must match hardware clock programming policy.
- DDR5 power-management replacement is memory-type dependent and can materially change stutter/p-state validation.

## Test Signals

Validation should cover empty/incomplete PMFW tables, DDR5 vs non-DDR5, vmin limit updates, fine-grain clock construction, and inherited VBIOS/software overrides. Runtime signals are DML2 mode acceptance, watermark changes, p-state behavior, and differences from DCN401 on the same clock/BIOs inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn42/dcn42_soc_and_ip_translator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn42/dcn42_soc_and_ip_translator.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn42/dcn42_soc_and_ip_translator.h

## Purpose

This header declares the DCN42 SoC/IP translator constructor and the DCN42 SoC bounding-box getter.

## Important APIs, Types, And Functions

- `dcn42_construct_soc_and_ip_translator(struct soc_and_ip_translator *soc_and_ip_translator)`.
- `dcn42_get_soc_bb(struct dml2_soc_bb *soc_bb, const struct dc *dc, const struct dml2_configuration_options *config)`.

## Control Flow

The header has no executable flow. It exposes DCN42 translator functions to the generic translator factory and any direct DML2 integration code.

## State And Persistence Behavior

No state is stored here. The declared implementation populates caller-owned DML2 structures from DC runtime state.

## Dependencies And Integration Points

Includes core DC types, `dc.h`, `clk_mgr.h`, DML top SoC parameter types, and the generic `soc_and_ip_translator` definition. It is consumed by `soc_and_ip_translator.c`.

## Risks And Edge Cases

The include path uses `dml_top_soc_parameter_types.h` directly while DCN401 uses the `dml2_0/dml21/inc/...` path; include path changes can break one header but not the other. Signature changes must stay synchronized with the generic function table.

## Test Signals

Build coverage confirms include paths and declarations. Runtime validation is indirect through successful creation of a DCN42 translator and correct `get_soc_bb`/`get_ip_caps` callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn42/dcn42_soc_and_ip_translator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/soc_and_ip_translator.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/soc_and_ip_translator.c

## Purpose

`soc_and_ip_translator.c` is the generic factory/destructor for the SoC/IP translator abstraction. It selects a generation-specific translator implementation based on Display Core version.

## Important APIs, Types, And Functions

- `dc_create_soc_and_ip_translator(dc_version)`: allocates a translator and dispatches construction.
- `dc_destroy_soc_and_ip_translator(&translator)`: frees the translator and nulls the caller's pointer.
- `dc_construct_soc_and_ip_translator(translator, dc_version)`: private switch mapping `DCN_VERSION_4_01` to DCN401 and `DCN_VERSION_4_2` to DCN42.

## Control Flow

Creation allocates with `kzalloc_obj`, returns NULL on allocation failure, then calls the private switch. Unsupported versions leave `translator_funcs` unset. Destruction calls `kfree` and clears the pointer.

## State And Persistence Behavior

The factory allocates one heap object containing a function-table pointer. It owns no global state. Lifetime is caller-managed through create/destroy.

## Dependencies And Integration Points

It includes the generic translator header and generation-specific DCN401/DCN42 headers. Resource and DML2 setup code use the returned translator to get SoC bounding boxes and IP capabilities without hard-coding generation logic.

## Risks And Edge Cases

- Unsupported versions still return a non-NULL object with no callbacks, so callers must handle missing `translator_funcs`.
- The switch must be updated when new DCN revisions add translator implementations.
- Destruction assumes the caller passes a valid pointer-to-pointer; double-destroy would dereference a NULL object pointer if not guarded externally.

## Test Signals

Factory tests should verify callback selection for DCN4.01 and DCN4.2, NULL allocation behavior, unsupported-version behavior, and pointer nulling on destroy. Build coverage catches missing generation constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/soc_and_ip_translator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/Makefile

## Purpose

The SSPL Makefile adds the scaler programming library to the AMD Display build. SSPL calculates scaler, EASF, and iSHARP programming data used by DCN display pipes.

## Important APIs, Types, And Functions

- `SPL = dc_spl.o dc_spl_scl_filters.o dc_spl_scl_easf_filters.o dc_spl_isharp_filters.o dc_spl_filters.o spl_fixpt31_32.o spl_custom_float.o`.
- `AMD_DAL_SPL = $(addprefix $(AMDDALPATH)/dc/sspl/,$(SPL))`.
- `AMD_DISPLAY_FILES += $(AMD_DAL_SPL)`.

## Control Flow

Kbuild expands the SSPL object list, prefixes each object with the display source path, and appends them to the driver object list.

## State And Persistence Behavior

No runtime state exists. The file controls which SSPL compilation units are linked into the display driver.

## Dependencies And Integration Points

It depends on `AMDDALPATH` and `AMD_DISPLAY_FILES`. It integrates the core SPL calculator, fixed-point math, custom float conversion, standard scaler filters, EASF filter tables, iSHARP filter tables, and filter conversion helpers.

## Risks And Edge Cases

Leaving out one object can compile the public headers but fail at link time or disable a required filter path. Adding new public SPL APIs usually requires updating this object list.

## Test Signals

Build/link tests should resolve `spl_calculate_scaler_params`, filter lookup helpers, fixed-point math helpers, and iSHARP/EASF support. Runtime scaler tests indicate whether the full object set is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.c

## Purpose

`dc_spl.c` is the core scaler programming library. It converts high-level plane, stream, slicing, rotation, pixel-format, scaling-quality, EASF, and iSHARP inputs into `dscl_prog_data` for DCN scaler hardware programming.

## Important APIs, Types, And Functions

- Public APIs: `SPL_NAMESPACE(spl_calculate_scaler_params)` and `SPL_NAMESPACE(spl_get_number_of_taps)`.
- Geometry helpers: `calculate_plane_rec_in_timing_active`, `calculate_mpc_slice_in_timing_active`, `calculate_odm_slice_in_timing_active`, `spl_calculate_recout`, `intersect_rec`, and `shift_rec`.
- Scaling math: `spl_calculate_scaling_ratios`, `spl_calculate_viewport_size`, `spl_calculate_init_and_vp`, `spl_calculate_inits_and_viewports`, and `spl_handle_3d_recout`.
- Policy helpers: `spl_get_optimal_number_of_taps`, `enable_easf`, `spl_get_isharp_en`, `spl_get_dscl_mode`, and `spl_choose_lls_policy`.
- Programming emitters: `spl_set_dscl_prog_data`, `spl_set_easf_data`, `spl_set_isharp_data`, `spl_set_manual_ratio_init_data`, and `spl_set_taps_data`.

## Control Flow

The full parameter path zeroes scratch state, records active timing size, computes recout by mapping plane clip from stream-source to timing-active space, slices it by MPC and ODM, computes luma/chroma ratios, applies OPP recout adjustment, estimates viewport size, chooses taps/EASF/iSHARP using input policy and line-buffer callback limits, computes final viewport offsets and filter inits, handles stereo offsets, clamps viewport size, writes DSCL programming fields, then fills EASF and iSHARP-specific registers/LUT pointers.

`spl_get_number_of_taps` follows the same early path but only emits tap fields. This lets callers ask resource questions without filling the whole DSCL programming payload.

## State And Persistence Behavior

The function keeps all intermediate state in stack `struct spl_scratch` and writes caller-owned `spl_out->dscl_prog_data`. It mutates `spl_in->lls_pref` when the caller leaves it as `LLS_PREF_DONT_CARE`. Filter/LUT pointers refer to static tables in sibling files.

## Dependencies And Integration Points

It depends on `dc_spl_types.h`, fixed-point helpers, `dc_spl_scl_easf_filters.h`, `dc_spl_isharp_filters.h`, and SPL callback `spl_calc_lb_num_partitions`. DCN resource code enables SPL via `dc->config.use_spl` and uses the output to program DSCL, EASF, iSHARP, scaler filters, viewport, recout, black color, ratios, and inits.

## Risks And Edge Cases

- Many divisions assume nonzero source/destination dimensions and slice counts.
- `enable_easf` returns a variable named `skip_easf`, so misuse is easy when editing.
- Some paths fill DSCL data before returning false; callers must respect the boolean.
- Rotation, mirroring, chroma cositing, 3D, MPC slicing, ODM slicing, custom width, and OPP adjustments interact tightly.
- EASF and iSHARP only support certain tap combinations; policy/tap changes can silently disable features.
- The line-buffer callback must be valid and return accurate partition counts.

## Test Signals

Strong test coverage includes identity scale bypass, RGB/YUV420/YUV444 formats, chroma cositing, 90/180/270 rotation, horizontal mirror, integer scaling, >2:1 EASF disable, >6:1 downscale asserts, MPO/MPC slicing, ODM combine, 3D side-by-side/top-bottom, line-buffer-limited vtaps, EASF linear/nonlinear modes, HDR coefficient calculation, and iSHARP policy thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.h

## Purpose

`dc_spl.h` is the public SSPL interface header for scaler parameter calculation.

## Important APIs, Types, And Functions

- Defines scaler black offsets: `BLACK_OFFSET_RGB_Y` and `BLACK_OFFSET_CBCR`.
- Declares `SPL_NAMESPACE(spl_calculate_scaler_params(struct spl_in *spl_in, struct spl_out *spl_out))`.
- Declares `SPL_NAMESPACE(spl_get_number_of_taps(struct spl_in *spl_in, struct spl_out *spl_out))`.
- Includes `dc_spl_types.h`.

## Control Flow

The header has no executable flow. It exposes the two core entry points implemented in `dc_spl.c`.

## State And Persistence Behavior

No state is stored here. The declared functions write caller-owned output structures and may update fields inside `spl_in`.

## Dependencies And Integration Points

Consumers include this header to call SPL from Display Core scaling/resource programming. The `SPL_NAMESPACE` macro allows namespacing across build environments.

## Risks And Edge Cases

The API relies on large structured inputs from `dc_spl_types.h`; callers must initialize all geometry, format, quality, callback, and output pointers before calling. The black-offset constants must remain consistent with DSCL programming expectations for RGB and YCbCr.

## Test Signals

Build coverage confirms public symbols. Runtime scaler tests should call both public APIs with valid `spl_in`/`spl_out` structures and verify programmed recout, viewport, taps, ratios, and filter pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_filters.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_filters.c

## Purpose

`dc_spl_filters.c` provides a small filter coefficient format conversion helper for SPL scaler tables.

## Important APIs, Types, And Functions

- `SPL_NAMESPACE(convert_filter_s1_10_to_s1_12(const uint16_t *s1_10_filter, uint16_t *s1_12_filter, int num_taps))`: converts fixed-point coefficients from S1.10 to S1.12 by multiplying each entry by four.
- Uses `NUM_PHASES_COEFF` from the paired header to determine `33 * num_taps` entries.

## Control Flow

The function computes `num_entries = NUM_PHASES_COEFF * num_taps`, then linearly copies and scales every coefficient from source to destination.

## State And Persistence Behavior

No persistent state exists. The destination buffer is caller-owned and overwritten in place.

## Dependencies And Integration Points

It includes `dc_spl_filters.h` and is linked into the SSPL component. It supports filter-table preparation for scaler/EASF/iSHARP code that needs S1.12 hardware coefficient format from S1.10 source tables.

## Risks And Edge Cases

- The function assumes both pointers are valid and the destination has enough space.
- Multiplying by four can overflow if a coefficient is not a valid S1.10 value fitting the expected hardware range.
- `num_taps` must match the table layout used by the caller.

## Test Signals

Unit tests can convert known 3/4/6/8-tap arrays and verify every output equals input times four for exactly `33 * taps` entries. Memory sanitizer coverage catches undersized buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_filters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_filters.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_filters.h

## Purpose

`dc_spl_filters.h` declares common SSPL filter helper definitions.

## Important APIs, Types, And Functions

- `NUM_PHASES_COEFF 33`: number of coefficient phases used by the helper.
- Declares `SPL_NAMESPACE(convert_filter_s1_10_to_s1_12(...))`.
- Includes `dc_spl_types.h`.

## Control Flow

No executable control flow is present.

## State And Persistence Behavior

The header stores no state. The declared helper writes caller-owned buffers.

## Dependencies And Integration Points

It is included by `dc_spl_filters.c` and by iSHARP filter code. The phase count must align with static filter table lengths across SSPL.

## Risks And Edge Cases

If `NUM_PHASES_COEFF` changes without regenerating static coefficient tables, conversion lengths and table sizes will diverge. Consumers must provide correctly sized buffers.

## Test Signals

Build coverage validates declarations. Filter conversion tests should verify the phase-count contract against all tap counts used by scaler and iSHARP tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_filters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.c

## Purpose

`dc_spl_isharp_filters.c` owns iSHARP reference LUTs, blur-and-scale coefficient tables, sharpness-level adaptation, and helper APIs that attach iSHARP filter data to DSCL programming output.

## Important APIs, Types, And Functions

- Static tables: `filter_isharp_1D_lut_3p0x`, S1.10 and S1.12 blur-scale tables for 3-tap, 4-tap, and 6-tap-in-4-tap-layout cases.
- Mutable cache: `filter_isharp_1D_lut_pregen[NUM_SHARPNESS_SETUPS]`.
- Sharpness helpers: `spl_calculate_sharpness_level_adj`, `spl_calculate_sharpness_level`, and `spl_build_isharp_1dlut_from_reference_curve`.
- Public lookup helpers: `spl_get_pregen_filter_isharp_1D_lut`, `spl_dscl_get_blur_scale_coeffs_64p`, `spl_dscl_get_blur_scale_coeffs_64p_s1_10`, and `spl_set_blur_scale_data`.

## Control Flow

Sharpness LUT generation maps a discrete requested sharpness level through setup-specific min/mid/max ranges, optionally reduces it based on scale ratio, converts the selected level to fixed point, scales each byte of the base 3.0x LUT, clamps values to `0x7f`, and stores a cached pre-generated table per `enum system_setup`. Repeated calls with the same setup and sharpness skip recomputation.

Blur-scale lookup selects static coefficient tables by tap count. Supported taps are 3, 4, and 6; unsupported values break to debugger and return NULL. `spl_set_blur_scale_data` assigns horizontal and vertical blur-scale filter pointers from current scaler taps.

## State And Persistence Behavior

Most data is static read-only. `filter_isharp_1D_lut_pregen` is static mutable cache state storing the last generated sharpness table for each setup. There is no locking in this file, so concurrent callers can race while updating the same setup's cached LUT.

## Dependencies And Integration Points

It depends on SPL fixed-point math, `spl_debug.h`, filter helper definitions, and `dc_spl_isharp_filters.h`. `dc_spl.c` calls it when iSHARP is enabled to generate the delta LUT, retrieve the cached LUT, and attach blur-scale filters to `dscl_prog_data`.

## Risks And Edge Cases

- Only taps 3, 4, and 6 are valid for iSHARP blur-scale lookup.
- The mutable pre-generated LUT cache is not synchronized; parallel commits with different sharpness levels could interleave.
- The cached key ignores the full sharpness range and policy, using only resulting numerator/denominator per setup.
- Byte-level LUT scaling assumes the packed DWORD layout of `filter_isharp_1D_lut_3p0x`.
- S1.10 and S1.12 tables must remain numerically paired.

## Test Signals

Tests should validate sharpness reduction thresholds, min/mid/max interpolation for SDR/HDR and linear/nonlinear setups, LUT clamping, cache reuse, blur-scale table selection for 3/4/6 taps, NULL/debug behavior for invalid taps, and `dscl_prog_data->filter_blur_scale_h/v` pointer assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.h

## Purpose

`dc_spl_isharp_filters.h` defines iSHARP filter helper types and public lookup/generation APIs used by the SPL core.

## Important APIs, Types, And Functions

- `NUM_SHARPNESS_ADJ_LEVELS`.
- `struct scale_ratio_to_sharpness_level_adj`: ratio threshold to sharpness down-adjust mapping.
- `struct isharp_1D_lut_pregen`: cached sharpness numerator/denominator and generated LUT values.
- `enum system_setup`: `SDR_NL`, `SDR_L`, `HDR_NL`, `HDR_L`, and `NUM_SHARPNESS_SETUPS`.
- Public APIs: `spl_set_blur_scale_data`, `spl_build_isharp_1dlut_from_reference_curve`, `spl_get_pregen_filter_isharp_1D_lut`, `spl_dscl_get_blur_scale_coeffs_64p`, and `spl_dscl_get_blur_scale_coeffs_64p_s1_10`.

## Control Flow

No executable control flow exists in the header. It defines the shape of lookup tables and declares functions implemented by `dc_spl_isharp_filters.c`.

## State And Persistence Behavior

The header stores no state. The implementation has static LUT cache state represented by `struct isharp_1D_lut_pregen`.

## Dependencies And Integration Points

It includes `dc_spl_types.h` for `dscl_prog_data`, `spl_scaler_data`, `adaptive_sharpness`, fixed-point types, and policy enums. It is included by `dc_spl.c` to configure iSHARP during scaler parameter calculation.

## Risks And Edge Cases

Changing enum order changes the cache index and setup interpretation. The public APIs assume caller-selected tap values are supported by iSHARP tables. The LUT size must match `ISHARP_LUT_TABLE_SIZE`.

## Test Signals

Build coverage validates API compatibility. Functional tests should include every `system_setup`, supported tap count, sharpness policy, and integration with `spl_calculate_scaler_params` when iSHARP is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.h -->
