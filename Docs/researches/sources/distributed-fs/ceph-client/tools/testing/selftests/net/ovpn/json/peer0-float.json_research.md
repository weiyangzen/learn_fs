# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-float.json

## Purpose
`peer0-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer0 in the asymmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 9 event(s), event type(s) peer-del-ntf, peer-float-ntf, peer id sequence `[1, 2, 3, 1, 2, 3, 4, 5, 6]`, and delete reason set `expired, userspace`. It also expects float notifications to remote IPv4 addresses 10.10.1.3, 10.10.2.3, 10.10.3.3.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.
