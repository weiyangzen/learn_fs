# sources/distributed-fs/ceph-client/include/keys/dns_resolver-type.h

Source read summary: 16 lines, 364 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/dns_resolver-type.h` declares the DNS resolver key type used to cache DNS lookup results in the kernel key retention service.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: none. Important constants/macros: none.

Control flow: Network filesystems and other clients request DNS keys; resolver upcalls instantiate this key type and later consumers read cached resolution payloads.

State and persistence behavior: Resolved records persist in keyrings until timeout, revocation, or garbage collection.

Dependencies and integration points: It includes `linux/key-type.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Stale or malformed resolver payloads can misdirect network mounts; TTL and negative-result behavior need careful handling in the implementation.

Test signals: Test request-key DNS upcalls, cache expiry, negative lookups, and consumers such as CIFS/NFS/Ceph that rely on resolver keys.
