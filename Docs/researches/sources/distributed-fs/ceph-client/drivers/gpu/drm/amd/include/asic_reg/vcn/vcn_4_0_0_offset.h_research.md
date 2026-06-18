# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_offset.h

## Purpose

`vcn_4_0_0_offset.h` is a generated-style register offset map for AMD VCN 4.0.0 hardware in the AMDGPU driver copy under `sources/distributed-fs/ceph-client`. It exposes preprocessor constants for SOC15 register addressing of the video codec, JPEG, multimedia scheduler, unified scheduler, power-gating, memory-interface, and indirect register spaces. The companion `vcn_4_0_0_sh_mask.h` supplies bit masks and shifts; this file supplies the register address selectors consumed by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_DPG_MODE`, and related macros.

The file is not normal executable code. Its important behavior is contractual: each `reg...` macro names a memory-mapped hardware register offset and each matching `reg..._BASE_IDX` macro selects the SOC15 base-index slot for that register. There are also `ix...` macros for indexed/indirect register spaces. A wrong value here routes reads or writes to the wrong hardware location, so this header is part of the hardware ABI between AMDGPU and VCN 4.0.0 ASICs.

## Register Surface

The header is protected by `_vcn_4_0_0_OFFSET_HEADER` and contains about 950 direct `reg...` offsets, 950 matching `_BASE_IDX` selectors, 42 indirect `ix...` offsets, and 15 address-block comments. All direct register base-index macros in this file are `1`.

Major address blocks:

- `uvd0_uvddec`, base `0x1fb00`: top-level UVD/VCN decode control, clock gating, firmware/driver GP communication, interrupts, multiple encode/decode ring base/size/pointer registers, scratch registers, soft reset, status, and command registers.
- `uvd0_ecpudec`, base `0x1fe00`: VCPU cache and non-cache windows, VCPU control, trace, and indirect access registers.
- `uvd0_uvd_mpcdec`, base `0x1ff30`: motion/pixel cache and MPC mux/ALU/performance/indirect registers.
- `uvd0_uvd_rbcdec`, base `0x1ff90`: ring-buffer controller, indirect-buffer sizing, write-pointer polling, semaphore, job start, engine control, and swap registers.
- `uvd0_lmi_adpdec`, base `0x20090`: local memory interface BARs, VMIDs, urgent/latency/perf controls, memory check, RAS, and memory-client mappings for VCPU, RBC, MIF, JPEG, scaler, privacy, image paste, and related clients.
- `uvd0_jpegnpdec`, base `0x20f00`: JPEG decode command ring, decode control/status, pitches, tiling surfaces, GFX address config, output dimensions, GPCOM, indexed data, and JPEG soft reset.
- `uvd0_uvd_jrbc_dec`, base `0x21100`: JPEG ring-buffer controller pointers, control, IB state, preempt fence data, scratch, and status.
- `uvd0_uvd_jmi_dec`, base `0x21200`: JPEG memory interface controls, prefetch controls, VMIDs, read/write BARs, memcheck, latency/perf counters, atomics, swap control, JPEG2 registers, and RAS.
- `uvd0_uvd_jpeg_common_dec`, base `0x21400`: JPEG soft-reset and interrupt aggregation registers.
- `uvd0_uvd_jpeg_common_sclk_dec`, base `0x21480`: JPEG clock-gating, memory clock-gating, soft reset, and performance-bank registers.
- `uvd0_uvd_pg_dec`, base `0x1f800`: power-gating FSM, DPG LMA, scratch, firmware version, address-config, time counters, VCN features, GPUIOV/RAS status, VCN ring doorbell controls, ring read/write pointers, and DPG control.
- `uvd0_mmsch_dec`, base `0x20d00`: multimedia scheduler ucode/SRAM, VF context, GPUIOV command/status, mailboxes, FIFOs, busy status, and scratch registers.
- `uvd0_slmi_adpdec`, base `0x21c00`: MMSCH non-cache BARs, VMID, LMI status, and MMSCH RAS control.
- `uvdctxind`, base `0x0`: indexed UVD context registers such as clock-gating memory control, clock control, software scratch, and IH semaphore control.
- `lmi_adp_indirect`, base `0x0`: indexed LMI CRC and memory-check interrupt registers.

Several macro aliases intentionally share the same numeric offset. Examples include many `*_SUVD_CGC_GATE` names mapping to `0x00c4`, `*_SUVD_CGC_GATE2` names mapping to `0x00c5`, and `*_SUVD_CGC_CTRL` names mapping to `0x00c6`. Later MES aliases also share offsets, such as `regVCN_MES_INTR_ROUTINE_START`/`regVCN_MES_MTVEC_LO`, `regVCN_MES_INTR_ROUTINE_START_HI`/`regVCN_MES_MTVEC_HI`, `regVCN_MES_IC_BASE_LO`/`regVCN_MES_MIBASE_LO`, and `regVCN_MES_DC_BASE_LO`/`regVCN_MES_MDBASE_LO`. These aliases let call sites use hardware-domain terminology without duplicating address knowledge.

## Important APIs, Types, and Macros

This file defines macros rather than C functions or types. The public API surface is the macro namespace:

- `regUVD_*`: VCN/UVD decoder, VCPU, ring, LMI, DPG, JPEG, MMSCH, and legacy-named VCN registers.
- `regJPEG_*`: JPEG common interrupt, clock-gating, reset, memory-check, tiling, and performance registers.
- `regMMSCH_*`: multimedia scheduler registers for firmware SRAM, VF contexts, GPUIOV, mailbox, and busy/status paths.
- `regVCN_*`: VCN-specific doorbell, RAS, UMSCH/MES, hypervisor, and scheduler registers.
- `regUMSCH_*`: unified scheduler reset/control points.
- `ixUVD_*`: offsets for indirect UVD context and LMI adapter register spaces.
- `<register>_BASE_IDX`: base-index constants used by SOC15 addressing helpers.

Consumers typically pass these macros to AMDGPU MMIO helpers. In `vcn_v4_0.c`, `SOC15_REG_ENTRY_STR(VCN, 0, regUVD_RB_BASE_LO)` and similar entries expose debug/register-list state, while runtime paths use `WREG32_SOC15(VCN, inst_idx, regUVD_RB_BASE_LO, ...)`, `RREG32_SOC15(VCN, i, regUVD_STATUS)`, and `WREG32_P(SOC15_REG_OFFSET(VCN, i, regUVD_VCPU_CNTL), ...)`. In `jpeg_v4_0.c`, JPEG ring setup uses `regUVD_JRBC_RB_WPTR`, `regUVD_LMI_JRBC_RB_64BIT_BAR_LOW`, `regUVD_JRBC_RB_SIZE`, and `regJPEG_SYS_INT_EN`. In `umsch_mm_v4_0.c`, UMSCH/MES boot uses `regVCN_MES_CNTL`, `regVCN_MES_IC_BASE_CNTL`, `regVCN_MES_PRGRM_CNTR_START`, `regVCN_MES_IC_BASE_LO`, `regVCN_MES_DC_BASE_LO`, `regUVD_UMSCH_FORCE`, and `regVCN_MES_MSTATUS_LO`.

## Control Flow

There is no local control flow in the header. Control flow appears when driver code sequences these register constants:

1. VCN initialization includes this header and `vcn_4_0_0_sh_mask.h`, disables or enables power/clock gates, configures `regUVD_VCPU_CNTL`, disables `regUVD_MASTINT_EN`, programs `regUVD_LMI_CTRL`/`regUVD_LMI_CTRL2`, configures MPC mux registers, resumes MC/LMI state, and boots or resets VCPU state.
2. Ring setup writes GPU addresses and sizes into `regUVD_RB_BASE_LO`, `regUVD_RB_BASE_HI`, `regUVD_RB_SIZE`, and related pointer registers, then uses `regVCN_RB_ENABLE` and doorbell registers such as `regVCN_RB1_DB_CTRL` to expose queues to firmware.
3. JPEG initialization writes JRBC/LMI register addresses and sizes, clears `regUVD_JRBC_RB_RPTR`/`regUVD_JRBC_RB_WPTR`, and either uses direct register writes or MMSCH commands in SR-IOV mode.
4. MMSCH/UMSCH setup writes context descriptor addresses through `regMMSCH_VF_CTX_ADDR_LO`/`HI`, waits on `regMMSCH_VF_MAILBOX_RESP`, and boots MES through `regVCN_MES_*` instruction/data base, bound, control, cache, and status registers.
5. Runtime ring pointer access reads or writes `regUVD_RB_WPTR`, `regUVD_RB_RPTR`, `regUVD_JRBC_RB_WPTR`, or `regUVD_JRBC_RB_RPTR` unless doorbells are enabled and the driver uses CPU-visible write-pointer memory plus a doorbell write.

Because the constants are preprocessor definitions, the compiler substitutes the literal offsets into the register helper calls. The effective physical MMIO address is built elsewhere from the hardware IP block, instance index, SOC15 base table, `_BASE_IDX`, and the offset.

## State and Persistence Behavior

The header stores no runtime state and persists nothing by itself. It defines the addresses of hardware state that other code mutates:

- Persistent-for-device-session hardware configuration: VCPU control, LMI coherency, MPC replacement/muxing, JPEG memory interface, MMSCH/UMSCH firmware windows, and clock/power-gating controls.
- Queue state: ring base/size registers, read/write pointers, doorbell controls, output/audio/JPEG ring registers, and JRBC/UMSCH ring state.
- Interrupt state: enable/status/ack registers for VCPU, system, SUVD, JPEG, JRBC, MMSCH, memcheck, and master interrupt paths.
- Power and reset state: DPG, PGFSM, soft reset, power status, JPEG soft reset, and clock-gating registers.
- Virtualization/SR-IOV state: `regUVD_IOV_MAILBOX*`, MMSCH VF context/mailbox registers, GPUIOV scheduler state, VMID registers, and hypervisor VMID controls.
- Diagnostics: scratch registers, performance counters, latency counters, CRC indexed registers, RAS status/control, and internal violation/status registers.

Persistence duration is controlled by hardware reset, driver suspend/resume, DPG power transitions, SR-IOV mailbox/MMSCH flows, and firmware reloads. Any modification to offsets can silently corrupt this state model by causing driver writes to target unrelated registers.

## Dependencies and Integration Points

Direct dependencies:

- AMDGPU SOC15 register access macros from `soc15.h`, `soc15d.h`, and SOC15 hardware IP tables.
- `vcn_4_0_0_sh_mask.h`, which gives bit-level masks/shifts for many offsets defined here.
- `ivsrcid/vcn/irqsrcs_vcn_4_0.h`, which pairs interrupt source IDs with VCN/JPEG interrupt status paths.
- AMDGPU VCN/JPEG/MMSCH/UMSCH source files that include this header: notably `vcn_v4_0.c`, `jpeg_v4_0.c`, and `umsch_mm_v4_0.c`.
- Shared driver structures such as `struct amdgpu_device`, `struct amdgpu_ring`, VCN firmware shared memory structures, and MMSCH init table structures. These structures decide what values are written to the registers named here.

Integration behavior is ASIC-version-specific. VCN 4.0.0 has sibling headers such as `vcn_4_0_3_offset.h`, `vcn_4_0_5_offset.h`, and later VCN 5.x offset headers. Many macro names are reused across versions while numeric offsets can differ. Source files select the correct offset header for a hardware generation, so cross-version edits must not assume same-name registers have stable values.

The source path is under a `ceph-client` source tree, but this file is AMDGPU display/media driver content. It has no Ceph filesystem behavior; its relevance to the broader tree is that the distributed filesystem source snapshot carries a Linux kernel GPU driver subtree.

## Risks

- Offset drift: changing a literal offset or `_BASE_IDX` can redirect MMIO access to a different register or block, causing hangs, failed firmware boot, broken JPEG/VCN queues, missed interrupts, or memory corruption.
- Alias misunderstanding: duplicate numeric offsets are intentional for shared/aliased hardware registers. Deduplicating names or "fixing" repeated values can break domain-specific call sites.
- Version mixing: copying offsets from VCN 4.0.3, 4.0.5, or 5.x into this 4.0.0 header can compile successfully but target the wrong hardware layout.
- Missing companion mask updates: if a register offset is updated without the corresponding mask/shift definition in `vcn_4_0_0_sh_mask.h`, call sites may compile but set incorrect bit fields.
- Indirect versus direct access confusion: `ixUVD_*` constants are not direct `reg...` MMIO offsets and must be used through the correct indexed-register helpers.
- SR-IOV/MMSCH sensitivity: virtualization paths use MMSCH mailbox and VF context registers. Incorrect offsets may only surface in virtual functions or when firmware-managed initialization is active.
- Power-gating sensitivity: DPG and PGFSM registers gate access to other state. Bad DPG offsets can leave the hardware inaccessible or prevent suspend/resume recovery.

## Test Signals

Build and compile-time signals:

- Kernel/driver build succeeds for AMDGPU files including `vcn_v4_0.c`, `jpeg_v4_0.c`, and `umsch_mm_v4_0.c`.
- No duplicate macro redefinition warnings appear when including this header with `vcn_4_0_0_sh_mask.h` and other ASIC register headers.
- Static checks confirm every direct register macro used in VCN/JPEG/UMSCH 4.0 code exists in this header and has a matching `_BASE_IDX` where expected.

Runtime and hardware signals:

- VCN 4.0 initialization reaches firmware-ready state, including successful polling of `regUVD_STATUS`/VCPU readiness and no "VCN is not responding" errors.
- Encode/decode rings initialize with expected base, size, read-pointer, and write-pointer values, and doorbell mode advances work without stale `regUVD_RB_WPTR`/`regUVD_RB_RPTR`.
- JPEG decode ring initializes, `regUVD_JRBC_STATUS` reports job completion, and `regUVD_JRBC_RB_WPTR`/`RPTR` update consistently.
- SR-IOV paths complete MMSCH initialization with `regMMSCH_VF_MAILBOX_RESP` returning the expected OK or acceptable incomplete status and the header init status reporting pass.
- UMSCH firmware boot reaches the expected `regVCN_MES_MSTATUS_LO` value used by `umsch_mm_v4_0.c`.
- Interrupt tests observe VCN/JPEG status bits, acknowledgements, and IRQ routing through the expected status/ack registers.
- Suspend/resume and power-gating tests preserve or reprogram DPG, LMI, ring, clock-gating, and soft-reset state without hangs.
