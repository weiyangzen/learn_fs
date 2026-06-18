# sources/control-plane/longhorn-engine/integration/data/test_frontend.py

## Purpose
Tests switching a volume that starts without a frontend to a blockdev frontend, preserving data across frontend shutdown/start cycles.

## Important APIs, Types, and Functions
- `test_frontend_switch()`.

## Control Flow
The test opens two replicas, starts a no-frontend controller volume, asserts frontend is empty, starts `tgt-blockdev`, writes and verifies data, shuts frontend down, starts it again, and verifies data persists.

## State and Persistence Behavior
Mutates frontend runtime state and writes persistent volume data through the block device. Confirms data remains on replicas while frontend is down.

## Dependencies and Integration Points
Uses data fixtures, `common.core` helpers, and constants. Exercises `volume.go` frontend start/shutdown behavior through gRPC fixture methods.

## Risks and Edge Cases
Depends on frontend type availability and block device readiness. Only one write offset/length is checked.

## Test Signals
Focused signal for no-frontend startup and dynamic frontend lifecycle behavior.
