# sources/distributed-fs/ipfs-kubo/bin/container_daemon

## Purpose
This shell entrypoint initializes or opens the container's IPFS repo, drops root privileges to the `ipfs` user, configures API/gateway binding, loads optional swarm keys, runs init hooks, and execs `ipfs`.

## Important APIs, Types, And Functions
It uses `gosu`, `$IPFS_PATH`, `$IPFS_PROFILE`, `$IPFS_SWARM_KEY`, `$IPFS_SWARM_KEY_FILE`, `ipfs init`, `ipfs config`, `install`, `find`, `sort`, `xargs`, and `container_init_run`.

## Control Flow
When run as root it ensures repo ownership and re-execs as `ipfs`. As the unprivileged user it prints `ipfs version`, initializes the repo if missing, writes network defaults, copies swarm key material if supplied, executes `/container-init.d/*.sh`, and finally `exec ipfs "$@"`.

## State And Persistence Behavior
It persists repo config and optional `swarm.key` under `$IPFS_PATH`, changes ownership, and executes arbitrary container init scripts.

## Dependencies And Integration Points
It integrates the Dockerfile entrypoint, container volume layout, private swarm configuration, and Kubo daemon command.

## Risks And Test Signals
Risks include recursive chown cost, secrets passed through environment, hook script failures aborting startup, and API binding to all interfaces. Signals are initialized config, copied swarm key permissions, hook execution logs, and successful daemon start.
