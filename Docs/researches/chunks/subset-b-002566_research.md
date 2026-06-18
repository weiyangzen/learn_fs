# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h lines 4979-7470

## Scope

This chunk is a generated AMD GC 12.0.0 register-offset header segment. It contains preprocessor constants only: one `reg*` address macro and one matching `reg*_BASE_IDX` macro for each register. The requested range has 2,400 `#define` lines, representing 1,200 register offsets and 1,200 base-index constants.

The chunk begins mid-address-block. Lines 4979-5505 continue `gc_gfx_cpwd_cpwd_cprs64dec` from the previous chunk, covering the tail of CP MEC RS64 and graphics RS64 data-cache/aperture offsets. Lines 5506-7470 then cover complete CPWD channel, GL2, performance, power, RLC, IMU, GRBMH, PA, SQ, and early SPI/SX shader-engine address blocks. The range ends at `regSPI_LB_DATA_PERWGP_WAVE_HSGS_BASE_IDX`, before the remaining SPI low-bandwidth wave counters and later shader-engine registers that appear in the next chunk.

Although the source tree is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics-core metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_12_0_0_offset.h` gives AMDGPU, KFD, MES, IMU, gfxhub, and SOC24 code symbolic addresses for GC 12.0.0 hardware registers. Driver code passes these macros to `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, ring-packet emitters, golden-register tables, and dump/debug helpers. The paired `_BASE_IDX` macros select the register base aperture used by SOC15 addressing.

This chunk focuses on these hardware areas:

- CP RS64 firmware and scheduler registers for MEC and graphics pipes, including program counters, interrupt/pending/exception state, GP registers, local/instruction/scratch apertures, data-cache base/control/operation registers, and repeated data-cache aperture windows.
- CPWD channel and cache-side control registers: `CH`, `CHA`, `CHC`, `CHI`, `GL2A`, and `GL2C` control, steering, compression, credits, status, and disable/override registers.
- CP, CPF, CPG, CPC, GE, GE1, GE2, GC-EA, GCR, CHA, CHC, GL2A, GL2C, and GRBM performance counters and selector registers.
- GDFLL, XVMIN, GRTAVFS, and RTAVFS registers used around graphics voltage/frequency and adaptive-voltage/frequency monitor/control blocks.
- RLC and RLCS control/status/programming space, including safe mode, clear-state buffer addressing, microcode RAM access, timers, power-gating and clock-gating controls, SPM/perfmon registers, save/restore machine state, GPM general/semaphore registers, UTCL1/UTCL2 error/status registers, and IMU/RLC message registers.
- PF/VF-facing RLC interrupt and scheduler registers exposed through the `pfvfdec_rlc` address block.
- PWR, PSP, CH power, and GFX IMU register blocks for IMU firmware loading, IMU/RLC RAM access, C2P message access, reset status, bootloader addresses, and IRAM/DRAM data ports.
- Shader-engine register blocks for GRBMH, PA debug/rate/safe registers, SQ/SQC/SQG/SP/LDS debug and indirect access registers, SX debug-busy registers, and early SPI debug, CU-mask, lifetime, load-balance, GDS-credit, and active-wave counters.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable branches in this range. The public interface is the macro naming and address contract:

- `regNAME` expands to a register offset value, such as `regCP_MEC_RS64_CNTL`, `regRLC_SAFE_MODE`, `regGFX_IMU_I_RAM_DATA`, `regSQ_IND_INDEX`, or `regSPI_WGP_WORK_PENDING`.
- `regNAME_BASE_IDX` expands to the SOC15 base-index selector. In this chunk CPWD/RLC/IMU registers primarily use base index `1`; shader-engine blocks such as GRBMH, PA, SQ, SX, and SPI primarily use base index `0`.
- Matching field layouts live in `gc_12_0_0_sh_mask.h`. Consumers combine this offset header with shift/mask macros through `REG_SET_FIELD`, `REG_GET_FIELD`, and explicit masks such as `RLC_SAFE_MODE__CMD_MASK`.
- Consumers usually reach these constants through AMDGPU register helpers rather than raw MMIO arithmetic: `SOC15_REG_OFFSET(GC, inst, regX)`, `RREG32_SOC15(GC, inst, regX)`, `WREG32_SOC15(GC, inst, regX, value)`, `WREG32_SOC15_NO_KIQ`, and ring-based write-register packets.

Important register families in this chunk include:

- `CP_MEC_*`: MEC RS64 program counter, trap/interrupt registers, MIE/MIP timer registers, GP registers, local/instruction/scratch apertures, data-cache control, and repeated `CP_MEC_DC_APERTURE0..15_{BASE,MASK,CNTL}` entries.
- `CP_GFX_RS64_*`: graphics RS64 data-cache apertures for data cache instances 0 and 1, plus exception/interrupt entries that support PFP/ME RS64 firmware data cache setup.
- `CH*`, `GL2*`, `GC_EA_*`, `GCR_*`: channel/cache/memory-fabric control, pipe steering, SDP credits/reserves/priority/enable, and performance counters.
- `RLC_*` and `RLC_RLCS_*`: the largest family in this chunk, covering core RLC enable/status, microcode data ports, SPM and perfmon, clear-state, save/restore, power and clock gating, CGCG/CGLS, SRM, GPM, UTCL error reporting, semaphore, IMU mailbox/telemetry, SDMA interrupt bridge, memory power control, and RLCS end/status registers.
- `GFX_IMU_*`: IMU C2P message access, scratch, core/reset control, RLC RAM index/address/data, bootloader address/size, and IMU IRAM/DRAM address/data ports.
- `GRBMH_*`, `PA_*`, `SQ*`, `SX_*`, `SPI_*`: shader-engine and shader-processor control/debug/status offsets, including SQ indirect read/write, watchpoint address/control registers, CU masks, WGP/work-pending status, load-balance data, and active-wave counters.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. The active SOC/IP path includes `gc_12_0_0_offset.h` and the matching `gc_12_0_0_sh_mask.h`.
2. Code selects the GC instance or XCC/pipe/queue context through SOC24/GRBM selection helpers where required.
3. A register offset macro from this file and a field macro from the shift/mask header are combined to build an MMIO address or register value.
4. The driver writes or reads the register via SOC15 helpers, indirect SQ access, RLC-safe paths, KIQ/ring packets, or firmware loader loops.
5. Hardware side effects, waits, resets, cache invalidations, and firmware handshakes are implemented in the consumer code, not in this generated file.

Concrete examples from nearby consumers:

- `gfx_v12_0.c` programs MEC RS64 start addresses with `regCP_MEC_RS64_PRGRM_CNTR_START` and `_HI`, resets MEC pipes through `regCP_MEC_RS64_CNTL`, and checks `regCP_MEC_RS64_INSTR_PNTR` during compute pipe reset.
- `gfx_v12_0.c` programs PFP/ME/MEC firmware data-cache bases through `regCP_GFX_RS64_DC_BASE0_LO/HI`, `regCP_GFX_RS64_DC_BASE1_LO/HI`, `regCP_MEC_MDBASE_LO/HI`, `regCP_MEC_DC_BASE_CNTL`, and `regCP_MEC_DC_OP_CNTL`, with explicit invalidate-complete polling in the shift/mask fields.
- RLC initialization writes clear-state buffer addresses through `regRLC_CSIB_ADDR_HI`, `regRLC_CSIB_ADDR_LO`, and `regRLC_CSIB_LENGTH`; starts/stops RLC through `regRLC_CNTL`; toggles SMU handshake and clock-gating state through `regRLC_PG_CNTL`, `regRLC_CGTT_MGCG_OVERRIDE`, and `regRLC_CGCG_CGLS_CTRL`; and enters/exits safe mode with `regRLC_SAFE_MODE`.
- RLC firmware loading uses `regRLC_GPM_UCODE_ADDR/DATA`, `regRLC_LX6_IRAM_ADDR/DATA`, and `regRLC_LX6_DRAM_ADDR/DATA`.
- IMU loading and setup in `imu_v12_0.c` uses `regGFX_IMU_I_RAM_ADDR/DATA`, `regGFX_IMU_D_RAM_ADDR/DATA`, `regGFX_IMU_C2PMSG_ACCESS_CTRL0/1`, `regGFX_IMU_C2PMSG_16`, `regGFX_IMU_SCRATCH_10`, `regGFX_IMU_CORE_CTRL`, and `regGFX_IMU_GFX_RESET_CTRL`.
- SQ debug and KFD/debug paths use SQ indirect or command registers such as `regSQ_IND_INDEX`, `regSQ_IND_DATA`, and `regSQ_CMD`.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state whose lifetime is owned by the GPU and driver programming sequence:

- CP MEC and graphics RS64 state persists in command-processor registers and firmware data-cache aperture registers until reset, reprogrammed, context-switched, or lost across GPU reset/power events. Program-counter, trap, timer, interrupt, and GP registers may be firmware-owned while the CP is running.
- CP data-cache aperture registers define firmware-visible memory windows. Wrong base/mask/control offsets can redirect firmware loads/stores, break instruction/data cache invalidation, or expose the wrong memory region to a CP micro-engine.
- Performance counter registers are sampled or latched hardware state. Counter low/high pairs and selector registers must be programmed/read in valid order by perfmon/SPM code.
- RLC state persists across many low-power and context-save operations. Safe mode, clear-state buffer addresses, SRM enable, clock/power gating controls, SPM buffers, GPM data, semaphores, and UTCL error/status registers are mutable hardware state. Some registers are firmware ports where repeated writes stream microcode or RAM contents.
- IMU IRAM/DRAM and RLC RAM ports act as indexed firmware-memory accessors. Address/data register ordering matters, and version stamps written back to address registers are used by the driver as part of the load sequence.
- Shader-engine status/debug registers are per-SH/SE or indexed through shader-array selection. SQ watch registers and SPI CU masks are persistent debug or dispatch-affinity state until reprogrammed.

This header does not encode read-only, write-only, write-one-to-clear, latch, poll, or side-effect semantics. Those behaviors must come from the hardware programming guide, the matching shift/mask header, firmware contracts, and the surrounding AMDGPU code.

## Dependencies And Integration Points

The immediate dependency is `gc_12_0_0_sh_mask.h`, which provides the field definitions used with these offsets. The offset values also depend on AMD's generated GC 12.0.0 register database and must stay synchronized with other GC 12.0.0 generated headers, defaults, firmware interfaces, and SOC24 IP discovery data.

Observed integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c`, the main GFX 12 implementation. It consumes many registers from this chunk for CP firmware loading, MEC compute enable/reset, RLC startup, RLC safe mode, clock/power gating, clear-state buffer programming, SQ indirect reads, interrupt registers, pipe reset diagnostics, and golden settings.
- `drivers/gpu/drm/amd/amdgpu/mes_v12_0.c`, which includes this header for MES queue scheduler interaction and register access.
- `drivers/gpu/drm/amd/amdgpu/imu_v12_0.c`, which uses the GFX IMU and several golden-register offsets in this range.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.c`, `sdma_v7_0.c`, and `soc24.c`, which include the same generated GC 12.0.0 register headers for hub setup, SDMA/SOC-level integration, and register initialization.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12.c`, `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c`, and `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c`, which rely on the same GC 12.0.0 register definitions for KFD compute queues, MQDs, and scheduler/debug behavior.
- Firmware blobs and firmware headers for MEC, PFP, ME, RLC, MES, and IMU, whose load/start/status sequences depend on these register addresses matching the hardware.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong offset or base index compiles cleanly but sends MMIO to the wrong register or aperture.
- This chunk starts and ends inside larger generated structures. The previous chunk owns the beginning of `gc_gfx_cpwd_cpwd_cprs64dec`, including early CP MEC RS64 definitions; the next chunk completes the SPI family. File-level research should merge those artificial boundaries before making complete claims about the whole address block.
- `_BASE_IDX` mistakes are as damaging as bad offsets. Most CPWD/RLC/IMU registers in this chunk use base index `1`, while shader-engine blocks use base index `0`; mixing them can address the wrong MMIO base even when the numeric offset is correct.
- CP RS64 data-cache and firmware-start registers are boot-critical. Bad `CP_MEC_*` or `CP_GFX_RS64_*` offsets can cause firmware load failure, cache invalidation timeouts, stuck MEC/PFP/ME pipes, bad ring tests, or unrecoverable GPU resets.
- Repeated data-cache aperture and performance-counter families are copy-sensitive. A single off-by-one in `APERTURE0..15` or counter low/high/select pairs may only fail under a specific pipe, aperture, or counter slot.
- RLC safe mode, SRM, SPM, and power/clock-gating registers have strict ordering and side effects. Wrong offsets can leave RLC enabled when it should be quiesced, make safe-mode polling time out, corrupt clear-state restore, or break GFXOFF/SMU handshake behavior.
- Firmware-memory data ports such as `RLC_*_UCODE_DATA`, `RLC_LX6_*_DATA`, and `GFX_IMU_*_RAM_DATA` are sequential access points. Misaddressing the data or address register can silently load corrupt microcode.
- PF/VF and SR-IOV-sensitive registers such as the RLC PF/VF block and KIQ/no-KIQ paths can behave differently in virtualized environments. A register that works on bare metal may be trapped, virtualized, or inaccessible in a VF.
- SQ/SPI/PA debug and watch registers may be per-SE/per-SH, selected by GRBM/SRBM state, or indirect. Wrong offsets or missing selection can produce misleading dumps rather than immediate failures.
- Performance and power registers often produce subtle regressions. Errors in GDFLL/GRTAVFS/RTAVFS, clock-gating, CU-mask, or SPI lifetime/load-balance registers may show up as clocks, residency, dispatch fairness, or perf-counter anomalies rather than a hard fault.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and runtime hardware tests:

- Build AMDGPU with GFX 12, SOC24, MES, KFD, IMU, SDMA, and gfxhub support enabled. Missing or renamed macros should surface in the include users listed above.
- Mechanically compare lines 4979-7470 against AMD's authoritative GC 12.0.0 register database. Check that each non-`BASE_IDX` register has exactly one matching `_BASE_IDX`, and that the base index matches the address block's expected aperture.
- Run structural checks for repeated families: `CP_MEC_DC_APERTURE0..15`, `CP_GFX_RS64_DC_APERTURE0..15` for both cache instances, perfcounter low/high/select pairs, `RLC_SPM_*`, `RLC_SRM_INDEX_CNTL_ADDR/DATA_0..7`, `RLC_SEMAPHORE_0..3`, `SQ_WATCH0..3`, and `SPI_CONFIG_CU_MASK_*`.
- Boot on GC 12.0.0 hardware and watch for successful RLC, MEC, PFP, ME, MES, and IMU firmware load messages. Failure signals include RLC autoload timeout, instruction/data cache invalidation timeout, IMU start timeout, and failed ring tests.
- Exercise graphics and compute ring initialization, queue submission, preemption/reset, and recovery. Relevant signals are stuck CP/MEC pipe resets, nonzero CP/MEC instruction-pointer deltas after reset, KIQ readiness failures, and MES legacy queue reset fallback.
- Exercise RLC safe-mode entry/exit, clear-state buffer programming, GFXOFF/power-gating transitions, clock-gating toggles, SPM perfmon, and SRM save/restore. Watch for safe-mode polling timeouts, bad clear-state restore, SPM VMID programming failures, or GFXOFF residency regressions.
- Validate IMU firmware loading and IMU-driven power-up paths. Check C2P access control, IMU reset-status polling, IRAM/DRAM loading, and any APU-specific `amdgpu_dpm_set_gfx_power_up_by_imu` behavior.
- Run SQ/SPI debug tests: SQ indirect register reads, shader debugger/watchpoint use, SPI CU mask and WGP work-pending status reads, and active-wave/lifetime counter collection.
- Run performance-counter and profiling workloads using CP, CPF/CPC/CPG, GE, GC-EA, GCR, CHA/CHC, GL2A/GL2C, GRBM, RLC, SQ, SX, and SPI counters. Expected signals are stable counter reads, sane low/high composition, and no selector aliasing.
- Run SR-IOV VF and bare-metal coverage where available, especially around no-KIQ RLC SPM access, RLC PF/VF interrupt/status registers, MES queue management, and trapped register writes.

## Cross-Chunk Notes

The previous chunk contains the start of `gc_gfx_cpwd_cpwd_cprs64dec`; this chunk starts at `regCP_MEC_GP1_LO_BASE_IDX` after `regCP_MEC_GP1_LO` was defined on the prior line. The next chunk begins immediately after `regSPI_LB_DATA_PERWGP_WAVE_HSGS_BASE_IDX` and should complete the SPI low-bandwidth per-WGP wave counters and remaining shader-engine register offsets. The final per-file document should reconcile these chunk boundaries before describing complete CP RS64 or SPI register families.
