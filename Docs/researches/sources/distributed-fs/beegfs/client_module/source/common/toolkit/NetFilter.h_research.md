# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NetFilter.h

## Purpose
Defines the public IP filter data structures and operations for BeeGFS kernel networking.

## Important APIs and types
`NetFilterEntry` stores an IPv6 mask and a pre-masked compare address. `NetFilter` stores a dynamically allocated array and entry count. The public API covers init/construct/uninit/destruct, `NetFilter_isAllowed`, `NetFilter_isContained`, and an inline `NetFilter_getNumFilterEntries`.

## State, dependencies, integration
The header depends on kernel IPv4/IPv6 types and `common/Common.h`. It exposes raw array ownership only to implementation code; external users should treat `NetFilter` as an opaque-ish struct and call lifecycle helpers. It is integrated through `App_getNetFilter` and datagram sending.

## Risks and test signals
Callers must not call `NetFilter_isAllowed` before successful init because the struct contains raw pointers. Empty filters are intentionally permissive. Tests should verify lifecycle cleanup, count reporting, and that filter logic remains IPv4-mapped compatible.
