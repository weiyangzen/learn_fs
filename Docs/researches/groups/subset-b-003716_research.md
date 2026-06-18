# subset-b-003716 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik.h

## Purpose
`cik.h` is a small private CIK-family Radeon driver interface header. It forward-declares `struct radeon_device` and exposes cross-file entry points for CIK RLC safe mode, memory-controller firmware loading, clock-gating updates, soft-reset probing, command-submission buffer setup, and SDMA lifecycle control.

## Important APIs, types, and dependencies
- Depends on external Radeon core definitions for `struct radeon_device`, `u32`, and `bool`; this file deliberately avoids including the larger driver headers.
- RLC and command-submission APIs: `cik_enter_rlc_safe_mode`, `cik_exit_rlc_safe_mode`, `cik_init_cp_pg_table`, `cik_get_csb_size`, and `cik_get_csb_buffer`.
- Firmware and reset APIs: `ci_mc_load_microcode` and `cik_gpu_check_soft_reset`.
- Power/clock API: `cik_update_cg`.
- SDMA APIs implemented in `cik_sdma.c`: `cik_sdma_resume`, `cik_sdma_enable`, and `cik_sdma_fini`.

## Control flow and integration points
This header is not executable logic; it is an internal contract consumed by CIK ASIC setup, reset, power-management, command-processor, and SDMA code. Callers use these prototypes during device initialization/resume, clock-gating transitions, GPU reset detection, and teardown.

## State and persistence behavior
The file owns no state. The declared functions mutate persistent hardware and driver state through `struct radeon_device`, including RLC mode, microcode-resident controller state, clock-gating registers, command-submission buffers, and SDMA rings.

## Risks and test signals
Prototype drift is the main risk: mismatched definitions or missing declarations break C builds across the Radeon CIK implementation. Runtime validation comes indirectly from CIK device probe/resume, soft-reset paths, SDMA ring/IB tests, command submission, suspend/resume, and clock-gating smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_blit_shaders.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_blit_shaders.h

## Purpose
`cik_blit_shaders.h` provides a static CIK default GPU context-state command stream used by the Radeon blit path. The `cik_default_state` array is encoded as PM4-style register write packets, primarily `PACKET3_SET_CONTEXT_REG`-class headers (`0xc0xx6900`) followed by register offsets and default values for depth, rasterizer, viewport, vertex, blend, shader, and anti-aliasing state.

## Important APIs, types, and data
- `static const u32 cik_default_state[]`: a contiguous command buffer that programs default render state such as `DB_RENDER_CONTROL`, `PA_SC_CLIPRECT_*`, `PA_SC_VPORT_SCISSOR_*`, `VGT_*`, `CB_BLEND*`, `DB_DEPTH_CONTROL`, `CB_COLOR_CONTROL`, `PA_CL_*`, `PA_SU_*`, `PA_SC_*`, and `DB_ALPHA_TO_MASK`.
- `static const u32 cik_default_size = ARRAY_SIZE(cik_default_state)`: compile-time size used by consumers when copying/emitting the state.
- Depends on `u32`, `ARRAY_SIZE`, and packet/register definitions supplied by the including Radeon translation unit.

## Control flow and integration points
The file contains no functions. Consumers include it and emit/copy the static dword stream into a ring, IB, or driver-owned state buffer before CIK blit operations so a known graphics context exists. The encoded sequence walks register ranges in contiguous extents, reducing per-register command overhead.

## State and persistence behavior
The header itself is immutable static data. When emitted to hardware, it overwrites GPU context registers with deterministic defaults. That state persists in the GPU context until later command streams change it or a hardware context reset occurs.

## Dependencies and constraints
The array depends on exact CIK register ordering and packet encoding. The values assume expected CIK context-register offsets and field semantics from `cikd.h` and related Radeon packet helpers. Alignment and count values in the packet headers must match the number of following dwords.

## Risks and test signals
Risks include silent GPU hangs or rendering/copy corruption if any packet count, register offset, or default value is wrong. Test signals include blit/copy correctness, GPU ring progress after default-state emission, absence of command-processor faults, and suspend/resume or reset paths that rebuild default state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_blit_shaders.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_reg.h

## Purpose
`cik_reg.h` defines a focused set of CIK register addresses, bitfields, and helper constants used by Radeon display, debug/watchpoint, interrupt, and SDMA queue code. It is narrower than `cikd.h`, concentrating on display scanout/cursor programming, SQ/TCP watch registers, CPC/HQD/SDMA RLC queue registers, and address-watch control packing.

## Important APIs, types, and definitions
- Display and cursor registers: `CIK_GRPH_CONTROL` with depth, bank, tiling, pipe, and pixel-format helpers; `CIK_CUR_*` cursor address, size, position, hotspot, color, and update registers; `CIK_ALPHA_CONTROL`, `CIK_LB_DATA_FORMAT`, and `CIK_LB_DESKTOP_HEIGHT`.
- Debug/watch registers: `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_CMD`, `TCP_WATCH{0..3}_ADDR_{H,L}`, and `TCP_WATCH{0..3}_CNTL`.
- Interrupt and queue registers: `CPC_INT_CNTL`, `CP_HQD_IQ_RPTR`, and `SDMA0_RLC0_*` queue registers, plus `SDMA0_CNTL` and `SDMA1_CNTL`.
- Enumerations define maximum trap/watch resources and address-watch register slots.
- `union TCP_WATCH_CNTL_BITS` packs watchpoint mask, VMID, ATC, mode, and valid fields over a 32-bit register value.

## Control flow and integration points
This header does not execute control flow. Driver code uses these constants to build MMIO register reads/writes, compose display surface configuration, control cursor updates, program address watchpoints, and configure SDMA RLC queue state.

## State and persistence behavior
All state lives in hardware registers. Writes using these definitions persist in display engines, watchpoint logic, or SDMA queue registers until overwritten, reset, or power-gated. The `TCP_WATCH_CNTL_BITS` union is a transient CPU-side representation used to compose or inspect a register value.

## Dependencies and constraints
The file assumes Linux-style integer types (`uint32_t`) and Radeon MMIO accessors in consumers. Several helpers mask and shift user-provided values; callers must still provide values legal for the active ASIC and display mode. TCP watch addresses are documented as dword addresses multiplied by four, a detail callers must preserve.

## Risks and test signals
Incorrect field definitions can corrupt scanout format, cursor updates, debugger watchpoints, or queue setup. Test signals include modeset/cursor tests, KFD or debugger watchpoint validation, SDMA queue bring-up, register readback comparisons, and absence of page faults or display underruns after programming these registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_sdma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_sdma.c

## Purpose
`cik_sdma.c` implements the CIK System DMA engine support for the Radeon driver. CIK exposes two SDMA engines used for asynchronous graphics DMA and compute queues. This file handles SDMA ring pointer access, IB execution, fence/semaphore packets, engine stop/start, microcode loading, copy acceleration, ring and IB self-tests, lockup detection, VM page-table updates, and VM TLB flushing.

## Important APIs and functions
- Ring pointer operations: `cik_sdma_get_rptr`, `cik_sdma_get_wptr`, and `cik_sdma_set_wptr` read/write hardware or writeback-backed ring pointers for `R600_RING_TYPE_DMA_INDEX` and `CAYMAN_RING_TYPE_DMA1_INDEX`.
- Submission helpers: `cik_sdma_ring_ib_execute` pads to SDMA alignment and emits an `SDMA_OPCODE_INDIRECT_BUFFER`; `cik_sdma_fence_ring_emit` writes a fence, traps for interrupt generation, and emits an HDP flush; `cik_sdma_semaphore_ring_emit` emits wait/signal semaphore packets.
- Lifecycle: `cik_sdma_enable`, `cik_sdma_resume`, and `cik_sdma_fini` halt/unhalt engines, load firmware, initialize rings, test them, and tear them down.
- Internal setup: `cik_sdma_gfx_stop`, `cik_sdma_gfx_resume`, `cik_sdma_ctx_switch_enable`, `cik_sdma_load_microcode`, plus placeholder compute queue functions `cik_sdma_rlc_stop` and `cik_sdma_rlc_resume`.
- Copy and tests: `cik_copy_dma`, `cik_sdma_ring_test`, `cik_sdma_ib_test`, and `cik_sdma_is_lockup`.
- VM helpers: `cik_sdma_vm_copy_pages`, `cik_sdma_vm_write_pages`, `cik_sdma_vm_set_pages`, `cik_sdma_vm_pad_ib`, and `cik_dma_vm_flush`.

## Control flow
Resume loads SDMA microcode, enables both engines, initializes both graphics rings, and runs `radeon_ring_test` per ring. Ring setup programs semaphore timers, ring buffer size, read/write pointers, writeback address, base address, and IB enable bits before marking a ring ready. Stop disables RB/IB control, marks rings not ready, and uses an SDMA soft reset as a hibernation workaround. Copy and VM functions fill ring/IB dwords with SDMA packet sequences, then emit fences or pad IBs as required.

## State and persistence behavior
The file mutates persistent hardware state in SDMA registers (`SDMA0_*` plus `SDMA1_REGISTER_OFFSET`), microcode memory, ring buffer pointers, writeback slots, fence memory, VM context registers, and TLB invalidation registers. Driver state is updated in `rdev->ring[]`, `rdev->wb`, `rdev->fence_drv[]`, and synchronization structures. SDMA firmware is loaded from `rdev->sdma_fw`; both legacy big-endian blobs and newer firmware headers are supported.

## Dependencies and integration points
Includes `radeon.h`, `radeon_ucode.h`, `radeon_asic.h`, `radeon_trace.h`, `cik.h`, and `cikd.h`. It relies on Radeon ring, IB, fence, sync, TTM, VM, writeback, and MMIO helpers such as `radeon_ring_write`, `radeon_ring_lock`, `radeon_fence_emit`, `radeon_ib_schedule`, `RREG32`, and `WREG32`. It integrates with the ASIC copy callback through `cik_copy_dma` and with VM management through SDMA page-table update helpers.

## Risks and test signals
High-risk areas are packet sizing and alignment, firmware size/version handling, endian paths, writeback address programming, fence ordering, hibernation reset behavior, and VM flush correctness. Bugs manifest as DMA ring timeouts, fence stalls, corrupted BO moves, stale PTEs, VM faults, or GPU lockups. Direct test signals are `cik_sdma_ring_test`, `cik_sdma_ib_test`, `radeon_ring_test`, fence wait completion, BO move stress, VM map/unmap stress, suspend/hibernate/resume, and lockup reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_sdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cikd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cikd.h

## Purpose
`cikd.h` is the main CIK ASIC hardware definition header for the Radeon driver. It maps large portions of CIK register space and packet encodings: power management, thermal/fan control, PCIe, SMC, memory controller, VM, command processor, RLC, SDMA, UVD/VCE media blocks, ATC, interrupts, and PM4/SDMA packet formats.

## Important APIs, types, and definitions
- Golden/config constants: `BONAIRE_GB_ADDR_CONFIG_GOLDEN`, `HAWAII_GB_ADDR_CONFIG_GOLDEN`, render-backend bitmap widths, and DIDT/SMC/DPM register fields.
- Power, thermal, fan, clock, and PCIe definitions: `GENERAL_PWRMGT`, `CG_THERMAL_*`, `CG_FDO_*`, SPLL controls, and PCIe link-control fields.
- Core register definitions: `SRBM_GFX_CNTL`, `SRBM_STATUS`, `SRBM_SOFT_RESET`, VM L2/context registers, memory-controller aperture/timing registers, GRBM indexing, scratch registers, CP queue/HQD registers, and RLC power-gating/safe-mode fields.
- PM4 packet helpers: `PACKET0`, `PACKET2`, `PACKET3`, `PACKET3_COMPUTE`, packet decoders, and many `PACKET3_*` opcodes/field helpers.
- SDMA definitions: two-engine offset constants, SDMA microcode/control/ring/IB registers, `SDMA_PACKET`, and SDMA opcodes for copy, write, IB, fence, trap, semaphore, poll, constant fill, PTE/PDE generation, timestamp, and SRBM writes.
- UVD/VCE/ATC/IH definitions support media engines and address-translation/PASID plumbing.

## Control flow and integration points
The file contains no functions, but it controls how many CIK driver files construct MMIO accesses and command packets. `cik_sdma.c` directly uses SDMA register and opcode definitions from this header. Command processor setup, VM management, power management, reset, media, and interrupt code use the broader register map and packet helpers.

## State and persistence behavior
All persistent state represented here is hardware state. The macros encode addresses and bitfields for registers whose values persist across command submissions and often across runtime power transitions until explicitly reset. Packet macros create command-stream words that alter GPU state when consumed by CP or SDMA engines.

## Dependencies and constraints
Consumers need Radeon utility macros such as `REG_SET` and standard fixed-width integer handling. Register values are ASIC-specific and must match CIK hardware documentation. Field helpers generally shift without full semantic validation, so call sites must mask, range-check, and respect block-specific ordering/alignment rules.

## Risks and test signals
Any incorrect address, bit mask, packet opcode, or shift can cause hard-to-debug hardware failures: failed init, broken power management, GPU hangs, VM faults, media engine failure, or corrupted command streams. Test signals include CIK boot/probe, modeset, suspend/resume, power-management transitions, VM fault tests, command submission, SDMA tests, UVD/VCE playback/encode, and register readback against known-good traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cikd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_cayman.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_cayman.h

## Purpose
`clearstate_cayman.h` defines static default register-state tables for Cayman-generation GPUs. The tables describe context, clear, and control-constant sections consumed by Radeon clear-state emission code to reset graphics context registers to known defaults.

## Important APIs, types, and data
- Includes `clearstate_defs.h` for `struct cs_extent_def`, `struct cs_section_def`, and `enum section_id`.
- `SECT_CONTEXT_def_1` through `SECT_CONTEXT_def_7` contain context-register default values with explicit `HOLE` placeholders where register ranges skip unsupported or reserved addresses.
- `SECT_CONTEXT_defs` maps those arrays to register indices and counts, including extents beginning at `0x0000a000`, `0x0000a1f5`, `0x0000a200`, `0x0000a23a`, `0x0000a29e`, `0x0000a2a5`, and `0x0000a2de`.
- `SECT_CLEAR_def_1` and `SECT_CLEAR_defs` define clear masks for `SQ_TEX_SAMPLER_CLEAR`, `SQ_TEX_RESOURCE_CLEAR`, and `SQ_LOOP_BOOL_CLEAR` at `0x0000ffc0`.
- `SECT_CTRLCONST_def_1` and `SECT_CTRLCONST_defs` define `SQ_VTX_BASE_VTX_LOC` and `SQ_VTX_START_INST_LOC` at `0x0000f3fc`.
- `cayman_cs_data` is the top-level sentinel-terminated section list.

## Control flow and integration points
There are no functions. Consumers iterate `cayman_cs_data`, then each section's extent list, emitting register writes for each array/count pair. The top-level sentinel `{ NULL, SECT_NONE }` and extent sentinels `{ NULL, 0, 0 }` terminate iteration.

## State and persistence behavior
The header data is immutable. When emitted, it resets persistent GPU context registers, shader-resource clear masks, and control constants. The values persist in hardware until later command streams or context switches update them.

## Risks and test signals
Risks are off-by-one register counts, wrong extent base indices, missing holes, or incorrect default values causing render corruption or command-processor faults. Test signals include clear-state packet emission tests, Cayman blit/draw smoke tests, context reset behavior, and comparison of generated command streams to known-good register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_cayman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_ci.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_ci.h

## Purpose
`clearstate_ci.h` defines CIK/CI default clear-state context register tables. Unlike the Evergreen/Cayman variants, this header provides only a context section, reflecting the CIK register layout and defaults used to initialize or restore graphics state.

## Important APIs, types, and data
- Includes `clearstate_defs.h`.
- `ci_SECT_CONTEXT_def_1` through `ci_SECT_CONTEXT_def_7` hold CIK context defaults, including depth/stencil, scissor, BC base, shader resource, viewport, color-buffer, blend, rasterizer, geometry, streamout, and anti-aliasing related registers.
- `ci_SECT_CONTEXT_defs` maps the arrays to extents at `0x0000a000`, `0x0000a0d6`, `0x0000a1f5`, `0x0000a200`, `0x0000a2a0`, `0x0000a2a3`, and `0x0000a2a5`.
- `ci_cs_data` is the top-level sentinel-terminated section list with `SECT_CONTEXT` followed by `SECT_NONE`.

## Control flow and integration points
The file has no executable control flow. Clear-state consumers iterate `ci_cs_data` and emit each context extent as packetized context-register writes for CIK hardware. The descriptor format is shared with other clearstate headers through `clearstate_defs.h`.

## State and persistence behavior
The arrays are static immutable CPU-side data. Emission writes persistent CIK context-register state. The state remains active until the next context restore, clear-state command, draw setup, or GPU reset changes it.

## Dependencies and constraints
The content depends on CIK-specific register index layout and field semantics. The use of `unsigned int` rather than `u32` still assumes 32-bit entries. Consumers must respect sentinel termination and must not interpret `HOLE` zeroes as omitted registers; they are part of counted ranges.

## Risks and test signals
Bad counts or defaults can corrupt CIK graphics state, particularly color/depth targets, scissor/viewport, shader resources, and AA state. Test signals include CIK clear-state emission, draw/blit correctness after reset or preamble, command submission without CP faults, and register trace comparison against expected CIK defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_ci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_defs.h

## Purpose
`clearstate_defs.h` defines the shared descriptor schema for Radeon clear-state tables. Architecture-specific clearstate headers use these types to describe groups of default register values and the section category each group belongs to.

## Important APIs, types, and data
- `enum section_id`: declares `SECT_NONE`, `SECT_CONTEXT`, `SECT_CLEAR`, and `SECT_CTRLCONST`.
- `struct cs_extent_def`: describes one contiguous register extent with a pointer to dword values, a starting register index, and a register count.
- `struct cs_section_def`: maps a sentinel-terminated extent list to a section id.

## Control flow and integration points
No functions are present. Clear-state emitters consume architecture-specific arrays of `struct cs_section_def`, stop at `SECT_NONE`, iterate each section's `struct cs_extent_def` array, and stop at a `NULL` extent pointer.

## State and persistence behavior
The descriptors are CPU-side metadata. They do not own state, but they define how static default tables become persistent GPU register state when emitted into a command stream.

## Dependencies and constraints
This header has no external includes and relies on C integer types only. Users must keep descriptor lifetimes static or otherwise valid while emitters iterate them. Register counts must match the pointed-to array lengths exactly.

## Risks and test signals
The main risks are schema misuse: missing sentinels, wrong counts, or invalid extent pointers. Test signals include successful iteration of all clearstate tables, absence of out-of-bounds reads under sanitizers/static analysis, and valid command streams generated for Evergreen, Cayman, and CI clearstate data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_evergreen.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_evergreen.h

## Purpose
`clearstate_evergreen.h` defines static default register-state tables for Evergreen-generation GPUs. Its shape closely matches the Cayman variant: context extents, clear-mask extents, control-constant extents, and a top-level section descriptor list.

## Important APIs, types, and data
- `SECT_CONTEXT_def_1` through `SECT_CONTEXT_def_7` contain context defaults for depth/stencil, scissor, shader constants/resources, viewport, blend/rasterizer, vertex/geometry, streamout, and AA state.
- `SECT_CONTEXT_defs` maps extents at `0x0000a000`, `0x0000a1f5`, `0x0000a200`, `0x0000a23a`, `0x0000a29e`, `0x0000a2a5`, and `0x0000a2de`. The fourth extent count is 98, slightly different from Cayman's corresponding count.
- `SECT_CLEAR_def_1` maps clear masks for sampler/resource/loop-bool clear registers at `0x0000ffc0`.
- `SECT_CTRLCONST_def_1` maps vertex base/start-instance defaults at `0x0000f3fc`.
- `evergreen_cs_data` is the top-level `struct cs_section_def` list ending in `SECT_NONE`.

## Control flow and integration points
There are no functions. Clear-state emission code includes this data and iterates the section and extent descriptors to produce command-stream writes for Evergreen hardware. The descriptor contract is defined by `clearstate_defs.h`, though this header itself does not include it and depends on the including compilation context.

## State and persistence behavior
The static arrays do not change. When emitted, they program persistent Evergreen GPU context, clear, and control-constant registers until later rendering setup or reset changes them.

## Dependencies and constraints
The file depends on `u32` and the clearstate descriptor types being visible to the including source. The register index/count pairs are tightly coupled to Evergreen register layout. `HOLE` zeroes are counted placeholders and must remain aligned with the target register ranges.

## Risks and test signals
Incorrect extents or defaults can break Evergreen rendering, blits, and post-reset context initialization. Test signals include Evergreen clear-state command generation, draw/blit smoke tests, GPU hang absence after preambles, and command-stream/register trace comparison with known-good defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_evergreen.h -->
