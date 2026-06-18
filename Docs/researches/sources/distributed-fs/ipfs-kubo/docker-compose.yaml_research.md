# sources/distributed-fs/ipfs-kubo/docker-compose.yaml

Purpose: provides a default Docker Compose service for running Kubo. Important entries are the `ipfs` service, persistent volumes, `IPFS_PATH`, and port mappings.

Control flow: Compose builds the local Dockerfile, restarts unless stopped, mounts `ipfs_path` at `/data/ipfs`, FUSE volumes at `/ipfs` and `/ipns`, sets `IPFS_PATH=/data/ipfs`, exposes swarm TCP/UDP port 4001 on all interfaces, and binds API 5001 plus gateway 8080 to loopback only.

State and persistence: named volumes persist repo data and FUSE mount content across container restarts.

Dependencies/integration: Docker Compose v3.8, local Dockerfile, Kubo container entrypoint behavior. It aligns with network defaults used by the node/libp2p code in this subset.

Risks: swarm ports are remotely reachable by default; API and gateway are safer on loopback but users extending compose can expose admin API accidentally. No automated tests in this file; validation is Docker Compose parsing and runtime smoke testing.
