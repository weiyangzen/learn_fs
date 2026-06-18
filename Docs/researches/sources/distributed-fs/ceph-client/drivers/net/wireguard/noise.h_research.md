# sources/distributed-fs/ceph-client/drivers/net/wireguard/noise.h

Purpose: Defines WireGuard Noise state types and declares the cryptographic handshake/keypair APIs.

Important APIs and types: `struct noise_replay_counter` stores anti-replay bitmap state. `struct noise_symmetric_key` stores key bytes, birthdate, and validity. `struct noise_keypair` stores index-table entry, sending/receiving keys, send counter, receive replay counter, remote index, initiator flag, kref/RCU, and debug ID. `struct noise_keypairs` stores current/previous/next RCU keypairs. `struct noise_static_identity` stores device public/private static key under rwsem. `enum noise_handshake_state` and `struct noise_handshake` capture the in-progress protocol transcript, remote static/ephemeral keys, preshared key, hash/chaining key, latest timestamp, and remote index. Declares all Noise lifecycle, keypair, identity, precompute, handshake create/consume, and session-begin functions.

Control flow: The header defines state transitions used by `noise.c`, with callers in send/receive/netlink/device/peer. `wg_noise_reset_last_sent_handshake()` sets a timestamp far enough in the past to allow immediate initiation.

State and persistence: Header declares sensitive volatile key material that must be zeroed on clear, stop, peer destroy, suspend, vmfork, or static identity change. Keypairs and handshakes are indexed in runtime lookup tables.

Dependencies and integration points: Includes message constants and peerlookup entry types plus kernel locks, atomics, krefs, and rwsem types. Consumed throughout WireGuard datapath and control plane.

Risks: Struct layout and locking comments define cross-file invariants. Callers must hold the right locks when accessing private key, handshake transcript, or RCU keypair pointers. Exposing raw key buffers increases risk of missed zeroization.

Test signals: Compile coverage, static identity setting, handshake state-machine tests, keypair RCU/kref lifetime tests, and anti-replay counter selftest.
