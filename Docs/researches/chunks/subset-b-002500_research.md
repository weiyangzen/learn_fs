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
