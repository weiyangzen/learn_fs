<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/p2p.go -->
# sources/distributed-fs/ipfs-kubo/p2p/p2p.go

## Purpose

This file defines the top-level P2P forwarding manager that owns listener registries and active stream tracking.

## Important APIs, Types, and Functions

`P2P` contains local listener registry, remote/libp2p listener registry, stream registry, identity, peer host, and peerstore. `New` initializes these and wires the stream registry to the host connection manager. `CheckProtoExists` checks whether a protocol is registered in the host muxer.

## Control Flow, State, and Integration

The manager is in-memory runtime state owned by a Kubo node. It coordinates CLI/API P2P listener creation with libp2p host stream handlers and active stream connection-manager tags.

## Dependencies, Risks, and Test Signals

Dependencies are go-log, libp2p host/peerstore/protocol. Risks include stale registries if callers do not close listeners and mux protocol checks racing with handler changes. P2P API integration tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/p2p.go -->
