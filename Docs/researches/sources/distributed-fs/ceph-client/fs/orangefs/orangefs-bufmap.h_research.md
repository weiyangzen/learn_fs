## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-bufmap.h

### Purpose
This header declares the OrangeFS bufmap API used by the device, file I/O, and directory code.

### Important APIs, types, and functions
It declares map lifecycle (`orangefs_bufmap_initialize`, `orangefs_bufmap_finalize`, `orangefs_bufmap_run_down`), size query, regular I/O slot get/put, readdir slot get/put, and iov_iter copy helpers.

### Control flow
Callers initialize the map from the daemon-provided descriptor, get a slot before issuing operations that require shared memory or readdir indices, copy data as needed, and put the slot after the daemon completes the operation. Shutdown is a two-phase finalize/run-down sequence.

### State and persistence behavior
The header exposes no state directly; it abstracts the global map in `orangefs-bufmap.c`.

### Dependencies and integration points
Depends on `struct ORANGEFS_dev_map_desc` and `struct iov_iter` declarations being visible through including sources. Used by `file.c`, `inode.c`, `dir.c`, and `devorangefs-req.c`.

### Risks
The API does not encode whether a slot is regular I/O or readdir, so callers must pair the right get/put functions. Copy helpers assume a valid initialized map and buffer index.

### Test signals
Compile coverage catches declaration drift. Runtime tests should verify every get path has a matching put on success, error, interrupt, and daemon purge paths.
