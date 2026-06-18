# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/options.h

## Purpose
`options.h` defines libhdfs++ client configuration data, including NameNode HA service metadata and operational tunables.

## Important APIs, Control Flow, and State
`NamenodeInfo` stores nameservice, node name, and URI and provides host/port helpers. `Options` stores default filesystem URI, RPC/data timeouts, retry/failover behavior, cache and Kerberos/SASL settings, thread counts, block reader settings, and `services`, a map of nameservices to configured NameNodes. It is a plain configuration carrier populated by configuration parsers/builders and copied into `FileSystem`.

## Dependencies and Integration Points
It depends on `URI`, string, vector, and map. `ConfigParser`, `FileSystem::New`, HA connection logic, RPC retry, and authentication code consume these fields.

## Risks and Test Signals
Defaults and Hadoop XML key mapping are compatibility-sensitive. HA service maps must preserve all endpoints. Tests should validate default construction, `NamenodeInfo` host/port extraction, parser-to-options mapping, timeout units, retry limits, Kerberos/SASL toggles, and copy behavior into filesystems.
