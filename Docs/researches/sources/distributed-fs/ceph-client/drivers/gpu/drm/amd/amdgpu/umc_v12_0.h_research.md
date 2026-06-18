# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v12_0.h

## Purpose

This header defines the UMC v12.0 register spacing, channel geometry, ECC counter constants, physical-address bit positions, MCA/IPID decode helpers, error classifier prototypes, and the exported `umc_v12_0_ras` registration object.

## Important APIs, Types, and Functions

Important constants include `UMC_V12_0_NODE_DIST`, `UMC_V12_0_INST_DIST`, `UMC_V12_0_CROSS_NODE_OFFSET`, channel counts, ECC counter initial values, bad-page expansion counts, PA bit definitions, and MCA hardware identifiers. Public helpers include `MCA_IPID_2_DIE_ID`, `MCA_IPID_2_UMC_CH`, `MCA_IPID_2_UMC_INST`, and `MCA_IPID_2_SOCKET_ID`.

## Control Flow

The header has no runtime flow. It controls implementation behavior by giving `umc_v12_0.c` the constants needed for channel iteration, register offset calculation, MCA IPID parsing, ECC counter initialization, and bad-page address expansion.

## State and Persistence Behavior

It stores no state. Its macros shape how runtime state in `adev->umc`, MCA status registers, and RAS page-retirement logs is interpreted.

## Dependencies and Integration Points

The header includes `soc15_common.h` and `amdgpu.h`, and depends on register field macros for MCA/IPID extraction. It is consumed by the UMC v12 implementation and generation dispatch code.

## Risks

Wrong distance or bit-position constants directly affect register access and bad-page retirement. The total-channel macro depends on initialized `adev->gmc.num_umc`, and the IPID decode macros are generation-specific.

## Test Signals

Runtime signals include correct channel enumeration, valid socket/die/UMC/channel reporting in RAS logs, correct bad-page fanout counts, and absence of invalid MMIO reads during UMC scans.
