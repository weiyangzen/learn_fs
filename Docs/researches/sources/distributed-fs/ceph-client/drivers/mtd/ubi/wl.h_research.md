# sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.h

Purpose: this private header supplies wear-leveling declarations that vary with `CONFIG_MTD_UBI_FASTMAP`. It lets `wl.c` call static fastmap-aware helpers from the included fastmap WL implementation while keeping no-fastmap fallbacks minimal.

Important APIs, types, and functions: in fastmap builds it declares `update_fastmap_work_fn()`, `find_anchor_wl_entry()`, `get_peb_for_wl()`, `next_peb_for_wl()`, `need_wear_leveling()`, `ubi_fastmap_close()`, `ubi_fastmap_init()`, and `may_reserve_for_fm()`. Without fastmap it declares only `get_peb_for_wl()`, provides no-op `ubi_fastmap_close()` and `ubi_fastmap_init()`, and makes `may_reserve_for_fm()` return its input.

Control flow: `ubi_fastmap_init()` contributes fastmap reservation requirements to the caller's reserved PEB count, zeros pool reservations when fastmap is disabled, and initializes the fastmap work item. The no-fastmap branch compiles out these behaviors so WL uses its local non-fastmap `get_peb_for_wl()` implementation and plain wear-leveling threshold logic.

State and persistence behavior: this header itself stores no state. In fastmap mode it controls initialization of `ubi->fm_work` and reservation accounting for fastmap pools and two fastmap copies, which later affects persistent fastmap updates on flash. In no-fastmap mode no additional state is reserved.

Dependencies and integration points: it is included by `wl.c` after `ubi.h`. The declarations correspond to functions supplied either by `fastmap-wl.c` included from `wl.c` or by local no-fastmap functions at the end of `wl.c`.

Risks: because these functions are `static` declarations for code included into one translation unit, mismatches between `wl.h`, `wl.c`, and `fastmap-wl.c` can fail at compile time or subtly alter WL selection. Reservation math in `ubi_fastmap_init()` directly reduces available PEBs during WL init. The no-fastmap no-ops must keep behavior identical to older WL logic.

Test signals: build both fastmap and no-fastmap configurations; verify reserved PEB counts with fastmap enabled, disabled at runtime, and compiled out; confirm `fm_work` is initialized when needed; and exercise anchor reservation paths versus no-fastmap free-PEB selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.h -->
