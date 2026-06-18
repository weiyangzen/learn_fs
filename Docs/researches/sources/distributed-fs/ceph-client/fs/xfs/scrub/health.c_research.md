<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/health.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/health.c

Purpose: Maps scrub results to XFS in-core health state, clearing or setting sick flags for filesystem, allocation group, realtime group, and inode metadata after scrub and repair.

Important APIs, types, and functions: Defines `enum xchk_health_group`, `struct xchk_health_map`, and `type_to_health_flag[]`, mapping scrub types to health groups and sick masks. Public functions include `xchk_health_mask_for_scrub_type()`, `xchk_update_health()`, `xchk_ag_btree_del_cursor_if_sick()`, `xchk_mark_healthy_if_clean()`, `xchk_file_looks_zapped()`, and `xchk_health_record()`.

Control flow: `xchk_update_health()` handles the special HEALTHY scrub type, determines whether scrub found direct or cross-reference corruption, merges `healthy_mask` when clean, and updates the target group. Inode repairs add `XFS_SICK_INO_FORGET` so sickness does not survive inode inactivation incorrectly. `xchk_ag_btree_del_cursor_if_sick()` drops cross-reference btree cursors if the referenced structure is already known sick, except when that structure is the primary scrub target or was just repaired. `xchk_health_record()` scans fs, AG, and realtime group health for lingering primary sickness.

State and persistence: Health flags are in-core state associated with mount, perag/rtgroup objects, and inodes. The file does not write on-disk metadata, but it changes what future scrub and health reporting believe is sick, healthy, zapped, or too unreliable for cross-reference.

Dependencies and integration points: Depends on `xfs_health` APIs, scrub type constants, btree cursor sick masks, perag/rtgroup iteration, and scrub output flags. It gates cross-reference behavior throughout scrub and records repair effectiveness after rescrub.

Risks and test signals: Incorrect mapping can hide corruption or keep fixed metadata marked sick. Test every scrub type mapping, clean vs corrupt vs xcorrupt outcomes, HEALTHY full-fs clearing, already-fixed AG repairs, inode inactivation during repair, cursor deletion for sick xref btrees, zapped-file detection, and health-record scans over AG and realtime group primary flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/health.c -->
