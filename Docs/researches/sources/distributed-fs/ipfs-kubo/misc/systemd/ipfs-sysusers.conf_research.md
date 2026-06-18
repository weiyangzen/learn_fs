<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-sysusers.conf -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-sysusers.conf

## Purpose

This sysusers configuration declares the system user and group used by the systemd Kubo service units.

## Important APIs, Types, and Functions

It creates user `ipfs` with description `IPFS daemon` and home `/var/lib/ipfs`, creates group `ipfs`, and adds user `ipfs` to group `ipfs`.

## Control Flow, State, and Integration

systemd-sysusers consumes this file during package install or boot, persisting `/etc/passwd`/group database entries through the platform's sysusers mechanism.

## Dependencies, Risks, and Test Signals

Dependencies are systemd-sysusers. Risks include conflicts with pre-existing users/groups or packaging systems that manage users differently. Validation is `systemd-sysusers --dry-run` and service startup under the created account.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-sysusers.conf -->
