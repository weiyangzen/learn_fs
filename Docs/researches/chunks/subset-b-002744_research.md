# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_2_sh_mask.h lines 5195-7850

## Scope

This chunk is the final 2,656 lines of the generated-style AMDGPU GMC 8.2 shift/mask header. It contains only preprocessor `#define` symbols for register-field masks and shifts, followed by the `GMC_8_2_SH_MASK_H` include-guard close at line 7850.

There are no functions, structs, enums, global variables, allocations, locks, loops, branches, callbacks, or runtime side effects in this range. The exported surface is compile-time metadata used by AMDGPU code to pack values into, and unpack values from, GMC 8.2 memory-controller, virtual-memory, translation-cache, arbitration, power, and writeback registers.

Although the path is under a `ceph-client` source mirror, this file is AMD GPU DRM hardware metadata. It is not Ceph filesystem code.

## Purpose

`gmc_8_2_sh_mask.h` pairs with the GMC 8.2 register-offset header (`gmc_8_2_d.h`) and AMDGPU MMIO/register helpers. This tail chunk defines the bit layouts for register families that control or observe:

- MC crossbar arbitration and FIFO monitoring.
- MC, ATC, CHUB ATC, and GRUB performance counters.
- Address Translation Cache (ATC), ATS/PRI/PASID behavior, ATC L1/L2 TLB/cache debug state, fault reporting, and VMID-to-PASID mapping.
- GMCON power, clock-gating, stutter, PGFSM, and performance-monitor controls.
- VM L2 cache controls, VM contexts 0 and 1, context fault controls/status, dummy/default fault pages, invalidation requests/responses, PRT aperture/fault policy, page-table base/start/end registers, and identity apertures.
- SR-IOV/virtualization-related frame-buffer sizing and offset registers for virtual functions, plus MARC relocation/length windows.
- MC arbiter "HARSH" scheduling, GRUB priorities, GRUB probe/credit/feature controls, and transaction-control-buffer access.
- Fused DRAM address mapping, controller base/limit/high-offset fields, DRAM aperture/default/lock controls, and Garlic arbitration priorities.
- MCIF writeback buffer-manager state, buffer addresses, pitch, per-buffer status/error bits, software/VCE locking, interrupts, VMID filtering, arbitration, urgency watermarks, and debug access.

The file lets C code refer to field boundaries symbolically rather than hard-coding masks such as `0x10000000` or shifts such as `0x1c`. That is important because most consumers use read-modify-write sequences where one wrong mask can corrupt adjacent hardware fields.

## Important APIs, Types, And Constants

The "API" in this chunk is the naming convention:

- `<REGISTER>__<FIELD>_MASK` identifies the bit mask for a field.
- `<REGISTER>__<FIELD>__SHIFT` identifies the least-significant-bit position for that field.
- Full-width data/count fields use masks such as `0xffffffff`; smaller fields use byte, nibble, VMID, page-number, or client-id-sized masks.

Major exported register-field groups include:

- Lines 5195-5242: `MC_XBAR_ARB_MAX_BURST`, `MC_XBAR_FIFO_MON_CNTL*`, `MC_XBAR_FIFO_MON_RSLT*`, `MC_XBAR_FIFO_MON_MAX_THSH`, and spare crossbar words. These describe write-port burst limits, FIFO monitor start/stop thresholds and trigger IDs, four monitor result counters, maximum thresholds, and spare bits.
- Lines 5243-5762: performance-counter layouts for `MC_CITF`, `MC_HUB`, `MC_RPB`, `MC_MCBVM`, `MC_MCDVM`, `MC_VM_L2`, `MC_ARB`, `ATC`, `CHUB_ATC`, and `MC_GRUB`. Repeated patterns define low 32-bit count words, high 16-bit count/compare words, counter configuration fields (`PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, `CLEAR`), and result control (`PERF_COUNTER_SELECT`, start/stop triggers, enable-any, clear-all, stop-on-saturate).
- Lines 5763-6221: ATC/ATS address apertures, ATS control/debug/fault/status/default-page fields, ATC L2/L1 cache and TLB debug fields, read/write TLB status and parity-injection fields, all 16 VMID-to-PASID mapping registers, remap-complete status bits, outstanding VMID status bits, and SMU power/status bits.
- Lines 6222-6388: `GMCON_*` fields for client stall/urgency masks, stutter watermarks, debug, miscellaneous power/clock-gating/soft-reset controls, memory power low-power masks, MGCG override masks, perfmon controls/results, PGFSM indexed access, and STCTRL busy/handshake masks.
- Lines 6389-6834: VM L2 cache and VM context fields. These cover L2 cache enable/fragment/endian/PDE/PTE/default-page/identity modes, invalidation controls, cache sizing and force-miss debug, context enable/page-table-depth/fault-action bits for contexts 0 and 1, context fault address/status/default address fields, invalidation request/response domains 0-15, PRT apertures and fault-disabling policy, context-disable bits 0-15, page-table bases for contexts 0-15, and identity-aperture/physical-offset controls.
- Lines 6835-6984: SR-IOV and relocation fields: `MC_VM_FB_SIZE_OFFSET_VF0` through `VF15` for per-virtual-function frame-buffer size/offset pairs, `MC_VM_SYSTEM_APERTURE_*`, `MC_VM_LOCAL_FB_*`, `MC_VM_FB_LOCATION*`, AGP top/bot/base and default address fields, `MC_VM_MARC_RELOC_*`, `MC_VM_MARC_LEN_*`, and `MC_VM_MARC_CNTL`.
- Lines 6985-7320: MC arbiter and GRUB priority fields. `MC_ARB_HARSH_*` describes read/write priority groups, bandwidth periods/counts/saturation, force-highest/stall controls, and perf monitor selection. `MC_ARB_GRUB_PRIORITY*` maps memory clients such as CB, DB, TC, ACP, DMIF, MCIF, RLC, VMC, SDMA, HDP, UVD, VCE, SMU, SEM, ISP, VP8, and VIN to read/write GRUB priority fields.
- Lines 7321-7536: fused DRAM and Garlic arbitration fields. These include per-channel/chip-select base address and enable fields, DRAM bank address mapping, DCT base/limit/high-offset/mode fields, DRAM aperture/default/lock fields, isochronous and urgency priority enables/overrides, request credits, response FIFO limits, Garlic write priority fields, and the `MC_CG_DATAPORT` data word.
- Lines 7537-7624: GRUB probe map, post-probe delay, probe credits, feature toggles, TX credits, and indexed TCB data access.
- Lines 7625-7848: MCIF writeback buffer-manager fields for software and VCE control, current line and status readback, pitch, four buffer status/status2 blocks, arbitration/watermarks/test debug, Y/C base addresses and offsets for buffers 1-4, and writeback VMID access control.

## Control Flow

This chunk has no direct control flow. The implied runtime flow in AMDGPU code is:

1. Include `gmc_8_2_d.h` for the register address and this header for the register field layout.
2. Build a register value by shifting a field value with `__SHIFT` and masking it with `__MASK`, or isolate a hardware readback with the mask and shift.
3. Perform a register write, read-modify-write, poll, interrupt acknowledgement, fault decode, performance-counter readout, or debug dump in the surrounding driver.
4. Hardware consumes or produces the corresponding GMC/ATC/VM/MCIF/arbiter state.

The ordering requirements are external to this header. Examples include flushing or waiting for VM invalidations before reusing page tables, clearing fault status only after logging it, programming performance counters before enabling them, and respecting buffer locks/interrupt acks for MCIF writeback.

## State And Persistence Behavior

The header itself is stateless. The constants describe state that persists in hardware registers after driver writes, or transient state that software observes through readback registers.

Persistent control state includes VM L2 enable/configuration, VM context control, page-table base/start/end registers, context-disable bits, PRT policy, ATC/ATS mode bits, VMID/PASID mappings, per-VF frame-buffer windows, MARC relocation windows, DRAM/fused aperture mapping, arbiter/GRUB priorities, GMCON clock/power/stutter controls, and MCIF writeback buffer configuration.

Transient or event-like state includes performance counter low/high words, FIFO monitor result counters, ATC/VM busy/deadlock/fault/parity status, VM invalidation responses, protection-fault status/address/client fields, MCIF current-buffer/current-line/error/status bits, and interrupt ack/status bits.

Several fields have special persistence hazards:

- `CLEAR`, `CLEAR_ALL`, `CLEAR_*`, `INVALIDATE_*`, `POWER_DOWN`, `POWER_UP`, interrupt `ACK`, parity-injection, and indexed-read/write-enable fields are command-like bits. They may be write-one-to-trigger or otherwise edge-sensitive in hardware even though this header only exposes their positions.
- Fault status address fields and "allow subsequent updates" controls affect whether later faults overwrite earlier diagnostic state.
- VMID/PASID mappings and VM context page-table state are security-sensitive because stale mappings can expose one process or virtual function's memory to another.
- MCIF buffer lock and active/error bits coordinate software and VCE/writeback ownership. Wrong lock or ack handling can lose frames or hide overflow/line-length errors.

## Dependencies And Integration Points

This header depends on the generated GMC 8.2 register database staying synchronized with the hardware and with `gmc_8_2_d.h`. The direct include point found in this tree is VI-era AMDGPU code such as `amdgpu/mxgpu_vi.c`, which includes both `gmc/gmc_8_2_d.h` and `gmc/gmc_8_2_sh_mask.h` alongside other VI register headers.

Important integration surfaces include:

- AMDGPU MMIO helpers and read-modify-write helpers that combine register offsets with these masks/shifts.
- GMC v8 memory-management initialization and GPUVM programming paths, especially VM L2 cache setup, context setup, page-table base programming, dummy/default-page policy, and TLB/cache invalidation.
- Fault reporting, interrupt handling, and hang/debug dump paths that decode VM and ATC fault/status fields.
- SR-IOV and MxGPU paths that configure per-VF frame-buffer windows, VMID restrictions, and virtualization-related ATC/VM state.
- Performance-monitor/debugfs or profiling paths that program GMC/ATC/GRUB performance counters and read counter results.
- Power-management and clock-gating paths that use GMCON and ATC/VM clock-gating/memory-light-sleep fields.
- Display/video/writeback paths that program MCIF writeback buffers, pitches, addresses, locks, VMID access, and interrupt behavior.
- Memory-controller arbitration/tuning paths that use HARSH, GRUB, Garlic, and DRAM aperture/mapping fields.

Because the symbols are preprocessor macros, they are globally visible after inclusion. They must stay name-compatible with the rest of the AMDGPU register headers and cannot be scoped like C enums or typed constants.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift compiles cleanly but programs the wrong hardware bits, potentially corrupting VM state, disabling faults, breaking address translation, or producing misleading diagnostics.
- Many register names are repeated with numeric suffixes (`0-15` VMIDs/domains/contexts/VFs, four perf counters, four MCIF buffers). Off-by-one edits or copy/paste drift can silently target the wrong VMID, invalidation domain, virtual function, or buffer.
- Full-width fields such as counters, data ports, fault-client names, and buffer base addresses need correct register width assumptions. Treating a page-number field as a byte address, or vice versa, would misprogram memory windows.
- VM fault controls include separate interrupt/default/save bits for multiple fault classes. Enabling default-page behavior where interrupt/save was expected can mask real page-table bugs.
- `VM_INVALIDATE_REQUEST` and `VM_INVALIDATE_RESPONSE` fields are per-domain bitmaps. Callers must not assume a request completed until the matching response bit is observed according to the surrounding driver protocol.
- ATC/ATS/PASID fields interact with IOMMU/PCIe ATS semantics. Incorrect disable, invalidation, or VMID/PASID mapping can cause stale translations, incorrect fault attribution, or isolation problems.
- Fault status update controls can overwrite the first fault if subsequent updates are allowed too early, making root-cause analysis harder after GPU hangs.
- Performance-counter selectors and result controls are repetitive across blocks but not interchangeable. A counter configured for one block's event mux may read plausible but meaningless values if used with another block.
- Debug and parity-injection fields (`INJECT_SOFT_PARITY_ERROR`, `INJECT_HARD_PARITY_ERROR`, cache/TLB read selectors) are dangerous outside controlled validation because they can deliberately create error conditions.
- Arbitration and priority fields can create QoS regressions. Misprogramming HARSH, GRUB, or Garlic priorities may starve display/video/SDMA clients or reduce GPU throughput without an obvious kernel failure.
- MCIF writeback status includes overflow, long-line, short-line, frame-length, lock, active, field, next-buffer, and current-line bits. Clearing or ignoring them incorrectly can hide dropped/corrupt writeback frames.
- Some symbols contain doubled wording such as `*_MASK_MASK`, reflecting generated names for fields that themselves are called "mask". Consumers should not "clean up" these names without updating all generated users.

## Test Signals

Useful validation signals for this chunk are mostly build, generated-data, and hardware/runtime checks:

- Kernel build coverage for AMDGPU VI/GMC 8.2 files that include `gmc_8_2_sh_mask.h`.
- Mechanical comparison against AMD's authoritative GMC 8.2 register database for every mask and shift in lines 5195-7850.
- Static checks that every field mask is compatible with its shift and width, and that repeated numeric families have the expected sequence of bits or register suffixes.
- Cross-checks that every register field here has a matching register offset in `gmc_8_2_d.h` and, where applicable, matching enum/value definitions in companion headers.
- GPUVM tests that create/destroy contexts, program page tables, invalidate VM domains, exercise dummy/default-page behavior, and verify no stale translations or unexpected VM faults.
- Fault-injection or negative tests that trigger read/write/execute/PDE/dummy/range faults and verify decoded VMID, client ID, address, protection bits, and interrupt/save/default behavior.
- SR-IOV/MxGPU tests that validate per-VF framebuffer size/offset isolation, allowed VMID masks, PASID mappings, and virtualization entry/exit invalidation behavior.
- Performance-counter tests selecting representative MC, ATC, CHUB_ATC, VM_L2, ARB, and GRUB events and checking that counters clear, enable, saturate/stop, and increment under targeted workloads.
- Power-management tests for GMCON/ATC/VM clock-gating and memory-light-sleep settings, with resume/reset paths verifying register reprogramming.
- Display/video writeback tests that cycle MCIF buffers 1-4, exercise software and VCE locks, verify interrupt ack/status behavior, and detect overflow/line/frame-length error reporting.
- Memory-bandwidth and display-stability workloads to catch arbitration regressions from HARSH, GRUB, Garlic, or DRAM mapping fields.
- Runtime warning signals include GPU VM faults with wrong client/VMID decode, invalidation timeouts, hangs after context teardown, impossible performance counter values, SR-IOV memory isolation failures, dropped writeback frames, or display underflow/stutter after arbitration changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002744`. It covers lines 5195-7850, the tail of `gmc_8_2_sh_mask.h`. The final per-file research should merge this with earlier chunks for the complete GMC 8.2 register-field map, including register families whose definitions begin before line 5195.
