# sources/distributed-fs/ceph/src/mds/MDSAuthCaps.cc

## Purpose

`MDSAuthCaps.cc` implements parsing, matching, merging, serialization text, and authorization checks for CephFS MDS capability strings. It turns user/keyring strings such as `allow rw path=/foo fsname=myfs root_squash network ...` into grant objects and evaluates whether a client may perform a requested filesystem operation.

## Important Functions And Control Flow

`MDSCapParser` is a Boost.Spirit grammar. It parses one or more `allow` grants separated by comma or semicolon. A grant has a cap spec (`*`, `all`, `r`, `rw`, and combinations including `f`, `p`, `s`), optional `fsname`, optional `path`, optional `root_squash`, optional `uid`, optional `gids`, and optional network. Parsed grants are stored in `MDSAuthCaps`.

`MDSCapMatch::normalize_path` strips leading slashes from stored match paths. `match` first checks filesystem name, then UID/GID constraints when a UID is specified, then calls `match_path`. `match_path` strips trailing slashes from the configured path and enforces subtree matching without accepting prefix collisions such as `/foo` matching `/food`.

`MDSCapGrant::parse_network` parses the configured network into `entity_addr_t` and prefix length. `MDSAuthCaps::parse` handles the legacy string `allow` as `RWPS`, runs the grammar, sorts grant GIDs, parses networks, and clears all grants on failure. `is_capable` iterates grants, filters invalid/nonmatching networks, checks match predicates and basic read/write bits, applies root squash to root write attempts, validates special bits (`MAY_SET_VXATTR`, `MAY_SNAPSHOT`, `MAY_FULL`), and if the grant is UID-scoped, applies chown/chgrp and Unix owner/group/other mode checks.

`merge_one_cap_grant` and `merge` support `fs authorize` style idempotent grant merging by fsname/path, updating permissions and only adding `root_squash`, not removing it. `to_string` and stream operators render capabilities for diagnostics and keyring output.

## State And Persistence Behavior

This file does not persist data directly, but parsed caps are security-critical state attached to authenticated sessions and keyrings. Failure to parse clears `grants`, preventing partial malformed capabilities from being retained. Network parse state is cached in each grant as `network_parsed`, `network_prefix`, and `network_valid`. Merge behavior is intentionally monotonic for `root_squash` to avoid authorizing commands that silently reduce an existing restriction.

## Dependencies And Integration Points

The implementation uses Boost.Spirit/Qi, Boost.Phoenix, Ceph address parsing helpers (`parse_network`, `network_contains`), `mdstypes.h` operation masks, and Ceph debug logging. `MDSDaemon` calls `MDSAuthCaps::parse` during messenger authentication and session accept, and command handling uses `Session::auth_caps.allow_all()` for privileged tell commands.

## Risks And Test Signals

Primary risks are authorization bypass via path-prefix mistakes, UID/GID list ordering assumptions, malformed network handling, and inconsistent legacy grammar behavior. Tests should cover quoted/unquoted paths, leading/trailing slash normalization, `/foo` versus `/food`, wildcard and empty fs names, root-squash write denial for UID/GID 0, set-vxattr/snapshot/full bits, chown/chgrp constraints, network inclusion/exclusion, parse failure clearing grants, and merge idempotency.
