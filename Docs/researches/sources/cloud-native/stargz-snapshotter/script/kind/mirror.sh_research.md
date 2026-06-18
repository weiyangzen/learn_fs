# sources/cloud-native/stargz-snapshotter/script/kind/mirror.sh

Purpose: Optimizes and pushes one source image into the kind private registry.
Important APIs/types/functions: `retry`; positional `SRC` and `DST`; env `REGISTRY_CREDS`.
Control flow: updates CAs, builds `ctr-remote`, starts containerd, pulls source, optimizes to OCI eStargz, and pushes with credentials.
State and persistence: writes `/out/ctr-remote` and registry content.
Dependencies and integration points: called by the prepare service in `kind/test.sh`.
Risks: requires registry credentials and mounted CA; no daemon state cleanup.
Test signals: failure prevents kind private registry test from running.
