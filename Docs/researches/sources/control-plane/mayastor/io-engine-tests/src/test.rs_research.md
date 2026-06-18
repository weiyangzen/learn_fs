<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/test.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/test.rs

Purpose: v1 test-service wrappers for dynamic fault injection management.

Important APIs: `add_fault_injection(rpc, inj_uri)`, `remove_fault_injection(rpc, inj_uri)`, and `list_fault_injections(rpc)` lock the shared RPC handle and call generated test service methods.

Control flow: each function maps a successful tonic response to its inner value, returning `Status` on RPC errors.

State and dependencies: mutates io-engine fault-injection registry, typically used by nexus tests after constructing an injection URI for a child device.

Integration points: `NexusBuilder::add_injection_at_replica()` calls `add_fault_injection` after resolving the child device name.

Risks and test signals: injection URI syntax is not validated locally; failures come from the remote test service. `list_fault_injections` is the primary verification signal after add/remove.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/test.rs -->
