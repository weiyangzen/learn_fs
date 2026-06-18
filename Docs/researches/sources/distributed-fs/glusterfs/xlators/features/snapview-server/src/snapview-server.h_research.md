# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server.h

Purpose: declares snapview-server public/private structures, constants, macros, and cross-file helper prototypes.

Important APIs/types: constants bound cached gfapi objects (`SNAP_VIEW_MAX_GLFS_T`, fd and object limits) and set the default log directory. Macros include `SVS_STACK_DESTROY`, `SVS_CHECK_VALID_SNAPSHOT_HANDLE`, `SVS_GET_INODE_CTX_INFO`, and `SVS_STRDUP`. Types include `inode_type_t` for entry-point/snapshot/virtual inodes, `svs_inode_t` for gfapi object mapping plus synthetic metadata, `svs_fd_t`, `snap_dirent_t`, and `svs_private_t`. Prototypes expose inode/fd context helpers, gfid/iatt helpers, snapshot initialization/list helpers, management init/submit, and `svs_get_handle`.

Control flow/state: the macros encode important runtime policy. `SVS_CHECK_VALID_SNAPSHOT_HANDLE` scans the current snapshot list under lock before a cached `glfs_t` is trusted. `SVS_GET_INODE_CTX_INFO` recovers missing/invalid fs/object handles via `svs_get_handle`.

Dependencies/integration: includes Gluster dict/defaults/mem/call-stub/iatt/logging/ACL/syncop/list/timer, libgfapi internals, RPC client/protocol headers, and server message IDs. It is shared by `snapview-server.c`, helpers, and management.

Risks/test signals: macros mutate caller variables and branch to caller labels, so call-site variable naming is part of the contract. `SVS_CHECK_VALID_SNAPSHOT_HANDLE` compares pointer identity; tests should cover stale handles after snapshot refresh and paths where handle recovery is attempted.
