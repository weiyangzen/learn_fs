# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002521`: lines 1-2485, `Docs/researches/chunks/subset-b-002521_research.md`
- `subset-b-002522`: lines 2486-5011, `Docs/researches/chunks/subset-b-002522_research.md`
- `subset-b-002523`: lines 5012-7489, `Docs/researches/chunks/subset-b-002523_research.md`
- `subset-b-002524`: lines 7490-9939, `Docs/researches/chunks/subset-b-002524_research.md`
- `subset-b-002525`: lines 9940-12094, `Docs/researches/chunks/subset-b-002525_research.md`

## Chunk Research

### subset-b-002521: lines 1-2485

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h lines 1-2485

## Purpose

This chunk is a generated AMD GC 11.0.3 register-offset header slice. It contains no executable driver logic; it publishes preprocessor constants that name Graphics Core MMIO register offsets and the SOC15 base-index selector used by AMDGPU register access helpers.

The requested range covers the file header guard and 1,198 register-offset macros, each paired with a `_BASE_IDX` macro for 2,396 `#define` lines total. It is dominated by the two SDMA decode windows for SDMA0 and SDMA1, then covers their hypervisor and performance-counter windows, and starts the main graphics-core decode space through the beginning of the DB/raster-backend block. The final line is `regDB_DEBUG7_BASE_IDX`; the DB block continues after this chunk.

Although the repository path is under a local `ceph-client` mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, runtime branches, allocation paths, locks, or includes beyond the header guard in this range. The public interface is the generated macro namespace:

- `reg<REGISTER>`: a register offset value consumed by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, `SOC15_REG_ENTRY`, and related AMDGPU helpers.
- `reg<REGISTER>_BASE_IDX`: the SOC15 base-address index for that register. In this chunk, normal SDMA and graphics-block registers use base index `0`, while SDMA hypervisor and performance-counter windows use base index `1`.

Major register families in this chunk:

- `gc_sdma0_sdma0dec` at source lines 28-884, base address `0x4980`: SDMA0 public decode registers. It starts with engine-level controls and status such as `DEC_START`, global timestamp, power/control/chicken bits, `GB_ADDR_CONFIG`, queue status, EDC counters, atomic controls, UTCL1/TLBI/page/XNACK registers, error/violation logs, scratch RAM, timestamps, queue reset, and CE/FED status. It then exposes eight repeated queue register groups, `QUEUE0` through `QUEUE7`.
- `gc_sdma0_sdma1dec` at lines 886-1742, base address `0x6180`: SDMA1 public decode registers with the same structure as SDMA0, offset upward by the SDMA1 register window. It has the same engine-level, UTCL1, error/status, queue reset, and eight queue groups.
- SDMA queue groups: for each queue, this chunk provides ring-buffer control/base/read-pointer/write-pointer registers, read-pointer writeback address registers, indirect-buffer controls and base/size/register pointer registers, skip/context/doorbell registers, doorbell log and offset, context-save-area addresses, schedule/preempt/dummy registers, write-pointer polling address registers, AQL and minor pointer update registers, RB preempt, and `MIDCMD_DATA0` through `MIDCMD_DATA10` plus `MIDCMD_CNTL`.
- `gc_sdma0_sdma0hypdec` and `gc_sdma0_sdma1hypdec` at lines 1744-1826: SDMA hypervisor/virtualization registers for microcode address/data/self-load, broadcast microcode writes, VM context low/high/control, active function ID, virtual reset request, context/public register type tables, VM control, and F32 control.
- `gc_sdma0_sdma0perfsdec`, `gc_sdma0_sdma1perfsdec`, `gc_sdma0_sdma0perfddec`, and `gc_sdma0_sdma1perfddec` at lines 1828-1898: SDMA performance-counter setup, select, result control, misc control, and low/high result registers for both SDMA engines.
- `gc_grbmdec` at lines 1900-1984: GRBM status, power, soft-reset, clock-enable, read/write error, trap, DSM bypass, chip revision, interrupt, RSMU, UTCL2 invalidation range, fence range, CP performance monitor selection, clock gating, memory power, and related graphics register bus manager controls.
- `gc_cpdec` at lines 1986-2106: command processor and graphics front-end offsets, including `CP_GFXU_DEC_START`, GE/GE2 status and control, IA status/control, VGT/WD status, CP performance counter selection and result, shader array/TCC disable and configuration registers, primitive config, and violation status registers.
- `gc_padec`, `gc_sqdec`, and `gc_shsdec` at lines 2108-2384: primitive assembler/culling/binning controls, SQ/SQC/SQG/LDS/SX state and debug controls, and a large SPI shader-input block covering debug/trap controls, wave lifetime controls/status, load-balancing counters, GDS/export/scoreboard sizing, compute wave active status/counts, and per-privilege trap-screen address/range registers.
- `gc_tpdec` and `gc_gdsdec` at lines 2386-2440: texture data/address block control/status/scratch registers and global data share configuration, protection fault, EDC, and DSM controls.
- `gc_rbdec` at lines 2442-2485: the beginning of DB/raster-backend offsets, including DB debug registers, stutter controls, credit/watermark/subtile/cacheline/FIFO/ring/memory-arbitration controls, exception control, and `DB_DEBUG7`.

## Control Flow

This header has no local control flow. It participates in runtime control flow only through macro expansion in AMDGPU and KFD code that chooses a register offset, combines it with a SOC15 base/index, and then performs MMIO reads or writes.

The clearest direct sequence tied to this chunk is SDMA queue programming:

1. SDMA/KFD code computes an SDMA queue register base from `regSDMA0_QUEUE0_RB_CNTL`, `regSDMA1_QUEUE0_RB_CNTL`, and the stride `regSDMA0_QUEUE1_RB_CNTL - regSDMA0_QUEUE0_RB_CNTL`.
2. Queue load paths write `QUEUE0_RB_CNTL` with `RB_ENABLE` cleared, poll `QUEUE0_CONTEXT_STATUS` for idle, program doorbell offset and doorbell enable, restore ring read/write pointers, program ring base and read-pointer writeback addresses, then re-enable the ring.
3. Dump paths walk contiguous ranges from `QUEUE0_RB_CNTL` through `QUEUE0_RB_WPTR_HI`, from `QUEUE0_RB_RPTR_ADDR_HI` through `QUEUE0_DOORBELL`, from `QUEUE0_DOORBELL_OFFSET` through `QUEUE0_RB_PREEMPT`, and from `QUEUE0_MIDCMD_DATA0` through `QUEUE0_MIDCMD_CNTL`.
4. SDMA engine setup uses `regSDMA0_WATCHDOG_CNTL`, `regSDMA0_UTCL1_CNTL`, `regSDMA0_UTCL1_PAGE`, and queue ring/IB registers to configure timeout, page policy, write-pointer polling, read-pointer writeback, doorbells, and ring/IB enablement.

The later GRBM, CP, PA, SQ, SPI, TP, GDS, and DB offsets are used similarly by GFX initialization, interrupt/error handling, reset, RAS, debug, trap, register dump, and performance-counter paths. Ordering rules live in those driver paths and hardware programming guides, not in this generated header.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. Its constants identify hardware-visible state:

- SDMA engine state: power/control bits, timestamps, queue status, watchdog settings, EDC counters, error logs, GPU IOV violation logs, UTCL1/TLBI/page/XNACK state, scratch RAM, queue reset request, FED status, and CE state.
- SDMA queue state: RB/IB base addresses, size, read/write pointers, read-pointer writeback address, doorbell enable/log/offset, AQL settings, schedule quantum, context status, context-save addresses, preemption, pointer-update control, and mid-command save data.
- SDMA virtualization state: microcode load windows, VM context bounds/control, active function, virtual reset request, and public/context register type controls.
- SDMA perf state: counter selection, configuration, low/high result registers, and result/misc controls.
- Graphics core state: GRBM status/errors/resets/traps, command processor/front-end status and counters, shader-array and TCC configuration/disable information, SQ/SQC/SQG/LDS/SX debug/performance state, SPI trap/debug/wave lifetime/load-balancing/counter state, texture block state, GDS protection/EDC/DSM state, and DB debug/stutter/FIFO/watermark/exception state.

Persistence and side effects are hardware-defined. Some registers are durable configuration until GPU reset, suspend/resume, power gating, mode changes, or driver reinitialization. Others are volatile status, latches, counters, self-clearing commands, request/ack handshakes, write-one-to-clear fields, or read-only state. The offset header does not encode those semantics; the companion `gc_11_0_3_sh_mask.h`, default headers, firmware, and driver code supply field definitions and access policy.

## Dependencies And Integration Points

This generated file must remain synchronized with AMD's GC 11.0.3 register database and companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h` supplies the field shifts and masks for these register names.
- Other GC 11.0.3 generated headers supply defaults, enums, and later offset ranges used with the same register namespace.
- SOC15 register helpers combine these offsets and `_BASE_IDX` values with block/instance selectors to produce physical MMIO addresses.

Observed direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`

Observed consumers of register families from this chunk include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`, which computes SDMA RLC queue offsets from `regSDMA0_QUEUE0_RB_CNTL`, `regSDMA1_QUEUE0_RB_CNTL`, and queue stride macros, then loads/dumps SDMA MQD state with the queue registers in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_0.c`, which uses SDMA queue, UTCL1, watchdog, doorbell, and status offsets for SDMA ring setup, register dump tables, write-pointer programming, and SR-IOV-sensitive queue control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`, which references `regSDMA0_QUEUE_RESET_REQ` for SDMA queue reset paths and `regSPI_COMPUTE_QUEUE_RESET` from the SPI area for compute queue reset.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c` and `gfx_v11_0_3.c`, which use GC offsets with shift/mask macros for GFX initialization, debug, trap, interrupt, and RAS paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`, which includes this header for GCVM/GFXHUB programming and identifies SDMA0/SDMA1 as GCVM clients.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`, which uses the same generated register namespace for IMU/RLC RAM golden programming outside this specific chunk.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset or base index can compile cleanly while directing an MMIO access to the wrong register or register aperture.
- The SDMA queue layout is assumed to be regular. Consumers derive queue stride from `regSDMA0_QUEUE1_RB_CNTL - regSDMA0_QUEUE0_RB_CNTL` and use queue0 register names as canonical offsets for all queues. A generator error in one queue block can affect only selected queue IDs and be hard to detect in light testing.
- SDMA0 and SDMA1 layout symmetry is important. KFD and SDMA code computes engine bases with both `regSDMA0_QUEUE0_RB_CNTL` and `regSDMA1_QUEUE0_RB_CNTL`; incorrect SDMA1 offsets could break only the second engine.
- `_BASE_IDX` values matter for SOC15 addressing. Hypervisor and perf windows in this chunk use base index `1`; treating them like normal base index `0` registers would access the wrong aperture.
- Queue pointer, doorbell, preempt, minor pointer update, and context status registers are sequencing-sensitive. Wrong offsets can cause queue load timeouts, stale read/write pointers, missed doorbells, corrupted MQD restoration, or hangs during preemption/reset.
- SDMA UTCL1/TLBI/XNACK/page and VM context registers interact with GPU memory translation and fault retry behavior. Incorrect offsets can produce VM faults, invalidation failures, or SR-IOV-specific regressions.
- Registers named `ERROR`, `VIOLATION`, `EDC`, `FED`, `TRAP`, `RESET`, or `INT` often have side effects or sticky status semantics in their field definitions. The offset header alone does not protect callers from read/modify/write mistakes.
- Performance-counter offsets are split into setup/select/result blocks. Mixing perfs and perfd windows or base indices can yield invalid profiling data without obvious functional failure.
- The graphics decode blocks after line 1900 are partial starts of larger namespaces. File-level research must merge later chunks before making complete claims about CP, PA, SQ, SH/SPI, TP, GDS, DB, or CC_RB register coverage.
- The chunk boundary stops inside `gc_rbdec`: `regDB_DEBUG5`, DB FGCG controls, more FIFO depth registers, and CC_RB redundancy begin immediately after this range.

## Test Signals

Useful validation is mostly build-time, mechanical, and hardware-runtime oriented:

- Build AMDGPU with GC 11.0.3, SDMA, GFXHUB, IMU, KFD, MES, and SR-IOV paths enabled. Missing or renamed macros should surface in `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, `imu_v11_0_3.c`, SDMA, MES, and KFD users.
- Mechanically compare this range against the authoritative GC 11.0.3 register database and ensure every `reg...` macro has exactly one matching `_BASE_IDX`.
- Cross-check this offset range with `gc_11_0_3_sh_mask.h` so heavily used registers such as `SDMA0_QUEUE0_RB_CNTL`, `SDMA0_QUEUE0_CONTEXT_STATUS`, `SDMA0_QUEUE0_DOORBELL`, `SDMA0_QUEUE0_DOORBELL_OFFSET`, `SDMA0_WATCHDOG_CNTL`, `SDMA0_UTCL1_CNTL`, and SPI/GRBM status registers have matching field definitions.
- Run repetition checks across `SDMA0_QUEUE0-7` and `SDMA1_QUEUE0-7`: RB/IB/doorbell/schedule/preempt/mid-command subranges should preserve the intended stride and ordering.
- Exercise SDMA ring bring-up, packet submission, fence completion, write-pointer polling, doorbell and non-doorbell modes, suspend/resume restore, and GPU reset recovery. Expected signals are clean fence completion, stable ring pointers, and no SDMA queue idle timeout.
- Exercise KFD SDMA queues across both SDMA engines and multiple queue IDs. This specifically validates the queue-stride and engine-base calculations that use this chunk.
- Exercise SR-IOV VF paths where available, because SDMA write-pointer polling, GPU IOV violation logs, VM context registers, and hypervisor decode registers are virtualization-sensitive.
- Capture SDMA register dumps before and after queue load/reset. Dump ranges should include sane contiguous values for queue RB/IB, doorbell, preempt, and mid-command registers.
- Run GFX initialization, RAS/FED interrupt handling, compute queue reset, shader trap/debug paths, and performance-counter collection on GC 11.0.3 hardware or emulation. Failures may appear as ring timeouts, invalid register reads, missed interrupts, bad perf data, or GPU reset.
- Validate that generated offset/base-index changes are not hand-edited. Any update should come from the register generator or be justified against silicon documentation.

## Cross-Chunk Notes

This is the first chunk of `gc_11_0_3_offset.h`, so it owns the license/header guard and the beginning of the GC 11.0.3 register namespace. It contains complete SDMA0/SDMA1 public queue decode blocks and SDMA hypervisor/perf windows, but only starts the later graphics decode blocks. The next chunk should continue inside `gc_rbdec` with `regDB_DEBUG5` and later DB/CC_RB register offsets. The final per-file research document should reconcile these artificial boundaries before describing whole-file CP, PA, SQ, SPI, TP, GDS, DB, or raster-backend coverage.

### subset-b-002522: lines 2486-5011

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h lines 2486-5011

## Purpose

This chunk is generated AMD GC 11.0.3 register-offset metadata. It contains no executable C code; it publishes `reg*` register address constants and matching `*_BASE_IDX` constants for AMDGPU, AMDKFD, MES, GFXHUB, IMU/RLC initialization, and low-level debug paths. Consumers pair these offsets with generated shift/mask headers and SOC15 register access helpers to program the graphics, compute, memory-translation, command-processor, and debug blocks for this ASIC generation.

The selected range starts at the tail of DB/CB/GB render-backend and color-buffer offsets, then covers GCEA arbitration, RMI/PMM/UTCL1, GCVM/GCVML2/ATCL2/TLB and their performance-counter windows, PSP-owned GCVM controls, shader and compute user/config state, CP ring and HQD state, SPI compute controls, TCP watchpoints, and the beginning of GDS VMID aperture registers. Although the repository path is under `ceph-client`, this file is AMD GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, memory allocations, or direct I/O operations in this range. The exposed interface is a generated preprocessor namespace:

- `reg<REGISTER>` gives the register's GC 11.0.3 offset value.
- `reg<REGISTER>_BASE_IDX` gives the base-index selector used by SOC15-style register helpers; every entry in this chunk uses base index `0`.
- Consumers typically use these constants through `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `RREG32`, `WREG32`, `WREG32_RLC`, `SOC15_REG_ENTRY_STR`, or XCC/instance variants.
- Bitfield interpretation is intentionally not in this file. It comes from the matching generated `gc_11_0_3_sh_mask.h` and related default headers.

Major register groups in this chunk:

- Tail render-backend/color-buffer registers: `regDB_DEBUG5`, `regDB_FGCG_*`, `regCC_RB_REDUNDANCY`, `regCC_RB_BACKEND_DISABLE`, `regGB_ADDR_CONFIG`, `regGB_BACKEND_MAP`, `regGB_GPU_ID`, `regCB_HW_CONTROL*`, `regCB_DCC_CONFIG*`, `regCB_HW_MEM_ARBITER_*`, `regCB_FGCG_SRAM_OVERRIDE`, and `regCB_CACHE_EVICT_POINTS`.
- `gc_gceadec`, `gc_gceadec2`, and `gc_gceadec3`: GCEA DRAM and IO client/group/VC maps, lazy/CAM/page-burst controls, read/write priority age/queuing/fixed/urgency/quantum controls, SDP arbitration, credits, tag/VCC/VCD reserves, request control, latency sampling, MAM/EDC/DSM controls, GL2C/XBR credits, probes, error status, backdoor credits, return-memory reserve, and SDP enable.
- `gc_rmi_rmidec`: RMI control/status, subblock status, crossbar configuration and arbiter controls, UTC/XNACK and UTCL1 controls, formatter state, scoreboard controls/status, clock control, RB-to-GLX client mapping, debug/spare registers, and RMI redundancy.
- `gc_pmmdec` and `gc_utcl1dec`: GCR PIO control/data, PMM control/status, and UTCL1 control/status registers.
- `gc_gcvmsharedpfdec`, `gc_gcvml2pfdec`, `gc_gcatcl2dec`, `gc_gcl2tlbpfdec`, `gc_gcvmsharedvcdec`, and `gc_gcvml2vcdec`: the main graphics VM register map. This includes NB/PCI aperture registers, FB/system/local aperture bounds, steering and reset requests, UTCL2 clock/busy/fault controls, VM L2 control/status/protection-fault/default-address registers, identity apertures and physical offsets, walker throttles, PTE cache dump, credit-safety controls, ATC L2 controls/cache-data/status, TLB status, GPUVA VMID translation-assist request/response registers, virtual-client FB/AGP/system aperture registers, 16 context controls, 18 invalidate engines with semaphore/request/ack/range registers, 16 context page-table base/start/end register pairs, and per-PF/VF PTE cache fragment-size registers.
- GCVM, ATC L2, and L2 TLB performance-counter windows: `regGCVML2_PERFCOUNTER2_*`, `regGCMC_VM_L2_PERFCOUNTER_*`, `regGCUTCL2_PERFCOUNTER_*`, `regGC_ATC_L2_PERFCOUNTER*`, `regGCL2TLB_PERFCOUNTER*`, select/mode registers, per-counter config registers, and result-control registers.
- `gc_rlcsdec`: RLC/RLCS FED status registers.
- `gc_gcvml2pspdec` and `gc_gcl2tlbpspdec`: PSP/security-facing GCVM controls, including translation bypass by VMID, IOMMU host translation enable/control/optimization/MMIO controls, 16 MARC base/relocation/length/mapping entries, translation fault controls, and GPUVA VMID translation-assist control.
- `gc_shdec`: shader-program and compute dispatch state. The shader side covers PS/GS/ES/HS/LS program low/high addresses, resource registers, checksums, user-data registers 0-31, user-data address pairs, request controls, user accumulators, and meshlet GS controls. The compute side covers dispatch dimensions/start/thread counts, pipeline/perfcount enables, program address/resource/VMID/limits, static thread management and destination masks, scratch/dispatch packet addresses, restart/relaunch/wave-restore registers, dispatch IDs, DDID, checksum, user data 0-15, tunnel/end markers, and reserved SH registers.
- `gc_cppdec`: CP/CPC/CPF/CPG command-processor state. It includes CU mask DMA registers, EOP wait and clock-gating sync controls, interrupt info/address/PASID/status/control, GFX errors, UTCL1 controls/errors/status, AQL status, legacy graphics ring base/control/read/write pointer and doorbell range registers, per-ME/pipe priority and VMID registers, fatal/ECC/debug/power registers, write-pointer polling controls, F32 interrupt registers, context and VMID reset/preempt controls, suspend/resume and DDID registers, HPD and MQD/HQD GFX queue state, CP DMA watchpoints, jump-table status, busy hysteresis, timestamp offsets, SDMA command-state handoff registers, and soft-reset/GFX controls.
- `gc_spipdec`: SPI arbitration/cycle controls, workload-control pipe percentage slots for graphics/HP3D/CS0-CS7, VMID accumulation/debug controls, compute queue reset, and compute wavefront context save.
- `gc_cpphqddec`: CP hardware queue descriptor registers for compute queues, including UTCL1 control/error, MQD base, active/VMID/persistent/priority/quantum state, packet queue base/read/write pointer/report/poll/doorbell/control registers, IB base/read/control, dequeue/offload/semaphore/message/atomic state, HQ scheduler/status/control aliases, EOP base/control/pointers/events, context-save and suspend offsets/sizes, GDS resource state, error/AQL/DDID/dequeue status.
- `gc_tcpdec`: four TCP watchpoint triples, each with high address, low address, and control registers.
- `gc_gdspdec`: initial GDS VMID base/size pairs for VMID0 through VMID5. The source chunk ends before the rest of the GDS VMID window, so the adjacent chunk is needed for the complete GDS register set.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by driver code:

1. ASIC-specific code includes `gc/gc_11_0_3_offset.h` with the matching generated bitfield and default headers.
2. The driver selects a register offset by subsystem, instance, VMID, context, queue, or counter index.
3. The driver composes or decodes the register value using companion shift/mask constants or hard-coded hardware values from tables.
4. SOC15, RLC-safe, XCC-aware, or direct MMIO helpers perform the actual access while the owning driver path handles ordering, locking, reset sequencing, firmware coordination, and power-state constraints.

Observed consumers in this tree include `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`, all of which include this exact offset header. Related GC 11 code uses many offsets from this chunk: GFXHUB programs `regGCVM_CONTEXT0_CNTL` and derives context spacing from `regGCVM_CONTEXT1_CNTL - regGCVM_CONTEXT0_CNTL`; GFX and KFD code program and inspect HQD packet-queue registers such as `regCP_HQD_PQ_BASE`; KFD uses `regTCP_WATCH0_ADDR_H` and `regTCP_WATCH1_ADDR_H - regTCP_WATCH0_ADDR_H` as the TCP watchpoint stride; GFX code clears or restores `regGDS_VMID0_BASE`/`SIZE` pairs with `WREG32_SOC15_OFFSET`.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state by naming offsets.

The represented state is extensive and mostly volatile:

- Render-backend, CB, GCEA, RMI, UTCL1, and PMM registers describe hardware configuration, arbitration, redundancy/harvest controls, queueing policy, fabric credits, XNACK/UTC behavior, and live error/status state.
- GCVM/GCVML2/ATCL2/TLB registers describe address translation configuration: apertures, context enablement, page-table bases and bounds, invalidate request/ack sequencing, protection fault capture, translation-assist request/response, MARC ranges, IOMMU controls, translation bypass, and per-PF/VF cache-fragment settings.
- Shader and compute registers describe live draw/dispatch state and command-stream-visible context: program addresses, resource registers, user SGPR data, accumulators, dispatch geometry, scratch and packet addresses, static thread masks, restart/relaunch state, and wave-restore addresses.
- CP and HQD registers describe command submission and queue state: ring bases and pointers, read-pointer writeback, doorbells, VMIDs, queue priority/quantum, MQD base, packet and indirect-buffer queues, EOP queues, context-save areas, suspend state, GDS resources, DDID state, HPD controls, interrupts, errors, timestamps, and debug/watchpoint state.
- TCP watchpoint and GDS VMID registers describe debug watch windows and per-VMID GDS allocation apertures.
- Performance-counter registers hold counter selection/configuration, mode, result-control, and low/high readback values.

Persistence depends on hardware access class and power state. Some registers are configuration that stays valid until GPU reset, suspend/resume, runtime power-gating, queue teardown, or explicit reprogramming. Others are live counters, sticky fault/status bits, firmware-owned state, write-one/self-clearing controls, indirect debug windows, or hardware-owned queue pointers. The macros do not encode read-only/write-only/reserved semantics, so consumers must rely on programming guides and companion masks/defaults.

## Dependencies And Integration Points

The direct dependency is the generated register family for GC 11.0.3:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h` for fields within these registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_default.h` or shared GC 11 defaults where reset/golden values are needed.
- SOC15 register-helper infrastructure and ASIC IP block tables that map these register offsets to MMIO addresses.

Important integration points include:

- IMU/RLC golden-value loading in `imu_v11_0_3.c`, including GCVM context defaults.
- GFXHUB v3.0.3 VM setup, aperture programming, L2/protection fault handling, page-table context programming, and TLB invalidation.
- GFX v11 ring, queue, context, compute-dispatch, GDS, CP, and reset paths that use these offsets either directly or through shared GC 11 helpers.
- AMDKFD queue management and debug support, including HQD/MQD save/restore, queue eviction/restore, AQL queue controls, TCP watchpoints, wavefront context-save, and trap/debug interactions.
- MES v11 queue management, which writes HQD packet-queue and context registers from MQD state.
- Doorbell/NBIO integration, because CP and HQD doorbell range/control registers must match allocated doorbell offsets and user queues.
- PSP/IOMMU/SR-IOV integration, especially for the PSP-facing GCVM MARC, translation bypass, per-PF/VF, and fault-control registers.
- Performance-monitoring and debugfs/trace tooling that select and read GCVM, ATC L2, and L2 TLB counters.

## Risks And Edge Cases

- Header/ASIC mismatch is the main structural risk. These are untyped numeric offsets; using GC 11.0.3 offsets with another GC generation can compile while targeting the wrong hardware register.
- The chunk contains many repeated indexed families. Off-by-one arithmetic around VM contexts, invalidate engines, shader user data, CP pipes, HQD queues, TCP watchpoints, or GDS VMIDs can program a valid but unintended register.
- Some registers alias intentionally, such as `regCOMPUTE_DESTINATION_EN_SE*` with `regCOMPUTE_STATIC_THREAD_MGMT_SE*`, `regCP_RB0_*` with `regCP_RB_*`, `regCP_HQD_DMA_OFFLOAD` with `regCP_HQD_OFFLOAD`, and HQ scheduler/status aliases. Consumers must know which semantic view applies to the access path.
- Register offsets alone do not define safe access ordering. Queue and ring registers require careful disable/program pointer/program base/enable sequencing, and GCVM invalidate registers require request/ack polling and correct address ranges.
- VM and IOMMU registers are high impact. Incorrect aperture, page-table base, context bounds, MARC, bypass, or translation-fault control values can cause GPU page faults, host-memory exposure, VMID isolation failures, or hangs.
- CP/HQD state is firmware- and scheduler-coordinated. Misprogramming MQD/HQD bases, doorbells, EOP queues, context-save addresses, or dequeue/offload/status registers can break command submission, preemption, or recovery.
- Shader and compute context registers are often command-stream programmed. Driver-side writes must be limited to well-defined init/debug/reset paths to avoid racing active workloads.
- Performance-counter windows may require select/config/result sequencing and may be shared with profiling tooling. Blind reads can produce inconsistent low/high values if latch semantics are ignored.
- PSP-facing GCVM controls may be security-sensitive and may not be safe for ordinary driver writes outside approved firmware handoff paths.
- TCP watchpoints and debug state can perturb running compute workloads if enabled at the wrong time or with the wrong address/control pairing.
- The chunk boundary is artificial. It starts after earlier DB/CB definitions and ends mid-GDS VMID range, so adjacent chunk research is needed for the complete file-level register-map narrative.

## Test Signals

Useful validation is mostly build, generated-header consistency, hardware smoke, reset, and profiling coverage:

- Build coverage for GC 11.0.3 paths that include this header, especially `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, `imu_v11_0_3.c`, shared `gfx_v11_0.c`, `amdgpu_amdkfd_gfx_v11.c`, and MES v11 code.
- Generated-header checks that every `reg*` in this range has a matching `*_BASE_IDX`, offsets match AMD source data for GC 11.0.3, intentional aliases are documented, and adjacent indexed families have the expected stride.
- GFXHUB VM tests that create GPU VM contexts, program page-table bases and bounds, issue invalidations through all used engines, verify ACK/status behavior, and exercise protection-fault reporting.
- Reset, suspend/resume, runtime power-gating, and GPU recovery tests while VM contexts, GDS allocations, graphics rings, compute queues, and KFD queues are active.
- GFX and compute ring tests that submit commands, validate CP/HQD pointers and fences, exercise doorbells and write-pointer polling, and confirm queue teardown/reload does not leave stale HQD or MQD state.
- KFD tests for AQL queues, queue eviction/restore, preemption, TCP watchpoints, wavefront context-save, and GDS VMID allocation.
- Shader/compute command-stream tests that verify PS/GS/HS/LS and compute program/resource/user-data registers are restored correctly across context switches and resets.
- Performance-counter tests for GCVM/GCVML2/ATCL2/L2TLB select/config/readback paths, including low/high counter consistency and result-control behavior.
- Negative signals include GPU page faults after VM setup, invalidate timeouts, stuck CP or HQD active bits, stalled fences, wrong doorbell routing, corrupted GDS partitioning, unexpected ECC/UTCL1/RMI/GCEA error status, invalid TCP watchpoint hits, nonsensical perf-counter values, or failures isolated to GC 11.0.3 ASICs.

### subset-b-002523: lines 5012-7489

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h lines 5012-7489

## Scope

This chunk is a generated AMD GC 11.0.3 register-offset header slice. It contains C preprocessor `#define` constants only: one register-offset macro and one `<REGISTER>_BASE_IDX` macro for each register. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or executable branches in this range.

The selected lines contain 2,406 `#define` statements: 1,203 register offset macros and 1,203 matching base-index macros. The chunk starts in the middle of the `gc_gdspdec` address block at `regGDS_VMID6_BASE`, then covers RAS signature registers, GUS fabric/register controls, a large graphics context-space block, SR-IOV PF/VF and PF-only privileged blocks, SPI per-CU resource reservation, and the beginning of the `gc_gfxudec` user/config-space command-processor block. It ends at `regVGT_NUM_INDICES`, so the surrounding VGT/GE user-config register group continues in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_11_0_3_offset.h` maps symbolic GC 11.0.3 register names to the numeric offsets used by AMDGPU MMIO and packet-building helpers. Driver code combines these offsets with register field definitions from `gc_11_0_3_sh_mask.h` and SOC15 addressing helpers to read, write, or decode graphics-core hardware state without embedding raw register numbers throughout the driver.

This chunk covers these register surfaces:

- GDS partitioning and reset state for VMID-owned global data share resources.
- RAS signature capture controls for graphics sub-block reliability diagnostics.
- GUS fabric, queue, credit, priority, combine-flush, and L1 shader-array traffic controls.
- Core graphics context registers for depth/stencil, scissor/rasterization, primitive assembly, shader/export setup, color buffer state, context rolls, coherency, and performance/event counters.
- PF/VF-visible and PF-only privileged control registers used by SR-IOV, command processor debug paths, DIDT/EDC/throttling, TCP/UTCL1/GCR/PMM, and current/activity counter logic.
- SPI resource reservation controls for per-CU availability and enable masks.
- User/config-space command processor registers for EOP fences, pipeline statistics, scratch registers, atomic pre-operation values, DMA, indirect-buffer command bases, index/dispatch addresses, coherency commands, and front-end draw/dispatch controls.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `reg<NAME>` expands to a register offset relative to its address block.
- `reg<NAME>_BASE_IDX` expands to the SOC15 base-address table index used with the offset.
- `// addressBlock:` comments identify the generated hardware address block.
- `// base address:` comments document each block's physical/register-base address in AMD's register database.

There are no callable APIs or C types here. Consumers normally use these constants through AMDGPU helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_SOC15_RLC`, golden-register table macros, and debug/register-dump helpers. Field composition and extraction live in the companion shift/mask header, not this offset header.

Important address blocks and families in this range include:

- Tail of `gc_gdspdec`: `regGDS_VMID6_BASE/SIZE` through `regGDS_VMID15_BASE/SIZE`, `regGDS_GWS_VMID0..15`, `regGDS_OA_VMID0..15`, GWS/OA reset registers, GDS context-switch counters/status, and `regGDS_MEMORY_CLEAN`.
- `gc_rasdec`: `regRAS_SIGNATURE_CONTROL`, `regRAS_SIGNATURE_MASK`, and signature registers for SX, DB, PA, SC, SPI, CB, and BCI sub-blocks.
- `gc_gusdec`: GUS IO/DRAM/GCEA combine flush controls, priority age/queuing registers, SDP credit/reserve/enable controls, RMI and EA controls, shader-array pipe configuration, VM safety controls, L2/EA mapping, PASID/L2A selection, SDP window registers, and L1 per-shader-array command/data in/out registers.
- `gc_gfxdec0`: the largest block in the chunk. It starts with DB depth/stencil render state, screen and generic scissors, target masks, viewport controls, primitive and rasterization controls, SX export controls, SPI interpolation/barycentric/attribute controls, shader wait counters, texture address and coherency controls, VGT/PA/GE primitive and tessellation state, context counters, DB/CB render-target and compression metadata bases, and color-buffer descriptors for slots 0 through 7.
- `gc_pfvf_cpdec`, `gc_pfvf_grbmdec`, `gc_pfvf_padec`, and `gc_pfvf_sqdec`: PF/VF-accessible controls including `regCP_MEC_CNTL`, `regCP_ME_CNTL`, `regGRBM_GFX_CNTL`, PA/VRS/binning/enhance controls, SQ runtime/performance/debug controls, and shader TMA base registers.
- `gc_pfonly_cpdec`, `gc_pfonly_cpphqddec`, `gc_pfonly_didtdec`, `gc_pfonly_spidec`, `gc_pfonly_tcpdec`, `gc_pfonly_gdsdec`, `gc_pfonly_utcl1dec`, `gc_pfonly_pmmdec`, and `gc_pfonly_gccacdec`: privileged-only controls for CP debug/fetch/DFY data, HPD/MES queue offsets/status, DIDT EDC thresholds/stall patterns/status, SPI debug/trap/reset/arbitration/resource-limit and compute wavefront context-save status, TCP invalidate/status/control/credit, GDS enhancement/restore, UTCL1 and GCR target/credit controls, PMM control, and extensive GC/SE CAC, EDC, PCC, power-break, throttle, hysteresis, and weighting registers.
- `gc_pfonly2_spidec`: `regSPI_RESOURCE_RESERVE_CU_0..15` and `regSPI_RESOURCE_RESERVE_EN_CU_0..15`, which reserve and enable compute-unit resources per CU index.
- Beginning of `gc_gfxudec`: command processor EOP done/fence addresses and data, pipeline statistics addresses and counters, scratch and atomic scratch registers, append/fence data, PFP/ME atomic pre-operation values, GDS atomic pre-operation values, ME memory command addresses/data, semaphore/timer registers, CP DMA PFP/ME controls and addresses, indirect-buffer and stream-table bases/sizes, doorbell base/size, PFP completion and metadata addresses, indirect draw/dispatch addresses, index base/type, GDS backup address, CP ME coherency command registers, RLC GPM perf counters, `regGRBM_GFX_INDEX`, and initial VGT/GE draw state through `regVGT_NUM_INDICES`.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution of symbolic register names into numeric offsets.

The implied runtime flow is:

1. A GC 11.0.3 driver path selects a `reg...` macro from this header.
2. The SOC15 helper combines the macro's offset with the GC instance and the macro's `_BASE_IDX` to form the actual register address.
3. The driver reads, writes, or read-modify-writes that register through AMDGPU MMIO, RLC-safe, indirect, or golden-setting helper paths.
4. The hardware block, firmware, command processor, shader processor, graphics pipeline, or privileged management logic applies the state.

For GDS and CP registers, higher-level code performs sequencing around queue setup, VMID assignment, context switch, fence emission, ring execution, DMA, and coherency commands. For DB/CB/PA/SPI/VGT/GE graphics state, command streams or driver setup code program these offsets as part of graphics pipeline state. For privileged PF-only blocks, firmware, bring-up, diagnostics, power management, or SR-IOV host code controls access and sequencing. This header does not encode access permissions, side effects, polling loops, reset ordering, or clear-on-read/write behavior.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists only in the GPU registers and in memory objects whose addresses are programmed through those registers.

Hardware state represented by this chunk includes VMID-specific GDS ranges, GWS/OA ownership, GDS context-switch counters, RAS signature latches, GUS credit and queue policy, graphics context state, render-target descriptors, compression/decompression bases, primitive/tessellation/raster state, shader interpolation/export setup, scratch registers, CP fence and statistics addresses, CP DMA addresses and commands, indirect-buffer bases, doorbell buffer layout, coherency command state, and privileged CAC/EDC/throttle/debug controls.

Many of these registers persist until rewritten, queue/context teardown, graphics state reprogramming, GPU reset, suspend/resume restoration, clock/power-gating loss, firmware reinitialization, or PF-level management intervention. Others are live counters, latches, status registers, command registers, or self-clearing controls. This generated offset header does not distinguish read-only, write-only, clear-on-write, sticky, or self-clearing semantics; consumers must rely on hardware documentation and existing driver sequences.

The `_BASE_IDX` value is part of address persistence at the software level. Most early registers in this chunk use base index `0` before the later address blocks switch to base index `1`, reflecting different SOC15 base entries. A wrong base index can address the wrong hardware aperture even when the offset value is correct.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h` supplies matching bit shifts and masks for many registers named here.
- AMDGPU SOC15 register helpers supply the actual address calculation and MMIO access behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c` includes this header and directly references GUS registers such as `regGUS_IO_RD_COMBINE_FLUSH`, `regGUS_IO_WR_COMBINE_FLUSH`, `regGUS_DRAM_COMBINE_FLUSH`, `regGUS_MISC2`, `regGUS_SDP_CREDITS`, and related SDP reserve/enable registers in IMU/RLC golden-value tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c` includes this offset header with the matching shift/mask header for GC 11.0.3-specific graphics behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c` includes this offset header for GC 11.0.3 graphics-hub integration.
- Broader `gfx_v11_0.c` code uses same-generation register families such as `regGDS_VMID0_BASE/SIZE`, `regCP_MEC_CNTL`, and `regPA_SC_VRS_SURFACE_CNTL_1` for GDS setup, CP pipe control, and golden settings.
- Nearby generation headers, especially GC 11.x and GC 12.x offset headers, use similar names but may not share identical offsets or base indices. Cross-generation reuse must go through the correct ASIC-specific header.

Runtime integration points include graphics pipeline state setup, command submission, KFD/compute queue management, VMID resource assignment, fence and event writeback, pipeline statistics, GDS backup/restore, coherency commands, SR-IOV PF/VF access partitioning, RAS diagnostics, power and current/activity management, EDC/DIDT throttling, clock/power gating, debug/trap handling, and GPU reset/suspend/resume restore paths.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong offset or `_BASE_IDX` compiles cleanly but directs MMIO to the wrong register or aperture.
- This chunk starts mid-block. The `gc_gdspdec` address-block comment and `GDS_VMID0..5` definitions are in the previous chunk, while this chunk starts at `GDS_VMID6_BASE`.
- This chunk ends mid logical user-config sequence. Later VGT/GE draw-state registers follow `regVGT_NUM_INDICES` in the next chunk.
- Repeated families are easy to mis-index. GDS VMID base/size pairs, GWS/OA VMID registers, CB color slot descriptors, SPI resource reserve/enables, and per-SE/CAC weight registers rely on stable numeric ordering.
- `_BASE_IDX` transitions matter. The early GDS/RAS block uses base index `0`, while GUS and most later graphics/PF/user-config blocks use base index `1`. Copying offsets without base-index awareness can break address calculation.
- PF/VF and PF-only boundaries are security-sensitive. Exposing PF-only controls to the wrong path could affect virtualization isolation, debug visibility, throttling, power behavior, or queue ownership.
- CP registers in `gc_gfxudec` are command-submission critical. Bad offsets for EOP fences, append data, DMA commands, IB bases/sizes, doorbells, or coherency registers can produce lost fences, stuck rings, corrupted command streams, or invalid memory accesses.
- DB/CB metadata and base-address registers are render-output critical. Wrong offsets can corrupt depth/stencil, color, compression metadata, or fast-clear state.
- GUS, UTCL1, GCR, and TCP controls interact with traffic ordering, credits, invalidation, and translation behavior. Incorrect programming can appear as hangs, memory faults, performance cliffs, or intermittent cache-coherency symptoms.
- RAS, EDC, CAC, DIDT, PCC, and power-break status/control registers may be latched, threshold-driven, or clear-sensitive. Offset mistakes can hide fault evidence or trigger inappropriate throttling.
- Register names that look generic, such as `regSCRATCH_REG*`, `regCP_*_ATOMIC_PREOP_*`, or `regGCR_*`, have generation- and block-specific semantics. They should not be substituted across ASIC families by name alone.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include GC 11.0.3 support. Missing, malformed, or renamed macros should surface in `imu_v11_0_3.c`, `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and shared GFX 11 paths.
- Mechanically compare every offset and `_BASE_IDX` in this chunk against AMD's authoritative GC 11.0.3 register database.
- Cross-check that registers with field-level programming have corresponding entries in `gc_11_0_3_sh_mask.h`.
- Verify repeated families for monotonic spacing and expected count: GDS VMID base/size pairs, GDS GWS/OA VMID registers, CB color slots 0-7, SPI resource reserve/enables 0-15, per-SE CAC weights, scratch registers, and CP address low/high pairs.
- Run IMU/RLC golden-setting initialization on GC 11.0.3 hardware and confirm the GUS golden values program the expected registers without RLC/IMU load failures.
- Exercise graphics workloads that use depth/stencil, scissor, rasterization, color targets, compression metadata, tessellation, primitive assembly, VRS/binning controls, and pipeline statistics.
- Exercise compute/KFD and graphics submission paths that depend on GDS allocation, CP MEC/ME controls, EOP fence writes, append buffers, CP DMA, indirect buffers, doorbells, wait/signal semaphores, coherency commands, and GDS backup addresses.
- Exercise SR-IOV or virtualized configurations where PF/VF-visible and PF-only blocks are separated, checking for access faults, isolation failures, or missing privileged setup.
- Exercise reset, suspend/resume, preemption, power/clock gating, throttling, and RAS/EDC injection or monitoring paths while checking CP status, EOP fences, queue progress, RAS signatures, EDC/DIDT status, CAC counters, and throttle status.
- Decode known-good register dumps with these offsets and compare the resolved names and base indices against reference tools, especially across the base-index `0` to `1` transition.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002523`. The final per-file research should merge this with neighboring chunks for full `gc_11_0_3_offset.h` coverage. In particular, the previous chunk owns the start of `gc_gdspdec` and the first GDS VMID registers, while the next chunk continues the `gc_gfxudec` VGT/GE user-config register sequence after `regVGT_NUM_INDICES`.

### subset-b-002524: lines 7490-9939

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h lines 7490-9939

## Purpose

This chunk is generated AMD GC 11.0.3 register offset metadata. It contains no executable C logic; it exports preprocessor constants that name MMIO/register-file offsets and paired `_BASE_IDX` values for the GC hardware IP block. The register names in this range are consumed by AMDGPU, GFXHUB, IMU, MES, KFD/debug, performance-monitoring, reset, and power-management code through SOC15 register helpers.

The selected range starts in the tail of a base GC graphics register span and then covers several address blocks:

- Base GC register span from `regVGT_NUM_INSTANCES` through `regSPI_ATTRIBUTE_RING_SIZE`: draw/geometry setup, primitive assembly, screen/trap controls, thread-trace userdata, GDS direct/atomic/streamout registers, and SPI configuration/throttling/attribute-ring controls.
- `gc_cprs64dec` at base `0x32000`: RS64 command-processor registers for MES, MEC, and graphics front-end firmware engines.
- `gc_gl1dec`, `gc_chdec`, `gc_gl2dec`, and `gc_gl1hdec`: cache, channel, burst, arbitration, retry, and soft-reset registers for GL1/GL1C/GL1H/GL2/CH front-end cache and transport blocks.
- `gc_perfddec` at base `0x34000`: performance counter data/readback registers, usually low/high counter halves and latency-stat data.
- `gc_perfsdec` at base `0x36000`: performance counter select/config/control registers, RLC streaming performance monitor controls, SQ thread-trace buffer controls, and GDFLL EDC hysteresis select/status.
- `gc_gdfll_gdfll_dec` and `gc_gdfll_se_gdfll_dec`: global and shader-engine GDFLL EDC hysteresis control/status registers.
- The final line begins the next `gc_grtavfs_grtavfs_dec` block, but no complete GRTAVFS register pair is included in this chunk.

Although the repository path is under `ceph-client`, this file is GPU driver hardware metadata and is unrelated to Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or direct I/O operations in this range. The API is the generated macro namespace:

- `reg<NAME>` maps a hardware register to a numeric offset such as `0x224d`, `0x2800`, `0x3c80`, or `0x48e9`.
- `reg<NAME>_BASE_IDX` gives the register base-index selector used by SOC15-style helpers; every macro in this chunk uses base index `1`.
- Consumers commonly use generated aliases from the same offset header family, such as `mm<NAME>` or `ix<NAME>`, together with bit definitions from `gc_11_0_3_sh_mask.h`.

Major register groups in this chunk:

- `VGT_*` and `GE_*`: instance counts, tessellation factor ring size and memory base, hull-shader off-chip parameters, vertex index bounds, primitive instance base, graphics engine control, user VGPR registers/enables, stereo control, primitive allocation, GS fast-launch workgroup dimensions, and GS output primitive type.
- `PA_*`: line stipple state, screen extent min/max values, and P3D/HP3D/general trap-screen enable, horizontal/vertical position, occurrence, and count registers.
- `SQ_THREAD_TRACE_USERDATA_*` and later `SQ_THREAD_TRACE_*`: shader thread-trace userdata slots, trace buffer base/size pairs, trace control/masks, write pointer, status, draw/marker counters, and dropped-counter telemetry.
- `GDS_*`: GDS read/write windows, burst access, atomics, GWS resource state, ordered-append counters/addressing, streamout counters, and GS scratch-style data registers.
- `SPI_*`: shader processor interpolator/global SPI configuration, wave limits, GS throttling, attribute ring base/size, and performance-counter select/config entries.
- `CP_MES_*`, `CP_MEC_*`, and `CP_GFX_RS64_*`: RS64 firmware program-counter and trap-vector start registers, interrupt enable/pending/status data, instruction pointers, machine CSRs (`MSTATUS`, `MEPC`, `MCAUSE`, `MBADADDR`, `MIP`, `MIE`, `MISA`, vendor/arch/impl/hart IDs), cycle/time/retired-instruction counters, process quantum and doorbell controls, GP registers, local/data/instruction/scratch apertures, cache operation controls, perfcount controls, interrupt data slots, and repeated data-cache aperture base/mask/control windows.
- `GL1*`, `GL2*`, `CH*`, and `CHA/CHC/CHCG/CHI`: cache/channel arbitration controls, burst masks/controls, status, retry, clock-gating overrides, virtual-channel enable, GL2 address-match controls, writeback/invalidate and soft-reset controls, command-merge controls, load-balancer counter controls/data/selects, and response throttling.
- `*_PERFCOUNTER*_LO`/`HI` under `gc_perfddec`: sampled counter data for CP, GRBM, GE1/GE2, PA, SPI, PC, SQ/SQG, SX, GCEA, GDS, TA, TD, TCP, GL2, GL1, CH, CB, DB, RLC, RMI, GCR, UTCL1, CHA, and GUS blocks.
- `*_PERFCOUNTER*_SELECT`, `*_SELECT1`, filters, modes, and result controls under `gc_perfsdec`: event-selection and configuration registers that feed the matching `gc_perfddec` readback counters.
- `RLC_SPM_*`: RLC streaming performance monitor ring base/size/pointers, segment threshold/size, global and shader-engine mux selection address/data windows, accumulator data/control/status registers, pause/status/mode, graphics-clock counts, RSPM request/return mailboxes, command/ack, and GPU IOV perf-count access windows.
- `GDFLL_*EDC_HYSTERESIS_*`: electrical-design-current hysteresis controls and status for global and shader-engine GDFLL blocks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by code that includes the generated header and performs register access:

1. A GC 11.0.3 driver path includes `gc_11_0_3_offset.h`, usually with `gc_11_0_3_sh_mask.h`.
2. The path chooses a register macro for direct MMIO, SOC15 indexed access, register-list save/restore, golden-register programming, firmware setup, or performance-monitoring configuration.
3. The offset and base index are passed through helpers such as `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, or `WREG32`.
4. The actual ordering, synchronization, power-state checks, firmware ownership, and read/modify/write behavior live in the consuming AMDGPU paths and hardware programming rules, not in this generated file.

The chunk names registers used during graphics setup, MES/MEC/GFX firmware control, trap/debug capture, cache and fabric control, performance-counter programming, streaming perf sampling, and EDC hysteresis. It does not describe when those registers may be safely touched, which registers are read-only, which bits are self-clearing, or which firmware owns a register at runtime.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It is compile-time metadata.

The represented hardware state is broad:

- Draw and geometry state includes instance counts, vertex bounds, transform-feedback/tessellation memory addresses, and GE/VGT/SPI programming that can affect submitted draws.
- Trap, thread-trace, and SQ-related state includes user payload registers, trace buffers, masks, write pointers, statuses, draw/marker counters, and dropped-trace telemetry.
- GDS and streamout state includes memory access windows, atomic source/destination operands, ordered-append counters, GWS allocation counters, and streamout written/needed primitive counters.
- RS64 CP/MES/MEC/GFX state includes firmware PC/vector/counter/CSR values, interrupt pending/data state, doorbell routing, local aperture mappings, scratch/instruction/data-cache aperture setup, and firmware-visible GP registers.
- GL1/GL2/CH state includes arbitration, burst throttling, retry/status, writeback/invalidate, soft-reset, address-match, response-throttle, and clock-gating override values.
- Performance state includes both selectable event sources and readback counters across many GC subblocks, plus RLC SPM ring state, mux selections, accumulator RAM windows, request/response mailboxes, pause/status, and clock-count registers.
- GDFLL EDC hysteresis state controls and reports droop/current-related hysteresis behavior for global and shader-engine domains.

Persistence is hardware-defined. Some values are programmed during initialization or workload setup and survive until GPU reset, suspend/resume, power-gating, or explicit reprogramming. Others are volatile live counters, pointers, firmware CSRs, interrupt payloads, status bits, reset strobes, indirect windows, or hardware-owned fields that can change while command processors and shader engines run. The macros provide addresses only; they do not encode ownership or lifetime.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h`, which supplies field shifts and masks for the registers named here. Consumers must keep the offset and mask headers from the same GC generation together.

Observed include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`

Related GC 11.0.3 firmware declarations appear in `gfx_v11_0.c`, `mes_v11_0.c`, and `imu_v11_0.c` for PFP, ME, MEC, RLC, MES, MES2/MES1, and IMU firmware blobs. Those firmware paths are natural integration points for this chunk's CP/MES/MEC/GFX RS64 control registers and RLC/SPM/performance state.

Key integration surfaces:

- GFX 11.0.3 bring-up and reset code that programs golden registers, initializes rings, configures GE/VGT/SPI state, and manages CP firmware engines.
- MES/MEC scheduling and queue-management paths that rely on RS64 program counters, trap vectors, doorbells, local apertures, scratch state, and pending interrupt registers.
- GFXHUB and memory-system code that touches GL1/GL2/cache/channel state or uses address-match and invalidation controls during VM/cache setup.
- Debug, trap, KFD, and profiling flows that consume SQ thread trace, GDS, PA trap screen, and perf counter registers.
- RLC SPM and perfmon infrastructure that programs select registers under `gc_perfsdec`, reads counter data under `gc_perfddec`, and manages SPM rings/muxes/accumulators.
- Power, reliability, and validation flows that observe or tune GDFLL EDC hysteresis state.

## Risks And Edge Cases

- Header generation mismatches are the highest risk. Using `gc_11_0_3_offset.h` with a different generation's `*_sh_mask.h`, firmware path, or register table can compile while targeting the wrong register.
- These constants are untyped preprocessor values. The compiler cannot distinguish a counter select register from a counter data register, an RLC SPM indirect address from data, or a read-only status register from a writable control register.
- Every macro in this chunk has `_BASE_IDX` value `1`; code that assumes base index `0`, bypasses SOC15 helpers, or mixes direct and indexed addressing can silently access the wrong block.
- RS64 CP/MES/MEC/GFX registers are firmware-facing. Reads can observe live firmware state, and writes can corrupt firmware execution, interrupt handling, doorbell routing, aperture mappings, or cache behavior if not sequenced with halt/reset/ownership rules.
- Repeated aperture windows (`CP_MES_DC_APERTURE*`, `CP_MEC_DC_APERTURE*`, `CP_GFX_RS64_DC_APERTURE*`) are easy to index incorrectly. Off-by-one aperture programming can expose the wrong local/data/instruction/scratch address range to firmware.
- Performance counters and RLC SPM registers are stateful. Reprogramming select registers while counters are active, racing ring pointers, or mixing per-SE/global mux selections can produce misleading samples or stall the monitoring path.
- Some registers are live hardware counters split into `LO` and `HI` halves. Readers need rollover-safe sampling and should not assume a single 32-bit read is enough.
- Cache/channel controls such as GL2 writeback/invalidate, soft reset, address-match, and response throttling can affect correctness and performance globally if written outside documented quiescent states.
- GDS direct and atomic windows expose hardware data/control operations rather than ordinary memory. Incorrect access can clobber streamout/GWS/OA state or interfere with running workloads.
- Trap-screen, thread-trace, and shader debug registers may be per-shader-engine, privilege-sensitive, or workload-sensitive. Sampling while waves execute can produce transient or inconsistent data unless the caller coordinates with debug/trap mechanisms.
- The chunk boundary is artificial: it starts after earlier VGT/GE register definitions and ends immediately after the next address block header. Adjacent chunks are needed for the complete file-level map.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware/runtime smoke coverage:

- Compile AMDGPU with GC 11.0.3 support and ensure `imu_v11_0_3.c`, `gfx_v11_0_3.c`, and `gfxhub_v3_0_3.c` include this header without macro conflicts.
- Generated-header checks that every `reg*` macro in this range has a matching `_BASE_IDX` macro, all base indices are intentional for the address block, and companion field definitions exist where the register has named fields in `gc_11_0_3_sh_mask.h`.
- Register-list/golden-register tests that verify `SOC15_REG_OFFSET` and `SOC15_REG_ENTRY` resolve expected offsets for GE/VGT/SPI, CP RS64, GL1/GL2/CH, RLC SPM, and perf-counter registers on GC 11.0.3 ASICs.
- Firmware bring-up tests for PFP/ME/MEC/RLC/MES/IMU that cover RS64 program-counter/vector setup, interrupt pending/data paths, doorbell controls, and local aperture programming.
- Graphics and compute workload smoke tests that exercise VGT/GE/SPI draw setup, GDS/streamout counters, and GWS/OA resources while checking for hangs, malformed draws, or unexpected protection faults.
- SQ thread-trace and profiling tests that allocate trace buffers, program masks/control registers, run known workloads, and verify write pointers, status, draw/marker counters, and dropped counters are plausible.
- Perfmon/SPM tests that program select registers, read low/high data pairs with rollover handling, configure RLC SPM ring/mux/accumulator state, and confirm counters advance under targeted workloads.
- Reset, suspend/resume, runtime power-management, and GPU recovery tests that verify volatile RS64, cache, perfmon, and GDFLL/EDC state is restored or intentionally reset.
- Regression signals include invalid firmware PCs or pending interrupts after init, stuck SPM ring pointers, zero or saturated performance counters under load, trace dropped counters rising unexpectedly, cache invalidation timeouts, GDS/streamout counter mismatches, or failures limited to GC 11.0.3 hardware.

### subset-b-002525: lines 9940-12094

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h lines 9940-12094

## Scope

This chunk is the final large slice of the generated AMD GC 11.0.3 register offset header. It contains only C preprocessor constants: 2,083 `#define` statements across 2,155 lines, including 1,728 `reg*` MMIO offset macros, 864 matching `_BASE_IDX` macros for `reg*` entries, and 355 `ix*` indirect-register index macros. There are no functions, structs, enums, globals, locks, allocations, I/O calls, or executable branches in this range.

The chunk starts inside the `gc_grtavfs_grtavfs_dec` address block after the block comment from the previous chunk, covers GRTAVFS, hypervisor, CP hypervisor, GRBM hypervisor, GCVM shared hypervisor, RLC, RLCS, PF/VF RLC, power/clock, PSP, GFX IMU, CAC indirect, RTAVFS indirect, and SQ wave-debug indirect offsets, then ends with the header guard `#endif`.

Although this file lives under `sources/distributed-fs/ceph-client`, it is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_11_0_3_offset.h` gives symbolic register addresses for AMD graphics core 11.0.3. Driver code combines these offsets with SOC15 MMIO helpers, indirect-register accessors, and companion shift/mask/default headers to program and inspect GPU hardware without hard-coding numeric addresses at call sites.

This chunk's purpose is to expose register locations for:

- RTAVFS/GRTAVFS clock-voltage and adaptive-voltage-frequency-scaling access windows.
- RLC and GPU IOV hypervisor state, including virtual-function enable/masks, scheduler state, doorbell status, VM busy state, SDMA status, firmware memory windows, scratch windows, and virtualization reset/response registers.
- Command processor hypervisor microcode and instruction/data memory windows for PFP, ME, MEC, MES, CPC, and GFX RS64 blocks.
- GRBM hypervisor selector/data windows and GCVM shared frame-buffer size/offset registers per VF.
- Core RLC, RLCS, and PF/VF RLC control/status, timers, interrupts, doorbells, safe mode, power-gating, clock counting, UTCL1 errors, profiling, residency counters, IMU/SMU mailboxes, and firmware bootload/reset vectors.
- GC power and clock-gating controls for graphics pipeline blocks.
- PSP-facing CP/GRBM/RLC debug, CAM, security, firewall, and data-memory index windows.
- GFX IMU mailbox, scratch, telemetry, interrupt, clock/reset, RAM, timer, fence, bootloader, and PSP-facing registers.
- CAC and RTAVFS indirect index spaces plus SQ wave-debug indirect registers.

## Important APIs, Types, And Macros

The only API surface is the macro namespace generated for the hardware register database:

- `reg<NAME>` macros give MMIO register offsets as word offsets, not byte offsets.
- `reg<NAME>_BASE_IDX` macros select the SOC15 register-base instance. Every visible `reg*` entry in this chunk uses base index `1`.
- `ix<NAME>` macros give indices for indirect register spaces such as `gccacind`, `secacind`, `grtavfsind`, and `sqind`.
- `// addressBlock:` and `// base address:` comments group register names by hardware decoder/address block.

There are no callable APIs or C types in this header. Runtime consumers generally use these constants through AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, indirect wave/CAC accessors, `SOC15_REG_OFFSET`, and field helpers from matching shift/mask headers.

Important macro families in this chunk include:

- GRTAVFS/RTAVFS registers: `regGRTAVFS_*`, `regGRTAVFS_SE_*`, `regRTAVFS_*`, and `ixRTAVFS_REG0..194` provide direct and indirect windows for AVFS register address/data/control/status, target frequency/voltage, soft reset, PSM, and clock controls.
- Hypervisor and IOV registers: `regRLC_GPU_IOV_*`, `regRLC_HYP_*`, `regRLC_GPU_IOV_SDMA0..7_STATUS`, `regRLC_GPU_IOV_SDMA0..7_BUSY_STATUS`, `regRLC_GPU_IOV_VF_*`, `regRLC_GPU_IOV_SCH_*`, and `regRLC_GPU_IOV_INT_*` describe virtual-function scheduling, doorbells, masks, interrupts, reset requests, scratch, and SDMA status.
- RLC firmware and memory windows: `regRLC_GPM_UCODE_*`, `regRLC_RLCP_IRAM_*`, `regRLC_RLCV_IRAM_*`, `regRLC_LX6_*`, `regRLC_PACE_*`, `regRLC_SRM_*`, and related scratch/data address pairs expose firmware upload/debug surfaces.
- CP hypervisor registers: `regCP_HYP_*`, aliases such as `regCP_PFP_UCODE_*`, `regCP_ME_RAM_*`, `regCP_MEC_ME*_UCODE_*`, instruction-cache and data-cache base/bound controls, MES/MEC memory base aliases, and GFX RS64 base/bound registers.
- GRBM/GCVM hypervisor registers: `regGRBM_GFX_INDEX_SR_*`, `regGRBM_GFX_CNTL_SR_*`, `regGC_IH_COOKIE_0_PTR`, `regGRBM_SE_REMAP_CNTL`, and `regGCMC_VM_FB_SIZE_OFFSET_VF0..15`.
- Core RLC registers: `regRLC_CNTL`, `regRLC_STAT`, timer and clock-count registers, `regRLC_RLCG_DOORBELL_*`, power-gating controls, SERDES access, GPM general registers, SRM indexed address/data registers, UTCL1 control/error/status registers, PACE/RLCV/RLCP/XT doorbells, firewall, profiling, residency counters, GFX IH client status, SPM delay accessors, LX6/XT core status, SMU command/message/argument registers, and IMU bootload/reset-vector registers.
- RLCS registers: `regRLC_RLCS_*` covers decoder start/end, exception registers, clock/deep-sleep controls, IOV state, soft reset, interrupt controls and info, bootload status, power brake, general/auxiliary registers, GCR data/status, IMU/RLC message and telemetry registers, RAM access, IH controls, and `regRLC_RLCS_DEC_END`.
- PF/VF RLC registers: `regRLC_SAFE_MODE`, SPM sample/MC/interrupt registers, CSIB address/length, CP scheduler/EOF interrupt registers, and spare interrupt registers.
- Power/clock registers: `regCGTS_*`, `regCGTT_*`, `regCGTX_*`, `regSQ_*_CLK_CTRL`, `regICG_*`, `regGFX_ICG_*`, `regTA_CGTT_CTRL`, `regDB_CGTT_*`, `regCB_CGTT_*`, `regGL1*`, `regCHI_*`, `regGUS_*`, and related block clock-gating controls.
- PSP/debug registers: `regCP_MES_DM_INDEX_*`, `regCP_MEC_DM_INDEX_*`, `regCP_GFX_RS64_DM_INDEX_*`, `regCPG_PSP_DEBUG`, `regCPC_PSP_DEBUG`, `regGRBM_IOV_ERROR_FIFO`, security/CAM registers, and `regRLC_FWL_FIRST_VIOL_ADDR`.
- GFX IMU registers: `regGFX_IMU_C2PMSG_0..47`, access-control registers, power-management IRQ, MP1/RLC mailboxes, status, SOC access, VF control, telemetry, scratch, GTS offsets, PIC/IH interrupt controls, fuse/clock/doorbell/DPM/reset/isolation controls, RAM access, fence logging, timers, core status, and PSP bootloader/I-RAM windows.
- Indirect CAC/SQ registers: `ixGC_CAC_*`, release/stall/power-brake LUTs, fixed-pattern performance counters, `ixSE_CAC_*`, and SQ wave debug indices such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO/HI`, `ixSQ_WAVE_TTMP0..15`, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_EXEC_LO/HI`.

## Control Flow

This header has no runtime control flow. It affects behavior only when compiled C code expands these macros while calculating register addresses.

The implied runtime flow is:

1. GC 11.0.3-specific driver code includes this offset header, often with `gc_11_0_3_sh_mask.h` and default-value headers.
2. The driver selects a `reg*` macro and base index for SOC15 MMIO access, or an `ix*` macro for an indirect aperture.
3. AMDGPU helpers translate the symbolic offset into a device register address and perform read, write, poll, or read-modify-write operations.
4. Hardware/firmware state machines in RLC, CP, GRBM, PSP, IMU, SMU, CAC, RTAVFS, or SQ observe the register access and perform the actual operation.

Examples of consumer paths in this tree include `amdgpu/imu_v11_0_3.c`, `amdgpu/gfxhub_v3_0_3.c`, and `amdgpu/gfx_v11_0_3.c`, which include this GC 11.0.3 offset header. Related generation code such as `gfx_v11_0.c` uses the same register families for RLC safe-mode commands, IMU C2P mailbox access, and SQ wave debug reads.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists in GPU registers, firmware RAMs, doorbell state, MMIO-visible status latches, indirect register spaces, and memory-backed firmware/queue structures.

State described by this chunk includes:

- Firmware code/data windows and checksums for RLC, CP, PFP, ME, MEC, MES, GPM, RLCP, RLCV, LX6, PACE, and GFX IMU blocks.
- Virtualization and IOV state such as VF enable bits, VF masks, active function ID, scheduler control, SDMA status, VM busy state, interrupt status/disable/force, scratch windows, and virtual reset requests/responses.
- Doorbell ranges, controls, statuses, and captured data for RLCG, RLCV, RLCP, XT, IMU, and CPAXI monitoring.
- Power-management and clock state such as RLC power gating, dynamic/static PG status, residency counters, CGTT/ICG controls, memory sleep, SMU clock requests, SMU commands, and AVFS target frequency/voltage registers.
- Error, security, and debug state such as UTCL1 error/status, firewall violations, GRBM IOV error FIFO, security/CAM data, GFX IH client statuses, CP/PSP debug windows, SPM/SPP profiling state, and SQ wave debug registers.
- IMU mailbox, scratch, telemetry, timer, reset, isolation, fence, RAM, bootloader, and RLC/MP1/SOC handshake state.

Many registers are live hardware status or command apertures rather than durable software state. Some values persist until GPU reset, power-gating loss, suspend/resume reinitialization, firmware reload, queue teardown, or driver reprogramming. Some status bits may be clear-on-read, write-one-to-clear, self-clearing, firmware-owned, or access-restricted, but this offset header does not encode those side-effect classes.

## Dependencies And Integration Points

This chunk depends on the GC 11.0.3 register description remaining internally consistent:

- The companion GC 11.0.3 shift/mask header supplies bitfield layouts for many registers named here.
- Default-value headers for nearby GC 11.x generations provide reset-value context where generated defaults exist.
- SOC15 register helper infrastructure interprets `reg*` offsets and `_BASE_IDX` values.
- Indirect access helpers interpret `ix*` indices for CAC, RTAVFS, and SQ debug apertures.
- Firmware loading and runtime management code must agree with the instruction/data memory windows exposed here.

Integration points include AMDGPU graphics initialization, RLC bring-up, CP/MES/MEC firmware upload, PSP coordination, GFXHUB/VM configuration, SR-IOV scheduling, VF reset handling, SDMA/queue status attribution, interrupt handling, safe-mode entry/exit, clock/power gating, SMU messaging, IMU boot and telemetry, shader profiling/thread tracing, CAC/power-brake tuning, and wavefront debug/register-dump tooling.

## Risks And Edge Cases

- Generated-header drift is the main risk. An incorrect numeric offset or base index can compile cleanly but direct reads/writes to the wrong hardware register.
- The line range starts after the `gc_grtavfs_grtavfs_dec` address-block comment, so the first visible GRTAVFS macros rely on previous-chunk context.
- Several names are aliases for the same offset, especially CP hypervisor and MES/MEC memory-base registers. Consumers must use aliases consistently with the intended firmware block and access mode.
- The large RLC/RLCS region mixes configuration, status, interrupt, firmware-memory, power, doorbell, error, and mailbox registers. Full-register writes or stale generation assumptions can break firmware sequencing, power gating, or queue progress.
- Doorbell and scheduler offsets are liveness-sensitive. Wrong RLCG/RLCV/RLCP/XT/IMU doorbell ranges or status offsets can cause lost notifications, stuck queues, or misleading diagnostics.
- IOV and VF registers are isolation-sensitive. Misprogramming VF masks, active function IDs, VM busy status, reset requests, scratch windows, or GCMC VF frame-buffer offsets can corrupt virtualization behavior or hide guest faults.
- Firmware upload windows require strict address/data ordering. Misusing `*_ADDR`, `*_DATA`, `*_BASE_LO/HI`, and `*_BOUND_LO/HI` aliases can load code or data into the wrong microcontroller aperture.
- PSP, GRBM security/CAM, and firewall registers are privilege-sensitive. Incorrect offsets can affect protected debug/security flows or obscure first-violation attribution.
- Clock, power, memory-sleep, AVFS, and IMU reset/isolation registers interact with active hardware state. Access must follow existing sequencing and polling rules rather than treating offsets as ordinary storage.
- Indirect `ix*` register spaces are not MMIO offsets. Accidentally passing `ixSQ_*`, `ixGC_CAC_*`, or `ixRTAVFS_*` constants through direct SOC15 MMIO helpers would address the wrong space.
- The RTAVFS indirect list skips `ixRTAVFS_REG188`; tools that assume a contiguous 0..194 range may mis-handle the gap.
- The chunk closes the header guard. Any generated merge conflict or missing `#endif` around this range would break all translation units including this header.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include GC 11.0.3 support. Missing or malformed macros should surface in `imu_v11_0_3.c`, `gfxhub_v3_0_3.c`, `gfx_v11_0_3.c`, shared GFX 11 code, and related firmware/power/debug paths.
- Mechanically compare every offset and `_BASE_IDX` in this chunk against AMD's authoritative GC 11.0.3 register database.
- Cross-check matching register names in `gc_11_0_3_sh_mask.h` and default headers where applicable; offsets, masks, and defaults must describe the same hardware generation.
- Run static checks that every `reg*` macro has a paired `_BASE_IDX` macro, every paired entry in this chunk uses the expected base index, and `ix*` macros are not paired with `_BASE_IDX`.
- Validate alias groups intentionally share offsets, especially CP/PFP/ME/MEC/MES memory windows and GRBM CAM/security aliases.
- Boot affected GC 11.0.3 hardware and exercise graphics/compute queue creation, firmware loading, ring submission, fence progress, VM fault handling, SDMA activity, and SR-IOV paths if available.
- Exercise RLC safe mode, GPU reset, suspend/resume, power-gating, clock-gating, memory-sleep, SMU messaging, and IMU boot/telemetry while checking for stuck polls or timeout regressions.
- Exercise interrupt/error paths and inspect CP/RLC/RLCS/GRBM/UTCL1/firewall/IOV diagnostic registers for sane attribution.
- Read SQ wave debug registers via the proper indirect path and compare wave status, PC, TTMP, M0, and EXEC values against known-good debug tooling.
- Use register-dump comparison against reference hardware or firmware logs for RLC doorbells, RLC/IMU mailboxes, GFX IMU C2P messages, CAC indirect registers, RTAVFS indirect registers, and PSP-facing debug/CAM windows.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002525`. The final per-file research should merge this with neighboring chunks for full `gc_11_0_3_offset.h` coverage. The previous chunk owns the address-block context immediately before line 9940, and this chunk owns the final header guard closure after the SQ indirect register definitions.
