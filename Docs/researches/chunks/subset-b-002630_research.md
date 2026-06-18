# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h lines 4993-7473

Covered source range: lines 4993-7473 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`

## Purpose

This chunk is a generated AMDGPU GC 9.1 register-offset header segment. It contains C preprocessor constants only: no functions, structs, enums, variables, storage, allocations, locking, callbacks, or executable branches. The constants map named Graphics Core hardware registers to offsets and, for ordinary MMIO registers, pair each address macro with a generated `_BASE_IDX` macro.

The selected range begins in the middle of an unnamed-by-comment MMIO block that is already active before line 4993. It starts at `mmCP_DMA_PFP_SRC_ADDR` and continues through command processor, graphics frontend, shader, render backend, memory/cache, performance, RLC, power, hypervisor, CAC, SQ indirect, and DIDT indirect register families. It ends inside the `didtind` address block at `ixDIDT_DBR_EDC_STALL_DELAY_1`; the rest of the DIDT DBR block continues after this chunk. The final per-file report should reconcile those chunk-boundary splits.

The file path sits under a `ceph-client` source mirror, but this header is AMD DRM GPU hardware metadata, not Ceph filesystem logic.

## Scope and Register Areas

This range has 2,421 `#define` lines: 2,040 `mm*` defines, 381 `ix*` indirect-register defines, 1,020 `_BASE_IDX` lines, and 1,401 address-bearing macros. The dominant direct MMIO families are `RLC`, `CP`, `CGTS`, `SQ`, `PA`, `MC`, `GDS`, `VGT`, `GRBM`, `SPI`, `DB`, `CGTT`, `VM`, `WD`, `RMI`, `TCC`, `TCA`, `CB`, `TCP`, `SX`, `IA`, `TA`, `CPG`, `CPF`, `CPC`, `TD`, `ATC`, `SQC`, `UTCL2`, `SMU`, and `GCEA`.

Important direct-address groups in the opening portion include:

- `CP_*`, `CPF_*`, `CPG_*`, and `CPC_*`: command processor DMA, PFP/ME/CE buffers, indirect-buffer offsets, scratch registers, coherency registers, command buffer sizes, EOP completion controls, metadata bases, indirect draw/dispatch addresses, index state, GDS backup addresses, sample status, and ME coherency status.
- `GRBM_GFX_INDEX`: per-instance, shader-array, and shader-engine register targeting control. This register is central to programming per-SE/SH hardware and has matching field definitions in `gc_9_1_sh_mask.h`.
- `VGT_*`, `IA_*`, and `WD_*`: geometry/input front-end state such as primitive type, index type, streamout filled sizes, vertex index bounds, instance/index counts, tessellation/ring memory bases, GS/ES/VS ring item sizes, primitive distribution, draw distribution controls, draw-init status, and wave allocation limits.
- `PA_*`, `SPI_*`, and `SQ_*`: setup, scanner, shader processor input, and shader queue addresses for viewport/primitive state, shader program resources and user data, wave limits, trap/debug registers, LDS sizing, shader scratch, thread-trace, performance counters, interrupt messages, and SQ command/control registers.
- `SX_*`, `DB_*`, `CB_*`, `GDS_*`, `TA_*`, `TD_*`, `TCP_*`, `TCC_*`, `TCA_*`, `RMI_*`, `MC_*`, `ATC_*`, and `VM_*`: color/depth/backend, global-data-share, texture, cache, memory-interface, VM, and address-translation registers used for pipeline state, caches, faults, counters, flushes, and diagnostics.

The chunk then enters named address blocks:

- `gc_perfddec` at base `0x34000`: many `CGTS_*` and `CGTT_*` performance and clock/throttle selector, counter, control, and status registers, plus `GCEA_PERF_*`, `GC_PERF_*`, and miscellaneous GC performance controls.
- `gc_utcl2_atcl2pfcntrdec`, `gc_utcl2_vml2prdec`, `gc_utcl2_atcl2pfcntldec`, and `gc_utcl2_vml2pldec`: UTCL2/ATCL2/VML2 performance counter read, select, control, status, and invalidate controls.
- `gc_perfsdec`: global GC performance monitor configuration, per-block counter selection, counter low/high values, 64-bit counter pairs, and master control/status.
- `gc_rlcpdec`: a dense RLC block covering performance monitors, golden-setting support, power/power-gating handshakes, profiling/data ports, graphics memory save/restore pointers, virtual-function interface registers, CP/MEC/GRBM status mirrors, interrupt/status, and ucode control.
- `gc_pwrdec` and `gc_ea_pwrdec`: power, clock-gating, stutter, light-sleep, power-status, and SRAM/logic gating controls across GRBM, CP, RLC, SPI, SQ, DB, CB, TCC, TCP, TA, TD, WD, VM, PA, GDS, CPF/CPG/CPC, RMI, and MC.
- `gc_utcl2_vmsharedhvdec` and `gc_hypdec`: hypervisor/virtualization-facing registers such as VRAM page-table base/limit, VM context control and faults, VF/VMID controls, GRBM virtualization, scrubber/cleaner, PASID mapping, and ATS/ATC/VML2 cache invalidation controls.
- `gccacind` and `secacind`: indirect clock/activity counter control, weights, accumulators, and overrides for many GC and SE subblocks.
- `sqind`: shader wave indirect debug state including wave status, mode, trap status, hardware ID, GPR/LDS allocation, program counter, instruction dwords, TTMP registers, `M0`, execution mask, and interrupt-word aliases.
- `didtind`: dynamic power/current control, stall, tuning, EDC, threshold, status, overflow, rolling-power-delta, and stall-delay registers. This chunk covers SQ, DB, TD, TCP, and the beginning of DBR DIDT groups.

## Important APIs, Types, and Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `mm<REGISTER>` gives a direct GC 9.1 MMIO register offset.
- `mm<REGISTER>_BASE_IDX` gives the SOC15 base-index selector for that register. In this chunk the direct MMIO registers use base index `1`.
- `ix<REGISTER>` gives an indirect register index. These occur in `gccacind`, `secacind`, `sqind`, and `didtind` blocks and do not have `_BASE_IDX` companion macros in this range.

The address macros are normally used with AMDGPU register helper infrastructure rather than hand-built addresses. Common integration patterns include `SOC15_REG_OFFSET(GC, instance, mm...)`, `RREG32_SOC15`, `WREG32_SOC15`, direct `RREG32`/`WREG32` where the generation-specific offset is already selected, and specialized indirect helpers such as DIDT or SQ wave-indirect accessors. Bit fields for these registers live in the companion `gc_9_1_sh_mask.h` header, for example `GRBM_GFX_INDEX__*` and `SQ_IND_INDEX__*`.

## Control Flow and Data Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution:

1. A GC 9.1-aware AMDGPU source file includes this generated offset header, often alongside `gc_9_1_sh_mask.h` and default-value headers.
2. Runtime code selects the detected ASIC/IP block and the desired register instance.
3. A register helper combines the SOC15 block base, instance, macro offset, and base index into an MMIO address, or an indirect helper writes a selector register and then reads/writes an indirect data port.
4. The driver reads, writes, polls, or composes register values using the address macro plus field masks from the matching shift/mask header.

For direct MMIO registers, the data flow is usually driver or firmware programming to hardware state, followed by readback/polling for status and fault information. For `sqind` and `didtind`, the macro value is an index into an indirect register window rather than a CPU-visible MMIO address by itself. SQ wave dump paths typically program `SQ_IND_INDEX` with wave/SIMD/thread/index fields, then read `SQ_IND_DATA` for indexes such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, or `ixSQ_WAVE_EXEC_LO`. DIDT paths use DIDT-specific accessors such as `RREG32_DIDT` and `WREG32_DIDT`.

## State and Persistence Behavior

The macros store no state. They describe hardware registers whose values are owned by GPU hardware, firmware, command submission, initialization, power management, debug paths, and reset/recovery code.

Several groups represent persistent configuration until reset or later programming: CP ring and indirect-buffer bases/sizes, VGT geometry state, shader program/user-data addresses, PA/SPI/SQ setup controls, backend/cache policy, RLC save/restore pointers, virtualization mappings, and clock/power-gating policy. Other registers are volatile status or counters: busy/status registers, performance counters, fault records, EDC counters, wave debug state, and power/stutter status can change while the GPU is running.

Indirect groups have additional sequencing state. Reading `ixSQ_WAVE_*` depends on the current indirect selector fields and selected wave context. DIDT and CAC indirect registers depend on their access window and are not interchangeable with direct `mm*` addresses. Hypervisor and virtualization registers may persist VMID/PASID/fault ownership state across queue activity and are sensitive during GPU reset or SR-IOV transitions.

## Dependencies and Integration Points

This chunk depends on the rest of `gc_9_1_offset.h` for the include guard, earlier direct MMIO blocks, and trailing DIDT definitions. It is designed to stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h`, which defines field shifts/masks for the addresses in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_default.h`, where reset/default values are available for related registers.
- SOC15 register helper code that interprets the `mm*` offset plus `_BASE_IDX` convention.

The one direct include found in this repository copy is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.c`, which includes `gc/gc_9_1_offset.h` for GC 9.1 device support while handling PSP v10 microcode, firmware quirks, ring setup, and mailbox polling. Even when a specific consumer does not spell many of these macros directly in this tree, the generated header is part of the ASIC register contract used by AMDGPU bring-up, firmware handoff, debug, reset, and power-management code.

Related integration patterns elsewhere in AMDGPU show how the same macro families are used:

- `GRBM_GFX_INDEX` is selected before programming per-instance/per-SE/per-SH registers, with locking requirements called out around GRBM index/control access in virtualization paths.
- SQ indirect wave-state dumps program `SQ_IND_INDEX` and read `SQ_IND_DATA` with `ixSQ_WAVE_*` indexes.
- Legacy DIDT power-management code reads and writes `ixDIDT_SQ_CTRL0`, `ixDIDT_DB_CTRL0`, `ixDIDT_TD_CTRL0`, and `ixDIDT_TCP_CTRL0` through `RREG32_DIDT`/`WREG32_DIDT`.
- Performance, RLC, clock-gating, and power registers feed golden-register programming, runtime power policy, hang diagnostics, and GPU reset/recovery validation.

## Risks and Gotchas

- Manual edits are high risk. A wrong offset or `_BASE_IDX` compiles cleanly but can redirect MMIO to the wrong register, wrong hardware instance, or wrong indirect index.
- The chunk starts and ends mid-logical area. It starts after prior CP DMA/ME/coherency definitions and ends before the full DIDT DBR group is complete.
- `mm*` and `ix*` macros are different address spaces. Treating an indirect `ix*` value as a direct MMIO offset, or vice versa, would access the wrong hardware path.
- `_BASE_IDX` values are part of the SOC15 addressing contract. Dropping or changing base index `1` for this direct-register range can silently shift accesses into the wrong aperture.
- `GRBM_GFX_INDEX` changes the target of many subsequent accesses. Code using it must preserve broadcast/index semantics and honor existing locking or access-control conventions.
- Many registers are control or debug knobs, not simple status values. CP, RLC, power-gating, DIDT, clock-gating, DSM/debug, virtualization, and cache/TLB registers can affect command execution, reset behavior, power throttling, memory translation, or fault visibility.
- Some registers are counters, latched faults, clear-on-read, write-one-to-clear, or hardware-owned status in practice. The offset header does not encode access type, volatility, side effects, or reset semantics.
- Repeated aliases and same-offset aliases are intentional in generated register headers. For example, multiple `ixSQ_INTERRUPT_WORD_*` names share `0x20c0`; tooling should not treat this as a duplicate-generation bug without hardware context.
- Generated headers often have near-identical names across GC versions. Mixing GC 9.1 offsets with a different generation's shift/mask header can produce valid C with invalid hardware behavior.

## Test and Validation Signals

Useful validation is mostly build-time, static consistency, and hardware smoke coverage:

- Compile coverage for translation units that include `gc_9_1_offset.h`, especially `psp_v10_0.c` in this source tree.
- Static checks that every direct `mm*` define in this range has exactly one matching `_BASE_IDX` define, and that indirect `ix*` defines are not expected to have `_BASE_IDX` companions.
- Static comparison against the generated register database or adjacent GC 9.x headers for known shared offsets such as `mmCP_DMA_PFP_SRC_ADDR`, `mmGRBM_GFX_INDEX`, `mmGRBM_GFX_INDEX_SR_SELECT`, `mmGRBM_GFX_INDEX_SR_DATA`, `ixSQ_WAVE_STATUS`, and `ixDIDT_SQ_CTRL0`.
- Runtime GC 9.1 smoke on Raven/Picasso-class hardware covering PSP initialization, graphics ring setup, basic command submission, suspend/resume, GPU reset, and power-management transitions.
- Debug/hang-dump validation that SQ wave indirect reads return plausible wave status/PC/EXEC data and that DIDT/CAC/performance accesses use the correct indirect path.
- Fault and virtualization tests that exercise VMID/PASID/fault registers, ATC/UTCL2 invalidation, and RLC/GRBM virtualization controls without spurious protected-register or read/write errors.

## Chunk Boundary Notes

This is a chunk-only research document for `subset-b-002630`. It covers only lines 4993-7473 of `gc_9_1_offset.h`; it is not the final per-file report. The merge/reconciliation lane should combine this with preceding chunks for the earlier CP/SQ/etc. direct MMIO definitions and following chunks for the remainder of `didtind` and the file epilogue.
