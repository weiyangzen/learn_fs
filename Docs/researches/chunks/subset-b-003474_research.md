# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_sh_mask.h lines 4758-7370

## Scope And Purpose

This chunk is a large middle section of the generated AMD VCN 5.0.0 shift/mask header. It contains C preprocessor constants that describe bit positions and already-shifted masks for VCN/UVD and JPEG hardware registers. The companion `vcn_5_0_0_offset.h` file supplies the register offsets; this file supplies the bitfield layout used by AMDGPU VCN 5.x and JPEG 5.x driver code to program those registers without hard-coded bit arithmetic.

The range starts just after `UVD_JRBC_SCRATCH0__SCRATCH0_MASK`, then covers the JMI/JPEG memory interface, JPEG common interrupt and memcheck registers, JPEG clock-gating/performance registers, VCN power-gating and dynamic power-gating state, ring-buffer and AGDB controls, MMSCH and UMSCH scheduler registers, VCN MES processor state, S/LMI apertures, context-indirect clock-gating and scratch registers, and the start of the LMI-adapter memory-check register bank. The chunk ends in the middle of `UVD_MEMCHECK_VCPU_INT_STAT`; later lines define the remainder of that register and adjacent ack/memcheck2 fields.

There is no executable logic here. The value of the chunk is as a hardware ABI description: if any `__SHIFT` or `_MASK` value is wrong, driver register writes may affect the wrong field, interrupt handling may acknowledge the wrong source, or firmware bring-up may point hardware at the wrong memory aperture.

## Register Field Groups

The `uvd_uvd_jmi0_uvd_jmi_dec` block defines decode-side JMI and LMI controls. It includes JPEG prefetch gating (`UVD_JPEG_DEC_PF_CTRL`), JRBC/JPEG arbitration and burst/swap controls (`UVD_LMI_JRBC_CTRL`, `UVD_LMI_JPEG_CTRL`), traffic drop bits (`JPEG_LMI_DROP`), VMID selectors for JRBC and JPEG traffic, split low/high 64-bit BAR fields for JPEG read/write, JRBC ring-buffer and indirect-buffer windows, preempt fences, and atomic write BARs. `UVD_JMI_DEC_SWAP_CNTL` and `UVD_JMI_ATOMIC_CNTL*` are especially sensitive because they encode memory-controller byte-swap policy, atomic burst/drop/gating state, and atomic MC/UVD swap fields.

The `uvd_uvd_jmi_common_dec` block covers common memory-interface behavior. It exposes urgent/QoS watermarks and timers (`UVD_JADP_MCIF_URGENT_CTRL`, `UVD_JMI_URGENT_CTRL`, `UVD_JMI_CTRL`), JPEG memcheck safe-address/clamping controls, latency counters and performance monitors, clean-status bits for LMI/JPEG read/write drains, and `UVD_JMI_CNTL__SOFT_RESET_MASK`. JPEG 5.x code uses `UVD_JMI_CNTL__SOFT_RESET_MASK` during JPEG software reset sequencing.

The `uvd_uvd_jpeg_common_dec` and `uvd_uvd_jpeg_common_sclk_dec` blocks describe JPEG reset, interrupt, memory-check, master interrupt, IH, arbitration, clock-gating, memory clock-gating, and performance-bank fields. `JPEG_SYS_INT_EN`, `JPEG_SYS_INT_STATUS`, and `JPEG_SYS_INT_ACK` cover decode JRBC/core/PF/RAS sources; the `*1` variants cover encode-side EJPEG/EJRBC sources. The memcheck registers have separate enable/status/ack banks for decode (`DJRBC0`, `BSFETCH0`, `OBUF0`) and encode (`EJRBC`, `PELFETCH`, `SCALAR`, `BS`) read/write low/high errors. `JPEG_CGC_*` and `JPEG_*_CGC_MEM_CTRL` define clock-gating and memory light/deep sleep controls, while `JPEG_PERF_BANK_*` defines the small JPEG performance-counter interface.

The `uvd_uvd_pg_dec` block is the largest section in this chunk. It covers power status, dynamic power-gating (`UVD_DPG_LMA_CTL`, `UVD_DPG_LMA_DATA`, `UVD_DPG_LMA_MASK`, `UVD_DPG_PAUSE`, `UVD_DPG_LMA_CTL2`), scratch registers, firmware versioning, PF and GPU IOV status, VCPU error detection and instruction-address capture, LMI address-space aperture controls, address config registers, generic performance counters, clock deep-sleep controls, timestamp counter halves, feature and RAS status registers, UMSCH enable/control, JPEG and ring doorbell controls, AGDB controls/masks, ring enable and write-pointer controls, and several ring read/write pointer registers. VCN 5.x driver code uses the `UVD_DPG_PAUSE__NJ_PAUSE_DPG_REQ_MASK` and `UVD_DPG_PAUSE__NJ_PAUSE_DPG_ACK_MASK` fields when entering or leaving dynamic power-gating mode, and uses the ring pointer offsets/masks around ring initialization and submission.

The `uvd_mmsch_dec`, `uvd_vcn_umsch_dec`, and `uvd_vcn_cprs64dec` blocks describe scheduler and embedded-controller state. MMSCH fields include VF VMID/context address/size and mailbox registers. UMSCH fields include MES control, scheduler control, AGDB write pointers, four mailbox/response pairs, spare registers, UTCL1 controls, busy masks, ring base/size/rptr/wptr, master interrupt/IH controls, eight-bit interrupt enable/status/ack/source banks, context ID, and reset/force controls. The CPRS64/MES block resembles a RISC-V machine-state register file: program counter and interrupt routine addresses, MTVEC, control bits, pipe priority, MIE/MIP/MSTATUS/MEPC/MCAUSE/MBADADDR, cycle/time/instret counters, MISA/vendor/arch/implementation/hart IDs, cache operation controls, MTIMECMP, GP registers, local aperture base/mask/control fields, perfcount control, pending interrupt, interrupt data registers, and 16 data-cache aperture descriptors.

The `uvd_vcn_hypdec` block defines hypervisor-facing MES instruction/data base and bounds registers, including aliases such as `VCN_MES_IC_BASE_LO` and `VCN_MES_MIBASE_LO` sharing the same bit layout. The `uvd_slmi_adpdec` block defines eight non-cacheable MMSCH 64-bit BAR windows, VMID packing for those windows, MMSCH and UMSCH LMI status fields, and IOV active-function ID. The `uvdctxind` block defines context-indirect clock-gating memory controls, 16 software scratch registers, `UVD_IH_SEM_CTRL`, and miscellaneous preemption controls. The final `lmi_adp_indirect` portion begins with LMI CRC registers, swap control, and the main `UVD_MEMCHECK_SYS_INT_EN/STAT/ACK`, `UVD_MEMCHECK_VCPU_INT_EN`, and partial `UVD_MEMCHECK_VCPU_INT_STAT` layouts.

## Important APIs, Types, And Functions

This chunk exports only macros. There are no functions, structs, enums, inline helpers, or persistent C objects.

The generated API convention is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit shift for a field within a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned bit mask for that field.
- Split 64-bit registers use `*_LOW__BITS_31_0_*` and `*_HIGH__BITS_63_32_*` fields rather than a C 64-bit type.
- Multi-instance windows are represented as repeated register names, for example `UVD_LMI_MMSCH_NC0_64BIT_BAR_*` through `UVD_LMI_MMSCH_NC7_64BIT_BAR_*`, `VCN_MES_DC_APERTURE0_*` through `VCN_MES_DC_APERTURE15_*`, and `VCN_UMSCH_AGDB_WPTR0` through `VCN_UMSCH_AGDB_WPTR5`.

Consumers combine these macros with register offsets from `vcn_5_0_0_offset.h` and AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, and `SOC15_REG_OFFSET`. Generation-specific users include `amdgpu/vcn_v5_0_1.c`, `amdgpu/vcn_v5_0_2.c`, `amdgpu/jpeg_v5_0_1.c`, and `amdgpu/jpeg_v5_0_2.c`, which include both `vcn_5_0_0_offset.h` and `vcn_5_0_0_sh_mask.h`.

## Control Flow

The header itself has no runtime control flow. The control flow it supports appears in hardware initialization, reset, interrupt, and diagnostics paths:

1. Driver code selects a register offset from `vcn_5_0_0_offset.h`.
2. It composes a 32-bit register value using the `__SHIFT` and `_MASK` definitions from this file.
3. It writes the value to a SOC15 register, indirect register, or DPG SRAM shadow depending on the block and power mode.
4. Hardware updates persistent register state, begins or stops traffic, records status bits, gates clocks, acknowledges interrupts, or changes scheduler/MES state.
5. Driver code later reads status/counter/pointer registers and decodes the result with the matching masks.

Common flows represented by this chunk include JPEG software reset through `UVD_JMI_CNTL__SOFT_RESET_MASK`, JPEG interrupt enable/status/ack programming through `JPEG_SYS_INT_*`, dynamic power-gating pause request/ack polling through `UVD_DPG_PAUSE`, ring write-pointer programming through `UVD_RB_WPTR*` and `VCN_UMSCH_RB_WPTR`, UMSCH mailbox and interrupt handling, and memcheck enable/status/ack handling through the JPEG and UVD memcheck banks.

## State And Persistence Behavior

The macros do not store state, but they describe stateful hardware registers. BAR low/high fields persist configured memory apertures until the block is reset, power-gated, or reprogrammed. VMID fields persist the virtual-memory context used for hardware memory transactions. Ring pointer and doorbell fields persist producer/consumer state used by firmware and driver submission paths. Interrupt enable bits persist routing policy, while status bits latch hardware events until acknowledged through the matching ack register.

Power-gating and clock-gating fields are especially stateful. `UVD_DPG_*`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_CGC_*`, and `JPEG_CGC_*` describe whether subblocks are running, paused, gated, in memory light/deep sleep, or waiting for an acknowledge. VCN suspend/resume and GPU reset paths must restore required programming after power loss.

The MES/UMSCH and MMSCH fields describe firmware-visible execution context: program counters, exception state, timers, local apertures, mailboxes, busy masks, ring pointers, and interrupt source bits. These registers are not ordinary software variables; stale or incorrectly restored values can desynchronize the host driver, scheduler firmware, and hardware.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_offset.h`. It maps the fields in this chunk to concrete offsets, including JPEG common registers around `regJPEG_SYS_INT_*`, power-gating registers around `regUVD_DPG_*`, ring pointer registers around `regUVD_RB_*`, UMSCH registers around `regVCN_UMSCH_*`, MES registers around `regVCN_MES_*`, S/LMI registers around `regUVD_LMI_MMSCH_*`, context-indirect `ixUVD_*` registers, and LMI indirect `ixUVD_MEMCHECK_*` registers.

The main code integration points are the AMDGPU VCN and JPEG 5.x implementation files. `vcn_v5_0_1.c` and `vcn_v5_0_2.c` include this header for VCN ring setup, DPG pause/resume, ring write-pointer access, and reset/power-management sequences. `jpeg_v5_0_1.c` and `jpeg_v5_0_2.c` include it for JPEG reset and interrupt enable programming, including `UVD_JMI_CNTL__SOFT_RESET_MASK` and `JPEG_SYS_INT_EN__DJRBC0_MASK`. Similar-looking VCN 4.x and 5.3 files should not reuse these masks unless they also use the matching offset/header generation.

This header also integrates with firmware contracts. UMSCH/MES mailbox, ring, interrupt, cache, and aperture fields must match what VCN firmware expects. The names expose hardware concepts, but the legal sequencing and side effects are defined by the hardware/firmware interface rather than by this header.

## Risks And Edge Cases

The primary risk is bitfield drift. These are generated hardware definitions, so a one-bit error can silently program the wrong function. High-risk areas include sparse interrupt layouts, 64-bit low/high BAR pairs, repeated aperture windows, VMID packing fields, and status/ack pairs whose bit positions must match exactly.

Another risk is mixing generations or address spaces. The same logical register names appear in multiple VCN generations and in direct versus indirect address blocks. Code must pair `vcn_5_0_0_sh_mask.h` with `vcn_5_0_0_offset.h` and must use the correct SOC15 block, base index, instance, or indirect accessor. Reusing VCN 4.x masks or offsets with VCN 5.0 code can compile while programming a different hardware field.

Ack/status registers require care. The macros name bits but do not document whether hardware uses write-one-to-clear, write-one-to-acknowledge, sticky status, read side effects, or power-gated access restrictions. Drivers should acknowledge only bits from the matching status bank and avoid broad read/modify/write patterns that could drop a concurrent event.

The chunk boundary itself is an edge case for research and review: line 7370 stops before `UVD_MEMCHECK_VCPU_INT_STAT` is complete. Any final per-file analysis must reconcile this chunk with the following chunk before drawing conclusions about the full VCPU memcheck status/ack layout.

## Test Signals

There are no direct unit tests for this generated header. Useful validation signals are hardware-facing and integration-oriented:

- A kernel build of AMDGPU VCN/JPEG 5.x paths catches missing or renamed macros.
- VCN firmware load, ring initialization, and ring write-pointer update tests exercise `UVD_RB_WPTR*`, `VCN_RB_*`, UMSCH ring, and doorbell fields.
- JPEG decode/encode ring tests exercise `JPEG_SYS_INT_EN`, `JPEG_SYS_INT_STATUS`, `JPEG_SYS_INT_ACK`, and `UVD_JMI_CNTL`.
- Suspend/resume, GPU reset, and dynamic power-gating tests exercise `UVD_DPG_PAUSE`, `UVD_DPG_LMA_*`, clock-gating, scratch, and restore-sensitive state fields.
- Fault-injection or RAS diagnostics should verify JPEG and UVD memcheck status bits latch expected low/high errors and clear only through the matching ack masks.
- Cross-generation review should verify every VCN 5.0 consumer includes the matching `vcn_5_0_0_offset.h` and does not borrow VCN 4.x or VCN 5.3 masks for fields with similar names.
