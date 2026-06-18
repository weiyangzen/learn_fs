# sources/distributed-fs/ipfs-kubo/test/3nodetest/server/Dockerfile

Purpose: builds the server node image for the three-node integration test.

Important APIs and control flow: initializes a repo, installs static config, prints identity, marks `run.sh` executable, exposes swarm ports, enables profiling/no-color logs, and runs `/tmp/test/run.sh` under bash.

State and persistence: embeds a static server repo/config in the image layer.

Dependencies and integration: used by `fig.yml` server service linked to bootstrap and sharing the data volume.

Risks and test signals: static private key and old config schema are test-only. Runtime behavior depends on fig link env vars and shared volume access.
