<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-gateway.socket -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-gateway.socket

## Purpose

This systemd socket unit provides socket activation for the Kubo gateway listener.

## Important APIs, Types, and Functions

The unit sets `Service=ipfs.service`, `FileDescriptorName=io.ipfs.gateway`, `BindIPv6Only=true`, and listens on `127.0.0.1:8080` and `[::1]:8080`.

## Control Flow, State, and Integration

Enabling it lets systemd bind gateway sockets and pass descriptors to `ipfs.service`, completely overriding configured gateway listeners. It is wanted by `sockets.target`.

## Dependencies, Risks, and Test Signals

Dependencies are systemd and daemon socket activation support. Risks are hidden listener override, local port conflicts, and IPv4/IPv6 binding nuances. Runtime validation should check gateway availability and descriptor name handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-gateway.socket -->
