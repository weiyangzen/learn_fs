# sources/distributed-fs/glusterfs/libglusterfs/src/graph.c

Purpose: `graph.c` manages GlusterFS translator graphs after parsing: linking, autoload insertion, option validation, initialization, activation, topology comparison, reconfiguration, attach/detach for multiplexed services, cleanup, and pidfile/checksum bookkeeping.

Important APIs and types: key functions include `glusterfs_read_secure_access_file`, `glusterfs_xlator_link`, `glusterfs_graph_insert`, autoload helpers for ACL/WORM/meta/mac-compat/gfid-access, `glusterfs_graph_prepare`, `glusterfs_graph_activate`, `glusterfs_volfile_reconfigure`, `gf_volfile_reconfigure`, `glusterfs_graph_reconfigure`, `glusterfs_graph_destroy`, `glusterfs_graph_fini`, `glusterfs_graph_attach`, `glusterfs_process_svc_attach_volfp`, `glusterfs_process_svc_detach`, and mux pidfile helpers.

Control flow and state: preparation selects graph top, inserts requested autoload translators, stamps DOB/UUID/ID, applies command-line options, and assigns context. Activation counts leaves, validates options, initializes translators, logs unknown options, links graph into `ctx->graphs`, sets `ctx->active`, notifies root of `GF_EVENT_GRAPH_NEW`, and sends parent-up notifications. Reconfiguration parses a new graph, compares topology, and either calls per-translator reconfigure or requires rebuild. Multiplex attach builds a child graph, initializes it, links it under the parent graph, stores checksum/pidfile state, and adds it to context lists. Detach unlinks and spawns cleanup.

Dependencies and integration: depends on `xlator.h`, options, defaults, dict, syscalls, OpenSSL SHA256, pthreads, and parser-provided `glusterfs_graph_construct`.

Risks: many paths manipulate shared graph/context lists and rely on cleanup locks/condition variables. Comments note memory leaks on attach error paths. A scanned call passes `newvolfile_graph->first` where a `char *volume_name` is expected, which should be compile-checked. PID lock setup treats lock failure as non-fatal. Reconfigure topology equality must match mux/server special cases.

Test signals: graph parse/prepare/activate, autoload insertion order, option override, topology equal/not-equal reconfigure, mux attach/detach under concurrent notify, cleanup wait for `child_down_cond`, pidfile update/lock behavior, checksum storage, and failure injection for allocation/init/link errors should be covered.
