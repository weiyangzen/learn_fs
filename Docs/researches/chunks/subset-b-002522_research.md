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
