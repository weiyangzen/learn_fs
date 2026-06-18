# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 4887-7556

## Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask slice. It has no executable functions or C data structures; its API surface is preprocessor constants of the form `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. DCN 4.1.0 display, DMUB, GPIO, IRQ, clock, and resource code include this header together with `dcn_4_1_0_offset.h` so register helper macros can address MMIO fields by name instead of embedding bit positions.

The range begins in the middle of the MCIF writeback buffer status block, covers MMHUBBUB and Azalia/HDA audio control windows, then covers DCHUBBUB arbitration, SDPIF, return path, VM request/translation, and the start of HUBP0/HUBPREQ0 plane fetch registers. It ends at the first shift macro for `HUBPREQ0_DCN_CUR0_TTU_CNTL1`; the matching mask and following HUBPREQ fields belong to the next chunk.

## Important APIs and register groups

- `MCIF_WB_BUF_1_STATUS*` through `MCIF_WB_BUF_4_STATUS*` describe writeback buffer activity, lock/overflow/disable state, buffer tags, next-buffer selection, current scanline, new-content flags, color depth, TMZ flags, luma/chroma overruns, and eye flags. The chunk starts after some `MCIF_WB_BUF_1_STATUS` shift definitions, so final per-file analysis should reconcile the previous chunk for that register.
- `MCIF_WB_ARBITRATION_CONTROL`, `MCIF_WB_SCLK_CHANGE`, `MCIF_WB_NB_PSTATE_CONTROL`, `MCIF_WB_SELF_REFRESH_CONTROL`, `MULTI_LEVEL_QOS_CTRL`, `MCIF_WB_WATERMARK`, and `MCIF_WB_NB_PSTATE_LATENCY_WATERMARK` define writeback arbitration slices, time-per-pixel, watermark acknowledge forcing, pstate/self-refresh watermarks, and urgency scaling.
- `MCIF_WB_BUF_[1-4]_ADDR_[Y/C]`, high address registers, luma/chroma sizes, per-buffer resolution, `MCIF_WB_SECURITY_LEVEL`, and `MCIF_WB_VMID_CONTROL` expose the memory addresses, dimensions, VMID, and security/TMZ-related placement for writeback luma/chroma surfaces.
- `MMHUBBUB_WARMUP_*`, `MMHUBBUB_MIN_TTO`, `MMHUBBUB_CTRL`, `WBIF_SMU_WM_CONTROL`, `WBIF0_MISC_CTRL`, outstanding counters, memory-power registers, clock control, soft reset, error status, client unit ID, and warmup VMID fields describe the multimedia hubbub side of display memory warmup, writeback interface throttling, power state, reset, and DMUIF interaction.
- `AZALIA_CONTROLLER_CLOCK_GATING`, `AZALIA_AUDIO_DTO`, `AZALIA_AUDIO_DTO_CONTROL`, `AZALIA_SOCCLK_CONTROL`, DMA controls, payload capabilities, stream arbitration, soft reset, and memory-power fields encode the display HDA/Azalia audio controller clocking, DTO phase/module programming, DMA snoop/isochronous attributes, underflow behavior, stream payload limits, and input-stream memory power policy.
- `AZALIA_INPUT_CRC*` and `AZALIA_CRC*` fields define two input CRC engines and two general CRC engines with enable, block mode, instance selection, source/channel selection, block size/iteration, completion status, and 32-bit result readback.
- `AZALIA_F0_CODEC_*`, `CC_RCU_DC_AUDIO_*`, and `REG_DC_AUDIO_*` define root codec parameter/control fields: vendor/device and revision IDs, channel count, resync FIFO, group type, supported rates/formats, power states, power/reset control, subsystem ID response, converter synchronization, and audio port connectivity.
- `AZF0STREAM0` through `AZF0STREAM15` expose repeated indexed stream register windows. Each stream instance has an 8-bit stream register index, write-enable bit, and 32-bit data field.
- `AZF0ENDPOINT0` through `AZF0ENDPOINT7` and `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` expose repeated indexed codec endpoint and input-endpoint register windows with 14-bit endpoint indexes and 32-bit data fields.
- `DCHUBBUB_ARB_*` covers display hubbub arbitration: outstanding request min/max, saturation level, forced QoS, DRAM self-refresh/pstate/C-state/deep-sleep controls, USR retraining controls, duplicated watermark sets A/B, fractional urgent bandwidth for nominal/flip/MALL, watermark-change request/status/select fields, global MALL state, timeouts, global timer, VTG controls, soft reset, clock gating, DCFCLK gating, latency measurement, ROB status, timeout interrupt status, and FMON controls.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, `DCHUBBUB_FORCE_IO_STATUS_*`, `DCN_VM_FB_LOCATION_*`, `DCN_VM_AGP_*`, `DCN_VM_LOCAL_HBM_*`, pipe security/noalloc/datafetch fields, request-rate limit, SDPIF memory power, and MCACHE invalidation controls describe the path between display hubbub and memory fabric, including request credits, response/error status, security levels per pipe/resource class, memory aperture translation, force-I/O diagnostics, and cache invalidation error handling.
- `DCHUBBUB_RET_PATH_*`, `DCHUBBUB_CRC_*`, `DCHUBBUB_DCC_STAT*`, `DCHUBBUB_COMPBUF_CTRL`, `DCHUBBUB_DET[0-3]_CTRL`, `DCHUBBUB_STAT`, `DCHUBBUB_MEM_PWR_*`, `COMPBUF_MEM_PWR_CTRL_*`, `COMPBUF_RESERVED_SPACE`, `DCN_DECOMP_STATUS`, and debug/test registers describe return-path power, CRC capture, DCC statistics, compression buffer and DET sizing/current state, outstanding pipe status, memory-power mode/status, decompression status, and debug selectors.
- `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` define repeated display VM context fields: page-table depth/block size, page-directory base high/low, logical page start high/low, and logical page end high/low. `DCN_VM_DEFAULT_ADDR_*`, `DCN_VM_FAULT_CNTL`, `DCN_VM_FAULT_STATUS`, and fault address fields define default page behavior and page-fault diagnostics.
- `HUBP0_DCSURF_*`, `HUBP0_DCHUBP_*`, and `HUBP0_HUBP_*` fields begin the pipe-0 hubp block: surface pixel format/rotation/array/pitch meta, swizzle/resource/pipe-aligned address configuration, tiling, primary/secondary luma/chroma viewport start/dimension, request-size configuration, hubp control, clock control/status, VM page configuration, MALL configuration and sub-viewport windows, MCACHE ID programming, DCFCLK/DPPCLK measurement windows, and MALL status.
- `HUBPREQ0_DCSURF_*` and `HUBPREQ0_DCN_*` fields begin the pipe-0 hubpreq block: surface pitch and VMID, primary/secondary luma/chroma surface base addresses, surface TMZ/DCC controls, flip/update-lock controls, flip interrupt mask/type/clear/status fields, surface-in-use and earliest-in-use address/VMID readbacks, request expansion modes, TTU QoS watermarks, global TTU controls, and TTU delivery/QoS fields for surf0, surf1, and cursor0.

## Control flow and usage model

There is no local control flow. These macros are compile-time metadata consumed by generated or macro-built register tables.

The normal runtime path is:

1. Include `dcn_4_1_0_offset.h` for register offsets and this header for field encodings.
2. Expand ASIC-specific register tables with helper macros such as `SR`, `SRI`, `SF`, `FD_MASK`, and `FD_SHIFT`.
3. Use AMD Display Core and DMUB register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to read or update named fields while preserving unrelated bits.

Concrete DCN 4.1.0 consumers include `display/dmub/src/dmub_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/gpio/dcn401/*`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, and `display/dc/resource/dcn401/dcn401_resource.c`. The fields in this chunk are also aligned with common DC block code for mmhubbub, hubbub, hubp/hubpreq, audio, IRQ, power, and diagnostics.

## State and persistence behavior

The header itself has no mutable state. The state described by its masks lives in DCN hardware registers and persists until explicitly reprogrammed, reset by block/GPU reset, or restored during suspend/resume/runtime power transitions.

Important stateful areas include:

- Writeback buffer ownership and progress state: active, software/VCE locks, disable/overflow, current line, new-content, overrun, luma/chroma addresses, sizes, resolution, VMID, security level, and TMZ bits. These fields interact with capture/writeback programming and may change asynchronously while writeback is running.
- Memory arbitration and watermarks: MCIF, MMHUBBUB, and DCHUBBUB watermarks, pstate permissions, self-refresh/C-state/deep-sleep controls, urgent bandwidth fractions, MALL selection, and watermark-change request/status bits must match the current display mode, memory clock plan, and power-management policy.
- Azalia audio controller state: DTO phase/module, force DTO, DMA snoop/isochronous modes, underflow filler/control, stream payload capacities, indexed stream/endpoint windows, codec power/reset state, and audio memory-power states persist across display audio enable/disable paths and need suspend/resume restoration.
- SDPIF and VM state: framebuffer/AGP/HBM aperture registers, VM context page-table ranges, physical-request overrides, per-pipe security/noalloc/datafetch settings, MCACHE invalidation controls, and fault status/address registers affect all display memory fetches for the programmed pipe/resource classes.
- HUBP/HUBPREQ plane fetch state: surface format, tiling, viewport, request sizing, DCC/TMZ, MALL/MCACHE, VM page settings, TTU QoS, surface addresses, flip/update locks, and flip interrupt status are central to atomic plane updates and page flips.
- Diagnostic and status state: CRC engines, DCC stat counters, compbuf/DET current size, ROB/timeout/FMON state, force-I/O status, decompression status, memory-power status, MALL status, and surface-in-use readbacks are hardware-produced and may be sticky or clear-on-write depending on the field.

## Dependencies and integration points

- Requires the matching generated offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`. Shift/mask and offset files must be generated from the same register database.
- Depends on AMDGPU Display Core register helpers and macro conventions. The names must match table initializers exactly; build failures catch missing symbols, but they do not prove that a field is semantically safe for a given programming sequence.
- Integrates with DMUB service code. `dmub_dcn401.c` reads `DCN_VM_FB_LOCATION_BASE` and `DCN_VM_FB_OFFSET`, writes MMHUBBUB/DMCUB reset and window registers outside this exact slice, and relies on this header for the corresponding `FD_MASK`/`FD_SHIFT` table generation.
- Integrates with DCN 4.1 IRQ setup. `irq_service_dcn401.c` includes this header for interrupt register masks; the HUBPREQ flip interrupt fields in this chunk map to page-flip IRQ sources in the same service family.
- Integrates with mmhubbub/writeback code for `MCIF_WB_*`, `MMHUBBUB_*`, and `WBIF*` register programming.
- Integrates with clock and power-management code through `MMHUBBUB_CLOCK_CNTL`, `DCHUBBUB_CLOCK_CNTL`, `DCFCLK_CNTL`, `AZALIA_*_PWR*`, SDPIF/return-path memory power, DCHUBBUB memory-power mode/status, and pstate/self-refresh watermarks.
- Integrates with display audio/HDA code through Azalia controller, codec-root, stream, endpoint, DTO, DMA, CRC, and power fields.
- Integrates with hubbub/hubp/hubpreq resource and plane-update paths through DCHUBBUB arbitration/VM/return-path controls and HUBP0/HUBPREQ0 surface address, viewport, request-size, MALL, MCACHE, flip, and TTU QoS fields.

## Risks and edge cases

- The main generated-header risk is offset/mask drift. Correct field constants paired with stale register offsets can silently access the wrong MMIO register.
- This chunk has two boundary truncations: it starts in the middle of `MCIF_WB_BUF_1_STATUS` and ends inside `HUBPREQ0_DCN_CUR0_TTU_CNTL1`. Merge/reconciliation should use adjacent chunks for complete register coverage.
- Many registers mix software-owned controls with hardware-owned status, clear, pending, current, sticky, or interrupt bits. Full-register writes can accidentally clear events, acknowledge errors, disturb status selectors, or corrupt neighboring controls.
- Writeback and hubp surface-address fields are split low/high and luma/chroma. Incorrect sequencing or mismatched VMID/TMZ/security/DCC bits can cause memory faults, corrupted captures, protected-content violations, or display underflow.
- Watermark and pstate fields are timing-sensitive. Forcing QoS, self-refresh, pstate, C-state, deep-sleep, or watermark-change controls outside the expected DC mode-set/power sequence can produce underflow, missed flips, latency spikes, or blocked clock changes.
- Indexed Azalia stream and endpoint windows require correct index/data/write-enable ordering. Reusing the wrong stream instance or endpoint index can corrupt unrelated codec state.
- VM context and aperture fields are high-impact. Incorrect page-table base/range, framebuffer offset, AGP/HBM range, default-address, or fault-control settings affect display memory translation for all fetches using that context.
- HUBPREQ flip controls and interrupt bits are asynchronous relative to vupdate/vblank. Mishandling update locks, pending status, triple-buffering, GSL, flip-away clear/status, or pending delay can create stuck page flips or missed page-flip events.
- Power and clock gates can outlive a single modeset. Forced-on settings can waste power; forced-off or disabled memory blocks can break active audio, writeback, hubbub, SDPIF, compbuf, DET, or return-path traffic.

## Test signals

- Build coverage with DCN 4.1.0 enabled should compile all DCN401 register tables that include `dcn_4_1_0_sh_mask.h` and `dcn_4_1_0_offset.h`.
- Generated-header consistency checks should verify every field in the chunk has the intended `__SHIFT`/`_MASK` pair and that repeated layouts, such as MCIF buffers, Azalia streams/endpoints, VM contexts, DET controls, and pipe security fields, remain intentionally aligned.
- Writeback validation should exercise four-buffer programming, luma/chroma address/high address handling, VMID/security/TMZ combinations, overrun/overflow detection, pstate/watermark behavior, and suspend/resume restoration.
- Audio tests should cover HDA/Azalia enablement, DTO programming, audio underflow handling, stream and endpoint indexed-register access, codec power/reset transitions, payload capacity reporting, audio CRC engines, and memory-power state changes.
- DCHUBBUB watermark and power tests should exercise pstate/self-refresh/C-state/deep-sleep transitions, USR retraining, watermark-change request completion, MALL use, timeout detection/interrupts, FMON, and runtime PM.
- VM and memory-fault tests should program display VM contexts, framebuffer/AGP/HBM aperture fields, per-pipe security/noalloc/datafetch controls, MCACHE invalidation, and verify fault status/address reporting on invalid accesses.
- Plane and flip tests should cover HUBP0/HUBPREQ0 surface formats, tiling, DCC/TMZ, luma/chroma viewports, primary/secondary addresses, TTU QoS, MALL/MCACHE configuration, flip interrupts, update locks, GSL/triple-buffer cases, and surface-in-use readbacks.
- Diagnostic tests should validate DCHUBBUB CRC, DCC stat counters, compbuf/DET resizing, decompression status clear, force-I/O sticky status, memory-power status readbacks, outstanding-pipe status, and MALL status fields.
