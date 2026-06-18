# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 25202-27680

## Purpose

This chunk is generated AMD GC 12.0.0 graphics-core register bitfield metadata. It contains C preprocessor constants only: each register field is represented by a `__SHIFT` value and a `_MASK` value used to pack or decode 32-bit MMIO register values. There are no executable functions, structs, allocation paths, locks, callbacks, or persistence routines in this slice.

The selected range starts in the tail of the texture-address `TA_CNTL_AUX` definition, continues through texture address status and scratch fields, then covers a large render-backend/depth-buffer block, color-buffer/global-backend topology controls, RMI and UTCL1 controls/status, shader-program register layouts for pixel/geometry/hull stages, SPI arbitration and debug controls, TCP watchpoints, RAS signature registers, and the beginning of the command-buffer depth/stencil render-state register set. The final line is inside `DB_SHADER_CONTROL`; the remaining masks for that register continue after this chunk.

Although this path is under a `ceph-client` source tree, the file is AMD GPU driver hardware metadata. It is coupled to the matching GC 12.0.0 register offset header and to AMDGPU/AMDKFD code using `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and table-driven golden-register programming.

## Important APIs, Types, And Macros

The public interface in this chunk is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` identifies the low bit of a hardware field.
- `<REGISTER>__<FIELD>_MASK` identifies the bit range for the same field.
- Register comments such as `//DB_DEBUG`, `//SPI_SHADER_PGM_RSRC1_PS`, or `//DB_RENDER_CONTROL` group field macros by hardware register.
- Address-block comments such as `gc_gfx_se_gfx_se_rbdec`, `gc_gfx_se_rmi_gfx_se_rmidec`, `gc_gfx_se_gfx_se_shdec`, `gc_gfx_se_gfx_se_tcpdec`, and `gc_gfx_se_gfx_se_gfxdec0` group the registers by hardware decode block.

Major register families represented here:

- Texture-address tail: remaining `TA_CNTL_AUX` fields include anisotropic filtering, gather/swizzle behavior, deterministic-mode disables, cubemap slice clamp, small-negative truncation, and array round mode. `TA_CNTL2` adds component-storage, request-id, element-size hash, coordinate truncation, unlit-quad elimination, and PRT-plus accumulation controls. `TA_STATUS` provides FIFO non-empty and busy bits for texture-address subunits, and `TA_SCRATCH` exposes a full-width scratch field.
- Depth/render backend debug and timing: `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_DEBUG5`, `DB_DEBUG6`, and `DB_DEBUG7` cover compression disables, forced depth/stencil reads, HiZ/HiS behavior, fast Z/stencil disables, viewport/z-plane optimization, tile/cache/data-forwarding behavior, coherency stalls, VRS interactions, NOZ behavior, panic/test/spare bits, and several workaround-style controls. `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH1..4`, `DB_RING_CONTROL`, `DB_MEM_ARB_WATERMARKS`, `DB_MEM_CONFIG`, `DB_ARB_CONFIG`, and `DB_SUMMARIZER_TIMEOUTS` describe DB buffering, credits, watermarks, SRAM allocation, arbitration, and timeout tuning.
- Backend topology and color-buffer controls: `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_1`, `GB_BACKEND_MAP`, `GB_GPU_ID`, and `GB_ADDR_CONFIG_READ` encode render-backend harvesting and graphics-block topology such as pipe count, compressed fragments, RBs per shader engine, shader-engine count, pipe interleave size, and packetizer count. `CB_HW_CONTROL_4`, `CB_HW_CONTROL_3`, `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_MEM_ARBITER_CTL`, `CB_FGCG_SRAM_OVERRIDE`, and `CB_CACHE_EVICT_POINTS` cover CB request throttling, DCC/cache behavior, arbitration, SRAM clock gating override, and cache eviction thresholds.
- SPI and shader program state: `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL` define queue/event and export-throttle controls. The shader-decode block defines checksum, program address, resource, user-data, request-control, meshlet, GS output, and accumulator registers for PS, GS/ES, and HS/LS stages. `SPI_SHADER_PGM_RSRC1_*` and `SPI_SHADER_PGM_RSRC2_*` are especially dense, covering VGPR/SGPR counts, priority, float mode, DX10 clamp/debug mode, LDS size, scratch enable, user SGPR counts, exception enables, shared VGPR count, and similar stage-specific dispatch metadata.
- RMI and UTCL1 memory interface: `RMI_GENERAL_CNTL`, `RMI_GENERAL_CNTL1`, `RMI_GENERAL_STATUS`, `RMI_SUBBLOCK_STATUS0..3`, `RMI_XBAR_CONFIG`, `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_DEMUX_CNTL`, `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, formatter controls, scoreboard controls/status, crossbar arbiter controls, clock controls, CID mapping, XNACK debug, spare registers, and `CC_RMI_REDUNDANCY` describe routing, backpressure, UTCL1 behavior, scoreboard state, interface clocking, and redundancy. The separate `UTCL1_CTRL_1`, `UTCL1_HASH_CTRL`, `UTCL1_ALOG`, and `UTCL1_STATUS` registers describe UTCL1 request buffering, hash/client behavior, address logging, and status.
- SPI arbitration/debug and TCP watchpoints: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0/1`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_COMPUTE_WF_CTX_SAVE`, and `SPI_SAVE_RESTORE_STATUS` define SPI scheduling weights, wave-context limits, per-VMID debug accumulation, queue reset, and wavefront context-save status. `TCP_WATCH0..3_ADDR_H/L` and `TCP_WATCH0..3_CNTL` define four TCP memory-watch channels with address, mask, mode, and VMID controls.
- RAS signatures: `RAS_SIGNATURE_CONTROL`, `RAS_SIGNATURE_MASK`, and per-block signature registers for SX, DB, PA, SC, SPI, CB, BCI, and GE expose RAS signature collection/inspection points.
- Draw/depth state: `DB_RENDER_CONTROL`, `DB_DEPTH_VIEW`, `DB_DEPTH_VIEW1`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_DEPTH_SIZE_XY`, `DB_Z_INFO`, `DB_STENCIL_INFO`, depth/stencil read/write base registers, `DB_GL1_INTERFACE_CONTROL`, `DB_MEM_TEMPORAL`, depth bounds, `DB_COUNT_CONTROL`, `DB_VIEWPORT_CONTROL`, `DB_SPI_VRS_CENTER_LOCATION`, and the beginning of `DB_SHADER_CONTROL` describe depth/stencil clear/copy/decompress behavior, view selection, render overrides, surface dimensions, Z/stencil formats and swizzle modes, base addresses, GL1 speculation/compression modes, temporal hints, occlusion/count controls, viewport clamp, VRS sample centers, and shader/depth interaction.

Several definitions are full-width masks, including scratch or address-base fields such as `TA_SCRATCH__SCRATCH_MASK`, `DB_DFD_INDIRECT_DAT__DAT_MASK`, depth/stencil base fields, depth bounds, and RAS signature fields. Full-width masks are packing metadata only; they do not imply the register is safe for arbitrary writes.

## Control Flow

This header has no direct runtime control flow. The operational flow is indirect:

1. GC 12 code includes `gc/gc_12_0_0_sh_mask.h` together with `gc/gc_12_0_0_offset.h`.
2. A call site chooses a register offset, for example `regGB_ADDR_CONFIG`, `regRMI_GENERAL_CNTL`, `regSPI_SHADER_PGM_RSRC1_PS`, `regDB_RENDER_CONTROL`, or `regDB_SHADER_CONTROL`.
3. The call site composes or decodes a register value using field helpers such as `REG_SET_FIELD` or `REG_GET_FIELD`, which rely on the exact `__SHIFT` and `_MASK` names in this file.
4. The value is read from or written to hardware through SOC15 register helpers, debug register accessors, firmware/golden-register tables, queue setup, reset paths, power-management restore paths, or draw/dispatch state programming.

Concrete in-tree consumers for this GC 12 namespace include:

- `amdgpu/gfx_v12_0.c`, which includes this header and reads `regGB_ADDR_CONFIG`; it decodes `GB_ADDR_CONFIG` fields into `adev->gfx.config.gb_addr_config_fields` for packetizers, pipes, compressed fragments, RBs per SE, shader engines, and pipe interleave.
- `amdgpu/imu_v12_0.c`, which programs golden values for registers in this range, including repeated per-index `regRMI_GENERAL_CNTL` writes and `regGB_ADDR_CONFIG`.
- `amdgpu/soc24.c`, which exposes `regGB_ADDR_CONFIG` through the device register read path and returns the cached `adev->gfx.config.gb_addr_config` value when available.
- `amdgpu/mes_v12_0.c`, `amdgpu/sdma_v7_0.c`, and `amdgpu/gfxhub_v12_0.c`, which include the GC 12.0.0 generated register namespace for adjacent queue, SDMA, and VM/cache programming.
- Display code such as `display/amdgpu_dm/amdgpu_dm_plane.c`, which reads `regGB_ADDR_CONFIG` through the same field helpers to derive tiling/display-plane layout information.

## State And Persistence Behavior

The file stores no software state. It describes hardware state that may be software-programmed, hardware-owned, sticky, read-only, write-only, self-clearing, indexed per shader engine, or restored by firmware depending on the register.

The most visible persistent software state tied to this chunk is `adev->gfx.config.gb_addr_config` and its decoded `gb_addr_config_fields`, populated from `GB_ADDR_CONFIG` in GC 12 initialization and reused by SOC24 register reporting and display/tiling paths. Incorrect masks for those fields can persist wrong topology assumptions after initialization.

Other represented state includes DB debug/workaround configuration, DB FIFO and arbitration watermarks, CB hardware controls, RMI routing/status/scoreboard state, UTCL1 address-translation controls/status, shader-program resource descriptors, TCP watchpoint configuration, RAS signature registers, depth/stencil surface state, and draw-time depth/shader controls. Some fields remain programmed until GPU reset, suspend/resume restore, power-gating restore, firmware reinitialization, context-state load, or explicit driver writes. Status, busy, scoreboard, fault, and signature fields are generally hardware-produced observations, while debug, DSM/spare, watchpoint, and override fields can perturb execution when written.

The header does not encode access permissions, reset defaults, broadcast/indexing semantics, reserved-bit requirements, sequencing requirements, or whether a field is latched or self-clearing. Call sites must preserve unrelated bits, use the matching offset header, and follow ASIC programming-guide ordering.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h`. In that file, this chunk's registers map to offsets such as `regTA_CNTL_AUX`, `regTA_CNTL2`, `regDB_DEBUG`, `regDB_DEBUG5`, `regGB_ADDR_CONFIG`, `regGB_ADDR_CONFIG_1`, `regGB_ADDR_CONFIG_READ`, `regRMI_GENERAL_CNTL`, `regRMI_UTCL1_CNTL1`, `regUTCL1_CTRL_1`, `regSPI_SHADER_PGM_RSRC1_PS`, `regSPI_ARB_PRIORITY`, `regTCP_WATCH0_CNTL`, `regRAS_SIGNATURE_CONTROL`, `regDB_RENDER_CONTROL`, `regDB_COUNT_CONTROL`, and `regDB_SHADER_CONTROL`.

Integration points include:

- GC 12 graphics initialization and topology discovery in `gfx_v12_0.c`.
- IMU/RLC golden-register programming in `imu_v12_0.c`.
- SOC24 register-access/debug paths in `soc24.c`, especially indexed register access guarded by `adev->grbm_idx_mutex`.
- MES, SDMA, GFXHUB, KFD, and display code that compiles in the same generated GC 12 namespace and relies on shift/mask compatibility.
- Clear-state and context-state programming for draw/depth registers such as `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, and `DB_SHADER_CONTROL`.
- Hardware diagnostics, perf/debug, RAS, TCP watchpoint, and register-dump tooling that decodes status/signature/watch registers from this range.

The chunk has artificial boundaries. It starts after the first `TA_CNTL_AUX` fields and ends before all `DB_SHADER_CONTROL` masks are visible, so adjacent chunks are required before making whole-register or whole-file statements about either boundary register.

## Risks And Edge Cases

- Header/offset mismatch is the primary risk. Using GC 12.0.0 masks with another generation's offset header can compile while silently decoding or programming the wrong bits.
- Dense debug/control registers such as `DB_DEBUG*`, `DB_RENDER_OVERRIDE*`, `CB_HW_CONTROL*`, `RMI_*CNTL*`, and `SPI_SHADER_PGM_RSRC*` contain many adjacent fields. A stale shift or mask can corrupt unrelated behavior without a compiler warning.
- `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_1`, and `GB_ADDR_CONFIG_READ` are topology-sensitive and feed persistent driver configuration. Wrong decoding can break tiling, render-backend harvesting assumptions, display-plane layout, compressed-fragment handling, or pipe interleave calculations.
- `DB_DEBUG*` and `DB_RENDER_OVERRIDE*` fields can disable compression, fast paths, coherency stalls, z-plane optimizations, or NOZ behavior. Mistakes may appear only as workload-specific hangs, depth/stencil corruption, VRS artifacts, performance cliffs, or power regressions.
- RMI and UTCL1 fields influence memory-interface routing, XNACK behavior, address translation, scoreboard handling, and crossbar arbitration. Incorrect programming can produce stale translations, bad backpressure, memory-ordering faults, or hard-to-reproduce GPU hangs.
- Shader program resource fields are ABI-like hardware descriptors. Incorrect VGPR/SGPR, LDS, scratch, exception, shared-VGPR, or user-SGPR masks can break dispatch, trap/debug behavior, context save/restore, or shader execution only for specific stages.
- TCP watchpoint and SPI debug controls are diagnostic-sensitive. Wrong VMID, mask, mode, or queue-reset fields can miss real faults, trigger false debug events, or disrupt active compute queues.
- RAS signature registers and masks must remain aligned with hardware reliability tooling; misdecoding signatures can hide real error signatures or create false telemetry.
- The header exposes reserved, spare, and full-width fields. Visible masks should not be treated as safe production write masks without ASIC-specific documentation.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware-oriented smoke and regression coverage:

- Build coverage for AMDGPU, MES, SDMA, GFXHUB, KFD, display, and IMU/RLC paths that include `gc_12_0_0_sh_mask.h` with `gc_12_0_0_offset.h`.
- Generated-header checks that each `__SHIFT` has the intended `_MASK`, masks align with shifts, fields do not overlap within a register except documented aliases/full-width fields, and register names match `gc_12_0_0_offset.h`.
- Static comparison against the authoritative GC 12.0.0 register database for this line range, with special attention to repeated shader user-data registers, TCP watch channels, RMI scoreboard/status fields, and `DB_SHADER_CONTROL` continuation across the chunk boundary.
- Topology/init tests confirming `gfx_v12_0.c` decodes `GB_ADDR_CONFIG` into expected `adev->gfx.config` values and that `soc24.c` reports the cached value correctly.
- Golden-register tests for `imu_v12_0.c` values touching `regRMI_GENERAL_CNTL` and `regGB_ADDR_CONFIG`, verifying mask/value pairs preserve non-target fields and match ASIC defaults.
- Graphics tests stressing depth/stencil clears, copies, decompression, HTILE/HiZ/HiS behavior, Z/stencil formats, depth bounds, occlusion counts, VRS center locations, and shader depth/export behavior.
- Suspend/resume, GPU reset, runtime power-management, and SR-IOV smoke tests that cover restoration of DB/CB/RMI/UTCL1/SPI state.
- RAS/debug tests for signature collection, TCP watchpoints, SPI per-VMID debug accumulation, compute queue reset/context-save status, RMI status/scoreboard reads, and UTCL1 address logging.
