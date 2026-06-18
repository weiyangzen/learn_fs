# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapMapping.java

Purpose: immutable value object for one portmap mapping tuple: program, version, transport, and port.

Important APIs/types/functions: constants `TRANSPORT_TCP` and `TRANSPORT_UDP`, constructor, `serialize`, static `deserialize`, `getPort`, static `key`, and `toString`.

Control flow: serialization writes four integers to XDR; deserialization reads four integers. `key` joins program, version, and transport, intentionally excluding port so set/unset/getport address the mapping identity.

State and persistence: immutable fields; no persistence. Instances are stored in `RpcProgramPortmap`'s in-memory map.

Dependencies and integration: used by `PortmapRequest`, `PortmapResponse`, `RpcProgram`, and `RpcProgramPortmap`.

Risks: no validation of transport, version, program, or port ranges. No equals/hashCode, so map identity uses string keys rather than object keys.

Test signals: portmap tests cover serialization, key behavior, and getport values.
