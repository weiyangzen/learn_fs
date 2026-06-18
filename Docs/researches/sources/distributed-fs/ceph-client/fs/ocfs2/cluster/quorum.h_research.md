# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/quorum.h

## Purpose
`quorum.h` declares the O2CB quorum interface used by heartbeat and networking.

## Important APIs, types, and functions
It declares lifecycle functions `o2quo_init` and `o2quo_exit`, heartbeat event functions `o2quo_hb_up`, `o2quo_hb_down`, `o2quo_hb_still_up`, network event functions `o2quo_conn_up`, `o2quo_conn_err`, and direct disk-timeout fencing `o2quo_disk_timeout`.

## Control flow
Heartbeat and TCP code notify quorum of membership/connectivity transitions. Quorum internally delays or schedules self-fence decisions based on those notifications.

## State and persistence behavior
The header has no state and exposes no structures. Implemented state is runtime-only and may lead to local panic/restart.

## Dependencies and integration points
It depends on node numbers (`u8`) and is included by heartbeat and networking modules.

## Risks and test signals
Risks are callers omitting paired up/down or conn_up/conn_err events and making quorum state inconsistent. Test signals include balanced event sequences, duplicate event BUG paths, and disk-timeout call sites.
