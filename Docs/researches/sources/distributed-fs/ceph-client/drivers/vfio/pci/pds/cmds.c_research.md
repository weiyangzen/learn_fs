# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/cmds.c

Purpose: implements PDS firmware/admin-queue commands used by the VFIO migration and dirty logging layers.

Important APIs: client registration/unregistration, `pds_vfio_suspend_device_cmd()`, `pds_vfio_resume_device_cmd()`, migration state size/save/restore commands, host VF migration status notification, dirty status/enable/disable, and dirty sequence/ack commands.

Control flow: commands are wrapped as `PDS_AQ_CMD_CLIENT_CMD` and sent through the PF `pdsc_adminq_post()` path using the registered client id. Suspend is two-phase: send suspend, then poll suspend-status with fast polling until completion or timeout. Migration save/restore maps the anonymous migration file scatterlist for DMA, builds a PDS SGL, issues SAVE or RESTORE, and unmaps afterward. Dirty tracking commands exchange region descriptors and sequence/ack SGLs with firmware.

State and persistence: persistent state is firmware-side; driver state includes `client_id`, DMA-mapped SGL addresses, and file/dirty-region metadata owned elsewhere. Command functions balance DMA mappings around each request.

Dependencies and integration: depends on PDS core interfaces, PF lookup through `pdsc_get_pf_struct()`, adminq command layouts, DMA APIs, `lm.c` migration files, and `dirty.c` region tracking.

Risks: failures in adminq, DMA mapping, or firmware status polling abort VFIO state transitions. The dirty-status path currently requires SEQ_ACK bitmap support. Correct endian conversion and SGL length reporting are essential.

Test signals: client registration lifetime, suspend timeout, adminq `-EAGAIN` polling, save/restore DMA mapping failures, dirty capability absence, dirty disable returning nonzero regions, and seq/ack read/write command errors.
