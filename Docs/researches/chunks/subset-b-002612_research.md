# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h lines 1-2509

## Scope

This chunk is the first segment of the generated AMD GC 9.0 register offset header. It contains the MIT license, the `_gc_9_0_OFFSET_HEADER` include guard, and C preprocessor constants mapping GC 9.0 hardware register names to register offsets. Each visible register offset is paired with a `<REGISTER>_BASE_IDX` macro, almost always `0`, for use by SOC15 register-address construction helpers.

The selected range covers 1,210 non-`_BASE_IDX` register offset macros from `0x0000` through `0x1089`. It starts with top-level SQ debug status aliases before the first address-block comment, then spans these address blocks: `gc_grbmdec`, `gc_cpdec`, `gc_padec`, `gc_sqdec`, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, `gc_rbdec`, `gc_ea_gceadec2`, `gc_rmi_rmidec`, `gc_utcl2_atcl2dec`, `gc_utcl2_vml2pfdec`, `gc_utcl2_vml2vcdec`, `gc_utcl2_vmsharedpfdec`, `gc_utcl2_vmsharedvcdec`, `gc_tcdec`, `gc_shdec`, and the start of `gc_cppdec`. The chunk ends mid-`gc_cppdec` at `mmCP_ME2_PIPE0_INT_CNTL`; later CP interrupt/status and ring-management macros continue in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata, not distributed filesystem logic.

## Purpose

`gc_9_0_offset.h` provides the register-address side of the GC 9.0 hardware definition. Driver code uses these `mm...` macros to form MMIO addresses, indexed-register offsets, and PM4 packet payloads for graphics, compute, memory-translation, cache, render-backend, and command-processor programming. Companion generated headers provide field masks/shifts and defaults; this file only identifies where each register lives.

This chunk covers the early GC 9.0 control surface:

- GRBM global control, status, soft reset, trap, scratch, power, read/write-error, RSMU, UTCL2 invalidation range, and shader-engine status registers.
- CP/CPC/CPF command-processor status, queue availability, ring-buffer pointers, instruction pointers, preemption/status counters, queue thresholds, and debug/stat registers.
- PA/VGT/WD front-end and rasterization-related controls, cache invalidation, primitive/shader-array configuration, DMA state, binner/performance controls, FIFO sizing, and UTCL1 status.
- SQ/SQC shader-core configuration, LDS/shared-memory settings, exception/debug controls, instruction/data-cache controls, thread trace words, EDC counters, resource descriptor words, scratch words, and UTCL1 controls.
- SPI/SX shader interpolator/export state, wave lifetime counters, CU masks, load-balancer data, trap-screen addresses, GDS credits, and shader-array debug state.
- Texture/TA/TD, GDS, DB/CB/GB render backend, RMI, ATC L2, VM L2, VM context, shared aperture, TCP/TCI/TCC/TCA cache, graphics shader-stage, compute dispatch, and start-of-CP ring/doorbell/interrupt registers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime variables in this chunk. Its public interface is the generated macro contract:

- `mm<REGISTER>` expands to a numeric GC 9.0 register offset.
- `mm<REGISTER>_BASE_IDX` identifies the SOC15 base index used by helpers that combine an IP block, instance, and register offset.
- Address-block comments preserve the generating register database's block names and base addresses. They are useful when reconciling offsets with hardware manuals or other generated IP-version headers.
- Several aliases intentionally map different legacy or semantic names to the same offset. Examples in this chunk include `mmCP_RB_RPTR` and `mmCP_RB0_RPTR`, `mmCP_RB_BASE` and `mmCP_RB0_BASE`, `mmCP_RING_PRIORITY_CNTS` and `mmCP_ME0_PIPE_PRIORITY_CNTS`, plus many thread-trace word aliases at `0x03b0` and `0x03b1`.

Typical consumers include `gfx_v9_0.c`, `soc15.c`, `gfxhub_v1_0.c`, PSP setup files, KFD GC 9 code, virtualization support, and power-management include paths. The macros are commonly passed to `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `SOC15_REG_ENTRY_STR`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_GOLDEN_VALUE`, and PM4 packet emission code.

## Control Flow

The header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU is:

1. Select GC 9.0 register headers for an ASIC using that graphics IP version.
2. Use an `mm...` macro and its base index to build a concrete register address for MMIO, indexed access, or command-stream programming.
3. Combine the address macro with field masks/shifts from the matching `gc_9_0_sh_mask.h` header when modifying individual fields.
4. Read, write, poll, or emit the register as part of device initialization, ring setup, VM setup, graphics/compute dispatch, interrupt handling, reset, suspend/resume, debug dumps, or KFD queue management.

The file itself does not encode sequencing requirements. For example, programming VM invalidation request/ack registers, CP ring base/write-pointer registers, cache invalidation registers, or shader program addresses requires ordering, waits, and field packing supplied by driver code and the hardware programming model.

## State And Persistence Behavior

The macros are stateless and persist nothing. The hardware registers they identify are stateful, and their lifetime depends on the block:

- GRBM, GB, DB, CB, TC, ATC, RMI, and power/clock registers represent global or per-IP hardware state normally initialized at device bring-up and restored after reset or power transitions.
- CP ring-buffer, doorbell, interrupt, VMID, priority, and active-status registers bind driver-managed ring objects and doorbell ranges to hardware queue execution. Stale values can redirect command fetching or break interrupt delivery.
- VM context and VM invalidation registers persist address-space configuration, page-table ranges, fault reporting, invalidate request/ack state, and shared aperture settings. These must stay synchronized with GPUVM and KFD memory-management state.
- Shader-stage and compute registers describe program addresses, resource limits, user-data registers, thread geometry, scratch dispatch addresses, and wave restore state. These are context or dispatch state and may be emitted through command streams rather than simple MMIO writes.
- Debug, EDC/ECC, trap, performance, and status registers may be read-only, sticky, clear-on-write, write-one-to-clear, or diagnostic-only depending on the specific register. This header does not identify those access semantics.

Because offsets are raw hardware contract data, incorrect persistence handling is usually a consumer bug rather than a header behavior. Still, a wrong offset in this file can make otherwise correct save/restore or polling code operate on the wrong register.

## Dependencies And Integration Points

This chunk depends on the rest of the GC 9.0 generated register set staying consistent:

- `gc_9_0_sh_mask.h` supplies bit fields for the same register names.
- `gc_9_0_default.h`, where present, supplies default values for many of the same registers.
- SOC15 register helpers translate `(IP block, instance, base index, offset)` into actual MMIO addresses.
- PM4 packet builders use these offsets when emitting SET registers or command processor setup packets.
- AMDGPU ring, VM, GFX, CP, PSP, KFD, virtualization, reset, debugfs, and power-management code all assume these offsets match the hardware database.

Integration points visible from repository searches include GC 9 includes in `gfx_v9_0.c`, `soc15.c`, `gfxhub_v1_0.c`, PSP v3/v11/v12 files, KFD GC 9 MQD management, SR-IOV/MxGPU support, Arcturus KFD code, and Vega powerplay includes. Common direct uses include GRBM status polling, `GB_ADDR_CONFIG` golden settings and reads, CP ring base/pointer setup, compute shader PM4 test packets, VM context programming, and debug register lists.

## Risks And Edge Cases

- Generated-header drift is the main risk. A single wrong offset can compile cleanly but cause MMIO writes or PM4 packets to touch unrelated hardware state, leading to GPU hangs, bad page faults, corrupted render/compute output, or broken interrupts.
- The chunk contains many repeated register families: VM contexts 0-15, invalidation engines 0-17, shader user-data slots, CP rings 0-2, compute user-data slots, tile modes, and wave lifetime/status counters. Off-by-one generator errors in these sequences can affect only one queue, VM context, shader stage, or engine.
- Aliased macros are intentional compatibility and naming surfaces. Removing or "deduplicating" aliases such as `mmCP_RB_BASE`, `mmCP_RB0_BASE`, `mmCP_RING0_PRIORITY`, or thread-trace word aliases can break consumers that use a different naming convention for the same offset.
- The chunk ends in the middle of the `gc_cppdec` address block. Final per-file research must merge adjacent chunks to capture the complete CP interrupt/status and ring-control register family.
- The `_BASE_IDX` value is part of the SOC15 address contract. Assuming all future or adjacent headers use the same base index can break multi-base IP blocks, even though this range mostly uses `0`.
- Register names alone do not communicate access permissions, reset values, reserved-bit policy, or whether read-modify-write is safe. Consumers need the matching field/default headers and hardware programming rules.
- VM, ATC/TCC/TCP cache, and invalidation registers are ordering-sensitive. Correct offsets are necessary but not sufficient; callers must still issue required waits, flushes, acknowledgements, and range programming.
- CP ring and doorbell registers carry GPU addresses, queue ownership, and interrupt routing. Width, alignment, and high/low register pairing mistakes around these offsets can cause command fetch from the wrong memory or missed fence completion.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware exercise:

- Kernel build coverage for AMDGPU and KFD code paths that include `gc_9_0_offset.h`, especially `gfx_v9_0.c`, `gfxhub_v1_0.c`, `soc15.c`, PSP setup, and KFD MQD management.
- Mechanical comparison against AMD's authoritative GC 9.0 register database for every `mm...` offset and `_BASE_IDX` pair in lines 1-2509.
- Cross-checks that registers in this chunk have matching shift/mask definitions and defaults where those companion headers generate them.
- Static checks for repeated families: VM context ranges, VM invalidate engine request/ack/address ranges, CP ring aliases, shader user-data sequences, compute dispatch registers, tile-mode arrays, and thread-trace aliases.
- Runtime smoke tests that initialize GC 9 hardware, submit graphics and compute rings, program CP ring buffers and doorbells, dispatch compute shaders, reset the GPU, suspend/resume, and poll GRBM idle/status registers.
- GPUVM and KFD tests that exercise VM context setup, page-table base/start/end ranges, invalidate request/ack handling, dummy/protection fault reporting, PASID/VMID state, and shared aperture registers.
- Rendering and compute correctness tests that cover shader program address programming, user-data upload, scratch/tmp ring setup, TC/TCC cache invalidation, render-backend configuration, GDS, and EDC/ECC reporting paths.
- Diagnostic signals include hangs during ring bring-up, GRBM never-idle polling, failed VM invalidation acknowledgements, page faults with implausible addresses, missing CP interrupts, broken doorbells, bad shader dispatch packets, or failures isolated to one VM context, invalidation engine, ring, or shader stage.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002612`. It covers lines 1-2509 of `gc_9_0_offset.h`; the final per-file document should merge it with following chunks to complete `gc_cppdec` and the remaining GC 9.0 register address space.
