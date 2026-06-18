# sources/distributed-fs/ceph-client/fs/afs/Kconfig

## Purpose
This Kconfig file exposes the Linux AFS client, optional dynamic debugging, local caching support, and server cursor debugging.

## Important APIs, types, and functions
Symbols are `AFS_FS`, `AFS_DEBUG`, `AFS_FSCACHE`, and `AFS_DEBUG_CURSOR`. `AFS_FS` depends on `INET` and selects `AF_RXRPC`, `DNS_RESOLVER`, `NETFS_SUPPORT`, and `CRYPTO_KRB5`.

## Control flow
Selecting `AFS_FS` causes kbuild to build `kafs.o`; optional symbols enable debug or cache code paths compiled elsewhere.

## State and persistence
Only build-time `.config` state is stored. Runtime state is in the AFS client module.

## Dependencies and integration points
The selected dependencies match AFS's RxRPC transport, DNS-based cell/VL discovery, netfs integration, and Kerberos/RxGK support.

## Risks and test signals
Risks include dependency drift as security and netfs code changes. Test signals include built-in/module builds, `INET=n`, fscache matrix builds, dynamic-debug configs, and randconfig coverage.
