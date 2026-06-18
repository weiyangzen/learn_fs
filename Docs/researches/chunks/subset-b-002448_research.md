# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h lines 9944-11375

## Purpose

This chunk is the final slice of the generated AMD Graphics Core 10.1.0 register-offset header. It defines numeric register offsets and register-base indices for AMDGPU GC blocks; it does not contain executable driver logic. Consumers include the header to translate symbolic register names into MMIO register offsets (`mm*`) or indirect-register indices (`ix*`) used by AMDGPU register access helpers and generated register tables.

Although the repository path is under a local `ceph-client` source mirror, this file is GPU driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The requested range contains 1,432 lines and 1,389 `#define` statements: 793 direct `mm*` register defines, 596 indirect `ix*` register-index defines, and 397 `_BASE_IDX` defines. It starts in the middle of the CGTS per-WGP control-register grid, after `mmCGTS_SA0_WGP00_CU1_SIMD0_CTRL_REG` was defined in the previous chunk, and ends at the file-level `#endif` after the DIDT indirect-register block.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, or direct MMIO operations in this range. The interface is entirely preprocessor constants:

- `mm<REGISTER>`: direct GC register offset used by AMDGPU MMIO access macros and generated register lists.
- `mm<REGISTER>_BASE_IDX`: register-base selector for direct-register access. Every `_BASE_IDX` in this chunk is `1`, matching the GC base segment used by these addresses.
- `ix<REGISTER>`: indirect-register index for indexed access spaces such as CAC, SPM, SQ, and DIDT.
- `// addressBlock: ...` comments: generated boundaries that identify the hardware register namespace or indirect aperture for the following defines.

The chunk covers these major groups:

- CGTS and CGTT clock-gating/control offsets before the first visible address-block marker. This includes `mmCGTS_SA*_WGP*_CU*_{SIMD0,SIMD1,TATD,TCP}_CTRL_REG` entries for shader-array/WGP/CU units, plus clock controls for SPI, PC, BCI, VGT, IA, WD, GS/NGG, PA, SC, SQ, SX, TD, TA, TCP, GDS, DB, CB, GL2, CP, RLC, RMI, GCR, UTCL1, GCEA, SE/GC CAC, GRBM, GL1, CH, GUS, and PH.
- `gc_hypdec` at base `0x3e000`: command processor, RLC, GRBM, interrupt-cookie, and GPU I/O virtualization registers. It includes ucode address/data pairs for PFP, CE, MEC, GPM, PACE, GPU_IOV, RLCV, RLCP; instruction/data cache base controls; MES instruction/data/local apertures and bounds; GRBM CAM and indexed SR controls; RLC GPU_IOV scheduling, status, reset, timer, doorbell, mask, interrupt, semaphore, checksum, scratch, and bootload registers.
- `gc_sdma0_sdma0hypdec` and `gc_sdma1_sdma1hypdec` at bases `0x3e200` and `0x3e280`: mirrored SDMA virtualization/ucode/VM context registers for SDMA0 and SDMA1, including `UCODE_ADDR`, `UCODE_DATA`, `VM_CTX_LO/HI`, `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, `VIRT_RESET_REQ`, `VF_ENABLE`, `CONTEXT_REG_TYPE0..3`, and `VM_CNTL`.
- `gc_gcvmsharedhvdec` at base `0x3ea00`: shared GCVM virtualization aperture definitions. It maps per-VF framebuffer size/offset registers for VF0 through VF31, MARC base/relocation/length registers, IOMMU controls, PCIe ATS controls for the PF and VF0 through VF31, a GCUTCL2 clock-gating register, and shared active-function state.
- `gccacind`: indirect graphics-core clock/activity counter and power-control registers. It includes PCC and power-break stall-pattern controls, GC CAC ID/control/override, per-block activity weights, per-block accumulators, per-block override registers, stall/release/power-break LUTs, fixed-pattern performance counters, and hardware LUT update status.
- `secacind`: a small shader-engine CAC indirect block with SE CAC ID/control/override select/value registers.
- `spmglbind`: global SPM sample-delay indirect registers for CPG/CPC/CPF, GDS/GCR/PH/GE/GUS, CH/ATCL2/VML2, SDMA, GL2A, GL2C, EA, and CHC instances.
- `spmind`: shader-engine SPM sample-delay indirect registers for SPI, SQG, CBR/DBR, SA0/SA1 graphics subblocks, per-WGP TA/TD/TCP units, and GL1/CB/DB/SC/RMI paths.
- `sqind`: shader queue indirect debug and wave-state registers such as `ixSQ_DEBUG_STS_LOCAL`, wave mode/status/trap status, hardware IDs, GPR/LDS allocation, IB state, wave PC/instruction, TTMP registers, M0, EXEC, flat scratch, XNACK mask, and overlapping interrupt-word aliases.
- `didtind`: deterministic/dynamic induced throttling indirect registers for SQ, DB, TD, and TCP blocks. Each block exposes control, OCP, stall, tuning, auto-release, stall-pattern, scale-factor, release-count/status, weight, EDC threshold/timer/delay/status/overflow/rolling-delta/PCC counter, and final stall-event-counter indices.

## Control Flow

This header has no runtime control flow. Runtime behavior appears only after another AMDGPU source file includes the header and expands these macros:

1. A GC 10.1.0 consumer selects a direct `mm*` register offset or an indirect `ix*` register index.
2. For direct registers, the consumer pairs the offset with its `_BASE_IDX` and uses AMDGPU register helpers for reads, writes, read-modify-write operations, polling, register dumps, or generated initialization sequences.
3. For indirect registers, the consumer programs the appropriate selector/data aperture for the address block and uses the `ix*` value as the indexed register address.
4. Hardware, firmware, microcontrollers, and virtualization paths perform the actual clock-gating, cache, command-processor, SDMA, VM, CAC, SPM, SQ debug, or DIDT behavior.

The only sequencing implied by this chunk is external to the header. Examples include loading CP/RLC/SDMA microcode through address/data pairs, configuring MES apertures and bounds, selecting active virtual functions, programming GPU_IOV scheduling and resets, setting per-VF GCVM/ATS windows, sampling SPM counters, reading SQ wave state, and adjusting CAC/DIDT power-throttling tables.

## State And Persistence Behavior

The macros are stateless compile-time constants. They name hardware-visible state but do not store it. Register contents live in GPU hardware, firmware-owned SRAMs, indirect-register banks, or virtualization apertures and may be volatile, latched, write-one-to-clear, self-clearing, retained, or reset depending on the owning block.

State named by this chunk includes:

- Clock-gating and clock-control state across graphics front-end, shader, texture, cache, command-processor, RLC, memory, and hub blocks.
- Command-processor and RLC microcode addressing/data state, instruction/data cache base state, MES local aperture state, and RLC scratch/bootload/reset/checksum state.
- GPU I/O virtualization state: active function IDs, VF enable masks, scheduling registers, doorbell status/set/clear, VM busy status, interrupt status/disable/force, virtual reset requests, semaphores, SMU/RLC responses, and per-SDMA virtualized context registers.
- GCVM state: per-VF framebuffer size/offset registers, MARC base/relocation/length windows, IOMMU controls, and PCIe ATS controls.
- CAC and DIDT state: per-block activity weights, accumulators, overrides, stall/release/power-break patterns, EDC thresholds/timers/delays/status, rolling power deltas, and throttling/event counters.
- SPM and SQ debug state: global and per-shader-engine sample delays, wave execution/debug registers, temporary wave registers, program counter, EXEC mask, scratch/XNACK state, and interrupt-word aliases.

Persistence is hardware-defined and outside this header. Values can be initialized during GPU bring-up, rewritten by firmware or power-management code, reset during GPU reset or virtualization reset, reprogrammed during suspend/resume, and changed by debug/profiling flows. The header does not define reset values, access permissions, legal field encodings, locking rules, polling timeouts, or ownership between PF, VF, firmware, and host driver.

## Dependencies And Integration Points

This generated offset header must stay synchronized with the GC 10.1.0 register database and with companion shift/mask headers that describe bit fields for the same symbolic registers. Integration points include:

- AMDGPU GC 10.1.0 support code under `drivers/gpu/drm/amd/`, especially graphics, command processor, SDMA, RLC, MES, VM, virtualization, power management, profiling, and debug paths.
- Companion generated headers in `drivers/gpu/drm/amd/include/asic_reg/gc/`, such as GC 10.1.0 shift/mask headers and neighboring generation offset headers.
- Register-access helpers that combine `mm*` offsets, `_BASE_IDX` selectors, and field masks/shifts from companion headers.
- Microcode loading paths for CP PFP/CE/MEC, RLC GPM/PACE/GPU_IOV/RLCV/RLCP, and SDMA0/SDMA1.
- SR-IOV/GPU virtualization paths that manage VF enablement, active function IDs, per-VF framebuffer/ATS/MMIO state, virtual resets, doorbell status, scheduling, and interrupt reporting.
- Profiling, telemetry, and power-management flows using CAC, SPM, SQ wave debug, and DIDT indirect registers.

The range crosses multiple generated address spaces. Direct `mm*` offsets use the GC base-index convention, while `ix*` defines are offsets inside specific indirect register banks. Consumers must not mix these access methods.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset can compile cleanly while targeting the wrong GPU register.
- The file is generated. Manual edits risk divergence from AMD's register database, silicon documentation, firmware assumptions, and matching shift/mask headers.
- The first requested line is a continuation of the CGTS register family: `mmCGTS_SA0_WGP00_CU1_SIMD0_CTRL_REG` itself is in the previous chunk, while this chunk begins with its `_BASE_IDX`.
- Several symbols intentionally alias the same offset, such as `mmCP_ME_RAM_RADDR` and `mmCP_ME_RAM_WADDR`, `mmCP_MES_IC_BASE_*` and `mmCP_MES_MIBASE_*`, `mmCP_MES_DC_BASE_*` and `mmCP_MES_MDBASE_*`, `mmGRBM_CAM_*` and `mmGRBM_HYP_CAM_*`, and the SQ interrupt-word aliases at `0x20c0`. Deduplication tools must preserve aliases because different driver paths may use semantic names.
- Direct `mm*` and indirect `ix*` names are easy to confuse. Using an `ix*` value through a direct MMIO helper, or using an `mm*` offset through an indirect aperture, can silently access unrelated hardware.
- Virtualization registers are sensitive to PF/VF ownership, active-function selection, scheduling windows, doorbell status, and reset/interrupt handshakes. Incorrect offsets can break isolation or leave a VF stuck after reset.
- Microcode address/data pairs require ordered writes and hardware-specific handshakes. Offset mistakes may corrupt firmware load, cache base programming, or scratch/bootload state.
- CAC, SPM, SQ debug, and DIDT paths are diagnostic or power-management oriented and may be sampled or modified while hardware is active. Incorrect register definitions can produce misleading counters, over-throttle/under-throttle blocks, or disturb wave/debug state.
- The final chunk ends at the file `#endif`; there is no following chunk for this source file. The merged per-file report should note that this slice closes the header.

## Test Signals

Useful validation for this generated header and its consumers includes:

- Build AMDGPU configurations that include GC 10.1.0 support; missing or renamed macros should surface as compile failures in register-table, graphics, SDMA, RLC, VM, virtualization, or debug code.
- Mechanically compare the full header against the authoritative GC 10.1.0 register database, checking offset values, `_BASE_IDX` values, address-block boundaries, and intentional alias symbols.
- Cross-check each `mm*` register used by code with the matching shift/mask header for GC 10.1.0, especially CP/RLC/SDMA/GCVM/GPU_IOV/CAC/DIDT registers.
- Exercise boot, firmware loading, ring initialization, graphics queues, SDMA queues, MES paths, suspend/resume, GPU reset, and SR-IOV VF reset/enable flows on GC 10.1.0 hardware.
- Validate register dumps for CP/RLC/SDMA microcode address/data windows, MES apertures, GPU_IOV state, GCVM VF windows, PCIe ATS controls, and active function IDs against known-good hardware traces.
- Run profiling and telemetry checks that read SPM sample-delay registers, CAC accumulators/weights/overrides, SQ wave debug state, and DIDT counters without producing access faults or inconsistent decoded output.
- Watch for kernel logs indicating MMIO faults, ring test failures, firmware load failures, SDMA VM context failures, VM/IOMMU/ATS faults, stuck virtual resets, lost GPU_IOV interrupts, repeated doorbell-status errors, and abnormal power-throttling behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of the final direct-GC register group, including the `mmCGTS_SA0_WGP00_CU1_SIMD0_CTRL_REG` offset line immediately before this range. This chunk resumes at that symbol's `_BASE_IDX`, completes the remaining CGTS/CGTT direct offsets, covers the hypervisor, SDMA, GCVM, CAC, SPM, SQ, and DIDT address blocks, and closes `gc_10_1_0_offset.h` with `#endif`.
