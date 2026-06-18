# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_modparams.c

## Purpose
Declares socklnd module parameters, validates selected parameter values, exposes global tunable pointer tables, computes default `conns_per_peer`, and copies module/net defaults into per-NI LND tunables.

## Important APIs and functions
Parameters cover timeout, TX credits, peer credits, scheduler/connd counts, reconnect intervals, eager ACK, typed connections, bulk threshold, socket buffers, Nagle, round-robin, keepalive, checksum and checksum-error injection, zero-copy thresholds, IRQ affinity compatibility, `conns_per_peer`, route setup, optional TCP backoff, debug protocol override, and TOS. `ksocknal_tunables_init` populates `ksocknal_tunables` and `ksock_default_tunables`. `ksocknal_tunables_setup` merges module defaults with common LNet network tunables. `ksocklnd_lookup_conns_per_peer` estimates connections per peer from interface speed.

## Control flow
Module load registers parameters through `module_param*`. TOS uses a custom setter to allow -1 through 255 only. Interface speed lookup scans the NI namespace for the configured interface, supports IPv4 labels and IPv6 device-name matching, asks ethtool for speed, and maps Mbps to a small heuristic connection count. Init also caps zero-copy minimum payload and warns on removed IRQ affinity behavior.

## State and persistence
The file owns static module parameter storage for the module lifetime. `ksocknal_tunables` stores pointers to those variables, so runtime code observes current writable parameter values. `ksock_default_tunables` is copied into NIs that have not explicitly set LND tunables.

## Dependencies and integration points
Uses Linux module parameter APIs, ethtool, rtnl-protected netdevice enumeration, IPv4/IPv6 address lists, LNet NI/common tunable structs, and constants from `socklnd.h`.

## Risks and test signals
Risk areas include writable parameters changing while connections are active, speed lookup returning driver errors, IPv6 temporary-address selection, unit conversion for reconnect milliseconds, and `conns_per_peer` exceeding bitfield capacity. Tests should validate parameter bounds, TOS rejection, default merging, ethtool-failure fallback, IPv4 and IPv6 interface lookup, and that per-NI tunables are stable enough for active connection setup.
