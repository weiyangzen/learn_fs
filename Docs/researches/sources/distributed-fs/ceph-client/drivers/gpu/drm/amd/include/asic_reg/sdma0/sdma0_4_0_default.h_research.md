# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_default.h

## Purpose
`sdma0_4_0_default.h` is a generated AMD SDMA0 4.0 register reset/default-value contract. It gives compile-time constants for the expected power-on or programmed baseline values of the SDMA0 engine register block at base address family `sdma0_sdma0dec`. Consumers use these constants together with the matching offset and shift/mask headers to build register-init tables, compare hardware state, and document the intended SDMA engine configuration for GFX, PAGE, RLC0, and RLC1 queues.

## Important APIs, Types, and Functions
There are no C functions, structs, or runtime APIs. The entire interface is preprocessor macros named `mmSDMA0_*_DEFAULT` plus a few shared SDMA macros such as `mmSDMA_POWER_GATING_DEFAULT`, `mmSDMA_PGFSM_CONFIG_DEFAULT`, `mmSDMA_PGFSM_WRITE_DEFAULT`, and `mmSDMA_PGFSM_READ_DEFAULT`. The file contains 260 `_DEFAULT` macros. Important groups include microcode access (`UCODE_ADDR`, `UCODE_DATA`, `UCODE_CHECKSUM`), VM and SR-IOV controls (`VM_CNTL`, `VM_CTX_*`, `ACTIVE_FCN_ID`, `VF_ENABLE`), public/context register classification (`CONTEXT_REG_TYPE*`, `PUB_REG_TYPE*`), power/clock controls, UTCL1 translation-cache controls/status, EDC/error/perf registers, and repeated ring/IB/doorbell/context-state blocks for GFX, PAGE, RLC0, and RLC1.

## Control Flow and State
This header has no executable control flow. Inclusion exposes constants to code that emits MMIO writes or validates register fields elsewhere in the AMDGPU driver. The state represented by the macros is hardware state: SDMA queue enable defaults, write-pointer polling defaults, context status reset bits, interrupt/preemption defaults, default address zeroing for ring/IB/CSA pointers, and initial diagnostic/performance counter values.

## Persistence and Dependencies
The constants are persistent only as compiled driver data. They depend on the AMD register database for SDMA 4.0 and must stay aligned with `sdma0_4_0_offset.h` for addresses and `sdma0_4_0_sh_mask.h` for field interpretation. Integration code usually accesses these registers through AMDGPU MMIO helpers and ASIC-specific SDMA setup paths, not through functions in this header.

## Integration Points, Risks, and Test Signals
Integration points include SDMA firmware loading, ring setup, VM/UTCL1 programming, power-gating setup, SR-IOV visibility, queue preemption, doorbell programming, and debug/perf counter paths. A key 4.0-specific detail is that this file includes defaults for `VF_ENABLE`, `PHASE2_QUANTUM`, and the PAGE queue block; later 4.1 defaults in this subset omit those. Risks are silent because macro values compile cleanly even when wrong: stale generated defaults can leave SDMA powered or clocked incorrectly, program invalid queue defaults, mask reset regressions, or confuse register dumps. Test signals include successful SDMA firmware load, copy/fill/ring tests across GFX/PAGE/RLC queues, suspend/resume with power gating, SR-IOV smoke tests where supported, clean EDC/error counters after reset, and register-dump comparisons against known SDMA 4.0 hardware.
