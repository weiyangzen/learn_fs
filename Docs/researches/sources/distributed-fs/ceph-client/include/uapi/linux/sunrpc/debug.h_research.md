# sources/distributed-fs/ceph-client/include/uapi/linux/sunrpc/debug.h

## Purpose
Defines SUNRPC debug flag bits and binary sysctl IDs for RPC, NFS, NFSD, and lockd debug control.

## Important APIs, Types, and Constants
Debug masks include `RPCDBG_XPRT`, `RPCDBG_CALL`, `RPCDBG_DEBUG`, `RPCDBG_NFS`, `RPCDBG_AUTH`, `RPCDBG_BIND`, `RPCDBG_SCHED`, `RPCDBG_TRANS`, `RPCDBG_SVCXPRT`, `RPCDBG_SVCDSP`, `RPCDBG_MISC`, `RPCDBG_CACHE`, and `RPCDBG_ALL`. Sysctl IDs include `CTL_RPCDEBUG`, `CTL_NFSDEBUG`, `CTL_NFSDDEBUG`, `CTL_NLMDEBUG`, `CTL_SLOTTABLE_UDP`, `CTL_SLOTTABLE_TCP`, `CTL_MIN_RESVPORT`, and `CTL_MAX_RESVPORT`.

## Control Flow, State, and Persistence
The header defines values only. Runtime debug state is stored in dynamically registered SUNRPC sysctl tables and read or changed by sysctl/procfs interfaces.

## Dependencies and Integration Points
Integrates with `CTL_SUNRPC` from `sysctl.h`, SUNRPC module sysctl registration, NFS tooling, and kernel debug logging.

## Risks and Test Signals
Risks include binary sysctl deprecation, flags being interpreted differently across modules, and noisy debug output. Test by toggling each debug mask through supported proc/sysctl paths, checking no ABI renumbering, and validating NFS/SUNRPC logging paths.
