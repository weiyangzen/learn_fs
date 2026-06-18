# sources/distributed-fs/glusterfs/xlators/meta/src/meta-hooks.h

Purpose: central declaration header for all virtual `.meta` tree hook functions. It gives every file/dir/link module a uniform `meta_<name>_hook(call_frame_t *, xlator_t *, loc_t *, dict_t *)` prototype.

Important APIs/types/functions: `DECLARE_HOOK(name)` expands to a hook declaration. The declarations cover root, graph, xlator, logging, process, volfile, subvolume, option, diagnostic, memory, history, latency, and profile nodes.

Control flow: `meta-defaults.c` lookup uses `struct meta_dirent.hook` pointers declared here. Directory modules include this header to refer to hooks for their child entries; hook implementations then attach `meta_ops` and optional inode context to the looked-up inode.

State and persistence behavior: the header defines no state. Its contract is that hook implementations mutate inode context through `meta_ops_set()` and `meta_ctx_set()` during lookup.

Dependencies and integration points: depends on types declared through `meta.h`/Gluster headers and is included by most `xlators/meta/src/*` modules that define static dirent tables.

Risks and edge cases: adding a new hook implementation without declaring it here breaks modules that reference it in dirent tables. A declaration can also hide missing implementation until link time.

Test signals: build/link coverage for all declared hooks and traversal tests that touch each fixed dirent referencing a hook.
