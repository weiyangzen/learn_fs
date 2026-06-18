# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-mgmt.c

Purpose: manages snapview-server communication with Gluster management to discover and refresh the snapshot list.

Important APIs/functions: `svs_mgmt_init()` creates an RPC client to glusterd using command-line volfile server/address-family settings, registers notify and callback programs, and starts the client. `svs_rpc_notify()` triggers snapshot refresh on RPC connect. `mgmt_cbk_snap()` handles management callbacks indicating snapshot-list changes. `svs_mgmt_submit_request()` serializes XDR requests into iobuf/iobref and submits RPC. `svs_get_snapshot_list()` requests snapshot name/uuid/volume data. `mgmt_get_snapinfo_cbk()` decodes the response dict and swaps `priv->dirents`.

Control flow: init builds transport options, starts RPC, and registers `GF_CBK_GET_SNAPS`. A refresh creates a frame, serializes a dict containing `volname`, and sends `GF_HNDSK_GET_SNAPSHOT_INFO`. The callback unserializes `snap-count`, `snap-volname.N`, `snap-id.N`, and `snapname.N`, allocates a new dirent array, carries forward matching cached `glfs_t` handles from the old array, swaps under `snaplist_lock`, then finalizes stale old handles.

State/persistence: authoritative snapshot state in this translator is `svs_private_t.dirents` plus `num_snaps`. The state is in-memory and refreshed from glusterd; libgfapi handles are preserved for unchanged snapshots and finalized for removed snapshots.

Dependencies/integration: depends on Gluster RPC client, handshake/callback programs, XDR types `gf_getsnap_name_uuid_req/rsp`, dict serialization, iobuf pools, and `SVS_STACK_DESTROY`. It uses `ctx->mgmt` for submission in `svs_mgmt_submit_request`.

Risks/test signals: refresh failure can leave old state intact or fail init depending on call site. The stale-handle transfer depends on matching both snapshot name and uuid. Tests should cover empty list, added/removed snapshots, renamed/recreated snapshots with same name different uuid, RPC connect refresh, malformed dict keys, XDR decode failure, frame cleanup on submit failure, and glfs_fini for stale cached handles.
