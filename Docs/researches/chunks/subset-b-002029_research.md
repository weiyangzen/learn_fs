# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h - subset-b-002029

## Scope

- Chunk id: `subset-b-002029`
- Source lines: 4914-7582
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`
- Observed content: 2,669 lines, 2,053 `#define` entries, 1,025 `__SHIFT` macros, 1,028 `_MASK` macros, 489 register comments, and 42 address-block markers.

This chunk is a generated AMD DCN 3.2.1 register field mask/shift segment. It has no executable C code, no functions, and no C data types. Its purpose is to publish compile-time bit positions and bit masks for DCN321 display hardware registers so AMDGPU Display Core code can pack, unpack, and read-modify-write memory-mapped register fields safely.

## Purpose

The chunk covers the tail of the `dce_dc_mmhubbub_mmhubbub_dispdec` block and then several large display/audio/memory-request blocks:

- `dce_dc_mmhubbub_mmhubbub_dispdec`: MMHUBBUB warmup, writeback watermark, clock, memory-power, soft-reset, VGA/WBIF, and DMU interface status fields.
- `dce_dc_hda_*`: Azalia HDA audio controller, codec root, stream index/data windows, output endpoints, input endpoints, audio clocks, DMA behavior, CRC diagnostics, power states, and audio port connectivity.
- `dce_dc_dchubbubl_hubbub_dispdec`: DCHUBBUB arbitration, watermark set A/B/C/D fields, MALL state, VTG controls, global timer, surface-check addresses, soft reset, clock gating, performance measurement, timeout detection, and FMON controls.
- `dce_dc_dchubbubl_hubbub_sdpif_dispdec`: SDPIF request/response status, PRQ error detection, force-IO capture, framebuffer/AGP/HBM aperture fields, per-pipe security levels, no-allocate behavior, request rate limiting, and SDPIF memory-power state.
- `dce_dc_dchubbubl_hubbub_ret_path_dispdec`: DCHUBBUB return-path memory power, CRC generation/result registers, DCC statistics, compressed buffer controls, DET buffer controls, global memory-power controls, debug, and reserved compbuf space fields.
- `dce_dc_dchubbubl_hubbub_vmrq_if_dispdec`: DCN VM context 0-15 page table controls, context base/start/end address fields, default address, fault control/status, and fault address capture.
- `dce_dc_dcbubp0_dispdec_hubp_dispdec`: HUBP0 surface format, address and tiling configuration, viewport dimensions, request sizing, HUBP control, clock control, VM page config, MALL config/status, and measurement windows.
- `dce_dc_dcbubp0_dispdec_hubpreq_dispdec`: HUBPREQ0 pitch, VMID, primary/secondary/meta surface addresses, flip control, flip interrupts, in-use addresses, TTU/QoS, VM aperture/TLB controls, prefetch, blanking, nominal/vblank/flip delivery parameters, cursor settings, memory power, pstate force, and status.
- `dce_dc_dcbubp0_dispdec_hubpret_dispdec`: HUBPRET0 return/crossbar control, memory power, read-line programming, vblank/read-line interrupts, and read-line snapshots.

The generated pattern is consistent throughout:

- A `//REGISTER_NAME` marker names the hardware register.
- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask within the 32-bit register.

The matching register offsets live in `dcn_3_2_1_offset.h`; this header supplies only field layout.

## Important APIs, Types, and Macros

There are no C APIs, functions, structs, or enums in this chunk. The public interface is the macro namespace.

Important macro families include:

- MMHUBBUB and writeback integration:
  - `MMHUBBUB_WARMUP_CONTROL_STATUS`, `MMHUBBUB_WARMUP_BASE_ADDR_LOW/HIGH`, `MMHUBBUB_WARMUP_ADDR_REGION`, and `MMHUBBUB_WARMUP_VMID_CONTROL` define warmup enable, software interrupt, base address, region, increment, and VMID fields.
  - `WBIF_SMU_WM_CONTROL`, `WBIF0_MISC_CTRL`, and `WBIF0_PHASE*_OUTSTANDING_COUNTER` define writeback watermark change request/ack, SOCCLK deep sleep, interrupt status, timeout, and outstanding-counter fields.
  - `MMHUBBUB_MEM_PWR_STATUS`, `MMHUBBUB_MEM_PWR_CNTL`, `MMHUBBUB_CLOCK_CNTL`, `MMHUBBUB_SOFT_RESET`, `DMU_IF_ERR_STATUS`, and `MMHUBBUB_CLIENT_UNIT_ID` define memory power, gate-disable, soft-reset, DMU error clear, and client unit-id fields.
- Azalia HDA controller and audio codec:
  - `AZALIA_CONTROLLER_CLOCK_GATING`, `AZALIA_AUDIO_DTO`, `AZALIA_AUDIO_DTO_CONTROL`, `AZALIA_SOCCLK_CONTROL`, and `AZ_CLOCK_CNTL` describe audio clock gating, DTO phase/module, forced DTO behavior, SOCCLK deep-sleep exit, and test-clock selection.
  - `AZALIA_DATA_DMA_CONTROL`, `AZALIA_BDL_DMA_CONTROL`, `AZALIA_RIRB_AND_DP_CONTROL`, and `AZALIA_CORB_DMA_CONTROL` describe snoop/isochronous behavior and DMA/control-ring behavior for audio data, BDL, RIRB, DP updates, and CORB traffic.
  - `AZALIA_INPUT_CRC*` and `AZALIA_CRC*` define CRC enable, sample/continuous/block modes, block iteration, completion/status, channel select, and CRC result fields.
  - `AZALIA_MEM_PWR_CTRL` and `AZALIA_MEM_PWR_STATUS` expose global audio memory power plus per-input-stream memory power state for streams 0-5.
  - `AZALIA_F0_CODEC_*`, `CC_RCU_DC_AUDIO_*`, and `REG_DC_AUDIO_*` publish codec vendor/revision, supported rates/formats/power states, reset, subsystem response, converter sync, GTC group offsets, and audio output/input port connectivity override fields.
  - `AZF0STREAM0` through `AZF0STREAM15`, `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, and `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` are repeated index/data windows for stream and endpoint register access.
- DCHUBBUB arbitration and global controls:
  - `DCHUBBUB_ARB_DF_REQ_OUTSTAND`, `DCHUBBUB_ARB_SAT_LEVEL`, `DCHUBBUB_ARB_QOS_FORCE`, `DCHUBBUB_ARB_DRAM_STATE_CNTL`, and `DCHUBBUB_ARB_USR_RETRAINING_CNTL` define request outstanding thresholds, saturation, urgent/nominal QoS force, self-refresh/pstate gating, and retraining policy.
  - `DCHUBBUB_ARB_*_WATERMARK_A/B/C/D`, `DCHUBBUB_ARB_FRAC_URG_BW_*`, and `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL` define four watermark sets for urgency, self-refresh enter/exit, UCLK/FCLK pstate change, retraining, trip-to-memory, urgent bandwidth fractions, and the request/done/status handshake used to switch sets.
  - `DCHUBBUB_ARB_MALL_CNTL`, `SURFACE_CHECK*_ADDRESS_*`, `VTG0_CONTROL` through `VTG3_CONTROL`, `DCHUBBUB_GLOBAL_TIMER_CNTL`, `DCHUBBUB_PERFORMANCE_MEASUREMENT_CNTL*`, `DCHUBBUB_TIMEOUT_*`, and `FMON_CTRL` define MALL use/prefetch state, surface checker addresses, vertical timing generator counters, timer setup, latency instrumentation, timeout status/interrupts, and frame monitor controls.
- SDPIF, aperture, and security:
  - `DCHUBBUB_SDPIF_CFG0/1/2` define outstanding request status, port/response state, credit errors, PRQ errors, force-snoop, host VM security level, and unit-id bitmasks.
  - `VM_REQUEST_PHYSICAL`, `DCHUBBUB_FORCE_IO_STATUS_0/1`, `DCN_VM_FB_LOCATION_*`, `DCN_VM_AGP_*`, and `DCN_VM_LOCAL_HBM_ADDRESS_*` define physical request forcing/capture and the display VM aperture ranges for framebuffer, AGP, and local HBM.
  - `DCHUBBUB_SDPIF_PIPE_*_SEC_LVL`, `DCHUBBUB_SDPIF_PIPE_NOALLOC`, and `SDPIF_REQUEST_RATE_LIMIT` define per-pipe security, per-request-class security, no-allocate, and rate-limiting fields.
- Return path, CRC, DCC, and buffers:
  - `DCHUBBUB_RET_PATH_MEM_PWR_*`, `DCHUBBUB_CRC_CTRL`, `DCHUBBUB_CRC*_VAL_*`, and `DCHUBBUB_DCC_STAT*` define return-path SRAM state, CRC mode/selection/result, and DCC statistics.
  - `DCHUBBUB_COMPBUF_CTRL`, `DCHUBBUB_DET*_CTRL`, `DCHUBBUB_MEM_PWR_MODE_CTRL`, `COMPBUF_MEM_PWR_CTRL_*`, `DCHUBBUB_MEM_PWR_STATUS`, `COMPBUF_RESERVED_SPACE`, and `DCHUBBUB_DEBUG_CTRL_0` define compressed-buffer size, DET buffer configuration, per-bank memory power force/disable/mode, memory status, reserved space, and debug selection.
- DCN VM context and faults:
  - `DCN_VM_CONTEXT0_CNTL` through `DCN_VM_CONTEXT15_CNTL` define page-table depth and block size for each VMID context.
  - Each context has `PAGE_TABLE_BASE_ADDR_HI32/LO32`, `PAGE_TABLE_START_ADDR_HI32/LO32`, and `PAGE_TABLE_END_ADDR_HI32/LO32` fields for directory base and logical page range programming.
  - `DCN_VM_DEFAULT_ADDR_MSB/LSB`, `DCN_VM_FAULT_CNTL`, `DCN_VM_FAULT_STATUS`, and `DCN_VM_FAULT_ADDR_MSB/LSB` define default fault address behavior, fault clear/mode/interrupt enable, range/PRQ fault disable bits, faulting VMID/table level/pipe, and captured fault address.
- HUBP0 and HUBPREQ0 surface request path:
  - `HUBP0_DCSURF_SURFACE_CONFIG`, `HUBP0_DCSURF_ADDR_CONFIG`, `HUBP0_DCSURF_TILING_CONFIG`, viewport registers, `HUBP0_DCHUBP_REQ_SIZE_CONFIG*`, `HUBP0_DCHUBP_CNTL`, `HUBP0_HUBP_CLK_CNTL`, `HUBP0_DCHUBP_VMPG_CONFIG`, and `HUBP0_DCHUBP_MALL_*` define pixel format, rotation, mirroring, alpha plane enable, swizzle/tiling, chunk sizes, stereo/blanking/reorder behavior, clock gating, VM page config, and MALL mode/status.
  - `HUBPREQ0_DCSURF_*_ADDRESS*`, `HUBPREQ0_DCSURF_SURFACE_CONTROL`, `HUBPREQ0_DCSURF_FLIP_CONTROL*`, `HUBPREQ0_DCSURF_SURFACE_FLIP_INTERRUPT`, and `HUBPREQ0_DCSURF_SURFACE_INUSE*` define primary/secondary/luma/chroma/meta addresses, flip mode, flip request/ack/pending status, interrupt control/clear/status, and in-use/earliest-in-use address tracking.
  - `HUBPREQ0_DCN_TTU_QOS_WM`, `HUBPREQ0_DCN_GLOBAL_TTU_CNTL`, `HUBPREQ0_DCN_SURF*_TTU_CNTL*`, `HUBPREQ0_DCN_CUR*_TTU_CNTL*`, `HUBPREQ0_DCN_DMDATA_VM_CNTL`, `HUBPREQ0_DCN_VM_*`, `HUBPREQ0_PREFETCH_SETTINGS*`, `HUBPREQ0_VBLANK_PARAMETERS_*`, `HUBPREQ0_FLIP_PARAMETERS_*`, `HUBPREQ0_NOM_PARAMETERS_*`, and `HUBPREQ0_PER_LINE_DELIVERY*` define TTU/QoS, cursor and surface delivery timing, metadata VM behavior, aperture/TLB controls, prefetch, vblank, flip, and nominal request timing.
- HUBPRET0 return/timing:
  - `HUBPRET0_HUBPRET_CONTROL`, `HUBPRET0_HUBPRET_MEM_PWR_*`, `HUBPRET0_HUBPRET_READ_LINE_CTRL*`, `HUBPRET0_HUBPRET_READ_LINE0/1`, `HUBPRET0_HUBPRET_INTERRUPT`, and `HUBPRET0_HUBPRET_READ_LINE_VALUE` define DET base, 3-to-2 packing, crossbar source selection, return-path memory power, programmable read-line windows, vblank/read-line interrupt mask/type/clear/status, and current/snapshotted pipe read line.

## Control Flow

The header has no runtime control flow. The runtime flow is supplied by DCN321 display code:

1. `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` includes `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`.
2. DC resource construction builds register, shift, and mask tables for blocks such as hubbub, VMID, HUBP, audio, AFMT/VPG/APG, DWB, and MMHUBBUB.
3. Block constructors such as `hubbub32_construct`, `dce_audio_create`, `dcn30_dwbc_construct`, and `dcn32_mmhubbub_construct` receive pointers to those register/shift/mask tables.
4. Runtime code uses AMD display register helpers to write fields by applying the generated shift/mask constants to 32-bit MMIO register values.
5. Hardware state machines then act on the programmed bits, while status and diagnostic fields are read back through the same macro contract.

The implied hardware flows include:

- Programming watermark set A/B/C/D fields, requesting a DCHUBBUB watermark switch, and checking the change-done status.
- Programming VM context base/start/end registers before enabling HUBP/HUBPREQ fetches for a VMID.
- Staging surface address, pitch, tiling, viewport, TTU, and prefetch fields before surface flip request/ack handling.
- Handling flip and vblank/read-line interrupts by masking, clearing, and reading the status fields.
- Configuring audio clocks, stream windows, endpoint windows, and DMA/CRC behavior through Azalia index/data and control registers.
- Reading timeout, VM fault, force-IO, CRC, DCC, outstanding request, and memory-power status fields for debug and recovery.

## State and Persistence Behavior

The macros are compile-time constants and persist only in the compiled driver image. They describe hardware register state with these lifetimes:

- Persistent until reset or reprogrammed: surface format/tiling/pitch, viewport dimensions, VM context page-table ranges, MALL policy, TTU/QoS timing, watermark sets, audio DTO/DMA policy, memory-power modes, clock-gate disables, soft-reset control bits, and endpoint/stream index selections.
- Transactional or handshake state: DCHUBBUB watermark change request/done/status, WBIF watermark change request/status, surface flip request/ack/pending, interrupt clear/status bits, warmup interrupt status/ack, timeout clear, VM fault clear, CRC sample/reset controls, and memory-power force/disable transitions.
- Captured or sampled status: outstanding counters, VM fault VMID/table/pipe/address, force-IO address/request type, CRC result values, DCC statistics, surface-in-use addresses, pipe read-line snapshots, MALL prefetch complete, ROB overflow, FMON state, pstate/self-refresh permissions, and HUBPREQ status registers.
- Power-management state: multiple blocks expose paired `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` fields. Driver writes force/disable/mode bits and polls or reads state bits for MMHUBBUB, Azalia, SDPIF, return path, compbuf/DET, HUBPREQ, and HUBPRET memories.

Because this is a hardware register contract, incorrect constants can be persistent at runtime even though the macros themselves are static. A wrong mask or shift can cause the driver to preserve, clear, or set the wrong MMIO bits until the affected block is reset or reprogrammed.

## Dependencies

Direct dependencies and pairings:

- The matching offset header `dcn_3_2_1_offset.h` provides register addresses and base-index information. This file provides the field layout for those addresses.
- AMD Display Core register helpers (`reg_helper.h` and related macros) consume shift/mask pairs to compose writes and extract readback fields.
- DCN321 resource construction in `display/dc/resource/dcn321/dcn321_resource.c` includes this header and passes generated tables into hubbub, HUBP, audio, DWB, MMHUBBUB, timing, stream, and encoder-related block constructors.
- Shared DCN32/DCN30/DCN20 implementations consume these tables because DCN321 reuses many common block implementations while providing chip-specific register offsets and field masks.
- Hardware semantics come from DCN 3.2.1 display IP: DCHUBBUB, HUBP/HUBPREQ/HUBPRET, MMHUBBUB/WBIF, Azalia HDA, SDPIF, and VM request interfaces.

## Integration Points

- DCN321 device bring-up: `amdgpu_dm.c` selects `DMUB_ASIC_DCN321`, and `dc_resource.c` creates the DCN321 resource pool, which includes this header through `dcn321_resource.c`.
- HUBBUB and VMID: `dcn321_hubbub_create()` initializes DCHUBBUB and VMID register/shift/mask tables, including the DCHUBBUB arbitration/VM/fault fields in this chunk.
- HUBP0 request pipeline: `dcn321_hubp_create()` initializes HUBP instances. The HUBP0/HUBPREQ0/HUBPRET0 fields in this chunk are the instance-0 template for surface fetch and timing behavior; generated macro-list patterns commonly replicate these for other instances through offset/header conventions.
- Audio: `dcn321_create_audio()`, AFMT, VPG, APG, and stream encoder creation use audio-related register tables. The Azalia and audio codec macros here are the low-level HDA field definitions for display audio paths.
- Writeback/MMHUBBUB: `dcn321_dwbc_create()` and `dcn321_mmhubbub_create()` construct writeback and MMHUBBUB objects using generated register fields such as WBIF, MCIF/WB, MMHUBBUB warmup, watermark, and memory-power controls.
- Diagnostics and recovery: VM fault, timeout, CRC, DCC, force-IO, outstanding counter, and interrupt status fields provide observable signals for debugfs, driver logs, hardware recovery paths, and bring-up validation.

## Risks

- Generated-header drift: This file must match the actual DCN 3.2.1 register specification and `dcn_3_2_1_offset.h`. A mismatch can silently program the wrong bits.
- Cross-version confusion: Many names are similar to DCN 3.2.0 and later DCN 3.5.x headers, but fields can diverge. Copying masks between ASIC generations risks invalid programming.
- Read-modify-write hazards: A wrong mask can clobber adjacent control bits, especially in dense registers such as `DCHUBBUB_ARB_DRAM_STATE_CNTL`, `HUBPREQ0_DCSURF_SURFACE_CONTROL`, `HUBPREQ0_DCSURF_FLIP_CONTROL`, `DCHUBBUB_CRC_CTRL`, and Azalia memory-power controls.
- Interrupt and clear-bit semantics: Registers with `*_CLEAR`, `*_ACK`, `*_STATUS`, and `*_INT_STATUS` fields may use write-one-to-clear or sticky semantics. Treating them as ordinary persistent fields can lose interrupts or leave stale status asserted.
- VM and fault containment: VM context, aperture, default address, and fault-disable fields affect display memory translations. Incorrect settings can produce blank scanout, GPU page faults, or reads from unintended physical ranges.
- Power and clock gating: MMHUBBUB, DCHUBBUB, HUBP, HUBPREQ, HUBPRET, SDPIF, Azalia, and WBIF power/clock fields can gate required memories or clocks. Bad programming may surface as hangs, underruns, audio dropouts, timeout interrupts, or failed flips.
- Timing sensitivity: Watermark, TTU, prefetch, pstate, and per-line delivery fields interact with display mode timing. Incorrect values may pass compile tests but fail under high bandwidth, multi-plane, MALL, self-refresh, or pstate-transition workloads.
- Repeated index/data windows: Azalia stream/endpoint macros are repetitive. Off-by-one instance use can route programming to the wrong audio stream or endpoint without compiler diagnostics.

## Test Signals

Useful validation signals for changes involving this chunk:

- Build coverage: compile AMDGPU/DC with DCN321 enabled; missing or renamed macros should fail at compile time in `dcn321_resource.c` or shared DCN block code.
- Register table sanity: compare generated shift/mask entries against `dcn_3_2_1_offset.h` and the ASIC register source used to generate both files.
- Boot/probe: verify DCN321 hardware initializes the resource pool, creates hubbub, HUBP, audio, DWB, and MMHUBBUB objects, and reaches display modeset without register access faults.
- Display modes: exercise single and multi-plane scanout, rotation/mirroring/alpha plane, luma/chroma formats, DCC/meta surfaces, cursor, page flips, vblank, and read-line interrupts.
- Memory and VM: test VMID context programming, GPUVM/system aperture modes, fault reporting, force-IO status capture, and fault interrupt clear/status paths.
- Power management: test MALL, self-refresh, UCLK/FCLK pstate transitions, clock gating, memory power collapse/restore, warmup, and writeback watermark changes while watching timeout, ROB overflow, underrun, and flip status fields.
- Audio: test DP/HDMI audio stream creation, endpoint routing, HBR/compressed channel counts, audio DTO programming, DMA snoop/isochronous settings, and CRC/underflow diagnostics.
- Diagnostics: read CRC results, DCC stats, DCHUBBUB performance counters, FMON state, outstanding counters, surface-in-use addresses, and HUBPREQ status under active scanout to confirm masks extract plausible non-stuck values.
