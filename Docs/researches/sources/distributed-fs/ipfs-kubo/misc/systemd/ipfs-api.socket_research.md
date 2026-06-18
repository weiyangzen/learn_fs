<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-api.socket -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-api.socket

## Purpose

This systemd socket unit provides socket activation for the Kubo API listener.

## Important APIs, Types, and Functions

The unit sets `Service=ipfs.service`, `FileDescriptorName=io.ipfs.api`, `BindIPv6Only=true`, and listens on `127.0.0.1:5001` and `[::1]:5001`.

## Control Flow, State, and Integration

When enabled, systemd owns the API socket and passes it to `ipfs.service`, overriding API listeners configured in Kubo config. It installs under `sockets.target`.

## Dependencies, Risks, and Test Signals

Dependencies are systemd socket activation support and Kubo service code recognizing `io.ipfs.api`. Risks include surprising config override and port conflicts. Validation is `systemctl enable --now ipfs-api.socket` plus checking daemon API fd adoption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-api.socket -->
