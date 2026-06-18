# sources/distributed-fs/openafs/src/gtx/gtxobjects.h

Purpose: defines the generic GTX object abstraction, `struct onode`, used by text and light objects and displayed by frames.

Important APIs and types: `GATOR_OBJNAMELEN`, `struct onode` with type, name, geometry, changed/refcount state, window, operation table, graph/navigation pointers, and private data; `struct onodeops`; `OOP_DESTROY`, `OOP_DISPLAY`, `OOP_RELEASE`; initialization and creation parameter structs; `gator_objects_init`, `gator_objects_create`, and `gator_objects_lookup`.

Control flow and state: callers initialize object/window packages, then create typed objects via `onode_createparams`. The implementation attaches type-specific ops and private data and may link previous/parent objects.

Dependencies and integration: includes `gtxwindows.h`; used by light/text object headers, frame display lists, tests, and `objects.c`.

Risks: object type indexes are used directly into arrays in `objects.c`, so invalid `cr_type` can index outside initialized entries. Name copy uses fixed-size storage. Release/destroy semantics are incomplete in object implementations. Test signals should validate object creation bounds, parent/previous linking, display dispatch, and lookup expectations.
