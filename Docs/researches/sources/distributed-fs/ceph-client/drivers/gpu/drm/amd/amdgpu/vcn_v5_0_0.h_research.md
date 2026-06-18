<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_0.h

## Purpose
Defines small VCN 5.0.0 public constants and declares the VCN 5.0.0 IP block object. The address constants describe VCN video/AON SOC and IP-relative base addresses for multiple instances.

## Important APIs, Types, And Functions
The file defines `VCN_VID_SOC_ADDRESS`, `VCN_AON_SOC_ADDRESS`, `VCN1_VID_SOC_ADDRESS`, `VCN1_AON_SOC_ADDRESS`, `VCN_VID_IP_ADDRESS`, and `VCN_AON_IP_ADDRESS`. It declares `extern const struct amdgpu_ip_block_version vcn_v5_0_0_ip_block`.

## Control Flow
There is no runtime control flow. Compile-time consumers include ASIC/IP discovery code and VCN implementation files that need these base address constants or the external IP block symbol.

## State And Persistence
The header stores no state. The constants become compile-time inputs to code that maps VCN register spaces; the external symbol points to lifecycle functions in `vcn_v5_0_0.c`.

## Dependencies And Integration Points
Requires AMDGPU core declarations for `struct amdgpu_ip_block_version`. It is included by VCN 5.0.x implementation files, so changes can affect address calculations outside only 5.0.0.

## Risks And Test Signals
Incorrect SOC/IP address constants would cause register programming against the wrong aperture, usually surfacing as VCN boot, ring, or interrupt failures. Build success checks symbol consistency; runtime ring tests and firmware boot are the meaningful integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_0.h -->
