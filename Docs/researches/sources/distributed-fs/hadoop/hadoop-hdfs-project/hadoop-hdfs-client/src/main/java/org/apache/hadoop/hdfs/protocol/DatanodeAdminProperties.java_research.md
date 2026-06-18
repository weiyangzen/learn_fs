# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeAdminProperties.java

## Purpose
`DatanodeAdminProperties` models static administrator-specified host configuration for datanode administration. The class is used by `CombinedHostFileManager` to deserialize JSON-based host include/exclude configuration and differs from runtime `DatanodeInfo` state.

## APIs and Behavior
It exposes JavaBean-style getters and setters for `hostName`, `port`, `upgradeDomain`, `adminState`, and `maintenanceExpireTimeInMS`. Defaults are `AdminStates.NORMAL` and `Long.MAX_VALUE` for maintenance expiry. The comments specify `AdminStates.DECOMMISSIONED` for decommission configuration.

## State, Dependencies, and Integration
The class is mutable and intentionally simple for configuration binding. Its key dependency is `DatanodeInfo.AdminStates`, so configured states map directly to runtime administrative state names. Persistence happens outside this class in the JSON host file and NameNode host manager.

## Risks and Test Signals
There is no validation for host name, port range, or maintenance times. Tests should cover JSON deserialization defaults, explicit decommission/maintenance states, upgrade domain propagation into runtime reports, and behavior when invalid ports or null states are supplied by configuration.
