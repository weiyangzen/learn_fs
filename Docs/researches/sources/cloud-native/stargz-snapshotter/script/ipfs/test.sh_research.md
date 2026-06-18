# sources/cloud-native/stargz-snapshotter/script/ipfs/test.sh

Purpose: Builds a temporary IPFS-enabled Go test container and runs IPFS client tests.
Important APIs/types/functions: uses `go_base_version`, `IPFS_VERSION`, temp Dockerfile, and cleanup trap.
Control flow: builds an image with Go, fuse3, and go-ipfs, mounts the repo read-only, starts the entrypoint, and runs `go test -v -run TestIPFSClient ./client/... --ipfs-api=http://localhost:5001`.
State and persistence: creates temporary Docker build context and Docker image `testipfs`.
Dependencies and integration points: depends on Docker, Go base image, IPFS download, FUSE device, and repository IPFS client tests.
Risks: hard-codes amd64 IPFS tarball; read-only repo means tests must not need writes under source tree.
Test signals: direct CI signal for IPFS client package integration.
