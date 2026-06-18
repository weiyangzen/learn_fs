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
