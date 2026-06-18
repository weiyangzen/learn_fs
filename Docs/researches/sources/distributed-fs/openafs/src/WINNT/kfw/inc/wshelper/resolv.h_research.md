# sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/resolv.h

## Purpose

`resolv.h` declares a BIND-style resolver interface implemented on Windows. It exposes resolver state, DNS search options, query/compression functions, and compatibility stubs for unsupported resolver APIs.

## Important APIs, types, and functions

Constants include `MAXNS`, `MAXDFLSRCH`, `MAXDNSRCH`, `LOCALDOMAINPARTS`, `RES_TIMEOUT`, and `MAXMXRECS`. `struct mxent` stores MX preferences and hostnames. `struct state` stores retry timing, option flags, name server addresses, packet id, default domain, and search list. Resolver option flags include `RES_INIT`, `RES_DEBUG`, `RES_USEVC`, `RES_RECURSE`, `RES_DEFNAMES`, `RES_DNSRCH`, and `RES_DEFAULT`. Public APIs are `res_init`, `res_search`, `dn_comp`, `rdn_expand`, `res_setopts`, `res_getopts`, `res_mkquery`, `res_send`, and `res_querydomain`. The macro `dn_expand` is redirected to `rdn_expand`.

## Control flow

The intended runtime flow is to call `res_init` to populate global `_res`, then call `res_search` with a DNS name, class, and type. Compression helpers encode and expand DNS names while maintaining pointer tables. Unsupported functions are declared for compatibility but documented as unsupported.

## State and persistence behavior

The global `extern struct state _res` holds resolver process state: retry settings, options, name servers, default domain, and search domains. `res_init` reads environment, local host/domain, registry, or resolver files to populate this state. Query buffers are caller-owned.

## Dependencies and integration points

The header includes `windows.h`, `arpa/nameser.h`, and `stdio.h`. It is included by `wshelper.h`, which layers host, service, and Hesiod helpers over these resolver primitives. The `dn_expand` redirection avoids conflict with Microsoft library implementations.

## Risks and edge cases

Global `_res` state is mutable and potentially non-thread-safe. The answer buffer contract requires callers to compare returned response size with `anslen` to detect truncation. Legacy option flags include virtual-circuit and stay-open semantics that may not be implemented when backed by Windows DNS APIs. Macro remapping of `dn_expand` can surprise consumers expecting the Winsock symbol.

## Test signals

Tests should cover `res_init` with environment, registry, and fallback inputs; `res_search` response sizing; name compression/decompression including loops and bounds; `dn_expand` macro behavior; and unsupported function return behavior.
