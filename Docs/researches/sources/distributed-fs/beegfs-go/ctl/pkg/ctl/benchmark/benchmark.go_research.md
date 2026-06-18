# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/benchmark/benchmark.go

Purpose: implements backend support for BeeGFS storage benchmark control actions against storage targets or nodes.

Important APIs/types/functions: `NewStorageBenchConfig`; `StorageBenchConfig`; `StorageBenchResult`; `TargetResult`; `ExecuteStorageBenchAction`; `filterTargetsByNode`.

Control flow: execution initializes logging, node store, and mappings, filters targets by explicit target IDs, explicit storage nodes, or all storage targets, builds a base `StorageBenchControlMsg`, sends one TCP request per storage node with its target IDs, validates response target/result lengths, maps response target IDs back to entity ID sets, and returns per-node results.

State and persistence: sends benchmark control messages to storage nodes; depending on `Action`, this may start, stop, or query server-side benchmark activity. Local state is transient.

Dependencies and integration points: uses `config.NodeStore`, `util.GetMappings`, `target.GetTargets`, BeeMsg storage benchmark messages, BeeGFS entity types, and logging.

Risks: RST mapping errors are ignored only for `ErrMappingRSTs`, but the code still passes `mappings` into filtering, so callers rely on mapping availability for target selection. Cannot specify both target IDs and storage nodes. Response target IDs are trusted after length check but must map back to known targets. No parallel fan-out; large node counts are sequential.

Test signals: no direct tests. Useful tests would mock mappings/node store for duplicate target filtering, target-vs-node exclusivity, all-target selection, response length mismatch, and request construction.
