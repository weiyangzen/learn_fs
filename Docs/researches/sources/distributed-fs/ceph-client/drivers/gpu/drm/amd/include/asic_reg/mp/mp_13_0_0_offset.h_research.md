# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_0_offset.h

## Purpose

`mp_13_0_0_offset.h` defines MP 13.0.0 register offset macros and matching `_BASE_IDX` selectors. It is the address-side companion to MP 13.0.0 shift/mask headers: callers use these `reg...` constants to identify hardware registers and use separate field macros to interpret or construct register values.

The header maps MP0 and MP1 SMN-decoded mailbox/interrupt registers, MP1 public firmware flag registers, and MPIO public firmware flags for ASIC generation 13.0.0.

## Important APIs, Types, And Macros

This file exports preprocessor constants only; it has no functions, structs, enums, or data objects.

Important macro families:

- `regMP0_SMN_C2PMSG_32` through `regMP0_SMN_C2PMSG_103`: contiguous MP0 SMN offsets from `0x0060` through `0x00a7`.
- `regMP0_SMN_IH_CREDIT`, `regMP0_SMN_IH_SW_INT`, and `regMP0_SMN_IH_SW_INT_CTRL`: MP0 SMN interrupt helper registers at `0x00c1` through `0x00c3`.
- `regMP1_SMN_C2PMSG_32` through `regMP1_SMN_C2PMSG_127`: contiguous MP1 SMN offsets from `0x0260` through `0x02bf`, giving MP1 a larger mailbox range than MP0 in this header.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, `regMP1_SMN_FPS_CNT`, and `regMP1_SMN_PUB_CTRL`: MP1 SMN interrupt/count/control registers from `0x02c1` through `0x02c5`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH31`, with no `EXT_SCRATCH9` definition visible in the sequence: scratch offsets run from `0x0340` through `0x035f` with that documented gap.
- `regMP1_FIRMWARE_FLAGS` and `regMPIO_FIRMWARE_FLAGS`: public CRU firmware flag registers, both at address `0xbee009` but in different address blocks.
- Every `reg...` offset has a corresponding `reg..._BASE_IDX` macro set to `0`.

## Control Flow

There is no runtime control flow. The only structural flow is the `_mp_13_0_0_OFFSET_HEADER` include guard.

At runtime, consuming code supplies control flow by selecting a register macro, resolving its base index through AMDGPU register access helpers, and reading or writing the mapped hardware register.

## State And Persistence Behavior

The header is stateless. It names device register locations whose contents are maintained by the GPU, SMU firmware, and interrupt hardware. Scratch registers and firmware flags may persist for the lifetime of a device/firmware session, but the header does not allocate, cache, or synchronize that state.

## Dependencies And Integration Points

The only direct dependency is the C preprocessor. Integration depends on consistency with:

- `mp_13_0_0_sh_mask.h` for field definitions.
- AMDGPU SMU/MP register access macros that expect `reg...` and `reg..._BASE_IDX` naming.
- Firmware command paths using `C2PMSG` mailboxes.
- Interrupt handlers using `IH_CREDIT`, `IH_SW_INT`, and `IH_SW_INT_CTRL`.
- Firmware status/control code using `FIRMWARE_FLAGS`, `MP1_SMN_PUB_CTRL`, and extended scratch registers.

The `regMP1_FIRMWARE_FLAGS` and `regMPIO_FIRMWARE_FLAGS` address reuse at `0xbee009` is safe only because the address blocks differ. Code that flattens register addresses without preserving address block context could confuse them.

## Risks And Maintenance Notes

Register offsets are ABI-like hardware constants. A wrong value can cause MMIO/SMN accesses to hit an unrelated register, hang firmware communication, lose interrupts, or corrupt scratch/control state. The most important variant-specific risk is confusing MP 13.0.0 with MP 13.0.2: this header includes `regMP1_SMN_PUB_CTRL`, extended scratch registers through `EXT_SCRATCH31`, and `regMPIO_FIRMWARE_FLAGS`, while the MP 13.0.2 offset header in this work item is narrower.

Because all `_BASE_IDX` values are `0`, any future multi-base variant would require careful generator and consumer updates. The absent `EXT_SCRATCH9` macro should be treated as intentional unless confirmed against upstream generation inputs.

## Test Signals

Useful signals include:

- Successful AMDGPU compilation for MP 13.0.0 targets.
- Static comparison of generated offsets against upstream AMD headers.
- SMU mailbox command tests that exercise MP0 and MP1 `C2PMSG` ranges.
- Runtime register access traces confirming MP1 scratch and firmware flag reads use the correct address block.
- Interrupt smoke tests validating `IH_CREDIT`, `IH_SW_INT`, and `IH_SW_INT_CTRL` offsets.
