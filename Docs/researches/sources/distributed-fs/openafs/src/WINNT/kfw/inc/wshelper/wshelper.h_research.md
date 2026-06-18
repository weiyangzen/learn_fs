# sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/wshelper.h

## Purpose

`wshelper.h` is the top-level public header for the Windows WSHelper DNS/Hesiod compatibility library. It exposes resolver-backed replacements for host, service, address parsing, hostname, and domain-name lookup APIs.

## Important APIs, types, and functions

Supported APIs are `rgethostbyname`, `rgethostbyaddr`, `rgetservbyname`, `inet_aton`, `wsh_gethostname`, and `wsh_getdomainname`. Declared unsupported placeholders are `gethinfobyname`, `getmxbyname`, `getrecordbyname`, and `rrhost`.

## Control flow

Callers use `rgethostbyname` or `rgethostbyaddr` to obtain library-owned `hostent` structures, `rgetservbyname` for service data, `inet_aton` to parse IPv4 dotted strings, and `wsh_gethostname`/`wsh_getdomainname` to discover local naming. Simple hostnames are documented as expanded using the default domain search behavior.

## State and persistence behavior

Returned `hostent` and `servent` structures are library-owned and only one copy is allocated per call per thread, so callers must copy data they need to retain. Resolver configuration state is inherited from `resolv.h` and `mitwhich.h`.

## Dependencies and integration points

The header includes `winsock.h`, `mitwhich.h`, `resolv.h`, and `hesiod.h`. It provides a Unix-like lookup surface for Windows components that expect BIND/Hesiod semantics.

## Risks and edge cases

The API mixes supported and unsupported functions in one header. Static/thread-local result ownership can cause use-after-next-call bugs. It is IPv4-centric through `inet_aton` and older Winsock structures. Name expansion depends on resolver defaults that may be MIT-specific unless configured.

## Test signals

Tests should verify host lookup with simple and fully qualified names, reverse lookup, service lookup including protocol filtering, `inet_aton` acceptance/rejection cases, buffer sizing for hostname/domain functions, and repeated-call ownership behavior.
