# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlmcbk_svc.c

## Purpose
Implements the rpcgen-generated NLM callback service used by Gluster NFS lock management to receive NSM/NLM callback notifications. The file registers `NLMCBK_PROGRAM` version `NLMCBK_V1` on UDP and TCP, dispatches the `NLMCBK_SM_NOTIFY` procedure, and starts the shared NFS RPC poller.

## Important APIs, types, and functions
`nlmcbk_sm_notify_0_svc()` adapts the RPC service entry point to `nlm4svc_sm_notify()`. `nlmcbk_program_0()` is the RPC procedure switch, decodes `xdr_nlm_sm_status`, sends void replies, and frees arguments. `nsm_thread()` is the worker entry that unsets any existing portmapper registration, creates UDP/TCP transports, registers the callback program, sets `THIS`, and calls `nfs_start_rpc_poller()`.

## Control flow
The NFS translator starts `nsm_thread()` with the NFS xlator pointer. The thread registers transports, then the SunRPC service layer invokes `nlmcbk_program_0()` for incoming calls. `NULLPROC` receives an immediate void reply; `NLMCBK_SM_NOTIFY` is decoded and forwarded into the NLM implementation, then replied to with an XDR void result.

## State and persistence behavior
No durable state is stored here. Runtime state is the RPC transport registration in portmap/rpcbind and the process-global xlator context `THIS` for the callback thread. Failure paths log and return without cleaning earlier registrations or transports.

## Dependencies and integration points
Depends on `nlm4.h` for NLM program/procedure constants, XDR functions, and `nfs_start_rpc_poller()`. It integrates with `nlm4svc_sm_notify()` in the NLM server path, the process portmapper, libtirpc/SunRPC `svc_*` APIs, Gluster logging, and NFS message IDs.

## Risks and test signals
Risks include generated-code drift from `nlm4.x`, leaked UDP transport if TCP registration fails, portmapper conflicts, missing `errno` propagation on registration failures, and callback service startup silently ending before the poller starts. Useful tests include simulated `NULLPROC` and `NLMCBK_SM_NOTIFY` RPCs over UDP/TCP, rpcbind registration/unregistration conflicts, malformed XDR decode, argument-free failure logging, and NFS lock recovery after an NSM status notification.
