# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4hc.h

Purpose: declaration header for the LZ4HC zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_lz4hc`.

Control flow and state: none.

Dependencies and integration: used by zcomp conditional backend registration.

Risks: symbol/header drift.

Test signals: compile with LZ4HC enabled.
