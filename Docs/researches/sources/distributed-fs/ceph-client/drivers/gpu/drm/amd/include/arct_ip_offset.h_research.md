# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/arct_ip_offset.h

## Purpose
This generated-style header provides Arcturus ASIC register base offsets by hardware IP block, instance, and segment. It feeds the SOC15 register-offset table so shared AMDGPU register macros resolve to the correct Arcturus base addresses.

## Important APIs, Types, And Data
The header defines `MAX_INSTANCE` as 8 and `MAX_SEGMENT` as 6. It declares `struct IP_BASE_INSTANCE` and `struct IP_BASE` with `__maybe_unused` annotations.

Static `IP_BASE` tables cover `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIF0_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA0_BASE` through `SDMA7_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `UVD_BASE`, `DBGU_IO_BASE`, and `RSMU_BASE`. Flattened `*_BASE__INSTn_SEGm` macros mirror the tables for compile-time use.

Arcturus has eight instance slots. Several tables use all or many slots, notably UMC and SDMA, while many control IPs only populate instance 0 and leave remaining slots as zero.

## Control Flow
There are no functions. `arct_reg_base_init()` includes this header and loops over `i < MAX_INSTANCE`, storing table instance pointers into `adev->reg_offset` for `GC`, `HDP`, `MMHUB`, `ATHUB`, `NBIO` from `NBIF0_BASE`, `MP0`, `MP1`, `UVD`, `DF`, `OSSSYS`, `SDMA0` through `SDMA7`, `SMUIO`, `THM`, `UMC`, and `RSMU`.

## State And Persistence
The header provides immutable compiled-in data. Runtime state is the `adev->reg_offset` pointer table populated from it during device initialization. No offsets are modified or persisted by this header.

## Dependencies And Integration Points
The data shape is coupled to AMDGPU SOC15 register infrastructure and `amdgpu/arct_reg_init.c`. It supports register access for graphics, memory hub, ATHUB, NBIF/PCIe, SDMA engines, UVD, thermal, SMU, UMC, and RSMU blocks on Arcturus.

## Risks
Wrong base addresses can cause register operations to target incorrect hardware blocks. Because this header defines generic `IP_BASE` type names also used by other ASIC offset headers, it should remain isolated to one ASIC init compilation unit.

The Arcturus init code maps `NBIO_HWIP` to `NBIF0_BASE`, so naming changes in this header need coordinated updates. `MAX_INSTANCE` is 8 here, unlike Aldebaran's 7; common code must not assume all SOC15 ASIC offset headers use the same instance count.

## Test Signals
Build coverage of `arct_reg_base_init()` catches symbol and type breakage. Runtime validation should include register reads for every initialized HWIP, especially all SDMA instances, UMC instances, ATHUB, NBIF/PCIe, and RSMU. Comparing populated `adev->reg_offset` entries against known Arcturus address-map data is the key regression test.
