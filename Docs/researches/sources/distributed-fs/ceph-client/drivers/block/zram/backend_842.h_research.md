# sources/distributed-fs/ceph-client/drivers/block/zram/backend_842.h

Purpose: declaration header for the zram 842 backend.

Important APIs/types/functions: includes `zcomp.h` and declares `extern const struct zcomp_ops backend_842`.

Control flow and state: no runtime control flow or mutable state.

Dependencies and integration: allows `zcomp.c` to reference the backend ops table when `CONFIG_ZRAM_BACKEND_842` is enabled.

Risks: declaration must match the C file symbol name; include guard prevents duplicate declarations.

Test signals: compile with 842 backend enabled and disabled.
