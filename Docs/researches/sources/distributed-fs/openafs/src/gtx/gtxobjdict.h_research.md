# sources/distributed-fs/openafs/src/gtx/gtxobjdict.h

Purpose: declares an object dictionary API intended to map object names to `struct onode *` instances.

Important APIs: `gator_objdict_init`, `gator_objdict_add`, `gator_objdict_delete`, and `gator_objdict_lookup`.

Control flow and state: the header defines no storage. The intended lifecycle is initialize dictionary, add objects as they are created, delete them as they are destroyed, and look them up by name.

Dependencies and integration: includes `gtxobjects.h`. `objects.c` initializes the dictionary and delegates `gator_objects_lookup` to it. No effective add/delete calls are visible in the researched `objects.c` creation path.

Risks: the implementation is a stub: add/delete return success and lookup returns `NULL`. This means object-name lookup is currently nonfunctional, and successful add/delete statuses are misleading. Test signals should assert lookup behavior explicitly, especially if future code starts depending on `gator_objects_lookup` for navigation, help, or object discovery.
