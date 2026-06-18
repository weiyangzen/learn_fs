# sources/cloud-native/stargz-snapshotter/script/k3s/mirror.sh

Purpose: Optimizes and pushes a test image into the k3s private registry.
Important APIs/types/functions: `retry`; positional `SRC`/`DST`; env `REGISTRY_CREDS`.
Control flow: updates certs, builds `ctr-remote`, starts containerd, pulls source, optimizes to OCI eStargz, and pushes with credentials.
State and persistence: writes `/out/ctr-remote` and registry content.
Dependencies and integration points: called from the k3s prepare container in `k3s/test.sh`.
Risks: requires trusted registry CA and credentials; no explicit cleanup of containerd data.
Test signals: failure blocks k3s private registry test setup.
