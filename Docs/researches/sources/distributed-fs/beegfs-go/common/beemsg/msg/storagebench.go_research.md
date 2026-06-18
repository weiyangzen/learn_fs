<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/storagebench.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/storagebench.go

Purpose: BeeMsg definitions to start/query/control BeeGFS storage benchmark operations.

Important APIs/types/functions: `StorageBenchControlMsg` serializes action, type, block size, file size, thread count, O_DIRECT flag, and target IDs. `StorageBenchControlMsgResp` deserializes status, action, type, error code, target IDs, and per-target result values.

Control flow: request serialization writes fixed scalar fields followed by a total-size sequence of target IDs. Response deserialization mirrors fixed fields followed by two sequences.

State and persistence: no local persistence; it controls and reads benchmark state on storage targets.

Dependencies and integration points: depends on `common/beegfs` storage benchmark enums and `beeserde`; transported through the generic BeeMsg utilities.

Risks: there is no check that `TargetIDs` and `TargetResults` have the same length. Enum validity is not checked locally.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/storagebench.go -->
