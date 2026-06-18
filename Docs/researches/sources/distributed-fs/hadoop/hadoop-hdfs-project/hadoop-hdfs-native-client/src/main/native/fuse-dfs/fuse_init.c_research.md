# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_init.c

## Purpose
Mount-time initialization for `fuse_dfs`, creating private context, parsing protected paths, initializing connection cache, and negotiating FUSE capabilities.

## Important APIs, Types, And Functions
`dfs_init`, `dfs_destroy`, `init_protectedpaths`, `dfsPrintOptions`, and `print_env_vars`.

## Control Flow
`dfs_init` allocates `dfs_context`, copies selected global options, logs options, splits colon-separated protected paths, normalizes read buffer size, initializes libhdfs connection subsystem, optionally tests connection, and sets desired FUSE capabilities for atomic truncate, async read, big writes, and dont-mask permissions. `dfs_destroy` only traces.

## State, Persistence, And Dependencies
Mount context persists in FUSE private data. Connection cache globals are initialized here. Protected paths are allocated dynamically. Depends on global `options`, libfuse capability flags, and `fuse_connect`.

## Integration Points
Registered as `.init` and `.destroy` in `fuse_dfs.c`; the only place libhdfs is initialized after FUSE daemonization.

## Risks
`dfs_destroy` does not free allocated context/protected path memory. Fatal init failures call `exit`, terminating mount. Protected path parser only supports colon separation and exact later matching. Capability negotiation depends on compile-time FUSE macros.

## Test Signals
Mount startup, initchecks, read buffer defaults, and capability-sensitive open(O_TRUNC)/big-write workloads validate this file.
