# sources/cloud-native/stargz-snapshotter/script/cri-o/test-stargz.sh

Purpose: Runs CRI-O validation with stargz-store additional layer store and mirrored optimized images.
Important APIs/types/functions: `retry`, `cleanup`, auth registry setup, mirror config append, digest rewriting, auth pull check, critest, remote snapshot log validation.
Control flow: creates compose stack with CRI-O node, prepare node, public and auth registries; prepares TLS/auth creds; mirrors images; configures containers/image and stargz-store mirrors; rewrites digest references; rebuilds critest; restarts services; pulls an auth-protected eStargz image; runs critest; checks stargz-store logs.
State and persistence: creates temp auth certs, compose resources, registry content, CRI-O/store configs, and log extracts.
Dependencies and integration points: integrates CRI-O, containers/image, stargz-store, registry auth/TLS, ctr-remote mirror preparation, and `check_remote_snapshots`.
Risks: network, TLS, and sed-based digest rewriting are fragile; requires privileged containers and systemd.
Test signals: second phase of CRI-O CI; success covers auth and lazy layer store behavior.
