# sources/distributed-fs/orangefs/src/client/sysint/error-details.c
## sources/distributed-fs/orangefs/src/client/sysint/error-details.c

**Purpose:** Allocates and frees variable-sized `PVFS_error_details` structures used to return server-specific errors from multi-server management operations.

**APIs and control flow:** `PVFS_error_details_new(count)` computes `sizeof(PVFS_error_details) + (count - 1) * sizeof(PVFS_error_server)`, allocates it, and sets `count_allocated`. `PVFS_error_details_free()` directly frees the structure.

**State and dependencies:** No global state. Depends on `PVFS_error_details` and `PVFS_error_server` layout in `pvfs2-types.h`.

**Risks and tests:** There is no validation for `count <= 0`, so size computation can underflow or allocate a malformed object. It also does not initialize count-used fields or server entries. Tests should cover count 1, multiple servers, zero/negative counts if reachable, allocation failure, and consumers that expect initialized arrays.
