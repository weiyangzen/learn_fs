# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.c` implements non-recursive custom XDR routines for GlusterFS readdir and readdirp response lists. It avoids large stack usage from rpcgen's recursive linked-list encoders while preserving the existing wire format. The source was read as a complete 92-line file for this report.

## Important APIs, Types, and Functions

Exports are `xdr_gfx_dirlist_custom`, `xdr_gfx_readdir_rsp_custom`, `xdr_gfx_dirplist_custom`, and `xdr_gfx_readdirp_rsp_custom`. The list-entry helpers serialize one `gfx_dirlist` or `gfx_dirplist` node without recursing into `nextentry`; the response helpers iteratively walk the linked list using `xdr_pointer`.

## Control Flow

Entry helpers encode/decode fixed entry fields and return `TRUE` only if every field succeeds. Response helpers first encode/decode `op_ret`, `op_errno`, and `xdata`, then set a pointer-to-pointer to the list head and loop over `xdr_pointer`. The loop returns `TRUE` when the decoded/encoded pointer is `NULL`; otherwise it advances to the current node's `nextentry` field.

## State and Persistence Behavior

The file owns no persistent state. During XDR decode, `xdr_pointer` can allocate list nodes according to the SunRPC XDR allocator rules. During encode, it walks caller-owned list nodes. It does not free list storage.

## Dependencies and Integration Points

It depends on generated `glusterfs4-xdr.h`, `rpc-pragmas.h`, and Gluster FOP definitions. Generated XDR code or protocol code can select these custom functions instead of recursive rpcgen output for large directory responses.

## Risks and Edge Cases

Wire compatibility depends on matching the generated field order exactly. The iterative loop must advance via `nextentry` after each non-null node; otherwise it would loop forever or corrupt decode output. Very large lists still consume memory and wire bandwidth, but no longer consume one C stack frame per entry. Decode ownership and freeing must match the generated structure's normal cleanup expectations.

## Test Signals

Round-trip encode/decode tests for empty, one-entry, and large readdir/readdirp lists are important. Stress tests with many directory entries should demonstrate bounded stack use. Compatibility tests should compare bytes against rpcgen output for small lists.
