# sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/src/addr.c

## Purpose
Implements address-based RPC authentication for protocol/server. It accepts or rejects clients based on configured allow/reject address patterns for the requested remote subvolume, optional subdir-specific rules, address family, and privileged-port policy.

## Important APIs, Types, And Functions
`gf_auth()` is the exported auth entry point. It reads `remote-subvolume`, `peer-info`, `subdir-mount`, `auth.addr.<subvol>.allow`, `auth.addr.<subvol>.reject`, legacy `auth.ip.<subvol>.allow`, and `rpc-auth-allow-insecure`. `parse_entries_and_compare()` handles either legacy comma-delimited address lists or subdir form `/dir(addr|addr),/other(addr)`. `compare_addr_and_update()` checks hostnames, CIDR/network strings, fnmatch patterns, and negated entries. `options[]` documents allow/reject options.

## Control Flow
`gf_auth()` starts as `AUTH_DONT_CARE`. It finds configured allow/reject lists, extracts the peer address from IPv4/IPv6/SDP or UNIX peer info, rejects unprivileged TCP ports unless insecure auth is allowed, applies reject rules first, and then allow rules. A matching reject returns `AUTH_REJECT`; a matching allow returns `AUTH_ACCEPT`; absent or nonmatching configuration leaves `AUTH_DONT_CARE`.

## State And Persistence
No persistent module state. All decisions are computed from input and config dictionaries per authentication call.

## Dependencies And Integration Points
Uses Gluster dict/data helpers, `authenticate.h`, `rpc-transport.h`, peer info, `gf_is_same_address()`, `gf_is_ip_in_net()`, `valid_host_name()`, `fnmatch()`, and socket address families. Loaded by the protocol server auth framework.

## Risks
Parsing mutates duplicated option strings with `strtok_r`; invalid subdir syntax can abort processing early. The comment notes that a negation flag is not reset per entry in `compare_addr_and_update()`, so a negated entry can affect later entries in the same call. `strrchr(peer_addr, ':')` is assumed to find a service separator for IP peers. Reject is evaluated before allow, which is safe but must be documented for operators.

## Test Signals
Cover IPv4, IPv6, UNIX sockets, privileged and unprivileged ports, `rpc-auth-allow-insecure`, wildcard/hostname/CIDR/fnmatch entries, negated entries, reject-before-allow, legacy `auth.ip.*.allow`, subdir-specific rules, malformed subdir entries, and missing peer info.
