# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega20_ip_offset.h

## Purpose
`vega20_ip_offset.h` provides the Vega20 ASIC IP-base offset map used by AMDGPU register definitions. It is structurally similar to the Vega10 map but expands the table dimensions to match Vega20's register segment layout and selected additional windows. It is consumed as read-only data for building MMIO offsets for power, graphics, display, media, memory, and fabric IPs.

## Important APIs, Types, and Constants
The header sets `MAX_INSTANCE` to `6` and `MAX_SEGMENT` to `6`, and defines the same `IP_BASE_INSTANCE` and `IP_BASE` table types used by other AMD generated offset headers. Static tables include `ATHUB_BASE`, `CLK_BASE`, `DCE_BASE`, `DF_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `SDMA0_BASE`, `SDMA1_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `UVD_BASE`, `VCE_BASE`, `XDMA_BASE`, and `RSMU_BASE`.

The macro block exposes every instance/segment cell as `*_BASE__INSTn_SEGm`. Important non-zero offsets include `CLK_BASE` six segments from `0x00016C00` through `0x0001B200`, `GC_BASE` at `0x00002000` and `0x0000A000`, `MMHUB_BASE` at `0x0001A000`, `SDMA0_BASE` at `0x00001260`, `SDMA1_BASE` at `0x00001860`, `SMUIO_BASE` at `0x00016800`/`0x00016A00`, `UVD_BASE` including an instance 1 segment at `0x00009000`, `VCE_BASE__INST0_SEG0` at `0x00008800`, and `RSMU_BASE` at `0x00012000`.

## Control Flow and State
The file contains no functions or runtime branches. All state is compile-time constant address data. The table initializer order is the only "flow": downstream macros index by IP, instance, and segment to derive a final register address. Zero-filled cells mark unavailable windows and must not be interpreted as valid block bases unless the corresponding hardware really maps at zero.

## Dependencies and Integration Points
The header integrates with AMDGPU ASIC register include files and code paths that select Vega20 offsets by including this header. It depends on Linux kernel C types/attributes being available in the including translation unit. It also integrates with driver code that expects VCE/UVD, NBIO, SMUIO, clock, and data-fabric base names to exist consistently across ASIC families.

## Risks
Because this file defines hardware addresses, incorrect constants can cause invalid MMIO, failed firmware handshakes, power-management failures, or misleading debug output. Vega20 differs from Vega10 in segment count and some block bases, so copy/paste between the two files is high risk. The apparent VCE initializer comment and macro value should be treated carefully during updates because comments and macro values must match the generated hardware source of truth.

## Test Signals
Compile tests should catch struct-dimension mismatches and duplicate/missing symbols. Hardware validation should exercise boot, SMU communication, SDMA engines, UVD/VCE media init, clock/fuse/thermal reads, and register dumps on Vega20 boards. Automated comparison against the generated register database should verify that the static `IP_BASE` tables and `*_BASE__INST*_SEG*` macros are identical.
