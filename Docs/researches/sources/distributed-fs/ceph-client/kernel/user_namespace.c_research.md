<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user_namespace.c -->
# sources/distributed-fs/ceph-client/kernel/user_namespace.c

Purpose: implements user namespace creation, destruction, id mapping, `/proc/*/{uid,gid,projid}_map` writes, setgroups policy, and proc namespace operations. It is central to unprivileged namespace isolation and kernel ID translation.

Important APIs and state: creation APIs are `create_user_ns()` and `unshare_userns()`. Mapping APIs include `make_kuid()`, `from_kuid()`, `from_kuid_munged()`, kgid and kprojid variants, `map_id_down()`, `map_id_up()`, and range helpers. Proc write APIs are `proc_uid_map_write()`, `proc_gid_map_write()`, `proc_projid_map_write()`, and `proc_setgroups_write()`. `userns_operations` exposes namespace get/put/install/owner hooks. `userns_state_mutex` serializes map and setgroups state.

Control flow: namespace creation checks nesting depth, ucount limits, chroot restrictions, parent mappings for creator IDs, LSM approval, memory allocation, ns common init, inherited flags, sysctl setup, credential capability reset, and namespace-tree insertion. Freeing is deferred through work and walks parent references while freeing large idmap arrays, sysctls, keys, binfmt_misc, and ns common state. ID maps use small inline extent arrays or larger sorted forward/reverse arrays for bsearch.

Map writes are one-shot, page-sized, offset-zero only operations. `map_write()` parses extents, rejects wraparound, overlap, empty maps, excessive lines, unauthorized writers, and unmappable parent IDs, then sorts and publishes extents with a write barrier before setting `nr_extents`. `new_idmap_permitted()` allows narrow self maps, capability-based maps, and special project-id maps; `verify_root_map()` protects uid 0 mappings and file capabilities.

State and persistence: user namespaces persist via ns refs and parent chains. Maps become immutable after first successful write. Setgroups can be permanently denied before gid_map is written. Ucount and rlimit limits are inherited at creation.

Dependencies and integration: depends on credentials, LSM, procfs seq files, nsfs operations, ucounts, keyrings, binfmt_misc, nstree, sort/bsearch, and user access.

Risks: this is security-sensitive. Bugs can grant capabilities, incorrect ID mappings, or setgroups access. Barriers around map publication protect lockless readers. Test signals include unprivileged user namespace creation, chroot denial, nested depth, root uid map with/without CAP_SETFCAP, overlapping/wrapping extent rejection, large extent sorting, setgroups deny-before-gid-map, namespace install constraints, and id translation round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user_namespace.c -->
