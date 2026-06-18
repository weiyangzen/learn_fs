# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_stats.h

Purpose: internal stats/debugfs header for OCRDMA. It declares the debugfs text-buffer size, enumerates all debugfs stats file types, and exposes stats lifecycle, per-port debugfs, and PMA counter functions to the rest of the driver.

Important APIs/types/functions: `OCRDMA_MAX_DBGFS_MEM` fixes each device's debugfs formatting buffer at 4096 bytes. `enum OCRDMA_STATS_TYPE` assigns identifiers for resource, RX, WQE, TX, doorbell error, RX/TX QP error, TX/RX debug, driver debug, and reset stats. Prototypes cover global debugfs root creation/removal, per-device stats memory allocation/release, per-port stats file add/remove, and `ocrdma_pma_counters()`.

Control flow: `ocrdma_main.c` calls `ocrdma_init_debugfs()` at module init and `ocrdma_rem_debugfs()` at exit. Device add calls `ocrdma_alloc_stats_resources()` before registration and `ocrdma_add_port_stats()` after link query; removal reverses this through `ocrdma_rem_port_stats()` and `ocrdma_release_stats_resources()`. MAD handling calls `ocrdma_pma_counters()` to fill standard port counters.

State and persistence: no data is defined directly in this header, but the enum values are stored in per-device `struct ocrdma_stats` instances and used as dispatch keys by `ocrdma_stats.c`. The buffer size constant constrains persistent debugfs scratch memory allocated in `dev->stats_mem`.

Dependencies/integration: includes `linux/debugfs.h`, `ocrdma.h`, and `ocrdma_hw.h`, creating a dependency cycle where stats declarations also see hardware mailbox prototypes and SLI layouts. It exposes `struct ib_mad` usage through the PMA prototype.

Risks and test signals: adding a new enum value requires matching debugfs descriptor initialization and read dispatch or reads will fail with `-EFAULT`. Changing `OCRDMA_MAX_DBGFS_MEM` affects stackless formatting assumptions and user-visible debugfs output length. Test compile coverage for include cycles, debugfs file creation for every enum type, PMA counter calls with stats disabled or allocation failed, and cleanup paths when debugfs root creation returns NULL or an error dentry.
