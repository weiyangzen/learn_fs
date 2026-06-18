<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/files.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/files.go

## Purpose

Implements the `ipfs files` command family for MFS (Mutable File System) operations: read, write, move, copy, list, mkdir, stat, rm, flush, CID format changes, chmod, touch, and recovery chroot.

## Important APIs, Types, and Functions

`FilesCmd` registers all MFS subcommands and the shared `--flush` option. `updateNoFlushCounter` enforces `Internal.MFSNoFlushLimit`. Major handlers include `filesStatCmd`, `filesCpCmd`, `filesLsCmd`, `filesReadCmd`, `filesMvCmd`, `filesWriteCmd`, `filesMkdirCmd`, `filesFlushCmd`, `filesChcidCmd`, `filesRmCmd`, `filesChmodCmd`, `filesTouchCmd`, and `filesChrootCmd`. Helpers include `statNode`, `walkBlock`, `getNodeFromPath`, `getPrefix`, `checkPath`, `getFileHandle`, and `removePath`.

## Control Flow

Handlers validate absolute MFS paths with `checkPath`, get the node through `cmdenv`, and operate on `nd.FilesRoot`. Mutating commands call `updateNoFlushCounter` unless they always flush. `stat` resolves a node, computes UnixFS metadata, and optionally walks an offline DAGService to report local availability. `cp` supports lazy `/ipfs/` to MFS references, validates root codecs as UnixFS dag-pb or raw, optionally creates parents, force-unlinks files, puts the node, and flushes target plus parent. `write` opens or creates a file, applies CID/hash/raw-leaf options, seeks/truncates/limits input, copies bytes, closes, and flushes parent. `rm` rejects `--flush=false`, removes one or more paths, and emits per-path errors before returning aggregate failure.

## State and Persistence Behavior

Most commands mutate MFS DAG state and, when flush is true, persist updated roots and clear parent caches. `--flush=false` defers durability and increments a global unflushed operation counter. `files flush` persists a path and resets the counter. `files chroot` opens the repo while the daemon is stopped and directly rewrites `node.FilesRootDatastoreKey`, making it a recovery-grade persistent mutation.

## Dependencies and Integration Points

Uses boxo MFS, UnixFS, merkledag, blockstore, offline exchange, Kubo config/import defaults, fsrepo/datastore, CoreAPI resolution, CID/multihash builders, and command environment helpers. Integrates with GC safety through MFS root persistence and with import config for CID/hash/HAMT directory behavior.

## Risks and Edge Cases

`--flush=false` trades consistency for speed and can lose data on daemon crash before flush. The global no-flush counter is process-wide and caches the config limit on first use. Lazy `cp` can protect partial DAGs from GC without fetching full content. `files chroot` is destructive and requires confirmation but bypasses live MFS machinery. Race conditions are acknowledged around created file type checks.

## Test Signals

`files_test.go` covers rejection of non-UnixFS dag-cbor-like copy roots. Command tree tests cover subcommand registration. Important missing tests include no-flush limit behavior, parent flushing, write/truncate/count combinations, rm aggregate errors, chcid root rejection, stat locality, chmod/touch metadata, and chroot validation/persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/files.go -->
