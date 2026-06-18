# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlm4.h

## Purpose
Defines the NLMv4 public interface and shared data structures for GlusterFS NFS lock-manager support. It centralizes NLM procedure numbers, fixed service port/program IDs, platform-specific rpc.statd/sm-notify paths, service initialization prototypes, and the client/share/fd structures used by `nlm4.c`.

## Important APIs, Types, and Functions
The header defines all NLMv4 procedure numbers from `NLM4_NULL` through `NLM4_FREE_ALL`, plus `NLM4_PROC_COUNT`. It defines the registered service port `GF_NLM4_PORT`, log domain `GF_NLM`, NLM program/version constants `NLM_PROGRAM` and `NLM_V4`, and platform-specific defaults for `GF_RPC_STATD_PROG`, `GF_RPC_STATD_PIDFILE`, and `GF_SM_NOTIFY_PIDFILE`.

Public service prototypes are `nlm4svc_init(xlator_t *nfsx)` and `nlm4_init_state(xlator_t *nfsx)`. `nlm4_lkowner_t` is a fixed 1024-byte owner buffer used when decoding NLM netobj owners. `nlm_client_t` stores caller socket identity, unique marker, client/fd/share list hooks, callback RPC client, caller name, and NSM monitor state. `nlm_share_t` stores a share reservation linked by client and inode, including owner, inode, deny mode, and access mode. `nlm_fde_t` stores a tracked fd and transit count.

## Control Flow
The header itself has no runtime control flow. Its constants drive the server actor table and callback client procedure table in `nlm4.c`. Its structs define how lock manager operations move from decoded RPC arguments to tracked client/fd/share state.

## State and Persistence Behavior
The structures declared here represent in-memory state. `nlm_client_t` instances are created per caller name and removed on disconnect, `FREE_ALL`, or state manager notification. `nlm_fde_t` entries retain Gluster fd references for active client locks. `nlm_share_t` entries retain inode references for advisory share reservations. None of these structures are durable across NFS daemon restart; recovery depends on NSM/statd notifications and the NLM grace period.

## Dependencies and Integration Points
The header depends on Gluster dictionaries, lists, locking, UUID compatibility, lock-owner types, NFS core types, NFSv3 file handles, NFSv3 XDR types, and NLMv4 XDR definitions. `nfs3.h` includes it because NLM arguments and owner buffers are embedded in the shared NFSv3 call-state structure. `nlm4.c` consumes the constants and structs to register the NLM RPC service and manage client state.

## Risks and Edge Cases
The fixed-size owner buffer must be large enough for decoded NLM owners and must stay compatible with `gf_lkowner_t` copy limits. Platform-specific statd paths can be wrong for distributions or containerized deployments. The fixed port and procedure count are external RPC ABI, so changes can break client interoperability. Since list nodes are embedded, each `nlm_client_t`, `nlm_share_t`, and `nlm_fde_t` must have exactly one owning list lifecycle at a time.

## Test Signals
Compile tests should cover Linux, Darwin, and NetBSD path selection where supported. Runtime signals include NLM service registration on port `38468`, successful rpcinfo discovery, lock/share tests that allocate and free all declared structs, owner matching tests, and recovery tests that exercise statd pid-file configuration overrides.
