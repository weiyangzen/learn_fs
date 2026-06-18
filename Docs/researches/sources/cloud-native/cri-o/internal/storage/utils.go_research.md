# sources/cloud-native/cri-o/internal/storage/utils.go

Purpose: provides a small helper to identify containers created by CRI-O based on stored runtime metadata.

Important APIs/types/functions: `IsCrioContainer(md *RuntimeContainerMetadata) bool` returns true when both `PodName` and `PodID` are non-empty.

Control flow: single boolean expression; no nil guard.

State and persistence: reads `RuntimeContainerMetadata` fields produced by `runtime.go`; does not mutate or persist anything.

Dependencies/integration: belongs with the storage metadata model and likely filters containers/storage records to distinguish CRI-O-managed containers from Podman or other users.

Risks: passing nil panics. The heuristic assumes both pod fields are mandatory for all CRI-O-created sandboxes and containers; any migration with missing legacy fields would be classified as non-CRI-O.

Test signals: no direct tests in this subset; storage metadata creation tests indirectly preserve the invariant that CRI-O containers have pod name and ID.
