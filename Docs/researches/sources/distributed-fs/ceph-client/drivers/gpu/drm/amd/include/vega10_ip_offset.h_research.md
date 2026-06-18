# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_ip_offset.h

## Purpose
`vega10_ip_offset.h` is a generated-style AMDGPU register-base map for Vega10-family ASIC IP blocks. It defines a shared two-dimensional `struct IP_BASE` layout and then publishes both static `IP_BASE` instances and matching preprocessor macros for instance/segment base addresses. Consumers use these constants to compose register offsets for NBIF/NBIO, display, media, graphics, memory hub, SDMA, SMU-adjacent, thermal, clock, fuse, and other IP blocks.

## Important APIs, Types, and Constants
The file exports `MAX_INSTANCE` as `5` and `MAX_SEGMENT` as `5`, then declares `struct IP_BASE_INSTANCE { unsigned int segment[MAX_SEGMENT]; }` and `struct IP_BASE { struct IP_BASE_INSTANCE instance[MAX_INSTANCE]; }`. The static base tables are marked `__maybe_unused`, which allows inclusion in register headers without forcing every translation unit to reference every table. Important base tables include `NBIF_BASE`, `NBIO_BASE`, `DCE_BASE`, `DCN_BASE`, `MP0_BASE`, `MP1_BASE`, `MP2_BASE`, `DF_BASE`, `UVD_BASE`, `VCN_BASE`, `DBGU_BASE`, `DBGU_NBIO_BASE`, `DBGU_IO_BASE`, `DFX_DAP_BASE`, `DFX_BASE`, `ISP_BASE`, `SYSTEMHUB_BASE`, `L2IMU_BASE`, `IOHC_BASE`, `ATHUB_BASE`, `VCE_BASE`, `GC_BASE`, `MMHUB_BASE`, `RSMU_BASE`, `HDP_BASE`, `OSSSYS_BASE`, `SDMA0_BASE`, `SDMA1_BASE`, `XDMA_BASE`, `UMC_BASE`, `THM_BASE`, `SMUIO_BASE`, `PWR_BASE`, `CLK_BASE`, and `FUSE_BASE`.

The macro block mirrors those tables as `IP_BASE__INSTn_SEGm` constants. Notable active base ranges include graphics at `GC_BASE__INST0_SEG0` `0x00002000` and segment 1 `0x0000A000`, memory hub at `0x0001A000`, SDMA0/SDMA1 at `0x00001260` and `0x00001460`, UVD/VCN at `0x00007800` and `0x00007E00`, VCE at `0x00007E00`/`0x00048800`, SMUIO/PWR/CLK/FUSE near `0x00016800` through `0x00017400`, and NBIO/NBIF segments spanning low, indirect, and high windows.

## Control Flow and State
There is no executable control flow. The header is a pure compile-time data source. State is static, immutable, and embedded into object files only when referenced. Zeros represent absent instances or unused segments and are semantically meaningful because register access macros may index into the table.

## Dependencies and Integration Points
The table shape is shared with AMD register access code in the DRM driver and is normally included by ASIC register headers or IP-specific code. It depends on the compiler seeing `__maybe_unused` from kernel attributes. Integration is by symbol naming convention: downstream code expects names like `GC_BASE` or macros like `GC_BASE__INST0_SEG0` to match generated register definitions.

## Risks
The main risk is silent register misaddressing if a segment value, instance count, or macro name drifts from the hardware register database. The header duplicates data in static structs and macros, so edits must keep both forms consistent. Reusing this file for non-Vega10 ASICs is unsafe because many later families add segments or relocate blocks. The `MAX_INSTANCE`/`MAX_SEGMENT` sizes are part of the ABI expected by any table-indexing helper.

## Test Signals
Build coverage should include AMDGPU objects that include Vega10 register headers with warnings enabled, catching malformed initializers or missing attributes. Runtime signals are indirect: successful ASIC initialization, register reads from GFX/MMHUB/SDMA/SMUIO, power management bring-up, display/media block discovery, and absence of invalid MMIO accesses on Vega10 hardware. Diff-based validation against the AMD register database is the strongest unit-level signal.
