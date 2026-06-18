# sources/distributed-fs/eos/namespace/ns_quarkdb/utils/QuotaRecomputer.hh

## Purpose
`QuotaRecomputer.hh` declares the public utility class used to recompute quota-node accounting from a QuarkDB namespace subtree.

## Important APIs, Types, and Functions
The header forward-declares `qclient::QClient`, `folly::Executor`, `QuotaNodeCore`, and `IView`, then declares `class QuotaRecomputer`. Its constructor takes a QuarkDB client pointer and executor pointer. `MDStatus recompute(const std::string& cont_uri, IContainerMD::id_t cont_id, QuotaNodeCore& core)` is the only public operation.

## Control Flow
The header does not implement control flow, but it defines a call contract: callers provide both the quota-node URI and container ID plus mutable output accounting core. The implementation resets and fills that core.

## State and Persistence Behavior
The class stores raw, non-owning pointers to `QClient` and `folly::Executor`. It does not own namespace services or quota nodes. Persistence behavior is read-only in the implementation; output state is returned through `QuotaNodeCore&`.

## Dependencies and Integration Points
The API sits between QuarkDB namespace exploration and quota accounting. It includes `IContainerMD.hh`, `Namespace.hh`, and `MDException.hh` for namespace types and status handling. Consumers must ensure the client and executor outlive the recomputer.

## Risks and Edge Cases
Raw pointer lifetime is the main API risk. Passing `nullptr` for either dependency is not guarded in the declaration and would fail later in implementation. Requiring both URI and ID can introduce inconsistency if they do not refer to the same container; the implementation uses both independently.

## Test Signals
Header-level tests are not applicable. Integration tests should instantiate with fixture QuarkDB state, verify nonzero quota-node recomputation, invalid ID behavior, and nested quota-node exclusion.
