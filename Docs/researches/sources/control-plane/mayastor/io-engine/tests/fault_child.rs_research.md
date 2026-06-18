# sources/control-plane/mayastor/io-engine/tests/fault_child.rs

Purpose: verifies nexus child faulting rules: the only healthy child cannot be faulted, but an unhealthy/unsynchronized child can be faulted permanently.

Important APIs/types/functions: `nexus_create`, `nexus_lookup_mut`, `add_child`, `fault_child`, `FaultReason::OfflinePermanent`, and child state helpers.

Control flow: creates a one-child malloc nexus, adds a second child without rebuild so it remains degraded/unsynced, expects faulting the original healthy child to fail, and expects faulting the unhealthy added child to succeed.

State and persistence: in-memory malloc bdevs and nexus state only.

Dependencies and integration points: nexus child state machine and fault policy.

Risks and edge cases: does not destroy the nexus explicitly at the end, relying on test process cleanup. Names are fixed.

Test signals: targeted regression guard for preventing data-loss by faulting the last healthy child.
