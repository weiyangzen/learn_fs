# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/aldebaran_ip_offset.h

## Purpose
This generated-style header provides Aldebaran ASIC register base offsets by hardware IP block, instance, and segment. It is consumed during ASIC bring-up to populate `adev->reg_offset[hwip][instance]` so common register access macros can add block-specific base addresses.

## Important APIs, Types, And Data
The header defines `MAX_INSTANCE` as 7 and `MAX_SEGMENT` as 6, then declares `struct IP_BASE_INSTANCE { unsigned int segment[MAX_SEGMENT]; }` and `struct IP_BASE { struct IP_BASE_INSTANCE instance[MAX_INSTANCE]; }`.

It exports static constant `IP_BASE` tables for Aldebaran IP blocks including `ATHUB_BASE`, `CLK_BASE`, `DBGU_IO0_BASE`, `DF_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `IOAGR0_BASE`, `IOAPIC0_BASE`, `IOHC0_BASE`, `L1IMUIOAGR0_BASE`, `L1IMUPCIE0_BASE`, `L2IMU0_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA0_BASE` through `SDMA4_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `VCN_BASE`, `WAFL0_BASE`, `WAFL1_BASE`, and `XGMI0_BASE` through `XGMI2_BASE`.

For each table, it also emits flattened macros such as `ATHUB_BASE__INST0_SEG0`, `NBIO_BASE__INST0_SEG5`, or `XGMI2_BASE__INST5_SEG1`. These are compile-time constants for code that wants preprocessor-level offsets instead of walking the table.

## Control Flow
There are no functions. Control flow happens in the including ASIC initialization file. `aldebaran_reg_base_init()` includes this header and loops over `i < MAX_INSTANCE`, assigning selected table instances into `adev->reg_offset` for `GC`, `HDP`, `MMHUB`, `ATHUB`, `NBIO`, `MP0`, `MP1`, `DF`, `OSSSYS`, `SDMA0` through `SDMA4`, `SMUIO`, `THM`, `UMC`, and `VCN`.

## State And Persistence
The header contributes immutable static data compiled into the driver. Runtime state is created when the driver stores pointers to table instances in `adev->reg_offset`. The data itself is not persisted beyond the loaded kernel module image and is not modified.

## Dependencies And Integration Points
The table shape must match `adev->reg_offset` expectations in the AMDGPU SOC15 register access layer. It is tightly coupled to `amdgpu/aldebaran_reg_init.c`, SOC15 hardware IP identifiers, and all register headers whose `mm*` offsets are resolved relative to these base segments.

## Risks
Because this is address-map data, a single wrong offset can make register reads or writes hit the wrong block. Many instances and segments are zero placeholders; caller code must distinguish absent mappings from valid segment 0 values where appropriate. The generic `struct IP_BASE` name is shared by other ASIC offset headers, so multiple such headers should not be included in the same compilation unit unless guarded by local conventions.

`MAX_INSTANCE` and `MAX_SEGMENT` are part of the ABI with initialization loops and register-offset consumers. Changing either without updating the associated ASIC init path can leave offsets uninitialized or cause out-of-bounds assumptions.

## Test Signals
Compile coverage of `aldebaran_reg_base_init()` catches structural breakage. Hardware or emulation smoke tests should read known stable registers for every initialized HWIP and verify nonzero base segments match the ASIC address map. RAS, SDMA, VCN, MMHUB, ATHUB, and UMC initialization are strong integration signals because they exercise different populated base tables.
