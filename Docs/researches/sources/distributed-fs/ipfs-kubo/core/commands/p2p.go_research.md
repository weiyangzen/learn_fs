# sources/distributed-fs/ipfs-kubo/core/commands/p2p.go

## Purpose

`p2p.go` implements experimental `ipfs p2p` stream mounting commands. It creates local-to-libp2p forwarders, libp2p-to-local listeners, lists and closes listeners, and lists/resets active p2p streams.

## Important APIs, Types, and Functions

`P2PCmd` registers `forward`, `listen`, `ls`, `close`, and `stream`. Output types are `P2PListenerInfoOutput`, `P2PStreamInfoOutput`, `P2PLsOutput`, `P2PStreamsOutput`, and `P2PForegroundOutput`. Helpers include `parseIpfsAddr`, `checkPort`, `forwardLocal`, and `p2pGetNode`. The protocol namespace default is `/x/`.

## Control Flow

All operational commands call `p2pGetNode`, which requires an online node and `Experimental.Libp2pStreamMounting` config. `forward` parses a protocol, local listen multiaddr, and remote peer multiaddr, resolves DNS multiaddrs if needed, enforces `/x/` unless custom protocols are allowed, adds target addresses to the peerstore, and starts a local listener. `listen` parses a protocol and local target multiaddr, rejects TCP/UDP port zero, enforces protocol namespace, and starts a remote protocol handler forwarding to the target. Foreground mode emits an active status and blocks until request cancellation or listener closure, cleaning up on cancellation. `ls` walks local and p2p listener registries under locks. `close` builds a predicate from all/protocol/listen/target filters and closes matching listeners. `stream ls` enumerates active stream handlers; `stream close` resets all or one by numeric ID.

## State and Persistence Behavior

State is live daemon memory: p2p listeners, streams, peerstore temporary addresses, and foreground command lifetimes. No repo config is changed. Listeners persist in the daemon until explicitly closed, daemon shutdown, or foreground cancellation.

## Dependencies and Integration Points

Dependencies include Kubo `p2p` manager, `core.IpfsNode`, cmdenv, libp2p peerstore/protocol/peer types, multiaddr, and multiaddr DNS resolution. The command integrates with daemon config and live network state.

## Risks and Test Signals

Risks include orphaned listeners, ambiguous DNS multiaddr resolution to multiple peers, unsafe custom protocol namespaces, port-zero listeners, foreground cleanup races, and output headers printed inside loops. Tests should cover config/offline gating, protocol prefix enforcement, parseIpfsAddr raw and DNS paths, ambiguous peer IDs, checkPort TCP/UDP/no-port/zero cases, close filter combinations, foreground cancellation/close behavior, stream reset by ID, and registry locking under concurrent changes.
