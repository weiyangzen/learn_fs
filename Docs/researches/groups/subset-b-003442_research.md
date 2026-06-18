# subset-b-003442 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_1_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_1_0_sh_mask.h

## Purpose

`vcn_1_0_sh_mask.h` is an AMDGPU ASIC register field header for the first VCN generation. It does not implement executable C logic; it exports preprocessor constants that describe bit shifts and masks for VCN/UVD and JPEG register fields. Driver code combines these constants with register offsets from the matching `vcn_1_0_offset.h` header and SOC15 register-access macros to program hardware.

The file is protected by `_vcn_1_0_SH_MASK_HEADER`, carries AMD's permissive register-header license, and contains 1,145 `#define` entries. The definitions are grouped by hardware address block comments rather than by C APIs.

## Important APIs, Types, And Macro Families

The public interface is entirely macro based. Each field follows the generated naming pattern `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, allowing callers to build register values with shifts and to isolate fields with masks.

Major address blocks:

- `uvd_uvd_pg_dec`: 112 definitions covering power-gating FSM configuration/status, `UVD_POWER_STATUS`, harvesting, dynamic power-gating LMA access, DPG pause handshakes, scratch registers, and DPG VCPU cache BAR/offset fields.
- `uvd_uvdgendec`: 8 definitions for `UVD_LCM_CGC_CNTRL`, including force-on/off and on/off delay fields.
- `uvd_uvdnpdec`: 446 definitions for JPEG decode ring control, JPEG command/data registers, tiling/address configuration, semaphores, VCPU GP command mailbox, engine control, SUVD clock-gating controls, non-pageable VCPU cache BARs, scratch registers, ring buffer base/size/pointers, and LMI BARs.
- `uvd_uvddec`: 578 definitions for core decode and command processor state, including semaphore control, JRBC/LMI ring BARs and VMIDs, ring control, context indirect registers, clock-gating gates/status/control, interrupts, LMI/MPC/GPCOM/VCPU cache configuration, VCPU control, soft reset, RBC ring/IB registers, status bits, semaphore timeout controls, context IDs, write-pointer polling, and extra ring base/size/read-pointer fields.

Representative high-risk field groups include `UVD_PGFSM_CONFIG__*` and `UVD_PGFSM_STATUS__*` two-bit power-domain fields, `UVD_POWER_STATUS__UVD_PG_EN_MASK`, `UVD_DPG_PAUSE__JPEG_PAUSE_DPG_REQ/ACK_MASK`, `UVD_JPEG_*` ring pointer/size masks, `UVD_LMI_*_64BIT_BAR_*` address fields, `UVD_CGC_*` clock-gating controls, `UVD_MASTINT_EN` and `UVD_SYS_INT_EN` interrupt enables, `UVD_VCPU_CACHE_*`, `UVD_SOFT_RESET__*`, and `UVD_STATUS__*` busy/ack bits.

## Control Flow

There is no runtime control flow in this file. The effective flow is compile-time inclusion followed by call-site use:

1. A VCN or JPEG implementation includes this header alongside the corresponding offset header.
2. The C code computes packed register values using `1 << FIELD__SHIFT`, `2 << FIELD__SHIFT`, or mask clear/set sequences.
3. SOC15 helpers such as `WREG32_SOC15`, `RREG32_SOC15`, `SOC15_WAIT_ON_RREG`, and DPG-mode write helpers send the values to hardware.
4. Hardware state transitions are validated by polling status masks and fields defined here.

Examples in this tree include `vcn_v1_0.c`, which uses `UVD_PGFSM_CONFIG__UVDM_PWR_CONFIG__SHIFT` through `UVD_PGFSM_CONFIG__UVDW_PWR_CONFIG__SHIFT` to power VCN domains on and off, waits on `UVD_PGFSM_STATUS`, updates `UVD_POWER_STATUS`, and uses clock-gating/reset/status fields during boot and shutdown. `jpeg_v1_0.c` includes this header for JPEG v1.0 register field names used when programming JPEG ring behavior.

## State And Persistence Behavior

The header stores no software state and persists nothing. Its constants describe persistent hardware state exposed through MMIO registers. Writes made through consumers affect VCN power domains, SRAM-backed DPG programming, ring buffer pointers, memory BARs, firmware/VCPU cache windows, interrupt status, semaphore state, and scratch registers until the hardware block is reset, power-gated, or reprogrammed.

Because the constants are compiled into the driver, any incorrect mask or shift becomes a persistent ABI-like hardware programming error for all supported devices using the VCN 1.0 path. The scratch and context fields are especially stateful from the hardware perspective because firmware and the driver can use them to exchange status across ring submissions and suspend/resume sequences.

## Dependencies

This header depends only on the C preprocessor and include-guard conventions. It is designed to be included by AMDGPU kernel C files and other generated register headers. Its useful dependencies are at the integration layer:

- Matching register offsets from `vcn/vcn_1_0_offset.h`.
- SOC15 register access and offset composition macros.
- AMDGPU VCN and JPEG implementation files that understand the hardware generation.
- Common enum values such as `UVD_PGFSM_CONFIG__UVDM_UVDU_PWR_ON` from AMDGPU VCN support headers when call sites compare packed status values.

## Integration Points

Primary consumers found in the source tree are `drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c` and `drivers/gpu/drm/amd/amdgpu/jpeg_v1_0.c`. The VCN implementation uses the power-gating, clock-gating, soft-reset, interrupt, LMI, RBC, VCPU cache, semaphore, and status masks during lifecycle, DPG/SPG transitions, ring setup, and diagnostics. The JPEG implementation includes it with `vcn_1_0_offset.h` while building JPEG ring packets and programming JPEG/JRBC registers.

The header also aligns with later generated VCN mask headers. Similar macro names appear in VCN 2.x, 3.x, 4.x, and 5.x files, so shared AMDGPU code patterns assume consistent naming for equivalent fields while generation-specific files select the correct bit layout.

## Risks

The main risk is silent hardware misprogramming. A wrong shift or mask can power-gate the wrong tile, leave a domain active, fail to acknowledge DPG pause, corrupt a ring pointer, route an interrupt incorrectly, or point firmware/VCPU cache windows at the wrong address range. Because most definitions are plain numeric constants, the compiler cannot validate semantic correctness.

Power-management fields are particularly sensitive: VCN 1.0 code builds multi-domain values by OR-ing many shifted literals. A single mismatched field can make `SOC15_WAIT_ON_RREG` time out or make suspend/resume unreliable. Ring and BAR fields are also sensitive because low-bit alignment masks such as `0xFFFFFFC0L`, pointer masks, and 64-bit BAR high/low pairs must match the hardware packet format.

Another maintenance risk is cross-generation name reuse. Similar register names exist in UVD and later VCN headers with different field sets or base offsets; including the wrong generation header can compile but program the wrong bit layout.

## Test Signals

Useful validation signals are hardware and integration tests rather than unit tests for the header itself:

- Successful VCN 1.0 driver probe, firmware boot, suspend/resume, and power-gating transitions in SPG and DPG modes.
- Decode, encode, and JPEG ring tests passing through AMDGPU's ring test paths.
- No timeouts while polling `UVD_PGFSM_STATUS`, `UVD_STATUS`, reset status, semaphore timeout status, or ring buffer status.
- Correct interrupt delivery and acknowledgement for VCN/JPEG ring fences.
- Stable operation under mixed decode/JPEG workloads that exercise DPG pause request/ack fields.
- Register dumps showing sane ring pointer, BAR, cache, clock-gating, and interrupt values after init and after resume.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_1_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_0_0_offset.h

## Purpose

`vcn_2_0_0_offset.h` is the generated MMIO offset map for AMD VCN 2.0.0. It defines symbolic `mm...` register offsets and a companion `..._BASE_IDX` for each register so SOC15 access macros can address the correct register aperture. It contains no executable logic; it is a hardware contract between AMDGPU's VCN/JPEG 2.0 code and the VCN 2.0.0 register map.

The file is protected by `_vcn_2_0_0_OFFSET_HEADER`, carries AMD's permissive register-header license, and contains 935 `#define` entries. Each concrete register normally has two macros: `mmREGISTER` for the offset and `mmREGISTER_BASE_IDX` for selecting the base index. Address-block comments document the underlying hardware block base addresses.

## Important APIs, Types, And Macro Families

The exported API is the set of `mm*` preprocessor constants. The register map is split across twelve address blocks:

- `uvd0_jpegnpdec` at base `0x1e200`: 22 JPEG decode registers for decode control, ring base/write/read/size, scratch, interrupts, pitch, GFX8/GFX10 tiling surfaces, address mode/configuration, GPCOM command/data, and soft reset.
- `uvd0_uvd_jpeg_enc_dec` at base `0x1e300`: 4 JPEG encode interrupt/control/scratch registers.
- `uvd0_uvd_jpeg_enc_sclk_dec` at base `0x1e380`: 15 JPEG encode status, pitch, luma/chroma bases, GFX10 tiling/address configuration, GPCOM, clock-gating, scratch, and soft-reset registers.
- `uvd0_uvd_jrbc_dec` and `uvd0_uvd_jrbc_enc_dec` at bases `0x1e400` and `0x1e480`: parallel decode and encode JRBC ring/IB control, urgent control, conditional read timers, soft reset, status, buffer status, preemption, fence, ring size, and scratch registers.
- `uvd0_uvd_jmi_dec` at base `0x1e500`: 60 JMI/LMI registers for JPEG/JRBC memory interfaces, VMIDs, perfmon counters, 64-bit BARs for reads/writes/preemption fences, JPEG2 paths, swap control, and Huffman fence addresses.
- `uvd0_uvd_jpeg_common_dec` and `uvd0_uvd_jpeg_common_sclk_dec` at bases `0x1e700` and `0x1e780`: common JPEG reset, interrupt, arbiter, clock-gating, memory clock-gating, and performance bank registers.
- `uvd0_uvd_pg_dec` at base `0x1f800`: 46 power-gating, DPG LMA, DPG pause, scratch, DPG VCPU cache, page-fault/status, GFX address config, general counters, and timestamp registers.
- `uvd0_uvddec` at base `0x1ff00`: 162 core VCN decode registers for semaphores, ring buffers, latency counters, context indirect access, clock gating, interrupts, LMI/VM controls, MPC, GPCOM, VCPU cache/noncache windows, VCPU control/debug, soft reset, RBC, job start/done, status, context save/restore, CAM, CRCs, timestamps, UMC controls, and picture output metadata.
- `uvd0_uvdnpdec` at base `0x20700`: 79 non-pageable decode registers for semaphores, VCPU command mailbox, SUVD clock gating, VCPU cache BAR windows, scratch, MDM DMA/busy state, version, GP scratch registers, encode register index/data, output ring, ring aliases, encode pipe busy, and LMI BARs.
- `uvd0_uvdnp2dec` at base `0x21100`: 20 MMSCH non-cache BAR registers, MMSCH VMID/control, MMSCH soft reset, and LMI arbiter control.

The `BASE_IDX` values are not uniform: early JPEG/JRBC/JMI/common blocks use base index `0`, while power-gating, core decode, non-pageable, and MMSCH blocks use base index `1`. Consumers rely on this distinction when `SOC15_REG_OFFSET()` or `SOC15_REG_ENTRY_STR()` expands register names into actual MMIO addresses.

## Control Flow

This header has no runtime control flow. Its operational flow is:

1. A VCN/JPEG 2.0 implementation includes this file and the matching `vcn_2_0_0_sh_mask.h`.
2. Code passes symbolic offsets such as `mmUVD_JPEG_CNTL`, `mmUVD_JRBC_RB_WPTR`, or `mmUVD_PGFSM_CONFIG` to SOC15 register helpers.
3. The helper combines the hardware IP block, instance, offset, and `BASE_IDX` to read, write, wait on, or dump registers.
4. Field masks from the matching mask header determine the value layout written to these offsets.

The main local consumer found in this tree is `drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.c`, which includes this header, declares a JPEG register dump list with entries such as `mmUVD_JPEG_POWER_STATUS`, `mmUVD_JPEG_INT_STAT`, `mmUVD_JRBC_RB_RPTR`, `mmUVD_JRBC_RB_WPTR`, `mmUVD_JRBC_RB_CNTL`, `mmUVD_JRBC_RB_SIZE`, `mmUVD_JRBC_STATUS`, `mmJPEG_DEC_ADDR_MODE`, and GFX10 tiling/pitch registers, and initializes JPEG ring state using the resulting offsets.

## State And Persistence Behavior

The file stores no software state and performs no persistence. The registers it names represent persistent hardware state while the VCN/JPEG block is powered: ring buffer addresses and pointers, interrupt enable/status/ack bits, VMID routing, 64-bit BAR windows, clock-gating and power-gating state, scratch registers, firmware command mailboxes, context save/restore controls, timestamps, performance counters, and reset controls.

Because these offsets are compiled into kernel code, they persist as the driver's hardware ABI for VCN 2.0.0 devices. If an offset or base index is wrong, subsequent driver operations can read or write an unrelated register, which may persist until hardware reset or power-cycle.

## Dependencies

The header has no C library dependency. Its practical dependencies are:

- SOC15 register helper macros that interpret `mm...` and `..._BASE_IDX` pairs.
- Matching field masks and shifts from `vcn/vcn_2_0_0_sh_mask.h`.
- AMDGPU VCN/JPEG 2.0 implementation files, especially `jpeg_v2_0.c`.
- IRQ source definitions such as `ivsrcid/vcn/irqsrcs_vcn_2_0.h` used with registers named here.
- Register dump helpers such as `SOC15_REG_ENTRY_STR()` that consume `mm...` constants.

## Integration Points

`jpeg_v2_0.c` is the clearest direct integration point. During software init it uses offsets from this file to build register dump coverage, set internal/external pitch offsets, configure the JPEG decode ring, and access JRBC and JPEG status/control registers. The same offset naming style is used by VCN lifecycle code for boot, reset, interrupt, ring, LMI, and power-management sequences when targeting VCN 2.0.0 hardware.

The offset file must remain synchronized with `vcn_2_0_0_sh_mask.h`. Offsets identify which register is accessed; masks identify which bits inside that register matter. A mismatch between the two headers creates valid C that writes valid MMIO addresses with invalid field layouts.

## Risks

Incorrect offsets or `BASE_IDX` values are high-impact because SOC15 register helpers hide the final address arithmetic. A register name can compile cleanly while expanding to the wrong aperture. This is especially risky where the same numeric offset exists under different base blocks or where JPEG blocks use base index `0` while VCN power/core blocks use base index `1`.

Ring and memory-interface offsets are particularly sensitive. Misaddressing `mmUVD_JRBC_RB_*`, `mmUVD_RBC_RB_*`, `mmUVD_LMI_*_64BIT_BAR_*`, or VMID registers can corrupt command submission, point DMA at incorrect memory, or break fence completion. Power/reset offsets such as `mmUVD_PGFSM_CONFIG`, `mmUVD_DPG_PAUSE`, `mmUVD_SOFT_RESET`, `mmJPEG_SOFT_RESET2`, and `mmUVD_MMSCH_SOFT_RESET` can cause boot, suspend/resume, or reset failures. Interrupt offsets can cause missed or stuck interrupts.

Generated-header drift is another risk. Later VCN headers include related but not identical register maps; copying constants across generations or including the wrong offset header can lead to subtle hardware failures that are not visible at compile time.

## Test Signals

Useful validation signals include:

- VCN 2.0.0/JPEG 2.0 probe and software init completing without MMIO access faults or register dump failures.
- JPEG decode ring initialization, fence emission, interrupt handling, and ring tests passing.
- Register dumps from `jpeg_reg_list_2_0` showing coherent values for power status, interrupt status, JRBC pointers/control/size/status, GFX10 address configuration, tiling surfaces, and pitch registers.
- Suspend/resume and reset paths preserving or restoring ring, BAR, VMID, power-gating, and clock-gating state.
- No hangs while waiting on JRBC/RBC status, interrupt acknowledgement, soft reset, DPG pause, or power-gating status.
- Memory validation under JPEG/VCN workloads that exercises 64-bit BAR high/low pairs, VMID routing, and ring pointer updates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_0_0_offset.h -->
