# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 5026-7369

## Scope

This chunk is a generated AMD GC 11.5.0 graphics-core register field header. It contains `#define` constants for bit shifts and bit masks, not executable C. The assigned range starts in the middle of the `gc_rbdec` `DB_DEBUG` register definition, continues through depth-buffer, color-buffer, graphics backend, GCEA, SPI, and RMI register blocks, and ends in the middle of `RMI_UTCL1_CNTL1`. The companion offset header (`gc_11_5_0_offset.h`) supplies register addresses; this file supplies the field layouts used by register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD`.

Because this is a generated hardware interface header, the "APIs" are the macro names themselves. The stable convention is:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned bit mask.
- Register names align with `reg*` or `mm*` address symbols in the matching offset header.

## Purpose

The chunk describes how software should pack and unpack register values for several GC subblocks:

- `gc_rbdec`: render backend/depth buffer/color buffer controls, including DB debug and stutter controls, DB FIFO depths, RB redundancy/backend disable mapping, GB address layout, CB hardware controls, CB DCC/cache behavior, and CB memory arbiters.
- `gc_gceadec`, `gc_gceadec2`, `gc_gceadec3`: Graphics Coherent Engine Arbiter and EA/SDP controls. These cover client-to-group mapping, group-to-VC mapping, request combining/flushing, arbitration priority coefficients, burst limits, credit/tag/VC reservation, MAM controls, EDC counters, error status, probe routing, and SDP enable/request control.
- `gc_spipdec2`: SPI queue/event and export throttling controls.
- `gc_rmi_rmidec`: RMI global controls, status, subblock FIFO counters, crossbar configuration, UTC/XNACK controls, demux controls, and the beginning of UTCL1 control fields.

The values are hardware ABI. Driver code must use them exactly as published for GC 11.5.0; a one-bit drift can make register programming target the wrong hardware behavior.

## Important Register Groups

### DB and RB/GB/CB fields

The range begins with the tail of `DB_DEBUG` masks and then defines `DB_DEBUG2` through `DB_DEBUG7`, `DB_DEBUG5`, stutter controls, FIFO-depth registers, and backend topology registers.

Key DB fields include:

- Compression and fast-path debug controls: `DB_DEBUG__DEBUG_FAST_Z_DISABLE_MASK`, `DB_DEBUG__DEBUG_FAST_STENCIL_DISABLE_MASK`, `DB_DEBUG2__ALLOW_COMPZ_BYTE_MASKING_MASK`, `DB_DEBUG3__DISABLE_ZCMP_DIRTY_SUPPRESSION_MASK`, and `DB_DEBUG5__DISABLE_Z_LIMIT_SUMM_MASK`.
- Cache and memory behavior toggles: `DB_DEBUG2__DISABLE_TC_ZRANGE_L0_CACHE_MASK`, `DB_DEBUG2__DISABLE_TC_MASK_L0_CACHE_MASK`, `DB_DEBUG4__DISABLE_MCC_BURST_FIFO_MASK`, `DB_DEBUG4__WR_MEM_BURST_CTL_MASK`, and `DB_FREE_CACHELINES__FREE_Z_ONLY_MASK`.
- Synchronization and hazard behavior: `DB_DEBUG__DISABLE_DEPTH_SURFACE_SYNC_MASK`, `DB_DEBUG__DISABLE_HTILE_SURFACE_SYNC_MASK`, `DB_DEBUG4__DISABLE_PREZ_POSTZ_DTILE_CONFLICT_STALL_MASK`, `DB_DEBUG5__DISABLE_EVENT_INSERTION_AFTER_ZPC_BEFORE_CONTEXT_DONE_MASK`.
- Clock and power controls: `DB_FGCG_SRAMS_CLK_CTRL__OVERRIDE0_MASK` through `OVERRIDE31_MASK`, plus `DB_FGCG_INTERFACES_CLK_CTRL__DB_*_OVERRIDE_MASK`.
- Resource sizing: `DB_FIFO_DEPTH1`, `DB_FIFO_DEPTH2`, `DB_FIFO_DEPTH3`, `DB_FIFO_DEPTH4`, `DB_WATERMARKS`, `DB_MEM_ARB_WATERMARKS`, and `DB_CREDIT_LIMIT`.

Backend topology and address mapping fields include `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, `GB_BACKEND_MAP`, `GB_GPU_ID`, and `CC_RB_DAISY_CHAIN`. These expose the number of pipes, pipe interleave size, compressed fragment limit, number of packers, shader engines, RBs per shader engine, backend disable masks, and RB ordering. These values are commonly used by graphics initialization and memory tiling logic to derive how render backends map to the memory system.

The CB section defines:

- `CB_KEY_OVERRIDE_0` through `CB_KEY_OVERRIDE_7`, all full-register override fields.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, and `CB_HW_CONTROL_4`, covering color-cache fetch policy, SMT scoring, shader/blend optimizations, early write acknowledgements, NACK processing, DCC/VRS/FMAsk options, serializer optimization, and pixel-in-quad handling.
- `CB_DCC_CONFIG` and `CB_DCC_CONFIG2`, covering sample mask tracking, constant encode disable, read-return FIFO depth, DCC cache tag count, and DCC key-disable behavior.
- `CB_HW_MEM_ARBITER_RD` and `CB_HW_MEM_ARBITER_WR`, which define read/write memory arbiter modes, age handling, CC/DC weights, decay behavior, age/weight scaling, and last-beat grouping.
- `CB_CACHE_EVICT_POINTS`, which controls high/low points for CC/DC cache eviction.

### GCEA client mapping, priority, and credit fields

The GCEA span is the largest part of this chunk. It begins at `gc_gceadec` with DRAM read/write client-to-group maps:

- `GCEA_DRAM_RD_CLI2GRP_MAP0/1` and `GCEA_DRAM_WR_CLI2GRP_MAP0/1` assign client IDs `CID0` through `CID31` to 2-bit groups.
- `GCEA_IO_RD_CLI2GRP_MAP0/1` and `GCEA_IO_WR_CLI2GRP_MAP0/1` perform the same mapping for IO paths.
- `GCEA_DRAM_RD_GRP2VC_MAP` and `GCEA_DRAM_WR_GRP2VC_MAP` map request groups to virtual channels.

The arbitration and pacing fields include:

- Lazy/combining controls: `GCEA_DRAM_RD_LAZY`, `GCEA_DRAM_WR_LAZY`, `GCEA_IO_RD_COMBINE_FLUSH`, and `GCEA_IO_WR_COMBINE_FLUSH`.
- CAM controls: `GCEA_DRAM_RD_CAM_CNTL` and `GCEA_DRAM_WR_CAM_CNTL`, including pipe selection, pop-policy, force-on-clash fields, chain limits, and refill-chain enable.
- Burst limits: `GCEA_DRAM_PAGE_BURST` and `GCEA_IO_GROUP_BURST`.
- Priority inputs: `GCEA_*_PRI_AGE`, `GCEA_*_PRI_QUEUING`, `GCEA_*_PRI_FIXED`, `GCEA_*_PRI_URGENCY`, and `GCEA_*_PRI_QUANT_PRI1/2/3`.
- Urgency masking: `GCEA_IO_RD_PRI_URGENCY_MASKING` and `GCEA_IO_WR_PRI_URGENCY_MASKING`, which provide mask-enable/mask-value pairs for many request classes such as SDMA, CP, CB, DB, TCP, SQC, and semaphores.

The SDP and VC reservation section defines:

- `GCEA_SDP_ARB_DRAM` and `GCEA_SDP_ARB_FINAL` for read/write burst limits, early switch conditions, chain breaking, readonly VCs, error event/halt request behavior, and per-path throttles.
- `GCEA_SDP_DRAM_PRIORITY` and `GCEA_SDP_IO_PRIORITY` for 4-bit read/write group priorities.
- `GCEA_SDP_CREDITS`, `GCEA_SDP_TAG_RESERVE0/1`, `GCEA_SDP_VCC_RESERVE0/1`, and the start of VCD reserve handling around the `gc_gceadec2` boundary.
- `GCEA_SDP_REQ_CNTL` for pass-PW overrides, request-chain overrides, inner domain mode, and block-level fields for read/write/atomic traffic.
- `GCEA_SDP_ENABLE__SDP_ENABLE_MASK`, a simple enable bit near the `gc_gceadec3` section.

The MAM and error-observability fields include:

- `GCEA_MISC` and `GCEA_MISC2`, with relative priority mode bits, early write-return enables per VC, link-manager thresholds, chain-switch behavior, and an `INTERLEAVE_PRI_WITHIN_QUANTUM` control.
- `GCEA_LATENCY_SAMPLING`, which selects sampler paths, operation types, and VCs.
- `GCEA_MAM_CTRL` and `GCEA_MAM_CTRL2`, controlling MAM disable, DBIT/ARAM coalescing, flush tracker operations, SDP priority, ARAM tracking geometry, and forced query-dirty behavior.
- `GCEA_EDC_CNT`, `GCEA_EDC_CNT2`, and `GCEA_EDC_CNT3`, which expose compact 2-bit SEC/DED/SED counters for command, data, page, tag, and MAM memories across DRAM, IO, GMI, read-return, and write-return paths.
- `GCEA_GL2C_XBR_MAXBURST`, `GCEA_PROBE_CNTL`, `GCEA_PROBE_MAP`, and `GCEA_ERR_STATUS`. `GCEA_ERR_STATUS` includes SDP read/write response status bits, dataparity error bits, request-type error bits, error-source fields, and `CLEAR_ERROR_STATUS`.
- `GCEA_RRET_MEM_RESERVE` with read-return tag/VC credit reserve fields.

### SPI fields

The `gc_spipdec2` section is small:

- `SPI_PQEV_CTRL` has `NUM_QUEUES` and `PQEV_ENABLE` fields.
- `SPI_EXP_THROTTLE_CTRL` controls export throttling with enable, period, upstep/downstep, low/high stall monitor history counts, stall threshold, skew count, and throttle reset.

These fields sit in the shader processor/input side of graphics scheduling and export pacing. They are likely programmed by GPU initialization tables or firmware-assisted paths, not ordinary hot-path drawing code.

### RMI fields

The `gc_rmi_rmidec` section defines RMI control and status:

- `RMI_GENERAL_CNTL` exposes burst disable, VMID bypass enable bitmap, RB0 harvest enable, and loopback-disable-by-request-type fields.
- `RMI_GENERAL_CNTL1` controls early write acknowledgements per memory type, 64-byte read stall modes for two TCIW paths, loopback early-WRACK disable, policy override, arbiter address-change enable, and last-of-burst insertion disable.
- `RMI_GENERAL_STATUS` reports combined RMI errors, skid FIFO over/underflow, crossbar busy, scoreboard busy, TCIW formatter/return formatter busy, read/write consumer FIFO busy, and skid FIFO free-space-zero error.
- `RMI_SUBBLOCK_STATUS0` through `RMI_SUBBLOCK_STATUS3` expose UTC external latency FIFO occupancy/full/empty state, TCIW inflight counters, skid FIFO free space, PRT FIFO usage, and total free space.
- `RMI_XBAR_CONFIG` exposes mux override, request-type override, CB/DB override, arbiter disable, request-enable masks, request override, and RB0 enable.
- `RMI_PROBE_POP_LOGIC_CNTL` controls external latency FIFO depths and translation-combine behavior.
- `RMI_UTC_XNACK_N_MISC_CNTL` controls XNACK timer increment/start values, UTCL1 permission mode, and CP VMID reset request disable.
- `RMI_DEMUX_CNTL` defines demux arbiter override, stall timer, and mode fields for two arbiters.
- `RMI_UTCL1_CNTL1` begins at the end of this chunk. The assigned range covers shifts through `REG_INV_VMID`; the masks and remaining fields continue in the following chunk.

## Control Flow

There is no local control flow. The runtime flow exists in consumers:

1. Code includes `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h`.
2. It reads or builds a 32-bit register value using `RREG32*`/literal defaults.
3. It applies fields with helpers such as `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` or extracts fields with `REG_GET_FIELD(value, REGISTER, FIELD)`.
4. It writes the value with `WREG32*`, or records field metadata through macros such as `SOC15_REG_FIELD`.

The only direct C include of this exact GC 11.5.0 mask header found in this tree is `amdgpu/gfxhub_v11_5_0.c`, which uses this mask-header family for GPUVM/GFXHUB register programming. The DB/CB/GCEA/RMI symbols in this chunk are also consistent with programming patterns in neighboring AMDGPU generations: golden register tables set DB/CB/GCEA defaults, RAS/EDC tables use `GCEA_EDC_CNT*` fields for error counters, and error handlers clear or decode `GCEA_ERR_STATUS`.

## State and Persistence

The macros have no storage. They describe volatile MMIO hardware state:

- DB/CB/RB/GB fields affect render backend behavior, cache policy, compression, synchronization, and topology.
- GCEA fields affect request routing, arbitration, virtual-channel pressure, credits, error reporting, and EDC observability.
- SPI fields affect queue/event and export throttling behavior.
- RMI fields affect RMI request handling, XNACK/UTCL1 behavior, crossbar/demux routing, and status reporting.

Register values normally persist only until GPU reset, mode switch, power-gating reset, suspend/resume, or firmware reinitialization. The driver and firmware may reapply golden settings during ASIC initialization or resume. Some status/counter registers are read-only or write-to-clear by convention, notably status/error/counter style registers such as `RMI_GENERAL_STATUS`, `RMI_SUBBLOCK_STATUS*`, `GCEA_EDC_CNT*`, and `GCEA_ERR_STATUS`.

## Dependencies and Integration Points

Primary dependencies:

- `gc_11_5_0_offset.h`: supplies register addresses that pair with these field masks.
- AMDGPU SOC15 access helpers: `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, and golden-register table helpers.
- Bitfield helpers: `REG_SET_FIELD` and `REG_GET_FIELD`, which depend on the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- Hardware/firmware ABI: generated field names and bit positions must match the GC 11.5.0 register specification and firmware expectations.

Important integration surfaces:

- Graphics initialization and golden settings: DB/CB/GCEA/RMI fields are commonly programmed in generation-specific golden register arrays or IMU/RLC initialization tables.
- GPU memory management: `GB_ADDR_CONFIG*`, RMI UTCL1/XNACK controls, and GCEA routing/priority fields interact with memory tiling, GPUVM behavior, and request flow to memory clients.
- RAS/error reporting: `GCEA_EDC_CNT*`, `GCEA_ERR_STATUS`, and RMI status fields are natural inputs to diagnostics, RAS reporting, and hardware-health telemetry.
- Debug and bring-up: `DB_DEBUG*`, `CB_HW_CONTROL*`, `GCEA_PROBE*`, `SPI_EXP_THROTTLE_CTRL`, and `RMI_*STATUS*` fields are likely used when validating silicon, chasing hangs, or tuning performance.

## Risks

- Bitfield mismatch: incorrect shift or mask values can silently program unrelated bits. This is especially dangerous for full-register fields and dense maps such as `GCEA_*_CLI2GRP_MAP*`, `GCEA_*_PRI_*`, and `DB_FGCG_SRAMS_CLK_CTRL`.
- Reserved-bit writes: many fields include `SPARE`, `RESERVED`, or broad unused masks. Callers should preserve reset values unless the hardware spec says a reserved field is writable.
- Cross-generation reuse: field names recur across GC generations, but masks may differ. Code must include the GC 11.5.0 header when targeting GC 11.5.0 rather than borrowing values from `gc_10_3_0`, `gc_11_0_*`, or GC 12 headers.
- Partial chunk boundaries: this research slice omits the beginning of `DB_DEBUG` and the end of `RMI_UTCL1_CNTL1`. Any merged per-file report should reconcile adjacent chunks before claiming full register coverage.
- Hardware side effects: fields such as flush, clear, force miss, throttle reset, disable clocks, disable caches, or clear error status can have immediate runtime effects. They should not be manipulated from generic debug code without the same sequencing used by the driver/firmware.
- Virtualization/SRIOV: some low-level GC registers may be PF-only or firmware-owned. VF code should avoid direct writes unless the existing access policy explicitly allows them.

## Test Signals

Useful validation signals for changes touching this header or consumers:

- Compile coverage: an AMDGPU build with GC 11.5.0 paths enabled catches renamed, missing, or malformed macros.
- Register helper smoke tests: any consumer using `REG_SET_FIELD`/`REG_GET_FIELD` should produce expected values for representative multi-bit fields such as `GB_ADDR_CONFIG__NUM_PKRS`, `CB_HW_MEM_ARBITER_RD__SCALE_WEIGHT`, `GCEA_SDP_ARB_FINAL__DRAM_BURST_LIMIT`, and `RMI_GENERAL_CNTL__VMID_BYPASS_ENABLE`.
- Boot/init logs on GC 11.5.0 hardware: look for GPUVM initialization success, no early GFXHUB protection faults, and no register access faults.
- Suspend/resume and GPU reset: DB/CB/GCEA/RMI state should be reinitialized cleanly after reset or resume.
- Graphics workload stability: render/depth compression, DCC, blend optimization, and backend mapping changes should be validated with basic rendering, Vulkan/GL CTS subsets, and stress workloads that exercise depth/stencil and color compression.
- Memory/error telemetry: RAS or debug paths should decode `GCEA_EDC_CNT*`, `GCEA_ERR_STATUS`, and `RMI_GENERAL_STATUS` consistently with hardware events; write-to-clear paths should clear only intended bits.
- Performance regressions: arbitration, burst, credit, and throttling fields can change latency or throughput. Compare memory-heavy graphics workloads before and after any consumer changes using these fields.
