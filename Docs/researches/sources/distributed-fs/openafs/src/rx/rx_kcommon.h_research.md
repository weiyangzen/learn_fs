# Research: sources/distributed-fs/openafs/src/rx/rx_kcommon.h

## sources/distributed-fs/openafs/src/rx/rx_kcommon.h

### Purpose
`rx_kcommon.h` is the common kernel include umbrella and type/macro bridge for RX kernel builds across supported operating systems.

### Important Definitions
- Includes large sets of platform kernel, socket, route, interface, UDP/IP, process, stdarg, AFS, RX, XDR, stats, and errno headers.
- Defines `MAXRXPORTS`, `rxk_ports_t`, `rxk_portRocks_t`, and externs `rxk_ports`/`rxk_portRocks`.
- Defines workarounds such as empty `struct coda_inode_info` for Linux header conflicts.
- Externs platform objects such as `inetdomain` and Solaris interface info when relevant.

### Control Flow and State
This header has no executable flow, but it determines which kernel APIs and structs are visible to `rx_kcommon.c` and other kernel RX files. It maps platform availability through preprocessor branches.

### Dependencies and Integration Points
Central to kernel RX compilation. It includes `rx/rx.h`, `rx_kmutex.h`, `rx/rx_globals.h`, `afs/afs_osi.h`, `afs/lock.h`, `rx/xdr.h`, and `afs/afs_stats.h`.

### Risks and Edge Cases
- Include order is fragile and platform-specific; small changes can break old kernels.
- The Linux Coda header workaround intentionally defines guard macros and a dummy struct, which can conflict if real Coda definitions are later needed.
- Kernel API drift makes these branches high-maintenance.

### Test Signals
Compile-only matrix testing across Linux, BSD, Darwin, Solaris, AIX, and UKERNEL configurations is the main signal. Static include-order tests or CI jobs per platform macro set are valuable.
