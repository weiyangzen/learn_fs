# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c

## Purpose

`dcn201_resource.c` is the DCN 2.0.1 resource-pool implementation for Cyan Skillfish-style hardware. It is a smaller DCN2-family variant that defines local IP and SoC DML bounding boxes, DCN201-specific register lists and constructors, a reduced capability table, and a resource function table that reuses many DCN20 algorithms.

## Important APIs, Types, And Functions

- `dcn201_create_resource_pool()` allocates and constructs a `dcn201_resource_pool`.
- `dcn201_resource_construct()` initializes caps/debug/workarounds, creates clocks, DCCG, DML instance, IRQ service, per-pipe HUBP/IPP/DPP, OPP/TG/MPC/HUBBUB/DIO, AUX/I2C, common stream/audio resources, and the DCN201 hardware sequencer.
- `dcn201_resource_destruct()` and `dcn201_destroy_resource_pool()` tear down the pool.
- Local factories create DCN201 DPP, IPP, OPP, HUBP, timing generator, MPC, HUBBUB, DIO, link encoder, clock sources, AUX/I2C, audio, stream encoder, and hwseq objects.
- `dcn201_acquire_free_pipe_for_layer()` provides a generation-local secondary-pipe acquisition helper.
- `dcn201_get_dcc_compression_cap()` forwards DCC capability queries to HUBBUB.
- `dcn201_populate_dml_writeback_from_context()` wraps the DCN201 FPU writeback population function.
- `dcn201_link_init()` reads integrated BIOS info to disable DP spread spectrum when requested.

## Control Flow

Construction assigns BIOS registers and `dcn201_res_pool_funcs`, hard-codes the reduced resource cap (`2` TG/OPP/audio/stream encoders/DDC, `4` video planes, no DWB/DSC), sets DC caps, color capabilities, debug defaults, and A0-era workarounds, then creates two clock sources plus the DP DTO source. It creates DCCG, patches `dcn201_ip.max_num_otg` and `max_num_dpp`, initializes DML with `DML_PROJECT_DCN201`, creates the DCN201 IRQ service, and allocates four HUBP/IPP/DPP pipes. It then creates OPPs, AUX/I2C engines, timing generators, MPC, HUBBUB, DIO, common resources via `resource_construct()`, and the hw sequencer.

The resource function table delegates major behavior to DCN20: bandwidth validation, DML pipe population, stream add/remove, pipe release, unknown-plane patching, MCIF arbitration, stream encoder matching, vstartup, and default tiling. DCN201 replaces construction/destruction, link init, pipe acquisition, DCC cap query, and writeback DML population.

## State And Persistence Behavior

The file has no disk persistence. It mutates the DC resource pool, DC caps/debug/check-config/workaround state, DML bounding-box instance, link spread-spectrum flag, and pipe/resource ownership state. The local `dcn201_ip` and `dcn201_soc` static objects provide DML state for this generation and are adjusted for actual OTG/DPP counts during construction.

## Dependencies And Integration Points

It depends on DCN201 register offset/mask headers, Cyan Skillfish offsets, DCN201 hardware constructors, DCN20 common resource helpers, DCN20 DML FPU helpers, generic DC resource code, IRQ service, DCE AUX/I2C/audio/clock helpers, and DIO/link/stream encoder constructors. Its `resource_funcs` table integrates with generic DC through the same callbacks as DCN20, but with no DSC allocation callback and no panel control constructor.

## Risks And Edge Cases

- The capability table advertises no DSC and no DWB; delegated DCN20 stream paths must tolerate `add_dsc_to_stream_resource = NULL` and zero DSC resources.
- The pool has four video planes but only two OPPs/TGs/stream encoders, so validation must prevent unsupported active stream combinations.
- Static DML SoC/IP values are hard-coded and can become stale relative to firmware/SMU reality.
- `dcn201_resource_destruct()` destroys IRQ service inside the per-pipe loop if non-NULL; pointer clearing by `dal_irq_service_destroy()` must prevent repeated destruction.
- Link init depends on optional integrated BIOS info.
- The debug defaults disable PP-lib clock requests and watermark ranges, which changes validation/runtime behavior compared with other DCN2 variants.

## Test Signals

Build tests should cover DCN201 register-list and constructor compatibility. Runtime tests should cover pool construction/destruction, failure cleanup, two-stream limits, four-plane/two-OTG validation behavior, DCN20 delegated bandwidth validation, no-DSC stream handling, DCC cap forwarding, DP spread-spectrum BIOS handling, DML bounding-box initialization, AUX/I2C creation, and FPU writeback population wrappers. Watch for `DC_FAIL_BANDWIDTH_VALIDATE`, allocation error logs, pipe acquisition failures, and unexpected calls to NULL DSC/panel callbacks.
