# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/0FS.json

## Purpose
This fixture is a minimal `ceph fs dump` sample with no filesystems and no standby MDS daemons. It is the negative baseline for MDS liveness probe tests.

## Important APIs, Types, and Functions
The JSON contains top-level epoch and compatibility metadata, `default_fscid: -1`, `feature_flags`, an empty `standbys` array, and an empty `filesystems` array.

## Control Flow, State, and Persistence
The fixture is embedded into the liveness probe test. Since both the standby and active MDS lookup paths are empty, a probe for any specific daemon should conclude definite absence and exit with failure.

## Dependencies and Integration Points
It integrates only with the probe test harness and the shell script's `jq` expressions. It models a Ceph cluster with no CephFS/MDS map entries.

## Risks
Because it is minimal, it does not exercise missing fields beyond the empty arrays. If the probe is changed to tolerate empty maps differently, this fixture should remain the strict negative case.

## Test Signals
The expected signal is exit code `1` when probing `myfs-c` or any other absent daemon.
