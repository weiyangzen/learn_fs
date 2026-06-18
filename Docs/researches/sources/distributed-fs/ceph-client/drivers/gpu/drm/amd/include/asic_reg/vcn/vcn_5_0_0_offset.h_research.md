# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_0_0_offset.h

## Purpose

`vcn_5_0_0_offset.h` is an AMDGPU ASIC register-offset header for the VCN 5.0.0 media block. It contains preprocessor constants for memory-mapped VCN, UVD-compatible, JPEG, MMSCH, UMSCH, MES, power-gating, LMI, and indirect register addresses. The file is data-only: it exports `#define` names that driver implementation files pass into SOC15 register access helpers.

The offsets are grouped by generated `addressBlock` comments. Each block records the hardware address aperture name and base address, while each `reg*` or `ix*` macro gives the register's offset within the SOC15 register table. Most direct registers also have a matching `<name>_BASE_IDX` macro, almost always set to `1`, which SOC15 helper macros use when computing MMIO addresses.

## Exported API Surface

This header exports macros, not C types or functions.

- Header guard: `_vcn_5_0_0_OFFSET_HEADER`.
- Direct MMIO register macros: `regUVD_*`, `regVCN_*`, `regJPEG_*`, `regMMSCH_*`, `regUMSCH_*`, and `regCDEFE_*`.
- Indirect register index macros: `ixUVD_*`, for context-indirect and LMI-adapter-indirect spaces.
- Base-index macros: `<direct-reg>_BASE_IDX`, paired with direct `reg*` macros for SOC15 addressing.

The file contains 1,590 register-related `#define` lines: 816 non-`_BASE_IDX` register/index definitions and 774 `_BASE_IDX` definitions. Several values intentionally have multiple names, reflecting hardware aliases or broadcast views, for example `regVCN_MES_INTR_ROUTINE_START` and `regVCN_MES_MTVEC_LO` both map to `0x0781`, and `regVCN_MES_IC_BASE_LO` and `regVCN_MES_MIBASE_LO` both map to `0x08d0`.

## Register Block Map

The direct blocks cover:

- `uvd_uvddec` at base `0x1fc00`: top-level UVD/VCN decode controls, clock gating, general-purpose command registers, interrupts, ring buffer base/size/pointer controls, context registers, MPEG2 decode surface fields, scratch registers, status, reset, and VCPU command registers.
- `uvd_vcn_cdefe_cdefe_broadcast_dec0` at base `0x1fc00`: CDEFE clock-gating broadcast aliases.
- `uvd_ecpudec` at base `0x1ff00`: VCPU cached/noncached region offsets and sizes, VCPU control, trace, and indirect access registers.
- `uvd_lmi_adpdec` at base `0x20290`: LMI 64-bit BAR low/high pairs for decode engines, VCPU cache/noncache regions, current picture surfaces, bitstream/data buffers, privacy/image-paste surfaces, VMID controls, latency/perf counters, urgent controls, prefetch, and LMI status/control.
- `uvd_uvd_jpeg0_jpegnpdec`, `uvd_uvd_jpeg_sclk0_jpegnpsclkdec`, `uvd_uvd_jrbc0_uvd_jrbc_dec`, `uvd_uvd_jmi0_uvd_jmi_dec`, `uvd_uvd_jmi_common_dec`, `uvd_uvd_jpeg_common_dec`, and `uvd_uvd_jpeg_common_sclk_dec`: JPEG decode, JPEG ring-buffer controller, JPEG memory interface, interrupt, memcheck, soft reset, clock gating, and performance counter registers.
- `uvd_uvd_pg_dec` at base `0x1f800`: power-gating, dynamic power gating, firmware/version, free counter, address config, RAS status, doorbell, ring enable/write-pointer controls, and UVD ring pointer registers.
- `uvd_mmsch_dec`: MMSCH virtual-function VMID, context address/size, and mailbox registers.
- `uvd_vcn_umsch_dec`: UMSCH/MES control, AGDB write pointers, mailbox channels, spare registers, ring base/size/pointers, interrupt control/status/ack/source, and reset registers.
- `uvd_vcn_cprs64dec`: VCN MES/RISC-V-style program counter, trap/vector aliases, machine status/cause/cycle/time/counter registers, general-purpose register pairs, indexed data memory access, local aperture setup, interrupt data registers, and 16 data-cache aperture base/mask/control triplets.
- `uvd_vcn_hypdec`: MES instruction/data cache base, legacy `MIBASE`/`MDBASE` aliases, cache control, and memory bounds.
- `uvd_slmi_adpdec`: MMSCH noncached BAR pairs, MMSCH VMID/control/status, UMSCH active function ID, and UMSCH LMI status.

The indirect blocks cover:

- `uvdctxind`: context-indirect clock-gating controls, software scratch registers, and IH semaphore control.
- `lmi_adp_indirect`: LMI CRC, swap control, and memcheck interrupt enable/status/ack index registers.

## Dependencies and Integration Points

This header depends only on the C preprocessor. It does not include other headers, allocate storage, or compile any object code.

In this source tree it is included by the VCN/JPEG 5.0.x driver implementations, including `amdgpu/vcn_v5_0_0.c`, `amdgpu/vcn_v5_0_1.c`, `amdgpu/vcn_v5_0_2.c`, `amdgpu/jpeg_v5_0_0.c`, `amdgpu/jpeg_v5_0_1.c`, and `amdgpu/jpeg_v5_0_2.c`. Those files include the matching `vcn_5_0_0_sh_mask.h` for bit masks and use the offsets with SOC15 helpers such as `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY_STR`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, and `SOC15_WAIT_ON_RREG`.

Concrete consumers include:

- VCN register-dump lists that name status, context, command, ring, and DPG registers with `SOC15_REG_ENTRY_STR`.
- VCN firmware boot/setup code that writes VCPU cache BARs, cache sizes, noncache regions, `regUVD_GFX10_ADDR_CONFIG`, `regUVD_POWER_STATUS`, `regUVD_VCPU_CNTL`, `regUVD_MASTINT_EN`, `regUVD_LMI_CTRL`, and ring-buffer registers.
- JPEG driver setup that configures JPEG power status, JPEG/JRBC ring controls, JPEG LMI VMIDs and BARs, JPEG clock-gating registers, JPEG interrupt registers, and external pitch via `SOC15_REG_OFFSET(JPEG, 0, regUVD_JPEG_PITCH)`.
- Reset and idle paths that poll status registers such as `regUVD_STATUS`, `regUVD_LMI_STATUS`, `regUVD_JRBC_STATUS`, and power-gating status registers.

## Control Flow

There is no executable control flow inside the header. Runtime control flow appears in consumers:

1. Driver code includes this offset header plus `vcn_5_0_0_sh_mask.h`.
2. Initialization code chooses an IP block and instance, then passes a `reg*` macro into a SOC15 helper.
3. The helper combines the hardware IP block, instance index, register offset, and base-index metadata to compute an MMIO address.
4. Driver code reads, writes, masks, or waits on that MMIO register to boot firmware, program rings, configure memory windows, enable interrupts, manage power states, dump diagnostic registers, or reset the media block.

The `ix*` macros are not direct MMIO addresses. They are indices used through context or adapter indirect paths, where a driver writes an index register and then reads or writes the paired data register.

## State and Persistence Behavior

The header itself is stateless and persistent only as source text. It defines constants that target hardware state when used by runtime code.

The stateful hardware domains represented by the macros include:

- Firmware/VCPU state: cache base and size registers, noncached regions, VCPU control/status/trace, firmware version, firmware power status, and firmware-driver message registers.
- Ring state: RB base high/low, size, read pointer, write pointer, arbitration, enable, doorbell controls, and JRBC/JPEG ring equivalents.
- Power and clock state: IPX DLDO configuration/status, UVD/JPEG power status, dynamic power gating controls, pause state, clock-gating gate/control/status registers, and memory clock-gating controls.
- Interrupt state: VCPU, system, JPEG, memcheck, UMSCH, and master interrupt enable/status/ack/source registers.
- Memory mapping state: LMI BAR low/high pairs, VMIDs, address-config registers, cache/data apertures, memory bounds, and memcheck safe-address registers.
- Diagnostics and RAS state: scratch registers, performance counters, latency counters, RAS status registers, poison/error registers, CRC indices, and MES machine exception registers.

Persistence across suspend, reset, or power-gating cycles is determined by hardware and driver save/restore paths, not by this header. Consumers must reprogram volatile registers during hardware initialization, resume, DPG entry/exit, and reset.

## Risks and Edge Cases

- Offset correctness is critical. A wrong value can program an unrelated MMIO register, causing failed firmware boot, ring hangs, bad DMA addresses, interrupt loss, power-management failures, or device reset.
- Base-index mismatches are subtle because most entries use `_BASE_IDX 1`. If a future ASIC revision changes an aperture or base index, copying this header without regeneration can silently target the wrong address.
- Aliased macro names are intentional but risky for maintenance. Names sharing the same offset may represent alternate hardware documentation names, broadcast registers, or compatibility aliases; changing only one alias can break consumers that rely on the other.
- The file mixes UVD legacy naming with VCN 5.0 hardware. Consumer code must choose the proper IP block argument (`VCN` versus `JPEG`) when using SOC15 helpers; the macro prefix alone is not enough to identify the runtime block.
- Direct `reg*` macros and indirect `ix*` macros are not interchangeable. Using an `ix*` index with direct MMIO helpers, or a direct register with an indirect accessor, would target the wrong path.
- Register pairs for 64-bit BARs and bounds must be programmed consistently. Low/high ordering errors or partial updates can corrupt firmware, ring, JPEG, or LMI memory windows.
- Security-sensitive registers exist in this map, including memcheck, safe address, VMID, GPUIOV, VF mailbox/context, and RAS/poison status. Incorrect offsets can undermine isolation or hide fault signals under SR-IOV or multi-VM use.
- Generated headers can drift from implementation files. VCN 5.3 and older VCN 4.x headers have related names but different offsets for some registers, so cross-version reuse should be treated as unsafe unless hardware documentation confirms compatibility.

## Test and Validation Signals

Useful validation is mostly integration-level:

- Compile coverage: the AMDGPU objects that include this header should build without undefined register macros or duplicate incompatible definitions.
- Register dump coverage: `amdgpu_vcn_reg_dump_init` and `amdgpu_jpeg_reg_dump_init` should produce coherent addresses for the listed VCN/JPEG registers.
- Firmware boot: VCN initialization should load firmware, set VCPU cache/noncache windows, and observe expected `regUVD_STATUS` and `regUVD_POWER_STATUS` transitions.
- Ring tests: VCN and JPEG ring initialization should update RB base/size/pointer registers and pass `amdgpu_ring_test_helper` where enabled.
- Interrupt tests: JPEG decode, VCN unified queue, poison, and memcheck interrupts should be enabled, acknowledged, and routed through the expected source IDs.
- Power-management tests: DPG pause/resume, clock gating, JPEG/UVD power status waits, and reset paths should not time out on status registers defined here.
- SR-IOV tests: VF VMID, mailbox, IOV active-function, and context-address registers should behave correctly in virtualized configurations.
- Fault/RAS tests: poison, RAS status, memcheck status/ack, and security violation report registers should surface injected or real faults through the expected driver paths.

## Research Notes

This report is based on a complete read of the 1,694-line header and targeted scans of local VCN/JPEG 5.0.x consumers. No source code changes were made to the researched header.
