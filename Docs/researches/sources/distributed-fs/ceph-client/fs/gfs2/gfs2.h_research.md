## sources/distributed-fs/ceph-client/fs/gfs2/gfs2.h

### Purpose
`gfs2.h` is a small common header for simple cross-file constants used throughout the GFS2 implementation. It does not own complex behavior; it provides uniform boolean-like option values and a short-name threshold.

### Important APIs, Types, and Functions
The header defines two enum pairs: `NO_CREATE`/`CREATE` and `NO_FORCE`/`FORCE`. It also defines `GFS2_FAST_NAME_SIZE` as `8`. There are no functions and no stateful types.

### Control Flow
There is no runtime control flow. The constants shape call-site readability, especially calls that conditionally create glocks or force operations.

### State and Persistence Behavior
The file contains no persisted state. Its constants can influence whether other code creates in-core structures or performs forced operations, but persistence is implemented elsewhere.

### Dependencies and Integration Points
`file.c`, `glock.c`, `inode.c`, and related GFS2 sources include this header for common symbolic values. In this subset, `CREATE` is passed into `gfs2_glock_get` paths and contrasts with `NO_CREATE` for lookup-only behavior.

### Risks and Edge Cases
Because the enums are unscoped integer constants, misuse at call sites is possible if arguments are ordered poorly. The risk is low but real in C APIs that accept plain `int create` or force parameters.

### Test Signals
No direct tests target this header. Coverage comes indirectly from glock lookup/create paths, inode creation/lookup paths, and any code that depends on fast-name sizing.
