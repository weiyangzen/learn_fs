# sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe.sh

## Purpose
This bash template is the runtime MDS liveness probe. It avoids restarting MDS pods unless the daemon is definitely absent from the Ceph MDS map, which reduces the risk of destabilizing CephFS during monitor or cluster failure conditions.

## Important APIs, Types, and Functions
Template variables are `MDS_ID`, `FILESYSTEM_NAME`, `KEYRING`, and `CMD_TIMEOUT`. The script sets `CEPH_ARGS` with the keyring, runs `ceph fs dump` with monitor host/member environment variables and JSON output, parses standby and active MDS names with `jq`, exits `0` if the daemon is present, and exits `1` only when the daemon is absent from both standby and active maps.

## Control Flow, State, and Persistence
If `ceph fs dump` returns nonzero, the script prints the output and exits `0` because health cannot be determined safely. If the command succeeds, it computes `standbyMds` from `.standbys[].name` and `activeMds` from the matching filesystem's `.mdsmap.info[].name`. Presence in either path passes the probe; absence fails. The script has no persistent state.

## Dependencies and Integration Points
The script requires `ceph`, `jq`, mounted keyring credentials, `ROOK_CEPH_MON_HOST`, and `ROOK_CEPH_MON_INITIAL_MEMBERS`. It is rendered by `livenessprobe.go` and embedded into the MDS container's Kubernetes exec liveness probe.

## Risks
Invalid JSON or `jq` errors can produce values that do not equal `true`; in current tests some invalid cases pass because shell control flow ultimately avoids a definite absence signal. Missing `jq` in the container would likely make the probe fail on otherwise valid Ceph output. The script deliberately passes on Ceph command failures, so it cannot detect every unhealthy daemon state.

## Test Signals
Probe tests should confirm pass for active and standby daemons, fail for definitely absent daemons or filesystems, pass on Ceph command errors, and cover multi-filesystem maps where similarly named MDS daemons belong to different filesystems.
