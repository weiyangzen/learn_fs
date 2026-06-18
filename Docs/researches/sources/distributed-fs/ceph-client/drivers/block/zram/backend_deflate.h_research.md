# sources/distributed-fs/ceph-client/drivers/block/zram/backend_deflate.h

Purpose: declaration header for the deflate zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_deflate`.

Control flow and state: none.

Dependencies and integration: consumed by `zcomp.c` backend registration when deflate support is configured.

Risks: only symbol/header synchronization risk.

Test signals: compile coverage with `CONFIG_ZRAM_BACKEND_DEFLATE`.
