## sources/distributed-fs/ipfs-kubo/test/sharness/t0240-republisher.sh

Purpose: tests IPNS republishing behavior across multiple nodes, including self key and alternate key records.

Important APIs and helpers: defines `setup_iptb`, `teardown_iptb`, `verify_can_resolve`, and `verify_cannot_resolve`; uses IPTB, `ipfsi config Ipns.RepublishPeriod`, `Ipns.ResolveCacheSize`, `ipfsi name publish -t`, `ipfsi name resolve`, `ipfsi key gen`, and date-based content.

Control flow and state: creates a testbed, configures short republish periods and zero resolve cache, publishes expiring IPNS records, records IDs, verifies resolution before and after expected republish windows, and repeats for an alternate Ed25519 key. State includes IPNS records in routing, local keystore keys, and node resolver caches.

Dependencies and integration points: covers IPNS republisher scheduling, record TTL/lifetime handling, routing publication, key-specific publishing, and resolver cache behavior.

Risks and test signals: catches records expiring without republish, resolve cache masking failures, and alternate-key republishing bugs. Passing is successful resolution to the expected `/ipfs/<hash>` when republish should have occurred and failure when it should not.
