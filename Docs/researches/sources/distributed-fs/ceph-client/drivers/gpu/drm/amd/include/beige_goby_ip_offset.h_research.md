# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/beige_goby_ip_offset.h

## Purpose

`beige_goby_ip_offset.h` is a generated ASIC register-base map for the Beige Goby AMDGPU family. It names the MMIO base segments for each major IP block and publishes both structured `static const struct IP_BASE` tables and preprocessor constants for every instance/segment slot. Downstream register headers and SOC15-style access macros use these bases to translate symbolic IP/register offsets into physical MMIO addresses for this ASIC.

## Important APIs, Types, and Macros

The header exports constants and two small layout types:

- `MAX_INSTANCE` is `7`; `MAX_SEGMENT` is `6`.
- `struct IP_BASE_INSTANCE { unsigned int segment[MAX_SEGMENT]; }` stores the segment bases for one IP instance.
- `struct IP_BASE { struct IP_BASE_INSTANCE instance[MAX_INSTANCE]; }` stores all possible instances for an IP block.
- `static const struct IP_BASE <IP>_BASE` tables cover `ATHUB`, `CLK`, `DBGU_IO0`, `DF`, `DIO`, `DCN`, `DPCS`, `FUSE`, `GC`, `HDA`, `HDP`, `MMHUB`, `MP0`, `MP1`, `NBIO`, `OSSSYS`, `PCIE0`, `SDMA0`, `SMUIO`, `THM`, `UMC`, and `VCN0`.
- `#define <IP>_BASE__INST<n>_SEG<m>` mirrors every structured entry as a macro, including zero-filled unused instance/segment slots.

Notable base shapes: `CLK_BASE` has seven populated instances, `DBGU_IO0_BASE` and `UMC_BASE` have two populated instances, most blocks populate only instance 0, `NBIO_BASE` and `PCIE0_BASE` share the same six populated segments, `GC_BASE` and `SDMA0_BASE` share a four-segment map, `DCN_BASE` and `DPCS_BASE` share a five-segment map, and `SMUIO_BASE` has four populated segments for instance 0.

## Control Flow

There is no executable control flow. Runtime behavior occurs when AMDGPU register-access helpers select an IP block, instance, and segment/base index. Generated offset headers provide a register offset within an IP segment, ASIC-specific code combines the selected base from this header with the register offset, and MMIO read/write helpers access the resulting address. The structured tables support indexed lookup, while the macros support compile-time expansion in generated register definitions.

## State and Persistence Behavior

The header has no runtime state. The `static const` tables are immutable per translation unit. The values describe hardware address-map state fixed for the Beige Goby ASIC; they do not persist driver state and are not modified by the driver.

## Dependencies

The header is standalone except for the C compiler and its include guard. It is meaningful only when used with Beige Goby-compatible generated register offset and mask headers and AMDGPU register access helpers. Its type names (`IP_BASE`, `IP_BASE_INSTANCE`) are also used by sibling ASIC offset headers, so include ordering must avoid conflicting duplicate definitions in a single translation unit.

## Integration Points

The direct references in this tree are mainly generated-header-level rather than C call sites. It parallels `sienna_cichlid_ip_offset.h` and other ASIC base maps and is part of the generated register infrastructure used by AMDGPU IP implementations for GC, SDMA, SMUIO, NBIO/PCIE, UMC, VCN, DCN/DPCS, thermal, clock, and firmware/SMU blocks. Beige Goby support elsewhere appears through firmware names and SMU powerplay table handling, including `beige_goby_*` firmware modules and `PPTable_beige_goby_t`.

## Risks and Edge Cases

- A wrong base segment redirects MMIO access to the wrong hardware block. This can cause silent misconfiguration, hangs, failed firmware loads, or register reads that look valid but describe another block.
- Zero entries are placeholders for absent instances or segments, not necessarily valid address zero. Consumers must know whether an instance exists before using a slot.
- The structured `static const` definitions in a header create one internal-linkage copy per translation unit.
- `MAX_SEGMENT` is 6 for Beige Goby, while sibling headers may use fewer segments. Generic code must use the header's own dimensions.
- Some IP blocks intentionally alias base maps (`NBIO`/`PCIE0`, `GC`/`SDMA0`, `DCN`/`DPCS`, `MP0`/`MP1`).

## Test Signals

Build coverage for Beige Goby ASIC support catches missing base symbols. Register smoke tests should read known ID/status registers from each populated IP block and compare against expected values. Firmware loading tests for GFX, SDMA, VCN, PSP/SMU, and DMUB provide broad indirect coverage. Suspend/resume, reset, clock-gating, and power-management tests touch many IP blocks through these bases. Address-map comparison against generated register database output or known-good MMIO traces is the strongest regression signal.
