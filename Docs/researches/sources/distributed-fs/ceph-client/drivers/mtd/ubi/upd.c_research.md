# sources/distributed-fs/ceph-client/drivers/mtd/ubi/upd.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/upd.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/upd.c

Purpose: this file implements whole-volume update and atomic LEB change support. Volume updates are made crash-detectable by an update marker stored in the volume table; interrupted updates leave the volume treated as damaged until a new update completes. Atomic LEB change collects replacement data and asks EBA to switch a single LEB atomically.

Important APIs, types, and functions: public internal entry points are `ubi_start_update()`, `ubi_more_update_data()`, `ubi_start_leb_change()`, and `ubi_more_leb_change_data()`. Internal helpers `set_update_marker()`, `clear_update_marker()`, and `write_leb()` manage the volume-table marker and per-LEB write semantics for dynamic versus static volumes.

Control flow: starting an update allocates a full LEB update buffer, sets the persistent update marker, unmaps every reserved LEB, flushes all WL erase work, and either clears the marker for zero-byte updates or initializes expected byte/LEB counters. Incremental update writes copy user data into `vol->upd_buf`, flush complete LEBs or the final partial LEB via `write_leb()`, and when all bytes arrive flush WL work, clear the marker, update static-volume size/corruption fields, free the buffer, and return the number of bytes accepted in the final call. Atomic LEB change similarly accumulates user data and calls `ubi_eba_atomic_leb_change()` once all bytes are present.

State and persistence behavior: the persistent state is `vtbl_rec.upd_marker`, written through `ubi_change_vtbl_record()`. Runtime state is `vol->updating`, `vol->changing_leb`, `upd_bytes`, `upd_received`, `upd_ebs`, `ch_lnum`, and `upd_buf`. Static-volume completion updates `used_bytes`, `used_ebs`, `last_eb_bytes`, and clears `corrupted`; dynamic updates trim trailing `0xFF` to keep later append space writable.

Dependencies and integration points: update marker writes go through the volume table path. LEB unmap/write/change calls go through EBA. WL flushing ensures old mappings are physically processed before update completion. User data is copied with `copy_from_user()`, and size arithmetic uses alignment and division helpers from Linux.

Risks: error paths after setting `vol->updating` or allocating `upd_buf` can leave cleanup responsibilities to the ioctl caller or higher layers; callers must serialize through volume/device locks. Whole-volume update first unmaps all LEBs, so the update marker is the main protection against exposing partial contents after reboot. Static-volume final LEB writes can be unaligned at the logical data level but must be padded correctly. Dynamic-volume trimming of trailing `0xFF` is required for writable free space and can change what is physically mapped.

Test signals: simulate interrupted updates and verify `upd_marker` blocks normal IO; complete zero-byte, dynamic, and static updates; write updates in small chunks crossing LEB boundaries; verify static `used_bytes` and CRC checking after update; inject EBA/WL failures; test atomic LEB change power-cut behavior; and verify dynamic trailing-FF trimming leaves all-FF LEBs unmapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/upd.c -->
