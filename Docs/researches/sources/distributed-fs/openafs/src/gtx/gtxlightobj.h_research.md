# sources/distributed-fs/openafs/src/gtx/gtxlightobj.h

Purpose: declares the GTX light object, a small labeled indicator object rendered through a generic window.

Important APIs and types: `GATOR_OBJ_LIGHT`, appearance masks for outline, inverse video, flash, and flash-cycle state, `GATOR_LABEL_CHARS`, `struct gator_lightobj`, `struct gator_light_crparams`, `gator_light_create/destroy/display/release/set`, and exported `gator_light_ops`.

Control flow and state: a light object stores on/off `setting`, `appearance`, flash metadata, label text, and an `llrock` pointer used by the implementation to hold lower-level drawing parameters. `gator_light_set` changes both logical setting and draw highlight.

Dependencies and integration: includes `gtxobjects.h`; instantiated through `gator_objects_create` after `objects.c` maps object type 1 to `gator_light_create` and `gator_light_ops`. Display dispatch uses `OOP_DISPLAY`.

Risks: appearance flags for outline/flash are declared but not fully implemented in `lightobject.c`. Label copying requires callers to respect fixed buffer size. Test signals should cover create/display/set and verify appearance flags either work or are documented unsupported.
