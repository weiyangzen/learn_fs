<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-hardened.service -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-hardened.service

## Purpose

This systemd service unit runs Kubo with a broad set of hardening directives for installations that do not need FUSE mounting.

## Important APIs, Types, and Functions

The unit configures `ReadWritePaths=/var/lib/ipfs/`, `ProtectSystem=strict`, private devices/tmp, restricted namespaces/realtime/SUID, syscall filters, address family limits, `CapabilityBoundingSet=CAP_NET_BIND_SERVICE`, `MemorySwapMax=0`, infinite startup timeout, `Type=notify`, `User/Group=ipfs`, `StateDirectory=ipfs`, `IPFS_PATH="${HOME}"`, `ExecStart=/usr/local/bin/ipfs daemon --init --migrate`, restart on failure, and SIGINT shutdown.

## Control Flow, State, and Integration

systemd creates/manages state under `/var/lib/ipfs`, starts the daemon with init/migration, and expects sd-notify readiness. Hardening blocks device access and FUSE-related functionality by design.

## Dependencies, Risks, and Test Signals

Dependencies are systemd features, an `ipfs` system user/group, and Kubo notify support. Risks include hardening directives unsupported by older systemd, FUSE breakage, `HOME` semantics under `StateDirectory`, and too-restrictive paths for custom repos. Validation is daemon startup, migration, restart behavior, and confirming forbidden FUSE paths are acceptable for this unit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-hardened.service -->
