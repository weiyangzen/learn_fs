# sources/distributed-fs/coda/coda-src/vol/treeremove.h

Purpose: declares the parameter block for recursive tree removal and the directory traversal callback entry point.

Important APIs/types: `TreeRmBlk` stores client, replicated/group volume id, `Volume *`, output status, store id, vnode list, resolution flag, optional hierarchical volume log, server id, and block count pointer. `init` populates those fields and resets `*blocks`. `PerformTreeRemoval(PDirEntry, void *)` is the exported callback.

Control flow/state: callers initialize a `TreeRmBlk` before walking a directory tree. In resolution mode it carries the log tree and server id; otherwise those fields are nulled.

Dependencies/integration: depends on server, object-list, and dlist types and integrates directory traversal with volume mutation and resolution logging. Risks include raw pointer lifetime, unchecked `blocks` pointer, and all state being public mutable fields. Test signals: recursive remove with/without resolution, block accounting, callback use through directory walker, and null-pointer misuse in setup.
