# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/dimgrey_cavefish_ip_offset.h

## Purpose
This generated-style header provides Dimgrey Cavefish SOC15 register base offsets by IP block, instance, and segment. It supplies the ASIC-specific address map used by AMDGPU register initialization and DCN 3.02 display code.

## Important APIs, Types, And Data
The header defines `MAX_INSTANCE` as 7 and `MAX_SEGMENT` as 6. `struct IP_BASE_INSTANCE` and `struct IP_BASE` model a rectangular table of segment base addresses. Static tables include `ATHUB_BASE`, `CLK_BASE`, `DBGU_IO0_BASE`, `DF_BASE`, `DCN_BASE`, `DPCS_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, and `VCN0_BASE`.

Dimgrey Cavefish uses a richer address map than Cyan Skillfish: most populated blocks have at least a low MMIO segment plus a high `0x024...` segment, `CLK_BASE` has seven populated instances, `DBGU_IO0_BASE` has two instances, `UMC_BASE` has four populated instances, `MP0_BASE` and `MP1_BASE` expose multiple firmware/management segments, and `NBIO_BASE` has six non-zero segments. The second half of the header exposes flattened `*_BASE__INSTn_SEGm` macros for compile-time uses.

## Control Flow
There is no executable control flow. `amdgpu/dimgrey_cavefish_reg_init.c` includes the header to populate `adev->reg_offset`. DCN 3.02 IRQ/resource/dmub code includes it to bind display and DMUB logic to Dimgrey Cavefish register apertures.

## State And Persistence
The header is immutable data only. After device initialization, pointers or copied offsets derived from it persist in the AMDGPU device's register-offset tables for the lifetime of the device. The header itself owns no runtime state.

## Dependencies And Integration Points
It is coupled to SOC15 HWIP indexing, generated register accessors, Dimgrey Cavefish ASIC init, DCN 3.02 resource construction, IRQ service setup, and DMUB support. The names `DCN_BASE`, `DPCS_BASE`, and `VCN0_BASE` are important integration points for display and media IP setup.

## Risks
Address-map drift is high impact: a wrong segment can silently program the wrong IP block, especially for high MMIO segments, UMC instances, or NBIO/MP management apertures. Consumers must honor this header's 7x6 dimensions and cannot reuse assumptions from ASICs with 6x5, 8x6, or other generated shapes. Reusing the generic `IP_BASE` names in broad include scopes risks type-name collisions with other offset headers.

## Test Signals
Build `dimgrey_cavefish_reg_init.c`, DCN 3.02 resource/IRQ paths, and DMUB support. Runtime checks should cover probe, display mode-set, HPD/AUX interrupts, VCN register access, UMC status reads, NBIO/PCIe access, clock/SMU access, suspend/resume, and GPU reset without register timeout or invalid aperture diagnostics.
