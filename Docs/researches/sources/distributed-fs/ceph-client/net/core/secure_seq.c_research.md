# sources/distributed-fs/ceph-client/net/core/secure_seq.c

## Purpose

`secure_seq.c` generates keyed, hard-to-predict TCP initial sequence numbers, TCP timestamp offsets, and ephemeral-port hash values for IPv4 and IPv6. It uses a per-boot random SipHash key and mixes endpoint addresses, ports, and a time component where appropriate. The file supports TCP/IP hardening by avoiding trivially predictable sequence and port selection inputs.

## Important APIs, Types, And Functions

`net_secret` is a static `siphash_aligned_key_t` initialized once by `net_secret_init()` through `net_get_random_once()`. `EPHEMERAL_PORT_SHUFFLE_PERIOD` controls how often ephemeral-port hash inputs change, currently every `10 * HZ`.

For TCP sequence and timestamp offsets, IPv6 builds `secure_tcpv6_seq_and_ts_off()` when IPv6 or INET is enabled, and IPv4 builds `secure_tcp_seq_and_ts_off()` under `CONFIG_INET`. Both return `union tcp_seq_and_ts_off`, whose 64-bit hash output is interpreted as sequence and timestamp-offset fields. `seq_scale()` adds a real-time based increment to the sequence value to preserve TCP-style monotonic progression.

For ephemeral port selection, `secure_ipv6_port_ephemeral()` hashes IPv6 source/destination addresses, destination port, and a jiffies time seed. `secure_ipv4_port_ephemeral()` hashes IPv4 source/destination addresses, destination port, and the same period-scaled time seed.

## Control Flow

Every public function first ensures the secret is initialized. TCP sequence functions construct an aligned tuple of endpoint addresses and ports, hash it with SipHash, clear timestamp offset when `net->ipv4.sysctl_tcp_timestamps != 1`, scale the sequence with `seq_scale()`, and return the union. Ephemeral-port functions hash endpoint data plus `jiffies / EPHEMERAL_PORT_SHUFFLE_PERIOD` and return a 64-bit value to the caller's port-selection logic.

The IPv4 TCP function uses `siphash_3u32()` over source address, destination address, and packed ports. The IPv6 TCP function builds an aligned struct containing two `in6_addr` values and both ports, then hashes through the destination-port field. The comments document that a zero source port would collide with the IPv4 ephemeral-port helper, but TCP source port zero is not expected.

## State And Persistence Behavior

The only persistent state in this file is `net_secret`, a kernel-memory random key initialized once per boot. There is no per-net namespace secret here. The per-call time behavior comes from `ktime_get_real_ns()` for sequence scaling and `jiffies` for ephemeral-port shuffle periods. The generated values are deterministic for a given secret and input tuple within the relevant time component.

## Dependencies And Integration Points

The file depends on the random subsystem, SipHash helpers, TCP sequence/timestamp union definitions from `net/secure_seq.h`, IPv4/IPv6 address types, jiffies, and TCP timestamp sysctl state through `struct net`. It exports sequence and ephemeral helpers for TCP/IP stack code and port selection code.

## Risks And Edge Cases

The security property depends on `net_get_random_once()` producing a secret before outputs are useful to attackers. Because the secret is global rather than per-netns, namespace isolation does not imply independent sequence-generation keys.

Timestamp offset handling is conditional: if TCP timestamps are not exactly enabled as value `1`, timestamp offset is forced to zero while the sequence still uses the hash and time scaling. Consumers must not expect a timestamp offset under all timestamp sysctl modes.

The ephemeral-port hash intentionally changes only every shuffle period; shorter periods could cause instability, while longer periods give attackers a wider observation window. The IPv4 comment about source port zero documents an input-domain assumption that should remain true.

## Test Signals

Useful tests include build coverage for `CONFIG_INET`, IPv6-only, and combined configurations; checks that repeated calls are stable for fixed inputs within a port-shuffle period but change over time; validation that timestamp offsets are zero when TCP timestamps are disabled or not in mode `1`; and statistical/regression tests that no obvious endpoint tuple collisions are introduced by struct layout or byte-order changes.
