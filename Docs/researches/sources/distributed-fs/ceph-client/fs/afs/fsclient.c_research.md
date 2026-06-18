# sources/distributed-fs/ceph-client/fs/afs/fsclient.c

Purpose: `fsclient.c` is the AFS File Server RPC marshal/unmarshal layer. It defines call types, request encoders, reply delivery state machines, and exported RPC issue functions used by higher-level operations.

Important APIs and functions: exported issuers cover status, data fetch/store, create, mkdir, remove file/dir, link, symlink, rename, setattr, volume status, lock set/extend/release, give-up-callbacks, capabilities, inline bulk status, and ACL fetch/store. Core decoders include `xdr_decode_AFSFid()`, `xdr_decode_AFSFetchStatus()`, `xdr_decode_AFSCallBack()`, `xdr_decode_AFSVolSync()`, and `xdr_decode_AFSFetchVolumeStatus()`.

Control flow: each issuer allocates an `afs_call`, encodes opcode and XDR parameters with padding, attaches FID/tracing metadata, then starts an operation call or direct call. Delivery functions use fixed reply transfer or staged extraction for variable data, strings, capabilities, inline bulk arrays, and ACLs. Fetch/store/setattr choose 64-bit opcodes when the server advertises FS64. FetchData can asynchronously stream bytes into a netfs subrequest before decoding trailing status/callback/volsync.

State and persistence: decoded status/callback data lands in `afs_vnode_param.scb` for later commit. Calls carry operation IDs, buffers, iterators, temp values, server/peer/probe state, write iterators, and async/cancel hooks. Capability probes update endpoint/server state through `fs_probe.c`; lock call types invoke `afs_lock_op_done()`.

Dependencies and integration points: protocol constants, rxrpc call infrastructure, netfs subrequests, `struct afs_operation`, probe state, lock manager, ACL structures, and YFS selection by callers.

Risks: XDR size and padding bugs affect names, symlinks, ACLs, and strings. Status decode must handle OpenAFS InlineBulkStatus quirks without masking real protocol errors. FetchData length handling must avoid overrun/underrun and mark EOF correctly. InlineBulkStatus count mismatches are fatal protocol errors.

Test signals: valid/malformed status decode, FetchData short/exact/long/zero/EOF/cancel, request padding for mutating RPCs, StoreData/setattr FS64 selection, volume string length rejection, lock done hook, GiveUpAllCallbacks, capabilities probes, InlineBulkStatus aborts/count mismatch, and ACL round trips.
