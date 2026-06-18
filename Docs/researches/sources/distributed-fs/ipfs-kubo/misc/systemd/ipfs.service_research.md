<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs.service -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs.service

## Purpose

This is the standard systemd service unit for running the Kubo daemon with fewer hardening restrictions than the hardened variant.

## Important APIs, Types, and Functions

It declares `After=network.target`, optional commented capability/env/NOFILE settings, `MemorySwapMax=0`, infinite startup timeout, `Type=notify`, `User=ipfs`, `Group=ipfs`, `StateDirectory=ipfs`, `Environment=IPFS_PATH="${HOME}"`, `ExecStart=/usr/local/bin/ipfs daemon --init --migrate`, restart on failure, and SIGINT shutdown.

## Control Flow, State, and Integration

systemd creates/manages the state directory, launches the daemon, waits for notify readiness, and restarts on failure. Comments document drop-in override mechanics.

## Dependencies, Risks, and Test Signals

Dependencies are systemd notify support, the `ipfs` user/group, and binary path `/usr/local/bin/ipfs`. Risks include custom repo paths requiring drop-ins, low file descriptor defaults, and infinite startup masking hangs. Validation checks daemon startup, readiness notification, migrations, restart, and compatibility with optional socket units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs.service -->
