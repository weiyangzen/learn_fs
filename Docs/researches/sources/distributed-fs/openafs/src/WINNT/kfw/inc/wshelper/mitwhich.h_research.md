# sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/mitwhich.h

## Purpose

`mitwhich.h` defines legacy Windows operating-system, Winsock stack, DNS server, default domain, resolver configuration path, and TCP/IP registry-key constants used by wshelper to discover network configuration.

## Important APIs, types, and functions

OS/stack strings and identifiers include `NT_32`, `NT_16`, `W95_32`, `W95_16`, `LWP_16`, `MS_NT_32`, `MS_95_32`, `NOVELL_LWP_16`, `MS_OS_NT`, `MS_OS_2000`, `MS_OS_XP`, and related unknown codes. DNS fallback constants are `DNS1`, `DNS2`, `DNS3`, and `DEFAULT_DOMAIN`. Resolver and registry constants include `_PATH_RESCONF`, `NT_TCP_PATH`, `NT_TCP_PATH_TRANS`, `W95_TCP_PATH`, `NT_DOMAIN_KEY`, `NT_NS_KEY`, `W95_DOMAIN_KEY`, and `W95_NS_KEY`.

## Control flow

There is no runtime logic. Preprocessor branching sets `_PATH_RESCONF` to `/etc/resolv.conf` for non-Windows targets and `c:/net/tcp/resolv.cfg` for Windows targets.

## State and persistence behavior

The file creates no state, but it points resolver code at persistent registry paths and optional resolver configuration files. The DNS server defaults are compiled into binaries as last-resort configuration.

## Dependencies and integration points

`wshelper.h` includes this header, and resolver initialization code uses these registry keys and defaults to locate domain names and name servers on older Microsoft TCP/IP stacks.

## Risks and edge cases

The values are historically MIT-specific and include hard-coded DNS server IPs. Modern Windows networking may not use the old registry paths or stack names. Site administrators were expected to rebuild or edit resources for non-MIT defaults, so unmodified binaries can resolve through inappropriate fallback servers if discovery fails.

## Test signals

Resolver initialization tests should simulate registry-present, config-file-present, and fallback-only cases. Non-MIT packaging should verify these defaults are overridden where appropriate.
