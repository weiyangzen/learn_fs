## sources/distributed-fs/beegfs/storage/source/net/message/nodes/StorageBenchControlMsgEx.cpp

### Purpose
`StorageBenchControlMsgEx.cpp` handles remote control of the storage benchmark operator. It starts, stops, queries, or cleans up benchmark runs.

### Important APIs, Types, And Functions
`processIncoming()` switches on `getAction()`: `START` calls `initAndStartStorageBench()`, `STOP` calls `stopBenchmark()`, `STATUS` fills results through `getStatusWithResults()`, and `CLEANUP` calls `cleanup()`. It chooses an error code from the command result or the operator's last run error, then replies with `StorageBenchControlMsgResp`.

### Control Flow, State, And Persistence
The handler mutates benchmark operator state and may create/delete benchmark files through operator methods. Status requests are read-only. Unknown actions only log an error and still send a response using operator status and last error.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageBenchOperator`, benchmark request/response types, and target lists. Risks include unknown actions not setting an explicit command error, concurrent benchmark commands, and result map size for large target sets. Tests should cover each action, command failure versus last-run error precedence, unknown action, and response status/type fields.
