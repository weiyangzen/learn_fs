<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/snap.h -->
## sources/distributed-fs/ceph/src/mds/snap.h

`snap.h` declares persistent MDS snapshot metadata structures. `SnapInfo` is a generic snapshot descriptor; `snaplink_t` records historical parent realm links; `sr_t` carries a complete durable version of a `SnapRealm`.

`SnapInfo` exposes encode/decode/dump/test generation, equality, stream output, and `get_long_name`. Fields are snapshot id, inode, timestamp, name, alternate name, cached long name, and metadata. Equality intentionally ignores alternate name, long-name cache, and metadata. `snaplink_t` has inode and first-snap fields plus standard encode/dump/test/stream APIs.

`sr_t` provides flag mutators for parent-global, subvolume, and snapdir visibility, plus encode/decode/dump/test/print. Durable fields include realm sequence, creation/destruction ids, parent-history maps, snap set, last modification time, change attribute, and flags. The default flags enable snapdir visibility.

State/persistence behavior is tightly tied to namespace snapshots. `seq` versions realm changes, `last_created`/`last_destroyed` bound visible snapshot sets, and past-parent state supports resolving historical paths after realm movement. `change_attr` tracks attribute mutations. The flag helpers define in-memory semantics that the implementation preserves through versioned decode upgrades.

Dependencies are Ceph `snapid_t`, `inodeno_t`, `utime_t`, buffer encoders, object types, and STL maps/sets. Integration points include `SnapRealm`, MDCache snapshot propagation, journal metablob snap blobs, subvolume metadata, and admin formatting.

Risks: equality omits metadata/alternate name, so callers must not use it for full record equivalence; default snapdir visibility is compatibility-sensitive; and parent history maps must be kept consistent with realm moves. Test signals are generated encode/decode, flag mutation tests, equality semantics checks, snap realm migration/history tests, and upgrade decode fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/snap.h -->
