<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/mod.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/mod.rs

Purpose: Simple module aggregator for compose RPC clients.

Important APIs: declares `pub mod v0;` and `pub mod v1;`, exposing legacy and current gRPC helper modules.

Dependencies and integration: downstream tests choose v0 or v1 depending on API surface under test. The benchmark code uses v0 for legacy nexus creation, while most builder helpers use v1.

State and persistence: none.

Risks and test signals: low risk; failures indicate missing module files or generated API changes in the submodules.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/mod.rs -->
