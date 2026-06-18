# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzorle.h

Purpose: declaration header for the LZO-RLE zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_lzorle`.

Control flow and state: none.

Dependencies and integration: consumed by zcomp's backend list.

Risks: symbol/header drift.

Test signals: compile with LZO backend support.
