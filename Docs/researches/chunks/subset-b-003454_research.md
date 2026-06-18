# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_3_0_0_sh_mask.h lines 5085-5530

## Scope And Purpose

This chunk is the tail of the generated VCN 3.0.0 shift/mask header for the AMDGPU VCN/UVD block. It defines preprocessor constants for the low-level register bit layout of memory-check interrupt status/acknowledge registers and the final `UVD_IH_SEM_CTRL` register. The companion offset header maps the corresponding VCN 3.0 indirect register names to offsets `ixUVD_MEMCHECK_SYS_INT_EN` through `ixUVD_IH_SEM_CTRL` at `0x0014` through `0x001e`; this file supplies the bit positions and masks used to compose or decode the 32-bit register values.

There is no executable logic in this range. Its purpose is ABI-like: C code in the AMDGPU VCN 3.0 and JPEG 3.0 implementation can include `vcn_3_0_0_sh_mask.h` and use stable symbolic field names instead of hard-coded bit arithmetic when enabling memory-check interrupts, reading fault status, acknowledging latched faults, or configuring interrupt-handler/semaphore metadata.

The chunk begins in the middle of the `UVD_MEMCHECK_SYS_INT_STAT` mask block, then covers the full `UVD_MEMCHECK_SYS_INT_ACK`, `UVD_MEMCHECK_VCPU_INT_EN`, `UVD_MEMCHECK_VCPU_INT_STAT`, `UVD_MEMCHECK_VCPU_INT_ACK`, `UVD_MEMCHECK2_SYS_INT_STAT`, `UVD_MEMCHECK2_SYS_INT_ACK`, `UVD_MEMCHECK2_VCPU_INT_STAT`, `UVD_MEMCHECK2_VCPU_INT_ACK`, and `UVD_IH_SEM_CTRL` definitions before closing the header guard.

## Register Field Groups

The first group maps legacy memory-check system interrupt status and acknowledge bits. `UVD_MEMCHECK_SYS_INT_STAT` and `UVD_MEMCHECK_SYS_INT_ACK` use the same low/high bit pairing for VCN client blocks such as `RE`, `IT`, `MP`, `DB`, `DBW`, `CM`, `MIF_REF`, `VCPU`, `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, and `IT_RD`. Each field has a `__SHIFT` value and a matching one-bit `*_MASK`; low/high status and ack fields occupy the same bit locations, including sparse high bits for `IT_RD` at bits 30 and 31.

`UVD_MEMCHECK_VCPU_INT_EN` is the enable register for routing memory-check events to the VCPU interrupt path. Unlike the status/ack registers, it uses one enable bit per error source rather than low/high pairs. It includes the base sources from the system register and adds read-side or second-set sources such as `CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, `LBSI_RD`, `RBC_RD`, `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, and `PREF`. Bits are sparse: for example `IT_RD_ERR_EN` is bit 15, `RBC_RD_ERR_EN` is bit 24, and `PREF_ERR_EN` is bit 29.

`UVD_MEMCHECK_VCPU_INT_STAT` and `UVD_MEMCHECK_VCPU_INT_ACK` mirror the first memory-check status/ack layout for VCPU-visible latched errors. They expose low/high error or acknowledge bits for `RE`, `IT`, `MP`, `DB`, `DBW`, `CM`, `MIF_REF`, `VCPU`, `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, and `IT_RD`.

The `UVD_MEMCHECK2_*` registers provide the second memory-check status/ack bank for additional read-side and extended memory interfaces. `UVD_MEMCHECK2_SYS_INT_STAT` and `UVD_MEMCHECK2_SYS_INT_ACK` cover `CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, `LBSI_RD`, `RBC_RD`, `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, and `PREF`. Their system-visible bit layout differs from the VCPU-visible layout: the system status/ack registers place `MIF_BSP2` and later fields at bits 22 through 31, while `UVD_MEMCHECK2_VCPU_INT_STAT` and `UVD_MEMCHECK2_VCPU_INT_ACK` place `MIF_BSP2` and later fields at bits 18 through 27. This is an important hardware contract and not a typo to normalize away.

`UVD_IH_SEM_CTRL` defines interrupt-handler and semaphore control fields. Single-bit controls are `IH_STALL_EN`, `SEM_STALL_EN`, `IH_STATUS_CLEAN`, and `SEM_STATUS_CLEAN`; packed metadata fields include `IH_VMID` at bits 4-7, `IH_USER_DATA` at bits 8-19, and `IH_RINGID` at bits 20-27. These masks allow the driver or firmware-facing code to describe how VCN interrupt/semaphore events should be identified and whether status should be cleaned.

## Important APIs, Types, And Functions

This chunk exports only C preprocessor macros. There are no C functions, structs, enums, static data objects, or inline helpers. The API surface consists of names following the generated register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift amount for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted 32-bit mask for the field.

Consumers normally combine these macros with the register offsets from `vcn_3_0_0_offset.h` and AMDGPU/SOC15 register helpers. For example, a write path can clear or set `UVD_MEMCHECK_VCPU_INT_EN__PREF_ERR_EN_MASK`, while a decode path can test `UVD_MEMCHECK2_SYS_INT_STAT__PREF_HI_ERR_MASK` after reading `ixUVD_MEMCHECK2_SYS_INT_STAT`.

## Control Flow

There is no runtime control flow in the header itself. Control flow is implicit in how downstream driver code uses these definitions:

1. Program the relevant memory-check interrupt-enable register using the `*_INT_EN` masks.
2. Hardware latches memory-check low/high or source-specific status bits in the `*_INT_STAT` registers.
3. Driver interrupt or diagnostic code reads the status register, decodes set bits using the matching masks, and chooses an error-handling path.
4. Driver code writes the corresponding `*_INT_ACK` mask bits to acknowledge or clear the latched status.
5. Interrupt-handler/semaphore behavior can be configured through `UVD_IH_SEM_CTRL` fields when the VCN block is initialized or reset.

Because the ack and status layouts are intentionally paired within each bank, any handler using this file should acknowledge exactly the bits it observed in the matching register bank rather than sharing masks between the `MEMCHECK` and `MEMCHECK2` banks blindly.

## State And Persistence Behavior

The macros do not store state, but they describe persistent hardware state in memory-mapped or indirect VCN registers. The status bits represent latched hardware error state until the appropriate acknowledge bits are written. The enable bits persist in the VCN block register file until reset, power-gating, firmware reinitialization, or explicit driver rewrite. `UVD_IH_SEM_CTRL` likewise reflects hardware register state and must be restored as part of VCN block initialization/resume if the block loses power.

The distinction between system interrupt state and VCPU interrupt state matters for persistence: a bit may be visible in a system status/ack register at one bit position and in a VCPU status/ack register at another, especially for the `MEMCHECK2` extended sources. State tracking in higher-level code should treat these as separate register layouts even when the field names refer to the same hardware source.

## Dependencies And Integration Points

The immediate dependency is the companion VCN 3.0 offset header, which defines register addresses for `ixUVD_MEMCHECK_SYS_INT_EN`, `ixUVD_MEMCHECK_SYS_INT_STAT`, `ixUVD_MEMCHECK_SYS_INT_ACK`, `ixUVD_MEMCHECK_VCPU_INT_EN`, `ixUVD_MEMCHECK_VCPU_INT_STAT`, `ixUVD_MEMCHECK_VCPU_INT_ACK`, `ixUVD_MEMCHECK2_SYS_INT_STAT`, `ixUVD_MEMCHECK2_SYS_INT_ACK`, `ixUVD_MEMCHECK2_VCPU_INT_STAT`, `ixUVD_MEMCHECK2_VCPU_INT_ACK`, and `ixUVD_IH_SEM_CTRL`.

The generated header is included by VCN 3.0 generation driver files such as `drivers/gpu/drm/amd/amdgpu/vcn_v3_0.c` and JPEG 3.0 code. Those files integrate the constants with AMDGPU register-access helpers, IP block initialization/reset, interrupt handling, power management, firmware bring-up, and debug paths.

The naming is also cross-generation aligned: similar `UVD_MEMCHECK*` and `UVD_IH_SEM_CTRL` fields appear in VCN 4.x and 5.x headers, sometimes with different offsets or enable-bit positions. This makes the file part of a generation-specific hardware description contract rather than a reusable generic definition.

## Risks And Edge Cases

The primary risk is incorrect bit mapping. These constants encode hardware ABI values; a one-bit shift error can enable the wrong error source, fail to report a real memory-check fault, or acknowledge the wrong latched status. The sparse fields at high bit positions and the differing `MEMCHECK2` system versus VCPU layouts are the most error-prone areas.

Another risk is over-generalizing across VCN generations. Later VCN headers share names but may place extended sources at different offsets or bits. Code should include the header for the active IP version and avoid mixing `vcn_3_0_0` masks with `vcn_4_*` or `vcn_5_*` offsets.

Generated-header churn is also a review risk. Since this file contains no type checking, duplicate-looking blocks can hide accidental copy/paste errors. Changes should be compared against AMD register specifications or an authoritative generated source, not inferred from neighboring masks alone.

For ack registers, callers must understand the hardware write semantics. These macros only name bits; they do not say whether a bit is write-one-to-clear, write-one-to-acknowledge, or has side effects. Incorrect read/modify/write logic could either lose events or leave interrupt status stuck.

## Test Signals

There are no direct unit tests for this header. Useful validation signals are integration and hardware-facing:

- A kernel build that includes `vcn_v3_0.c` and `jpeg_v3_0.c` catches missing or renamed macros.
- VCN firmware bring-up and reset tests should continue without interrupt storms or stuck memory-check status.
- Fault-injection or diagnostic paths that exercise VCN memory-check reporting should show expected low/high source bits in `UVD_MEMCHECK*_INT_STAT` and clear them through the matching `*_INT_ACK` masks.
- Suspend/resume, power-gating, and GPU reset tests should confirm VCN state is reprogrammed and no stale memory-check interrupt bits remain latched.
- Cross-generation review should verify VCN 3.0 code includes `vcn_3_0_0_offset.h` with `vcn_3_0_0_sh_mask.h`, not a sibling generation's mask header.
