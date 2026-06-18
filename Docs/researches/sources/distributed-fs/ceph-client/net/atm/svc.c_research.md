# sources/distributed-fs/ceph-client/net/atm/svc.c

## Purpose
`svc.c` implements the `PF_ATMSVC` socket family for switched virtual circuits. It provides bind/connect/listen/accept, QoS changes, SVC-specific socket options, point-to-multipoint party management, and protocol family registration while delegating raw VCC data-plane behavior to common VCC functions.

## Important APIs and Functions
- `svc_bind`: binds a local ATM SVC address by asking atmsigd (`as_bind`) and waiting for a reply.
- `svc_connect`: validates QoS and remote address, sends `as_connect`, supports nonblocking `SS_CONNECTING`, handles signal abort with `as_close`, then calls `vcc_connect`.
- `svc_listen` / `svc_accept`: coordinate listen registration and incoming `as_indicate` messages through the socket receive queue and accept backlog.
- `svc_disconnect` / `svc_release`: close registered SVCs, reject queued indications, and release common VCC state.
- `svc_change_qos`: sends `as_modify` and waits for daemon/driver result.
- `svc_setsockopt` / `svc_getsockopt`: handle `SO_ATMSAP` and `SO_MULTIPOINT` before delegating common options.
- `svc_ioctl` / `svc_compat_ioctl`: implement `ATM_ADDPARTY` and `ATM_DROPPARTY`, delegate everything else to common ioctls.
- `atmsvc_init` / `atmsvc_exit`: register/unregister the family.

## Control Flow
All signaling actions set `ATM_VF_WAITING`, enqueue a message to `sigd`, and sleep until the flag clears or the daemon disappears. Connect transitions through `SS_UNCONNECTED`, optional `SS_CONNECTING`, and `SS_CONNECTED`; successful daemon replies fill PVC coordinates and QoS before `vcc_connect`. Listen sockets receive `as_indicate` skbs from `signaling.c`; accept creates a new SVC socket, copies message QoS/address/SAP, connects the new VCC, and sends `as_accept`.

## State and Persistence
Persistent state lives in `atm_vcc`: local/remote SVC addresses, SAP, QoS, VPI/VCI/interface, session/listen/bound/registered/waiting flags, and socket errors. The accept queue stores pending indication skbs that must be rejected on release. Point-to-multipoint status uses `ATM_VF_SESSION` and `sk_err_soft` for endpoint replies.

## Dependencies and Integration
Depends on `signaling.c` for daemon request/reply, `common.h` for VCC creation/data plane/options, `addr.h` for address semantics, and Linux socket locking/wait queues. It is init-net-only.

## Risks and Test Signals
Risks include sleep/wakeup races with daemon exit, signal abort cleanup in connect, accept backlog accounting, queued indication rejection on release, pointer lifetime between listen and accepted sockets, and compat ioctl command correction for `ATM_ADDPARTY`. Test signals include blocking and nonblocking connect, interrupted connect aborts, daemon absence returning `-EUNATCH`, listen backlog full rejection, accept success/failure paths, QoS modification, multipoint add/drop party, and release with pending indications.
