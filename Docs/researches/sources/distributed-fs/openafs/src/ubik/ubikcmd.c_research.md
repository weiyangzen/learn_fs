
# sources/distributed-fs/openafs/src/ubik/ubikcmd.c

`ubikcmd.c` provides command-line parsing helpers for Ubik server applications. Its single API, `ubik_ParseServerList`, discovers the local host address, parses `-servers`, filters the local host out of the peer list, recognizes `-dubik`, and returns a null-terminated server list.

The function resolves the current hostname with `gethostname`/`gethostbyname`, stores that address in `*ahost`, then walks argv. While inside the `-servers` list, it resolves hostnames, appends non-local addresses until `MAXSERVERS`, and stops on the next option. It separately records whether `-servers` was present and sets global `ubik_debugFlag` when `-dubik` is seen.

There is no persistence; output is in-memory network-order addresses consumed by `ubik_ServerInit`. Dependencies are libc host lookup, Rx/XDR includes, AFS locks, `ubik.h`, and the global debug flag.

Risks are mostly operational: fixed 64-byte local hostname buffer, old `gethostbyname` IPv4 behavior, no duplicate peer suppression besides the local address, and strict dependence on a `-servers` argument. Test signals are parser-level: missing `-servers` returns `UNOENT`, unknown host returns `UBADHOST`, overlong server list returns `UNHOSTS`, local host is excluded, and `-dubik` toggles debug output.
