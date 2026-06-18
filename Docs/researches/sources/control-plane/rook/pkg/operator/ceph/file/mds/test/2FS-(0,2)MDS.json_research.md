# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(0,2)MDS.json

## Purpose
This fixture represents two filesystems where `myfs` has no MDS daemons and `myfs-a` has two MDS daemons. It tests that the liveness probe scopes active daemon matching to the requested filesystem.

## Important APIs, Types, and Functions
The `myfs` entry has empty `info` and `up`. The `myfs-a` entry has `info` names `myfs-a-a` and `myfs-a-b`, with states `up:active` and `up:standby-replay`, and `up.mds_0` pointing to the active daemon. Top-level `standbys` is empty.

## Control Flow, State, and Persistence
When probing `myfs-a-a` or `myfs-a-b` for filesystem `myfs-a`, the script should pass. When probing `myfs-a` or `myfs-b` for filesystem `myfs`, it should fail even though similarly prefixed daemons exist in the other filesystem.

## Dependencies and Integration Points
The fixture validates the `jq` selector `.filesystems[] | select(.mdsmap.fs_name == "$FILESYSTEM_NAME")`, preventing cross-filesystem false positives.

## Risks
The fixture uses filesystem and daemon names with shared prefixes, which is good for disambiguation but can be confusing in failure output. It does not include top-level standbys, so it only covers filesystem-scoped map matching.

## Test Signals
Signals are success for both `myfs-a` filesystem daemons and failure for missing daemons in the `myfs` filesystem.
