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
