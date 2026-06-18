# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-priv.h

## Purpose
This private header defines the internal data structures used by the K3 PSI-L endpoint library and declares every SoC endpoint map compiled into the TI DMA PSI-L object.

## Important APIs, Types, and Functions
`struct psil_ep` pairs a 32-bit thread ID with a `struct psil_endpoint_config`. `struct psil_ep_map` names a SoC map and stores source and destination endpoint arrays with counts. `psil_get_ep_config()` is declared for endpoint lookup. The header declares external map objects for AM654, J721E, J7200, AM64, J721S2, AM62, AM62A, J784S4, and AM62P.

## Control Flow
The header has no control flow, but its comment documents generic lookup behavior: if a destination thread has no explicit destination entry, the library masks the destination-thread offset and tries to find a symmetric source entry.

## State and Persistence
It defines the shape of static endpoint-map state. Because maps expose mutable endpoint config objects through pointers, these structures are both configuration tables and runtime state if modified by `psil_set_new_ep_config()`.

## Dependencies and Integration Points
The header depends on `linux/dma/k3-psil.h` for public endpoint configuration definitions. It is included by `k3-psil.c` and all SoC map files. The extern declarations must stay synchronized with the Makefile and SoC match table.

## Risks
Count fields must match array sizes; every map file uses `ARRAY_SIZE()` for this. Adding a new SoC requires coordinated edits here, in the generic selector, and in the Makefile. The symmetric fallback behavior means missing destination entries can be intentional or accidental, so table review must understand endpoint directionality.

## Test Signals
Build tests catch missing extern/object mismatches. Runtime lookup tests should verify explicit destination, symmetric fallback, and not-found behavior for at least one map. Static analysis can ensure every extern map has a Makefile object and a selector entry.
