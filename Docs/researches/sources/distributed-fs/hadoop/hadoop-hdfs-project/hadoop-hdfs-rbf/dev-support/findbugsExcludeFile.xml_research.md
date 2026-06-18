# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/dev-support/findbugsExcludeFile.xml

## Purpose
FindBugs/SpotBugs exclusion filter for the HDFS Router-Based Federation module. It suppresses generated federation protocol classes and two intentional representation-exposure findings used by router-admin bulk add support.

## Important Rules
The first `<Match>` excludes the generated package `org.apache.hadoop.hdfs.federation.protocol.proto`, where static analysis findings are expected to be noisy and not hand-maintained. Two additional matches target `org.apache.hadoop.hdfs.tools.federation.AddMountAttributes`: method `getNss` suppresses `EI_EXPOSE_REP`, and method `setNss` suppresses `EI_EXPOSE_REP2`.

## Control Flow, State, and Integration
This XML is consumed by the module's static-analysis build configuration. It does not execute code; it filters analyzer output so generated protobuf artifacts and intentional mutable-list accessors do not fail checks. There is no runtime state, only persistent build policy.

## Dependencies, Risks, and Test Signals
The suppressions depend on fully qualified class/package names and bug-pattern identifiers. The main risk is over-broad package suppression hiding real issues if hand-written code is added under the generated proto package. The `AddMountAttributes` exclusions deliberately accept mutable representation exposure, so callers must treat that object as a controlled bulk-request builder. The signal is build/static-analysis cleanliness; RAT also excludes this dev-support file in the RBF POM.
