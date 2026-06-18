# sources/distributed-fs/ceph/src/mds/cephfs_features.cc

Purpose: Implements name lookup, reverse lookup, stringification, and formatter dumping for CephFS client/MDS feature bits.

Important APIs/functions: `cephfs_feature_name`, `cephfs_feature_from_name`, `cephfs_stringify_features`, and `cephfs_dump_features`. `feature_names` is a fixed array aligned to `CEPHFS_FEATURE_MAX + 1`.

Control flow: Name lookup returns the indexed string unless the id is beyond the known array. Reverse lookup rejects `"reserved"` and performs a linear scan. Stringify and dump iterate the array, outputting only bits set in `feature_bitset_t`.

State and persistence behavior: Stateless utility code. Feature bits are serialized elsewhere as bitsets; this file only provides human-readable views.

Dependencies and integration points: Depends on `cephfs_features.h`, `mdstypes.h` for `feature_bitset_t`, `Formatter`, `CachedStackStringStream`, and `fmt::format`. Used by session feature negotiation, admin output, and logs.

Risks: `cephfs_feature_name` checks `id > feature_names.size()` rather than `>=`, so `id == size()` would index past the array. Any new macro in the header must update the array and keep the static assert passing.

Test signals: Unit test every feature id, unknown id at `size()` and greater, reserved reverse lookup, stringify ordering, and formatter field names.
