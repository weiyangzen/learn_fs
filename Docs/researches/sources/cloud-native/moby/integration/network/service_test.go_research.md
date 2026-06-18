<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/service_test.go -->
# sources/cloud-native/moby/integration/network/service_test.go

Purpose: integration suite for daemon network-pool persistence, swarm service/network behavior, ingress/default address pool configuration, live-restore custom interface names, and dynamic interface naming collisions.

Important APIs/types/functions: helper `delInterface` deletes a link and flushes iptables. Tests include daemon restart/pool cases, `TestServiceWithPredefinedNetwork`, skipped `TestServiceRemoveKeepsIngressNetwork`, `swarmIngressReady`, `noServices`, `TestServiceWithDataPathPortInit`, `TestServiceWithDefaultAddressPoolInit`, `TestCustomIfnameIsPreservedOnLiveRestore`, `TestCustomIfnameCollidesWithExistingIface`, `TestCustomIfnameWithMatchingDynamicPrefix`, and `checkIfaceAddr`.

Control flow: daemon pool tests start/restart daemons with `--default-address-pool`, `--bip`, and `--live-restore`, inspect bridge/user-network subnets, and ensure existing networks keep prior allocations. Swarm tests create services on predefined/overlay networks, poll task counts, inspect/remove services, validate data-path port and default address pool allocation for ingress and user overlay networks. Custom-ifname tests run containers with endpoint driver options, restart live-restore daemons, disconnect networks, provoke `eth0` rename collision, and verify dynamic `ethN` reuse after disconnect/reconnect.

State/persistence: mutates `docker0`, iptables, daemon network store, swarm cluster state, ingress/overlay networks, services/tasks, live-restore container sandbox state, and container interface names. Cleanup removes services/networks and may restart daemons to restore default state.

Dependencies/integration: daemon and swarm helpers, Docker API network/service clients, internal container/network helpers, bridge/netlabel options, `ip`/`iptables`, polling, and BusyBox. Many tests skip Windows, rootless, or remote daemon modes.

Risks: broad host-network mutations (`delInterface` and iptables flush) can affect neighboring tests if cleanup fails. Address-pool tests assume deterministic allocator order. Swarm tests can be timing-sensitive and one ingress test is explicitly skipped as flaky. Interface-name assertions encode live-restore sandbox reconstruction details.

Test signals: passing tests verify default pools do not overwrite existing networks or `--bip`, swarm services work with host/predefined networks, data-path/default address pools initialize as configured, ingress/default overlay subnets are allocated as expected, custom interface names survive live restore and collision/reuse behavior is correct.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/service_test.go -->
