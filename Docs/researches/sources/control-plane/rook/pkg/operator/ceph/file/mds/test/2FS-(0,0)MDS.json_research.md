# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(0,0)MDS.json

## Purpose
This fixture represents two filesystems, `myfs` and `myfs1`, both with empty MDS maps and no standbys. It is a multi-filesystem negative case for the liveness probe.

## Important APIs, Types, and Functions
The JSON has two `filesystems` entries with `mdsmap.fs_name` values `myfs` and `myfs1`, empty `info` maps, empty `up` maps, and `max_mds: 1`. Top-level `standbys` is empty.

## Control Flow, State, and Persistence
The fixture is embedded data consumed by shell-based probe tests. The probe can find the requested filesystem but cannot find the requested daemon in active or standby locations, so it should fail.

## Dependencies and Integration Points
It tests the script's filesystem selection logic independently of daemon membership. This ensures an existing filesystem with no daemon does not falsely pass due to the filesystem name alone.

## Risks
The fixture includes full Ceph compatibility metadata that tests do not inspect. Its primary value is the empty `info` and `standbys`; if Ceph represents empty maps differently, probe parsing may need adjustment.

## Test Signals
The expected signal is exit code `1` for probing `myfs-a` on filesystem `myfs`.
