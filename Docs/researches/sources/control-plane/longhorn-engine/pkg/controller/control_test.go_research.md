<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/control_test.go -->
## sources/control-plane/longhorn-engine/pkg/controller/control_test.go

Purpose: unit tests for controller sizing, WO write alignment, and ENOSPC replica error policy.

Important APIs/types/functions: test helpers include `fakeReader`, `fakeWriter`, `newMockReplicator`, byte-slice constructors, and gocheck suite. Tests cover `determineCorrectVolumeSize`, `writeInWOMode`, `handleDiskNoSpaceErrorForReplicas`, `categorizeOutOfSpaceReplicas`, and `listReplicasToErrOnEnospc`.

Control flow: tests construct fake sources and controller state without real replicas. WO writes verify read-modify-write alignment across 4096-byte sectors. ENOSPC tests assert which replicas stay RW or move ERR based on mode and written-byte groups.

State and persistence: purely in-memory test buffers and replica mode slices.

Dependencies and integration points: uses `gopkg.in/check.v1`, Go testing, `types`, and disk sector constants. It directly supports the controller no-space and rebuild write-path logic.

Risks: map iteration order can affect list order; tests mitigate some list comparisons by map conversion for `listReplicasToErrOnEnospc`, but some ordered list checks exist in categorization for deterministic replica traversal. These tests do not cover real backend errors, locks, frontend, freeze, or gRPC.

Test signals: strong focused signal for recently complex ENOSPC behavior and WO alignment. Needs integration complement for storage stack behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/control_test.go -->
