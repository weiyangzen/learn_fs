# sources/distributed-fs/ipfs-kubo/test/3nodetest/client/config

Purpose: static IPFS config for the 3nodetest client node.

Important APIs and control flow: JSON defines fixed identity/private key, API and swarm addresses, empty bootstrap list, old-style datastore, mounts, and version-check settings.

State and persistence: copied into `/root/.ipfs/config` during client image build.

Dependencies and integration: used by client Dockerfile and runtime `run.sh` which adds bootstrap dynamically.

Risks and test signals: old-style datastore config and fixed identity are only appropriate for historical integration tests. No direct validation besides the full 3nodetest.
