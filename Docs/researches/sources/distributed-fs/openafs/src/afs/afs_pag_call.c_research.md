# sources/distributed-fs/openafs/src/afs/afs_pag_call.c

## Purpose
`afs_pag_call.c` implements the PAG/NFS translator helper runtime used in PAG-only or translator contexts. It starts Rx services for remote stats and PAG callbacks, manages shutdown sequencing for Rx server/event/listener threads, converts selected pioctl payloads between host and network byte order, forwards pioctls to a remote system-control service, and restricts generic syscall calls.

## Important APIs, types, and functions
Global state includes `afs_termState`, `afs_gcpags`, `afs_shuttingdown`, `afs_cold_shutdown`, `afs_resourceinit_flag`, `afs_nfs_server_addr`, `afs_cb_interface`, `AFS_WaitHandler`, `srv_secobj`, `clt_secobj`, `stats_svc`, `pagcb_svc`, and `rmtsys_conn`. Key functions are `afs_Daemon`, `afspag_Init`, `afspag_Shutdown`, `token_conversion`, `FetchVolumeStatus_conversion`, `inparam_conversion`, `outparam_conversion`, `afs_syscall_pioctl`, and `afs_syscall_call`.

## Control flow
`afspag_Init` creates a callback UUID, initializes stats and PAG-specific locks, sets resource state and NFS server address, initializes sysnames, creates Rx stats and PAG callback services on port 7001, starts Rx server/listener/event/PAG daemon threads, initializes ICL logs, creates a remote `rmtsys` connection to port 7009, and sends a pioctl request asking the translator to drop cached credentials.

`afs_Daemon` periodically runs packet checks, user-data GC every 10 minutes, PAG GC every 60 minutes, waits, and participates in staged shutdown by moving `afs_termState` toward Rx event/listener shutdown. `afspag_Shutdown` sets `AFS_SHUTDOWN`, wakes Rx server procs, waits for state transitions, cancels daemon waits, and stops the Rx listener where present.

`afs_syscall_pioctl` copies in an `afs_ioctl`, handles local token/unlog/sysname pioctls first, builds `clientcred` from uid and PAG groups, canonicalizes path, allocates and converts input/output buffers, forwards the pioctl to `RMTSYS_Pioctl`, converts output payloads back, copies to user space, frees buffers, and returns remote or local errors.

## State and persistence behavior
Runtime state includes Rx services/connections, thread shutdown state, global shutdown mode, sysname and user/PAG data, and remote translator connection state. No persistent on-disk state is managed here.

## Dependencies and integration points
The file depends on Rx/RxStats, PAGCB and RMTSYS RPC definitions, pioctl command layouts, token and volume status structures, credential group encoding from PAG code, sysname/token handlers in `afs_pag_cred.c`, ICL, and OSI wait/copy/allocation APIs.

## Risks and edge cases
Pioctl marshalling is size-sensitive and only converts known commands. Buffer sizes are capped by `MAXBUFFERLEN`, with large buffers allocated differently from fixed large-space buffers. Secret token conversion must avoid reading past malformed lengths. Shutdown is state-machine based; missed wakeups or wrong state transitions can hang. `afs_syscall_call` only permits superuser shutdown and denies everything else.

## Test signals
Test translator startup service registration, remote credential flush pioctl, shutdown sequencing with and without Rx kernel listener, pioctl forwarding for token, unlog, sysname, volume status, cache parms, oversized input/output rejection, byte-order conversion round trips, and non-shutdown syscall denial.
