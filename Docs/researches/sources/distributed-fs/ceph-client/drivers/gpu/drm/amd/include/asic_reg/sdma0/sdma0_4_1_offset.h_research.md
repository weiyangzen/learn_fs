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
