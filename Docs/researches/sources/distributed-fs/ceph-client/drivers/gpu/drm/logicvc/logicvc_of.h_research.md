# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_of.h

Purpose: declares LogiCVC OF property IDs, property metadata structs, and parser helpers.

Important APIs/types/functions: `enum logicvc_of_property_index`, `struct logicvc_of_property_sv`, `struct logicvc_of_property`, and parse/node helper prototypes.

Control flow: no executable flow; the enum indexes the descriptor table in `logicvc_of.c`.

State and persistence: property descriptors define required/optional and range semantics used during probe.

Dependencies and integration points: used by core config parsing and layer parsing. Expects Linux device-node types from includers.

Risks and test signals: enum order must match descriptor table entries. Test compile coverage and DT parsing for every enum value.
