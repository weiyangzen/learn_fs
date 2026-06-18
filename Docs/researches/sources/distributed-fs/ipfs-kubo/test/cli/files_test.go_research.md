# sources/distributed-fs/ipfs-kubo/test/cli/files_test.go

Purpose: broad MFS CLI coverage for `files cp`, `rm`, no-flush limits, offline `files chroot`, and import configuration propagation into MFS operations.

Important APIs/functions: `TestFilesCp`, `TestFilesRm`, `TestFilesNoFlushLimit`, `TestFilesChroot`, `TestFilesMFSImportConfig`, plus UnixFS inspection helpers `UnixFSDataType`, `UnixFSHAMTFanout`, and config `Import.*`/`Internal.MFSNoFlushLimit`.

Control flow: tests validate copying valid UnixFS/raw nodes and rejecting dag-cbor/bad dag-pb, `files rm --flush=false` errors, unflushed operation counters and resets, offline chroot confirmation/replacement/failure cases, CIDv1/raw-leaf/chunker/HAMT settings for `files write`, `files mkdir`, `add --to-files`, CID parity with `ipfs add --trickle`, CID builder preservation through mutations and daemon restart, and config changes after restart.

State/persistence: MFS root mutations, repo config edits, daemon restarts, temporary source files, direct block/DAG puts, and chroot changes while daemon is stopped.

Dependencies/integration: MFS layer, UnixFS importer, HAMT conversion/reversion, config loader, repo lock, CID builder, and CLI validation.

Risks/test signals: high-value user-facing coverage. Some tests rely on exact error text and many parallel daemon instances; MFS multi-block behavior intentionally differs from `ipfs add` unless trickle is used.
