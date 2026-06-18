# sources/cloud-native/moby/integration-cli/docker_cli_network_unix_test.go

Purpose: comprehensive Unix network integration coverage for `docker network`, container network settings, remote network/IPAM plugins, daemon restart persistence, aliases, DNS, host/default bridge behavior, port mapping interactions, and conntrack cleanup.

Important APIs and functions: `DockerNetworkSuite` setup/teardown, `setupRemoteNetworkDrivers`, helpers `assertNwIsAvailable`, `assertNwNotAvailable`, `assertNwList`, `getNwResource`, `connectContainerToNetworks`, `verifyContainerIsConnectedToNetworks`, `verifyPortMap`, `verifyIPAddressConfig`, and `verifyIPAddresses`. It uses API structs from `container` and `network`, libnetwork remote driver/IPAM APIs, plugin spec files, `netlink`, `nlwrap`, and `unix`.

Control flow: suite setup starts an `httptest.Server` that implements network and IPAM plugin endpoints and writes `/etc/docker/plugins/*.spec`. Tests then cover default networks, create/rm/list filters, inspect by name/ID/multiple inputs, connect/disconnect paths, IPAM valid and invalid combinations, plugin v2 network drivers, default bridge discovery, anonymous endpoints, links, overlay-like port output, graceful and ungraceful daemon restarts, host mode restrictions, port mapping stability across network connect/disconnect, MAC assignment, stopped-container network edits, preferred IPv4/IPv6/link-local addresses, alias scoping, embedded DNS, internal networks, special-character names, live-restore bridge restoration, IP validation, bridge disconnect by ID, and conntrack flow deletion.

State and persistence: this file mutates daemon networks, plugin spec files under `/etc/docker/plugins`, kernel links/veths, conntrack tables, container endpoint configs, daemon restart state, IP allocation state, `/etc/hosts`, and port bindings. Several tests explicitly restart or kill daemons to validate disk-persisted network attachments and live-restore behavior.

Dependencies and integration points: Linux-only kernel networking, local daemon control, busybox/debian images, libnetwork remote driver contract, plugin installation, API inspect JSON, netlink, DNS at `127.0.0.11`, and swarm/overlay-adjacent behavior through dummy drivers.

Risks: high environmental sensitivity: requires local Linux privileges, available subnets/ports, netlink/conntrack access, amd64 for some plugin tests, and stable timing around daemon restart. Global `/etc/docker/plugins` writes and kernel resources must be cleaned or later tests can fail.

Test signals: network commands must reject invalid built-ins, preserve inspect and endpoint state, maintain IP/MAC/alias/link-local settings across starts and restarts, keep port mappings coherent, keep DNS scoped to user-defined networks, avoid stale inspect mutations after failed connects, restore live bridge allocations, and remove NAT conntrack flows when containers are deleted.
