# sources/control-plane/ceph-csi/internal/csi-addons/rbd/reclaimspace_test.go

Purpose: smoke tests for invalid reclaim-space requests without requiring a Ceph cluster or mounted filesystem.

Important APIs/types/functions: `TestControllerReclaimSpace()` creates a controller server with a new ID locker and sends an empty volume ID. `TestNodeReclaimSpace()` creates a node server and sends an empty volume ID/path/capability request.

Control flow: both tests expect errors from early validation.

State and persistence: no backend state or local mount state.

Dependencies and integration points: validates that reclaim-space RPCs fail fast for malformed required fields.

Risks: no coverage for success, in-use controller no-op, `fstrim`, capability rejection, or exact status codes.

Test signals: basic invalid-input guard only.
