# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/2FS-(1,2)MDS.json

## Purpose
This fixture represents two filesystems where `myfs` has one MDS daemon and `myfs-a` has two MDS daemons. It tests mixed partial/full daemon maps and name disambiguation.

## Important APIs, Types, and Functions
The `myfs` entry contains one `info` daemon named `myfs-b` in state `up:rejoin`. The `myfs-a` entry contains `myfs-a-a` and `myfs-a-b` in `up:active` and `up:standby-replay` states. There are no top-level standbys.

## Control Flow, State, and Persistence
The liveness probe should pass for `myfs-a-a` and `myfs-a-b` on filesystem `myfs-a`, fail for `myfs-a` on filesystem `myfs`, and pass for `myfs-b` on filesystem `myfs`. This proves the probe handles one filesystem having a partial daemon set while another has active plus standby-replay daemons.

## Dependencies and Integration Points
It is embedded by the Go liveness probe test and consumed by the shell script's filesystem-scoped `jq` map lookup.

## Risks
State `up:rejoin` is treated as present and therefore healthy by the probe. If liveness semantics become state-sensitive, this fixture's expected success for `myfs-b` may need reconsideration.

## Test Signals
Signals include success for present daemons regardless of active/rejoin/standby-replay state and failure for absent daemon names in the selected filesystem.
