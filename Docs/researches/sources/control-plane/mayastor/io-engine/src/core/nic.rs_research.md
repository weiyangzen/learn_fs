# sources/control-plane/mayastor/io-engine/src/core/nic.rs

## Purpose
Discovers and filters network interfaces for NVMf target address selection, with helpers for IP, subnet, MAC, and IPv4/IPv6 preference handling.

## Important APIs, Types, and Functions
- `SIpAddr` wraps IPv4 or IPv6 plus optional scope ID and converts from socket addresses.
- `InetConfig<T>` stores address/netmask pairs.
- `MacAddr` parses and formats six-byte MAC addresses.
- `Interface` stores name, IPv4/IPv6 configs, and MAC, with matching and sorting helpers.
- `find_all_nics()` enumerates system interfaces via `nix::ifaddrs`.
- `parse_ip` and `parse_ip_subnet` parse address and CIDR filters.

## Control Flow and State
`find_all_nics` iterates `getifaddrs`, creates an `Interface` for each address record, fills IPv4, IPv6, MAC, and netmask fields when present, skips scoped IPv6 addresses, and returns entries that have at least one IP address. `Interface` methods filter by exact IP, subnet, or preference order. IPv6 sorting prefers unique local, then link local, then non-unspecified, then non-multicast addresses.

No state is retained; discovery is live system state.

## Dependencies and Integration Points
Used by `MayastorEnvironment::detect_nvmf_tgt_iface_ip` to resolve `--tgt-iface` values. Depends on `nix::ifaddrs` and standard network types.

## Risks and Test Signals
`getifaddrs().unwrap()` can panic if interface enumeration fails. Multiple `getifaddrs` records for the same interface are not merged, so name/MAC filters may return partial records depending on ordering. IPv6 scope IDs are skipped. Tests should cover MAC parsing, subnet masks including `/0`, v4/v6 preference, exact matching, and multi-address interface behavior.
