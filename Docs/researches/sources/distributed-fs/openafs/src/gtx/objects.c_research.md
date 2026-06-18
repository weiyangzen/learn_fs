# sources/distributed-fs/openafs/src/gtx/objects.c

Purpose: implements the generic object factory and object subsystem initialization for GTX.

Important functions and state: `gator_objects_init` initializes debug state, installs type-specific ops for text and light, initializes the object dictionary, initializes the selected window backend through `gw_init`, and installs creation functions. `gator_objects_create` allocates/fills a generic `onode`, calls the type-specific creation routine, and links previous/parent object pointers. `gator_objects_lookup` delegates to the dictionary.

Control flow and state: module globals include `objects_debug`, `on_create[]`, and `objops[]`. Initialization is guarded by a static counter, but it never sets `initialized = 1` on first success, so the guard is ineffective.

Dependencies and integration: includes text/light object implementations by interface, the object dictionary, and windows. Tests and `gtx_Init` rely on it before creating objects.

Risks: no bounds check on `cr_type`; `strcpy` into fixed `o_name`; object dictionary is initialized but not populated; failed type-specific creation frees only the `onode`. Test signals should cover repeated initialization, invalid object type, duplicate/long names, parent/previous links, private-data failure cleanup, and lookup.
