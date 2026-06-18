# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002499`: lines 1-2488, `Docs/researches/chunks/subset-b-002499_research.md`
- `subset-b-002500`: lines 2489-4983, `Docs/researches/chunks/subset-b-002500_research.md`
- `subset-b-002501`: lines 4984-7461, `Docs/researches/chunks/subset-b-002501_research.md`
- `subset-b-002502`: lines 7462-9915, `Docs/researches/chunks/subset-b-002502_research.md`
- `subset-b-002503`: lines 9916-11685, `Docs/researches/chunks/subset-b-002503_research.md`

## Chunk Research

### subset-b-002499: lines 1-2488

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h lines 1-2488

## Purpose

This chunk is the opening slice of the generated AMD GC 11.0.0 register offset header. It contains preprocessor constants that map Graphics Core hardware register names to SOC15-style register offsets and base-index selectors. It has no executable C code; its public interface is a large set of `#define reg...` names consumed by AMDGPU, AMDKFD, display, SDMA, MES, IMU, and GFX code when issuing MMIO reads and writes.

The requested range covers the file license/header guard and 2,395 `#define reg...` lines. Those lines are mostly register-offset and matching `_BASE_IDX` definitions. The chunk begins at the start of the file with SDMA0 decoder metadata, covers the complete SDMA0 and SDMA1 queue/register blocks in this early part of the header, then covers several GC-wide blocks including GRBM, CP debug/status, PA, SQ, SH/SPI, texture, GDS, render backend/color/depth/cache, and the beginning of GCEA memory/client arbitration. The chunk ends inside `gc_gceadec` after `regGCEA_IO_WR_COMBINE_FLUSH`; later GC 11.0.0 offset definitions are outside this chunk.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU graphics hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, sysfs/debugfs entries, or direct register accesses in this range. The API is the generated macro naming contract:

- `reg<REGISTER>` expands to the register offset used by SOC15 register-access helpers.
- `reg<REGISTER>_BASE_IDX` selects the register aperture/base index. In this chunk most ordinary GC and SDMA queue registers use base index `0`, while SDMA hypervisor, performance-select, and performance-data windows use base index `1`.

Major address blocks in this chunk are:

- `gc_sdma0_sdma0dec`, base `0x4980`: SDMA0 core control/status and queue register window. It defines global SDMA control, timestamps, power, GB address config, ring-buffer pointer fetch, watchdog, quantum, status, EDC, atomics, UTCL1/XNACK/TLBI, tiling, interrupts, scratch RAM, queue reset, firmware status, and queues 0-7. Each queue has a repeated register pattern for ring-buffer control/base/read/write pointers, read-pointer writeback address, indirect-buffer control/base/size/offset, skip/context status, doorbell/log/offset, CSA address, scheduling, preempt, write-pointer polling address, AQL control, minor pointer update, RB preempt, and mid-command state.
- `gc_sdma0_sdma1dec`, base `0x6180`: the same SDMA decoder layout for SDMA1, with offsets shifted to the `0x0600`-based register range and queues 0-7 ending at `regSDMA1_QUEUE7_MIDCMD_CNTL`.
- `gc_sdma0_sdma0hypdec` and `gc_sdma0_sdma1hypdec`: SDMA microcode address/data, self-load, broadcast microcode access, and F32 control registers for both SDMA engines.
- `gc_sdma0_sdma0perfsdec`, `gc_sdma0_sdma1perfsdec`, `gc_sdma0_sdma0perfddec`, and `gc_sdma0_sdma1perfddec`: SDMA performance-counter configuration/select registers and low/high result windows.
- `gc_grbmdec`, base `0x8000`: graphics register bus manager controls, status per shader engine, soft reset, clock enable, read/write error, trap, scratch, fence-range, invalid-pipe, UTCL2 invalidation range, power, interrupt, and violation data registers.
- `gc_cpdec`, base `0x8200`: command processor debug and status registers for CPC/CPF/PFP/ME/MEC paths, busy/stalled/free-count reports, header dumps, instruction pointers, context/preemption status, ring read pointers, write-pointer polling, ROQ/STQ/MEQ thresholds and availability, indexed command debug access, and privilege-violation address reporting.
- `gc_padec`, base `0x8800`: primitive assembler/geometry front-end registers such as VGT FIFO depths, WD/IA UTCL1 state, shader-array/backend disable configuration, GE status/rate controls, pipe control, PA clip/setup status, and FIFO-depth controls.
- `gc_sqdec`, base `0x8c00`: shader queue, scalar/vector front-end, LDS, SQC, SQG, arbitration, performance snapshot, interrupt auto-mask/message controls, watchpoint address/control registers, and indirect SQ command/index/data access.
- `gc_shsdec`, base `0x9000`: shader/SPI-related debug, wavefront limit/lifetime status, static WGP masks, GDS credits, export/scoreboard buffer sizes, CSQ wave-active counters, trap-screen ranges for partitions P0/P1, and SPI configuration registers.
- `gc_tpdec`, base `0x9400`: texture/TA/TD status, DSM controls, scratch, and TA control/status registers.
- `gc_gdsdec`, base `0x9700`: global data share configuration, status, protection-fault, VM-protection-fault, EDC counters, and DSM controls.
- `gc_rbdec`, base `0x9800`: depth/color/render backend debug, stutter, credit, watermark, FIFO-depth, ring, exception, SRAM/interface clock gating, RB redundancy/backend-disable, GB address/backend map/GPU ID, CB hardware controls, DCC config, cache-evict points, and global chicken bits.
- `gc_gceadec`, base `0xa800`: the first GCEA DRAM and IO client-to-group, group-to-VC, lazy, CAM, page-burst, priority aging/queuing/fixed/urgency/quantum, and combine-flush offsets. The GCEA block continues after this chunk.

## Control Flow

This header has no runtime control flow. It participates in compile-time register selection:

1. GC 11 generation driver files include this offset header, usually with the matching `gc_11_0_0_sh_mask.h` and sometimes `gc_11_0_0_default.h`.
2. Driver code passes `reg...` constants to AMDGPU register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, or lower-level `RREG32`/`WREG32` paths after deriving an absolute offset.
3. The `_BASE_IDX` value tells SOC15 helper logic which register base aperture to use for the named register.
4. The hardware behavior is implemented by the consuming driver code and silicon. This generated file only supplies addresses.

The strongest local pattern is SDMA queue addressing. `amdgpu_amdkfd_gfx_v11.c` computes SDMA RLC register ranges from `regSDMA0_QUEUE0_RB_CNTL`, uses the distance from `regSDMA0_QUEUE1_RB_CNTL` to step between queue windows, and uses the distance between `regSDMA1_QUEUE0_RB_CNTL` and `regSDMA0_QUEUE0_RB_CNTL` to switch engines. `sdma_v6_0.c` similarly calls `sdma_v6_0_get_reg_offset()` with these generated offsets before programming or reading queue registers.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It names hardware-visible state:

- SDMA engine state: control, power, firmware/microcode access, global timestamps, status/error/EDC counters, UTCL1/XNACK/TLBI state, atomics, queue reset, scratch RAM, and per-queue RB/IB/doorbell/preemption/scheduling/AQL/mid-command state.
- SDMA performance state: selected events, counter configuration, result controls, and low/high counter readback registers.
- GRBM state: graphics front-end status, per-shader-engine status, soft-reset controls, clock enable state, traps, scratch registers, error/violation reports, power controls, and fence/invalid-pipe metadata.
- CP state: command processor debug/status, busy/stalled state, micro-engine instruction/header dumps, queue thresholds/availability, ring read pointers, preemption/context status, and privilege-violation reporting.
- Geometry/shader state: primitive assembler, work distributor, input assembler, geometry engine, shader queue, SQC/LDS/SQG, SPI wavefront lifetime/status, WGP masks, GDS credits, trap-screen ranges, and watchpoint registers.
- Texture/GDS/RB/GCEA state: texture pipe status, global data share protection/EDC, depth/color backend debug/configuration/cache state, GB address/backend mapping, and DRAM/IO arbitration and priority policy registers.

Persistence and side effects are entirely hardware-defined. Some registers are configuration that retain values until driver reprogramming, power gating, suspend/resume, GPU reset, or ASIC reset. Other registers are status, counters, request/ack, write-one-to-clear, indexed windows, scratch, or self-clearing controls. This offset header does not encode access permissions, reset values, bitfields, volatility, or sequencing rules.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's GC 11.0.0 register database and companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h` supplies bit shifts and masks for many of the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h` supplies reset/default values for many of the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c` includes this header and uses later and adjacent GC offsets for GFX bring-up, CP control, pipe reset, clock gating, and idle/status management. This chunk's GRBM, CP, SQ, PA, SPI, GDS, RB, and GCEA names are part of that register namespace even when individual uses are spread across the full file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c` includes this header and uses the SDMA queue offsets in this chunk for queue enable/disable, ring buffer programming, polling, and reset paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c` consume the SDMA queue layout for KFD queue management and MQD/RLC register programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c` uses GC 11 register naming while preparing compute queue descriptors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`, `imu_v11_0.c`, `gfxhub_v3_0.c`, `soc21.c`, `amdgpu_display.c`, and `display/amdgpu_dm/amdgpu_dm_plane.c` include this header as part of the SOC21/GC 11 register namespace.

The SDMA register offsets in this chunk are also structurally compared with later GC-generation headers such as `gc_11_0_3_offset.h`, `gc_11_5_0_offset.h`, `gc_12_0_0_offset.h`, and `gc_12_1_0_offset.h`. Consumers commonly assume repeated queue spacing and engine spacing are correct for the selected ASIC generation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset or base index compiles cleanly and can redirect an MMIO access to the wrong register.
- The file is generated. Manual edits risk divergence from the authoritative hardware register database, companion shift/mask/default headers, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. This chunk starts at the real file beginning, but it ends in the middle of `gc_gceadec`; final per-file research should merge later chunks before making whole-file claims.
- SDMA queue layout is repetition-sensitive. KFD and SDMA code compute queue and engine offsets from the generated constants. A single bad queue stride, SDMA0/SDMA1 delta, or `_BASE_IDX` can break queue setup, doorbells, write-pointer polling, preemption, AQL mode, queue reset, or mid-command restore.
- SDMA registers include live pointer, doorbell, interrupt, scratch, and status windows. Misaddressed writes can corrupt active DMA rings, hang queues, lose interrupts, or wedge GPU reset/recovery paths.
- Microcode and broadcast SDMA registers use base index `1`. Treating them like ordinary SDMA queue registers would access a different aperture and may fail firmware loading or diagnostics.
- Performance counter select/result registers are split into configuration and data windows. Wrong offsets can yield misleading profiling data or interfere with active counters.
- GRBM soft reset, clock, and status offsets are central to GPU reset/idle paths. Mistakes can cause waits that never complete, incomplete resets, or accidental reset of the wrong graphics sub-block.
- CP debug/status and ring-read-pointer registers are used while diagnosing or controlling command submission. Bad offsets can hide queue hangs, report false busy/idle state, or corrupt indexed debug access through `CP_CMD_INDEX`/`CP_CMD_DATA`.
- SQ/SPI watchpoint, trap-screen, and wavefront lifetime registers are debugger- and fault-path sensitive. Offset drift may only appear under GPU debugging, trap, preemption, or shader fault workloads.
- RB/CB/DB and GCEA registers affect memory/backend behavior and arbitration. Bad programming may show up as rendering corruption, DCC/cache issues, poor QoS, or workload-specific memory stalls rather than an obvious compile-time failure.
- Several registers are status, error, counter, indexed data, or clear/control windows. The offset header does not identify read-only/write-only/write-one-to-clear semantics, so consumers must rely on the matching shift/mask docs and hardware programming guides.

## Test Signals

Useful validation combines generated-header consistency checks with runtime GPU coverage:

- Build AMDGPU with GC 11 support enabled. Missing or renamed macros should surface in `gfx_v11_0.c`, `sdma_v6_0.c`, `amdgpu_amdkfd_gfx_v11.c`, KFD MQD/queue-manager code, MES, IMU, gfxhub, SOC21, and display include users.
- Mechanically compare this range against AMD's GC 11.0.0 register database and verify each `reg...` offset has the intended `_BASE_IDX` companion.
- Cross-check this offset header against `gc_11_0_0_sh_mask.h` and `gc_11_0_0_default.h` so shift/mask/default definitions reference valid registers and no generated name drift exists.
- Run repetition checks across SDMA0 and SDMA1 queues 0-7. Expected signals are consistent per-queue stride, consistent queue member ordering, and the intended SDMA1 offset delta from SDMA0.
- Exercise SDMA rings and KFD SDMA queues: queue create/destroy, DMA copy/fill, doorbell submission, write-pointer polling, interrupt delivery, queue reset, preemption, AQL mode, suspend/resume, and GPU reset recovery.
- Exercise SDMA performance counters and confirm selected events produce sane low/high counter values without corrupting queue operation.
- Run graphics command submission and reset/idle tests that cover GRBM status, soft reset, CP busy/stalled status, CP ring pointers, and pipe cleanup/reset paths.
- Run compute and graphics workloads with preemption, wavefront faults/traps, shader watchpoints where supported, and KFD queue scheduling to cover SQ/SPI/CP debug-sensitive registers.
- Use register dumps on GC 11.0.0 hardware to confirm key offsets land in the expected block ranges: SDMA0 `0x0000`-based queue window, SDMA1 `0x0600`-based queue window, GRBM around `0x0da0`, CP around `0x0e20`/`0x0f3c`, SQ around `0x10a0`, SPI around `0x11b8`, RB/CB around `0x13ac`/`0x1422`, and GCEA around `0x17a0`.
- Run display or rendering stress that exercises RB/CB/DB and GCEA arbitration indirectly, watching for corruption, hangs, timeout recovery, and performance/QoS regressions.

## Cross-Chunk Notes

This chunk starts at the actual file beginning and includes the license, include guard, and first register blocks. It fully covers the early SDMA0/SDMA1 decoder, SDMA hypervisor, and SDMA performance windows, and it covers complete GRBM, CP debug/status, PA, SQ, SH/SPI, TP, GDS, and RB block slices present before line 2488. It stops inside `gc_gceadec` after `regGCEA_IO_WR_COMBINE_FLUSH`; the next chunk should continue the remaining GCEA and later GC 11.0.0 offset blocks. The final per-file research document should reconcile this chunk with later chunks before summarizing all GC 11.0.0 register coverage.

### subset-b-002500: lines 2489-4983

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h lines 2489-4983

## Scope

This chunk is a generated AMDGPU GC 11.0.0 register-offset header segment. It contains C preprocessor constants only: each hardware register is exposed as `reg<NAME>` with a word offset, and each has a matching `reg<NAME>_BASE_IDX` that selects the SOC15 instance/base index. The matching bitfield definitions live in `gc_11_0_0_sh_mask.h`, and default values live in the GC default header.

The range starts in the tail of a GCEA arbitration block, then covers complete address blocks for GC VM/MMU programming, shader program resource registers, command processor queue and HQD registers, TCP watchpoints, GDS resource partitioning, and the beginning of GUS I/O arbitration. The chunk ends at `regGUS_IO_WR_PRI_QUANT_PRI4`; later GUS DRAM/SDP registers continue in the next chunk.

## Purpose

The purpose of this header slice is to give the GC 11 AMDGPU/KFD driver code stable symbolic offsets for low-level MMIO and command-processor programming. Driver paths use these macros with `SOC15_REG_OFFSET(GC, inst, reg...)`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32`, `WREG32_RLC`, IMU golden-register table macros, and KFD/MES queue-loading code. Because most call sites concatenate register names with the SOC15 helper layer, the macro names are a source-level hardware contract: a typo, offset drift, or wrong base index can compile cleanly in table-driven code but target the wrong register.

Important consumers in this tree include:

- `amdkfd/kfd_mqd_manager_v11.c`, which initializes GC 11 compute MQDs and fills fields that are later written to the CP/HQD register window.
- `amdgpu/amdgpu_amdkfd_gfx_v11.c`, which programs per-VM shader memory registers, loads/dumps/destroys HQDs, polls HQD state, executes wave-control commands, and configures TCP address watchpoints.
- `amdgpu/mes_v11_0.c`, which uses the same CP/HQD offsets when programming MES/KIQ queues and queue reset paths.
- `amdgpu/imu_v11_0_3.c`, whose IMU RLC RAM golden tables reference several GCVM and GUS registers from this chunk.

## Address Blocks and Register Families

The opening lines are the tail of a `GCEA` I/O priority/arbitration block. They define I/O read/write combine flush, group burst, age/queue/fixed/urgency/quantum priority, and SDP credit/reserve registers. The later `gc_gceadec2` and `gc_gceadec3` blocks add GCEA miscellaneous, latency sampling, MAM, EDC, DSM, XBR, probe, error status, RRET memory reserve, and SDP enable controls.

`gc_spipdec2` contributes early SPI controls, specifically `regSPI_PQEV_CTRL` and `regSPI_EXP_THROTTLE_CTRL`. These are small but high-impact shader-pipe knobs for queue/event and export throttling behavior.

`gc_rmi_rmidec` covers render/memory interface status and arbitration registers. It includes general control/status, subblock status, XBAR configuration and arbitration, UTC/UTCL1 controls, TCIW formatter controls, scoreboards, clock control, RB/GLX CID mapping, spare registers, and `regCC_RMI_REDUNDANCY`. These offsets are diagnostic and bring-up oriented, but bad values can also affect debug dumps or workaround tables.

`gc_pmmdec` and `gc_utcl1dec` are compact blocks for PIO/PMM control and UTCL1 status. They expose `GCR_PIO_*`, `PMM_*`, and `UTCL1_*` registers used around lower-level memory-interface diagnostics.

`gc_gcvmsharedpfdec`, `gc_gcvml2pfdec`, `gc_gcvmsharedvcdec`, `gc_gcvml2vcdec`, the performance-counter L2 blocks, `gc_gcvmsharedhvdec`, and `gc_gcvml2pspdec` form the largest VM/MMU portion of this chunk. They define offsets for:

- framebuffer, DRAM, system aperture, AGP, dummy page, APT, retry, and L1 TLB controls under `GCMC_VM_*`;
- GCVM L2 control, protection fault status/cntl, invalidate request/ack/status, context TLB control, walker/error/status, and credit controls;
- per-context `GCVM_CONTEXT0..15_*` page table base/end, protection fault default address, and per-PF/VF PTE cache fragment sizing;
- hypervisor/VF framebuffer size offsets and PSP-facing translation/fault registers;
- GCVM/GCMC/GCUTCL2 performance counter select/result registers.

This VM/MMU family is tied to GPU address translation, VMID context setup, protection fault reporting, cache invalidation, and SR-IOV/PF/VF partitioning. It is also referenced by IMU golden settings for GCVM L2 controls and protection-fault controls.

`gc_shdec` maps shader-program and shader-memory state. It includes `SPI_SHADER_PGM_RSRC4_*`, `SPI_SHADER_PGM_LO/HI_*`, `SPI_SHADER_USER_DATA_*` for PS/GS/VS/HS/LS/ES/CS, per-stage `SPI_SHADER_USER_ACCUM_*`, `COMPUTE_USER_DATA_0..15`, dispatch initiator and dimensional registers, compute program/resource registers, thread/wave/dispatch controls, `SH_MEM_BASES`, `SH_MEM_CONFIG`, and static thread-management masks for SE0..SE7. KFD writes `regSH_MEM_CONFIG` and `regSH_MEM_BASES` per VMID in `program_sh_mem_settings_v11()`, while MQD initialization persists many compute/static-thread values in memory for later HQD loading.

`gc_cppdec`, `gc_spipdec`, and `gc_cpphqddec` cover the command processor and shader-pipe queue interface. They include CU mask programming, CP GFX status/control, MEC/ME/PFP/CPF/CPG/CPC debug and interrupt registers, PQ/RB base/read/write pointer registers, DMA registers, queue reset and scheduler controls, interrupt status/ack registers, and the dense HQD/MQD register window from `regCP_MQD_BASE_ADDR` through `regCP_HQD_DEQUEUE_STATUS`. `amdgpu_amdkfd_gfx_v11.c` writes the HQD window sequentially from `regCP_MQD_BASE_ADDR` through `regCP_HQD_PQ_WPTR_HI`, dumps the same span for diagnostics, programs doorbell and write-pointer poll registers, and waits for `regCP_HQD_ACTIVE` to clear during queue destroy. MES uses the same offsets when adding/removing queues and resetting compute queues with `regCP_HQD_DEQUEUE_REQUEST` and `regSPI_COMPUTE_QUEUE_RESET`.

`gc_tcpdec` defines TCP address-watch registers for four watch slots: high/low address and control per slot. `amdgpu_amdkfd_gfx_v11.c` depends on the stride `regTCP_WATCH1_ADDR_H - regTCP_WATCH0_ADDR_H` and writes `regTCP_WATCH0_ADDR_H/L + watch_id * stride`, so register ordering and spacing are part of the debug-watchpoint ABI.

`gc_gdspdec` maps GDS/GWS/OA partitioning and context-switch state. It includes per-VMID GDS base/size registers for VMID0..15, per-VMID GWS and OA controls, GWS/OA reset masks, compute maximum wave ID, context-switch status and counters for CS/PS/GS/GFX paths, and `regGDS_MEMORY_CLEAN`. These offsets support shared-data-store resource assignment, cleanup, and debug/telemetry. MES exposes a `PROGRAM_GDS` scheduler opcode, so this register family is part of the queue scheduler/resource-management surface even where the exact writes are firmware-mediated.

`gc_gusdec` begins the GUS I/O arbitration block. This chunk covers read/write combine flush, age rate/coefficient, queueing, fixed priority, urgency coefficient/mode, and priority quantum registers for I/O clients. Later GUS DRAM and SDP controls continue outside this range.

## Important APIs, Types, and Functions

This header defines no functions, structs, enums, or runtime storage. Its API is the generated macro naming scheme:

- `reg<REGISTER>` is a 32-bit register word offset within the GC IP block/address block.
- `reg<REGISTER>_BASE_IDX` selects the SOC15 base index, usually `0` for normal GC aperture addressing and `1` for blocks in the alternate base aperture such as RMI/GUS.
- Address-block comments document the generated hardware grouping and base address, for example `gc_gcvml2vcdec` at `0xa3a0` and `gc_cpphqddec` at `0xc800`.

The key external helpers are `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `WREG32_RLC`, `REG_SET_FIELD`, and `REG_GET_FIELD`. The offset macros here pair with masks from `gc_11_0_0_sh_mask.h`; for example KFD programs `CP_HQD_PQ_DOORBELL_CONTROL` fields using mask macros and writes the result to the offset macro `regCP_HQD_PQ_DOORBELL_CONTROL`.

## Control Flow

There is no executable control flow in this header. Runtime control flow appears at integration points that consume the constants:

- KFD MQD creation initializes an in-memory `struct v11_compute_mqd`, including CP/HQD queue control, persistent state, doorbell, EOP, VMID, CU mask, and CWSR fields.
- KFD queue load selects a MEC/pipe/queue with SRBM, then writes the contiguous HQD register span beginning at `regCP_MQD_BASE_ADDR`; it then enables doorbell logic, programs write-pointer polling, starts the EOP fetcher, and sets `regCP_HQD_ACTIVE`.
- KFD queue dump and destroy read the same HQD offsets and poll `regCP_HQD_ACTIVE` after writing `regCP_HQD_DEQUEUE_REQUEST`.
- KFD debug paths program `regSH_MEM_CONFIG`, `regSH_MEM_BASES`, `regSQ_CMD`, and TCP watchpoint offsets; the TCP watch code assumes watch registers are laid out with a fixed stride.
- MES queue management and reset paths program the same CP/HQD and SPI compute reset offsets, while IMU golden-register setup applies table entries to GCVM and GUS registers during initialization.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware registers they describe are volatile GPU state, but several categories have longer-lived effects:

- GCVM/GCMC context and aperture registers define GPU virtual-memory translation behavior. Values may be reinitialized during GPU bring-up, reset recovery, suspend/resume, SR-IOV transitions, or VMID context changes.
- CP/HQD/MQD registers mirror queue state. KFD stores the desired state in MQD memory, writes it into HQD hardware registers when loading a queue, dumps it for diagnostics, and may checkpoint/restore MQDs around queue preemption or process checkpoint/restore.
- Shader memory and compute program/user-data registers are per-VMID or per-queue execution state. Incorrect offsets can persist as wrong address apertures, bad dispatch resources, or broken CWSR/debug state until the queue or VMID is rebuilt.
- GDS/GWS/OA base/size and reset registers represent shared resource allocation and cleanup state across compute queues/VMIDs.
- Fault/status/counter registers such as GCVM protection faults, GDS context-switch counters, RMI status, and GCEA/GUS arbitration counters are diagnostic latches or counters that remain meaningful until cleared, reset, or overwritten.

## Dependencies and Integration Points

This chunk depends on the broader generated AMD register ecosystem: matching `gc_11_0_0_sh_mask.h` field definitions, `gc_11_0_0_default.h` defaults, SOC15/IP discovery data, and the GC 11 firmware/firmware-mediated paths used by MES and IMU.

Important integration points include:

- KFD queue management through `kfd_mqd_manager_v11.c` and `amdgpu_amdkfd_gfx_v11.c`.
- MES scheduling through `mes_v11_0.c` and GC 11 MES firmware packets.
- IMU/RLC golden initialization through `imu_v11_0_3.c`.
- GFXHUB VM setup through `adev->gfxhub.funcs->setup_vm_pt_regs()`, which works alongside the GCVM/GCMC offsets in this chunk.
- Debug and profiling surfaces: HQD dumps, TCP watchpoints, wave control through `SQ_CMD`, GCVM/GDS/RMI/GCEA/GUS status registers, and performance counters.
- SR-IOV and partitioning surfaces through per-PF/VF VM registers, hypervisor shared blocks, and PSP-facing GCVM translation/fault controls.

## Risks

The highest risk is silent hardware misprogramming. Offset constants are plain numbers; an incorrect value can still compile and can make a write hit a different register in the same address block. This is especially dangerous in sequential ranges such as the HQD window, where KFD assumes that memory fields map directly to adjacent hardware registers from `regCP_MQD_BASE_ADDR` to `regCP_HQD_PQ_WPTR_HI`.

High-risk families in this chunk are GCVM/GCMC translation and protection-fault registers, because they affect memory isolation, page-table interpretation, retry/fault behavior, and SR-IOV partitioning; CP/HQD/MQD queue registers, because bad offsets can hang compute queues, corrupt doorbell/write-pointer behavior, or break preemption; TCP watchpoint registers, because the debug path assumes a fixed watch-slot stride; shader memory and program-resource registers, because they affect per-VMID addressing and dispatch execution; and GDS/GWS/OA partition registers, because incorrect partitioning or reset writes can leak or corrupt shared compute resources.

The `*_BASE_IDX` values are also significant. Mixing base index `0` and `1` can address the wrong GC aperture even if the local offset is correct. Generated address-block comments and base addresses should therefore be kept aligned with SOC15 register definitions and any firmware table usage.

Because this file is generated, manual edits are risky. Regeneration from the authoritative AMD register database should preserve name spelling, ordering, offset values, and base-index values. Removing apparently unused registers can also break out-of-tree diagnostics, firmware table generation, or future ASIC workarounds.

## Test Signals

Compile-time signals include successful AMDGPU/KFD builds anywhere these macros are used by `SOC15_REG_OFFSET`, `WREG32_SOC15`, `RREG32_SOC15`, IMU golden-register table entries, and KFD/MES queue setup. Renamed or deleted macros tend to fail quickly; wrong numeric values require runtime validation.

Runtime validation should focus on GC 11 hardware or emulation. Strong signals are successful GPU probe, IMU/RLC initialization, VM setup, suspend/resume and GPU reset recovery, MES startup, KFD process creation, AQL/PM4 compute queue creation, queue preemption/destroy, and stable queue dumps with sane HQD register values.

Memory-management signals include correct page-table base programming, no unexpected GCVM protection faults under VM stress, correct behavior under retry/fault tests, and no SR-IOV PF/VF aperture regressions. Compute/debug signals include working KFD CWSR, wave control, TCP address watchpoints, trap/debug handling, GDS resource assignment, and no hangs during GDS cleanup or queue reset. Golden-register signals include no regressions in IMU/RLC table application for GCVM and GUS registers referenced in this chunk.

### subset-b-002501: lines 4984-7461

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h lines 4984-7461

## Scope

This chunk covers lines 4984 through 7461 of AMD's generated GC 11.0.0 register-offset header. It is a declarative C preprocessor map: each hardware register gets a `reg...` offset macro and a matching `reg..._BASE_IDX` macro. The slice contains 1,203 register offset macros and 1,203 base-index macros.

The range starts inside the tail of `gc_gusdec`, then contains all of `gc_gfxdec0`, several PF/VF and PF-only GC control blocks, the GC CAC/EDC/power weighting block, SPI compute-unit reservation registers, the large `gc_gfxudec` user/config register block, and ends at the opening of `gc_cprs64dec`. There are no functions, structs, enums, branches, allocations, or direct MMIO operations in this header. Runtime behavior comes from AMDGPU code that includes this file and passes the generated symbols to SOC15 register access helpers.

## Purpose

`gc_11_0_0_offset.h` gives AMDGPU symbolic register offsets for the GC 11.0.0 graphics and compute IP. This chunk is centered on graphics context state, PF/VF-visible controls, PF-only power/debug controls, user/config-space surfaces, and the beginning of MES CP register offsets.

The macros let driver code use names such as `regDB_RENDER_CONTROL`, `regCP_MEC_CNTL`, `regDIDT_IND_INDEX`, `regGC_CAC_CTRL_1`, `regSPI_RESOURCE_RESERVE_CU_0`, `regGDS_RD_ADDR`, `regSPI_ATTRIBUTE_RING_SIZE`, and `regCP_MES_CNTL` instead of hard-coded offsets. The paired `BASE_IDX` values tell the SOC15 register infrastructure which base-address table entry to combine with the offset. In this chunk all visible `BASE_IDX` values are `1`, which distinguishes these blocks from earlier low-index SDMA/CP/GDS blocks that use base index `0`.

## Exported API Surface

The public surface is macro-only:

- `reg<REGISTER>`: generated register offset inside a GC 11.0.0 address block.
- `reg<REGISTER>_BASE_IDX`: generated SOC15 base-index selector for the same register.
- The surrounding header guard is `_gc_11_0_0_OFFSET_HEADER`, defined near the top of the full file outside this chunk.

Important address blocks in this slice are:

- `gc_gusdec` tail, base `0x33000`: GUS IO/DRAM priority quantum, combine/flush, SDP arbitration/credits/reserves, error/status, misc, and L1 channel/shader-array counters.
- `gc_gfxdec0`, base `0x28000`: DB, PA, VGT, CB, SX, GE, SPI, SQ, SQC, TA, GDS, and related graphics context offsets. This is the largest block in the chunk, with 519 register offset macros.
- `gc_pfvf_cpdec`, `gc_pfvf_grbmdec`, `gc_pfvf_padec`, and `gc_pfvf_sqdec`: registers intended to be visible in PF/VF flows, including CP engine control, GRBM addressing, PA scanner/binning/VRS/enhance controls, SQ runtime/debug state, shader trap base addresses, and shader memory configuration.
- `gc_pfonly_*` blocks: PF-only CP, HQD, DIDT, SPI, TCP, GDS, UTCL1, PMM/GCR, and CAC/EDC/power-management offsets.
- `gc_sedcdec`: SEDC GL1/GL2 override offset.
- `gc_pfonly_gccacdec`: GC and shader-engine CAC aggregation, EDC controls, throttle status, stall-pattern controls, indirect CAC access, and per-unit weight registers.
- `gc_pfonly2_spidec`: SPI per-CU resource reservation and enable masks for CU indices 0-15.
- `gc_gfxudec`, base `0x30000`: user/config-style graphics registers including scratch/user data, context controls, shader program resources, dispatch/draw controls, streamout counters, GDS direct/atomic access, occlusion counters, and SPI attribute-ring state.
- `gc_cprs64dec`, base `0x32000`: the start of MES CP register offsets, including `regCP_MES_PRGRM_CNTR_START`, `regCP_MES_INTR_ROUTINE_START`, `regCP_MES_MTVEC_LO/HI`, `regCP_MES_CNTL`, pipe priority registers, header dump, and interrupt-enable registers.

## Register Areas Covered

The `gc_gusdec` tail supplies arbitration and quality-of-service knobs for graphics memory or fabric traffic. The visible names cover IO read/write priority quantums, DRAM priority aging and urgency, SDP virtual-channel priority, tag/VCC/VCD reservation, SDP request control, error status, and L1 channel or shader-array command/data counters. Since the chunk begins mid-block, earlier GUS combine and priority controls are outside this item and must be merged from the preceding chunk.

`gc_gfxdec0` maps graphics pipeline context state. Its families include DB depth/stencil/render controls; PA scissor, viewport, primitive, binning, VRS, raster, and clip/setup state; VGT index, draw, geometry, primitive, instance, and streamout state; CB color target base, view, info, DCC, clear-word, attribute, and blend state; SX and shader export state; GE and WD controls; SPI shader/program interpolation and wave limits; SQ/SQC debug/cache surfaces; TA constant-buffer base registers; GDS direct and atomic access; streamout counters; occlusion counters; and the SPI attribute ring. This is the register-address layer used by command submission, context save/restore, debugging, and hang dumps; the actual bit fields live in the matching shift/mask header.

The PF/VF-visible blocks expose the subset of CP, GRBM, PA, and SQ controls that virtualization paths can legally address. `regCONFIG_RESERVED_REG0/1`, `regCP_MEC_CNTL`, and `regCP_ME_CNTL` are CP controls; `regGRBM_GFX_CNTL` selects graphics address routing; PA entries cover binner, VRS, trap-screen lock, interface FIFO, packer, and enhancement controls; SQ entries cover runtime/debug state plus shader TBA/TMA and shared memory base/config registers.

The PF-only blocks contain registers that should not be directly owned by virtual functions. They include CP debug/fetcher controls, HPD/ROQ status, DIDT EDC throttle/threshold/stall/status and indirect index/data, SPI trap/debug/arbiter/resource-limit controls, TCP invalidate/status/debug, GDS enhancement and OA clock-gating restore, UTCL1 invalidation and FIFO/GCRD controls, PMM/GCR command/status controls, and SEDC overrides.

`gc_pfonly_gccacdec` is power and activity accounting heavy. It maps GC-wide and per-shader-engine CAC aggregation windows, GFXCLK cycle counters, EDC stretch/unstretch counters, throttle control/status, PCC/PWRBRK/DIDT stall-pattern tables, hysteresis, indirect CAC access, and many per-client weight registers for CP, EA, UTCL2, GDS, GE, PMM, RLC, SQ, SP, LDS, SQC, CU, CB, DB, RMI, SX, UTCL1, GL1C, SPI, PC, PA, and SC. These offsets are sensitive because they feed power/thermal throttling and telemetry code.

`gc_pfonly2_spidec` contributes the per-CU SPI reservation surface: `regSPI_RESOURCE_RESERVE_CU_0` through `_15` and `regSPI_RESOURCE_RESERVE_EN_CU_0` through `_15`. These controls are likely consumed by firmware or privileged driver paths that reserve compute resources for queues, debug, or scheduling policy.

`gc_gfxudec` is a broad user/config block. It includes scratch registers; `CP_STRMOUT_CNTL`; context controls and anti-hang state; `COMPUTE_*` queue, dispatch, shader resource, trap, scratch, threadgroup, and user-data registers; `GE_*`, `VGT_*`, `PA_*`, `DB_*`, `CB_*`, `SPI_*`, `SQ_THREAD_TRACE_*`, `SQC_CACHES`, TA constant-buffer base, DB occlusion counters, GDS direct/atomic accessors, GDS streamout counters, and the attribute-ring registers. Many of these are programmed by graphics packets or queue setup and later sampled by driver diagnostics.

The `gc_cprs64dec` portion is only the first 14 offsets of the block. It introduces MES command processor state and aliases: `regCP_MES_INTR_ROUTINE_START` shares offset `0x2801` with `regCP_MES_MTVEC_LO`, and `regCP_MES_INTR_ROUTINE_START_HI` shares offset `0x2802` with `regCP_MES_MTVEC_HI`. This aliasing is intentional generated-header behavior but is a useful merge-time risk marker.

## Control Flow And State Behavior

There is no local control flow. The generated offsets become runtime behavior when included code calls SOC15 helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_FIELD15`, `REG_SET_FIELD`, or `REG_GET_FIELD`.

The state represented by this chunk is hardware MMIO state:

- Graphics context registers persist until context switch, clear-state load, queue command programming, reset, or power-gating domain loss.
- PF/VF-visible registers participate in virtualization-safe programming paths; PF-only registers require privileged ownership and should not be exposed to VF code without mediated access.
- DIDT, CAC, EDC, PCC, PWRBRK, and throttle registers hold power/thermal accounting, thresholds, status, and stall policy that can affect clocks, performance, and protection behavior.
- SPI CU reservation registers persist privileged scheduling/resource policy for compute units.
- `gc_gfxudec` compute, shader, scratch, GDS, streamout, occlusion, and trace registers reflect per-queue, per-context, or debug state programmed by command streams or kernel queue setup.
- MES CP state at the end of the chunk controls firmware command processor start vectors, interrupt vectors, priorities, and enables.

No software persistence is implemented here. These are compile-time constants. Actual persistence and reset behavior depend on ASIC reset domains, PF/VF ownership, firmware programming, command processor context save/restore, and driver write ordering.

## Dependencies And Integration Points

This file depends only on the C preprocessor syntactically, but it is part of a generated register-header set:

- `gc_11_0_0_offset.h` provides offsets and base indices.
- `gc_11_0_0_sh_mask.h` provides field shifts and masks for many of the same register names.
- `gc_11_0_0_default.h` provides full-register default values for many names in this chunk.

Direct include users in this tree include `amdgpu/gfx_v11_0.c`, `amdgpu/gfxhub_v3_0.c`, `amdgpu/mes_v11_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/sdma_v6_0.c`, `amdgpu/soc21.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdkfd/kfd_device_queue_manager_v11.c`, and `amdkfd/kfd_mqd_manager_v11.c`. `gfx_v11_0.c` includes this header and builds register dump lists with chunk symbols such as `regCP_MES_CNTL`, `regCP_HQD_*`, `regGDS_*`, `regSQC_CACHES`, and graphics status registers. It also programs HQD/MQD queue state using offsets from the same GC 11 namespace. `mes_v11_0.c` reads and writes `regCP_MES_CNTL` and programs HQD queue registers. `gfxhub_v3_0.c` pairs this offset header with the shift/mask and default headers to program GCVM/GCMC state from earlier file chunks.

`soc21.c` uses `SOC15_REG_OFFSET(GC, 0, regDIDT_IND_INDEX)` and `regDIDT_IND_DATA`, which are defined in the PF-only DIDT block in this slice, for indirect DIDT access. KFD v11 queue-management code includes this header for CP/HQD/SQ/GDS register names used in MQD load/unload and compute queue control.

The generated offsets are also tied to firmware-facing surfaces: `gfx_v11_0.c` declares GC 11 PFP/ME/MEC/RLC firmware blobs, while this chunk exposes MES and CP/HQD/MEC controls that must match firmware expectations for queue scheduling, preemption, and context management.

## Risks

- Generated-register drift is the main risk. If any offset or base index diverges from the ASIC register database, SOC15 reads and writes will hit the wrong MMIO address.
- The chunk starts and ends mid-block. Merge/reconciliation must combine neighboring chunks before making whole-block claims about `gc_gusdec` or `gc_cprs64dec`.
- All visible base-index macros are `1`; a mistaken `0`/`1` base-index change can be as damaging as a wrong offset because SOC15 address calculation changes the final MMIO target.
- PF/VF versus PF-only boundaries matter. Accidentally using `gc_pfonly_*` offsets in VF paths can cause access faults, no-ops, security issues, or inconsistent virtualized GPU state.
- Several registers are aliases or repeated families. The MES vector aliases at offsets `0x2801` and `0x2802`, repeated CB color target arrays, per-CU SPI reservation arrays, and per-client CAC weights all need generation consistency checks.
- Power and throttle registers in DIDT/CAC/EDC/PCC/PWRBRK blocks are high impact. Wrong programming can create performance cliffs, thermal throttling problems, hangs, or misleading telemetry.
- Graphics context offsets cover command-stream-programmed state. Wrong DB/PA/VGT/CB/SPI/SQ offsets can surface as rendering corruption, GPU hangs, failed context restore, bad shader dispatch, or unusable debug traces.
- Some names in `gc_gfxudec` are naturally packet-programmed user/config registers, while others are status or debug registers. The offset header does not encode access permissions, clear-on-read behavior, write-one-to-clear behavior, or firmware ownership.

## Test Signals

Good validation signals are mostly build-time, generated-header, and hardware-integration checks:

- Build AMDGPU with GC 11 support enabled so all include users of `gc_11_0_0_offset.h` compile, especially `gfx_v11_0.c`, `mes_v11_0.c`, `gfxhub_v3_0.c`, `soc21.c`, and KFD v11 queue-management files.
- Static generation checks should confirm that every `reg...` macro in this chunk has exactly one matching `reg..._BASE_IDX` macro and, where fields/defaults are expected, corresponding entries in `gc_11_0_0_sh_mask.h` and `gc_11_0_0_default.h`.
- Register-dump tests from `gfx_v11_0.c` should successfully read chunk-defined CP/MES/HQD, GDS, SQ/SQC, and status registers without invalid-address faults.
- Graphics workloads should cover clear-state/context programming, viewport/scissor, VRS/binning, primitive assembly, streamout, depth/stencil, render target color, occlusion queries, and shader trace/debug paths.
- Compute/KFD tests should cover MQD creation/load/unload, HQD programming, VMID/PASID queue ownership, AQL dispatch, trap TBA/TMA programming, scratch/user-data registers, preemption, and MES scheduling.
- Virtualization tests should verify that PF/VF-visible registers are usable from VF-mediated flows while PF-only blocks remain PF-controlled.
- Power-management tests should monitor DIDT/CAC/EDC/PCC/PWRBRK throttle status, power telemetry, stall counters, and suspend/resume behavior after touching GC 11 power and throttle code.
- Low-level register tests should verify `SOC15_REG_OFFSET(GC, 0, regDIDT_IND_INDEX)` and `regDIDT_IND_DATA` indirect access, plus `regCP_MES_CNTL` reads/writes in MES bring-up and halt/resume paths.

## Chunk Notes For Merge

This document is source-tree aligned and covers only `gc_11_0_0_offset.h` lines 4984-7461. It should be merged with adjacent chunk documents before producing the final per-file report. The preceding chunk is needed for the beginning of `gc_gusdec`; the following chunk is needed for the rest of `gc_cprs64dec` and later address blocks. The final report should treat this file as one generated GC 11.0.0 offset/base-index map paired with the matching default and shift/mask headers, with this chunk contributing the graphics-context, PF/VF, PF-only power/debug, user/config, and initial MES CP coverage.

### subset-b-002502: lines 7462-9915

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h lines 7462-9915

## Scope

This chunk is a generated AMDGPU GC 11.0.0 register-offset header segment. It contains C preprocessor constants only: each hardware register receives a `reg...` offset macro and an adjacent `reg..._BASE_IDX` macro. The range starts in the middle of the `gc_cprs64dec` command-processor RS64 address block at `regCP_MES_INTERRUPT`, continues through cache/interconnect and performance-monitor address blocks, covers RTAVFS register windows, contains the CP hypervisor/program-memory window, and ends in the first part of `gc_rlcdec` at `regRLC_AUTO_PG_CTRL`.

The segment defines 1,205 register-offset macros and 1,205 matching base-index macros. By address block, the non-`_BASE_IDX` register coverage is:

- `gc_cprs64dec` continued: 424 CP RS64/MES/GFX/MEC registers from `regCP_MES_INTERRUPT` through `regCP_GFX_RS64_INTERRUPT1`.
- `gc_gl1dec`, `gc_chdec`, `gc_gl2dec`, and `gc_gl1hdec`: 49 GL1/channel/GL2/GL1H cache and arbitration registers.
- `gc_perfddec`: 288 performance counter data/result registers.
- `gc_perfsdec`: 307 performance counter selector/control registers.
- `gc_grtavfs_grtavfs_dec`, `gc_grtavfs_se_grtavfs_dec`, and `gc_grtavfsdec`: 24 RTAVFS/global and shader-engine voltage/frequency-control window registers.
- `gc_cphypdec`: 55 CP hypervisor, CP microcode RAM, instruction-cache/data-cache base, and bound registers.
- `gc_rlcdec`: 58 RLC control, timer, doorbell, clock-count, clock-gating, and power-gating registers.

## Purpose

The purpose of this header slice is to give GC 11 AMDGPU code stable symbolic offsets for low-level graphics command processor, MES, cache fabric, performance-monitoring, RTAVFS, and RLC registers. Driver code combines these offsets with SOC15 register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and `REG_GET_FIELD`/`REG_SET_FIELD` definitions from the matching `gc_11_0_0_sh_mask.h`.

This is not policy code. It is generated hardware metadata used by policy code in `gfx_v11_0.c`, `mes_v11_0.c`, KFD GC 11 queue/MQD code, display code that needs GC register definitions, SDMA v6 support, and graphics hub initialization. The most active consumers for this chunk are MES and RLC paths: `mes_v11_0.c` programs `regCP_MES_*` instruction/data base and bound registers, scratch registers, program counters, and cache-operation controls; `gfx_v11_0.c` programs RLC control, clear-state, power-gating, clock-gating, firmware load, and status registers, and reads CP MES timer registers for clock-counter queries.

## Register Families Covered

The continued `gc_cprs64dec` portion covers MES and RS64 command-processor state. The MES group includes interrupt and scratch registers, instruction pointer, machine-mode status/cause/bad-address/IP registers, cycle/time/instret counters, ISA/vendor/architecture identifiers, timer compare registers, pipe quantum and priority controls, doorbell controls 1-6, debug interrupt pointers, GP0-GP9 scratch pairs, local data/instruction/scratch aperture registers, perfcount and pending interrupt state, interrupt data payload registers, debug and unknown interrupt status, queue current pointers, arbitration controls, busy status, command-engine switch controls, memory-mapped register access windows, and `CP_MES_MDBOUND`/`MIBOUND`-style memory range controls. The same address block then covers GFX RS64 and MEC RS64 program counter, status, interrupt, local aperture, event, debug, aperture base/mask/control, and machine-state registers. These definitions support firmware bring-up, MES scheduling, command submission, queue preemption, and post-hang debugging.

The GL1/CH/GL2/GL1H blocks provide cache and interconnect control/status offsets. They include GL1 DRAM burst masks and arbitration status, GL1C UTCL0 control/status/retry registers, CH arbitration and burst controls, channel-client credit/free-delay registers, CHC/CHCG control and status, GL2C miss-tag, ECC/XCC, invalidation, arbitration, and status registers, GL2A address-match and response-throttle registers, and GL1H arbitration controls. These are the low-level addresses for cache hierarchy tuning, invalidation status, retry/error diagnosis, and fabric arbitration.

The `gc_perfddec` and `gc_perfsdec` blocks are the largest middle section. The data block maps low/high result registers for performance counters across CP front-end subblocks (`CPG`, `CPC`, `CPF`), GRBM, graphics frontend and shader blocks (`PA`, `SPI`, `SQ`, `SQG`, `SX`), texture/cache blocks (`TA`, `TD`, `TCP`, `GL1A`, `GL1C`, `GL1H`, `GL2A`, `GL2C`, `UTCL1`), render and data-share blocks (`CB`, `DB`, `GDS`, `RMI`), and GUS/GCEA. The selector/control block maps the corresponding select, mode, counter-control, result-control, binning/sample-finish, latency-stat, and draw-window registers. Together these offsets are the address side of GPU performance monitoring: the field masks in the sibling sh-mask header define how to select events and modes, while these macros tell the driver where to read or program them.

The GRT/RTAVFS portions cover register-address, write-data, read-data, control/status, target frequency, target voltage, soft reset, PSM control, and clock-control windows for both global and shader-engine RTAVFS instances. The shorter `gc_grtavfsdec` block exposes the legacy/simple `regRTAVFS_RTAVFS_REG_ADDR` and `regRTAVFS_RTAVFS_WR_DATA` aliases. These are integration surfaces for adaptive voltage/frequency and clock-control firmware or PM paths, even though this header itself does not sequence voltage or frequency changes.

The `gc_cphypdec` block maps CP hypervisor and CP microcode RAM surfaces. It includes `regCP_HYP_PFP_UCODE_ADDR/DATA`, ME/MEC hypervisor microcode address/data aliases, PFP/ME/CPC/MES instruction-cache base/control/operation registers, MES instruction/data base and bound aliases (`MIBASE`, `MDBASE`, `MIBOUND`, `MDBOUND`), GFX RS64 data-cache and instruction-bound registers, and MEC data/instruction base/bound registers. Several macro names intentionally alias the same offset, such as `regCP_HYP_PFP_UCODE_ADDR` and `regCP_PFP_UCODE_ADDR`, or `regCP_MES_IC_BASE_LO` and `regCP_MES_MIBASE_LO`. These aliases let different driver subsystems use names matching their programming model while targeting the same register.

The `gc_rlcdec` block begins the RLC register map. This chunk includes RLC enable/status, F32 microcode version, reference/GPU/clock counters, GPM timer interrupt/control/status, interrupt status/clear registers, MGCG and CGCG/CGLS controls, jump-table restore, power-gating delays, ucode control, GPM thread reset/priority/enable/invalidate-cache controls, CP DMA completion status, RLCG doorbell control/status/range and four doorbell data pairs, GPU clock 32-bit selector/value, dynamic power-gating status/request, WGP status, always-on WGP mask, maximum power-gated WGP, and auto power-gating control. Later RLC registers are outside this chunk.

## Important APIs, Types, And Macros

This chunk declares no functions, structs, enums, or runtime storage. Its API is the generated macro naming convention:

- `reg<REGISTER>` gives the register offset used by SOC15 register accessors.
- `reg<REGISTER>_BASE_IDX` gives the register base-index selector. Every macro in this chunk uses base index `1`.
- Address-block comments, such as `// addressBlock: gc_perfsdec`, document the hardware decode block associated with the following offsets.
- Matching field macros live in `gc_11_0_0_sh_mask.h`; matching reset/default values live in `gc_11_0_0_default.h` where generated.

The driver-level API contract is compile-time name composition. A call such as `WREG32_SOC15(GC, 0, regRLC_CNTL, value)` depends on `regRLC_CNTL` from this file, while `REG_SET_FIELD(value, RLC_CNTL, RLC_ENABLE_F32, 1)` depends on the sibling sh-mask header. Golden register tables, debug register lists, register dump helpers, and KFD/MES setup code all rely on the spelling and numeric offsets staying in sync with the generated hardware database.

## Control Flow

There is no executable control flow in this header. The implied runtime flows are in consumers:

1. GC 11 initialization includes this header and selects registers through `reg...` symbols.
2. MES boot/setup code writes MES program-counter, instruction-cache, data-cache, scratch, bound, control, and cache-operation registers before starting MES firmware and later reads GP/status/time registers for scheduler state and diagnostics.
3. RLC initialization and power-management code writes clear-state buffer pointers, loads RLC/GPM/LX6/PACE/GPU IOV firmware through RLC ucode address/data registers, enables RLC F32, adjusts GPM thread enables, and toggles RLC power/clock-gating controls.
4. Performance monitoring code programs select/mode/control registers from `gc_perfsdec`, starts or gates counters, then reads result registers from `gc_perfddec`.
5. Debug, reset, and hang-dump paths read MES, GL/cache, RLC, and perf registers to report current hardware state.

The header is therefore upstream of many runtime branches, but the branch decisions and polling loops live in C source files such as `gfx_v11_0.c`, `mes_v11_0.c`, and KFD GC 11 queue management.

## State And Persistence

The macros themselves are immutable compile-time constants and hold no software state. The represented hardware state is volatile MMIO or indirect-register state owned by the GPU and firmware.

MES state persists while the MES firmware is running: scratch registers, instruction/data base and bounds, program counters, doorbell controls, pending interrupts, GP registers, queue pointers, and timer/cycle counters can be read back after setup or failure. Driver code also stores some values read from these registers into software structures, for example MES scheduler or KIQ version values read from `regCP_MES_GP3_LO` in later MES code paths.

RLC state controls persistent device behavior across the active GPU session. Enabling `RLC_CNTL`, setting power-gating controls, programming GPM thread enables, loading firmware through ucode address/data registers, and configuring clock-gating overrides remain active until changed, reset, or reinitialized after suspend/resume or GPU reset. Clock counters, interrupt latches, doorbell data, and perf counters are live diagnostic state and can change asynchronously.

Performance counter state is programmable and transient. Selector/control registers define what each counter observes; result registers accumulate until reset, stopped, or overwritten by hardware policy. RTAVFS registers represent hardware/firmware voltage-frequency control windows and should be treated as stateful control/status endpoints rather than ordinary scratch registers.

## Dependencies And Integration Points

This generated offset header depends on the surrounding GC 11 register-description set:

- `gc_11_0_0_sh_mask.h` supplies bit fields for the same register names.
- `gc_11_0_0_default.h` supplies default/reset values for generated registers where available.
- SOC15 register helpers convert `reg...` offsets plus block/instance/base-index data into MMIO addresses.
- `mes_v11_0.c` uses the MES and CP hypervisor aliases for firmware setup, scratch programming, instruction/data aperture setup, cache invalidation, and scheduler state reads.
- `gfx_v11_0.c` uses RLC offsets for firmware loading, clear-state buffer setup, RLC enable/disable, safe-mode/power-gating/clock-gating control, register access lists, and hang diagnostics.
- KFD GC 11 queue and MQD management includes this header with the sh-mask header for queue scheduling and compute integration.
- Performance-monitoring and profiling paths depend on the perf data/select offsets to match hardware event-selection field definitions.

The aliasing between `regCP_HYP_*`, `regCP_PFP_*`, `regCP_ME_*`, `regCP_MEC_*`, and `regCP_MES_*` names is an integration detail, not duplication to clean up casually. Different parts of the driver use the alias that matches the engine being programmed.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These offsets are numeric constants; an incorrect value or wrong base index can compile cleanly and make the driver read or write a different register. That can cause MES boot failure, incorrect queue scheduling, firmware load corruption, invalid cache apertures, broken performance counters, bad clock/power-gating behavior, or misleading hang dumps.

High-risk groups in this chunk include MES instruction/data base and bound registers (`regCP_MES_IC_BASE_*`, `regCP_MES_MIBASE_*`, `regCP_MES_DC_BASE_*`, `regCP_MES_MDBASE_*`, `regCP_MES_MIBOUND_*`, `regCP_MES_MDBOUND_*`), because MES firmware execution depends on those ranges; `regCP_MES_DOORBELL_CONTROL*` and queue pointer/status registers, because doorbell and scheduling mistakes can strand queues; CP hypervisor and microcode RAM aliases, because firmware upload paths write through them; RLC control, ucode, GPM thread, and power-gating registers, because they affect global graphics management; and perf select/result pairs, because a mismatched data/select pair produces plausible but wrong profiling data.

Generated alias pairs are an edge case for review. Multiple macro names can intentionally map to the same offset, for example instruction-cache names and machine-instruction-base aliases. Removing or renaming one alias can break consumers even if another numeric macro still exists. The chunk also starts mid-address-block, so analyses must include the preceding `gc_cprs64dec` context to avoid treating `regCP_MES_INTERRUPT` as the first register in the block.

Because this is generated source, manual edits should be avoided. If the hardware database is regenerated, offsets, base indices, sh-mask fields, and default values must be updated as a set.

## Test Signals

Useful compile-time signals are AMDGPU and AMDKFD builds that include `gc_11_0_0_offset.h`. Missing or renamed macros used by `gfx_v11_0.c`, `mes_v11_0.c`, KFD queue/MQD code, display code, SDMA v6, or gfxhub v3 fail at compile time.

Runtime validation needs GC 11 hardware or equivalent register emulation. Strong signals include successful GPU probe, MES firmware boot, KIQ/scheduler version reads, queue creation and submission through KFD and graphics paths, successful RLC firmware loading, clean suspend/resume and GPU reset recovery, and no hangs during RLC power-gating or clock-gating transitions.

Performance and diagnostic signals include sane perf-counter programming/readback across CP, GRBM, PA/SPI/SQ/SX, texture/cache, CB/DB/GDS/RMI, GL1/GL2, and UTCL1 blocks; stable MES timer reads from `regCP_MES_MTIME_*`; useful hang dumps for MES/RLC registers; correct RTAVFS control/status behavior under PM tests; and no unexpected cache retry, invalidation, ECC/XCC, doorbell, or RLC interrupt status changes after initialization.

### subset-b-002503: lines 9916-11685

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h lines 9916-11685

## Scope

This chunk is the final slice of the generated AMDGPU GC 11.0.0 register-offset header. It contains C preprocessor constants only. Each `reg*` symbol gives a SOC15 GC register offset and is usually followed by a matching `<name>_BASE_IDX` constant; each `ix*` symbol gives an indexed-register address used through an indirect register aperture rather than direct MMIO.

The range starts at `regRLC_SERDES_RD_INDEX` and runs through the closing include guard. It covers the latter part of the RLC direct register map, dedicated RLC sub-blocks, PF/VF RLC virtualization controls, power/hypervisor/PSP-facing GC blocks, the GFX IMU register map, and indexed CAC/RTAVFS/SQ wave debug spaces.

## Purpose

The purpose of this header slice is to publish ASIC-specific register addresses for GC 11.0.0-family AMD GPUs. Driver code includes this file instead of hard-coding numeric offsets when it initializes graphics firmware, uploads RLC and IMU microcode, reads shader wave state, configures low-level power/clock/debug features, and accesses indirect counter/control spaces.

This is source-level hardware interface data, not executable logic. The names are the API. Consumers such as `gfx_v11_0.c`, `imu_v11_0.c`, `mes_v11_0.c`, KFD v11 code, SDMA v6 code, display code, and SOC21 setup include `gc/gc_11_0_0_offset.h` and pass these macros to AMDGPU register helpers including `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, and `WREG32`.

## Register Families Covered

The first part continues the main RLC direct-register block. It includes `regRLC_SERDES_*` read/control/data/busy registers; `regRLC_GPM_GENERAL_0..16`; static power-gating and delay/status registers; GPM interrupt disable/force/stat registers; SRM control, command status, indexed address/data windows, and status registers; UTCL1 control/status/error registers for SPM/GPM threads; 3D clock-gating/ramp controls; RLC semaphores; PACE interrupt/timer controls; RLCV doorbell range/control/status and per-doorbell data registers; shader profiling controls/status; SMU message/argument/response registers; RLC GPM/CPM/IMU bootload registers; and `regRLC_GPM_UCODE_ADDR`/`regRLC_GPM_UCODE_DATA` for RLCG firmware upload.

The `gc_rlcsdec` block starts at line 10346 and exposes RLC secure/save-restore style controls. It includes RLCS decoder start/dump registers, exception registers, CGCG and deep-sleep controls, duplicated `regRLC_GPM_STAT`/`regRLC_RLCS_GPM_STAT` aliases at the same offset, IOV and VM busy status, GRBM soft reset, power-gating change status/readback, interrupt and semaphore surfaces, WGP status/readback, CP/SPM interrupt info, bootload status and ID status, power-brake controls, idle/busy status, general and auxiliary registers, SPM/SQTT mode, source-ID controls, GCR data/status, UTCL2 controls, secure-mode controls, FED status registers, and debug/value-stable status surfaces.

The `gc_pfvfdec_rlc` block provides PF/VF RLC virtualization doorbell and interrupt-window registers such as `regRLC_PF_VF_INT_STATUS`, `regRLC_VF_DOORBELL_START`, `regRLC_VF_DOORBELL_STATUS`, and related enable/status fields. These offsets are relevant to SR-IOV and virtual function command/doorbell routing.

The `gc_pwrdec`, `gc_hypdec`, and `gc_pspdec` blocks expose GC power control, hypervisor, and PSP-facing registers. They include power-brake controls and thermal-reset delay, CGTT controls/status/debug, hypervisor PM status and intruder/debug placeholders, PSP debug and mailbox registers for CPC/CPG/RLC, command-response/status data, secure-event queue ring base/size/read/write pointers, and PSP ring entry registers.

The `gc_gfx_imu_gfx_imudec` and `gc_gfx_imu_gfx_imu_pspdec` blocks map the GFX IMU. They include IMU version/status/scratch registers, core and reset controls, C2PMSG/P2CMSG message windows, access controls, RAM index/address/data windows, interrupt/status fields, DFT/BIST controls, GFX scheduler control, bootloader address/size registers, D/I RAM address/data apertures, and PSP-loaded RLC bootloader registers. `imu_v11_0.c` directly uses many of these offsets while loading IMU IRAM/DRAM and starting the IMU core.

The indexed `gccacind` block defines GC CAC indirect addresses. It starts with `ixGC_CAC_ID` and `ixGC_CAC_CNTL`, then lists accumulator indexes for CP, EA, UTCL2 router/VML/walker, GDS, GE, PMM, GL2C, PH, SDMA, CHC, GUS, and RLC, followed by release/stall/power-brake lookup tables, fixed-pattern performance counters, and `ixHW_LUT_UPDATE_STATUS`. These values are used through the GC CAC indirect index/data aperture rather than direct SOC15 register offsets.

The `secacind` block contains the SE CAC ID/control indexed registers. The `grtavfsind` block defines a linear indexed RTAVFS register bank, `ixRTAVFS_REG0` through `ixRTAVFS_REG194`. The `sqind` block defines SQ indirect wave/debug registers including local debug status/control, wave active/valid/mode/status/trap status, PC, GPR/LDS allocation, IB status/debug, scratch, HW IDs, scheduler mode, shader cycles, temporary registers `ixSQ_WAVE_TTMP0..15` with `TTMP2` absent in this slice, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_EXEC_LO/HI`.

## Important APIs, Types, and Macros

This file defines no C functions, structs, enums, or variables. Its important API surface is the macro convention:

- `regNAME` is a direct GC register offset consumed by SOC15 helpers.
- `regNAME_BASE_IDX` selects the register base index for SOC15 address calculation. In this chunk the main late-RLC, RLCS, PF/VF, power, hypervisor, PSP, and IMU direct registers use base index `1`.
- `ixNAME` is an indexed register number for an indirect aperture such as GC CAC, RTAVFS, or SQ wave debug.
- Address-block comments, for example `// addressBlock: gc_rlcsdec` and `// base address: 0x3b980`, preserve generated hardware grouping and help reviewers compare the output to AMD register databases.

The downstream helper contract is compile-time name stability. For example, `gfx_v11_0_load_rlcg_microcode()` writes `regRLC_GPM_UCODE_ADDR` and `regRLC_GPM_UCODE_DATA` through `WREG32_SOC15`; `imu_v11_0_load_microcode()` writes `regGFX_IMU_I_RAM_ADDR`, `regGFX_IMU_I_RAM_DATA`, `regGFX_IMU_D_RAM_ADDR`, and `regGFX_IMU_D_RAM_DATA`; and `gfx_v11_0_read_wave_data()` reads SQ wave state by passing `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_EXEC_LO`, and `ixSQ_WAVE_EXEC_HI` to an SQ indirect read helper.

## Control Flow

There is no control flow inside this header. It influences control flow at inclusion sites:

- During graphics initialization, `gfx_v11_0.c` enables and monitors RLC/RLCS state, uploads RLCG microcode through the GPM ucode address/data registers, configures SRM with `regRLC_SRM_CNTL`, and waits for RLCS bootload completion through `regRLC_RLCS_BOOTLOAD_STATUS` or ASIC-specific aliases.
- During IMU initialization, `imu_v11_0.c` requests IMU firmware, writes IMU IRAM and DRAM through the IMU address/data windows, sets debug and scratch controls, releases core reset, waits on `regGFX_IMU_GFX_RESET_CTRL`, and writes RLC RAM golden values through the IMU RLC RAM aperture.
- During shader debugging and GPU reset diagnostics, GFX code selects SQ indirect indexes and reads wave registers from the `sqind` space. The values collected from `ixSQ_WAVE_*` form the wave dump returned to higher-level debug paths.
- During indirect CAC access, generic AMDGPU helpers write an index register such as `mmGC_CAC_IND_INDEX` and read or write `mmGC_CAC_IND_DATA`; this chunk supplies the `ixGC_CAC_*` payload indexes for those transactions.
- During virtualization and PSP-mediated flows, PF/VF RLC and PSP mailbox/ring offsets provide the register endpoints for command status, doorbells, secure events, and firmware handoff.

## State and Persistence

The macros are compile-time constants and hold no state. The registers they name are volatile GPU hardware state. Many are reset by GPU reset, power transitions, or firmware ownership changes and then reprogrammed during probe, resume, or reset recovery.

Some register writes create persistent device state for the current hardware session. RLC and IMU firmware upload registers persist loaded microcode in hardware RAM or firmware-owned memory until reset or reload. IMU scratch, access-control, RAM-valid, and core-control registers affect whether the IMU can start and whether later power-management handoff works. RLC SRM, GPM, PACE, SMU, doorbell, and profiling controls can affect ongoing power, interrupt, save/restore, and debug behavior until overwritten.

Some registers are status or latch surfaces. RLCS exception, bootload, FED status, GCR, UTCL1/UTCL2 error, idle/busy, PF/VF interrupt status, PSP command/status, CAC accumulator, RTAVFS, and SQ wave registers expose transient hardware state. Reads can be used for diagnostics or polling, and some associated control/status bits may clear only through specific hardware-defined write sequences described outside this offset header.

## Dependencies and Integration Points

This chunk depends on the rest of the generated AMD ASIC register header set. The matching `gc_11_0_0_sh_mask.h` supplies bit masks and shifts for many of the same register names, while other offset/default headers cover neighboring blocks and reset defaults. The AMDGPU SOC15 register layer combines HWIP, instance, base index, and these offsets to form MMIO addresses.

Important integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`, which includes this header and uses RLC/RLCS, SQ indirect, and IMU bootloader offsets during graphics initialization, firmware upload, and wave dumps.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c` and `imu_v11_0_3.c`, which include this header and program IMU RAM, reset, scratch, C2PMSG, and RLC RAM windows.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reg_access.c`, `amdgpu.h`, and `amdgpu_cgs.c`, which provide generic indirect GC CAC read/write plumbing used by `ixGC_CAC_*` style indexes.
- KFD and MES v11 components, which include the same GC 11 header to program queueing, dispatch, and scheduling-facing registers elsewhere in the file.
- PSP and firmware-loading paths, where PSP mailbox/ring offsets and RLC/IMU bootloader offsets connect kernel-side firmware blobs to hardware-side command processors.

## Risks

The dominant risk is silent hardware misaddressing. These constants compile to integers, so an incorrect offset or base index can build cleanly while writes hit the wrong register or reads poll an unrelated status bit. For initialization paths this can surface as GPU probe failure, firmware load timeout, failed resume, reset loops, or hangs under graphics/compute load.

High-risk direct registers in this chunk include `regRLC_GPM_UCODE_ADDR`/`DATA`, RLC SRM controls, RLCS bootload/status/FED/error registers, PF/VF doorbell and interrupt registers, PSP mailbox/ring entries, and IMU RAM/control/reset registers. Misprogramming these can break firmware upload, interrupt routing, virtualization isolation, PSP handoff, or IMU-managed power states.

High-risk indexed registers include `ixSQ_WAVE_*`, because debug and reset diagnostics depend on exact SQ indirect addresses; `ixGC_CAC_*`, because indirect CAC access can affect accumulator/counter and power-control lookup state; and `ixRTAVFS_REG*`, because the names are generic numeric slots with little semantic redundancy, making off-by-one errors hard to detect by review.

Because this file is generated from hardware definitions, manual edits are risky. Any change should be checked against the matching generated sh-mask/default headers and the driver code that uses the affected macro names. Apparently unused definitions may still be consumed by out-of-tree diagnostics, firmware tables, register dump tooling, or later ASIC-specific workarounds.

## Test Signals

Compile-time signals include successful AMDGPU builds for GC 11 paths. Renamed or deleted macros used by `gfx_v11_0.c`, `imu_v11_0.c`, KFD v11, MES v11, display, or SDMA v6 code should fail at compile time. Numeric drift, however, usually requires hardware validation.

Runtime signals include successful probe of GC 11.0.0-family devices, successful RLC and IMU firmware loading, no `BOOTLOAD_COMPLETE` timeout while polling RLCS boot status, clean suspend/resume and GPU reset recovery, working GFXOFF/power-management transitions, and stable graphics/compute workloads after initialization.

Diagnostic signals include sane SQ wave dumps using `ixSQ_WAVE_*`, correct IMU firmware version reporting and reset completion, absence of unexpected RLCS FED or UTCL error status, correct PSP mailbox/ring command progress, and consistent CAC/RTAVFS indirect register reads where supported by hardware and firmware state. Virtualization-specific validation should include PF/VF interrupt and doorbell behavior when SR-IOV paths are enabled.
