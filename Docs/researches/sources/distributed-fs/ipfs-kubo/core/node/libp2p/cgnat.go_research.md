# sources/distributed-fs/ipfs-kubo/core/node/libp2p/cgnat.go

Purpose: detects and warns when a node appears behind carrier-grade NAT or double NAT. Important APIs are `DetectNAT`, `detectNATKind`, `classifyNAT`, `MonitorCGNAT`, `latchNotice`, `logCGNATNotice`, and `logDoubleNATNotice`.

Control flow: detection requires a host implementing `AllAddrs` and `Reachability`. `classifyNAT` ignores public reachability, ignores IPv6 and local-interface IPv4 addresses, classifies foreign RFC6598 addresses as CGNAT, and classifies foreign private addresses as double NAT unless CGNAT is found. `MonitorCGNAT` subscribes to `EvtLocalAddressesUpdated`, runs an initial check in a goroutine, and emits only first/upgrade notices through `latchNotice`.

State and persistence: no durable state. Runtime state is the single `reported` NAT kind in the monitor goroutine. Notices write directly to `cgnatNoticeOut` (default stderr) so they are visible even when go-log filters warn/info.

Dependencies/integration: libp2p host/network/event APIs, multiaddr, fx lifecycle. Wired conditionally by `groups.go` through `Internal.CGNATCheck`.

Risks: best-effort detection misses routers that do not expose mapped WAN addresses; direct stderr output bypasses normal logging controls except the config flag. Tests cover classification, notice latching, and notice content.
