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
