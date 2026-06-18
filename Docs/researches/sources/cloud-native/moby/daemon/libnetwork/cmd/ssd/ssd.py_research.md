<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/ssd.py -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/ssd.py

## Purpose
Python 2 diagnostic utility for swarm service discovery. It compares Docker daemon network/service data with per-namespace IPVS state, validates ingress iptables DNAT, and can compare gossip hashes across nodes.

## Important APIs, Types, And Functions
`which` locates binaries. `check_iptables` checks `DOCKER-INGRESS` NAT rules for published ports. `get_namespaces` maps containers or ingress sandbox to netns paths. `check_network` inspects a network, builds service fwmark-to-task mappings, enters namespaces, parses `ipvsadm -ln`, and compares real backends. Main modes are `default`, `gossip-consistency`, and `gossip-hash`.

## Control Flow
Default mode checks the requested network and ingress. Gossip-consistency creates a global `gossip-hash` service running the same image, waits, reads service logs, prints hashes, and removes the service. Gossip-hash inspects network service/task metadata, builds a sorted entry list, prints an MD5, flushes stdout, then waits forever.

## State And Persistence
State is external: Docker service definitions, task logs, kernel IPVS tables, iptables rules, and network namespaces. The script itself keeps transient dictionaries of fwmarks, expected tasks, and observed IPVS backends.

## Dependencies And Integration Points
Requires Docker Engine API over the Unix socket, docker-py, `nsenter`, `ipvsadm`, `iptables`, `bash`, and historical output formats such as `ifconfig eth1` with `inet addr`.

## Risks And Edge Cases
The script is Python 2-only, uses old docker-py APIs, and hashes strings without explicit byte encoding. `which` can return `None`; command construction often assumes valid paths. `get_namespaces` has awkward loop state but ultimately uses container IDs from inspect data. It prints mismatches rather than exiting nonzero for many failures, so automation must parse output.

## Test Signals
Expected output includes `service ... OK` for matching IPVS backends, printed ingress DNAT-missing messages when NAT is wrong, and matching gossip hashes across nodes for consistent control-plane state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/ssd.py -->
