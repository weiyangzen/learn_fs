# sources/distributed-fs/moosefs/mfsmaster/appendres.h

This header exposes the append-reservation table API to mfsmaster filesystem code while keeping the backing hash table private.

It declares `appendres_getvleng`, `appendres_setvleng`, `appendres_setrleng`, `appendres_clear`, `appendres_cleanall`, and `appendres_init`. Callers pass only inode numbers and lengths; the implementation owns all allocation and lookup state.

The intended lifecycle is initialize once, set a virtual length for an append reservation, query it while operations are in flight, retire it when real length catches up, and clear one or all reservations during cleanup. No persistent format or synchronization primitive is exposed.

The header depends only on `<inttypes.h>` and is integrated through `filesystem.c` and the mfsmaster build. Risks are that callers receive no allocation/status feedback and no documented locking contract. Test signals are compile coverage from consumers plus implementation tests for the declared lifecycle.
