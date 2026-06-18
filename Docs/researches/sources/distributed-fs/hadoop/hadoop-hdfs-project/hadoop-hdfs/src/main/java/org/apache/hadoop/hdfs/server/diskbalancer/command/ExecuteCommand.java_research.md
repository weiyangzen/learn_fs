# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/ExecuteCommand.java

Purpose: implements `hdfs diskbalancer -execute <planfile>`, reading a serialized `NodePlan` and submitting it to the target DataNode for asynchronous diskbalancer execution.

Important APIs/types/functions: constructor registers `-execute` and `-skipDateCheck`. `execute()` validates options, opens the plan file through `Command.open()`, reads UTF-8 JSON, checks `-skipDateCheck`, and calls `submitPlan()`. `submitPlan()` parses `NodePlan`, derives `<nodeName>:<port>`, computes a SHA-1 plan hash, creates a `ClientDatanodeProtocol` proxy, and invokes `submitDiskBalancerPlan(planHash, PLAN_VERSION, planFile, planData, skipDateCheck)`.

Control flow: the command is intentionally thin: local file/HDFS read, optional warning for forced old-plan execution, DataNode RPC submit, and immediate return. `DiskBalancerException` from the DataNode is logged with result code and rethrown for the CLI.

State and persistence behavior: no durable local state is held beyond inherited command state. The DataNode receives the entire JSON plan and hash and owns execution state after submission. The input plan file path is passed through to the DataNode as identifying metadata.

Dependencies and integration points: depends on `NodePlan.parseJson()` for safe plan deserialization, Commons Codec SHA-1, Hadoop FS streams, and `ClientDatanodeProtocol`. It is paired with `PlanCommand` output and `QueryCommand` status checks.

Risks: plan freshness is enforced by the DataNode unless `-skipDateCheck` is used; the command logs but does not otherwise guard against stale plans. DataNode address comes from plan fields, so malformed or hostile plan JSON must be rejected by `NodePlan.parseJson()` and DataNode-side validation. The SHA-1 hash is an identity/check value rather than a modern collision-resistant security primitive.

Test signals: `TestDiskBalancerCommand` includes execute-plan validity, invalid plan content, force execute, and DataNode exception cases.
