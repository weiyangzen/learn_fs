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
