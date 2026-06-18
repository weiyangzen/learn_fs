# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/bios_parser_common.c

Purpose: centralizes conversion from packed BIOS graphics object IDs to Display Core `graphics_object_id` values. Both legacy and atomfirmware parsers depend on this so object identity is consistent across parser generations.

Important functions: `object_id_from_bios_object_id()` is the exported function. It calls private helpers to extract object type, enum ID, and type-specific ID from `OBJECT_TYPE_MASK`, `ENUM_ID_MASK`, and `OBJECT_ID_MASK`. Type-specific mapping covers GPU raw IDs, many internal/external encoder IDs, connector IDs including USB-C, and a small set of generic objects.

Control flow: invalid object type or enum ID returns a zeroed `graphics_object_id`. Unknown encoders assert and return `ENCODER_ID_UNKNOWN`; unknown connectors/generic objects return unknown IDs without asserting. Valid values are assembled with `dal_graphics_object_id_init()`.

State and persistence: stateless pure translation; no allocation or hardware access.

Dependencies and integration points: depends on `bios_parser_common.h`, `grph_object_ctrl_defs.h`, `ObjectID.h`, and Display Core graphics object enums. Used heavily by connector enumeration, source-object lookup, integrated-info external paths, board layout, and atomfirmware display path parsing.

Risks: any new ATOM object ID not added here can become `UNKNOWN`, which can hide connectors/encoders from the display stack. Encoder unknowns assert, so newly introduced encoder IDs are more disruptive than connector additions. Because both parsers share this function, mapping bugs have broad blast radius.

Test signals: table-driven tests for all known encoder, connector, generic, enum, and type encodings; negative tests for unknown type/enum/object IDs; integration tests showing parser connector IDs match expected Display Core IDs for representative VBIOS images.
