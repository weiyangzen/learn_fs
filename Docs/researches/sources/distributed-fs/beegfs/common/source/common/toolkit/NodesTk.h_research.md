<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NodesTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/NodesTk.h

**Purpose:** Declares the static `NodesTk` cluster-node utility interface used by BeeGFS services and tools for node discovery, management downloads, target state retrieval, and node-store population.

**Important APIs/types/functions:** The public API mirrors the implementation: management heartbeat waiting; single-node heartbeat download; bulk node, target mapping, buddy group, target state, combined state/group, and storage pool downloads; movement of `NodeHandle` vectors into `AbstractNodeStore`; local NIC list application; and retry-delay calculation.

**Control flow:** Callers use the class as a pure namespace; construction is blocked by a private constructor. Most methods are synchronous and either return `bool` plus filled output parameters or return richer pairs/handles for target mappings and node info.

**State and persistence behavior:** The header declares no member state. It defines ownership transfer expectations: `downloadNodes` fills a vector of handles, and `moveNodesFromListToStore` transfers those handles into a node store and clears the vector.

**Dependencies and integration points:** Includes datagram listener, node stores, buddy group and target state structures, and BeeGFS common types. It is a shared contract for management bootstrap code across storage, metadata, client, and administrative components.

**Risks:** Several APIs use parallel lists instead of typed aggregate records, so callers must preserve order. Optional output pointers can be null. `silenceLog` behavior depends on build mode in the implementation. There is no asynchronous or cancellation token model besides `waitForMgmtHeartbeat` accepting a `PThread`.

**Test signals:** Compile-time coverage should ensure all included forward types remain available. Runtime coverage comes from tests or integration scenarios that mock node stores and message responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NodesTk.h -->
