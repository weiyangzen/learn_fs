# sources/distributed-fs/ipfs-kubo/test/3nodetest/bootstrap/Dockerfile

Purpose: builds the bootstrap node image for the three-node integration test.

Important APIs and control flow: starts from `zaqwsx_ipfs-test-img`, initializes an IPFS repo, replaces config from the Docker build context, runs `ipfs id`, enables profiling and no-color logs, and exposes TCP/UDP swarm ports.

State and persistence: creates `/root/.ipfs` at image build time with a fixed identity/config.

Dependencies and integration: used by `fig.yml` bootstrap service and linked by client/server via environment variables.

Risks and test signals: embeds static private key material suitable only for tests. Depends on old base image tag and old config schema. No Dockerfile-specific tests.
