# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-handshake.c

## Purpose

`client-handshake.c` implements connection negotiation for the protocol/client xlator. It discovers server-supported programs, optionally queries the portmapper for the brick port, sends `SETVOLUME`, records connection identity/version data, notifies parents of child status, and coordinates saved-fd reopening after reconnect.

## Important APIs, types, and functions

- `client_handshake()` starts negotiation by submitting a dump/version request through `conf->dump`.
- `client_dump_version_cbk()` decodes `gf_dump_rsp`, checks for portmap support, selects `clnt4_0_fop_prog`, then calls `client_setvolume()`.
- `select_server_supported_programs()` chooses the v2/4.x fop program and sets RPC auth to `AUTH_GLUSTERFS_v3`.
- `client_query_portmap()` and `client_query_portmap_cbk()` request a brick port from glusterd/portmap and reconfigure `conf->rpc`.
- `client_setvolume()` serializes the xlator options dict with fop/mgmt versions, process uuid, process name, client version, volume id, volfile metadata, subdir mount, lock version, and opversion.
- `client_setvolume_cbk()` handles authentication/volume errors, validates volume id, records `conf->child_up`, marks `conf->connected`, and calls `client_post_handshake()`.
- `client_post_handshake()`, `client_child_up_reopen_done()`, `client_reopen_done()`, and `client_attempt_reopen()` manage fd reopen gating and delayed `CHILD_UP` notification.
- `protocol_client_reopenfile_v2()` and `protocol_client_reopendir_v2()` resend open/opendir for saved fds.
- `clnt_handshake_prog`, `clnt_dump_prog`, and `clnt_pmap_prog` register RPC program metadata and procedure names.

## Control flow

The normal connection path is `client_handshake()` -> `client_dump_version_cbk()` -> `select_server_supported_programs()` -> `client_setvolume()` -> `client_setvolume_cbk()` -> `client_post_handshake()`. If the server advertises portmap, the dump callback sends `PORTBYBRICK`; the portmap callback reconfigures the RPC remote port, sets quick-reconnect flags, disconnects the current transport, and lets reconnect continue against the brick port.

After successful `SETVOLUME`, `client_post_handshake()` scans `conf->saved_fds` under `conf->fd_lock`. Fds with `remote_fd == -1` and no strict-lock-blocking lock context are moved to a temporary reopen list and assigned `client_child_up_reopen_done`. Parent `CHILD_UP` is delayed until all reopen callbacks decrement `conf->reopen_fd_count` to zero. If no eligible fd needs reopening, parents are notified immediately.

Single-fd lazy reopen is separate: fd-based fops can detect anonymous-fd fallback and later call `client_attempt_reopen()`. That function rate-limits by `CLIENT_REOPEN_MAX_ATTEMPTS`, marks the fdctx as in-progress by swapping `reopen_done`, removes it from `saved_fds`, and dispatches reopen.

## State and persistence behavior

State is held in `clnt_conf_t`: selected RPC programs, connection flags, `client_id`, `child_up`, `connected`, `quick_reconnect`, `skip_notify`, `portmap_err_logged`, `disconnect_err_logged`, `setvol_count`, `reopen_fd_count`, `saved_fds`, and the global volume id in `ctx->volume_id`. Fd reopen state is held in each `clnt_fd_ctx_t`: `remote_fd`, `reopen_done`, `released`, `reopen_attempts`, `is_dir`, `flags`, and `gfid`. The process uuid sent in `SETVOLUME` deliberately includes context id, graph id, pid, host, translator name, and reconnect counter so server-side resources are not reused across reconnects.

## Dependencies and integration points

This file depends on the RPC client, XDR types from `rpc-common-xdr.h`, `xdr-rpc.h`, `portmap-xdr.h`, protocol fop program from `client-rpc-fops_v2.c`, fd context helpers from `client-helpers.c`, event dispatch in `client.c`, dict serialization, graph/context options, and message IDs from `client-messages.h`. It integrates with parent translators through `GF_EVENT_CHILD_UP`, `GF_EVENT_CHILD_CONNECTING`, `GF_EVENT_AUTH_FAILED`, and `GF_EVENT_VOLFILE_MODIFIED`.

## Risks and edge cases

- `client_attempt_reopen()` reopens only when `reopen_attempts == CLIENT_REOPEN_MAX_ATTEMPTS`, incrementing otherwise; this is a deliberate delay/throttle but easy to misread as an off-by-one.
- Strict locks suppress fd reopen for fds with lock state, causing later fd operations to fail rather than silently use a reopened fd without recovered locks.
- If reopen submission fails, the code calls `fdctx->reopen_done()` with the prior remote fd value; child-up delay accounting still depends on the callback path completing.
- `client_setvolume_cbk()` treats auth failures and early subdir-mount ENOENT specially so mount startup can fail while background reconnect semantics continue for other errors.
- Volume-id mismatch is fatal for regular volumes but skipped for snapd, so tests must distinguish snapshot and non-snapshot remotes.
- Portmap callback always disconnects after reconfiguration; correctness depends on reconnect code honoring `quick_reconnect` and `skip_notify`.

## Test signals

Useful tests include server program selection, old-protocol behavior, portmap reconfiguration for TCP and RDMA brick names, SETVOLUME dict contents, auth failure and subdir-mount failure notification, volume-id mismatch, child_up false deferral, reconnect with zero saved fds, reconnect with multiple saved files/dirs, release racing with reopen, strict-lock reopen suppression, and lazy reopen after anonymous-fd fallback.
