# sources/cloud-native/stargz-snapshotter/script/criauth/mirror.sh

Purpose: Optimizes and pushes one source image into an authenticated registry for CRI auth tests.
Important APIs/types/functions: `retry`; positional `SRC` and `DST`; env `REGISTRY_CREDS`.
Control flow: updates CA certificates, builds `ctr-remote`, starts containerd, pulls source, optimizes to OCI eStargz destination, and pushes with credentials.
State and persistence: writes build output under `/out` and populates the private registry.
Dependencies and integration points: called inside the prepare service from `criauth/test.sh`.
Risks: requires valid mounted CA and credentials; no cleanup of containerd state.
Test signals: failure prevents private registry test setup.
