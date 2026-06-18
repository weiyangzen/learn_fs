# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_sh_mask.h lines 7371-7666

## Scope And Purpose

This chunk is the final section of the generated AMDGPU VCN 5.0.0 shift/mask header. It defines C preprocessor constants for UVD/VCN memory-check interrupt status and acknowledge registers, then closes the `_vcn_5_0_0_SH_MASK_HEADER` guard. The source is data-only: it has no executable C logic, but it is still part of the hardware ABI used by VCN 5.0 and JPEG 5.0 driver code to decode or compose 32-bit indirect register values.

The chunk starts in the middle of the `UVD_MEMCHECK_VCPU_INT_STAT` field definitions and then covers the full `UVD_MEMCHECK_VCPU_INT_ACK`, `UVD_MEMCHECK2_SYS_INT_STAT`, `UVD_MEMCHECK2_SYS_INT_ACK`, `UVD_MEMCHECK2_VCPU_INT_STAT`, and `UVD_MEMCHECK2_VCPU_INT_ACK` macro groups. The matching offsets live in `vcn_5_0_0_offset.h`: `ixUVD_MEMCHECK_VCPU_INT_STAT` is `0x0138`, `ixUVD_MEMCHECK_VCPU_INT_ACK` is `0x0139`, `ixUVD_MEMCHECK2_SYS_INT_STAT` is `0x0140`, `ixUVD_MEMCHECK2_SYS_INT_ACK` is `0x0141`, `ixUVD_MEMCHECK2_VCPU_INT_STAT` is `0x0142`, and `ixUVD_MEMCHECK2_VCPU_INT_ACK` is `0x0143`.

## Important APIs, Types, And Functions

The exported interface is entirely macro based. There are no functions, structs, enums, global variables, or inline helpers in this range. The macro naming convention is the generated AMD register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already shifted one-bit mask for that field.

`UVD_MEMCHECK_VCPU_INT_STAT` exposes VCPU-visible memory-check error status bits for the first memory-check bank. The beginning of this register is defined just before the chunk; this slice completes the higher fields: `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, and `IT_RD`, plus the full mask table for all status fields. It uses paired low/high error bits for `RE`, `IT`, `MP`, `DB`, `DBW`, `CM`, `MIF_REF`, `VCPU`, `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, and `IT_RD`. `IT_RD` is sparse and occupies bits 30 and 31.

`UVD_MEMCHECK_VCPU_INT_ACK` mirrors the same first-bank VCPU bit layout for acknowledge operations. Its fields are named with `_ACK` rather than `_ERR`, but their shifts and masks line up with the corresponding `UVD_MEMCHECK_VCPU_INT_STAT` status bits. This pairing allows interrupt or diagnostic paths to acknowledge exactly the VCPU-visible error bits they observed in the first-bank status register.

The `UVD_MEMCHECK2_*` groups describe the second memory-check bank for read-side and extended memory clients. The covered sources are `CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, `LBSI_RD`, `RBC_RD`, `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, and `PREF`, again with low/high variants for status and acknowledge fields.

## Register Layout Details

`UVD_MEMCHECK2_SYS_INT_STAT` and `UVD_MEMCHECK2_SYS_INT_ACK` share one system-visible layout. Their low fields occupy bits 0 through 11 for `CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, and `LBSI_RD`, then skip bits 12 through 15. `RBC_RD` uses bits 16 and 17. The later extended clients are placed at high bits: `MIF_BSP2` at bits 22 and 23, `MIF_BSP3` at 24 and 25, `MIF_SCLR` at 26 and 27, `MIF_SCLR2` at 28 and 29, and `PREF` at 30 and 31.

`UVD_MEMCHECK2_VCPU_INT_STAT` and `UVD_MEMCHECK2_VCPU_INT_ACK` share a different VCPU-visible layout. They match the system layout through `RBC_RD` at bits 16 and 17, but place `MIF_BSP2` and later fields at bits 18 through 27 instead of bits 22 through 31. This leaves bits 28 through 31 unused by the second-bank VCPU status/ack macros in this VCN 5.0.0 header.

That system-versus-VCPU layout difference is the most important detail in this chunk. The field names are similar across registers, but the masks are not interchangeable between `UVD_MEMCHECK2_SYS_INT_*` and `UVD_MEMCHECK2_VCPU_INT_*` for `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, and `PREF`.

## Control Flow

There is no direct control flow in the header. Runtime flow is imposed by AMDGPU VCN/JPEG code that includes `vcn_5_0_0_offset.h` and `vcn_5_0_0_sh_mask.h`, then combines offsets, masks, and SOC15-style register helpers.

A typical use pattern is:

1. Hardware latches a memory-check error into a `*_INT_STAT` register.
2. Driver interrupt, reset, diagnostics, or firmware-facing code reads the appropriate indirect register.
3. The code tests source-specific masks from this header to identify which memory client reported a low or high bound error.
4. The handler writes the matching `*_INT_ACK` mask bits to the acknowledge register for the same bank and visibility domain.

The ack/status pairing is local to each register family. First-bank VCPU status bits pair with `UVD_MEMCHECK_VCPU_INT_ACK`; second-bank system bits pair with `UVD_MEMCHECK2_SYS_INT_ACK`; second-bank VCPU bits pair with `UVD_MEMCHECK2_VCPU_INT_ACK`.

## State And Persistence Behavior

The macros themselves are compile-time constants and hold no software state. They describe persistent state in hardware registers inside the VCN/UVD block. Status bits represent latched hardware fault state, and acknowledge bits describe the write interface used to clear or acknowledge that latched state. The exact write semantics are determined by the hardware register specification; this header only names bit positions and masks.

The register contents persist while the VCN block remains powered and configured. They may be reset by VCN block reset, GPU reset, power-gating transitions, suspend/resume reinitialization, firmware reload, or explicit writes from the driver. Any code that saves, restores, polls, or clears VCN memory-check state must use the offset header and this shift/mask header as a pair for the active VCN generation.

## Dependencies And Integration Points

The direct dependency is the companion `vcn_5_0_0_offset.h` header, which supplies the register offsets for the macro groups described here. The VCN 5.0 generation driver files include both headers, including `amdgpu/vcn_v5_0_0.c`, `amdgpu/vcn_v5_0_1.c`, `amdgpu/vcn_v5_0_2.c`, and JPEG 5.0 files such as `jpeg_v5_0_0.c`, `jpeg_v5_0_1.c`, and `jpeg_v5_0_2.c`.

The integration point is the AMDGPU register-access layer and VCN/JPEG IP block lifecycle: hardware initialization, firmware bring-up, interrupt handling, diagnostics, reset, and power-management flows can all depend on these constants if they touch memory-check status or acknowledge registers. Similar macro groups exist in VCN 3.x, 4.x, and 5.3 headers, but those files are generation-specific contracts and should not be mixed with this VCN 5.0.0 header without checking the matching offsets and bit layout.

## Risks And Edge Cases

The main risk is treating visually similar register groups as identical. In this chunk, `UVD_MEMCHECK2_SYS_INT_*` and `UVD_MEMCHECK2_VCPU_INT_*` diverge for the extended clients after `RBC_RD`; using a system mask against a VCPU register, or the reverse, would test or acknowledge the wrong bit.

Sparse high-bit fields are another review hazard. `UVD_MEMCHECK_VCPU_INT_STAT` and `UVD_MEMCHECK_VCPU_INT_ACK` place `IT_RD` at bits 30 and 31 after `SRE` at bits 24 and 25. The second-bank system registers also reserve gaps before `RBC_RD` and before `MIF_BSP2`. These gaps should be preserved rather than compacted by hand.

Because this is generated hardware-description data, small textual changes have large behavioral impact. A shifted mask can hide memory-check faults, create stuck interrupts, acknowledge unrelated latched events, or break firmware/driver synchronization. Review should compare changes against generated AMD register definitions or hardware specifications, not infer correctness from neighboring names alone.

## Test Signals

There are no unit tests for this macro-only header. Useful validation signals are hardware and integration oriented:

- A kernel build including VCN 5.0 and JPEG 5.0 implementation files catches missing or renamed macros.
- VCN/JPEG bring-up should complete without interrupt storms or stuck memory-check status after reset.
- Fault-injection or diagnostic testing should show expected bits in `UVD_MEMCHECK_VCPU_INT_STAT`, `UVD_MEMCHECK2_SYS_INT_STAT`, and `UVD_MEMCHECK2_VCPU_INT_STAT`.
- Acknowledge paths should clear the matching status bits using the corresponding `*_INT_ACK` masks, especially for the second-bank fields whose system and VCPU masks differ.
- Suspend/resume, power-gating, and GPU-reset tests should verify that VCN state is reinitialized and stale memory-check interrupts do not remain latched.
