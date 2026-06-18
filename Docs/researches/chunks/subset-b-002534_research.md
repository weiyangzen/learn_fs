# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 19694-22207

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask register-header segment. It contains preprocessor constants only. Each hardware register field is represented by a `__SHIFT` value and a corresponding `_MASK` value so AMDGPU code can pack and extract 32-bit MMIO, indexed-register, or command-stream register values without hard-coding bit positions.

The requested range contains 2,153 `#define` entries: 1,077 `__SHIFT` constants and 1,076 `_MASK` constants. The mismatch comes from chunk boundaries, not from a semantic register layout: the first line is the final `CP_HQD_IQ_TIMER__ACTIVE_MASK` from a register whose shift definitions are in the previous chunk, and the last line stops inside `PA_SC_VPORT_SCISSOR_9_TL` before its remaining masks.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics-core metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_11_0_3_sh_mask.h` supplies field bit layouts for GC 11.0.3 graphics hardware. Driver code pairs these macros with register offsets from `gc_11_0_3_offset.h` and uses helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` to build or decode register values.

This chunk covers several register families:

- CP HQD/MQD queue metadata for compute queues, including dequeue requests/status, IQ/EOP pointers, offload controls, semaphore messages, MQD control, EOP ring base/control, context-save layout, GDS resource state, AQL controls, PQ write pointer state, suspend-state offsets, DDID counters, and HQD error flags.
- TCP address-watch registers, with four `TCP_WATCHn` slots that split watched addresses into high/low pieces and expose mask, VMID, mode, and valid bits.
- GDS/GWS/OA state, including per-VMID GDS base/size partitions, per-VMID GWS and OA resource ownership, GWS reset masks for resources 0-63, targeted GWS/OA resets, maximum compute wave id, GDS memory-clean control, and context-switch counters/status for CS, GFX, PS, and GS clients.
- RAS signature registers for SX, DB, PA, SC, SPI, CB, and BCI blocks, plus signature control and mask fields.
- GUS arbitration, QoS, credits, counters, and error/status state for IO read/write paths, DRAM paths, SDP links, latency sampling, L1 channel/shader-array counters, FP atomic logging, and write-response FIFO thresholding.
- The beginning of the `gc_gfxdec0` graphics state block, including DB render/depth/stencil/HTILE state, PA screen/window/generic/viewport scissor rectangles, clip rectangles and edge rules, CB target/shader masks, coherency destination bases, and early viewport scissor entries.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or executable branches in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register value.
- Matching register addresses live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`.
- AMDGPU code usually consumes the macros through `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `WREG32*`, `RREG32*`, and command-packet/state-emission helpers.

Important field groups in this chunk include:

- `CP_HQD_DEQUEUE_REQUEST`, `CP_HQD_DEQUEUE_STATUS`, `CP_HQD_EOP_RPTR`, `CP_HQD_EOP_WPTR`, `CP_HQD_EOP_CONTROL`, and `CP_HQD_ERROR`: queue dequeue, suspend, EOP ring, fetcher, semaphore, and per-path error status fields.
- `CP_MQD_CONTROL`, `CP_HQD_CTX_SAVE_*`, `CP_HQD_CNTL_STACK_*`, `CP_HQD_WG_STATE_OFFSET`, and `CP_HQD_SUSPEND_*`: queue descriptor, context-save, control-stack, workgroup-state, and suspend-state layout fields.
- `TCP_WATCH0_*` through `TCP_WATCH3_*`: four address-watch slots with address, mask, VMID, mode, and valid fields. `amdgpu_amdkfd_gfx_v11.c` uses these names when programming address watches for KFD debugging.
- `GDS_VMID0_BASE/SIZE` through `GDS_VMID15_BASE/SIZE`, `GDS_GWS_VMID0` through `GDS_GWS_VMID15`, and `GDS_OA_VMID0` through `GDS_OA_VMID15`: per-VMID GDS, GWS, and ordered-append allocation metadata.
- `GDS_GWS_RESET0`, `GDS_GWS_RESET1`, `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, and `GDS_OA_RESET`: resource and pipe reset controls.
- `GUS_IO_*`, `GUS_DRAM_*`, `GUS_SDP_*`, `GUS_MISC*`, `GUS_LATENCY_SAMPLING`, `GUS_ERR_STATUS`, and `GUS_L1_*`: memory-system arbitration/QoS, combining, fixed/aging/queuing/urgency coefficients, group bursts, SDP credit/reserve controls, error reporting, and per-channel/per-shader-array counters.
- `DB_RENDER_CONTROL`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_DEPTH_VIEW`, `DB_Z_INFO`, `DB_STENCIL_INFO`, and DB base/clear registers: depth/stencil/HTILE render-state and metadata fields.
- `PA_SC_*`, `PA_SU_HARDWARE_SCREEN_OFFSET`, `CB_TARGET_MASK`, `CB_SHADER_MASK`, and `COHER_DEST_BASE_*`: graphics setup, clipping/scissor, render target write mask, shader output mask, and coherency destination state.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU and KFD consumers:

1. Select GC 11.0.3 register definitions for the active ASIC.
2. Pair a register address from `gc_11_0_3_offset.h` with a field macro from this header.
3. Use `REG_SET_FIELD` or related helpers to compose a register value, or `REG_GET_FIELD` to decode saved hardware state.
4. Write/read the value through MMIO helpers, indexed register paths, RLC-safe accessors, or command-stream packets as part of queue setup, debug-watch programming, reset, context switch, render-state emission, or diagnostics.

For CP queue state, higher-level code chooses an MQD/HQD slot, writes descriptor and HQD registers, activates doorbell/pointer handling, and requests dequeue/suspend/resume through CP registers. For TCP watches, KFD debug code builds `TCP_WATCH0_CNTL` fields and writes the per-watch address registers using a stride between watch slots. For DB/PA/CB graphics state, command-stream producers or clear-state tables provide the sequencing; this file only names the bit layout.

The file does not encode ordering constraints, wait loops, cache flushes, W1C behavior, read-only/write-only semantics, or hardware side effects. Those semantics are owned by the surrounding AMDGPU code and the hardware programming guide.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- HQD/MQD queue state persists in CP queue registers and/or MQD save areas until overwritten, saved/restored, dequeued, suspended, reset, or lost across power/reset events.
- EOP, IQ, PQ, DDID, and context-save pointer fields represent ring/counter positions or memory offsets. Some are software-programmed, some are hardware-updated, and some are status or control bits around fetcher/dequeue activity.
- TCP watch registers are debug state scoped by watch slot and VMID. The address low field starts at bit 7, so callers must honor address alignment and mask shifting.
- GDS/GWS/OA registers describe partitioning and ownership for VMIDs and engine clients. Reset and clean registers have side effects; status/counter registers can change as queues and shader stages run.
- GUS QoS/arbitration registers tune memory fabric behavior, while error/status, latency sampling, credit, and L1 count registers are observational or diagnostic hardware state.
- DB/PA/CB graphics registers are context state for depth/stencil rendering, HTILE metadata, scissor/clip bounds, viewport state, and render-target write masks. They persist until replaced by later command packets, context restore, clear-state initialization, reset, or suspend/resume reprogramming.

Reserved or `UNUSED` fields appear throughout the range. Callers should preserve them on read-modify-write unless a documented full-register value is being emitted.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which supplies the matching register offsets. This shift/mask header must remain synchronized with that offset header and AMD's authoritative GC 11.0.3 register database.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`, which include the GC 11.0.3 offset and shift/mask headers for this ASIC generation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`, which programs HQD/MQD queue state and uses `TCP_WATCH0_CNTL` field macros for KFD address-watch setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v11_api_def.h` and `mes_v12_api_def.h`, which carry MES queue/context structures with fields corresponding to TCP watch controls and queue state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx11.h`, which contains default graphics clear-state values for DB render control and PA viewport scissor registers represented in this chunk.
- Common AMDGPU register helpers and SOC15 addressing macros, which perform the actual packing, unpacking, and MMIO/command-stream access.

Behaviorally, the chunk sits at the boundary between kernel queue management, KFD debugging, low-level GDS/GWS resource management, memory-fabric diagnostics/tuning, and graphics render-state programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask will compile cleanly but write or read the wrong hardware bits.
- The range starts and ends mid-register-family. File-level research must merge adjacent chunks before making complete claims about `CP_HQD_IQ_TIMER` or `PA_SC_VPORT_SCISSOR_9_TL`.
- HQD/MQD fields are queue-liveness sensitive. Incorrect dequeue, suspend, EOP, fetcher, PQ, or context-save masks can cause queue hangs, failed preemption, lost completions, bad user-mode queue restore, or invalid memory fetches.
- Address fields often have implicit alignment or unit semantics. Examples include `CP_HQD_CTX_SAVE_BASE_ADDR_LO__ADDR` starting at bit 12, `TCP_WATCHn_ADDR_L__ADDR` starting at bit 7, `DB_HTILE_DATA_BASE__BASE_256B`, and `COHER_DEST_BASE_*__DEST_BASE_256B`.
- TCP watch slot repetition is copy-sensitive. A single watch-slot layout or stride mismatch can break KFD watchpoints only for specific watch IDs.
- GDS/GWS/OA reset and ownership fields can affect inter-queue isolation. Bad VMID base/size, GWS resource, OA resource, or reset masks can leak resources between processes or cause CP GDS allocation errors.
- GUS arbitration/QoS fields can create subtle performance and fairness regressions rather than immediate failures. Bad priority, urgency, credit, or combine-flush definitions may only show under mixed graphics/compute/memory pressure.
- Error/status fields such as `CP_HQD_ERROR`, `GUS_ERR_STATUS`, and RAS signatures can be latched, clear-on-write, or otherwise access-sensitive. The generated masks do not distinguish those semantics.
- DB depth/stencil and HTILE fields interact with compression metadata, cache/coherency protocols, and render state. Wrong masks can present as depth corruption, incorrect fast clears, hangs during decompression/resummarize, or broken read-only depth/stencil views.
- Scissor, cliprect, viewport, and screen/window offset fields are repeated and coordinate-packed. Sign, range, and high-bit mistakes can cause clipped rendering or viewport-specific corruption.
- `CB_TARGET_MASK` and `CB_SHADER_MASK` are packed nibbles for eight targets/outputs. Mispacking can silently drop color channels or write unexpected MRT outputs.

## Test Signals

Useful validation should combine build coverage, generated-data checks, and runtime hardware tests:

- Build AMDGPU with GC 11 support and KFD enabled. Missing or renamed macros should surface in GC 11.0.3 include users, KFD queue/debug code, and common register-helper call sites.
- Mechanically compare this range against the authoritative GC 11.0.3 register database. Check that each complete register in the range has matching `__SHIFT` and `_MASK` entries and that repeated families are structurally consistent.
- Cross-check every register family in this chunk against `gc_11_0_3_offset.h` for matching `reg*` or `mm*` offset definitions.
- Run static mask sanity checks: masks should align with shifts, full-width fields should use `0xFFFFFFFFL`, repeated `GDS_VMIDn`, `GDS_GWS_VMIDn`, `GDS_OA_VMIDn`, `TCP_WATCHn`, `GUS_IO_RD/WR`, and `PA_SC_VPORT_SCISSOR_n` layouts should match expected repetition.
- Exercise KFD queue creation, restore, suspend/preemption, dequeue, and teardown paths. Watch for stuck HQDs, EOP pointer mismatches, failed dequeue status transitions, CP HQD error bits, and GPU reset recovery failures.
- Exercise KFD debugger address watches across all four watch IDs, different VMIDs, aligned and boundary addresses, and watch modes. Expected signals are correct traps and no cross-VMID/watch-slot aliasing.
- Run compute workloads that use GDS/GWS/OA resources and context switching, including multi-process VMID pressure. Watch for `CP_GDS_ALLOC_ERROR`, bad resource cleanup, or incorrect GDS memory-clean completion.
- Run mixed graphics/compute memory-pressure tests and inspect GUS/SDP/GUS_ERR_STATUS diagnostics. Performance regressions, fabric errors, credit stalls, or parity/FUE flags are relevant signals.
- Run depth/stencil, HTILE, depth bounds, fast-clear/decompress/resummarize, Z/stencil read-only, and MSAA depth tests to exercise DB fields in this chunk.
- Run viewport/scissor/cliprect/MRT color-mask rendering tests across multiple viewports and render targets. Expected signals include correct per-target channel masks, correct shader output masking, and no off-by-one or window-offset clipping errors.
- Compare graphics clear-state register dumps against `clearstate_gfx11.h` expectations for DB render control and PA viewport scissor defaults after init/reset.

## Cross-Chunk Notes

The previous chunk owns most of `CP_HQD_IQ_TIMER`; this chunk begins with only `CP_HQD_IQ_TIMER__ACTIVE_MASK`. This chunk then covers complete CP HQD/MQD, TCP watch, GDS/GUS/RAS, and early gfx DB/PA/CB groups until it stops inside `PA_SC_VPORT_SCISSOR_9_TL`. The next chunk should complete that viewport scissor register and continue the remaining viewport/scissor and graphics state metadata. The final per-file research document should reconcile these artificial boundaries before describing the full GC 11.0.3 shift/mask header.
