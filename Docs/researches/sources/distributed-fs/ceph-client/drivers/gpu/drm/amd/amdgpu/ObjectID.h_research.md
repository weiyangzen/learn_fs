<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ObjectID.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ObjectID.h

## Purpose
`ObjectID.h` is the legacy AMD display BIOS object-id contract used by the non-DC amdgpu display stack. It defines the bit layout and numeric constants for graphics object types, encoder object ids, connector object ids, router ids, generic objects, enumeration ids, full packed object identifiers, and object capability/table ids.

The file has no executable logic. Its purpose is ABI-style coordination with ATOM BIOS object tables and display code that decodes connector and encoder topology. The constants are consumed by connector, encoder, DisplayPort, CRTC, and DCE paths to identify things such as internal UNIPHY encoders, DACs, HDMI and DP bridge chips, LVDS/eDP panels, MXM routes, and hotplug/I2C capability records.

## Important APIs, types, and functions
- Graph object type macros define the high nibble of the packed id: `GRAPH_OBJECT_TYPE_GPU`, `ENCODER`, `CONNECTOR`, `ROUTER`, `DISPLAY_PATH`, and `GENERIC`.
- Object id macros define low-byte ids for encoder classes including internal LVDS/TMDS/DAC/DVO/UNIPHY variants, external SDVO/TMDS/HDMI/DP bridges, and legacy bridge chips such as `TRAVIS`, `NUTMEG`, `ALMOND`, and `ANX9805`.
- Connector object ids describe physical connector classes: DVI-I/DVI-D single and dual link, VGA, composite, S-video, YPbPr, HDMI type A/B, LVDS, DisplayPort, eDP, MXM, LVDS/eDP, and USB-C.
- `OBJECT_ID_MASK`, `ENUM_ID_MASK`, `OBJECT_TYPE_MASK`, and their shifts define the packed 16-bit object format used in BIOS tables.
- `CONSTRUCTOBJECTFAMILYID()` builds a family id from a graph object type and object id.
- The numerous `ENCODER_*_ENUM_ID*`, `CONNECTOR_*_ENUM_ID*`, `ROUTER_*`, and `GENERICOBJECT_*` macros precompose graph type, enum number, and object id into BIOS-compatible 16-bit identifiers.
- Capability macros such as `GRAPHICS_OBJECT_CAP_I2C`, `GRAPHICS_OBJECT_CAP_TABLE_ID`, and table ids for I2C command, hotplug detection interrupt, and encoder output protection label object records.

## Control flow
There is no runtime control flow. The only compile-time flow is an include guard and optional `_X86_` `#pragma pack(1)` / `#pragma pack()` pair around the definitions. Display code includes this header and compares or extracts id fields from values read out of BIOS object tables.

The important data path is external: BIOS table parser reads an object id, code masks it with `OBJECT_ID_MASK` and shifts with `OBJECT_ID_SHIFT` to get a raw encoder/connector id, then DCE and connector code switch on constants such as `ENCODER_OBJECT_ID_INTERNAL_UNIPHY*`, `ENCODER_OBJECT_ID_INTERNAL_KLDSCP_DAC*`, `CONNECTOR_OBJECT_ID_DISPLAYPORT`, or `CONNECTOR_OBJECT_ID_eDP`.

## State and persistence behavior
The header defines stable constants only. No kernel memory is allocated, no state is mutated, and no values are persisted by this file. The persistence requirement is external: the numeric values must remain stable because they match firmware table encodings and are baked into BIOS data.

## Dependencies and integration points
The file is integrated through amdgpu display components that include `ObjectID.h` directly or indirectly. Search hits show use in `amdgpu_connectors.c`, `amdgpu_encoders.c`, `atombios_dp.c`, `atombios_crtc.c`, and DCE generation files such as `dce_v8_0.c` and `dce_v10_0.c`.

It also overlaps conceptually with `drivers/gpu/drm/amd/display/include/grph_object_id.h`, which serves newer DC display code. Any change must respect both the ATOM BIOS object layout and legacy display paths still using this header.

## Risks and edge cases
The primary risk is ABI drift. Renumbering or deleting constants would make BIOS object parsing choose the wrong connector or encoder path. The duplicate value for `ENCODER_OBJECT_ID_ALMOND` and `ENCODER_OBJECT_ID_NUTMEG` is intentional legacy baggage and should not be "cleaned up" without checking all BIOS consumers.

Packed id construction is also easy to misuse: object id, enum id, and graph type occupy different bit fields, so callers must not compare a raw low-byte `*_OBJECT_ID_*` value with a full `*_ENUM_ID*` value. Comments mention deleted entries, obsolete Radeon/Kaleidoscope classes, and old external encoders; preserving gaps is safer than compacting them.

## Test signals
Useful signals are display bring-up on legacy DCE ASICs, correct connector type mapping in `xrandr`/DRM connector properties, HPD handling for DP/eDP/HDMI, and successful encoder routing on systems with ATOM BIOS object tables. Compile-time signals include all legacy display files building after including this header and no switch fall-through to unknown connector/encoder ids in DCE and ATOM BIOS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ObjectID.h -->
