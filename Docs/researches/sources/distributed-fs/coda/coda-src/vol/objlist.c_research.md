# sources/distributed-fs/coda/coda-src/vol/objlist.c

Purpose: appears intended as a C-style object list parallel to `vlist`, tracking per-fid objects and reintegration side state. As checked in, the file contains obvious type and identifier inconsistencies and likely does not compile in normal builds.

Important APIs: intended functions are `OBJ_Cmp`, `OBJ_NewList`, `OBJ_FreeList`, `OBJ_Find`, `OBJ_GetFree`, `OBJ_Free`, and `OBJ_Add`. They allocate list heads, search by `ViceFid`, allocate per-object state, and initialize file or directory side fields.

Control flow/state: expected flow is create list, find or add a `fsobj`, attach a vnode pointer/log lists/inode cleanup fields, and free only once the object is detached from any list and has no vnode pointer. However the implementation references `fsobj`, `obj`, `fsobjlist`, `fsobject`, `Fid`, `l`, and malformed `&b - fid` names inconsistently.

Dependencies/integration: includes `codadir`, `srv`, `dllist`, and `objlist.h`; intended to mirror `vlist.cc`. Risks are high: typoed variables, wrong list field names, missing return from `OBJ_GetFree`, and invalid free variable make this a maintenance/build hazard. Test signals are primarily build-system inclusion checks, compiler errors if enabled, and comparison with `vlist.cc` as the working implementation.
