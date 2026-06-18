# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/DiskBalancerWorkStatus.java

Purpose: `DiskBalancerWorkStatus` is a private, unstable DTO used by DataNode disk balancer status RPCs to report the currently submitted plan, its high-level result, and the per-volume move work items currently in progress. It is primarily a Jackson-serializable envelope around `Result`, `planID`, `planFile`, and a list of `DiskBalancerWorkEntry` records.

Important APIs/types/functions: constructors support empty creation, direct `Result`/plan fields, prebuilt `List<DiskBalancerWorkEntry>`, and parsing the current-state JSON list. `toJsonString()`, `currentStateString()`, and static `parseJson(String)` provide serialization/deserialization. `addWorkEntry()` guards null entries with `Preconditions.checkNotNull`. `Result` enumerates `NO_PLAN`, `PLAN_UNDER_PROGRESS`, `PLAN_DONE`, and `PLAN_CANCELLED` with integer values for protocol/UI compatibility. Nested `DiskBalancerWorkEntry` stores `sourcePath`, `destPath`, and a `DiskBalancerWorkItem`, with JavaBean accessors for Jackson.

Control flow: the object is populated by DataNode disk-balancer code as work starts or progresses, then serialized through static `ObjectMapper`/`ObjectReader` instances. The JSON-list constructor parses a serialized list of work entries via `READER_WORKENTRY`, while whole-object parsing uses `READER_WORKSTATUS`. There is no background execution here; it is a passive status model.

State and persistence behavior: state is in memory until serialized to JSON for RPC/query output. `currentState` is mutable and final only at the field-reference level, so callers can append via `addWorkEntry()` or mutate the returned list. `MAPPER_WITH_INDENT_OUTPUT` is used only for readable current-state output; whole-object JSON is compact.

Dependencies and integration points: depends on Jackson, Hadoop `Preconditions`, and `DiskBalancerWorkItem`. It integrates with the disk balancer status and plan query path in the DataNode, and its nested shape is part of the diagnostic JSON surface consumed by CLI/admin tools.

Risks and test signals: because the current-state list is exposed directly, callers can mutate it without validation. JSON compatibility depends on bean-style getters and default constructor on `DiskBalancerWorkEntry`; renames would affect clients. Tests should cover round-trip JSON for each constructor path, result enum integer values, null rejection in `addWorkEntry`, and parsing of embedded `DiskBalancerWorkItem` JSON.
