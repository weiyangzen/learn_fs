# sources/distributed-fs/ipfs-kubo/test/3nodetest/fig.yml

Purpose: defines the legacy fig/docker-compose topology for the three-node integration test.

Important APIs and control flow: services are `data`, `bootstrap`, `server`, and `client`. Data builds a volume and sleeps. Bootstrap runs `daemon --debug --init`. Server and client build their images, link to bootstrap, share the data volume, expose swarm ports, and set debug logging.

State and persistence: creates containers, shared `/data` volume, and image builds. Server writes CID marker files that client reads.

Dependencies and integration: consumed by legacy `fig` commands in the Makefile and runner script.

Risks and test signals: uses obsolete fig syntax and link-based environment variables. Container names expected by log/profiling scripts derive from fig naming. No standalone tests.
