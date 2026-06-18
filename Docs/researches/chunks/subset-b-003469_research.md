# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_5_sh_mask.h lines 4739-7304

## Scope

This chunk is a generated register field definition slice for AMD VCN 4.0.5. It does not implement executable code. Instead, it exposes preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK` so VCN/JPEG driver code can compose and decode 32-bit MMIO register values without embedding raw bit positions. The slice starts in the late LMI register area, covers JPEG decode/JPEG ring-buffer/JPEG memory-interface blocks, JPEG common interrupt and clock-gating blocks, VCN/UVD power-gating and debug/reporting blocks, VCN ring-buffer doorbell controls, UMSCH scheduler controls, and the beginning of the CPRS64/MES register block.

The companion address header for this generation is `vcn_4_0_5_offset.h`; consumers combine `reg...` offsets from that file with these mask/shift constants and access the hardware through AMDGPU MMIO helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and JPEG DPG-mode write helpers.

## Purpose

The chunk provides the hardware contract for programming and observing VCN 4.0.5 video/JPEG engines. Its constants cover:

- LMI byte-swap, VMID, memory-credit, indirect access, prefetch, and reference-surface BAR fields.
- JPEG decode controls: request enable, error reset, ring-buffer base/read/write pointers, ring size, picture dimensions, chroma/output format, timeout, interrupt enable/status, tier/component/sampling/quantization setup, output buffer pointers, pitch, tiling, address mode, command/data windows, and scratch storage.
- JPEG ring-buffer controller controls: write/read pointers, ring enable, indirect-buffer size, urgent control, conditional-read timers, status, buffer status, preemption command and fence fields, and scratch storage.
- JMI/LMI memory-interface controls for JPEG decode, encode, EJRBC, scalar, JPEG2, atomic writes, preemption fences, 64-bit BAR low/high pairs, VMID routing, swap mode, memory clamping, drop controls, latency/performance counters, clean-status reporting, and RAS error controls.
- JPEG common block controls for soft reset, system interrupts, memcheck interrupts, interrupt handler routing, master interrupt overrun state, arbitration drop controls, clock-gating gate/control/status, memory low-power modes, and performance-bank counters.
- VCN/UVD power-management and debug controls: PGFSM config/status, power status, JPEG power status, DPG local-memory access, DPG pause handshakes, scratch registers, free counter, VCPU cache BAR/VMID, register filtering, PF status, VCPU error address/range/error reporting, address configuration, general-purpose counters, deep-sleep controls, timestamp counter, feature capabilities, GPU IOV status, version, doorbell controls, and ring-pointer controls.
- UMSCH and MES controls: scheduler reset/busy state, AGDB write pointers, mailbox and response registers, UTCL1 controls, interrupt enable/status/ack/source, interrupt handler metadata, force-GPUVM controls, MES program/intr vector registers, pipe priority controls, interrupt/scratch/instruction-pointer state, RISC-like machine status/cause/address/counter/ID registers, cache operation controls, data-cache base/invalidate controls, timer compare, general-purpose state registers, data-memory index access, and local instruction/data aperture base/mask registers.

## Important APIs, Types, And Macros

There are no C types or callable functions in this chunk. The exported API is the macro namespace itself.

Key macro groups:

- `UVD_LMI_*`: local-memory interface fields for byte swapping, VMIDs, credits, prefetching, and 64-bit BAR pieces. These constants are used wherever the VCN block needs to bind GPU virtual memory contexts and memory apertures for firmware, ring, indirect-buffer, or surface traffic.
- `UVD_JPEG_*` and `JPEG_DEC_*`: JPEG decode engine fields. `UVD_JPEG_CNTL__REQUEST_EN_MASK` and `UVD_JPEG_CNTL__ERR_RST_EN_MASK` gate job requests and error reset. Ring pointer and size masks encode 16-byte-aligned values. SPS/tier/output fields describe decoded image geometry, chroma configuration, sampling factors, output pitches, tiling, and command windows.
- `UVD_JRBC_*`: JPEG ring-buffer controller fields. These cover RB/IB state, soft reset, ready/idle/busy status bits, urgent handling, conditional-read timers, preemption command bits (`PREEMPT`, `NO_FENCE`, `PREEMPT_ACK`, `PREEMPT_ON_FENCE`), and fence data.
- `UVD_JMI_*`, `UVD_LMI_J*`, `JPEG_MEMCHECK_*`, and `JPEG_LMI_DROP`: JPEG memory-interface fields. The low/high 64-bit BAR pairs map read/write/preemption/ring/IB/atomic/scalar/JPEG2/fence targets; VMID fields bind those accesses to GPUVM address spaces. Memcheck and clamping masks define bounds-enforcement and error-reporting surfaces.
- `JPEG_SYS_INT_*`, `JPEG_MEMCHECK_SYS_INT_*`, `JPEG_MASTINT_EN`, and `JPEG_IH_CTRL`: interrupt enable/status/ack routing for normal JPEG events and memory check violations. `JPEG_IH_CTRL` provides IH reset/stall/status-clean bits plus VMID, user-data, and ring-id fields sent to the interrupt handler.
- `JPEG_CGC_*` and `JPEG_*_CGC_MEM_CTRL`: clock-gating and memory low-power controls. `jpeg_v4_0_5.c` uses `JPEG_CGC_CTRL__DYN_CLOCK_MODE__SHIFT`, `JPEG_CGC_CTRL__JPEG_DEC_MODE_MASK`, `JPEG_CGC_GATE__JPEG_DEC_MASK`, `JPEG_CGC_GATE__JPEG2_DEC_MASK`, `JPEG_CGC_GATE__JMCIF_MASK`, and `JPEG_CGC_GATE__JRBBM_MASK` to enable and disable JPEG clock gating.
- `UVD_PGFSM_*`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_DPG_*`, and `UVD_IPX_*`-adjacent fields in this range: power-gating, dynamic power-gating, local-memory-access, pause, and power-state observation fields. `vcn_v4_0_5.c` uses `UVD_PGFSM_CONFIG__UVDM_UVDU_PWR_ON` from common VCN declarations together with `UVD_POWER_STATUS__UVD_PG_EN_MASK` and the power-status register.
- `VCN_RB*_DB_CTRL`, `VCN_AGDB_*`, `VCN_RB_ENABLE`, and `VCN_RB_WPTR_CTRL`: doorbell and ring-buffer enable/write-pointer control fields for main VCN rings, JPEG rings, multiple additional RBs, UMSCH, EJPEG, and audio.
- `VCN_UMSCH_*`, `UMSCH_*`, and `UVD_UMSCH_FORCE`: unified micro-scheduler controls for MES pipe selection, reset/busy observation, mailbox communication, AGDB ring write pointers, interrupts, IH context metadata, UTCL1 behavior, and forced GPUVM modes.
- `VCN_MES_*`: MES micro-engine fields, including program-counter/vector start addresses, reset/enable/step/halt/interrupt controls, pipe priority selection, machine interrupt/status/cause/address registers, instruction/data cache operations, timers/counters, general-purpose firmware state, data-memory indexed access, and local aperture configuration.

## Control Flow

This header chunk contains no direct control flow. Runtime control flow is created by driver code that reads a register, masks or shifts selected fields, and writes the updated value back to hardware. Common patterns are:

- Read-modify-write gate control: `jpeg_v4_0_5_disable_clock_gating()` and `jpeg_v4_0_5_enable_clock_gating()` read `regJPEG_CGC_CTRL` and `regJPEG_CGC_GATE`, then set or clear the JPEG/JMCIF/JRBBM masks from this chunk before writing them back.
- Power-gating state transitions: VCN 4.0.5 code writes `regUVD_POWER_STATUS`, waits on DLDO/power-status bits, and uses PGFSM/power-status masks to ensure blocks are powered before programming rings or firmware-visible state.
- Ring programming: ring base, read pointer, write pointer, size, and enable fields are programmed by the VCN/JPEG driver around firmware load, ring startup, command submission, preemption, and teardown. Pointer masks in this chunk enforce hardware alignment and field width.
- Interrupt flow: enable registers select which JPEG or UMSCH events can reach the IH, status registers expose pending bits, and ack registers clear handled bits. `*_IH_CTRL` fields bind interrupt VMID/user-data/ring-id context to the interrupt packet path.
- Memcheck flow: JMI/JPEG memcheck enable/status/ack fields allow high/low range violations on read and write clients to be surfaced and cleared; clamping and safe-address fields determine whether bad accesses are redirected.
- MES/UMSCH firmware flow: mailbox, scratch, program-counter, vector, cache-control, timer, and machine-status fields are observed and controlled by host-side setup, reset, debugging, and recovery paths rather than by ordinary CPU functions in this header.

## State And Persistence

All constants describe volatile hardware state, not persisted kernel data structures. Register values persist only as long as the GPU block retains power and reset state:

- Clock-gating, power-gating, and DPG fields are reset or reinitialized across GPU reset, suspend/resume, power transitions, and IP block bring-up.
- Ring pointers, doorbell controls, and write-pointer control state are live coordination state between the CPU driver, GPU command processor/firmware, and the VCN/JPEG engines. They are not meaningful after ring reset unless reprogrammed.
- VMID and BAR fields bind current GPU virtual-memory contexts and buffer addresses. Incorrect persistence across context switch, GPU reset, SR-IOV partition changes, or firmware restart can point the JPEG/VCN engines at stale memory.
- Scratch, mailbox, machine-status, cause, bad-address, counter, and GP registers provide firmware/debug state. They may be used to diagnose a hang or crash, but they are hardware/firmware state and should not be treated as durable host state.
- Interrupt status and ack registers are edge/state synchronization points. Missing an ack, acking with the wrong mask, or reading stale status can leave the interrupt path wedged or noisy.

## Dependencies

Primary dependencies:

- `vcn_4_0_5_offset.h` for the actual MMIO register offsets corresponding to the `reg...` names.
- AMDGPU SOC15 access helpers (`RREG32_SOC15`, `WREG32_SOC15`, `SOC15_WAIT_ON_RREG`, `SOC15_REG_OFFSET`, and JPEG DPG-mode wrappers) for safe hardware access.
- VCN/JPEG driver implementation files, especially `amdgpu/jpeg_v4_0_5.c` and `amdgpu/vcn_v4_0_5.c`, which include this header directly.
- Firmware and microcode for VCN 4.0.5 (`amdgpu/vcn_4_0_5.bin` in the driver firmware selection path), because many UMSCH/MES/ring/mailbox fields coordinate host setup with firmware behavior.
- AMDGPU power-management, interrupt-handler, GPUVM, ring scheduler, SR-IOV/IOV, and reset/recovery subsystems.

This generated header must remain synchronized with the hardware register specification and with the offset header from the same generation. Mixing masks from one IP version with offsets from another would compile but program the wrong bits.

## Integration Points

Observed local include points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c` includes `vcn/vcn_4_0_5_offset.h` and `vcn/vcn_4_0_5_sh_mask.h`. It uses this chunk's JPEG clock-gating masks and shifts in the enable/disable and DPG clock-gating paths, along with power-gating status masks from nearby VCN/JPEG register groups.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c` includes the same offset/mask pair. It uses power-status and PGFSM-related constants during static power-gating setup and reset/bring-up. Other VCN ring, doorbell, scratch, and scheduler constants in the chunk are part of the same IP block programming surface.

Broader integration:

- JPEG decode and encode rings depend on the JPEG/JRBC/JMI register groups to publish ring memory, IB memory, fence memory, output buffers, and preemption state.
- GPUVM and SR-IOV integration depends on the VMID fields (`*_VMID`) and IOV active-function status to route memory accesses and function context correctly.
- Interrupt handling depends on `JPEG_SYS_INT_*`, `JPEG_MEMCHECK_SYS_INT_*`, `JPEG_IH_CTRL`, `VCN_UMSCH_SYS_INT_*`, and `VCN_UMSCH_IH_CTRL` definitions matching IH packet setup and ack semantics.
- Power management depends on `JPEG_CGC_*`, `UVD_PGFSM_*`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, DPG pause/LMA, and deep-sleep control fields to avoid register access while blocks are gated or reset.
- Firmware debug/recovery paths depend on UMSCH/MES mailbox, scratch, busy, machine-state, cache-control, and local-aperture fields to inspect or manipulate scheduler state after hangs.

## Risks And Failure Modes

- Bitfield drift: because the file is generated, hand-editing masks or shifts risks silent hardware misprogramming. A wrong bit in a clock/power/reset field can hang the VCN or JPEG engine.
- Version mismatch: VCN 4.0.5 masks are not interchangeable with nearby VCN generations. Some field names are shared across versions but have different client lists or bit positions.
- Alignment and truncation: many ring pointer and BAR fields mask off low bits or split 64-bit addresses into low/high registers. Callers must shift and align addresses exactly as the hardware expects.
- VMID misuse: wrong VMID fields can cause JPEG/JRBC/EJRBC/scalar/atomic clients to access the wrong GPUVM context, causing faults, data corruption, or security issues under SR-IOV or process isolation.
- Interrupt ack mistakes: the enable/status/ack triplets share similar field names. Writing an enable mask to an ack register or failing to clear memcheck/system interrupt bits can create interrupt storms or lost events.
- Power/clock sequencing: accessing JPEG/VCN registers while `JPEG_CGC_*`, `UVD_PGFSM_*`, DPG pause, or DLDO state indicates the block is gated can return stale data or hang bus accesses.
- Memcheck/clamping policy: disabling clamping or programming an unsafe safe address weakens fault containment for bad JPEG/JMI DMA. Conversely, overbroad clamping can hide address-programming bugs until output corruption appears.
- Duplicated/deprecated field names: `VCN_MES_DC_OP_CNTL` contains both `DEPRECATED` and misspelled `DEPRACATED` field macros. Consumers should avoid assigning new semantics without checking the hardware spec.
- Debug register sensitivity: MES machine-state, local aperture, cache invalidation, and data-memory index registers are low-level firmware controls; accidental writes can perturb running scheduler firmware.

## Test Signals

Useful validation signals after changes that touch consumers of these masks:

- Build coverage for `amdgpu/jpeg_v4_0_5.c` and `amdgpu/vcn_v4_0_5.c` with this header included; compile failures catch renamed or missing macros.
- JPEG decode smoke tests on VCN 4.0.5 hardware: successful ring initialization, command submission, output buffer writeback, fence completion, and no `UVD_JPEG_INT_STAT` error bits such as FIFO overflow, timeout, marker/format/profile errors, or block-count sync errors.
- Clock-gating tests: toggling JPEG clock gating should update `JPEG_CGC_GATE`, `JPEG_CGC_CTRL`, and `JPEG_CGC_STATUS` consistently, with no decode regressions after idle/resume.
- Power-gating tests: suspend/resume, runtime power management, static power-gating enable/disable, and GPU reset should return `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, and PGFSM status to expected values before ring use.
- Interrupt tests: JPEG and UMSCH interrupt enable/status/ack paths should produce one handled interrupt per event, clear status after ack, and avoid overrun bits in `JPEG_MASTINT_EN` or `VCN_UMSCH_MASTINT_EN`.
- Memcheck tests: intentionally invalid or boundary GPU addresses, where supported by validation infrastructure, should set the expected `JPEG_MEMCHECK_SYS_INT_STAT` high/low read/write bits and clear through the matching ack masks.
- GPUVM/SR-IOV tests: multiple VMID contexts and VF/PF configurations should verify JPEG/JMI accesses are attributed to the intended VMID/function and do not leak or fault unexpectedly.
- Firmware recovery tests: forced VCN/JPEG hangs or resets should leave useful UMSCH/MES busy/status/cause/bad-address/scratch evidence and recover after cache invalidation/reset sequencing.
