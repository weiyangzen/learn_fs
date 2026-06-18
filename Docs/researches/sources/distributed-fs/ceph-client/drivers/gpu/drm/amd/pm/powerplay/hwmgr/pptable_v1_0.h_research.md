# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pptable_v1_0.h

## Purpose

This header defines the packed ATOM PowerPlay table v1.0 schema used for Tonga-era and Polaris-era GPUs. It is the firmware contract consumed by `process_pptables_v1_0.c` when converting VBIOS data into driver-owned PowerPlay tables.

## Important APIs, Types, and Functions

The file is data-layout only. `ATOM_Tonga_POWERPLAYTABLE` is the root structure with offsets to state, fan, thermal, MCLK/SCLK dependency, voltage lookup, multimedia, VCE, PPM, PowerTune, hard-limit, PCIe, and GPIO subtables. The variable-length table types use flexible arrays annotated with `__counted_by`, including state arrays, MCLK/SCLK dependencies, PCIe tables, MM dependencies, voltage lookup tables, VCE state tables, and hard-limit tables. Revision-sensitive variants include `ATOM_Polaris_SCLK_Dependency_Record`, `ATOM_Polaris10_PCIE_Record`, `ATOM_Fiji_Fan_Table`, `ATOM_Polaris_Fan_Table`, `ATOM_Fiji_PowerTune_Table`, and `ATOM_Polaris_PowerTune_Table`.

## Control Flow and State

There is no control flow. The important state model is packed little-endian firmware data with many 16-bit offsets relative to the root table address. `#pragma pack(push, 1)` is critical because the structures must match byte-exact VBIOS layouts.

## Dependencies and Integration

The header includes `hwmgr.h` and uses ATOM-style aliases such as `UCHAR`, `USHORT`, and `ULONG`. Its macros define platform capability bits, thermal controller identifiers, classification flags, fan flags, and table revision constants consumed by the v1.0 parser and broader hwmgr capability logic.

## Risks and Test Signals

Any layout drift, packing change, or incorrect revision interpretation can corrupt pointer arithmetic in the parser. The structures expose firmware-controlled counts and offsets, so parser bounds validation is the main safety signal. Practical test signals are successful initialization on Tonga/Fiji/Polaris boards, sane sysfs clock and fan output, and absence of parser assertions such as invalid state arrays or dependency tables.
