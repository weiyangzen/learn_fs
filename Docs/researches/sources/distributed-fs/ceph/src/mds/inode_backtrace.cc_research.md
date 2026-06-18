<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/inode_backtrace.cc -->
## sources/distributed-fs/ceph/src/mds/inode_backtrace.cc

`inode_backtrace.cc` implements serialization, dumping, test fixtures, comparison, and stream output for inode backpointers/backtraces. These structures are used as standalone ancestry records, commonly stored with object metadata to reconstruct or verify where an inode lives in the namespace.

`inode_backpointer_t` encodes directory inode, dentry name, and child version using struct version 2, with `decode_old` for legacy unframed vector entries. `inode_backtrace_t` encodes inode number, ordered ancestor vector, current data pool, and old pools using struct version 5. Decode rejects very old struct versions by returning early for `struct_v < 3`, handles pre-v4 ancestor layout manually, and only reads pool fields at v5+.

The key behavior is `inode_backtrace_t::compare`. It compares two backtraces for the same inode by ancestor versions and dentries, reports whether dentries are equivalent, and flags divergent history when version ordering contradicts path differences. The comparator uses the first ancestor as initial freshness signal, then walks the common prefix while tracking incompatible version direction.

Dependencies include Ceph buffer encoding macros, `Formatter`, `inodeno_t`, `version_t`, and STL strings/vectors. Integration points are backtrace storage during journal segment expiry (`store_backtrace` in `journal.cc`), metadata scrub/repair, object locator changes across pools, and diagnostic formatting.

Risks: old version decode returns a default object silently for ancient data, compare assumes same-inode precondition but does not enforce it, and pool/old-pool history must match actual backtrace writes during data-pool migration. Test signals include generated encode/decode instances, legacy ancestor decoding, compare cases for equal paths/newer versions/divergent versions, and journal expiry tests that commit backtraces in current and old pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/inode_backtrace.cc -->
