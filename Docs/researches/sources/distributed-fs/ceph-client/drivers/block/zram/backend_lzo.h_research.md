# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzo.h

Purpose: declaration header for the LZO zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_lzo`.

Control flow and state: none.

Dependencies and integration: used by `zcomp.c` for backend lookup.

Risks: symbol mismatch.

Test signals: compile with LZO backend enabled.
