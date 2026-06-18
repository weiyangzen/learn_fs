# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_d.h

## Purpose

`uvd_5_0_d.h` is the generated register-address header for UVD 5.0. It extends the familiar UVD address surface with VMID, 64-bit BAR, SUVD clock-gating, additional PGFSM read tiles, direct MIF address-config MMIO registers, scalar/JPEG-related address configuration, and internal LMI VMID indexed registers.

## Important APIs, Types, And Macros

The header exports semaphore, GPCOM, engine, UDEC, context, CGC, LMI, interrupt, MPC, VCPU cache/control, soft-reset, RBC, status, and timeout registers. UVD 5.0-specific or notable additions include `mmUVD_LMI_RBC_RB_64BIT_BAR_*`, `mmUVD_LMI_RBC_IB_64BIT_BAR_*`, `mmUVD_LMI_VCPU_CACHE_64BIT_BAR_*`, `mmUVD_LMI_RBC_IB_VMID`, `mmUVD_LMI_RBC_RB_VMID`, `mmUVD_SUVD_CGC_*`, `ixUVD_LMI_VMID_INTERNAL*`, PGFSM tile3 through tile7, `mmUVD_MIF_*_ADDR_CONFIG`, `ixUVD_MIF_SCLR_ADDR_CONFIG`, and `mmUVD_JPEG_ADDR_CONFIG`.

## Control Flow And Data Flow

Driver code uses these offsets to configure 64-bit memory windows and VMID-aware ring/IB access, boot firmware, configure memory tiling, submit decode commands, manage SUVD and UVD clock/power state, and poll or clear status. The address flow is broader than earlier UVD versions because ring, IB, and VCPU cache locations have explicit 64-bit BAR and VMID controls.

## State And Persistence Behavior

The header is stateless. Named registers hold persistent engine configuration: 64-bit base addresses, VMIDs, ring pointers, firmware cache windows, clock/power state, reset bits, semaphore latches, and MIF/JPEG tiling state.

## Dependencies And Integration Points

It pairs with UVD 5.0 mask and enum headers, especially `uvd_5_0_enum.h` for field values. Integration points include AMDGPU UVD 5.0 firmware loading, VM-aware ring setup, decode scheduling, JPEG/shared decode support, power gating, interrupts, and reset.

## Risks And Test Signals

Risks include mishandling 64-bit BAR high/low ordering, failing to program VMIDs consistently for RB and IB, applying earlier UVD offset assumptions, or omitting SUVD power/clock programming. Tests should cover firmware boot, decode and JPEG paths where present, VMID isolation, high-address buffer placement, ring tests, suspend/resume, and register-generation diffs.
