# sources/cloud-native/stargz-snapshotter/script/integration/test.sh

Purpose: Builds and runs the integration Docker Compose environment.
Important APIs/types/functions: env toggles `BUILTIN_SNAPSHOTTER`, `METADATA_STORE`, `FUSE_MANAGER`, `FUSE_PASSTHROUGH`, `TRANSFER_SERVICE`; helper `prepare_creds`.
Control flow: builds a base image, generates a test Dockerfile with IPFS/stargzify/configs/entrypoint, adjusts snapshotter config for selected variants, creates TLS registry credentials, writes a compose stack with test node plus registries, runs compose until the test container exits, then tears down volumes.
State and persistence: creates temp compose/auth/root/context dirs, Docker images, registry auth files, and compose volumes.
Dependencies and integration points: depends on Docker Compose, registry:2, Go tools, IPFS download, FUSE, and integration container scripts.
Risks: network-heavy and privileged; builtin+FUSE passthrough is explicitly unsupported; duplicate build args are passed in one docker build command.
Test signals: top-level integration CI entrypoint.
