# sources/distributed-fs/ceph-client/drivers/s390/cio/idset.h

Purpose: declares the opaque subchannel-ID set API implemented by `idset.c`.

Important APIs/types/functions: forward-declares `struct idset` and exposes creation, destruction, fill, subchannel add/delete/delete-subsequent/contains, empty check, and set-union functions.

Control flow: no direct control flow; callers allocate with `idset_sch_new()`, mutate/check, then free.

State and persistence behavior: hides bitmap storage details from users, keeping state opaque and in memory.

Dependencies and integration points: includes `asm/schid.h` for subchannel IDs and is consumed by CSS/CIO code that tracks scan/evaluation sets.

Risks and test signals: API lacks explicit bounds or locking in the header contract, so caller misuse can corrupt bitmap state. Compile coverage should ensure all users include the header rather than depending on implementation details.
