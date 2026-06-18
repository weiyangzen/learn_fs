# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_0_0_sh_mask.h lines 1-2536

## Scope

This chunk covers the first 2536 lines of the VCN 2.0.0 shift/mask register header. The file is a generated-style C preprocessor header for AMDGPU VCN/UVD hardware registers: it defines bit positions (`__SHIFT`) and bit masks (`_MASK`) used by driver code to compose, clear, poll, and decode 32-bit MMIO register values. The chunk starts with the copyright/license and include guard, covers 2134 `#define` macros, and ends partway through the `UVD_LMI_SWAP_CNTL` register field list.

There are no functions, structs, enums, or executable control paths in this chunk. Its API surface is the macro namespace exported to AMDGPU VCN 2.0 and JPEG 2.0 implementation files.

## Purpose

The header gives symbolic names to the bit layout of VCN 2.0.0 registers. It separates register addressing from bitfield layout: register offsets live in the paired `vcn_2_0_0_offset.h`, while this file supplies the constants for field extraction and composition. Consumers include `amdgpu/jpeg_v2_0.c` and `amdgpu/vcn_v2_0.c`, which include both the offset and shift/mask headers.

Typical downstream use is:

- build register values with `(value << FIELD__SHIFT) | FIELD_MASK`;
- clear or preserve fields with `reg &= ~FIELD_MASK`;
- test status by masking readback values from `RREG32`;
- program power, clock gating, VMID, interrupt, ring-buffer, JPEG, and memory-interface state through `WREG32`/`WREG32_SOC15` style accessors.

## Register Areas Covered

The chunk is organized by `// addressBlock:` comments and then by register-name comments.

- `uvd0_mmsch_dec` covers the multimedia scheduler block. It defines microcode/SRAM access fields, scheduler runstall/reset/lock fields, interrupt status/ack bits, VF VMID and mailbox fields, non-cacheable window fields, scratch registers, GPU IOV scheduler command/status blocks for slots 0, 1, and 2, context layout fields, VFID FIFO heads/tails, NACK status, and VM busy status.
- `uvd0_jpegnpdec` covers JPEG decode control: request/error/huffman speed bits, ring buffer base/read/write/size fields, decoder interrupt enable/status bits, pitch fields, GFX8/GFX10 tiling and address-mode fields, GPCOM command/data, scratch, and decoder soft reset.
- `uvd0_uvd_jpeg_enc_dec` and `uvd0_uvd_jpeg_enc_sclk_dec` cover JPEG encode interrupt, status, engine control, pitch, luma/chroma bases, GFX10 tiling, GPCOM, clock gating, scratch, and soft reset fields.
- `uvd0_uvd_jrbc_dec` and `uvd0_uvd_jrbc_enc_dec` cover JPEG ring-buffer controller decode/encode rings: RB write/read pointers, RB control, IB size/update, urgent control, conditional-read timers, soft reset, status/error bits, buffer status, preemption command/fence fields, RB size, and scratch.
- `uvd0_uvd_jmi_dec` covers the JPEG memory interface: arbitration wait and burst controls, read/write swap controls, VMIDs for RB/IB/JPEG paths, performance monitor fields, many 64-bit BAR low/high register halves for JPEG/JRBC/EJRBC read/write/preempt/memory paths, JPEG2 VMID/BAR controls, and JMI soft reset/read-return limit.
- `uvd0_uvd_jpeg_common_dec` covers JPEG common reset and interrupt hierarchy: reset status for decode/encode/JRBC/JMCIF blocks, system interrupt enable/status/ack, master interrupt overrun fields, interrupt-handler routing metadata, and JRBBM arbitration drops.
- `uvd0_uvd_jpeg_common_sclk_dec` covers JPEG clock/memory-gating and performance counters: CGC gate/control/status, memory light/deep/shutdown sleep controls for common/decoder/JPEG2/encoder blocks, atomic soft reset, performance bank configuration, event select, and four counter registers.
- `uvd0_uvd_pg_dec` covers VCN power gating and diagnostic state: PGFSM config/status across UVD sub-blocks, global UVD/JPEG power status, PG indirect index/data, harvesting disable bits, dynamic power-gating LMA controls, pause request/ack fields, scratch registers, free counter, DPG VCPU cache BAR/VMID/offset, page-fault status/clear bits, DPG clock/VCPU report, GFX8/GFX10 address config, general counters, and timestamp counter halves.
- `uvd0_uvddec` begins the main decode block. This chunk includes semaphore control, ring 3 pointers/base/size, ring arbitration control, LMI latency control/counters, soft reset status, SPH status, context index/data, UVD CGC gate/status/control/UDEC-status fields, VCPU interrupt route, scratch registers, LMI VCPU cache VMID, LMI control/interrupt/status/VM/perf fields, and the start of LMI byte-swap control.

## Important Macro Families

The primary API pattern is consistent:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field mask in register position.
- Full-width data registers use shift `0x0` and mask `0xFFFFFFFFL`.
- Low halves of 64-bit BARs are named `..._LOW__BITS_31_0_*`; high halves are `..._HIGH__BITS_63_32_*`.
- Ring-buffer base fields often reserve low alignment bits, for example base-low fields begin at shift `0x6`; read/write pointers and sizes commonly begin at shift `0x4`.
- VMID fields are compact 4- or 5-bit fields used to route memory accesses through GPU virtual memory contexts.

Important visible families include:

- `MMSCH_*`: scheduler microcode/SRAM, control, interrupts, SR-IOV/VF context/mailbox, GPU IOV command/status, and scratch/FIFO state.
- `UVD_JPEG_*` and `JPEG_DEC_*`: JPEG decode control, ring, interrupts, tiling, address mode, command, and reset fields.
- `UVD_JPEG_ENC_*` and `JPEG_ENC_*`: JPEG encode interrupts, engine enable/control, base addresses, tiling, GPCOM, clock gating, and reset fields.
- `UVD_JRBC_*` and `UVD_JRBC_ENC_*`: decode/encode ring-buffer controller command submission, IB handling, status/error, timeout, preemption, and scratch fields.
- `UVD_JMI_*` and `UVD_LMI_*`: memory interface arbitration, VMID selection, address BARs, byte swapping, coherency, urgent signaling, performance monitoring, and clean/idle status.
- `JPEG_CGC_*` and `UVD_CGC_*`: clock-gating control/status for JPEG and broader UVD sub-blocks.
- `UVD_PGFSM_*`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_DPG_*`: static/dynamic power gating, power status, DPG local memory access, pause, and diagnostic state.
- `UVD_SYS_INT_*`, `UVD_VCPU_INT_*`, `JPEG_SYS_INT_*`: interrupt enable/status/ack fields for host, firmware, JPEG, VCPU, fault, job, and mailbox paths.

## Control Flow and State Behavior

This chunk contains no runtime control flow. The effective control flow is imposed by driver call sites that include this header:

1. Driver code reads or initializes a register value.
2. It composes desired bitfields using the `__SHIFT` and `_MASK` constants.
3. It writes the resulting value to an MMIO register defined in the paired offset header.
4. It polls or decodes status/ack bits using the same masks.

The constants describe persistent hardware state rather than software-owned state. Register fields affect hardware-visible state such as scheduler locks, VF mailboxes, ring-buffer pointers, interrupt enables/acks, power-gating states, clock-gating gates, VMID routing, BAR addresses, coherency controls, and page-fault status. Persistence is therefore MMIO/device persistence: values remain in hardware registers until reset, power-gating transitions, firmware action, or later driver writes change them. The header itself has no storage and no initialization side effects.

## Dependencies and Integration Points

- Protected by `_vcn_2_0_0_SH_MASK_HEADER`, so it can be included by multiple C units without duplicate macro redefinition within one translation unit.
- Paired with `drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_0_0_offset.h`, which provides register addresses/base indices.
- Included directly by `drivers/gpu/drm/amd/amdgpu/vcn_v2_0.c` and `drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.c`.
- Used with AMDGPU MMIO helpers and SOC15 register macros in implementation code, especially for VCN startup/shutdown, JPEG power gating, ring setup, interrupt handling, and clock/power-gating control.
- Mirrors neighboring generated VCN generation headers (`vcn_1_0_sh_mask.h`, `vcn_2_5_sh_mask.h`, `vcn_3_0_0_sh_mask.h`, and later), so consumers rely on stable naming conventions across ASIC generations.

## Risks

- Bitfield accuracy is critical. A wrong mask or shift silently writes the wrong hardware bits, which can produce GPU hangs, broken media encode/decode, interrupt storms, missed interrupts, memory faults, or failed power transitions.
- Some macro names encode hardware spelling exactly, including misspellings such as `FUNCTINO_ID`; correcting those names casually would break existing generated-name consumers.
- Several fields are full-width and some are partial-width BAR halves; callers must preserve low alignment requirements and split 64-bit addresses correctly.
- Interrupt status/ack/enable families have parallel but not always identical field names. Mixing an enable mask with an ack or status register could clear or enable the wrong event.
- Clock-gating and power-gating fields affect live hardware blocks. Incorrect sequencing around `UVD_CGC_*`, `JPEG_CGC_*`, `UVD_PGFSM_*`, and `UVD_POWER_STATUS` can make subsequent register access unreliable.
- The requested chunk ends before completing `UVD_LMI_SWAP_CNTL`; merge/reconciliation must combine this chunk with the following chunk before treating the whole file as complete.

## Test Signals

Useful validation signals are mostly integration and hardware/driver oriented:

- The kernel build should compile `amdgpu/vcn_v2_0.c` and `amdgpu/jpeg_v2_0.c` without missing macro or redefinition errors.
- Static checks can verify every macro in this header follows the generated naming pattern and that masks fit in 32 bits.
- Register smoke tests should exercise VCN 2.0 initialization, firmware loading, ring setup, suspend/resume, and reset paths.
- Media tests should cover decode and JPEG encode/decode submission, including ring pointer movement, job completion interrupts, and fence completion.
- Power-management tests should cover clock gating, static/dynamic power gating, DPG pause/ack, and resume from low-power states.
- Fault and recovery tests should watch `UVD_PF_STATUS`, `UVD_SYS_INT_STATUS`, `UVD_VCPU_INT_ACK`, and JPEG interrupt status/ack fields for expected transitions.
- Cross-generation regression checks should compare unchanged common fields against adjacent VCN header generations while allowing generation-specific additions/removals.

## Chunk Notes for Merge

This is a partial report for lines 1-2536 only. It should be merged with later chunk reports for the same source file before producing the final source-tree-aligned per-file research document. The next chunk should resume inside the `uvd0_uvddec` address block, completing `UVD_LMI_SWAP_CNTL` and covering the remaining VCN decode/encode register families through the file's closing include guard.
