# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/dfs.hosts.json

## Purpose
`dfs.hosts.json` is a host include/exclude manager fixture describing DataNode host entries with optional upgrade domains, admin states, ports, and maintenance expiry.

## Important APIs, types, and functions
The JSON array contains seven objects:
- plain host `host1`
- `host2` with upgrade domain `ud0`
- `host3` decommissioned
- `host4` with upgrade domain `ud2` and decommissioned
- `host5` with port `8090`
- `host6` in maintenance
- `host7` in maintenance with `maintenanceExpireTimeInMS` as a string value

## Control flow
There is no executable control flow. Tests load the JSON into host-entry data structures and verify parser/default behavior.

## State and persistence behavior
The file is static test data. Loaded state should represent host-level administrative membership and maintenance/decommission metadata.

## Dependencies and integration points
It integrates with HDFS hosts-file JSON parsing, DataNode admin-state handling, upgrade-domain support, port-specific entries, and maintenance expiration handling.

## Risks and edge cases
The fixture intentionally mixes absent and present optional fields. The maintenance expiration is encoded as a string, so parsers must handle the expected type. Consumers should preserve port-specific behavior for `host5`.

## Test signals
Useful parser signals include correct defaults for missing fields, correct decommission and maintenance admin states, upgrade-domain extraction, and maintenance expiration parsing.
