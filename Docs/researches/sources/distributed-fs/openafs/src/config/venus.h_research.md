# sources/distributed-fs/openafs/src/config/venus.h

This installed header defines data structures used with Venus/cache-manager pioctls. It includes `afs/vioc.h` for ioctl command numbers and, outside `UKERNEL`, `netinet/in.h` for IPv4 server preference structures.

Important types include `spref`, `sprefrequest_33`, `sprefrequest`, `sprefinfo`, `setspref`, `gaginfo`, `rxparams`, `chservinfo`, `sbstruct`, and versioned `cm_initparams`. These structures carry server ranks, get/set server preference requests, cache-manager gag/log flags, RX tuning parameters, checkservers request state, store-behind settings, and cache manager initialization results. Constants include `DBservers`, `GAGUSER`, `GAGCONSOLE`, `logwritethruON`, and `CMI_VERSION`.

There is no runtime control flow; persistence occurs only through the pioctl consumers that serialize these structures to the cache manager. Dependencies are `vioc.h`, `afs/stds.h` types transitively, and network address types. Integration points are `fs`, `cmdebug`, cache-manager pioctl handlers, and any administrative tool using these structs. Risks are ABI compatibility, intentionally overrun flexible one-element arrays, bitfield layout in `cm_initparams`, and structure size expectations across 32/64-bit builds. Test signals are pioctl round trips for server preferences, RX params, gag flags, and init params.
