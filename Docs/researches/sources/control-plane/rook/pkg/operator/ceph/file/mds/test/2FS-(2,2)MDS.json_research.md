# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(2,2)MDS.json

## Purpose
This fixture represents two filesystems with two MDS daemons each. It is the full multi-filesystem positive case for the liveness probe and checks that similarly named daemon sets do not collide.

## Important APIs, Types, and Functions
Filesystem `myfs` has `info` names `myfs-a` and `myfs-b`, with states `up:standby-replay` and `up:active`. Filesystem `myfs-a` has `info` names `myfs-a-a` and `myfs-a-b`, with states `up:active` and `up:standby-replay`. Both have `max_mds: 1`, one active rank in `up`, and no top-level standbys.

## Control Flow, State, and Persistence
The fixture is embedded static JSON. The probe should pass for `myfs-a-a` on filesystem `myfs-a` and also pass for daemons in `myfs` when probed with that filesystem. Membership remains scoped to the selected filesystem.

## Dependencies and Integration Points
It validates the probe script against a realistic multi-filesystem MDS map with active and standby-replay daemons in each filesystem.

## Risks
The fixture's shared prefixes make it sensitive to any future bug that changes exact-name matching into substring matching. The probe still does not evaluate the health meaning of each MDS state beyond presence.

## Test Signals
The expected signal is successful probe exit for present daemon IDs in their respective filesystem maps, especially `myfs-a-a` under `myfs-a`.
