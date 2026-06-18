# sources/distributed-fs/openafs/src/util/winsock_nt.c

Purpose: Provides Windows Winsock initialization/cleanup wrappers and an exported `afs_gettimeofday()` shim.

Important APIs: Under `AFS_NT40_ENV`, defines `afs_winsockInit()`, `afs_winsockCleanup()`, and `afs_gettimeofday(struct timeval *, struct timezone *)`.

Control flow and state: `afs_winsockInit()` calls `WSAStartup()` requesting version 2 and returns `-1` if startup fails or the negotiated version is not 2. Cleanup calls `WSACleanup()`. `afs_gettimeofday()` delegates to roken `rk_gettimeofday()`.

Dependencies and integration: Includes Windows socket types through platform headers, `<sys/timeb.h>`, and `afs/afsutil.h`. Used by Windows networking utilities such as host parsing and UUID generation.

Risks and test signals: Repeated `WSAStartup()` calls require balanced cleanup in Windows semantics, but this wrapper does not refcount. It checks `data.wVersion != 2` rather than using `LOBYTE/HIBYTE`, which assumes version layout expectations. Tests are Windows network startup and host lookup behavior.
