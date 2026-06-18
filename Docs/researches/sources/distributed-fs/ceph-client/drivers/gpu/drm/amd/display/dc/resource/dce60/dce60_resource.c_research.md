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
