# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 7585-9915

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it publishes C preprocessor constants that describe the shift and mask layout of 32-bit graphics-core MMIO registers. Runtime AMDGPU and AMDKFD code pairs these constants with the matching register offset macros from `gc_11_0_0_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and golden-register programming helpers.

The selected range starts at the tail of texture-addressing control metadata, then covers GDS control/status and fault/EDC fields, render-backend depth/color block controls, global backend/address configuration, and two GCEA address-block regions for memory/IO arbitration, SDP credits, MAM controls, EDC counters, and diagnostic/error-injection controls. The final lines end inside `GCEA_DSM_CNTL2A`, so that register is only partially visible in this chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, dynamic allocations, callbacks, locks, or local includes in this slice. The exposed API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the same field.
- Register comments such as `//GDS_CNTL_STATUS` or `//GCEA_SDP_ARB_FINAL` group the field macros by hardware register.
- Address-block comments such as `// addressBlock: gc_gdsdec`, `gc_rbdec`, `gc_gceadec`, and `gc_gceadec2` group related register families.

Major register families in this chunk:

- Texture address tail: the chunk begins with remaining `TA_CNTL_AUX` masks, then defines `TA_CNTL2` point-sample acceleration, coordinate truncation, and unlit-quad elimination fields, plus `TA_STATUS` FIFO-empty and busy bits and a full-width `TA_SCRATCH` field.
- GDS decode block: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, `GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`, `GDS_EDC_CNT`, `GDS_EDC_GRBM_CNT`, `GDS_EDC_OA_DED`, `GDS_DSM_CNTL`, `GDS_EDC_OA_PHY_CNT`, `GDS_EDC_OA_PIPE_CNT`, and `GDS_DSM_CNTL2` describe global data share busy state, clamp/status bits, auto-increment/restore behavior, protection-fault attribution, VM fault attribution, ECC/EDC counters, per-ME/pipe/physical/PQ EDC reporting, and diagnostic scan/error-injection controls.
- Render backend/depth block: `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_DEBUG5`, `DB_DEBUG6`, and `DB_DEBUG7` expose many ASIC workaround, bypass, panic, clock-gating, conflict, coherency, VRS, HTILE, DTT, OSB, and test controls. Stutter, credit, watermark, FIFO-depth, last-of-burst, memory-arbiter, exception, and fine-grain clock-gating registers describe depth-buffer pipeline timing, resource limits, and error handling.
- RB/GB/CB configuration: `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `CC_RB_DAISY_CHAIN`, `GB_ADDR_CONFIG_READ`, `CB_HW_CONTROL_4`, `CB_HW_CONTROL_3`, `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_DCC_CONFIG`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, `CB_FGCG_SRAM_OVERRIDE`, `CHICKEN_BITS`, and `CB_CACHE_EVICT_POINTS` cover render-backend enablement/harvesting, address tiling geometry, daisy-chain wiring, color-buffer hardware queues, DCC cache sizing, arbitration, SRAM clock-gating override, and cache eviction thresholds.
- GCEA DRAM/IO arbitration: DRAM and IO read/write `CLI2GRP_MAP0/1` registers map client IDs 0 through 31 into four groups. `GRP2VC_MAP`, `LAZY`, `CAM_CNTL`, page/group burst limits, priority age/queueing/fixed/urgency coefficients, urgency masking, and quantization threshold registers define how those groups are assigned virtual channels and how request age, urgency, accumulation, reorder depth, and burst behavior affect arbitration.
- GCEA SDP controls: `GCEA_SDP_ARB_FINAL` defines DRAM/GMI/IO burst limits, burst multiplier, read-only virtual-channel flags, error event/halt behavior, burst stretch, and DRAM/GMI read/write throttles. `GCEA_SDP_IO_PRIORITY`, `GCEA_SDP_CREDITS`, tag reserve, and VCC reserve registers define final SDP priority and credit reservation policy.
- GCEA miscellaneous/MAM/EDC/DSM: `GCEA_MISC` selects relative priority modes, early write-return behavior, link-manager thresholds, command-stream preference, and write-to-read switching policy. `GCEA_LATENCY_SAMPLING` selects sampler traffic domains, operation classes, and virtual-channel masks. `GCEA_MAM_CTRL2` and `GCEA_MAM_CTRL` configure MAM/ARAM/DBIT tracking, flush behavior, interrupt generation, ring-buffer sizing, and address high bits. `GCEA_EDC_CNT` and `GCEA_EDC_CNT2` expose SEC/DED/SED counters for DRAM, GMI, IO, return-tag, page, and MAM memories. `GCEA_DSM_CNTL`, `GCEA_DSM_CNTLA`, and `GCEA_DSM_CNTL2` define DSM irritator data, single-write controls, and error-injection enable/delay fields; `GCEA_DSM_CNTL2A` begins in this chunk and continues after line 9915.

Most constants use the generated `0x...L` literal form. Several fields are full-width masks such as `TA_SCRATCH__SCRATCH_MASK`, `DB_DEBUG7__SPARE_BITS_MASK`, and `CHICKEN_BITS__SPARE_MASK`; full-width masks are still just packing definitions and do not imply that all bits are safe to write.

## Control Flow

This header has no runtime control flow. Its operational flow is indirect:

1. GC 11 code includes `gc/gc_11_0_0_sh_mask.h` with the corresponding `gc/gc_11_0_0_offset.h`.
2. A driver path chooses a register address using `reg*` offset macros, for example `regGDS_CONFIG`, `regDB_DEBUG4`, `regCB_DCC_CONFIG`, `regGCEA_SDP_ARB_FINAL`, `regGCEA_MISC`, or `regGCEA_DSM_CNTL2A`.
3. The code composes or decodes register values using the shift/mask macros from this header through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`.
4. The result is read from or written to hardware with SOC15 register helpers, firmware tables, golden-register programming, queue setup, reset, power-management, or debug/error paths.

Known consumers in this tree include `amdgpu/gfx_v11_0.c`, `amdgpu/gfxhub_v3_0.c`, `amdgpu/sdma_v6_0.c`, `amdgpu/mes_v11_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/imu_v11_0_3.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdkfd/kfd_mqd_manager_v11.c`, `amdkfd/kfd_device_queue_manager_v11.c`, and `display/amdgpu_dm/amdgpu_dm_plane.c`. For this chunk specifically, `gfx_v11_0.c` reads `TA_CNTL2__TRUNCATE_COORD_MODE`, uses `GB_ADDR_CONFIG` fields to derive render-backend layout, and exposes `regGDS_PROTECTION_FAULT` in debug register lists; IMU golden tables program `regGCEA_SDP_ARB_FINAL` with masks/value pairs.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes bit positions for hardware state owned by the GPU.

The represented hardware state includes texture-addressing status, GDS busy/fault/EDC/diagnostic state, DB pipeline debug/workaround bits, depth-buffer credits/watermarks/FIFO depths, RB/CB/GB harvesting and tiling configuration, DCC cache configuration, arbitration queues and weights, GCEA client grouping and virtual-channel mapping, SDP credit reservation, MAM/ARAM tracking state, and GCEA EDC counters/error-injection knobs.

Persistence depends on the underlying register semantics, not on this header. Some fields are configuration that remains until reset, suspend/resume restore, power-gating restore, firmware reinitialization, or explicit reprogramming. Some are live status bits, sticky fault indicators, hardware-owned counters, diagnostic strobes, write-one-to-clear fields, or test/error-injection fields. The header does not encode read-only/write-only, self-clearing, latched, privileged, broadcast, per-instance, golden-default, or reserved-bit behavior, so call sites must preserve unrelated fields and follow ASIC programming-guide ordering.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides the actual register offsets and base indices. In that file, this chunk's registers are represented by entries such as `regGDS_CONFIG`, `regDB_DEBUG`, `regDB_DEBUG4`, `regCB_DCC_CONFIG`, `regGCEA_SDP_ARB_FINAL`, `regGCEA_MISC`, and `regGCEA_DSM_CNTL2A`.

This generated metadata integrates with:

- AMDGPU GC 11 initialization and reset code, especially `gfx_v11_0.c`, which reads and writes many GC fields through `REG_SET_FIELD`/`REG_GET_FIELD`.
- GFX hub VM/cache code in `gfxhub_v3_0.c`; that file mostly uses neighboring VM macros, but it is compiled in the same GC 11 register namespace and demonstrates the expected shift/mask helper pattern.
- IMU/RLC firmware and golden-register setup in `imu_v11_0.c` and `imu_v11_0_3.c`, where `regGCEA_SDP_ARB_FINAL` is programmed by table-driven mask/value writes.
- KFD/MES/MQD paths for compute queue setup and scheduling, which include the same GC 11 generated header and rely on consistent field definitions across CP, GDS, and shader-related register families outside and around this chunk.
- Display/plane code that includes GC 11 masks for tiling/address configuration interoperability with DCC, render-backend, and memory layout metadata.
- Hardware diagnostics and debugfs-style paths that expose or decode `GDS_PROTECTION_FAULT`, busy/status, EDC, and DSM/error-injection registers.

The chunk is part of a larger generated header. Adjacent chunks are required for the complete `TA_CNTL_AUX` definition before line 7585 and the complete `GCEA_DSM_CNTL2A`/later GCEA definitions after line 9915.

## Risks And Edge Cases

- Header/offset mismatch is the main integration risk. Using GC 11.0.0 masks with a different GC offset header can compile but program wrong fields or wrong registers.
- The constants are untyped preprocessor macros. Field misuse can silently corrupt unrelated bits in control registers, especially debug/workaround, arbitration, and error-injection registers with dense bit layouts.
- Reserved and spare fields are explicitly present, including `UNUSED`, `SPARE`, `CHICKEN_BITS`, and full-width debug/scratch definitions. Call sites must not infer that a visible mask is safe to set on production hardware.
- GDS protection-fault and VM-protection-fault fields are attribution-sensitive. Misdecoded SE/SA/WGP/SIMD/wave/VMID/address fields can send debugging, fault recovery, or telemetry down the wrong path.
- EDC and DSM registers are reliability-sensitive. Incorrect counter decoding, single-write/irritator settings, or error-injection enables can hide real memory errors or create artificial faults during normal operation.
- DB and CB debug/control registers include many ASIC workaround, bypass, panic, coherency, clock-gating, and cache behavior bits. Small mistakes may only surface as hangs, depth/stencil corruption, DCC corruption, VRS artifacts, power regressions, or workload-specific performance cliffs.
- GB address and backend fields drive tiling and render-backend topology. Incorrect masks or stale assumptions around `GB_ADDR_CONFIG`, backend disabling, daisy-chain fields, or `GB_ADDR_CONFIG_READ` can break memory layout, RB harvesting, or address calculations.
- GCEA arbitration knobs can create starvation or severe latency/bandwidth regressions. Client-to-group maps, group-to-VC maps, urgency masking, priority coefficients, CAM depths, and burst limits need ASIC-specific defaults and workload validation.
- `GCEA_SDP_ARB_FINAL` includes error event/halt and throttle bits. Golden-register values or firmware tables that mask the wrong bits can alter final fabric behavior for DRAM, GMI, or IO traffic.
- The chunk boundary is artificial. `TA_CNTL_AUX` is only a tail fragment and `GCEA_DSM_CNTL2A` is only the first six shift fields here, so the later merge lane must reconcile adjacent chunks before producing a whole-file report.

## Test Signals

Useful validation is mostly generated-header consistency, build coverage, and hardware smoke/regression coverage:

- Build AMDGPU, AMDKFD, MES, SDMA, display, and IMU/RLC paths that include `gc_11_0_0_sh_mask.h` together with `gc_11_0_0_offset.h`.
- Generated-header checks that every visible `__SHIFT` has the intended matching `_MASK`, masks align with shifts, fields do not overlap within a register except documented aliases/full-register fields, and register names match offset-header entries.
- Static comparison against the authoritative generated register database for GC 11.0.0, especially for replicated DRAM/IO client maps, urgency masks, quantization thresholds, and DSM/EDC counter layouts.
- Golden-register programming tests for `regGCEA_SDP_ARB_FINAL` and neighboring IMU/RLC tables, verifying mask/value pairs leave reserved bits and non-targeted fields unchanged.
- GPU bring-up, reset, suspend/resume, runtime power-management, and SR-IOV tests that exercise DB/CB/GB/GDS/GCEA state initialization and restoration.
- GDS tests covering queue use of global data share, GWS/OA interactions, protection faults, VM protection faults, EDC counter reporting, and diagnostic/error-injection paths on controlled hardware.
- Graphics tests stressing depth/stencil, HTILE, VRS, DCC, render-backend harvesting, tiling, MSAA/subtile layouts, cache eviction, and last-of-burst behavior; failures can appear as corrupted depth/color output, hangs, or workload-specific performance regressions.
- Memory and fabric performance tests for DRAM, GMI, and IO traffic to catch GCEA client grouping, virtual-channel assignment, priority, urgency, CAM, lazy accumulation, burst, and throttle mistakes.
- Fault-injection and reliability tests for GCEA and GDS EDC/DSM controls, with explicit checks that injected errors are reported only in the expected SEC/DED/SED counters and that production paths leave injection disabled.
