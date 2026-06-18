# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ring_reconfig.py

Purpose: Validates ethtool netlink channel and ring parameter reconfiguration while preserving traffic functionality.

Important APIs/functions: Uses `NetDrvEpEnv`, `EthtoolFamily.channels_get/set`, `rings_get/set`, `GenerateTraffic`, `defer`, and `NlError`. Tests are `channels` and `ringparam`; `_configure_min_ring_cnt` temporarily reduces channel count to speed ring testing.

Control flow: `channels` discovers supported `rx`, `tx`, and `combined` channel types, tries selected mixes at one queue and max queue counts, and verifies accepted settings read back exactly. `ringparam` records ring maxima/current values, halves each ring parameter until rejected to find the minimum accepted value, sends traffic, then tries max settings and sends traffic again if accepted.

State and persistence: Mutates ethtool channel and ring settings on the device under test. Deferred calls restore original settings.

Dependencies and integration: Requires ethtool netlink support, a local/remote endpoint capable of traffic generation, and driver support for channels/rings.

Risks: Max ring settings may be memory-heavy and are allowed to fail. Some drivers expose partial channel combinations and reject mixed configurations. Traffic generation is needed to catch reconfiguration that succeeds but leaves queues unusable.

Test signals: PASS means accepted channel/ring settings are readable back, traffic completes at minimized rings, and optional max ring settings do not break traffic when accepted.
