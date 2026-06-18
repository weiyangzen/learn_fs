<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/id.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/id.go

## Purpose

Implements `ipfs id`, printing local or remote peer identity, public key, addresses, agent version, and protocol registrations with configurable peer ID base.

## Important APIs, Types, and Functions

`IDCmd` defines `peerid`, `--format`, and `--peerid-base`. `IdOutput` is the response. `printPeer` extracts peerstore information for a remote/local peer. `printSelf` gathers identity from the local node and host. `offlineIDErrorMessage` explains remote lookup limits without a daemon.

## Control Flow

The handler builds a `keyencode.KeyEncoder`, gets the node, chooses the requested peer or local identity, and either prints self directly or handles remote lookup. Remote lookup requires online mode unless `--offline` is set; online mode connects to the peer so identify data populates the peerstore. Text encoding either applies a token replacement format string or emits indented JSON.

## State and Persistence Behavior

Read-only for repo state. Online remote lookup may initiate libp2p connection and update peerstore metadata. Offline mode only formats existing peerstore data.

## Dependencies and Integration Points

Uses Kubo version, node host/peerstore, libp2p peer IDs, peerstore protocols, crypto public-key marshaling, kbucket lookup errors, key encoding, and display sanitization.

## Risks and Edge Cases

Remote `id` without daemon fails with a specific guidance message. AgentVersion and protocols are sanitized to avoid unsafe display. Format string replacement is simple token substitution and supports escaped newline/tab sequences, not a full template language.

## Test Signals

No direct tests in this subset. Useful coverage includes peerid-base variants, offline remote behavior, kb lookup failure mapping, sanitization of peerstore strings, and custom format output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/id.go -->
