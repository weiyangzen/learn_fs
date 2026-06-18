# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002681`: lines 1-2498, `Docs/researches/chunks/subset-b-002681_research.md`
- `subset-b-002682`: lines 2499-4945, `Docs/researches/chunks/subset-b-002682_research.md`
- `subset-b-002683`: lines 4946-7413, `Docs/researches/chunks/subset-b-002683_research.md`
- `subset-b-002684`: lines 7414-7450, `Docs/researches/chunks/subset-b-002684_research.md`

## Chunk Research

### subset-b-002681: lines 1-2498

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h lines 1-2498

## Purpose

This chunk is generated AMD GC 9.4.3 register offset metadata for the first part of `gc_9_4_3_offset.h`. It contains the license/header guard and the first 1,197 `reg*` offset macros plus their matching `*_BASE_IDX` macros. The values are SOC15-style register indices used by AMDGPU, AMDKFD, RAS, VM hub, IMU, and debug code to address GC 9.4.3 hardware registers without hard-coding raw offsets in C files.

Although this repository path is under `distributed-fs/ceph-client`, the file is Linux AMD GPU driver hardware metadata, not Ceph filesystem logic. It has no executable code and no filesystem behavior.

The covered range defines the `xcd0` GC register map from the GRBM block through the beginning of the shader program register block:

- `xcd0_gc_grbmdec` at base `0x8000`: GRBM control, status, power, soft reset, trap/error, scratch, fence, and virtualization violation registers.
- `xcd0_gc_cpdec` at base `0x8200`: command processor CPC/CPF/ME/MEC status, stalls, headers, queues, counters, availability, debug, and privilege violation registers.
- `xcd0_gc_padec` at base `0x8800`: primitive assembly, vertex geometry tessellator, work distributor, clipping, scan converter, binning, shader array, UTCL1, and sideband/debug registers.
- `xcd0_gc_sqdec` at base `0x8c00`: SQ/SQC/LDS/SP configuration, debug, timeout, indirect access, instruction pseudo-registers, counters, EDC/RAS, and UTCL1-related state.
- `xcd0_gc_shsdec` at base `0x9000`: SX/SPI shader-stage controls, EDC status, wavefront lifetime, load-balance counters, GDS/export/scoreboard resources, CSQ activity, and trap screen registers.
- `xcd0_gc_tpdec` at base `0x9400`: TD and TA texture data/address controls, power, status, scratch, DSM, and EDC registers.
- `xcd0_gc_gdsdec` at base `0x9700`: GDS configuration, status, protection faults, EDC, DSM, and watchdog/crossbar state.
- `xcd0_gc_rbdec` at base `0x9800`: DB/RB/GB/CB debug, cache, FIFO, DFSM, backend disable/redundancy, address configuration, tile/macro-tile modes, and color-buffer hardware controls.
- `xcd0_gc_ea_gceadec`, `xcd0_gc_ea_gceadec2`, and `xcd0_gc_ea_pwrdec`: graphics client external access / EA arbitration, priority, SDP, MAM, DSM, error, probe, and power-gating control registers.
- `xcd0_gc_rmi_rmidec`: RMI general, subblock, crossbar, UTCL1, scoreboard, clock, and debug registers.
- `xcd0_gc_utcl2_*`: ATC L2, VM L2/page-fault, VM context, invalidation, memory-controller aperture, shared VM, and L2 TLB registers.
- `xcd0_gc_tcdec`: texture/cache TCP/TCI/TCC/TCA/TCX controls, policy, invalidate, status, DSM, writeback/invalidate, reset, and EDC status registers.
- `xcd0_gc_shdec` at base `0xb000`: the start of shader-stage program and user-data offsets for pixel, vertex, geometry, export, hull, and local shader stages. This chunk stops at `regSPI_SHADER_USER_DATA_LS_13`; the rest is in the next chunk.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, callbacks, locks, allocations, or direct MMIO operations in this chunk. The public interface is the generated macro namespace:

- `reg<REGISTER>` names a 32-bit register index within a GC address block, for example `regGRBM_STATUS`, `regSQ_IND_INDEX`, `regGCEA_SDP_CREDITS`, `regVM_INVALIDATE_ENG0_REQ`, and `regSPI_SHADER_PGM_RSRC3_PS`.
- `reg<REGISTER>_BASE_IDX` identifies the SOC15 base aperture index to pair with the offset. Most entries in this chunk use base index `0`; `regGCEA_ICG_CTRL_BASE_IDX` uses base index `1`, matching the high base address `0x3c000`.
- Address-block comments carry hardware decode boundaries. They are not C namespaces, but they document which hardware decoder owns the following offsets.

High-signal register families in this chunk include:

- GRBM: `regGRBM_CNTL`, `regGRBM_STATUS*`, `regGRBM_SOFT_RESET`, `regGRBM_GFX_CNTL`, `regGRBM_UTCL2_INVAL_RANGE_*`, `regGRBM_FENCE_RANGE*`, `regGRBM_SCRATCH_REG0..7`, and error/trap/IOV registers. These are central to graphics block status, reset, fencing, and broadcast/debug workflows.
- CP: `regCP_CPC_*`, `regCP_CPF_*`, `regCP_MEC_*`, `regCP_ME_*`, `regCP_STAT`, `regCP_BUSY_STAT`, `regCP_STALLED_STAT*`, queue availability/status registers, and `regCP_CMD_INDEX`/`regCP_CMD_DATA`. These expose command processor state and diagnostics.
- PA/VGT/WD/SC: `regVGT_*`, `regIA_*`, `regWD_*`, `regPA_CL_*`, `regPA_SU_*`, `regPA_SC_*`, `regCC_GC_PRIM_CONFIG`, `regGC_USER_PRIM_CONFIG`, shader-array configuration, and UTCL1 controls. These map frontend primitive setup and binning/raster path registers.
- SQ/SQC: `regSQ_CONFIG`, `regSQC_CONFIG`, `regLDS_CONFIG`, `regSQ_DEBUG_STS_GLOBAL*`, `regSQ_UTCL1_*`, trap base/mask registers, `regSQ_IND_INDEX`, `regSQ_IND_DATA`, `regSQ_CMD`, time registers, repeated instruction pseudo-registers at `0x037f`, load-balance counters, EDC counters, and UE/CE status pairs for SQ, LDS, SP0, and SP1.
- SPI/SX: `regSPI_PS_MAX_WAVE_ID`, `regSPI_START_PHASE`, `regSPI_GFX_CNTL`, `regSPI_DSM_CNTL*`, `regSPI_UE_ERR_STATUS_*`, `regSPI_CE_ERR_STATUS_*`, `regSPI_CONFIG_PS_CU_EN`, `regSPI_WF_LIFETIME_*`, `regSPI_LB_*`, `regSPI_GDS_CREDITS`, export/scoreboard buffer-size registers, CSQ wave-active counters, and process trap-screen register ranges.
- Texture and GDS: `regTD_*`, `regTA_*`, and `regGDS_*` describe texture control/status/power/EDC/DSM plus global data share configuration, fault, EDC, and watchdog registers.
- Render backend: `regDB_DEBUG*`, `regDB_DFSM_*`, `regCC_RB_*`, `regGB_ADDR_CONFIG`, `regGB_BACKEND_MAP`, `regGB_TILE_MODE0..31`, `regGB_MACROTILE_MODE0..15`, `regCB_HW_CONTROL*`, `regCB_DCC_CONFIG`, and GC-user backend disable/redundancy aliases.
- GCEA/RMI/VM/cache: `regGCEA_*`, `regRMI_*`, `regATC_L2_*`, `regVM_L2_*`, `regVM_CONTEXT*`, `regVM_INVALIDATE_ENG*`, `regMC_VM_*`, `regL2TLB_*`, `regUTC_GPUVA_*`, `regTCP_*`, `regTC_CFG_*`, `regTCI_*`, `regTCC_*`, `regTCA_*`, and `regTCX_*`.
- Shader program state: `regSPI_SHADER_PGM_*`, `regSPI_SHADER_USER_DATA_*`, and address pairs for PS, VS, GS/ES, HS/LS begin here. These offsets are used by graphics pipeline programming and KFD/user-mode queue setup paths.

The offset macros are normally consumed by helpers and table macros such as `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `AMDGPU_RAS_REG_ENTRY`, `RREG32_SOC15`, `WREG32_SOC15`, and IMU/RLC golden-setting macros. Field packing and decoding is provided by the companion `gc_9_4_3_sh_mask.h`, not by this offset file.

## Control Flow

This chunk has no runtime control flow. Its only effect is through C preprocessing.

Typical consumer flow is:

1. A GC 9.4.3-specific source includes `gc/gc_9_4_3_offset.h` and usually `gc/gc_9_4_3_sh_mask.h`.
2. Driver code selects a hardware instance or XCC instance, often through `GET_INST(GC, i)` or SOC15 instance helpers.
3. It passes a `reg*` macro to `SOC15_REG_OFFSET`/`SOC15_REG_ENTRY` or to a generated table macro.
4. Runtime code performs MMIO reads/writes, ring programming, RAS queries, VM invalidation, or firmware-loaded golden-register programming using the resulting address.

Concrete examples in this tree:

- `amdgpu/gfxhub_v1_2.c` initializes VM hub address members from this header, including `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `regVM_INVALIDATE_ENG0_SEM`, `regVM_INVALIDATE_ENG0_REQ`, `regVM_INVALIDATE_ENG0_ACK`, `regVM_CONTEXT0_CNTL`, and `regVM_L2_PROTECTION_FAULT_*`. It also computes context and invalidate-engine spacing by subtracting adjacent offset macros such as `regVM_CONTEXT1_CNTL - regVM_CONTEXT0_CNTL` and `regVM_INVALIDATE_ENG1_REQ - regVM_INVALIDATE_ENG0_REQ`.
- `amdgpu/gfx_v9_4_3.c` includes this header and uses offsets from this chunk in RAS register lists, including CE/UE status pairs for `GCEA`, `GDS`, `SPI`, `SP0`, `SP1`, `SQ`, `SQC`, `TD`, `TA`, `TCP`, `TCI`, `TCA`, `TCC`, `TCX`, and `LDS`.
- `amdgpu/imu_v11_0_3.c` uses GCEA, GCVM/GCMC, primitive config, and RB backend offsets from this chunk in IMU/RLC RAM golden-value tables, for example `regGCEA_SDP_CREDITS`, `regGCEA_SDP_ENABLE`, `regGCEA_MISC`, `regGCEA_DRAM_PAGE_BURST`, `regCC_GC_PRIM_CONFIG`, and `regCC_RB_BACKEND_DISABLE`.
- `amdgpu/amdgpu_amdkfd_gc_9_4_3.c` includes this header for KFD-facing GC 9.4.3 integration, tying these offsets to queue, trap, and compute-oriented setup paths.

The header itself does not encode access order, polling conditions, write-one-to-clear behavior, read side effects, reset sequencing, GRBM indexing, or whether a register is firmware-owned. Those rules live in the consuming driver code, hardware specification, firmware protocols, and mask/default companion headers.

## State And Persistence Behavior

No software state is stored here. The macros name hardware state that lives in the GC 9.4.3 block and related graphics cache/VM subblocks.

The hardware state represented by this chunk includes:

- Persistent-until-reprogrammed configuration: GRBM control, PA/VGT/WD frontend configuration, SQ/SQC/LDS runtime configuration, SPI shader and wave limits, texture unit controls, GDS configuration, DB/RB/GB/CB backend configuration, GCEA arbitration/priority/SDP settings, RMI routing, ATC/VM L2 controls, VM context controls, memory apertures, and cache policy registers.
- Live status and counters: GRBM and CP busy/stall/status registers, PA/WD/IA/VGT status, SQ debug/time/counter state, SPI wavefront lifetime and CSQ active counters, TD/TA/GDS status, RMI and ATC/VM/TCP/TCI/TCC/TCA/TCX status, and performance counter registers.
- Fault and RAS state: protection fault controls/status/address registers, dummy page fault address registers, GDS/VM protection faults, and UE/CE status pairs for shader, texture, cache, GDS, GCEA, SQ/SQC/LDS/SP, TCP/TCI/TCC/TCA/TCX, and TD/TA blocks.
- Command/debug trigger state: soft reset registers, CP command index/data, SQ indirect index/data and command registers, cache invalidation registers, TCC writeback/invalidate and soft reset, DSM/error-injection controls, probe controls, and translation-assist request/response registers.
- Per-context VM persistence: page table base/start/end addresses for VM contexts 0 through 15, context control registers, invalidate engine semaphore/request/ack/range registers for engines 0 through 17, and memory aperture/location registers. These are reinitialized by VM hub and reset/resume paths and must match the active XCC/instance topology.

Persistence is hardware-defined. Some registers are programmed during ASIC initialization or firmware-loaded golden settings and persist until reset, suspend/resume, power-gating, XCC reset, or explicit reprogramming. Others are live status, counters, latches, or write-trigger registers. This generated file does not distinguish safe read-only observation from destructive or privileged writes.

## Dependencies

This chunk depends on the AMDGPU SOC15 register abstraction and on the generated GC 9.4.3 register family:

- `gc_9_4_3_sh_mask.h` supplies bitfield shifts and masks for registers named here.
- Later chunks of `gc_9_4_3_offset.h` complete the same header, including the rest of `xcd0_gc_shdec` and additional address blocks.
- SOC15 helper macros translate `(hardware block, instance, reg macro)` triples into actual MMIO offsets.
- RAS, VM hub, GFX, KFD, and IMU code depend on the offsets matching the actual GC 9.4.3 hardware register spec.

The file is generated-style hardware contract data. It should stay synchronized with sibling GC 9.4.x headers, with `gc_9_4_3_sh_mask.h`, and with tables in `gfx_v9_4_3.c`, `gfxhub_v1_2.c`, `amdgpu_amdkfd_gc_9_4_3.c`, and IMU golden-setting files. Cross-generation names are intentionally similar, but offsets and available registers can differ between GC 9.4.2, GC 9.4.3, MMHUB 1.7/1.8, and other SOC15 blocks.

## Integration Points

Primary integration points are:

- GFX 9.4.3 core driver: `gfx_v9_4_3.c` includes this header for register access, RAS register list construction, per-XCC behavior, soft recovery, debug, initialization, and error counting/reset flows.
- GFXHUB VM initialization: `gfxhub_v1_2.c` uses VM context, page table, invalidate engine, and protection fault offsets from this chunk to populate `adev->vmhub[AMDGPU_GFXHUB(i)]` for each GC/XCC instance.
- KFD compute integration: `amdgpu_amdkfd_gc_9_4_3.c` includes the header for queue/trap/compute-facing register programming on GC 9.4.3.
- RAS: UE/CE status offset pairs in this chunk back `AMDGPU_RAS_REG_ENTRY` definitions for SQ, SQC, LDS, SP, SPI, GDS, TD/TA, TCP/TCI/TCC/TCA/TCX, and GCEA memory domains.
- IMU/RLC golden settings: `imu_v11_0_3.c` and related IMU code use GCEA, GCVM/GCMC, primitive, shader-array, and RB backend offsets to build firmware-programmed initialization tables.
- GPUVM and TLB invalidation: `VM_L2_*`, `VM_CONTEXT*`, `VM_INVALIDATE_ENG*`, `ATC_L2_*`, `MC_VM_*`, and `UTC_GPUVA_*` offsets participate in page table setup, aperture setup, fault reporting, and invalidation request/acknowledgement paths.
- Graphics pipeline programming: PA/VGT/WD/SPI/SQ/DB/GB/CB offsets are consumed by graphics queue setup, shader program state, draw-time register programming, tiling/backend topology, cache policy, and debug/profiling logic.

## Risks And Edge Cases

- Offset/header mismatches are the main risk. Pairing `gc_9_4_3_sh_mask.h` or GC 9.4.3 consumer code with another generation's offset header can compile but address the wrong register.
- The chunk boundary is artificial. It starts at the file header and ends in the middle of `xcd0_gc_shdec`, after `regSPI_SHADER_USER_DATA_LS_13`; the next chunks are required for the complete shader-stage register set and the rest of the file.
- Several consumers compute spacing by subtracting adjacent macro values, such as VM context distance and invalidate-engine distance. Any non-regular offset edit would break indexed addressing even if the named first register still worked.
- Most `*_BASE_IDX` values are `0`, but `regGCEA_ICG_CTRL_BASE_IDX` is `1`. Code that ignores base index can address the wrong aperture for high-address power/control registers.
- Many macros name write-trigger, reset, invalidation, trap, debug, or DSM/error-injection registers. Treating them as ordinary configuration registers can clear state, trigger hardware actions, inject faults, or disturb live queues.
- RAS status registers can be sticky, latched, instance-specific, or clear-on-write depending on the block. The offset header cannot reveal those semantics.
- VM context, page table, aperture, and invalidation registers are isolation-critical. Wrong offsets can map the wrong address space, miss invalidation acknowledgement, report faults against the wrong VMID, or corrupt per-process GPU virtual memory.
- Backend topology registers such as `GB_ADDR_CONFIG`, tile/macro-tile modes, RB disable/redundancy, and CB/DB controls affect surface layout, DCC/HTILE behavior, scanout compatibility, and render correctness.
- Shader program and user-data offsets are ABI-sensitive. Incorrect stage offsets can put user SGPR data, program addresses, or resource registers into the wrong shader stage.
- This is generated metadata; manual edits are higher risk than regenerating from the authoritative AMD register source.

## Test Signals

Useful validation signals include:

- Build coverage for GC 9.4.3 AMDGPU and KFD paths that include this header, especially `gfx_v9_4_3.c`, `gfxhub_v1_2.c`, `amdgpu_amdkfd_gc_9_4_3.c`, and IMU golden-setting code.
- Static consistency checks that every `reg*` macro has a matching `reg*_BASE_IDX`, that address-block base-index transitions match the generated register database, and that offsets used in subtraction-based stride calculations remain regular.
- Generated-header consistency checks against `gc_9_4_3_sh_mask.h` so named registers have matching field definitions where fields exist.
- Hardware boot and init on GC 9.4.3 systems with multiple XCC instances, confirming GRBM, CP, GFX, VM hub, GDS, texture/cache, and shader pipeline initialization complete without invalid register access warnings.
- GPUVM tests that create/destroy VM contexts, program page table bases/start/end ranges, issue per-engine invalidations, poll acknowledgements, and verify protection fault reporting.
- RAS query/injection/reset tests for SQ/SQC/LDS/SP/SPI/GDS/TD/TA/TCP/TCI/TCC/TCA/TCX/GCEA status register pairs covered by this chunk.
- IMU/RLC golden-setting validation that expected GCEA, GCVM/GCMC, primitive, shader-array, and RB backend registers receive the intended mask/value programming.
- Graphics and compute smoke tests that exercise shader program registers, user-data SGPR setup, trap handling, queues, dispatch/draw execution, DB/CB backends, tiling, texture/cache behavior, and suspend/resume.
- Regression indicators include VM invalidation timeouts, wrong protection fault addresses/VMIDs, RAS counters on the wrong block, broken shader launches, render artifacts from backend/tile misconfiguration, RLC/IMU programming failures, or ring timeouts during reset/recovery.

### subset-b-002682: lines 2499-4945

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h lines 2499-4945

## Scope

This chunk covers a generated AMD GC 9.4.3 register-offset header range. It is not executable code; its public surface is a set of preprocessor constants mapping register names to per-address-block offsets and `*_BASE_IDX` selector values used by SOC15/MMIO register access helpers.

The slice starts in the middle of the shader processor interpolator/user-data register area at `regSPI_SHADER_USER_DATA_LS_13_BASE_IDX`, continues through compute dispatch state, CP graphics/compute queue state, SPI arbitration/debug/resource-reservation state, HQD queue descriptors, TCP watch/cache controls, GDS allocation/context-switch counters, RAS signatures, and a large graphics context block. It ends just after the start of the `xcd0_gc_gfxudec` block with EOP and stream-out address registers; the adjacent chunk is needed for the rest of `gfxudec` counter definitions.

Address blocks covered in this range:

- Existing `BASE_IDX 0` shader/compute context area before the first in-range address-block comment.
- `xcd0_gc_cppdec` at base address `0xc080`.
- `xcd0_gc_cppdec2` at base address `0xc600`.
- `xcd0_gc_spipdec` at base address `0xc700`.
- `xcd0_gc_cpphqddec` at base address `0xc800`.
- `xcd0_gc_tcpdec` at base address `0xca80`.
- `xcd0_gc_gdspdec` at base address `0xcc00`.
- `xcd0_gc_rasdec` at base address `0xce00`.
- `xcd0_gc_gfxdec0` at base address `0x28000`.
- Beginning of `xcd0_gc_gfxudec` at base address `0x30000`.

## Purpose

`gc_9_4_3_offset.h` provides compile-time symbolic register offsets for AMD GC 9.4.3 graphics-core hardware. Consumers pass these symbols to macros such as `SOC15_REG_OFFSET()`, `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, `RREG32_SOC15()`, and register-entry dump helpers so driver code can address hardware registers by stable names rather than literal offsets.

This chunk is centered on two hardware surfaces:

- Command, dispatch, queue, and memory-resource state for compute and graphics engines: compute dimensions/user data, CP ring buffer configuration, doorbells, interrupt state, UTCL1 errors/status, HQD/MQD queue descriptors, EOP queues, GDS/GWS/OA resources, TCP watchpoints, and RAS signature collection.
- Draw/render context state: depth-buffer state, scissor/window/viewport state, clip and user-clip-plane state, pixel-shader input mapping, blend/color target state, primitive assembly, tessellation/geometry/stream-out state, rasterization/sample state, and color-buffer render-target base/metadata addresses.

The header is generated from AMD register descriptions. Its correctness is foundational because a wrong numeric offset silently sends later driver code to the wrong MMIO/register-aperture location.

## Important API Surface

- Shader and compute context registers at lines 2499-2715 include `regSPI_SHADER_USER_DATA_LS_14` through `_31`, `regSPI_SHADER_USER_DATA_COMMON_0` through `_31`, `regCOMPUTE_DISPATCH_INITIATOR`, `regCOMPUTE_DIM_{X,Y,Z}`, `regCOMPUTE_START_{X,Y,Z}`, `regCOMPUTE_NUM_THREAD_{X,Y,Z}`, `regCOMPUTE_PGM_{LO,HI}`, `regCOMPUTE_DISPATCH_PKT_ADDR_{LO,HI}`, `regCOMPUTE_DISPATCH_SCRATCH_BASE_{LO,HI}`, `regCOMPUTE_PGM_RSRC{1,2,3}`, `regCOMPUTE_VMID`, resource/thread-management registers, restore/relaunch registers, and `regCOMPUTE_USER_DATA_0` through `_15`.
- `xcd0_gc_cppdec` at lines 2718-3079 defines CP front-end and ring state: DFY command/data registers, EOP wait timing, CPC/CPF/CPG UTCL1 controls and error status, CP virtual/error status, ring-buffer base/control/read/write pointer registers for RB0/RB1/RB2, doorbell ranges, interrupt control/status for rings and ME pipes, priority/VMID/preemption state, instruction-cache base/op controls, and ECC/EDC status.
- `xcd0_gc_cppdec2` at lines 3082-3141 defines scheduler-specific doorbell controls, doorbell clear, CPF/CPG/CPC DSM controls, EDC FUE control, graphics MQD base/control, ring status, UTCL1 status, soft reset, and CPC graphics control.
- `xcd0_gc_spipdec` at lines 3144-3263 defines SPI arbitration, per-pipe weight/percentage controls, graphics debug/trap controls, scratch address check/status, compute queue reset, per-CU resource reservation and enable registers for CUs 0-15, wavefront context-save control, and arbitration control.
- `xcd0_gc_cpphqddec` at lines 3266-3403 defines HQD/MQD queue control state: queue active/VMID/persistent state, priorities and quantum, packet-queue base/read/write pointers, read-pointer reporting address, write-pointer polling address, doorbell control, packet/IB queue controls, dequeue/offload/semaphore/message controls, atomic preops, HQ scheduler/status/control aliases, EOP queue base/control/events, context-save buffer/stack/workgroup/GDS state, error state, AQL controls, and dispatch IDs.
- `xcd0_gc_tcpdec` at lines 3406-3453 defines TCP watchpoint address/control pairs 0-3, GATCL1/TCP DSM controls, UTCL1 controls/status, and perf-counter filters.
- `xcd0_gc_gdspdec` at lines 3456-3693 defines GDS per-VMID base/size allocations for VMIDs 0-15, GWS and OA ownership per VMID, reset masks and triggers, max compute wave ID, GDS enhancement/restore/status, compute and graphics context-switch status, and per-shader-stage context-switch counters.
- `xcd0_gc_rasdec` at lines 3696-3753 defines RAS signature control/mask and signature registers for SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI blocks.
- `xcd0_gc_gfxdec0` at lines 3756-4925 is the largest part of the chunk. It defines depth/stencil render-target state (`DB_*`), coherency destination bases, scissor/window/cliprect/viewport state (`PA_SC_*`), color and shader masks, viewport Z ranges and transforms, user clip planes, pixel-shader input control, interpolation and shader output formats, blend controls, copy-state triggers, VGT draw/DMA/event/tessellation/geometry/stream-out state, rasterization and anti-aliasing sample state, and complete color-target register groups `CB_COLOR0_*` through `CB_COLOR7_*` including base, extended base, view, info, attrib, DCC, CMASK, FMASK, clear words, and DCC base.
- The start of `xcd0_gc_gfxudec` at lines 4928-4945 defines CP EOP completion address/data/fence registers and stream-out address registers. The continuation of this block is outside this chunk.

There are no C types, structs, enums, functions, or inline helpers in this range. Each logical register usually has two macros: `regNAME` for the offset and `regNAME_BASE_IDX` for the register base selector. Most queue/control registers in the earlier blocks use `BASE_IDX 0`; the `gfxdec0` and initial `gfxudec` registers use `BASE_IDX 1`.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by callers that choose a register symbol, combine it with a GC instance, and perform a read or write through AMDGPU register accessors. Typical flows are:

1. Initialization or resume code programs CP rings, doorbells, HQD queues, MQD pointers, SPI scheduling, GDS resources, and render context defaults using the symbolic offsets.
2. Command submission and queue-management paths update ring write pointers, HQD active/dequeue state, packet-queue bases, read-pointer report addresses, doorbell controls, and EOP queues.
3. Graphics command emission or context restore writes draw/render state registers such as DB, PA, VGT, SPI, and CB registers before draws.
4. Diagnostics, RAS, KFD, and reset paths read status, error, signature, queue, context-switch, and watchpoint registers to decide whether hardware is idle, occupied, faulted, or recoverable.

In the local tree, `gfx_v9_4_3.c` includes this header and programs HQD registers with `WREG32_SOC15_RLC(GC, GET_INST(GC, xcc_id), regCP_HQD_..., ...)`, including EOP base/control, PQ base, PQ control, report/poll addresses, and active/dequeue state. `amdgpu_amdkfd_gfx_v11.c` has the same register-family pattern for queue occupancy checks: it reads `regCP_HQD_ACTIVE`, then compares `regCP_HQD_PQ_BASE` and `regCP_HQD_PQ_BASE_HI` against a queue address. Newer `gfx_v11_0.c`, `gfx_v12_0.c`, `gfx_v12_1.c`, and MES paths use equivalent symbols from their generation-specific headers, showing the integration pattern this GC 9.4.3 header supports.

## State and Persistence

The macros are stateless compile-time constants. The hardware registers they name are persistent GPU state until changed by firmware, command processor packets, direct MMIO writes, context save/restore, power management, GPU reset, or suspend/resume.

Queue and dispatch state is persistent and safety-critical. CP ring bases, write/read pointers, doorbell ranges, HQD/MQD bases, EOP queue pointers, VMID fields, and AQL dispatch IDs represent live scheduling state for graphics and compute queues. Incorrect persistence can make a ring appear occupied, redirect queue fetches, lose completion notifications, or corrupt command processing.

Graphics context state is also persistent across command buffers according to the GPU context model. DB/CB/PA/VGT/SPI registers describe the current render target addresses and metadata, viewport/scissor/clip state, shader input routing, primitive topology, tessellation, stream-out, depth/stencil policy, color blending, and sample locations. A stale or misprogrammed register can affect later draws until overwritten or context-restored.

GDS/GWS/OA allocations are per-VMID resource partitioning state. Their base/size/ownership registers decide how shader queues see global data share and synchronization resources. GDS context-switch counters and status registers are diagnostic/persistence signals around context save/restore.

RAS signature registers are diagnostic accumulation/state registers for hardware error-signature collection. TCP watch registers persist as data-watch/debug controls. SPI resource reservation registers persist CU reservation policy that can constrain queue execution until cleared.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.4.3 register database. This offset header must stay synchronized with companion generated headers for GC 9.4.3 bit masks, defaults, and any packet/register programming tables.
- Integrated through AMDGPU SOC15 address helpers and direct register access macros. The numeric offset is only meaningful when paired with the correct hardware IP block (`GC`), instance/XCC selection, and `BASE_IDX`.
- Used by GC 9.4.3-specific graphics code such as `amdgpu/gfx_v9_4_3.c` and KFD integration such as `amdgpu_amdkfd_gc_9_4_3.c`, with nearby architecture versions following the same register names for debug tables, ring setup, HQD programming, and queue occupancy logic.
- The CP/HQD/MQD macros integrate with KFD and MES concepts: MQD memory contents are copied into hardware queue descriptors, doorbells notify the command processor, and polling/report addresses live in GPU-visible memory.
- The DB/CB/PA/VGT/SPI graphics context macros integrate with PM4 packet emission and context image layout. They are not usually written by arbitrary kernel code one by one during normal draws, but they define the register names used by packets, dumps, and restore paths.
- RAS signature macros integrate with GPU reliability/error-detection paths; TCP watch and UTCL1 status/error registers integrate with debug/fault diagnostics.

## Risks

- Offset drift is the primary risk. If a generated value or `BASE_IDX` is wrong, a valid-looking `WREG32_SOC15*` call targets the wrong register or wrong aperture. This can cause silent queue corruption, hangs, bad render output, or misleading diagnostics.
- The chunk boundaries are partial. The first line is only the base-index macro for `regSPI_SHADER_USER_DATA_LS_13`, whose offset appears before this chunk. The final `gfxudec` block continues after `regCP_STREAM_OUT_ADDR_HI`; merge tooling must not treat the block as complete from this document alone.
- Alias-like duplicate offsets are intentional but hazardous for manual review. Examples include `regCP_RB0_BASE` and `regCP_RB_BASE`, `regCP_ME0_PIPE*_PRIORITY` and `regCP_RING*_PRIORITY`, `regCP_HQD_DMA_OFFLOAD` and `regCP_HQD_OFFLOAD`, `regCP_HQD_HQ_SCHEDULER*`/status/control aliases, and `regCP_PIPEID`/`regCP_RINGID`. A caller must use the semantic alias appropriate to the engine path being maintained.
- Queue-management registers are high-risk. Bad HQD base, PQ control, doorbell control, report/poll address, EOP base, active/dequeue, or VMID programming can leave compute queues stuck, falsely occupied, or writing completion data to the wrong memory.
- Render-target address and metadata registers are high-risk. `CB_COLOR*_BASE`, `*_BASE_EXT`, `*_DCC_BASE`, `*_CMASK`, and `*_FMASK` fields affect GPU memory access. Incorrect offsets or writes can produce memory corruption or invalid compression metadata access.
- GDS/GWS/OA per-VMID registers repeat over VMID 0-15, creating copy/paste and loop-index hazards. A one-off error changes another VMID's resource allocation.
- `BASE_IDX` mismatch is subtle. Early CP/SPI/HQD/TCP/GDS/RAS registers use base index 0, while graphics context and the initial `gfxudec` registers use base index 1. Incorrect table generation or manual macro selection can address the wrong base.
- This header has no reserved-bit, sequencing, range, or locking enforcement. Consumers must preserve hardware-required write ordering and use the correct accessor variant, especially RLC-safe writes during queue setup.

## Test Signals

- Build coverage: compiling AMDGPU with GC 9.4.3 support catches missing symbols, malformed macros, duplicate definitions that break preprocessing, and include-order issues.
- Generated-header validation: compare lines 2499-4945 against the AMD GC 9.4.3 register source/spec and companion `*_sh_mask.h`/default headers, checking every `reg*` offset and `*_BASE_IDX`.
- Register-access smoke tests on GC 9.4.3 hardware: boot, suspend/resume, GPU reset, and ring initialization should complete without MMIO faults, register-restore warnings, or command-processor timeouts.
- Queue tests: run KFD/compute workloads that create, destroy, preempt, and resume queues. Watch `regCP_HQD_ACTIVE`, PQ base/high, doorbells, EOP write pointers, and dequeue behavior for hangs or false occupancy.
- Graphics tests: run draw workloads covering depth/stencil, multiple render targets, DCC/CMASK/FMASK, viewport/scissor arrays, tessellation/geometry, stream-out, MSAA sample positions, and primitive restart. Failures often indicate DB/CB/PA/VGT/SPI offset or context-restore mistakes.
- RAS/debug tests: read RAS signatures, TCP watch/status, UTCL1 status/error, CP/CPC/CPF/CPG error status, and GDS context-switch counters through debug or recovery paths and compare against known-good dumps.
- Cross-generation sanity: because GC 9.4.2 and GC 9.4.3 share many CP/HQD and CB offsets while GC 11/12 use different generated offsets for several blocks, tests should ensure the GC 9.4.3 device selects `gc_9_4_3_offset.h` rather than a neighboring generation's header.

### subset-b-002683: lines 4946-7413

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h lines 4946-7413

## Scope

This chunk covers generated register offset macros for the AMD GC 9.4.3 graphics block. It starts inside `addressBlock: xcd0_gc_gfxudec` at command-processor pipeline statistics registers and runs through later address blocks:

- `xcd0_gc_gfxudec`: CP pipeline statistics, scratch, semaphore, DMA, coherency, indirect-buffer, draw/dispatch, VGT, PA, SQ thread trace, DB counters, GDS, and SPI configuration offsets.
- `xcd0_gc_gccanedec`: a small GC CANE register window.
- `xcd0_gc_perfddec` and `xcd0_gc_perfsdec`: performance counter data registers and selector/control registers for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, and RMI.
- UTCL2 performance blocks: ATC L2, MC VM L2, and L2TLB counter data, configuration, and result-control windows.
- `xcd0_gc_gdflldec`: GDFLL EDC hysteresis control/status offsets.
- `xcd0_gc_rlcpdec`: RLC control, timers, clock counts, power-gating, SERDES, scratch, SRM, SMU command, UTCL1/prewalker, interrupt, semaphore, DSM, and error-status offsets.
- `xcd0_gc_pwrdec`: CGTS compute-unit control registers, TCC disable controls, CGTT clock controls, SQ power throttle, and per-block clock-gating controls.
- `xcd0_gc_hypdec`: CP hypervisor microcode windows, GRBM shadow-register selection, RLC GPU IOV/SR-IOV scheduler, doorbell, timer, interrupt, SDMA status, and scratch/microcode offsets.
- `xcd0_gc_utcl2_vmsharedhvdec`: per-VF framebuffer aperture, MARC, IOMMU, ATS, active-function, and XGMI GPU IOV controls.
- `xcd0_gc_pspdec`: PSP-facing CP/GRBM/RLC security and firewall offsets.
- `sqind`: the first SQ indirect wave debug/status offsets.

The file is a generated C preprocessor register map. It defines `reg*` and `ix*` constants plus matching `_BASE_IDX` constants only. There are no C functions, structs, variables, algorithms, or in-header storage in this chunk.

## Purpose

The chunk provides the address side of the AMDGPU register ABI for GC 9.4.3. Driver code includes this header to convert symbolic register names into MMIO offsets for `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC_SHADOW_EX`, and related AMDGPU accessors.

Each normal register has the pattern:

- `regNAME`: the register offset within the GC IP block's register address space.
- `regNAME_BASE_IDX`: the generated base-index selector used by the SOC15 register helper layer.

The `sqind` entries use `ixSQ_*` names because they are indirect SQ indexes rather than ordinary `reg*` MMIO offsets. They are consumed through SQ indirect-index access paths, not by writing them as direct MMIO register addresses.

This header is paired with sibling generated headers such as `gc_9_4_3_sh_mask.h` for field shifts/masks and any available default headers for reset/default values. The offsets here identify which register to read or write; the mask header identifies how individual fields are encoded inside that register.

## Important Macro Families

### Command Processor, Draw State, and Pipeline Statistics

The opening `xcd0_gc_gfxudec` range maps user/context-facing CP registers:

- Pipeline counters: `regCP_NUM_PRIM_WRITTEN_COUNT*_LO/HI`, `regCP_NUM_PRIM_NEEDED_COUNT*_LO/HI`, `regCP_VGT_*_COUNT_*`, `regCP_PA_*_COUNT_*`, `regCP_SC_PSINVOC_COUNT*_LO/HI`, and `regCP_VGT_CSINVOC_COUNT_LO/HI`.
- Pipeline statistics control and destination: `regCP_PIPE_STATS_ADDR_LO/HI`, `regCP_PIPE_STATS_CONTROL`, `regCP_STREAM_OUT_CONTROL`, and `regCP_STRMOUT_CNTL`.
- Scratch and synchronization windows: `regSCRATCH_REG0..7`, `regSCRATCH_UMSK`, `regSCRATCH_ADDR`, `regCP_SIG_SEM_ADDR_*`, `regCP_WAIT_SEM_ADDR_*`, `regCP_SEM_WAIT_TIMER`, and `regCP_WAIT_REG_MEM_TIMEOUT`.
- Atomic and GDS pre-operation aliases for PFP and ME: `regCP_PFP_ATOMIC_PREOP_*`, `regCP_PFP_GDS_ATOMIC*_PREOP_*`, `regCP_ATOMIC_PREOP_*`, `regCP_ME_ATOMIC_PREOP_*`, and `regCP_ME_GDS_ATOMIC*_PREOP_*`.
- CP DMA and coherency registers: `regCP_DMA_ME_*`, `regCP_DMA_PFP_*`, `regCP_DMA_CNTL`, `regCP_DMA_READ_TAGS`, `regCP_COHER_*`, and `regCP_ME_COHER_*`.
- Ring/IB state: `regCP_RB_OFFSET`, `regCP_IB1_OFFSET`, `regCP_IB2_OFFSET`, preamble begin/end offsets, CE IB offsets, command-buffer size registers, and base/size registers for CE, IB1, IB2, and stream state buffers.
- Draw/dispatch operand registers: `regCP_DRAW_INDX_INDR_ADDR*`, `regCP_DISPATCH_INDR_ADDR*`, `regCP_INDEX_BASE_ADDR*`, `regCP_INDEX_TYPE`, and completion/predicate/status registers.

These offsets are integration points for graphics queue setup, indirect-buffer execution, CP DMA operations, streamout/statistics query handling, and fence/semaphore packet execution.

### Geometry, PA, SQ Thread Trace, DB, GDS, and SPI Windows

The same `gfxudec` block also maps front-end and shader/debug-facing state:

- `regGRBM_GFX_INDEX` selects shader engine, shader array, and instance targeting for many broadcast or per-instance register writes. GC 9.4.3 code uses it through `WREG32_SOC15_RLC_SHADOW_EX` and direct SOC15 helpers.
- VGT/IA/WD state includes `regVGT_PRIMITIVE_TYPE`, `regVGT_INDEX_TYPE`, streamout filled-size counters, vertex index bounds, instance counts, tessellation-factor memory, WD buffer bases, and `regIA_MULTI_VGT_PARAM`.
- PA/scissor/trap state includes line stipple, screen extents, trap screen enable/position/count registers, and stereo state.
- SQ thread trace state includes `regSQ_THREAD_TRACE_BASE`, `SIZE`, `MASK`, `TOKEN_MASK`, `PERF_MASK`, `CTRL`, `MODE`, `BASE2`, `WPTR`, `STATUS`, `HIWATER`, `CNTR`, and user data registers.
- DB counters include occlusion and Z-pass low/high counter pairs.
- GDS registers cover direct read/write burst windows, atomic operation setup/results, GWS resource accounting, ordered-append controls, and OA ring sizing.
- SPI registers include basic configuration and wave-limit control.

These offsets are not ordinary host data structures. They refer to hardware state that is selected by GC instance and often by `GRBM_GFX_INDEX` before access.

### Performance Counter Data and Selector Blocks

`xcd0_gc_perfddec` contains low/high counter data registers. `xcd0_gc_perfsdec` contains selector, control, filter, mux, sample-delay, and result-control registers. Together they form the performance-monitoring ABI for major graphics blocks:

- CP-side counters: `CPG`, `CPC`, `CPF`, latency stat data/select registers, TC performance counter window selects, and `regCP_PERFMON_CNTL`.
- Front-end and raster blocks: `GRBM`, `WD`, `IA`, `VGT`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, and `SX`.
- Memory/cache blocks: `GDS`, `TA`, `TD`, `TCP`, `TCC`, `TCA`, `CB`, `DB`, `RLC`, and `RMI`.
- UTCL2 blocks: `regATC_L2_PERFCOUNTER_*`, `regMC_VM_L2_PERFCOUNTER_*`, `regL2TLB_PERFCOUNTER_*`, matching `*_CFG` registers, and `*_RSLT_CNTL` registers.

RLC SPM offsets in this range are especially important: `regRLC_SPM_PERFMON_CNTL`, ring base/size registers, SE/global muxsel address/data, per-block sample delay registers, ring read pointer, segment threshold, and `regRLC_SPM_PERFMON_SAMPLE_DELAY_MAX`. These are the address definitions used by profiling paths that stream sampled performance data through an RLC-managed memory ring.

### RLC Control, Firmware, Power, and Error State

`xcd0_gc_rlcpdec` maps the RLC control plane:

- Bring-up and safe-mode registers: `regRLC_CNTL`, `regRLC_STAT`, `regRLC_SAFE_MODE`, `regRLC_RLCV_SAFE_MODE`, `regRLC_SMU_SAFE_MODE`, `regRLC_RLCV_COMMAND`, and `regSMU_RLC_RESPONSE`.
- Timers and clocks: refclock timestamp pairs, `regRLC_GPM_TIMER_INT_*`, `regRLC_GPM_TIMER_CTRL`, `regRLC_GPM_TIMER_STAT`, GPU clock count pairs, capture registers, `regRLC_CLK_COUNT_*`, and clock-count control/status.
- Clock/power gating and load balancing: `regRLC_MGCG_CTRL`, `regRLC_PG_CNTL`, `regRLC_CGTT_MGCG_OVERRIDE`, `regRLC_CGCG_CGLS_CTRL*`, ramp control, dynamic/static PG status/request, CU masks, load-balance parameters, thread priority/enable, and max/always-on CU masks.
- RLC memory and firmware windows: GPM general registers, scratch address/data, SRM ARAM/DRAM/index-control address/data windows, SRM command/status/abort, CSIB address/length, SMU command/argument registers, and scheduler registers.
- UTCL1/prewalker/DSM/error paths: `regRLC_GPM_UTCL1_*`, `regRLC_SPM_UTCL1_*`, `regRLC_PREWALKER_UTCL1_*`, `regRLC_UTCL1_STATUS*`, `regRLC_UTCL2_CNTL`, `regRLC_DSM_*`, and corrected/uncorrected error status registers.
- Interrupt and synchronization offsets: RLC/GPM interrupt status, disable/force registers, CP EOF interrupt counters, spare interrupts, and `regRLC_SEMAPHORE_0..3`.

This block is central to GFX firmware bring-up, suspend/resume, reset, power management, performance monitoring, and error handling.

### CGTS, CGTT, and Power Block Offsets

`xcd0_gc_pwrdec` provides clock/power control offsets:

- `regCGTS_SM_CTRL_REG`, read-control/read-data registers, and TCC disable/user TCC disable registers.
- Per-CU CGTS control registers for CU0 through CU15, including `SP0`, `LDS_SQ`, `TA_SQC`, `SP1`, `TD_TCP`, and separate `TCPI` controls.
- Per-block CGTT clock controls for SPI, SPIS, PC, BCI, VGT, IA, WD, PA, SC, SQ, SQG, TD, TA, TCPI, TCX, DB, CB, TCC, TCA, CP, CPC, RLC, RMI, and TCPF.
- SQ power-throttle offsets and `regRLC_GFX_RM_CNTL`.

These offsets describe persistent hardware policy registers used to gate clocks, disable harvested units, or throttle shader resources. They must stay consistent with power-management policy, topology discovery, and SMU/RLC firmware expectations.

### Hypervisor, SR-IOV, VM, and Security Windows

`xcd0_gc_hypdec` maps privileged controls:

- CP microcode aliases: `regCP_HYP_PFP_UCODE_ADDR/DATA`, `regCP_PFP_UCODE_ADDR/DATA`, `regCP_HYP_ME_UCODE_ADDR/DATA`, `regCP_ME_RAM_RADDR/WADDR/DATA`, CE and MEC1/2 hypervisor/non-hypervisor address/data aliases, checksum registers, and `regCP_HYP_XCP_CTL`.
- RLC/GPM microcode and scratch: `regRLC_GPM_UCODE_ADDR/DATA`, `regRLC_GPU_IOV_UCODE_ADDR/DATA`, and `regRLC_GPU_IOV_SCRATCH_ADDR/DATA`.
- GRBM shadow-register selection: `regGRBM_GFX_INDEX_SR_SELECT/DATA`, `regGRBM_GFX_CNTL_SR_SELECT/DATA`, and `regGRBM_MCM_ADDR`.
- GPU IOV state: `regRLC_GPU_IOV_VF_ENABLE`, scheduler/config registers, active function ID, VM busy status, virtual reset request/response, F32 control/reset, interrupt status/disable/force, SMU response, SDMA0..7 status and busy-status registers, RLCV timer controls, VF doorbell status/set/clear, VF masks, and hypervisor semaphores.

`xcd0_gc_utcl2_vmsharedhvdec` extends virtualization and memory-management state with `regMC_VM_FB_SIZE_OFFSET_VF0..VF15`, MARC base/relocation/length low/high groups, IOMMU control/performance controls, PCIe ATS controls for PF and VF0..VF15, shared active function ID, and XGMI GPU IOV enable.

`xcd0_gc_pspdec` maps PSP/security-related offsets such as `regCPG_PSP_DEBUG`, `regCPC_PSP_DEBUG`, `regCP_PSP_XCP_CTL`, `regGRBM_SEC_CNTL`, GRBM IOV error FIFO data, DSM bypass, CAM index/data aliases, and `regRLC_FWL_FIRST_VIOL_ADDR`.

These ranges are privilege-sensitive. Many macros are valid only in PF, hypervisor, PSP, firmware-load, or diagnostic paths.

### SQ Indirect Wave Debug Indexes

The chunk ends at the start of the `sqind` address block with `ixSQ_DEBUG_STS_LOCAL`, `ixSQ_DEBUG_CTRL_LOCAL`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_HW_ID`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, and `ixSQ_WAVE_IB_STS`. These are indirect indexes for local SQ wave inspection and control, not direct register offsets.

## Control Flow and State Behavior

There is no executable control flow in this header. It affects runtime behavior by making symbolic register addresses available to compiled driver code.

The state represented by the macros is hardware-resident state. Important persistent or latched hardware state includes CP counters and ring/IB pointers, scratch and semaphore addresses, coherency ranges/status, draw/dispatch operands, SQ thread-trace buffers, DB/GDS counters and atomic windows, performance counter selections and samples, RLC firmware/safe-mode/timer/power-gating state, RLC SRM/GPM memory windows, clock-gating and throttle policy, SR-IOV scheduler and doorbell state, per-VF memory apertures, IOMMU/ATS state, security CAM/firewall state, and SQ wave debug status.

Some offsets name command or access windows rather than durable configuration. Examples include CP DMA command registers, GDS atomic operation registers, RLC capture/command/status pairs, SRM command windows, GRBM shadow-register select/data windows, CP/RLC microcode address/data ports, doorbell set/clear registers, and SQ indirect debug control. Correct users must follow the sequencing, polling, and timeout rules in the owning AMDGPU code and hardware specification; the offset header itself encodes only addresses.

## Dependencies and Integration Points

This chunk depends on the AMD generated register-header convention:

- `gc_9_4_3_offset.h` supplies register and index offsets.
- `gc_9_4_3_sh_mask.h` supplies field shifts and masks for many of the same register names.
- SOC15 access macros combine the GC IP block, GC/XCC instance, `_BASE_IDX`, and register offset into actual MMIO addresses.

Observed source-tree integration points include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`, which includes this header, writes `regGRBM_GFX_INDEX` through RLC-shadow-aware paths, reads `regRLC_CNTL`, and registers GC 9.4.3 debug access controls.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c`, which includes this header for GC 9.4.3 address definitions used by the graphics hub.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, which includes this header for KFD/compute integration on GC 9.4.3.
- Cross-generation AMDGPU code shows the same symbolic families used for firmware and register access patterns, for example `regGRBM_GFX_INDEX`, `regRLC_CNTL`, and `regCP_HYP_PFP_UCODE_ADDR` in nearby GFX 11/12 implementations. GC 9.4.3 consumers must still include the GC 9.4.3-specific offset/mask set because offsets and available registers can drift by generation.

The main external dependencies are the hardware register specification, RLC/CP/PSP/SMU firmware contracts, SR-IOV virtualization policy, and kernel AMDGPU helper APIs. The header is not useful independently of those consumers.

## Risks

- Offset drift is high impact. A wrong offset or base index can read or write a different hardware register, causing queue hangs, bad performance data, failed firmware load, broken power management, or loss of PF/VF isolation.
- The repeated performance-counter families are mechanically similar but not interchangeable. Counter counts, LO/HI ordering, selector availability, and block-specific control registers vary across CP, GRBM, SQ, memory, DB/CB, and RLC/RMI blocks.
- Several names are aliases for the same offset, such as CP ME/PFP/hypervisor microcode windows and atomic pre-operation registers. Consumers must choose the alias that matches privilege level and engine semantics, not infer that aliases are independent registers.
- `GRBM_GFX_INDEX` and the GRBM shadow-register select/data windows affect register targeting. Incorrect selection can program the wrong shader engine, shader array, instance, or VF/PF context.
- RLC, CGTS, CGTT, and SQ power-throttle registers affect firmware execution and clock/power state. Uncoordinated writes can desynchronize RLC/SMU policy, clock gates, or harvested-unit masks.
- SR-IOV, per-VF framebuffer aperture, IOMMU, ATS, doorbell, scheduler, and SDMA status offsets are isolation-sensitive. Incorrect programming can corrupt virtual function scheduling or memory partitioning.
- Indirect windows such as SRM RAM, CP microcode address/data, RLC GPU IOV scratch, GDS burst/atomic windows, and SQ wave debug indexes require strict address/data sequencing and status polling.
- The chunk begins and ends mid-file. The final merged per-file report must connect this research with adjacent chunks for the earlier part of `xcd0_gc_gfxudec` and the remaining SQ indirect register indexes.

## Test and Validation Signals

Useful validation is mostly build, bring-up, and hardware integration coverage:

- Compile AMDGPU and KFD code paths that include `gc/gc_9_4_3_offset.h`; missing or renamed macros should fail at build time.
- GC 9.4.3 bring-up and reset tests should exercise `regRLC_CNTL`, `regRLC_STAT`, safe-mode registers, RLC timers, clock counters, SMU command/response offsets, and GRBM targeting.
- Queue and command-submission tests should cover CP ring/IB offsets, CP DMA registers, scratch/semaphore registers, draw/dispatch indirect-address registers, completion status, and coherency registers.
- Performance tooling should validate counter LO/HI reads, selector programming, RLC SPM ring setup, mux selection, sample delays, result-control registers, and UTCL2 ATC/VM/L2TLB counter configuration.
- Debug/profiling tests should cover SQ thread trace, SQ indirect wave status indexes, DB occlusion/Z-pass counters, GDS atomic/OA windows, and GRBM instance selection.
- Power-management tests should cover CGTS/CGTT clock controls, TCC disable state, SQ throttle, RLC power-gating registers, and suspend/resume restoration.
- SR-IOV validation should exercise VF enablement, per-VF framebuffer size/offsets, MARC windows, IOMMU/ATS controls, doorbell set/clear/mask registers, scheduler state, SDMA status/busy status, virtual reset, and interrupt paths.
- Security/PSP diagnostics should verify GRBM security controls, IOV error FIFO data, CAM index/data aliases, DSM bypass handling, and RLC firewall violation reporting.

### subset-b-002684: lines 7414-7450

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h lines 7414-7450

## Scope

This chunk is the end of the generated AMD GC 9.4.3 register-offset header. It covers the tail of the `sqind` address block, specifically shader queue wavefront indirect-register offsets for program counter, instruction words, IB debug state, trap temporary registers, `M0`, execution masks, and SQ interrupt-word aliases. The file closes immediately after these definitions with the header guard `#endif`.

## Purpose

`gc_9_4_3_offset.h` supplies compile-time register numbers for GC 9.4.3 hardware. This range is for SQ indexed registers rather than direct MMIO registers. Driver code passes these `ixSQ_*` offsets through `regSQ_IND_INDEX`/`regSQ_IND_DATA` accessors to inspect per-wavefront state on a selected XCC, SIMD, wave, and sometimes thread.

The constants in this chunk let AMDGPU debug and fault-analysis paths read live shader wave state without embedding raw SQ index values. They are paired with field definitions in `gc_9_4_3_sh_mask.h` when software needs to decode returned register values, especially the `SQ_INTERRUPT_WORD_*` layouts.

## Important API Surface

- `ixSQ_WAVE_PC_LO` and `ixSQ_WAVE_PC_HI` define the low and high parts of the wavefront program counter.
- `ixSQ_WAVE_INST_DW0` and `ixSQ_WAVE_INST_DW1` expose the current or captured instruction doublewords for the selected wave.
- `ixSQ_WAVE_IB_DBG0`, `ixSQ_WAVE_IB_DBG1`, and `ixSQ_WAVE_FLUSH_IB` describe indirect offsets for instruction-buffer debug and flush state.
- `ixSQ_WAVE_TTMP0` through `ixSQ_WAVE_TTMP15` cover the trap temporary register window at offsets `0x026c` through `0x027b`.
- `ixSQ_WAVE_M0`, `ixSQ_WAVE_EXEC_LO`, and `ixSQ_WAVE_EXEC_HI` expose the scalar `M0` register and 64-bit execution mask halves.
- `ixSQ_INTERRUPT_WORD_AUTO_CTXID`, `ixSQ_INTERRUPT_WORD_AUTO_HI`, `ixSQ_INTERRUPT_WORD_AUTO_LO`, `ixSQ_INTERRUPT_WORD_CMN_CTXID`, `ixSQ_INTERRUPT_WORD_CMN_HI`, `ixSQ_INTERRUPT_WORD_WAVE_CTXID`, `ixSQ_INTERRUPT_WORD_WAVE_HI`, and `ixSQ_INTERRUPT_WORD_WAVE_LO` all alias SQ indirect offset `0x20c0`; the different names reflect alternate interpretations of the same interrupt payload.

There are no C functions, types, or structs in this chunk. The public interface is the generated preprocessor namespace of `ix...` constants.

## Control Flow

The header has no direct control flow. Runtime consumers follow the SQ indirect access pattern:

1. Select wave identity fields such as XCC, SIMD, wave, and optionally thread.
2. Program `regSQ_IND_INDEX` with the selected IDs, one of these `ixSQ_*` offsets shifted into `SQ_IND_INDEX__INDEX`, and `SQ_IND_INDEX__FORCE_READ_MASK`.
3. Read `regSQ_IND_DATA` to retrieve the selected wave register. Bulk SGPR/VGPR reads use the same path with `SQ_IND_INDEX__AUTO_INCR_MASK`.

In `amdgpu/gfx_v9_4_3.c`, `wave_read_ind()` implements this pattern. `gfx_v9_4_3_read_wave_data()` uses the constants from this final header region, including `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, `ixSQ_WAVE_INST_DW0`, `ixSQ_WAVE_INST_DW1`, `ixSQ_WAVE_IB_DBG0`, `ixSQ_WAVE_M0`, and neighboring wave-state offsets, to build a type-1 wave dump.

## State and Persistence

The macros are stateless compile-time constants. The hardware state they address is volatile per-wave SQ execution state: program counter, instruction state, instruction-buffer debug state, trap temporary registers, scalar addressing state, and active-lane masks can change as shader waves execute, trap, stall, or retire.

Reads through `regSQ_IND_INDEX`/`regSQ_IND_DATA` are snapshots of selected live hardware state, not persisted driver-owned state. `ixSQ_WAVE_FLUSH_IB` is a control-oriented SQ indexed register, so incorrect use could affect the selected wave's instruction buffer behavior rather than just observing it. The `SQ_INTERRUPT_WORD_*` aliases describe interrupt payload storage/decoding state; the matching mask header determines which bits mean context ID, common high bits, wave fields, or split high/low forms.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.4.3 register specification and must remain synchronized with `gc_9_4_3_sh_mask.h`, especially the `SQ_IND_INDEX` fields and `SQ_INTERRUPT_WORD_*` bit layouts.
- Integrated by `amdgpu/gfx_v9_4_3.c` wave-dump helpers through `WREG32_SOC15_RLC()`, `RREG32_SOC15()`, `GET_INST(GC, xcc_id)`, `regSQ_IND_INDEX`, and `regSQ_IND_DATA`.
- Shares the broader generated-register pattern with neighboring GC 9.x headers; the same symbol names appear in other ASIC headers but may differ across generations, so consumers rely on including the ASIC-specific offset header.
- SQ interrupt-word aliases integrate with KFD and interrupt-processing code conceptually: payload decoding uses `SQ_INTERRUPT_WORD_*` field masks, while this offset header provides the indirect location for GC 9.4.3.

## Risks

- Offset drift is the main risk. A wrong `ixSQ_WAVE_*` value would cause wave dumps to read unrelated SQ state, producing misleading crash diagnostics or bad debugger data.
- The chunk is a partial address-block tail. Earlier wave offsets such as status, trap status, HW ID, and allocation state are defined before line 7414, so merge tooling must combine this chunk with adjacent chunks for complete `sqind` coverage.
- The `ixSQ_INTERRUPT_WORD_*` names intentionally alias the same `0x20c0` offset. Treating them as separate hardware locations would be a documentation or consumer bug; the difference is in payload interpretation, not address.
- Reads of live wave state are timing-sensitive. Without a stopped or stable wave, PC, EXEC, instruction, and TTMP values can change between reads, giving an inconsistent snapshot.
- Any write path using `ixSQ_WAVE_FLUSH_IB` or trap temporary offsets must ensure the selected SIMD/wave/thread context is correct, because SQ indirect selection errors can disturb the wrong wave.

## Test Signals

- Build AMDGPU with GC 9.4.3 support to catch missing or renamed generated macros in `gfx_v9_4_3.c` and related generated-header includes.
- Compare this exact range against the authoritative GC 9.4.3 register source to verify `PC`, `INST`, `IB_DBG`, `TTMP`, `M0`, `EXEC`, and `SQ_INTERRUPT_WORD` offsets.
- Exercise GPU hang or debugfs wave-dump paths on GC 9.4.3 hardware and verify returned PC/EXEC/instruction fields look plausible and match known-good traces.
- Trigger KFD/SQ interrupt scenarios and validate that interrupt-word decoding remains aligned with the shared `0x20c0` offset and the masks in `gc_9_4_3_sh_mask.h`.
- Run suspend/resume and GPU reset recovery tests, then repeat wave-dump collection to catch stale indirect-index programming or ASIC-generation include mismatches.
