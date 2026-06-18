# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/yellow_carp_offset.h

## Purpose
`yellow_carp_offset.h` is the AMDGPU register-base map for Yellow Carp APUs. It defines generated IP base tables and matching macros for a more integrated SoC layout than the Vega discrete GPU headers, including ACP, FCH, PCIE, IOHC, DCN/DPCS, VCN, UMC, SMUIO, and multiple fabric or SoC register windows.

## Important APIs, Types, and Constants
The header defines `MAX_INSTANCE` as `7` and `MAX_SEGMENT` as `6`, then declares `IP_BASE_INSTANCE` and `IP_BASE`. Static tables include `ACP_BASE`, `ATHUB_BASE`, `CLK_BASE`, `DBGU_IO_BASE`, `DCN_BASE`, `DPCS_BASE`, `DF_BASE`, `FCH_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `IOHC0_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `MP2_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `PCIE_BASE`, `SDMA0_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, and `VCN_BASE`.

The macro block provides all `*_BASE__INSTn_SEGm` constants. Notable SoC/APU-specific bases include ACP at `0x02403800` and `0x00480000`, ATHUB windows at `0x00000C00`, `0x00013300`, and `0x02408C00`, DCN/DPCS at legacy display offsets plus `0x00009000` and `0x02403C00`, DF spanning `0x00007000`, `0x0240B800`, `0x02447800`, `0x00C00000`, and `0x03640000`, FCH at `0x0240C000`, `0x00B40000`, and `0x11000000`, GC/SDMA0 sharing visible bases at `0x00001260`, `0x0000A000`, and `0x02402C00`, NBIO including `0x0241B000` and `0x04040000`, PCIE instances from `0x02411800`/`0x04440000` upward, and UMC instance 0/1 memory controller windows.

## Control Flow and State
This file has no runtime execution. It is static SoC address data used by register macros and low-level MMIO helpers. State is immutable after compilation. The many non-zero secondary segments reflect Yellow Carp's split register address spaces; consumers must select the correct segment for the generated register definition.

## Dependencies and Integration Points
The header integrates with AMDGPU Yellow Carp register headers and ASIC initialization code. It is especially relevant to display core, multimedia, PCIe/NBIO, audio co-processor, power/thermal/SMU-facing registers, and memory-controller code. It relies on exact naming compatibility with generated register files.

## Risks
Yellow Carp has more active segment windows than older discrete GPU maps, increasing the risk of using the wrong segment or instance. Because GC and SDMA0 share listed segment bases, consumers must rely on the generated register definitions rather than assuming unique IP base ownership. A wrong SoC window can affect integrated platform devices beyond graphics, including FCH/PCIE/ACP. Edits should be generated from the hardware database, not hand-adjusted.

## Test Signals
Build tests should compile all Yellow Carp register consumers. Runtime signals include successful APU boot, display bring-up, VCN operation, SDMA operation, ACP visibility where enabled, PCIe/NBIO access, thermal/fuse/clock reads, and clean suspend/resume. Register-dump comparison against known Yellow Carp hardware is the most direct validation of offset correctness.
