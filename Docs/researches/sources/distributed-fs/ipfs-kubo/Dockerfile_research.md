# sources/distributed-fs/ipfs-kubo/Dockerfile

## Purpose
The Dockerfile builds and packages Kubo into a minimal `busybox:stable-glibc` runtime image with the `ipfs` binary, FUSE helper, TLS certificates, `tini`, `gosu`, and container startup scripts.

## Important APIs, Types, And Functions
It has three stages: `builder` based on `golang:${GO_VERSION}`, `utilities` based on Debian for runtime helper binaries, and final BusyBox runtime. Build args include `GO_VERSION`, `TARGETOS`, `TARGETARCH`, `IPFS_PLUGINS`, and `MAKE_TARGET`.

## Control Flow
The builder caches Go modules/build output, copies the tree, creates `.git/objects` for version metadata, and runs `make ${MAKE_TARGET}`. The final stage copies helpers and scripts, creates the `ipfs` user and repo/mount directories, exposes swarm/API/gateway ports, sets healthcheck, and defaults to `daemon --migrate=true --agent-version-suffix=docker`.

## State And Persistence Behavior
`/data/ipfs` is the persistent volume via `IPFS_PATH`; `/ipfs`, `/ipns`, `/mfs`, and `/container-init.d` are runtime directories. Health checks query the local RPC API.

## Dependencies And Integration Points
It integrates Make build targets, `bin/container_daemon`, `bin/container_init_run`, FUSE, runtime privilege drop via `gosu`, and daemon health semantics.

## Risks And Test Signals
Risks include Go version drift, glibc/helper compatibility, FUSE SUID security, and API healthcheck assumptions. Signals are successful multi-stage build, runnable daemon, and passing `ipfs diag healthy`.
