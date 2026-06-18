<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.c

Purpose: Wraps PDS admin queue commands used by the vDPA driver to initialize/reset hardware, update status and attributes, and initialize/reset individual virtqueues.

Important APIs/functions: `pds_vdpa_init_hw()`, `pds_vdpa_cmd_reset()`, `pds_vdpa_cmd_set_status()`, `pds_vdpa_cmd_set_mac()`, `pds_vdpa_cmd_set_max_vq_pairs()`, `pds_vdpa_cmd_init_vq()`, and `pds_vdpa_cmd_reset_vq()` all build `union pds_core_adminq_cmd` requests and call `pds_client_adminq_cmd()`.

Control flow: Each wrapper fills opcode, vDPA index, VF ID, and command-specific payload. VQ init sends queue length as `ilog2(q_len)`, ring addresses, interrupt index, and avail/used indexes with packed-ring invert handling applied by the caller. VQ reset asks firmware to stop/reset the queue, then copies returned avail/used indexes back into software state after undoing the invert mask.

State and persistence: Commands mutate firmware-managed VF/vDPA state. Software state is mostly read-only input except `pds_vdpa_cmd_reset_vq()`, which updates `vq_info->avail_idx` and `vq_info->used_idx`.

Dependencies and integration points: Depends on PDS adminq definitions from `linux/pds/*`, `struct pds_vdpa_device`, and `struct pds_vdpa_vq_info`. Called by `vdpa_dev.c` during `dev_add`, status changes, reset, queue ready transitions, and MAC/max-queue configuration.

Risks: Queue length must be a valid power-of-two-like value for `ilog2` encoding to match firmware expectations. Adminq errors are logged at debug level in wrappers and often escalated by callers. Endianness conversion is explicit and must match firmware ABI. Incorrect invert handling breaks packed-ring migration indices.

Test signals: Adminq traces should show IDENT/INIT/RESET/STATUS/SET_ATTR/VQ_INIT/VQ_RESET commands. Test queue ready toggles, reset index recovery, MAC provisioning, max queue pair changes, and firmware error status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.c -->
