# Research: subset-b-003350

Grouped research for two AMD OSSSYS register-definition headers. Each file section is bounded by the reconciliation markers required by the research pipeline.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_2_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_2_0_offset.h

## Purpose

`osssys_4_2_0_offset.h` is the OSSSYS 4.2.0 register offset table for AMDGPU SOC15-style register access. It maps symbolic `mm...` register names to offsets within the `osssys_osssysdec` address block, whose documented base address is `0x4280`, and defines a corresponding `*_BASE_IDX` for each register. It contains no executable logic; its job is to provide the address half of the register ABI, while the companion `osssys_4_2_0_sh_mask.h` supplies field masks and shifts.

The table spans IH VMID/PASID LUTs, IH cookie registers, semaphore request inputs, primary and secondary IH ring-buffer registers, retry CAM/version/control/status/performance registers, DSM match controls, interrupt flood/status/diagnostic registers, SEM UTC/MCIF/performance/status/mailbox registers, virtualization function/reset controls, client configuration/remap registers, interrupt drop match registers, SEM response address registers, atomic operation LUT, EDC/chicken controls, and MMHUB integration registers.

## Important APIs, Types, And Macros

This header exports only macros:

- `mmREG` constants define word offsets used by SOC15 register address helpers, for example `mmIH_RB_CNTL 0x0080`, `mmSEM_STATUS 0x0108`, and `mmSEM_ATOMIC_OP_LUT 0x01b2`.
- `mmREG_BASE_IDX` constants are all `0` in this file and identify the base-index slot used by generated SOC15 access machinery.
- IH ring offsets are grouped as ring 0 at `0x0080` onward, ring 1 at `0x008c` onward, and ring 2 at `0x0098` onward, with each ring exposing base, high-base, read pointer, write pointer, and doorbell read pointer registers.
- OSSSYS 4.2.0 adds or exposes offsets not present in older 4.0-style tables, including `mmIH_DOORBELL_RETRY_CAM`, `mmIH_RETRY_CAM_ACK`, `mmIH_RETRY_INT_CAM_CNTL`, `mmIH_MEM_POWER_CTRL`, `mmSEM_MEM_POWER_CTRL`, `mmIH_INT_DROP_CNTL`, `mmIH_INT_DROP_MATCH_VALUE{0,1}`, `mmIH_INT_DROP_MATCH_MASK{0,1}`, and `mmSEM_RESP_UVD_1`.

There are no functions, structs, enums, variables, or inline accessors.

## Control Flow

The header itself has no control flow. Runtime use is visible in `amdgpu/vega20_ih.c`, which includes `oss/osssys_4_2_0_offset.h` and `oss/osssys_4_2_0_sh_mask.h`. That driver:

- Converts offsets such as `mmIH_RB_BASE`, `mmIH_RB_CNTL`, and `mmIH_DOORBELL_RPTR` into concrete register addresses with `SOC15_REG_OFFSET(OSSSYS, 0, ...)`.
- Initializes `amdgpu_ih_regs` for ring 0, ring 1, and ring 2 only when each software ring has a nonzero `ring_size`.
- Reads and writes the computed control register addresses with `RREG32`, `WREG32`, `WREG32_NO_KIQ`, or PSP indirect programming when SR-IOV requires it.
- Uses companion `IH_RB_CNTL` masks/shifts to toggle ring enable, timestamp enable, interrupt enable, and overflow-clear handling.

Thus this offset file participates in runtime control flow by selecting which hardware addresses those consumers touch, but it does not implement the sequencing itself.

## State And Persistence Behavior

The header stores no software state and has no persistence. The offsets name hardware state:

- IH ring base/read/write/doorbell registers point to memory-backed interrupt rings and doorbell update paths.
- IH control/status/flood/drop/last-interrupt registers represent live interrupt handler state, some of which may be sticky until explicitly cleared.
- SEM mailbox/status/UTC/MCIF/response registers represent semaphore subsystem routing, pending requests, and mailbox state.
- Virtualization registers such as active function ID, virtual reset request, client config, and client ID remap affect PF/VF behavior.
- Power/clock control registers can change hardware block power behavior when programmed by consumers.

All persistence semantics are hardware-defined and external to this header.

## Dependencies And Integration Points

The file is coupled to:

- `osssys_4_2_0_sh_mask.h`, which defines field layout for the registers named here.
- SOC15 access helpers (`SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and direct `RREG32`/`WREG32` through precomputed addresses).
- AMDGPU IH implementations, especially `vega20_ih.c`; other ASIC generations have parallel offset files such as `osssys_4_0_offset.h`, `osssys_4_0_1_offset.h`, and `osssys_5_0_0_offset.h`.
- PSP and SR-IOV paths when IH control registers are programmed indirectly rather than through normal MMIO.

The symbolic names and base indexes are part of the generated AMDGPU register namespace. Renaming or relocating macros breaks compile-time consumers even when the numeric offsets are unchanged.

## Risks

- Offset drift is severe: an incorrect numeric offset directs register reads or writes to the wrong hardware register.
- Revision confusion can compile successfully because same-named registers exist in nearby OSSSYS versions but have different offsets or extra registers.
- Ring spacing differences matter: OSSSYS 4.2.0 places ring 1 at `0x008c` and ring 2 at `0x0098`, unlike some 4.0 offset variants where secondary rings start earlier. Copying older assumptions can misprogram retry CAM or ring controls.
- Base-index errors would affect SOC15 address calculation even if offsets are correct.
- The file has no self-checking logic; generated constants require external comparison or hardware tests.

## Test Signals

Relevant signals include:

- Successful build of ASIC code that includes `osssys_4_2_0_offset.h`, particularly `vega20_ih.c`.
- Device probe on OSSSYS 4.2.0-family GPUs reaches IH initialization without MMIO faults or PSP register-programming errors.
- Interrupt ring tests verify ring 0, ring 1, and ring 2 addresses are configured correctly and produce interrupts on the expected ring.
- Overflow and flood handling tests exercise `mmIH_RB_WPTR*`, `mmIH_STATUS`, `mmIH_INT_FLOOD_*`, and `mmIH_INT_DROP_*` paths.
- SR-IOV testing checks PSP indirect programming, active-function state, virtual reset request offsets, and client remap/configuration registers.
- Diffing against AMD generated register headers or upstream Linux AMDGPU headers is the strongest static validation for the numeric table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_2_0_offset.h -->
