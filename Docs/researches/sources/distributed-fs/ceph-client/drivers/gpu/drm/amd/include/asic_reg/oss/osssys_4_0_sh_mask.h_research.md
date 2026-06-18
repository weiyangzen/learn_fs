# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_sh_mask.h

## Purpose

`osssys_4_0_sh_mask.h` is a generated-style AMDGPU ASIC register bitfield header for the OSSSYS 4.0 address block. It defines `__SHIFT` and `_MASK` constants for the Interrupt Handler (IH) and Semaphore (SEM) register fields exposed through the OSSSYS decode block. The file contains no executable functions, types, storage, or inline helpers; it is a compile-time ABI map used by other AMDGPU code to pack, unpack, and update hardware register fields without duplicating bit positions.

The covered register families include VMID-to-PASID lookup tables, interrupt-cookie decoding registers, IH ring buffer configuration/status for rings 0-2, doorbell read pointers, interrupt status and flood/drop diagnostics, client credit and IOV violation logs, SEM clock/UTC/MCIF/performance/status/mailbox controls, virtualization active-function and reset request registers, client ID remap tables, atomic operation lookup fields, EDC/chicken controls, and MMHUB-level integration controls.

## Important APIs, Types, And Macros

This file's public surface is entirely C preprocessor macros:

- `*_SHIFT` macros define least-significant-bit positions for fields passed to AMDGPU register helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.
- `*_MASK` macros define the masked field width in a 32-bit register value.
- `IH_VMID_[0-15]_LUT` and `IH_VMID_[0-15]_LUT_MM` expose 16-bit PASID fields for standard and MM VMID mappings.
- `IH_COOKIE_[0-7]` describes the interrupt cookie payload layout: client/source/ring/VM identifiers, timestamp fragments, PASID source, and 128-bit context ID fragments.
- `IH_RB_CNTL`, `IH_RB_BASE`, `IH_RB_BASE_HI`, `IH_RB_RPTR`, `IH_RB_WPTR`, `IH_RB_WPTR_ADDR_{HI,LO}`, and `IH_DOORBELL_RPTR` describe the primary interrupt ring buffer controls. `IH_RB_CNTL_RING1` and `IH_RB_CNTL_RING2` repeat most of that control layout for secondary rings.
- `IH_STATUS`, `IH_VF_RB*_STATUS*`, `IH_INT_FLOOD_*`, `IH_INT_FLAGS`, and `IH_LAST_INT_INFO*` expose runtime health, overflow, flood/drop, per-client flag, and last-interrupt diagnostics.
- `IH_CLIENT_CFG`, `IH_CLIENT_CFG_INDEX`, and `IH_CLIENT_CFG_DATA` define the indexed client routing table used by PSP/GFX control paths to reroute interrupt clients to specific rings.
- `SEM_*` families describe semaphore subsystem clocking, UTCL2 translation enables, MCIF request crediting, performance counters, idle/status signals, mailbox client mapping, GPU IOV violation logging, response address registers, atomic operation lookup fields, and protection/chicken controls.

There are no C functions or structs here. The effective API contract is macro naming stability and exact bit compatibility with the corresponding hardware generation and offset headers.

## Control Flow

There is no runtime control flow in the header. Runtime behavior appears in consumers:

- `amdgpu/vega10_ih.c` includes `oss/osssys_4_0_offset.h` and this file, maps `mmIH_RB_*` offsets into `amdgpu_ih_regs`, then uses `REG_SET_FIELD(..., IH_RB_CNTL, ...)` to enable/disable interrupt rings, enable timestamping, configure write-pointer overflow handling, set ring size, enable write-pointer writeback, and select memory-client properties.
- `amdgpu/psp_v3_1.c` uses `IH_CLIENT_CFG_DATA` fields to build PSP messages that reroute VMC and UMC interrupt clients to ring 1.
- `amdgpu/psp_v11_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v9.c`, and related SOC15-era IH/PSP code include this register map as part of firmware, interrupt, and KFD integration.
- Newer IH paths such as `ih_v6_0.c`, `ih_v6_1.c`, and `ih_v7_0.c` use same-named OSSSYS fields, especially storm-client list controls, showing the macro naming convention is shared across generated OSSSYS revisions.

The control-flow risk is indirect: a wrong mask or shift silently causes consumers to write the wrong hardware bits.

## State And Persistence Behavior

This file stores no software state and has no persistence behavior. It models hardware state that lives in GPU MMIO registers:

- IH ring buffer state persists in hardware registers and memory-backed ring buffers across driver operations until reset or reprogramming.
- Write pointer writeback fields connect hardware register state with host-visible memory used by interrupt processing.
- Status/flood/violation/error registers represent transient or sticky hardware diagnostic state, often cleared by writing dedicated clear bits such as overflow/flood clear fields.
- VMID/PASID LUTs, active function IDs, virtual reset requests, and client remap/configuration tables affect SR-IOV and virtual-function routing behavior.

The header itself only supplies constants for correctly accessing that state.

## Dependencies And Integration Points

The file depends only on the C preprocessor and include guards, but it is normally paired with OSSSYS offset headers such as `osssys_4_0_offset.h`. Consumers rely on AMDGPU helper macros from the wider driver stack:

- `SOC15_REG_OFFSET(OSSSYS, instance, mmREG)` converts register offset macros into MMIO addresses.
- `RREG32*()` and `WREG32*()` perform reads and writes to the computed addresses.
- `REG_SET_FIELD()` and `REG_GET_FIELD()` use the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming pattern defined here.
- PSP SR-IOV paths use these fields to prepare indirect register programming when direct MMIO writes are not permitted.

The file is part of the AMD ASIC register include tree under `include/asic_reg/oss`, so it must stay synchronized with adjacent generated headers for OSSSYS 4.0 and closely related variants such as `osssys_4_0_1_sh_mask.h`.

## Risks

- Bitfield drift: any incorrect field width, shift, or mask can corrupt unrelated bits in hardware registers and produce interrupt loss, flood misclassification, bad ring setup, or SR-IOV isolation failures.
- Register revision mismatch: using this 4.0 shift/mask file with an offset file or ASIC whose field layout differs can compile cleanly but fail at runtime.
- Ring-specific differences: ring 1 and ring 2 controls omit some ring 0 fields such as ring-0-only interrupt enable behavior in consumers. Treating all rings as identical can write reserved or invalid bits.
- Reserved-bit writes: many registers expose reserved masks; callers should avoid programming unknown fields unless the hardware programming guide requires it.
- Generated-header maintainability: manual edits are hard to validate by inspection and can diverge from AMD source generation inputs.

## Test Signals

Useful validation signals are mostly compile-time and hardware/runtime:

- Full AMDGPU build checks that every `REG_SET_FIELD()` and `REG_GET_FIELD()` reference resolves to matching shift/mask macros.
- Boot/probe on OSSSYS 4.0-family GPUs should initialize IH rings, route PSP/KFD-related interrupts, and receive interrupts without ring overflow or flood storms.
- SR-IOV VF and PF test paths should exercise PSP-mediated IH register programming, active-function fields, virtual reset requests, and client routing.
- Interrupt stress tests should monitor `IH_STATUS`, `IH_RB*_INT_FLOOD_STATUS`, `IH_INT_FLOOD_STATUS`, and write-pointer overflow behavior.
- RAS/PSP/KFD interrupt tests can catch regressions in client ID, ring ID, PASID, and context ID decoding.
- Static comparison against upstream/generated AMD register headers is the best signal for the raw constants.
