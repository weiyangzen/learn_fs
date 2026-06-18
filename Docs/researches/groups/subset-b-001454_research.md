# Research: subset-b-001454

Grouped research for AMD Display Core resource-pool implementations and headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/`. Each section preserves the source path and is intended to be split into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce110/dce110_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce110/dce110_resource.c

## Purpose
This file builds the DCE 11.0 resource pool used by Carrizo and Stoney display hardware. It enumerates per-generation register tables, hardware-object factories, resource caps, validation callbacks, bandwidth setup, and teardown logic for the AMD Display Core resource layer.

## Important APIs, Types, And Functions
- `dce110_create_resource_pool()` allocates `struct dce110_resource_pool`, calls `dce110_resource_construct()`, and returns the embedded `struct resource_pool`.
- `dce110_resource_build_pipe_hw_param()` is exported for related generations; it derives pixel clock parameters, clock dividers, bit-depth reduction, and stream clamping state for a mapped pipe.
- `dce110_find_first_free_match_stream_enc_for_link()` selects a free stream encoder, preferring the link encoder's preferred DIG engine and falling back for MST cases.
- `dce110_res_pool_funcs` wires the pool into generic DC resource operations: destroy, link encoder create, panel control create, bandwidth/plane/global validation, underlay acquisition, add-stream mapping, and stream-encoder selection.
- Static factory helpers create timing generators, stream encoders, memory inputs, IPPs, transforms, OPPs, AUX engines, I2C engines, audio blocks, clock sources, ABM, DMCU, IRQ service, and hardware sequencer state.

## Control Flow
Construction starts by binding BIOS scratch registers and selecting `carrizo_resource_cap` or `stoney_resource_cap` from the ASIC revision. It sets public DC caps, creates a DP clock source and PLL clock sources from BIOS firmware data, then creates DMCU, ABM, IRQ service, per-pipe TG/MI/IPP/XFM/OPP objects, AUX/I2C engines, optional FBC compressor, a virtual underlay pipe, and generic link/audio/encoder resources via `resource_construct()`. Finally it constructs the DCE 11.0 hardware sequencer, publishes plane capabilities, initializes DCE bandwidth structures, and imports PPLIB clocks into `bw_vbios`.

The add-stream path maps pool resources, maps clock resources, then calls `build_mapped_resource()`, which finds the OTG master pipe, rejects unsupported underlay formats, builds clock/pipe parameters, and builds info frames. Bandwidth validation calls `bw_calcs()` and logs watermark changes when the calculated DCE bandwidth context differs from the current state.

## State And Persistence
The resource pool owns allocated hardware-object pointers in `pool->base`; persistent driver-visible caps are written into `dc->caps`, `dc->debug`, and `dc->check_config`. Underlay creation appends a virtual pipe at `underlay_pipe_index`, mutates max slave-plane caps, and can power on/program the underlay timing generator during acquisition. Bandwidth state is persisted in `dc->bw_dceip`, `dc->bw_vbios`, `dc->sclk_lvls`, and each validation context's `bw_ctx.bw.dce`.

## Dependencies And Integration Points
This file depends on DCE 11.0 register headers, GMC fallback register definitions, DCE component constructors, IRQ service creation, PPLIB clock queries, BIOS scratch register mappings, and generic `resource_construct()`/mapping helpers. It integrates with the DC core through `resource_funcs`, `resource_create_funcs`, `dc->hwseq`, `dc->fbc_compressor`, and link/audio/stream encoder factories.

## Risks
Clock setup depends on valid BIOS external DP clock metadata; failure leaves construction aborted. PPLIB clock-level indexing assumes non-empty level arrays. Link encoder creation indexes `link_enc_aux_regs[channel - 1]`, so invalid non-unknown channel values would be hazardous. The underlay path has format/order restrictions and does hardware power/timing programming while acquiring a secondary pipe. Constructor failure cleanup is broad but relies on partially initialized arrays matching `pipe_count`, `num_ddc`, stream count, and clock counts.

## Test Signals
Useful signals include successful boot/resource-pool construction on Carrizo and Stoney, DP/HDMI/DVI modesets, MST encoder allocation, FBC-enabled construction, NV12 underlay overlay validation, bandwidth failure logging, suspend/resume teardown, and memory-leak checks on constructor failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce110/dce110_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce110/dce110_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce110/dce110_resource.h

## Purpose
This header declares the DCE 11.0 resource-pool wrapper and the small set of DCE 11.0 helpers reused by other resource implementations.

## Important APIs, Types, And Functions
- `struct dce110_resource_pool` embeds `struct resource_pool`.
- `TO_DCE110_RES_POOL(pool)` converts a base `resource_pool` pointer back to its containing DCE 11.0 pool.
- `dce110_resource_build_pipe_hw_param()` exposes DCE 11.0 pipe clock and stream parameter construction to later DCE variants.
- `dce110_create_resource_pool()` is the generation factory for DCE 11.0.
- `dce110_find_first_free_match_stream_enc_for_link()` exposes the common stream encoder selection policy.

## Control Flow
The header has no runtime control flow. It is consumed by DC resource initialization code and by DCE 11.2, DCE 12.0, DCE 6/8, and DCN code that reuse the container, helper, or stream-encoder selection APIs.

## State And Persistence
The only state shape introduced here is the wrapper around `struct resource_pool`; all owned state is allocated and persisted by the implementation.

## Dependencies And Integration Points
It includes `core_types.h` for `struct pipe_ctx`, `struct resource_context`, `struct dc_stream_state`, `struct hw_asic_id`, and related DC types. The exported helpers are integration points between generation-specific resource files and generic DC resource mapping.

## Risks
The container macro assumes callers pass a valid embedded `resource_pool`. Because this header is reused by multiple generations, signature changes can break several resource backends at once.

## Test Signals
Compile coverage across DCE 11.0, DCE 11.2, DCE 12.0, older DCE, and DCN resource files is the primary signal. Runtime signals come from successful pool creation and stream encoder selection in those implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce110/dce110_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c

## Purpose
This file constructs the DCE 11.2 resource pool for Polaris-class hardware. It adapts the DCE 11 component model to six/five-pipe discrete GPUs, combo PHY PLL clocking, DCE 11.2 register layouts, and Polaris bandwidth watermark programming.

## Important APIs, Types, And Functions
- `dce112_create_resource_pool()` allocates and constructs a DCE 11.2 pool.
- `dce112_validate_bandwidth()` is exported and reused by DCE 12.0.
- `dce112_add_stream_to_ctx()` is exported and reused by DCE 12.0; it maps pool resources, maps PHY/DP clocks, and builds pipe resources.
- `resource_map_phy_clock_resources()` assigns DP/virtual streams to the DP DTO source and non-DP streams to the PLL tied to their transmitter.
- `find_matching_pll()` maps UNIPHY A-F to `DCE112_CLK_SRC_PLL0` through `PLL5`.
- `dce112_res_pool_funcs` installs DCE 11.2 creation, validation, stream mapping, and stream encoder selection callbacks.

## Control Flow
Construction selects Polaris 10 or Polaris 11/12 caps from ASIC revision, disables underlay, sets DC caps, creates six combo PHY PLL clock sources plus a DP DTO, then creates DMCU, ABM, IRQ service, per-pipe timing generators, memory inputs, IPPs, transforms, and OPPs. It creates AUX and hardware I2C engines per DDC line, calls `resource_construct()` to add shared link/audio/encoder resources, constructs the DCE 11.2 hardware sequencer, fills plane caps, initializes DCE bandwidth data, and pushes PPLIB clock/watermark ranges into bandwidth structures and PP/SMU.

The validation path restricts each stream to one non-video plane, calls shared DCE bandwidth calculations, and reports watermark deltas. The add-stream path performs generic pool mapping, generation-specific clock mapping, and DCE 11.0 pipe parameter building plus info-frame generation.

## State And Persistence
Persistent state lives in `pool->base` arrays, DC capability fields, BIOS register mappings, DCE bandwidth structures, and PP/SMU watermark range notifications. Transform instances set `lb_memory_size` to `0x1404`. Link encoder caps advertise HDMI 600 MHz, HDMI YCbCr420, DP HBR3, TPS3, and TPS4 support.

## Dependencies And Integration Points
The file depends on DCE 11.2 register headers, DCE 11.0 shared helpers, DCE 100 validation helpers, IRQ service DCE 110, PPLIB clock APIs, DCE component constructors, and generic resource mapping. The exported bandwidth/add-stream routines are direct integration points for DCE 12.0.

## Risks
Watermark range setup assumes valid PPLIB clock arrays or falls back to older APIs; invalid counts can still affect indexed levels. PLL selection depends on the link encoder transmitter being populated. Plane validation is conservative and rejects video planes entirely. Constructor cleanup must handle partially initialized six-pipe arrays and the separate DP clock source.

## Test Signals
Signals include Polaris 10/11/12 pool creation, HDMI 2.0/YCbCr420 modes, DP HBR3 link training, non-DP PLL selection by transmitter, bandwidth validation with PPLIB watermark notifications, one-plane validation failures for video or MPO attempts, and teardown after allocation-failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.h

## Purpose
This header exposes the DCE 11.2 resource-pool constructor and selected validation/mapping routines for use by DC core and nearby generations.

## Important APIs, Types, And Functions
- `dce112_create_resource_pool()` creates a DCE 11.2 pool.
- `dce112_validate_with_context()` is declared as an external validation API, though its implementation is not in this file.
- `dce112_validate_bandwidth()` exports the DCE bandwidth validation wrapper.
- `dce112_add_stream_to_ctx()` exports the DCE 11.2 stream resource mapping sequence.

## Control Flow
The header itself has no runtime behavior. It defines call boundaries used by DCE 11.2 and by DCE 12.0, which reuses the bandwidth and add-stream implementations.

## State And Persistence
No state is declared beyond function interfaces. The functions operate on `struct dc`, `struct dc_state`, `struct dc_stream_state`, and resource-pool state owned by implementation files.

## Dependencies And Integration Points
It includes `core_types.h` and forward-declares `struct dc` and `struct resource_pool`. It is an integration seam between generation resource construction and generic DC validation/modeset code.

## Risks
Because DCE 12.0 includes this header to reuse functions, ABI/signature changes here can break multiple resource backends. The declared `dce112_validate_with_context()` requires definition elsewhere; missing linkage would show up at build time.

## Test Signals
Build tests should verify both DCE 11.2 and DCE 12.0 users link successfully. Runtime tests should cover bandwidth validation and add-stream behavior through both generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c

## Purpose
This file constructs the DCE 12.0 resource pool for Vega-class SOC15 display hardware. It is a DCE 11.2-derived backend with SOC15 base-indexed register addressing, DCE 12 component constructors, Vega20 pipe harvesting, OEM I2C support, and DCE 12 hardware sequencer variants.

## Important APIs, Types, And Functions
- `dce120_create_resource_pool()` allocates and constructs the DCE 12.0 pool.
- `dce120_resource_construct()` performs all resource creation and capability publication.
- `dce120_res_pool_funcs` reuses `dce112_validate_bandwidth()` and `dce112_add_stream_to_ctx()` while providing DCE 12 link/panel/destroy callbacks.
- `read_pipe_fuses()` reads `CC_DC_PIPE_DIS` for Vega20 pipe harvesting.
- `dce120_hwseq_create()` and `dce121_hwseq_create()` select base DCE 12 or Vega20-specific HWSEQ registers through separate `resource_create_funcs`.
- `read_dce_straps()` uses SOC15 register reads rather than the older `REG_GET` path.

## Control Flow
Construction sets SOC15 BIOS scratch register addresses, publishes DCE 12 caps, creates six combo PHY PLLs and one DP DTO, validates clock-source allocation, then creates DMCU, ABM, DCE 12 IRQ service, and per-pipe TG/MI/IPP/XFM/OPP objects. On Vega20, disabled pipe fuses are skipped and compacted into contiguous pool indices. AUX and I2C engines are created per DDC line. The constructor chooses normal or Vega20 resource-create callbacks, calls `resource_construct()`, constructs the hardware sequencer, sets plane caps, initializes DCE bandwidth data from PPLIB with fallbacks, and optionally creates an OEM DDC service from BIOS firmware info.

## State And Persistence
State is held in `pool->base`, DC caps, BIOS register mappings, clock-source arrays, DCE bandwidth tables, and optional `pool->base.oem_device`. For harvested Vega20 parts, `pipe_count` and `timing_generator_count` are rewritten to the number of usable pipes after construction. `dc->debug.disable_clock_gate` defaults to true for this generation.

## Dependencies And Integration Points
Dependencies include DCE 12/SOC15/NBIO/MMHUB register offsets, DCE 11.2 shared validation and clock source construction, DCE/DIO component constructors, DCE 12 IRQ service, PP/SMU watermark notification APIs, `link_service` for OEM DDC, and generic resource construction. It integrates with DCE 11 shared stream encoder selection via `dce110_find_first_free_match_stream_enc_for_link()`.

## Risks
The Vega20 pipe-harvesting loop compacts resources by `j` while some NULL checks mistakenly reference `ipps[i]` and `transforms[i]`, which can miss failures when `i != j`. The fallback memory-clock loop initializes `mem_clks` using `eng_clks.num_levels`, which can exceed the declared fallback `mem_clks.num_levels`. IRQ destruction is inside the per-pipe loop, so partial teardown paths should be inspected for repeated destroy attempts. SOC15 base-address macros are sensitive to register-header correctness.

## Test Signals
Useful tests include Vega10 and Vega20 pool creation, harvested-pipe boot with disabled pipe fuses, HDMI/DP modesets, DP DTO and combo PHY PLL assignment through reused DCE 11.2 add-stream flow, OEM I2C firmware-device creation, PPLIB absent/fallback bandwidth setup, and allocation-failure teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.h

## Purpose
This header declares the public constructor for the DCE 12.0 resource pool.

## Important APIs, Types, And Functions
- `dce120_create_resource_pool(uint8_t num_virtual_links, struct dc *dc)` creates and returns a DCE 12.0 `struct resource_pool`.

## Control Flow
The header has no runtime control flow. DC initialization code calls the constructor declared here when the ASIC/display version maps to DCE 12.

## State And Persistence
No state is declared in the header. The implementation uses the DCE 11.0 resource-pool wrapper internally and persists state in `struct resource_pool` and `struct dc`.

## Dependencies And Integration Points
It includes `core_types.h` and forward-declares `struct dc` and `struct resource_pool`. It is the compile-time boundary between DC version selection and DCE 12 resource construction.

## Risks
The API exposes only a constructor, so any future DCE 12 helper reuse would require header expansion. Signature drift must be coordinated with DC factory selection code.

## Test Signals
Build coverage of DCE 12 selection and runtime pool construction on Vega-family hardware are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce60/dce60_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce60/dce60_resource.c

## Purpose
This file builds resource pools for DCE 6.0, 6.1, and 6.4 hardware. It adapts the common DCE resource model to older register layouts, analog/VGA support, software I2C fallback objects, generation-specific caps, and DCE 6 timing/memory/transform constructors.

## Important APIs, Types, And Functions
- `dce60_create_resource_pool()`, `dce61_create_resource_pool()`, and `dce64_create_resource_pool()` allocate and construct pools for the three DCE 6 variants.
- `dce60_res_pool_funcs` delegates validation and stream mapping to DCE 100 helper functions while using DCE 6 link/panel/destroy callbacks.
- `dce60_stream_encoder_create()` creates analog stream encoders for DACA/DACB and digital encoders otherwise.
- `dce60_link_encoder_create()` special-cases VGA connectors with analog engines before mapping transmitters to UNIPHY register instances.
- `dce60_mem_input_create()` sets the `single_head_rdreq_dmif_limit` workaround to `2`.

## Control Flow
Each constructor selects its resource caps (`res_cap`, `res_cap_61`, or `res_cap_64`), sets DC caps, creates DP and non-DP clock sources based on BIOS external DP clock availability, then creates DMCU, ABM, DCE 6 IRQ service, per-pipe timing generators, memory inputs, IPPs, transforms, and OPPs. It creates AUX, hardware I2C, and software I2C objects for each DDC line, publishes RGB plane caps, disables DP clock sharing, calls `resource_construct()` for shared link/audio/stream resources, and constructs the DCE 6 hardware sequencer.

## State And Persistence
The pool persists all hardware-object pointers and caps in `pool->base`; DC caps record cursor size, DVI support, APU status for DCE 6.1/6.4, and DP clock-sharing disablement. There is no underlay pipe. Software I2C objects are owned per DDC line and freed during destruction.

## Dependencies And Integration Points
Dependencies include DCE 6 register headers, GMC 6 fallback memory-input register definitions, DCE component constructors, DCE 60 IRQ/HWSEQ/timing implementations, DCE 100 validation helpers, and generic resource construction. Integration with analog display support happens through VGA connector and DACA/DACB encoder paths.

## Risks
The three constructors are mostly duplicated, so fixes must be applied consistently. Clock-source selection differs subtly between DCE 6.0/6.4 and 6.1. VGA/analog paths rely on valid analog engine metadata and sparse stream encoder register entries. The old hardware path has no scaling for FP16/NV12 and limited caps, so validation should reject unsupported formats before modeset.

## Test Signals
Signals include DCE 6.0/6.1/6.4 boot, VGA and digital connector modesets, analog stream encoder creation, external-DP-clock and PLL0 DP-clock configurations, hardware and software I2C access, DCE 100 validation behavior, and teardown under partial allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce60/dce60_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce60/dce60_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce60/dce60_resource.h

## Purpose
This header declares resource-pool constructors for DCE 6.0, DCE 6.1, and DCE 6.4.

## Important APIs, Types, And Functions
- `dce60_create_resource_pool()` creates a DCE 6.0 pool.
- `dce61_create_resource_pool()` creates a DCE 6.1 pool.
- `dce64_create_resource_pool()` creates a DCE 6.4 pool.

## Control Flow
There is no runtime logic in the header. DC version selection calls one of the declared constructors based on the target ASIC.

## State And Persistence
The header declares no state. Each constructor returns a generic `struct resource_pool` whose ownership is transferred to DC core.

## Dependencies And Integration Points
It includes `core_types.h` and forward-declares `struct dc` and `struct resource_pool`. It is the boundary between DCE 6 ASIC selection and the resource implementation.

## Risks
The three constructor APIs are easy to confuse because they share the same signature but publish different caps. Call-site ASIC mapping is therefore the main correctness dependency.

## Test Signals
Build coverage for all three constructor references and runtime creation on DCE 6.0/6.1/6.4 ASIC IDs are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce60/dce60_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.c

## Purpose
This file builds resource pools for DCE 8.0, 8.1, and 8.3 hardware. It is the DCE 8 counterpart to the older DCE resource constructors, adding DCE 8 register tables, Hawaii/Kaveri-style caps, analog encoder support, software I2C allocation, and DCE 8 timing/HWSEQ integration.

## Important APIs, Types, And Functions
- `dce80_create_resource_pool()`, `dce81_create_resource_pool()`, and `dce83_create_resource_pool()` are the public constructors.
- `dce80_res_pool_funcs` delegates validation and stream mapping to DCE 100 helpers while using DCE 8 construction/destruction functions.
- `dce80_stream_encoder_create()` handles DACA/DACB analog encoders and normal digital stream encoders.
- `dce80_link_encoder_create()` special-cases VGA analog links and otherwise maps UNIPHY transmitters to link encoder registers.
- `dce80_mem_input_create()` applies the `single_head_rdreq_dmif_limit = 2` workaround.

## Control Flow
Each constructor selects caps for DCE 8.0, 8.1, or 8.3, binds BIOS scratch registers, sets DC caps, creates DP/non-DP clock sources from BIOS external DP clock availability, creates DMCU, ABM, DCE 8 IRQ service, and allocates per-pipe timing generators, memory inputs, IPPs, transforms, and OPPs. It then creates AUX engines plus hardware and software I2C objects for DDCs, publishes RGB plane caps, disables DP clock sharing, calls `resource_construct()` for shared encoders/audio/link handling, and constructs the DCE 8 hardware sequencer.

## State And Persistence
State is persisted in `pool->base`, DC caps, DMCU/ABM/IRQ services, per-pipe object arrays, DDC engines, and clock-source arrays. There is no underlay pipe. DCE 8.1 and 8.3 mark the device as APU, while DCE 8.0 enables dual-link DVI and broader six-pipe caps.

## Dependencies And Integration Points
Dependencies include DCE 8 register headers, GMC 7.1 fallback memory-input definitions, DCE component constructors, DCE 80 IRQ/HWSEQ/timing modules, DCE 100 validation helpers, BIOS firmware clock metadata, and generic resource construction.

## Risks
Constructor bodies are duplicated across variants and differ mainly in caps and PLL choices. DCE 8.3 has reduced PLL/DDC resources and a different DP clock-source fallback, so incorrect ASIC mapping can expose missing clocks. Analog/VGA paths depend on sparse register arrays and valid analog engine metadata. Cleanup must free both hardware and software I2C engines for partially initialized variants.

## Test Signals
Signals include DCE 8.0/8.1/8.3 pool construction, HDMI/DVI/DP/VGA modesets, DCE 8.3 two-pipe operation, external DP clock versus PLL-backed DP clock behavior, software I2C fallback, DCE 100 bandwidth/plane validation, and leak-free cleanup after allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.h

## Purpose
This header declares resource-pool constructors for DCE 8.0, DCE 8.1, and DCE 8.3.

## Important APIs, Types, And Functions
- `dce80_create_resource_pool()` creates a DCE 8.0 pool.
- `dce81_create_resource_pool()` creates a DCE 8.1 pool.
- `dce83_create_resource_pool()` creates a DCE 8.3 pool.

## Control Flow
The header has no runtime flow; it provides constructor entry points for the DC version/ASIC selection layer.

## State And Persistence
No state is declared here. Each constructor returns an owned `struct resource_pool` that persists all DCE 8 resources in the implementation.

## Dependencies And Integration Points
It includes `core_types.h` and forward-declares `struct dc` and `struct resource_pool`. It integrates the DCE 8 resource backend with DC core initialization.

## Risks
The three variants share signatures but have different hardware caps. Incorrect call-site selection can overstate available pipes, clocks, or DDCs.

## Test Signals
Build coverage for all constructor declarations and runtime pool creation on DCE 8.0/8.1/8.3 ASICs are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c

## Purpose
This file constructs the DCN 1.0/1.01 resource pool for Raven-family hardware. Unlike the DCE files, it builds DCN objects such as HUBP, DPP, MPC, HUBBUB, OPTC, DIO, and DML/SOC/IP bandwidth state while still reusing several DCE components for AUX, I2C, audio, DMCU/ABM, and clock sources.

## Important APIs, Types, And Functions
- `dcn10_create_resource_pool()` allocates `struct dcn10_resource_pool` and invokes `dcn10_resource_construct()`.
- `dcn10_res_pool_funcs` installs DCN-specific destroy, link encoder, validation, secondary-pipe acquisition, add-stream, unknown-plane patching, stream encoder selection, vstartup, and tiling callbacks.
- `dcn10_validate_bandwidth()` wraps `dcn_validate_bandwidth()` in `DC_FP_START/END`.
- `dcn10_validate_global()` enforces DCN 1.0 MPO limits and a single-channel-memory underflow workaround for 4K desktop plus downscaled 4K video.
- `dcn10_acquire_free_pipe_for_layer()` allocates secondary DPP pipes for layer composition and maps HUBP/IPP/DPP/MPCC state.
- `dcn10_get_default_tiling_info()` publishes GFX9 linear default tiling.

## Control Flow
Construction binds NBIO BIOS scratch registers, selects four-pipe DCN 1.0 caps or three-pipe DCN 1.01 caps, publishes extensive DC caps and color-pipeline capabilities, creates combo PHY PLLs plus a DP DTO, DMCU, ABM, initializes DML with `dcn1_0_soc`/`dcn1_0_ip`, copies DCN IP/SOC defaults, and applies floating-point bandwidth construction. It creates PP/SMU function hooks, optionally updates bandwidth from PPLIB FCLK/DCFCLK voltage tables, synchronizes DML/bandwidth state, notifies PPLIB watermark ranges, creates IRQ service, skips disabled pipe fuses, then creates HUBP, IPP, DPP, OPP, and OPTC objects for valid pipes. It creates AUX/I2C engines, sets the final pipe and MPCC counts, updates DML max DPP counts, creates MPC, HUBBUB, and DIO, calls `resource_construct()` for shared resources, constructs the DCN HW sequencer, fills plane caps, and exposes DCC compression caps.

The add-stream path maps pool resources, calls DCE 11.2 PHY clock mapping, and builds DCN pipe clock/clamping/bit-depth parameters. Stream encoder selection prefers matching PHY or USB4 DPIA engines while avoiding virtual encoders as the generic fallback.

## State And Persistence
Persistent state includes `pool->base` object arrays, `dc->caps`, `dc->debug`, `dc->check_config`, `dc->dml`, `dc->dcn_ip`, `dc->dcn_soc`, `pool->base.pp_smu`, `pipe_count`, `timing_generator_count`, `mpcc_count`, and `dc->cap_funcs`. Pipe fuses can reduce usable pipe count and update DML maximum DPPs. Unknown plane states are patched to GFX9 64KB swizzle modes based on bits per pixel.

## Dependencies And Integration Points
The file depends on DCN 1.0 register offsets, SOC15/NBIO/MMHUB offsets, DML/FPU helpers, DCN component constructors, DCE clock/audio/AUX/I2C helpers, IRQ service DCN10, PPLIB/SMU clock APIs, DCE 11.2 clock-resource mapping, and generic resource construction. It is the DCN 1.x entry point for Display Core resource ownership.

## Risks
Destructors destroy IRQ service inside the per-pipe loop, which is sensitive to repeated calls if multiple pipes were allocated. Link encoder creation returns NULL without freeing `enc10` if HPD source is out of range after allocation. PPLIB clock verification breaks to debugger when clock tables are missing or zero, so platform firmware quality matters. Global validation intentionally rejects MPO on multi-display and specific 4K underflow-prone cases. Pipe fuse compaction requires all per-pipe arrays and DML counts to stay aligned.

## Test Signals
Signals include Raven/Raven2 pool construction, pipe-fuse-reduced systems, DCN 1.01 three-pipe systems, DP/HDMI/USB4 DPIA stream encoder selection, DML bandwidth validation, PPLIB FCLK/DCFCLK update and watermark notification, DCC capability queries through HUBBUB, MPO validation failures, unknown tiling patch behavior, and allocation-failure teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.h

## Purpose
This header declares the DCN 1.0 resource-pool wrapper, constructor, and helper exports used by DCN/DC resource code.

## Important APIs, Types, And Functions
- `struct dcn10_resource_pool` embeds `struct resource_pool`.
- `TO_DCN10_RES_POOL(pool)` converts a base pool pointer to the DCN 1.0 containing type.
- `dcn10_create_resource_pool()` creates the DCN 1.0/1.01 pool from `struct dc_init_data`.
- `dcn10_find_first_free_match_stream_enc_for_link()` exposes DCN stream encoder matching.
- `dcn10_get_vstartup_for_pipe()` returns the pipe DLG vstartup value.
- `dcn10_get_default_tiling_info()` publishes the default DCN tiling metadata.
- `dcn1_0_ip` and `dcn1_0_soc` are declared as external DML IP/SOC bounding-box inputs.

## Control Flow
The header has no runtime control flow. Its declarations are consumed by DCN initialization, validation, and helper code.

## State And Persistence
The wrapper shape identifies a DCN 1.0 pool while storing state in the embedded generic `resource_pool`. The extern DML structures represent shared immutable model inputs defined elsewhere.

## Dependencies And Integration Points
It includes `core_types.h` and `dml/dcn10/dcn10_fpu.h`, tying the resource backend to DC core types and DML model structures. The exported helpers bridge DCN resource allocation with stream encoder selection, timing, and tiling code.

## Risks
The header exposes DML/FPU types, so build configurations around floating-point code must remain compatible. The container macro has the usual embedded-struct validity requirement.

## Test Signals
Build coverage for DCN 1.0/1.01 resource users, DML symbol linkage, and runtime calls to stream encoder selection, vstartup, and default tiling helpers are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.h -->
