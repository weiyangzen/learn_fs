<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/snap.cc -->
## sources/distributed-fs/ceph/src/mds/snap.cc

`snap.cc` implements CephFS MDS snapshot descriptors and snap realm records. It provides versioned encoding/decoding, formatter dumps, generated test instances, and stream output for `SnapInfo`, `snaplink_t`, and `sr_t`.

`SnapInfo` stores one snapshot id, source inode, timestamp, name, alternate name, metadata map, and a mutable cached long name. Encoding is version 4 with metadata at v3+ and alternate name at v4+. `get_long_name` lazily formats `_<name>_<ino>` and invalidates by checking the cached string against current `name` shape. `snaplink_t` records a past parent inode and the first snap id for that parent relationship.

`sr_t` is the durable snap realm version: sequence, creation/destruction watermarks, current-parent-since, snap map, past parent map, past parent snap set, last-modified timestamp, change attr, and flags for parent-global, subvolume, and snapdir visibility. Decode handles an odd v2 extra byte, v5+ past parent snaps, v6+ flags, and v7+ timestamp/change attr. It upgrades old records so snapdir visibility is enabled in memory for pre-v8 data.

Dependencies are Ceph snap/object/utime/buffer types and `Formatter`. Integration points include `SnapRealm`, snapshot table/event replay, inode snap blobs in `journal.cc`, subvolume handling, and admin dumps.

Risks: cached `long_name` invalidation is string-shape based; old decode paths need precise compatibility; flags defaulting affects user-visible `.snap` behavior after upgrade; and snap maps are central to correct clone/past-parent lookup. Test signals include encode/decode across struct versions, visibility flag upgrade cases, snap realm dump output, long-name cache changes after rename/name mutation, and journal replay of snap blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/snap.cc -->
