# sources/control-plane/rook/tests/framework/clients/client.go

Purpose: `ClientOperation` manages `CephClient` CRs and validates resulting Ceph auth keys/caps in integration tests.

Important APIs/types/functions: `ClientOperation` holds `K8sHelper` and `CephManifests`. `Create` applies a `CephClient` manifest. `Delete` uses the Rook typed client to remove `CephClients`. `Get` calls `client.AuthGetKey`. `Update` reapplies caps and polls `client.AuthGetCaps` until the monitor cap matches the requested value.

Control flow: Kubernetes CR changes are applied first, then Ceph CLI/client calls observe whether the operator reconciled those changes. `Update` loops 30 times with 2-second sleeps and returns once `caps["mon"]` matches.

State and persistence behavior: persistent state is the `CephClient` custom resource and Ceph auth database entry. The wrapper has no persisted state.

Dependencies and integration points: depends on generated manifests, Rook Ceph client auth helpers, Rook typed Kubernetes clientset, and test logger.

Risks: `Update` only compares the `mon` capability, so mismatches in `osd`, `mgr`, or other caps may go undetected. The namespace parameter to `Create` is unused because the manifest settings own namespace selection. Ignored errors inside the polling loop can mask transient auth failures until timeout.

Test signals: after create/update, tests should verify key existence and all requested caps, not only monitor caps. Delete should verify both CR removal and Ceph auth cleanup where applicable.
