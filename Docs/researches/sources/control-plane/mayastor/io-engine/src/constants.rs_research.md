<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/constants.rs -->
## sources/control-plane/mayastor/io-engine/src/constants.rs

### Purpose
`constants.rs` centralizes small string constants used across io-engine for driver names, NVMe identity, NQN construction, eventing trace filters, and service identity.

### Important APIs, Types, And Functions
The file exports `NEXUS_CAS_DRIVER`, `NVME_CONTROLLER_MODEL_ID`, `NVME_NQN_PREFIX`, `EVENTING_TARGET`, and `SERVICE_NAME`.

### Control Flow
There is no runtime control flow. These constants are compiled into callers that need stable string identifiers.

### State, Persistence, And Dependencies
The file has no dependencies and no mutable state. The constants participate in integration with NVMe initiators/targets, eventing, and external component naming.

### Risks And Test Signals
Changing these strings can break compatibility with persisted metadata, event consumers, NQN conventions, or controller identity expectations. Tests should assert generated NQNs/model IDs and event source names where external contracts depend on them.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/constants.rs -->
