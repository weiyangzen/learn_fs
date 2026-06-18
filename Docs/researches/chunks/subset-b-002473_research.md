# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 7446-9968

## Scope

This chunk is a late segment of the generated AMD GC 10.3.0 register-offset header. It covers lines 7446 through 9968 and defines 1,212 register-offset macros plus 1,212 matching `_BASE_IDX` macros. The range begins in the tail of the CP MES register block, continues through GUS, GL1/CH/GL2, GC performance counter data/select/config blocks, GRTAVFS, RLC, RLC shadow/control blocks, GC power/clock-gating controls, and ends inside the beginning of the hypervisor CP microcode access block.

The content is declarative only. There are no C functions, structs, enums, branches, loops, locks, allocations, or direct software side effects. The exported interface is a set of preprocessor constants that name GC 10.3.0 MMIO register offsets and the register-base selector used by SOC15 register helpers.

## Purpose

`gc_10_3_0_offset.h` supplies symbolic register addresses for AMDGPU, KFD, SDMA, and SMU code that targets GC 10.3.0-class hardware. Driver code pairs these offsets with field definitions from `gc_10_3_0_sh_mask.h` and reset/default values from `gc_10_3_0_default.h`, then uses helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `RREG32_FIELD15`, and SMU/PSP register access wrappers instead of embedding raw MMIO addresses.

This slice concentrates on low-level graphics-control surfaces:

- CP MES scratch/general-purpose, debug-memory index/data, performance counter control, and pending-interrupt registers.
- GUS arbitration, priority, queueing, credit/reserve, latency, error, L1 channel/statistics, and performance counter registers.
- GL1, channel, GL2 cache/arbiter/status, steering, L2 writeback/invalidate, soft-reset, match/mask, and load-balancer registers.
- Performance counter data and select/config spaces for CP, GRBM, GE, PA, SPI, SQ, SX, GDS, TA/TD/TCP, CB/DB, RLC, RMI, UTCL1, GCR, GL1A/GL1C, CH/CHA/CHC/CHCG, GUS, GCVML2, GCUTCL2, and SDMA0-3.
- GRTAVFS/RTAVFS indirect access and target frequency/voltage controls.
- RLC firmware/control/status, timers, interrupts, load-balancer, power-gating, clock counting, doorbells, safe mode, scratch, log, ucode/IRAM, debug, GPM, SRM, XT, and microcontroller-control registers.
- RLCR and RLCS shadow/control/status registers for RLC context, exceptions, clock/power-management handshakes, interrupt handling, virtualization/IOV state, diagnostics, and bootload status.
- GC power decoder clock-gating/throttling controls for most graphics subblocks.
- Hypervisor CP ucode address/data aliases at the chunk end.

## Address Blocks Covered

Visible address-block boundaries in this range are:

- Continuation from the preceding CP MES block: `mmCP_MES_GP5_HI` through `mmCP_MES_PENDING_INTERRUPT`.
- `gc_gusdec`, base `0x33000`: GUS IO/DRAM priority, combining, credits, reserves, misc, latency/error, L1 channel, and GUS performance/status registers.
- `gc_gl1dec`, base `0x33400`: GL1 DRAM burst, arbiter status, pipe steering, GL1C status/UTCL0 retry.
- `gc_chdec`, base `0x33600`: channel arbiter, burst, credit, pipe steering, VC5, CHC/CHCG control and status.
- `gc_gl2dec`, base `0x33800`: GL2C/GL2A control, address match, writeback/invalidate, soft reset, CM/LB state, and pipe steering.
- `gc_perfddec`, base `0x34000`: performance counter result low/high and latency data registers across many GC subblocks.
- `gc_gcvml2prdec`, base `0x353a0`, and `gc_gcvml2perfddec`, base `0x353e0`: GCMC VM L2, GCUTCL2, and GCVML2 performance counter result registers.
- `gc_sdma0_sdma0perfddec` through `gc_sdma3_sdma3perfddec`, bases `0x35980`, `0x359b0`, `0x359e0`, and `0x35a10`: SDMA performance counter result registers.
- `gc_perfsdec`, base `0x36000`: performance counter select, select1, mode, bins, config, result-control, window, draw-object/window, and misc control registers.
- `gc_gcvml2pldec`, base `0x374b0`, and `gc_gcvml2perfsdec`, base `0x374f0`: GCMC VM L2, GCUTCL2, and GCVML2 performance counter config/select/mode registers.
- `gc_sdma0_sdma0perfsdec` through `gc_sdma3_sdma3perfsdec`, bases `0x37880`, `0x378b0`, `0x378e0`, and `0x37910`: SDMA performance counter config/select/misc registers.
- A bare generated `base address: 0x3a000` marker with no visible `addressBlock:` label in this chunk and no local register definitions before the next block.
- `gc_grtavfsdec`, base `0x3ac00`: GRTAVFS/RTAVFS indirect register address/data/control/status and target frequency/voltage controls.
- `gc_rlcdec`, base `0x3b000`: the largest local region, covering RLC control, firmware, status, timing, interrupts, power-gating, load-balancer, debug, logs, scratch, doorbell, safe-mode, ucode, IRAM, SRM, GPM, and XT registers.
- `gc_rlcrdec`, base `0x3b800`: RLC SPP CAM and PACE scratch access registers.
- `gc_rlcsdec`, base `0x3b980`: RLC shadow/control/status, exception, clock/power, IOV, interrupt-handler, WGP, bootload, auxiliary, KMD log, and decoder-end registers.
- `gc_pwrdec`, base `0x3c000`: CGTS status/disable registers and CGTT/CAC clock-gating controls across SPI, PC, BCI, VGT, IA, WD, GS/NGG, PA, SC, SQ, SX, TD/TA, TCPI/TCPF, GDS, DB, CB, GL2, CP/CPF/CPC, RLC, RMI, GCR, UTCL1, GCEA, SE, GC, GRBM, GUS, and PH.
- `gc_hypdec`, base `0x3e000`: CP PFP/ME/CE microcode address/data aliases at the end of the chunk.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated macro namespace:

- Every register name is emitted as `#define mm<REGISTER> <offset>`.
- Every register has a companion `#define mm<REGISTER>_BASE_IDX 1` in this range. Consumers pass the base index into SOC15-style address calculation so the same offset can be resolved against the proper register aperture/base.
- Alias registers intentionally share offsets in several places. Examples include `mmGRTAVFS_RTAVFS_REG_ADDR` and `mmRTAVFS_RTAVFS_REG_ADDR`, `mmRLC_GPM_STAT` and `mmRLC_RLCS_GPM_STAT`, and the hypervisor/non-hypervisor CP ucode aliases such as `mmCP_HYP_PFP_UCODE_ADDR` and `mmCP_PFP_UCODE_ADDR`.
- Low/high register pairs are common for 64-bit counters, timestamps, clock counts, doorbell payloads, scratch/log addresses, and ucode/data access windows.
- Repeated performance blocks are named by client and counter number, for example `mmSQ_PERFCOUNTER*_LO/HI`, `mmSQ_PERFCOUNTER*_SELECT`, `mmPA_SC_PERFCOUNTER*`, `mmSDMA*_PERFCOUNTER*`, and `mmGCMC_VM_L2_PERFCOUNTER*`.
- Control/status/readback naming conventions are visible in suffixes such as `CNTL`, `CTRL`, `STAT`, `STATUS`, `REQ`, `RESPONSE`, `ENABLE`, `DISABLE`, `CLEAR`, `FORCE`, `DEBUG`, `SCRATCH`, `LOG`, `UCODE`, `IRAM`, `DOORBELL`, `SOFT_RESET`, `CLK_CTRL`, and `PERFCOUNTER`.

The header does not encode field widths, read/write permissions, sticky-bit behavior, reset values, or clear semantics. Those come from the matching shift/mask/default headers and from hardware documentation or calling-code conventions.

## Control Flow And State Behavior

There is no local software control flow. Runtime behavior happens when included driver code uses these constants to read or write MMIO registers.

The named registers describe several hardware state machines and persistent register banks:

- CP MES state: general-purpose registers, debug-memory indirect access, performance counter control, and pending interrupts reflect micro-engine scheduling/diagnostic state.
- Cache/channel/GUS state: GL1/GL2/channel/GUS controls and status registers affect arbitration, client credits, data-path steering, cache invalidation/writeback, retry, soft reset, latency sampling, and error reporting. Values persist in hardware until reset, power-gating loss, firmware restore, or explicit driver/firmware writes.
- Performance monitoring state: counter result registers accumulate or expose selected events; select/config/mode registers determine which events are counted. Programming normally follows a configure-select-enable-sample-read sequence in caller code, not in this header.
- GRTAVFS/RTAVFS state: indirect register address/data/control/status plus target frequency/voltage registers participate in adaptive voltage/frequency scaling handshakes.
- RLC state: RLC control, firmware, timers, interrupts, GPM threads, load balancing, power-gating, clock counting, doorbells, scratch/log/ucode/IRAM access, safe-mode, and SRM registers are part of the RLC firmware and graphics power-management control plane. These registers are often tightly ordered with firmware loading, PSP/SMU handshakes, GFXOFF, CG/PG transitions, and GPU reset.
- RLCR/RLCS state: shadow/context, exception, bootload, IOV, interrupt-handler, WGP, and auxiliary registers reflect saved/restored RLC context and virtualization/diagnostic state.
- GC power/clock-gating state: `CGTS_*`, `CGTT_*`, `*_CGTT_*`, and `*_CAC_*` registers influence clock gating, coarse/fine-grained power behavior, and per-block clock controls. Writes can immediately affect access latency and block availability.
- CP hypervisor ucode windows: address/data aliases are indirect windows for PFP/ME/CE microcode access. Correct sequencing and ownership are external to this generated file.

Read-only, write-only, write-one-to-clear, sticky, and volatile behavior cannot be proven from the offset macros alone. Names such as `STATUS`, `STAT`, `RD_DATA`, `RD_REG`, `BUSY`, and `RESPONSE` imply readback-oriented state; names such as `CTRL`, `CNTL`, `SELECT`, `CFG`, `ENABLE`, `DISABLE`, `CLEAR`, `FORCE`, `UCODE_ADDR`, and `UCODE_DATA` imply configuration or command paths. The authoritative semantics remain in the ASIC register database and hardware-facing call sites.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk is coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h` for bit fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` for reset/default values.
- SOC15 register access helpers and AMDGPU register macros that combine IP block, instance, base index, and offset.

Direct GC 10.3.0 include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes the offset, sh/mask, and default headers for GC 10.3.0 VM hub setup and register programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which includes GC 10.3.0 offsets and masks for SDMA register programming and performance/engine integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes GC 10.3.0 offsets and masks for KFD/GFX 10.3 queue and compute-facing integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the GC 10.3.0 offset and mask headers for Vangogh SMU power-management paths, including GFXOFF-related register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`, which includes the GC 10.3.0 sh/mask companion and interacts with SDMA/shared register fields.

Important runtime integration areas are firmware loading, PSP/SMU/RLC handshakes, GFXOFF and power-gating transitions, GPU reset and suspend/resume restore, performance monitoring, debugfs/perf diagnostics, VM hub setup, SDMA bring-up, and KFD compute queue enablement. Many registers in this chunk are also likely firmware-owned or PF-owned under some modes; caller code must respect the ownership model for the active ASIC, virtualization mode, and power state.

## Risks

- Generated-header drift is the primary risk. A wrong offset or base index can direct a read/write to the wrong GC register even when the field mask and caller logic are correct.
- Alias offsets must remain intentional. Removing or changing aliases such as `RLC_GPM_STAT`/`RLC_RLCS_GPM_STAT`, RTAVFS aliases, or CP hypervisor/non-hypervisor ucode aliases can break code that uses older or block-specific names for the same register.
- Performance counter blocks are highly repetitive. A single off-by-one offset in low/high result pairs, select/select1 pairs, or SDMA instance spacing can produce misleading telemetry rather than an obvious crash.
- RLC registers are sensitive because they sit in firmware loading, power-gating, clock-gating, interrupt, reset, and context-save/restore paths. Bad offsets can hang firmware bring-up, block GFXOFF, break WGP power management, lose interrupts, or make GPU reset unreliable.
- Clock-gating and power-control offsets can make later MMIO accesses unreliable if code writes the wrong control register or writes it at the wrong time in SMU/RLC sequencing.
- Registers with names such as `SOFT_RESET`, `CLEAR`, `FORCE`, `DISABLE`, `UCODE_DATA`, and `IRAM_DATA` can have destructive or command-like semantics. Treating them as ordinary read/write scratch registers in diagnostics can perturb hardware state.
- Split low/high registers require stable ordering in caller code. Reading counters or timestamps without latching/capture semantics may race hardware increments; writing address/data windows in the wrong order can corrupt indirect access state.
- The chunk starts and ends mid-file, including a CP MES continuation at the start and partial `gc_hypdec` at the end. Merge-time review should not mark missing earlier/later names as local omissions.
- The bare `base address: 0x3a000` marker without local registers is a generated artifact in this slice. A parser that assumes each base-address line has a local address-block name and registers can misclassify this boundary.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Compile or preprocess GC 10.3.0 AMDGPU, SDMA, SMU, and KFD paths that include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and `gc_10_3_0_default.h`.
- Static generation checks that every non-boundary register macro in this range has exactly one matching `_BASE_IDX` macro and that duplicate offsets are limited to known aliases.
- Cross-check this offset slice against the GC 10.3.0 register database and companion sh/mask/default headers for name alignment, base-index consistency, and expected address-block membership.
- Boot and reset GC 10.3.0-class hardware, including Vangogh-style SMU/GFXOFF paths, and verify RLC firmware load, safe-mode transitions, GFXOFF entry/exit, clock-gating enablement, and suspend/resume restore.
- Exercise SDMA0-3 and KFD compute paths on GC 10.3.0 hardware to confirm queue bring-up, interrupts, VM integration, and engine reset do not regress.
- Run performance-counter smoke tests across graphics, shader, cache, memory, GUS, GCVML2, and SDMA blocks: configure counters, sample low/high results, reset/reconfigure, and verify sane monotonic or event-correlated behavior.
- Exercise GPU reset, RLC/SMU mailbox or response paths, power-gating transitions, and debugfs/perf readbacks while checking for MMIO timeouts or stuck status bits.
- For virtualization/SR-IOV-like modes, verify PF/VF ownership boundaries around RLC, RLCS, CP hypervisor ucode, clock-gating, and power-management registers.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 7446-9968 of `gc_10_3_0_offset.h`. Earlier chunks should cover the start of the CP MES address block and prior GC offset regions. Later chunks should continue the `gc_hypdec` register list and the remainder of the GC 10.3.0 offset namespace. The final per-file report should describe the whole file as a generated MMIO offset map for GC 10.3.0 hardware, used by AMDGPU, KFD, SDMA, and SMU code, rather than as handwritten executable logic.
