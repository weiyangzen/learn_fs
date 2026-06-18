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
