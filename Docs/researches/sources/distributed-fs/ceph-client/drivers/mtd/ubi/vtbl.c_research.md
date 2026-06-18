# sources/distributed-fs/ceph-client/drivers/mtd/ubi/vtbl.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/vtbl.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/vtbl.c

Purpose: this file manages the on-flash volume table stored in the internal layout volume. It validates volume-table records, updates records atomically through the layout volume, recovers redundant table copies after unclean reboot, creates an empty layout volume on blank flash, and initializes in-memory `ubi_volume` objects from attach information.

Important APIs, types, and functions: main entry points are `ubi_change_vtbl_record()`, `ubi_vtbl_rename_volumes()`, and `ubi_read_volume_table()`. Key helpers include `ubi_update_layout_vol()`, `vtbl_check()`, `create_vtbl()`, `process_lvol()`, `create_empty_lvol()`, `init_volumes()`, `check_av()`, `check_attaching_info()`, and `self_vtbl_check()`. `empty_vtbl_record` holds the CRC of an all-zero record.

Control flow: record changes update the in-memory `ubi->vtbl`, compute CRCs, and write the full table to both layout-volume LEBs using `ubi_eba_atomic_leb_change()`. Attach computes slot count from LEB size, finds the layout volume in attach info, creates it if the flash is empty, or processes existing LEB0/LEB1 copies. `process_lvol()` prefers valid LEB0 as most recent, restores LEB1 from it if needed, or restores LEB0 from valid LEB1 when LEB0 is corrupted. `init_volumes()` allocates volume objects for nonempty records, handles autoresize and skip-check flags, initializes fastmap check maps, derives static-volume used sizes from scanned LEBs, and creates the internal layout volume object.

State and persistence behavior: the volume table is persistent, duplicated in layout volume LEB0 and LEB1, and protected per-record by CRC. The in-memory `ubi->vtbl` is the authoritative mutable copy while attached. Attach-time `ubi_attach_info` is reconciled against the table; unknown volumes found on flash can be discarded as unfinished removals. Layout-volume updates are atomic at the LEB level and preserve legacy redundancy.

Dependencies and integration points: it depends on EBA atomic LEB change, IO data reads/writes, attach allocation helpers, fastmap checkmap setup, UBI media constants, CRC32, and global PEB accounting. It is called before normal volume devices are registered and feeds `vmt.c` with initialized volumes.

Risks: attach recovery depends on the assumption that LEB0 is updated before LEB1 and is newer if both are valid but differ. Static volumes without scanned LEBs are treated as empty because the volume table does not store static data size, a documented limitation. Autoresize must appear on at most one volume. `vtbl_check()` must reject inconsistent alignment, duplicate names, invalid flags, and oversized reservations before runtime state is trusted.

Test signals: blank-flash attach creates two layout copies; corrupt LEB0 or LEB1 and verify restoration; corrupt both and reject attach; update table and simulate power cuts between copy updates; validate duplicate-name and bad-record rejection; attach static volumes with missing LEBs and observe corrupted/empty handling; autoresize flag detection; and consistency checks between attach info and volume records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/vtbl.c -->
