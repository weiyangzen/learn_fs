# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/resources/core-site.xml

## Purpose
Test-resource `core-site.xml` that overrides Hadoop NFS test ports so the Hadoop NFS server and mount daemon do not collide with common system NFS services.

## Important Properties
`nfs.server.port` is set to `2079`, intentionally different from the default NFS port `2049`. `nfs.mountd.port` is set to `4272`, different from the default Hadoop mountd port `4242`. The file contains only these two properties under a Hadoop `<configuration>` root.

## Control Flow, State, and Integration
The file is loaded as a standard Hadoop test resource by configurations used in the hadoop-hdfs-nfs test module. Runtime tests may still override ports to `0` for ephemeral allocation, but this file provides safe defaults when a test or local run relies on classpath configuration. There is no application state or persistence beyond process-local service binding behavior.

## Dependencies, Risks, and Test Signals
The file depends on Hadoop configuration's deprecated/current key resolution; these property names match legacy keys also covered by `TestRpcProgramNfs3.testDeprecatedKeys()`. A risk is that fixed ports can still conflict if multiple test JVMs use this resource without overriding to ephemeral ports. The signal is indirect: NFS test startup succeeds on non-privileged, non-default ports.
