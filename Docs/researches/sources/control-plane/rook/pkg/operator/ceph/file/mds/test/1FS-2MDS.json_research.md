# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/1FS-2MDS.json

## Purpose
This fixture represents one CephFS filesystem with one daemon in the filesystem MDS map and one daemon in the top-level standby list. It tests both active/in-filesystem and standby probe success paths, plus absent daemon and wrong-filesystem failures.

## Important APIs, Types, and Functions
The top-level standby list includes `myfs-b`. The single filesystem has `mdsmap.fs_name: myfs`, `max_mds: 1`, `up.mds_0: 36794`, and `info` containing daemon `myfs-a` in state `up:creating`. The liveness probe treats any `info[].name` for the selected filesystem as active enough for success.

## Control Flow, State, and Persistence
The fixture is static embedded data. The probe should pass for `myfs-a` on filesystem `myfs`, pass for `myfs-b` via the standby list, fail for an absent daemon like `myfs-c`, and fail when the requested filesystem name does not match.

## Dependencies and Integration Points
It integrates with the liveness probe script's active MDS lookup under `.filesystems[] | select(.mdsmap.fs_name == ...) | .mdsmap.info`, and with standby lookup under `.standbys`.

## Risks
The active daemon state is `up:creating`, not `up:active`; the probe intentionally checks membership rather than state. If future behavior should require active state, this fixture would need updated expectations.

## Test Signals
Signals are success for `myfs-a` and `myfs-b`, failure for `myfs-c`, and failure when probing filesystem `myfs1` with daemon `myfs-a`.
