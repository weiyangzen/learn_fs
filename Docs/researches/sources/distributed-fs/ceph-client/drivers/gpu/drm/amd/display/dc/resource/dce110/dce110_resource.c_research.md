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
