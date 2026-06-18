# sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.c` provides convenience serialization and deserialization wrappers for NFSv3, mount, NLMv4, and ACL RPC messages. It adapts typed generated XDR functions to Gluster's `struct iovec` message buffers. The source was read as a complete 481-line file for this report.

## Important APIs, Types, and Functions

The file exports functions named `xdr_to_*args` for decoding request arguments and `xdr_serialize_*res` or `xdr_serialize_*` for encoding responses and lists. Examples include `xdr_to_getattr3args`, `xdr_serialize_getattr3res`, `xdr_to_read3args`, `xdr_serialize_read3res`, `xdr_to_write3args_nocopy`, `xdr_serialize_write3res`, directory operations, fsstat/fsinfo/pathconf/commit wrappers, mount wrappers (`xdr_to_mountpath`, `xdr_serialize_mountres3`, `xdr_serialize_mountbody`, `xdr_serialize_exports`, `xdr_serialize_mountlist`), NLM wrappers, and ACL wrappers.

## Control Flow

Most functions are one-line adapters to `xdr_to_generic`, `xdr_to_generic_payload`, or `xdr_serialize_generic` with the correct generated `xdr_*` procedure. `xdr_to_mountpath` explicitly creates a decode XDR stream over the input iovec and decodes a `dirpath` into caller-provided output storage. `xdr_serialize_exports` explicitly creates an encode stream and serializes the recursive exports list.

## State and Persistence Behavior

The file owns no persistent state. Decode wrappers fill caller-owned typed structs, and encode wrappers write into caller-provided output buffers. Nocopy decode leaves payload bytes referenced through an output iovec instead of copying them into the decoded struct. Any allocations made by lower-level XDR routines follow SunRPC/rpcgen conventions and must be freed by callers using the matching cleanup paths.

## Dependencies and Integration Points

It depends on generated NFS headers (`xdr-nfs3.h`, `nlm4-xdr.h`, `acl3-xdr.h` via the header), `xdr-generic.h`, and `xdr-common.h`. It is built only when GNFS support is enabled and is consumed by the Gluster NFS server/mount/NLM/ACL RPC layers.

## Risks and Edge Cases

Wrapper correctness depends on pairing every typed argument/result with the exact generated XDR function. Buffer size validation is delegated to XDR routines; null iovec bases return `-1` in explicit helpers and generic helpers. Nocopy write/read paths require callers to respect that payload bytes are not stored in the decoded structure. Recursive export/mount list encoding can still be sensitive to deeply nested lists.

## Test Signals

Tests should encode/decode each NFSv3 procedure, mount exports/list responses, NLM lock/share/test/freeall paths, ACL get/set paths, null-buffer failures, short-buffer failures, and nocopy write payload extraction. Interoperability with an NFSv3 client is the strongest end-to-end signal.
