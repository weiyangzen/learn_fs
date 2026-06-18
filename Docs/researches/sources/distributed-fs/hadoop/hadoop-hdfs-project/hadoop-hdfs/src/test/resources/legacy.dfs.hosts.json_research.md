# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/legacy.dfs.hosts.json

## Purpose

`legacy.dfs.hosts.json` is a legacy JSON-lines host include/exclude fixture for HDFS DataNode admin-state parsing. The complete 7-line file was read. It preserves compatibility coverage for host records that are not wrapped in a single JSON array.

## Important APIs, Types, and Functions

Each line is an independent JSON object with keys such as `hostName`, `upgradeDomain`, `adminState`, `port`, and `maintenanceExpireTimeInMS`. The fixture exercises host states `DECOMMISSIONED` and `IN_MAINTENANCE`, a numeric `port`, missing optional fields, and a string-valued maintenance expiration. Consumers are HDFS host-file managers, JSON host readers, and DataNode decommission/maintenance tests.

## Control Flow

The host reader scans records line by line, decodes each object, defaults missing fields, and constructs host/property entries. It must accept simple hosts (`host1`), upgrade-domain hosts (`host2`, `host4`), decommissioned hosts (`host3`, `host4`), explicit-port host (`host5`), and maintenance hosts (`host6`, `host7`).

## State and Persistence Behavior

The file is static administrative input. When loaded, it affects in-memory include/exclude host maps and DataNode admin-state decisions, but it does not itself persist NameNode state.

## Dependencies and Integration Points

It integrates with HDFS DataNodeManager host configuration refresh, DFSAdmin refresh commands, decommission tracking, maintenance mode scheduling, and upgrade-domain-aware placement tests.

## Risks and Edge Cases

Risks include parsers assuming a JSON array instead of JSON lines, rejecting unknown/missing optional fields, mishandling string versus numeric maintenance expiration, failing to default absent ports or admin states, and losing backward compatibility for legacy host files.

## Test Signals

Signals are successful parsing of seven host entries, expected admin states for `host3`, `host4`, `host6`, and `host7`, correct `host5:8090` handling, and no parse failure from the line-oriented format.
