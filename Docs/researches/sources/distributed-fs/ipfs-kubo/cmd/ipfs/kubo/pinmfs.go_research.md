# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/pinmfs.go

## Purpose
This file implements the daemon background service that periodically pins the current MFS root to configured remote pinning services.

## Important APIs, Types, And Functions
Types include `lastPin`, `pinMFSContext`, `pinMFSNode`, and `ipfsPinMFSNode`. Functions include `startPinMFS`, `pinMFSOnChange`, `pinAllMFS`, and `pinMFS`.

## Control Flow
The daemon starts a polling goroutine. On each interval it reloads config, reads the MFS root CID, skips disabled services, parses repin intervals, skips unchanged/recent pins, and starts parallel pin attempts. `pinMFS` lists existing remote pins by name, reuses non-failed current pins, replaces older pins, or creates a new pin with optional origin multiaddrs.

## State And Persistence Behavior
It maintains in-memory `lastPins` per service and mutates remote pinning services through add/replace calls. It reads current MFS root and config repeatedly.

## Dependencies And Integration Points
It integrates daemon lifecycle, config remote pinning policy, Boxo remote pinning client, MFS root node, libp2p host addresses, and logging.

## Risks And Test Signals
Risks include expensive MFS root reads, remote service hangs/errors, channel waits for all goroutines, invalid intervals, and duplicate pin-name assumptions. Tests assert config/root-node errors and service policy error logging.
