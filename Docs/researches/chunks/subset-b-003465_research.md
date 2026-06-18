# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_sh_mask.h lines 9715-10919

## Scope And Purpose

This chunk is the tail of the generated VCN 4.0.3 shift/mask header for AMDGPU's VCN/UVD hardware block. It provides C preprocessor constants for register fields rather than executable code. The constants describe how to pack and decode 32-bit register values for three repeated JPEG/JMI decode address blocks, context-indirect VCN clock-gating and scratch registers, LMI adapter indirect CRC and byte-swap controls, and memory-check interrupt status/acknowledge registers.

The chunk begins at the end of the `aid_uvd0_uvd_jmi5_uvd_jmi_dec` block, then contains complete `aid_uvd0_uvd_jmi6_uvd_jmi_dec` and `aid_uvd0_uvd_jmi7_uvd_jmi_dec` blocks. It then switches to `uvdctxind` and `lmi_adp_indirect` address blocks before closing the header guard. The companion offset header `vcn_4_0_3_offset.h` supplies the register offsets, while this file supplies the field positions and masks used by driver register helpers.

There are no functions, structs, enums, or local variables here. The practical API is a hardware description contract: driver code can include this generation-specific header and use symbolic field names such as `UVD_JMI7_UVD_JMI_ATOMIC_CNTL__ATOMIC_SW_GATE_MASK` or `UVD_MEMCHECK2_SYS_INT_STAT__PREF_HI_ERR_MASK` instead of open-coded shifts.

## Register Field Groups

The `UVD_JMI5`, `UVD_JMI6`, and `UVD_JMI7` groups describe per-JPEG/JMI decoder memory-interface controls. Each block has the same shape: JPEG decoder prefetch control, JRBC and JPEG LMI arbitration controls, drop controls, VMID assignment registers, 64-bit BAR low/high halves for ring buffers, indirect buffers, JPEG read/write, preempt fences, and atomic write targets, plus JMI decode swap and atomic control registers. Common fields include `ARB_RD_WAIT_EN`, `ARB_WR_WAIT_EN`, read/write max burst fields, `RD_SWAP`/`WR_SWAP`, JPEG/JRBC read and write drop bits, VMID nibbles for command and memory traffic, and 32-bit halves of 64-bit addresses.

The JMI decode swap fields are two-bit memory-controller swap controls for ring-buffer, indirect-buffer, memory-read, memory-write, preempt, and JPEG traffic. The atomic control fields cover arbitration wait, maximum burst, write drop, write clamping, urgency, software gating, UVD-side swap, and memory-controller swap. Because these three blocks are parallel instances, consumers should treat the numeric instance prefix as part of the register identity and not collapse them into one shared macro set.

The `uvdctxind` group defines context-indirect control registers. `UVD_CGC_MEM_CTRL`, `UVD_CGC_MEM_DS_CTRL`, and `UVD_CGC_MEM_SD_CTRL` expose light-sleep, deep-sleep, and shutdown enables for VCN subblocks such as LMI_MC, MPC, MPRD, WCB, UDEC_RE/CM/IT/DB/MP, SYS, VCPU, MIF, LCM, MMSCH, and MPC1. `UVD_CGC_MEM_CTRL` also includes `LS_SET_DELAY` and `LS_CLEAR_DELAY` timing fields. `UVD_CGC_CTRL2` controls dynamic OCLK/RCLK ramp behavior and the gater divider. `UVD_SW_SCRATCH_00` through `UVD_SW_SCRATCH_15` are full-width scratch registers with a single `DATA` field. `UVD_IH_SEM_CTRL` defines interrupt-handler and semaphore stall/clean bits plus `IH_VMID`, `IH_USER_DATA`, and `IH_RINGID` metadata fields.

The `lmi_adp_indirect` group starts with `UVD_LMI_CRC0` through `UVD_LMI_CRC15` register definitions. Each CRC register exposes one full-width `CRC32` field and is intended for LMI data-path validation or diagnostics. `UVD_LMI_SWAP_CNTL2` then defines two-bit swap controls for SCPU read/write, CENC, and FBC key traffic, plus a wider `ATOMIC_MC_SWAP` field.

The memory-check groups describe error enable, status, and acknowledge bit layouts for system-visible and VCPU-visible VCN memory-check paths. `UVD_MEMCHECK_SYS_INT_EN` and `UVD_MEMCHECK_VCPU_INT_EN` use one enable bit per source, spanning base decoder clients (`RE`, `IT`, `MP`, `DB`, `DBW`, `CM`, `MIF_REF`, `VCPU`, `MIF_DBW`, `MIF_CM_COLOC`, `MIF_BSP0`, `MIF_BSP1`, `SRE`, `IT_RD`) and extended read/client sources (`CM_RD`, `DB_RD`, `MIF_RD`, `IDCT_RD`, `MPC_RD`, `LBSI_RD`, `RBC_RD`, `MIF_BSP2`, `MIF_BSP3`, `MIF_SCLR`, `MIF_SCLR2`, `PREF`). The first-generation status and ack registers expose low/high pairs for the base sources. The `UVD_MEMCHECK2_*` registers expose low/high pairs for the extended read/client sources.

An important layout detail is that `UVD_MEMCHECK2_SYS_INT_STAT` and `UVD_MEMCHECK2_SYS_INT_ACK` place `MIF_BSP2` and later fields at bits 22 through 31, while `UVD_MEMCHECK2_VCPU_INT_STAT` and `UVD_MEMCHECK2_VCPU_INT_ACK` place those same named sources at bits 18 through 27. This generation-specific asymmetry is part of the hardware ABI and should not be normalized by shared helper code.

## Important APIs, Types, And Functions

This chunk exports only macros of the generated AMD register form:

- `<REGISTER>__<FIELD>__SHIFT` is the shift count for the field.
- `<REGISTER>__<FIELD>_MASK` is the already-shifted 32-bit mask for the field.

The macros are normally paired with offsets from `vcn_4_0_3_offset.h`, including `regUVD_JMI5_*`, `regUVD_JMI6_*`, and `regUVD_JMI7_*` entries for the JMI decode blocks and `ixUVD_CGC_MEM_CTRL`, `ixUVD_SW_SCRATCH_00` through `ixUVD_SW_SCRATCH_15`, `ixUVD_IH_SEM_CTRL`, `ixUVD_LMI_CRC*`, `ixUVD_MEMCHECK_SYS_INT_EN`, `ixUVD_MEMCHECK_SYS_INT_STAT`, `ixUVD_MEMCHECK_SYS_INT_ACK`, `ixUVD_MEMCHECK_VCPU_INT_EN`, `ixUVD_MEMCHECK_VCPU_INT_STAT`, `ixUVD_MEMCHECK_VCPU_INT_ACK`, `ixUVD_MEMCHECK2_SYS_INT_STAT`, `ixUVD_MEMCHECK2_SYS_INT_ACK`, `ixUVD_MEMCHECK2_VCPU_INT_STAT`, and `ixUVD_MEMCHECK2_VCPU_INT_ACK`.

No type checking is provided by the header. Callers must use the masks with the correct offset, instance, and register-access path. Full-width `0xFFFFFFFFL` fields identify registers where the entire 32-bit value is payload, such as scratch data, CRC32 values, and low/high halves of 64-bit BAR addresses.

## Control Flow

There is no runtime control flow in this file. Runtime flow exists in the driver and firmware-facing paths that consume these masks:

1. VCN initialization or resume code programs clock-gating, memory light-sleep/deep-sleep/shutdown, swap, VMID, BAR, and atomic behavior by composing register values from these masks.
2. Command submission and JPEG/JRBC paths use the JMI instance registers to point hardware at ring buffers, indirect buffers, JPEG read/write buffers, preempt fences, and atomic write memory.
3. Hardware sets memory-check status bits when protected memory clients report low/high or source-specific faults.
4. Interrupt, diagnostic, or recovery code reads the matching status register, decodes the active bits with this header's masks, and writes the corresponding ack register bits to clear or acknowledge latched state.
5. Scratch and CRC registers provide side channels for firmware/driver handoff or data-path checking, depending on the active VCN firmware and test mode.

The status and ack registers are intentionally paired within each bank, but fields should not be copied between `SYS`, `VCPU`, `MEMCHECK`, and `MEMCHECK2` banks without checking the exact mask definitions.

## State And Persistence Behavior

The macros themselves persist no state. They describe hardware state in VCN memory-mapped or indirect registers. BAR low/high registers persist programmed addresses until rewritten or until the VCN block is reset or power-gated. VMID, swap, arbitration, burst, drop, prefetch, atomic, and clock-gating fields similarly represent live hardware configuration and must be restored during block bring-up, suspend/resume, GPU reset, or power-management transitions that lose register state.

Memory-check status bits are latched hardware error state. They remain visible until the appropriate acknowledge path is used, subject to the hardware's write-acknowledge semantics. Interrupt enable bits determine which sources can signal the system or VCPU paths and are distinct from the status bits. Scratch registers are mutable firmware/driver state and should be treated as volatile across reset or firmware reinitialization unless a higher-level protocol explicitly preserves them.

## Dependencies And Integration Points

The direct dependency is the companion VCN 4.0.3 offset header in the same directory. It maps the symbolic register names to offsets and base-index metadata; this shift/mask header completes the register description. Both headers are generated hardware description inputs used by AMDGPU IP-version code through SOC15/AMDGPU register access helpers.

Integration points include VCN 4.x block initialization, JPEG ring setup, command processor/JRBC setup, preemption fence programming, VMID/address programming, power and clock-gating code, memory-check interrupt handling, GPU reset, suspend/resume, and diagnostic register dumping. Similar field names appear in VCN 4.0.0, VCN 3.x, and older UVD headers, but those sibling headers are generation-specific and can differ in instance count, bit positions, or subblock names.

The `uvdctxind` and `lmi_adp_indirect` address blocks imply indirect access paths rather than ordinary direct MMIO in all contexts. Driver code must use the register helper appropriate for the offset namespace; using a direct helper with an indirect offset, or mixing a JMI direct register offset with an indirect `ixUVD_*` offset, would program the wrong hardware location.

## Risks And Edge Cases

The main risk is hardware ABI drift. A single wrong shift or mask can route a JPEG/JRBC memory transaction through the wrong VMID, program a bad BAR half, swap data incorrectly, drop reads or writes unexpectedly, or acknowledge the wrong memory-check source. The repeated JMI5/JMI6/JMI7 blocks are visually similar, which makes copy/paste or generated-source errors hard to spot by inspection.

The memory-check layouts have sparse fields and bank-specific differences. In particular, extended `MEMCHECK2` system and VCPU status/ack registers do not use identical high-bit layouts for all sources. Generic helper code should use bank-specific masks rather than deriving one bank from another.

Clock-gating and memory sleep/shutdown masks are power-management sensitive. Enabling the wrong subblock sleep field or using the wrong delay field can cause hangs, lost firmware communication, or wakeup timing problems that may only reproduce under runtime power management, suspend/resume, or reset stress.

Ack register writes may have side effects such as write-one-to-clear or write-one-to-acknowledge behavior; this header names the bits but does not document the write semantics. Read/modify/write patterns should be checked against the hardware programming guide or existing AMDGPU usage.

## Test Signals

There are no direct unit tests for this generated header. Useful validation signals are hardware and integration oriented:

- A kernel build for AMDGPU VCN 4.0.3 users catches missing or renamed macros and include mismatches.
- VCN/JPEG firmware bring-up, ring tests, decode tests, and preemption tests should pass without ring buffer address, VMID, or swap-related failures.
- Runtime power management, suspend/resume, and GPU reset tests should verify that clock-gating and memory sleep/shutdown state is restored and does not cause VCN hangs.
- Memory-check fault injection or diagnostic tests should show expected bits in `UVD_MEMCHECK*_INT_STAT` and clear them through the matching `UVD_MEMCHECK*_INT_ACK` masks.
- Register dumps compared against AMD's generated register specification should preserve the JMI5/JMI6/JMI7 instance separation and the `MEMCHECK2` system-versus-VCPU bit-position differences.
