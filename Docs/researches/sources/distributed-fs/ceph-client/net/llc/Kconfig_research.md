# sources/distributed-fs/ceph-client/net/llc/Kconfig

## Purpose
This Kconfig file defines the base LLC support symbol and the user-visible LLC type 2 socket support symbol.

## Important APIs, Types, and Functions
`LLC` is a tristate base symbol without a prompt. `LLC2` is a tristate prompt for ANSI/IEEE 802.2 LLC type 2 support and selects `LLC`.

## Control Flow
The configuration controls compilation of the base LLC object and the LLC2 connection-oriented/socket object. Selecting LLC2 makes PF_LLC sockets available through the corresponding source files.

## State and Persistence
No runtime state exists here. Kconfig state determines build output and module availability.

## Dependencies and Integration Points
`LLC2` integrates with PF_LLC sockets, LLC station/SAP/connection code, procfs, and sysctl support depending on other kernel symbols.

## Risks and Edge Cases
Because `LLC` is selected by `LLC2`, base LLC may be built without a direct prompt. Build and packaging logic should not assume LLC2 is always present when LLC core exists.

## Test Signals
Build tests should cover LLC core only where selected by other users, LLC2 as built-in, LLC2 as module, and proc/sysctl combinations.
