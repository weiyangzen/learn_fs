# sources/distributed-fs/ceph-client/drivers/block/zram/backend_zstd.h

Purpose: declaration header for the Zstandard zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_zstd`.

Control flow and state: none.

Dependencies and integration: used by zcomp when ZSTD backend support is configured.

Risks: symbol/header synchronization only.

Test signals: compile with ZSTD backend enabled.
