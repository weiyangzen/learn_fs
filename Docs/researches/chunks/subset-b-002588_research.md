# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 4939-7413

## Scope

This chunk is a generated AMD GC 12.1.0 register-offset header segment. It contains C preprocessor constants only: each hardware register has a `reg...` macro containing the register offset and a matching `reg..._BASE_IDX` macro selecting the register base aperture. There are no functions, structs, enums, includes, variables, locks, allocations, callbacks, or executable branches in this range.

The selected range begins inside a command-processor RS64 address family, immediately after `regCP_CPC_IC_OP_CNTL_BASE_IDX`, and then covers multiple address blocks:

- CP graphics RS64 interrupt, local data/instruction/scratch apertures, general-purpose registers, instruction pointers, pending interrupts, and 16 data-cache aperture slots for each of two aperture banks.
- CH and GLARB arbitration/control blocks for graphics fabric request steering and credit/status tracking.
- CP/GRBM/GE/CH/GLARB/RLC/GCR/CHA performance counter data registers and matching select/control registers, including RLC streaming performance monitor (SPM) setup.
- XVMIN write-data access.
- RLC hypervisor, CP hypervisor, GRBM hypervisor, RLC core, RLCS, PF/VF RLC, power, PSP/security, CP PSP debug/data-mover, CH power, GFX IMU, GFX IMU PSP, GRBMH, and the first PA/GE/CC registers in the next address block.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_12_1_0_offset.h` gives AMDGPU code symbolic names for GC 12.1.0 register offsets. Callers combine these offsets with base-index metadata, generated field definitions from the matching shift/mask header, and AMDGPU MMIO, indirect-register, PM4, firmware, debug, or reset helpers. The result is that ASIC-specific code can address hardware registers without embedding raw offsets throughout driver logic.

This chunk maps mostly control-plane registers rather than render-state registers. Its main purpose is to expose the register addresses used to initialize, monitor, virtualize, debug, and power-manage the GC command, RLC, arbitration, performance, and IMU subsystems.

Notable functional areas are:

- CP RS64 graphics microcontroller state: interrupt enables, exception status, local base/mask/aperture registers, local instruction and scratch regions, performance-count control, machine interrupt/time compare style registers, general-purpose registers, instruction pointers, pending interrupt state, and data-cache aperture base/mask/control tuples.
- CH/GLARB arbitration and fabric configuration: arbitration controls, DRAM burst masks/controls, status, client credits, free-delay controls, FGCG/MGCG overrides, hash configuration, pipe steering, AID selection, and memory-disable user controls.
- Performance monitoring: low/high counter readout registers, select registers, latency-stat select/data registers, draw-object/window counters, GRBM/GE/RLC/GCR/CHA/CHC/GLARB counter families, and RLC SPM ring, mux, accumulation, pause/status, timestamp, and RSPM request/response registers.
- RLC virtualization and hypervisor control: VF enable/mask/status, SDMA status and busy state, VM busy state, scheduling block and active function ID, doorbell status set/clear, semaphores, virtual reset request, SMU/RLC response registers, VFI command/status/address/data windows, and PF/VF-facing RLC safe-mode and interrupt registers.
- CP hypervisor and firmware memory windows: PFP/ME/MEC microcode address/data/checksum/version registers, instruction-cache base/control registers, MES/MEC/GFX RS64 instruction/data base and bound aliases, and context-range limits.
- RLC core and RLCS control: RLC control/status, firmware versions, active masks, clock/timestamp counters, GPM timer and interrupt registers, RAS/MCA interrupt control, power-gating and clock-gating controls, GPM/SRM/SRS/SRM state, SPP private state, residency counters, IH client status, LX6/XT core state, doorbell monitors, SMU message/argument registers, and IMU bootload handoff registers.
- RLCS service block: decode start/end, exception dump registers, fence, CG/DS controls, power-gating status, bootload status, general-purpose registers, KMD logging controls, GCR data/status, RLC-IMU mailbox and RAM access, SDMA interrupt status, FED/security status, and UTCL2/SE snapshots.
- PSP/security access: GC_EA CPWD security-level and SDP error registers, GRBM source-ID and CAM programming, IOV range enables, security control, firewall violation address capture, UTC bypass control, and CP/MES/MEC/GFX RS64 indexed data-mover debug windows.
- GFX IMU control and firmware interface: C2P message mailboxes 0-47, access controls, MP1/RLC/SOC mailboxes, mutexes, VF control, scratch registers, GTS offset and firmware timestamp registers, interrupt controller and IH controls, fuse/clock/doorbell/DPM controls, RLC RAM windows, fence logging, core power/reset/isolation controls, timers, data/instruction RAM access, bootloader address/size, and gasket control.
- GRBMH and PA tail registers: high-level GRBMH control/status/soft-reset/read-error/clocking/sync registers and the start of the PA block containing GE rate controls, shader-array configuration, and SE control/status.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `reg<NAME>` expands to the GC 12.1.0 register offset used by AMDGPU register access paths.
- `reg<NAME>_BASE_IDX` expands to the base-index selector for that register. In this slice, CPWD/RLC/IMU/PSP style blocks mostly use base index `1`, while GRBMH and PA/GE tail registers use base index `0`.
- Field-level shift and mask constants live in the companion `gc_12_1_0_sh_mask.h` header, not in this offset header.
- Default/reset values, when generated for this ASIC family, are expected in matching default headers.

The chunk contains about 1200 register-offset macros, excluding the paired `_BASE_IDX` definitions. Large repeated or alias-prone families include:

- `regCP_GFX_RS64_*`: RS64 graphics-side local memories, interrupts, performance controls, GP registers, instruction pointers, pending interrupts, and data-cache aperture tables.
- `regCH*`, `regCHA*`, `regCHC*`, `regCHI*`, `regGLARB*`, `regGLARBA*`, `regGLARBC*`, `regGLARBI*`: arbitration, credit, clock-gating override, hash, pipe-steering, and fabric-local power/memory controls.
- `reg*_PERFCOUNTER*_LO/HI`, `reg*_PERFCOUNTER*_SELECT*`, `reg*_LATENCY_STATS_*`, `regRLC_SPM_*`: performance data, counter muxing, streaming monitor ring/segment/mux/accumulator controls, and SPM status.
- `regRLC_GPU_IOV_*`, `regRLC_VFI_*`, `regRLC_RLCS_IOV_*`: GPU IOV and virtualization state, command/status windows, scheduling, VF masks, and SDMA/VM busy indicators.
- `regCP_HYP_*` plus legacy aliases such as `regCP_PFP_UCODE_ADDR`, `regCP_ME_RAM_RADDR`, `regCP_ME_RAM_WADDR`, and `regCP_ME_RAM_DATA`: CP firmware and RAM windows exposed under both hypervisor and non-hypervisor names.
- `regRLC_*`: the largest family in the chunk, covering RLC core control, GPM/SRM/SRS/SPP state, clock/power gating, RAS/MCA, residency counters, doorbells, SMU messages, IMU bootload, and low-level firmware status.
- `regRLC_RLCS_*`: RLCS decode/service, bootload, logging, mailbox, RAM, power, interrupt, FED, and snapshot registers.
- `regGFX_IMU_*`: IMU mailboxes, scratch, timers, interrupts, bootloader, core control/status, power/reset/isolation, RLC RAM, and D/I-RAM access.
- `regGRBM*` and `regGRBMH*`: GRBM hypervisor indexed state, source-ID/security CAMs, remap controls, and GRBMH control/status/reset.
- `regGE_*` and `regCC_GC_SHADER_ARRAY_CONFIG`: early graphics-engine and shader-array configuration offsets at the end of the chunk.

Some offsets intentionally have multiple symbolic names. For example, `0x5814` is both `regCP_HYP_PFP_UCODE_ADDR` and `regCP_PFP_UCODE_ADDR`; `0x5816` is shared by `regCP_HYP_ME_UCODE_ADDR`, `regCP_ME_RAM_RADDR`, and `regCP_ME_RAM_WADDR`; `0x5850/0x5851` are both MES instruction-cache base names and `MIBASE` aliases; `0x5870/0x5871` are both MEC data-cache base names and `MDBASE` aliases; and `0x4e6c` is both `regRLC_GPM_STAT` and `regRLC_RLCS_GPM_STAT`. These aliases are part of the generated register database and can reflect different programming-model names for the same hardware offset.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied AMDGPU flow is:

1. ASIC discovery selects GC 12.1.0 register headers for the device.
2. A driver path chooses a symbolic register, its `_BASE_IDX`, and usually a companion field mask/shift from `gc_12_1_0_sh_mask.h`.
3. The offset is passed to an MMIO accessor, indirect indexed register helper, firmware programming sequence, PM4 packet builder, debug dump path, or register save/restore table.
4. Hardware state changes, status is sampled, or a diagnostic/control operation is triggered according to the target block's protocol.

Important implied sequences include:

- RS64 CP setup programs local base/mask/aperture registers, data/instruction bounds, scratch windows, interrupt enable/status registers, and instruction-cache/data-cache controls before or during microcontroller execution.
- Performance setup first programs select/mux/window registers, then starts or enables counters through performance-monitor controls, then reads low/high counter registers or RLC SPM output rings and accumulation memories.
- RLC and RLCS firmware flows use address/data register pairs for microcode, RAM, scratch, command, and mailbox windows; status and fence registers are polled by driver or firmware sequencing outside this header.
- GPU IOV and PF/VF flows use VF masks, scheduling registers, active function IDs, virtual reset requests, doorbell status set/clear registers, and VFI command/status windows to coordinate virtualization state.
- Power and clock management flows use RLC, CGTT, ICG, GRBM, GFX IMU, and residency-counter registers to gate clocks, request power transitions, measure residency, and coordinate with SMU/MP1.
- PSP/security flows use GRBM CAM/source-ID and security/firewall registers to configure allowed access ranges and capture violation addresses.
- IMU boot and communication flows use bootloader address/size registers, D/I-RAM access, C2P mailboxes, RLC/IMU mutex and mailbox registers, timers, interrupt controller controls, and reset/isolation controls.

The header does not define ordering constraints, polling conditions, delays, locking, register side effects, or firmware ownership. Those are supplied by AMDGPU code, platform firmware, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They name hardware registers whose contents are volatile GPU state.

CP RS64 and CP hypervisor registers represent firmware-visible command-processor state. Local base/mask/aperture, instruction/data bounds, scratch, cache base/control, and microcode window registers persist only as programmed hardware state and may be reset, reloaded, or saved/restored during GPU reset, suspend/resume, virtualization transitions, or firmware reload.

Performance counter registers are live measurement state. Select registers and monitor controls configure what is counted, low/high readout registers expose running or latched counters, and SPM ring/mux/accumulator registers persist sampling configuration and buffer pointers. Counter values, write pointers, status bits, and accumulation RAM contents can change while engines are active.

RLC/RLCS state is firmware-owned control state. It includes power-gating, clock-gating, GPM/SRM/SRS/SPP, interrupt, doorbell, SMU message, GCR, IMU mailbox, bootload, and residency state. Some registers are commands or acknowledgments with side effects; others are volatile status, counters, or firmware scratch/general-purpose storage.

GPU IOV and security registers persist virtualization and access-control state for PF/VF operation. VF enables, masks, scheduling state, active function IDs, doorbell status, security CAMs, IOV ranges, and firewall violation capture registers can affect isolation boundaries and may need strict restore semantics after reset or FLR.

GFX IMU registers hold mailbox, scratch, firmware timestamp, timer, interrupt, DPM, fence, RAM, bootloader, power, reset, and isolation state. Several are producer/consumer communication surfaces between driver, RLC, IMU firmware, SOC/MP1, and PSP. Treat them as firmware-owned unless the surrounding sequence documents direct host writes.

CH/GLARB/GRBMH/PA tail registers hold fabric arbitration, pipe steering, clocking, reset, status, and shader-array/GE configuration. Misprogramming can persist until reset and affect routing, performance, or visibility of graphics shader arrays and SE state.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register set remaining internally consistent:

- `gc_12_1_0_sh_mask.h` supplies field positions and masks for many registers named here.
- Other generated GC 12.1.0 headers may provide defaults, enumeration-like values, and additional address regions outside this chunk.
- AMDGPU register helpers, MMIO accessors, indirect register helpers, PM4 packet emitters, debugfs/register-dump code, firmware load code, reset code, power-management code, virtualization code, and RAS/error paths consume these offsets.

Key integration points include:

- GFX/CP firmware setup for PFP, ME, MEC, MES, and GFX RS64 microcode/RAM windows.
- Command submission and scheduling paths that depend on CP interrupt status, pending interrupt state, local memory windows, and scheduler-related RLC/IOV registers.
- RLC firmware loading, boot sequencing, safe mode, power-gating, clock-gating, SPM, thread trace, SPP, SMU messaging, and IMU bootload handoff.
- SR-IOV/PF/VF management paths that inspect or update VF enable/mask, VM/SDMA busy status, active function ID, scheduling block, virtual reset, VFI access, and doorbell state.
- PSP/security paths that configure GRBM source-ID/CAM/IOV ranges, SDP security maps, and firewall violation capture.
- Profiling and diagnostics paths that configure CP/GRBM/GE/CH/GLARB/RLC/GCR/CHA counters and RLC SPM buffers/muxes.
- Power-management paths that interact with CGTT, ICG, RLC residency counters, SMU command/argument registers, GFX IMU DPM controls, and power/reset/isolation controls.
- Interrupt handling paths through RLC IH cookies/status, RLC GFX IH client state, GFX IMU PIC/IH controls, and GRBMH status/read-error registers.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong offset or base index compiles cleanly but can direct an MMIO write to the wrong hardware register.
- This chunk starts and ends mid-file and mid-family. It begins after a prior CP CPC instruction-cache macro and ends in the first PA block, so adjacent chunks are needed for complete file-level conclusions.
- Alias registers can confuse audits. Shared offsets such as CP microcode/RAM names, MES/MEC base aliases, and `regRLC_GPM_STAT`/`regRLC_RLCS_GPM_STAT` must be validated as intentional aliases, not duplicate-generation errors.
- Base-index mismatches matter. Most CPWD/RLC/IMU/PSP registers here use base index `1`, while GRBMH/PA registers use base index `0`; using the wrong base aperture could target a different register space.
- Address/data window registers require sequencing. Microcode RAM, IMU RAM, SRM/SRS/SPM indirect RAM, SERDES, SOC, VFI, and CAM access patterns usually require write-address then read/write-data ordering, busy polling, or firmware arbitration that this header cannot express.
- Command, reset, safe-mode, interrupt-force/clear, doorbell, virtual-reset, fence, power-gating, clock-gating, and SMU-message registers can have side effects. Treating them as passive configuration or dump-only state can disrupt firmware or active queues.
- Performance counters and SPM state are volatile. Low/high counter reads can tear if the caller does not follow the hardware read protocol; SPM ring base/size/write-pointer state can corrupt profiling output if programmed while running.
- Virtualization and security registers are isolation-sensitive. Incorrect VF masks, active function IDs, IOV ranges, source-ID CAM data, or firewall controls can leak access across PF/VF boundaries or block required firmware/driver access.
- Power and clock controls interact with firmware ownership. Direct writes to CGTT/ICG/RLC/IMU power registers outside coordinated sequences can hang graphics, break residency accounting, or race SMU/MP1.
- IMU/RLC mailbox registers are concurrency-sensitive. Mutex, status, command, and scratch/mailbox registers may require strict producer/consumer handshakes between host, RLC, IMU, PSP, and SOC firmware.
- Repeated families are easy to validate incompletely: 48 IMU C2P messages, 16 IMU scratch registers, multiple SPM mux/data windows, multiple performance-counter banks, and SDMA0-7 IOV status registers need index-by-index checks.

## Test Signals

Useful validation is mostly generated-data consistency plus targeted AMDGPU build/runtime coverage:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_offset.h`, especially GC 12.1.0 CP, RLC, firmware, power, virtualization, performance, debug, reset, and interrupt paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database for every `reg...` offset and `reg..._BASE_IDX` in lines 4939-7413.
- Static checks that every non-alias offset has the expected paired `_BASE_IDX`, aliases are intentional, and repeated families remain monotonic and correctly spaced.
- Cross-checks that registers named in this chunk have matching shift/mask definitions where fields are expected, and defaults where generated.
- Firmware load and reset tests covering PFP/ME/MEC/MES/GFX RS64 microcode windows, RLC boot, IMU bootloader address/size, RLC safe mode, and reset recovery.
- SR-IOV or virtualization tests covering VF enable/mask, active function ID, VM/SDMA busy status, virtual reset, VFI command/status, PF/VF doorbells, and security/IOV range behavior.
- Profiling tests covering CP/GRBM/GE/CH/GLARB/RLC/GCR/CHA counters, latency stats, RLC SPM ring setup, mux programming, pause/status handling, and low/high counter consistency.
- Power-management tests covering RLC power/clock gating, CGTT/ICG controls, SMU command/message paths, residency counters, IMU DPM controls, and suspend/resume restore.
- Interrupt/debug tests covering RLC IH cookies, GFX IH client status, IMU PIC/IH state, GRBMH read-error/status, CP pending interrupts, and firmware mailbox status.
- Security diagnostics covering GRBM source-ID/CAM programming, SDP security maps, firewall first-violation address capture, and PSP/CP indexed debug windows.

Runtime warning signals include GPU hangs during firmware boot or reset, failed RLC/IMU mailbox handshakes, bad SPM samples, impossible counter values, broken VF isolation, unexpected firewall violations, missing or stuck interrupts, power-gating or clock-gating stalls, GRBMH read errors, and register dumps showing inconsistent base-index interpretation.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002588`. It covers lines 4939-7413 of `gc_12_1_0_offset.h`. The final per-file research should merge this with adjacent chunks to complete the surrounding CP RS64/CPWD register families before line 4939 and the PA/graphics-state address blocks after line 7413.
