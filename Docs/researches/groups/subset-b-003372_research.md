# Research: subset-b-003372

This grouped report covers generated AMDGPU SDMA0 4.x register-definition headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_default.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_offset.h

## Purpose
`sdma0_4_0_offset.h` defines the SDMA0 4.0 register-address map as word offsets from the SDMA0 register block base, documented in the file as base address `0x4980`. It is the address half of the SDMA0 4.0 register ABI: code combines these `mmSDMA0_*` offsets and `_BASE_IDX` selectors with AMDGPU register access helpers to read or write the right MMIO locations.

## Important APIs, Types, and Functions
There are no functions or types. The interface is 518 `mm...` macros: each register gets an offset macro and a corresponding `_BASE_IDX`, almost always `0`. The map starts with public engine controls (`UCODE_ADDR` at `0x0000`, `UCODE_DATA` at `0x0001`, VM context controls, `VF_ENABLE`, register-type metadata, power/clock/control registers, status and EDC registers), then moves through UTCL1, physical address, perf, trust/IOV, and finally queue contexts. Queue address ranges are structured: GFX registers begin at `0x0080`, PAGE at `0x00e0`, RLC0 at `0x0140`, and RLC1 at `0x01a0`. Each queue block defines ring base/read/write pointers, write-pointer polling, IB controls, doorbell, status/logging, watermarks, CSA, preempt, AQL, minor pointer update, and mid-command data/cntl registers.

## Control Flow and State
The header has no control flow. Its ordering and numeric spacing encode hardware state layout. Gaps in the sequence are meaningful reserved or unlisted hardware addresses, so consumers must not infer dense arrays except where the hardware block is explicitly repeated.

## Persistence and Dependencies
The offsets persist in compiled code wherever register access macros are expanded. They depend on matching generated headers: `sdma0_4_0_default.h` supplies reset values for the same names, and `sdma0_4_0_sh_mask.h` supplies field definitions. Downstream dependencies are AMDGPU SDMA engine setup, debugfs/register dumps, firmware load code, VM fault and UTCL1 diagnostics, power management, and queue/ring scheduling code.

## Integration Points, Risks, and Test Signals
Integration risks are high because an incorrect offset can write a valid but wrong register. `VF_ENABLE` at `0x000a`, `PHASE2_QUANTUM` at `0x004f`, and the PAGE block from `0x00e0` through `0x0129` are present in 4.0 and absent from the 4.1 offset header in this subset, so cross-version include mistakes are especially dangerous. Test signals include MMIO traces showing firmware writes to `UCODE_*`, successful ring initialization at the expected GFX/PAGE/RLC offsets, correct doorbell/rptr/wptr behavior, clean GPU reset and resume, and register dumps whose addresses match the SDMA 4.0 hardware specification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_sh_mask.h

## Purpose
`sdma0_4_0_sh_mask.h` defines bit positions and bit masks for SDMA0 4.0 registers. It is the field-level hardware contract used when driver code constructs, modifies, decodes, or logs SDMA register values. It complements the 4.0 offset header, which locates each register, and the 4.0 default header, which records baseline values.

## Important APIs, Types, and Functions
There are no functions or data types. The API is 1,567 preprocessor definitions with the generated naming pattern `SDMA0_REGISTER__FIELD__SHIFT` and `SDMA0_REGISTER__FIELD_MASK`. Major field families include VM controls (`VM_CNTL`, `VM_CTX_*`, `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `VF_ENABLE`), context/public register type bitmaps, SDMA power and clock control, global `CNTL` interrupt/preemption/UTC controls, copy-engine tuning in `CHICKEN_BITS`, GB address configuration, status registers, phase quantum scheduling, power-gating FSM fields, EDC counters, atomic controls, UTCL1 redo/watermark/read/write/invalidate/XNACK/page fields, relaxed ordering controls, physical address decode, perf counters, MMHUB trust levels, IOV violation logging, and ULV controls.

## Control Flow and State
This file has no runtime control flow, but it defines how runtime code safely touches hardware state. The masks describe which bits are writable or readable for each behavior: queue enablement, ring size, swap mode, rptr writeback, VMID/privilege, IB enable/switching, doorbell enable/capture, context status, write-pointer update failures, watermarks, preemption, AQL, and mid-command replay state. GFX, PAGE, RLC0, and RLC1 queue blocks repeat the same field schema, which allows the driver to apply common logic to separate SDMA contexts while still using explicit register names.

## Persistence and Dependencies
The macros are compile-time constants, but the state they encode is persistent hardware state in SDMA registers. The header depends on the SDMA 4.0 register database and must match `sdma0_4_0_offset.h` exactly. Driver code often combines these masks with helpers such as field-preparation or read-modify-write macros; wrong masks can preserve, clear, or set unrelated hardware bits.

## Integration Points, Risks, and Test Signals
Integration points span the whole SDMA driver: firmware loading, VM/TLB invalidate handling, ring/IB setup, preemption, AQL queues, doorbells, power gating, SR-IOV, error reporting, and performance monitoring. Risks include truncated address fields (`*_ADDR_LO` fields commonly start at bit 2 or 5), incorrect VMID or privilege fields causing memory isolation failures, bad UTCL1 invalidate/XNACK masks causing hangs after VM faults, and status-mask drift that hides real idle or fault conditions. Because this is a 4.0-only field file, using it with 4.1 offsets can expose fields such as `VF_ENABLE`, `PHASE2_QUANTUM`, and PAGE queue fields that do not exist in the 4.1 headers read for this item. Test signals include field-level register programming audits, GPU VM fault/invalidation tests, SDMA copy/fill with multiple VMIDs, doorbell stress, ring preemption, AQL packet execution, perf counter selection, SR-IOV violation logging, and suspend/resume power-gating tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_1_default.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_1_default.h

## Purpose
`sdma0_4_1_default.h` is the generated default-value header for the SDMA0 4.1 register block. It records reset or baseline values for the SDMA0 4.1 hardware revision and is intended to be used with the matching 4.1 offset map and compatible shift/mask definitions when initializing or validating SDMA state.

## Important APIs, Types, and Functions
There are no callable APIs or types. The file exposes 216 `_DEFAULT` macros. The macro surface covers SDMA microcode, VM context, public/context register classification, MMHUB, power/clock/control, GB address config, status, EDC, atomics, UTCL1, relaxed ordering, physical address, perf, trust/IOV, ULV, EA double-bit address registers, and queue defaults for GFX, RLC0, and RLC1. Compared with the 4.0 default header, this 4.1 file omits `mmSDMA0_VF_ENABLE_DEFAULT`, `mmSDMA0_PHASE2_QUANTUM_DEFAULT`, and the entire `mmSDMA0_PAGE_*_DEFAULT` queue block. It also updates revision-sensitive defaults such as `mmSDMA0_VERSION_DEFAULT` to `0x00000401`, `mmSDMA0_POWER_CNTL_DEFAULT` to `0x4003c050`, and `mmSDMA0_PUB_REG_TYPE2_DEFAULT` to `0x0fc66880`.

## Control Flow and State
The header has no executable logic. Its control significance comes from revision selection: including this file tells the rest of the driver that the SDMA0 instance follows the 4.1 default register contract. Hardware state described here includes initial queue disabled state, default context status values, write-pointer polling defaults, address-zero defaults, UTCL1 watermark/status defaults, and power-management defaults.

## Persistence and Dependencies
The macros persist as compiled constants in whatever ASIC table or init path includes them. The file depends on `sdma0_4_1_offset.h` for register locations and on compatible field definitions, typically the SDMA 4.x shift/mask contract. It integrates with AMDGPU SDMA setup, firmware loading, ring bring-up, GPU reset, power management, and diagnostic register dumps.

## Integration Points, Risks, and Test Signals
Main risks are revision mixups and silent generated-value drift. If 4.0 defaults are applied to 4.1 hardware, code may assume a PAGE queue or `PHASE2_QUANTUM` register that the 4.1 offset/default headers do not define. If 4.1 defaults are applied to 4.0 hardware, SDMA power and public-register type defaults may not match expected reset behavior. Test signals include successful SDMA engine discovery reporting version 4.1, ring tests for GFX/RLC0/RLC1 only, no attempts to program missing PAGE queue defaults, firmware load and queue scheduling success, stable suspend/resume with the 4.1 power default, and clean register-dump diffs against SDMA 4.1 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_1_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_1_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_1_offset.h

## Purpose
`sdma0_4_1_offset.h` defines the SDMA0 4.1 register offset map. Like the 4.0 offset header, it documents the SDMA0 base address as `0x4980` and provides word offsets plus `_BASE_IDX` selectors for all named registers in this hardware revision.

## Important APIs, Types, and Functions
There are no functions or types. The interface is 430 `mm...` macros. The map starts with microcode, VM context, virtualization reset, public/context register type maps, power/clock/control, status, EDC, atomics, UTCL1, physical address, perf, trust/IOV, ULV, and EA double-bit address registers. Queue blocks are present for GFX beginning at `0x0080`, RLC0 beginning at `0x0140`, and RLC1 beginning at `0x01a0`. The GFX block includes `CONTEXT_CNTL` at `0x0093`; the RLC blocks have the usual ring, IB, doorbell, status, watermark, CSA, preempt, AQL, minor pointer, and mid-command registers.

## Control Flow and State
This header has no control flow. Its numeric layout is the SDMA0 4.1 hardware state layout. `_BASE_IDX` is `0` throughout this file, so the register selection burden is primarily the offset name and the including ASIC register helper. The absence of certain 4.0 entries is part of the state model: `VF_ENABLE` at `0x000a`, `PHASE2_QUANTUM` at `0x004f`, and the PAGE queue block from `0x00e0` to `0x0129` are not defined here.

## Persistence and Dependencies
The offsets persist through compiled register-access code. They depend on `sdma0_4_1_default.h` for reset/default-value alignment and on the appropriate SDMA field mask definitions for bit operations. The header integrates with AMDGPU SDMA setup, queue/ring management, firmware upload, GPU reset paths, register tracing, and diagnostics.

## Integration Points, Risks, and Test Signals
The largest risk is accidental reuse of SDMA 4.0 register lists against this 4.1 map. Such code may compile if it only touches shared names, but fail at runtime if it assumes the PAGE queue or other removed registers exist. Bad offsets can corrupt adjacent SDMA controls, especially in dense queue blocks where ring, IB, doorbell, and status registers are close together. Test signals include version-gated include selection, successful firmware writes through `UCODE_ADDR`/`UCODE_DATA`, GFX/RLC0/RLC1 ring initialization at the expected offsets, no PAGE queue MMIO traffic on 4.1, passing SDMA copy/fill tests, clean GPU reset, and register dumps matching the 4.1 specification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_1_offset.h -->
