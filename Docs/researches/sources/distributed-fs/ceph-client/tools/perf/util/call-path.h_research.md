# sources/distributed-fs/ceph-client/tools/perf/util/call-path.h

## sources/distributed-fs/ceph-client/tools/perf/util/call-path.h

Purpose: this header defines the call-path tree data structures and public allocation/lookup API.

Important types and constants: `struct call_path` stores parent, symbol or ip, db-export id, kernel flag, RB node, and child tree. `CALL_PATH_BLOCK_SHIFT`, `CALL_PATH_BLOCK_SIZE`, and `CALL_PATH_BLOCK_MASK` define arena block size. `struct call_path_block` contains a block of nodes and list link. `struct call_path_root` contains the root path, block list, next index, and capacity.

Control flow and state: declarations expose `call_path_root__new()`, `call_path_root__free()`, and `call_path__findnew()`. State is root-owned and freed in bulk.

Dependencies and integration: includes Linux types and rbtree definitions; forward use of `struct symbol` is implicit through pointers. Used by call-return and export code that tracks context-sensitive call graphs.

Risks: callers must not free individual call paths or use nodes after root free. `db_id` is mutable caller/export state and initialized to zero.

Test signals: compile all call-path users, build and free deep trees, and verify exported db ids remain attached to stable nodes.
