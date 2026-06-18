<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr_cmds.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr_cmds.c

Purpose: implements the MTD command set for first-generation LPDDR flash discovered through QINFO/PFOW. It provides NOR-like read, write-buffer, erase, lock/unlock, and direct-point operations with chip-state arbitration.

Important APIs, types, and functions: exported `lpddr_cmdset()` allocates and fills `mtd_info`, initializes `flchip` and `flchip_shared` state, and installs MTD callbacks. Core helpers are `get_chip()`, `chip_ready()`, `put_chip()`, `wait_for_ready()`, `do_write_buffer()`, `do_erase_oneblock()`, `lpddr_writev()`, `lpddr_point()`, and `do_xxlock()`.

Control flow: operations take the target chip mutex, arbitrate shared write/erase ownership, optionally suspend erase for reads/points, issue PFOW commands, and wait for DSR ready/error bits. Writes split vectors on program-buffer boundaries, fill the PFOW program buffer, execute buffer program, and update `retlen`. Erases walk uniform erase blocks. `point()` exposes linear memory when map layout permits and increments chip point references until `unpoint()`.

State and persistence: persistent state is flash contents plus hardware block locks. Runtime state includes `flchip.state`, `oldstate`, wait queues, erase/write suspend flags, point reference counts, and shared write/erase ownership across hardware partitions.

Dependencies and integration points: depends on `linux/mtd/pfow.h`, `linux/mtd/qinfo.h`, map APIs, and QINFO probe code that sets `map->fldrv_priv`. It exports `lpddr_cmdset()` for `qinfo_probe.c`.

Risks: concurrency is intricate: shared engine handoff, suspend/resume, and wait-queue paths must preserve chip state. Timeout values derive from QINFO and default to busy polling when absent. VPP, XIP, and OTP are TODOs. Test signals include buffer writes across boundaries, erase suspend during reads, lock/unlock failures on protected blocks, point/unpoint refcounting, DSR error decoding, and parallel partition contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr_cmds.c -->
