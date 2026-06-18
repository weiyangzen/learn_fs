# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/displayobject.h

## Purpose
This SoC15 display-object header defines BIOS-shared numeric object IDs for GPUs, encoders, and connectors. These values encode object type, enum instance, and object kind into a compact integer used by AtomBIOS/display topology records.

## Important APIs, Types, And Data
`enum display_object_type` distinguishes none, GPU, encoder, and connector objects. `enum encoder_object_type` identifies internal UNIPHY encoder variants. `enum connector_object_type` covers single-link DVI-D, dual-link DVI-D, HDMI type A, LVDS, DisplayPort, eDP, and OPM. `enum object_enum_id` provides enum IDs 1 through 6.

`enum object_id_bit` defines masks and shifts: low 8 bits for object ID, bits 8-11 for enum ID, and bits 12-15 for object type. `GPU_ENUM_ID1`, the `ENCODER_INTERNAL_UNIPHY*` entries, and connector definitions such as `CONNECTOR_DISPLAYPORT_ENUM_ID1` through `CONNECTOR_DISPLAYPORT_ENUM_ID4` are composed with these shifts. OPM connector IDs map enum IDs to MXM DP/LVDS paths in comments.

## Control Flow
There are no functions. Consumers compare or decompose object IDs while parsing BIOS display path records, encoder records, connector records, and board-specific routing data.

## State And Persistence
The header is a constants-only ABI. The values persist in firmware tables and in parsed display topology state, but this file owns no runtime state or storage.

## Dependencies And Integration Points
It conditionally applies `#pragma pack(1)` for `_X86_`, matching BIOS-shared structure conventions. It overlaps conceptually with `amdgpu/ObjectID.h`, but this file is the SoC15-specific display-object definition. Integration points are AtomBIOS display parsing, connector enumeration, encoder mapping, and board topology handling.

## Risks
Changing any numeric value breaks compatibility with firmware object tables. The bit layout is small and rigid; adding new object IDs or enum IDs requires preserving mask/shift semantics. The header has legacy typos in enum names such as `objet`, so external code should use existing spellings rather than "correcting" them without a tree-wide migration.

## Test Signals
Build display BIOS parser paths and test systems with DVI, HDMI, LVDS/eDP, DisplayPort, and MXM/OPM mappings. Runtime signals include correct connector naming, HPD routing, encoder selection, link training, and absence of unknown-object diagnostics while parsing AtomBIOS tables.
