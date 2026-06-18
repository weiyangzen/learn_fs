# sources/distributed-fs/openafs/src/tools/dumpscan/parsevnode.c

Purpose: parses individual vnode records, including metadata, ACLs, file/directory/symlink data, and optional corruption resynchronization.

Important APIs/functions: `parse_vnode` reads vnode number/uniquifier, records offsets, parses tagged attributes with `vnode_fields`, optionally resyncs with `resync_vnode`, then dispatches to vnode-type callbacks. `store_vnode` fills `afs_vnode` fields and masks. `parse_acl` copies the raw ACL block and can print positive/negative rights via `rights2str`. `parse_vdata` reads data size/offset, handles symlink target buffering, parses directory contents when needed, or skips data.

State/dependencies: uses static `LastGoodVNode` for resync and static symlink buffer reuse. It depends on `dumpfmt.h`, `internal.h`, `afs/acl.h`, `afs/prs_fs.h`, directory parsing, and `match_next_vnode`.

Risks/test signals: static state is not reentrant. Resync heuristics can drop vnodes or seek around corrupt regions, so repaired parses need validation. Callback behavior depends on `DSFLAG_SEEK`; without seeking, callbacks that inspect data can consume the stream.
