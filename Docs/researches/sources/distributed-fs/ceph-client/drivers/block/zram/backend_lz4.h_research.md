# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4.h

Purpose: declaration header for the LZ4 zram backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_lz4`.

Control flow and state: none.

Dependencies and integration: used by the zcomp backend registry.

Risks: symbol mismatch only.

Test signals: compile coverage with `CONFIG_ZRAM_BACKEND_LZ4`.
