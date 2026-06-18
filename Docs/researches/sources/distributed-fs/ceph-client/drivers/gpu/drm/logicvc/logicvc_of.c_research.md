# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_of.c

Purpose: parses and validates LogiCVC device-tree properties for display and layer configuration.

Important APIs/types/functions: static string/value tables for display interface/colorspace and layer colorspace/alpha mode; property descriptor table; `logicvc_of_property_parse_u32`, `logicvc_of_property_parse_bool`, and `logicvc_of_node_is_layer`.

Control flow: `parse_u32` validates property index, enforces required properties, reads either strings mapped through `logicvc_of_property_sv_value` or numeric u32 values, applies optional ranges, and writes the result. Boolean parsing returns presence. Node helper matches child node name `layer`.

State and persistence: property metadata is static. Parsed values persist in `logicvc_drm_config` or `logicvc_layer_config`.

Dependencies and integration points: depends on Linux OF APIs, DRM print support, and constants from `logicvc_drm.h` and `logicvc_layer.h`. Called by core and layer config parsing.

Risks and test signals: descriptor ranges currently constrain layer colorspace to RGB only, so YUV layer strings are declared but not accepted. Missing required properties return `-ENODEV`. Test valid/invalid DT bindings, optional booleans, string enum parsing, and range failures.
