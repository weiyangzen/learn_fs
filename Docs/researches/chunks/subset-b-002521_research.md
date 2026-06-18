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
