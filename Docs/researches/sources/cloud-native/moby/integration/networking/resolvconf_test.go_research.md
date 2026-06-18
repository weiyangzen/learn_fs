# sources/cloud-native/moby/integration/networking/resolvconf_test.go

## Purpose
Tests Docker resolver behavior for localhost upstream resolvers, internal networks, container-local DNS servers, and Windows external DNS lookup. It protects resolver regressions around internal DNS forwarding and generated `/etc/resolv.conf`.

## Important APIs, Types, And Functions
Uses `daemon.WithResolvConf`, `network.GenResolvConf`, `network.StartDaftDNS`, `container.WithDNS`, bind mounts for `dnsd.conf`, and container `nslookup`. Network helpers create bridge networks with `WithInternal`, IPv6, and IPAM.

## Control Flow
`TestResolvConfLocalhostIPv6` starts a daemon whose host resolv.conf points at `127.0.0.53`, creates an IPv6 bridge network, runs a container, and compares generated `/etc/resolv.conf` text with the daemon path normalized. `TestInternalNetworkDNS` starts a loopback DNS server, verifies external DNS works on an external network, remains available after adding an internal network, fails with `SERVFAIL` after external disconnect, and works after reconnect. `TestInternalNetworkLocalDNS` runs a DNS server container on an internal network and queries it via `--dns` through Docker's internal resolver. `TestNslookupWindows` checks Windows external DNS forwarding for `docker.com`.

## State And Persistence Behavior
The tests mutate daemon resolver configuration, network attachments, and container DNS settings. They validate resolver behavior as network membership changes, not persistent daemon restarts.

## Dependencies And Integration Points
Integrates `/etc/resolv.conf` generation, Docker embedded DNS (`127.0.0.11`), host loopback DNS server behavior, internal network isolation, bind mounts, and Windows DNS proxy behavior.

## Risks
Assumes no conflicting DNS server on `127.0.0.1`, skips rootless when host loopback resolver is inaccessible, and uses external `docker.com` lookup on Windows. Exact resolv.conf text can change with resolver generation policy.

## Test Signals
Signals include exact resolv.conf content, `nslookup` exit codes, `SERVFAIL`, configured fake DNS response address, and Windows stdout containing `Addresses:`.
