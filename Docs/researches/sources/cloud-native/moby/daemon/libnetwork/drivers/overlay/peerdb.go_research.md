# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/peerdb.go

Purpose: Maintains overlay peer database state and programs Linux neighbor/FDB/XFRM entries for remote overlay peers.

Important APIs and types: `peerEntry` stores endpoint id, MAC, and VTEP, with invalid VTEP meaning local. `peerMap` wraps a set-matrix allowing transient multiple entries per IP. `Walk`, `Get`, `Add`, and `Delete` manage peer entries. `network.initSandboxPeerDB` replays remote peers into a newly initialized sandbox. `peerAdd`/`peerDelete` update DB and kernel state. `addNeighbor` adds neighbor and bridge FDB entries, starts encryption for secure networks, and joins subnets lazily. `deleteNeighbor` removes encryption, FDB, and neighbor entries with reference counting.

Control flow: duplicate IP conditions are logged as transient. If a delete leaves another DB entry for the same IP, it restores one kernel configuration. FDB entries are reference-counted by VTEP+MAC to avoid premature deletion.

State and persistence: in-memory peer DB and FDB count map; kernel neighbor/FDB entries in the overlay sandbox; XFRM encryption state through driver encryption helpers.

Dependencies and integration points: driven by NetworkDB events from `joinleave.go`; depends on OSL namespace neighbor APIs, `hashable`, `setmatrix`, and encryption.

Risks: transient duplicate handling is complex and can mask failures in expected races. Encryption setup/removal errors are logged but not fatal. Correctness depends on caller holding the network lock.

Test signals: no direct peerdb tests in this subset.
