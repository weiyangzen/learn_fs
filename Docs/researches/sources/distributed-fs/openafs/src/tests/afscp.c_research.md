<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afscp.c -->
# sources/distributed-fs/openafs/src/tests/afscp.c

## Purpose
Direct RX fileserver copy/lock utility used to exercise AFS fetch/store paths independently of normal file I/O. It can copy local-to-AFS, AFS-to-local, AFS-to-AFS, and release an AFS file lock.

## Important APIs, Types, And Functions
Key functions are `statfile`, `start_cb_server`, `do_rx_Init`, `get_sc`, `int_handler`, and `main`. It uses `pioctl` operations `VIOC_FILE_CELL_NAME`, `VIOCGETFID`, and `VIOCWHEREIS`; RX calls such as `RXAFS_CreateFile`, `FetchStatus`, `Start/EndRXAFS_FetchData`, `Start/EndRXAFS_StoreData`, `ReleaseLock`, and `GiveUpCallBacks`.

## Control Flow
Options set block size, local source/destination modes, sleep delay, unauthenticated mode, unlock mode, and loop duration. `statfile` resolves either normal AFS paths via pioctl or explicit `@afs:cell:server:volume:vnode:uniq`. Main initializes RX and a callback service, creates source/destination connections, creates or opens the destination, fetches status, streams bytes between local fds and RX calls, optionally loops until time/SIGINT, gives up callbacks, reports transfer rate, and exits nonzero on fetch/store errors.

## State And Persistence
Creates/truncates local files or AFS files and may release AFS locks. Maintains transient RX connections/calls, callback registration, data buffers, and security classes.

## Dependencies And Integration Points
Depends on OpenAFS RX, fileserver interfaces, callback stubs from `afscp_callback.c`, pioctl cache-manager access, DNS, and null RX security in this build.

## Risks And Test Signals
Authentication is effectively forced to null (`sscindex = scindex_NULL`), so secure-copy coverage is limited. Error cleanup relies on goto labels and can use partially initialized state. `strncpy` may not NUL-terminate long cell names. Signals include successful copy in all mode combinations, unlock output, callback give-up messages absent, and expected transfer-rate reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afscp.c -->
