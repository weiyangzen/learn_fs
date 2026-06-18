# sources/distributed-fs/ipfs-kubo/test/3nodetest/client/Dockerfile

Purpose: builds the client node image for the three-node integration test.

Important APIs and control flow: initializes an IPFS repo, installs static config, prints node identity, exposes swarm ports, enables profiling/no-color logs, and sets `/tmp/id/run.sh` as the default bash command.

State and persistence: creates a test repo with static identity and config in the image layer.

Dependencies and integration: run by `fig.yml` client service linked to bootstrap and sharing data volume.

Risks and test signals: static private key and old config schema are test-only. Runtime success depends on environment variables injected by legacy fig links and the server writing CID files to the shared volume.
