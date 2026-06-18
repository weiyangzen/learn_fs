# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/lm.c

Purpose: implements PDS live-migration anonymous files and VFIO migration state transition actions.

Important APIs and functions: migration file allocation/free, save read file op, restore write file op, `pds_vfio_step_device_state_locked()`, `pds_vfio_put_save_file()`, and `pds_vfio_put_restore_file()`.

Control flow: save file creation queries firmware state size, allocates a vmalloc-backed page buffer, creates a scatterlist for DMA, then `pds_vfio_get_lm_state_cmd()` fills it. User reads sequentially through page lookup. Restore creates a fixed-size state file, accepts sequential writes into pages, and on RESUMING->STOP issues `pds_vfio_set_lm_state_cmd()`. State transitions also drive full/P2P suspend/resume and dirty-disable cleanup.

State and persistence: `struct pds_vfio_lm_file` stores the anon inode, lock, current valid size, allocated size, backing pages, SG table, DMA SGL, and sequential lookup cache. File disable zeroes size and resets offsets; final release destroys lock and frees the wrapper.

Dependencies and integration: depends on VFIO migration arcs from `vfio_dev.c`, firmware commands from `cmds.c`, PDS admin data structures, anon inodes, highmem mapping, and scatterlist/DMA APIs.

Risks: restore writes increment `size` and must not exceed allocated state length. File lifetime uses an extra reference; release and driver cleanup must not double free. Sequential page lookup caching must reset correctly for backward offsets.

Test signals: save and restore FD creation, short reads/writes, disabled FD behavior, invalid offsets, migration arc coverage, suspend/resume command failures, restore command failure, and close/reset cleanup while FDs are open.
