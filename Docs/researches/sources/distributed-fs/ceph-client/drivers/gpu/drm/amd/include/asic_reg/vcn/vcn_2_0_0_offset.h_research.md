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
