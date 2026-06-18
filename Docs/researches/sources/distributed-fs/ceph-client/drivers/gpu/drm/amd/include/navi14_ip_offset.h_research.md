# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi14_ip_offset.h

## Purpose

`navi14_ip_offset.h` is the generated MMIO base-offset map for Navi 14 hardware. It publishes IP block base addresses as fixed C tables and preprocessor macros so AMDGPU register helpers can address the correct ASIC-specific aperture.

The header has the same overall format as `navi12_ip_offset.h`: include guard `_navi14_ip_offset_HEADER`, `MAX_INSTANCE` 7, `MAX_SEGMENT` 5, `IP_BASE` structures, static base tables, and flattened `BLOCK_BASE__INSTn_SEGm` constants. Its value is the Navi 14-specific address map, not executable logic.

## Important APIs, Types, And Data

The public types are:

- `struct IP_BASE_INSTANCE`, an array of five segment offsets.
- `struct IP_BASE`, an array of seven instances, marked `__maybe_unused`.

The header defines static tables for `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `DIO_BASE`, `DMU_BASE`, `DPCS_BASE`, `FUSE_BASE`, `GC_BASE`, `HDA_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIF0_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `USB0_BASE`, and `UVD0_BASE`.

Important Navi 14-specific details include populated display tables for `DMU_BASE` and `DPCS_BASE`, multiple clock table instances, two populated `SDMA_BASE` instances, and memory-controller entries under `UMC_BASE`. Compared with Navi 12, this file maps `MP1_BASE` the same way as `MP0_BASE`, and `PCIE0_BASE` mirrors the `NBIF0_BASE` segment set instead of the separate PCIe aperture used by Navi 12. Those differences are exactly the kind of ASIC-specific variation this header preserves.

## Control Flow

The file has no runtime control flow. It participates in compile-time address selection:

1. A Navi 14 consumer includes the header.
2. The consumer references an `IP_BASE` table or flattened macro for a hardware block.
3. SOC15/display register helpers combine that base with register-local offsets and base indices.
4. Hardware accesses use the resulting address for initialization, reset, clocking, display, media, bus, or diagnostics.

No direct in-tree include of `navi14_ip_offset.h` was found in the searched AMDGPU sources. The header therefore appears to be generated support data that may be used by build configurations, future code, or out-of-tree/platform-specific paths not visible in this source snapshot.

## State And Persistence Behavior

The constants are immutable and compiled into any object that includes the header. The file itself does not allocate memory, mutate driver state, read firmware, or persist settings. Its state impact is indirect: every register programmed through these constants changes hardware state that may last until reset, power-gating transitions, suspend/resume, or driver teardown.

## Dependencies

The file relies on kernel/compiler support for `__maybe_unused` and on AMDGPU register-access conventions that know how to use the base arrays. Correct operation also depends on matching ASIC selection, matching offset/mask headers, and avoiding inclusion of multiple ASIC offset headers with conflicting generic names in one translation unit.

## Integration Points

Potential consumers are the same AMDGPU layers that consume sibling Navi headers: display resource and GPIO code, IRQ services, clock/SMU code, SDMA/media setup, PCIe/NBIF code, RAS or diagnostics, and register dump tooling. Even without a direct include in this tree, its shape matches the generated interface used by DCN and SOC15 code.

The file integrates conceptually with `navi12_ip_offset.h`: both share many block names and segment patterns, but key MP1 and PCIe/NBIF differences mean substituting one for the other would be unsafe.

## Risks

The dominant risk is hardware misprogramming from a wrong base value or accidentally using the Navi 14 table for a different ASIC. Because register helpers hide address arithmetic, many errors would not be caught by the compiler. Display blocks (`DMU_BASE`, `DPCS_BASE`, `DIO_BASE`), management blocks (`MP0_BASE`, `MP1_BASE`), bus blocks (`NBIF0_BASE`, `PCIE0_BASE`), and memory-controller blocks (`UMC_BASE`) are especially sensitive.

The absence of direct includes in this snapshot means normal builds may not catch syntax drift, renamed tables, or generated-data mistakes. The generic symbol names also make multi-ASIC inclusion in a single C file risky.

## Test Signals

Useful test signals include compile coverage from a Navi 14-specific consumer, generated-data comparison against the authoritative hardware database, and real Navi 14 probe tests. Runtime validation should exercise display modeset and hotplug, clock/SMU register access, SDMA ring tests, UVD/media ring tests, PCIe/NBIF readback, memory-controller diagnostics, and suspend/resume.

Any timeout while polling display, SMU, SDMA, UVD, or bus status registers after selecting this map is a strong signal to inspect the affected base table and segment.
