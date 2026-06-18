# sources/distributed-fs/ceph/src/mds/MDSAuthCaps.h

## Purpose

`MDSAuthCaps.h` declares the data model and public authorization API for CephFS MDS capabilities. It defines operation masks, grant specs, match criteria, grant records, and the `MDSAuthCaps` container used by authenticated clients and daemon command paths.

## Important APIs And Types

The Unix-style operation mask includes `MAY_READ`, `MAY_WRITE`, `MAY_EXECUTE`, `MAY_CHOWN`, `MAY_CHGRP`, `MAY_SET_VXATTR`, `MAY_SNAPSHOT`, and `MAY_FULL`. `MDSCapSpec` stores cap bits (`ALL`, `READ`, `WRITE`, `SET_VXATTR`, `SNAPSHOT`, `FULL`) plus convenience combinations such as `RWPS` and `RWFPS`. Its `allows` method only covers read/write gating; special bits are checked separately by `is_capable`.

`MDSCapMatch` stores optional `uid`, `gids`, subtree `path`, `fs_name`, and `root_squash`. It provides `normalize_path`, `match`, `match_path`, `match_fs`, and versioned encode/decode helpers. `MDSCapAuth` is a compact encoded readable/writeable match used for passing cap-auth summaries. `MDSCapGrant` combines `MDSCapSpec`, `MDSCapMatch`, and optional network parse state.

`MDSAuthCaps` owns a vector of grants. Public methods include `clear`, `set_allow_all`, `parse`, `merge_one_cap_grant`, `merge`, `allow_all`, `is_capable`, `path_capable`, `fs_name_capable`, `get_cap_auths`, `root_squash_in_caps`, and `to_string`.

## State And Persistence Behavior

`MDSCapMatch` and `MDSCapAuth` are encoded with Ceph `ENCODE_START` version 1, so their wire/storage shape is explicit. `MDSCapGrant` network parse fields are runtime cache state and are not encoded in this header. `MDSAuthCaps` stores grants privately; callers must go through parsing/merging APIs to mutate them. `set_allow_all` normalizes universal access into a single all-match grant.

## Dependencies And Integration Points

The header depends on Ceph encoding, `entity_addr_t`, and standard string/vector types. It is consumed by `MDSDaemon`, sessions, auth/keyring handling, and any path permission checks that need to ask whether an authenticated identity can access a filesystem/path/mode combination.

## Risks And Test Signals

The separation between read/write `allows` and special-operation bits is easy to misuse; callers should use `is_capable` rather than testing `MDSCapSpec` directly. Encoding compatibility for `MDSCapMatch` and `MDSCapAuth` should be tested with round-trip cases. Security tests should validate that private `grants` cannot be left partially parsed after failed `parse`, and that `allow_all`, `fs_name_capable`, and `root_squash_in_caps` agree with full `is_capable` semantics where expected.
