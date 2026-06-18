<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.c

Purpose: Management Complex command wrapper for DPAA2 Data Path SEC Interface objects. It opens/closes DPSECI sessions, enables/disables/resets objects, reads attributes, configures queues and congestion notification, and retrieves SEC accelerator capabilities.

Important APIs and control flow: each function allocates `struct fsl_mc_command`, encodes a command header with `mc_encode_cmd_header()`, fills little-endian command parameters from `dpseci_cmd.h`, sends via `mc_send_command()`, and decodes response fields. `dpseci_open()` returns an MC token for later calls. Queue functions set/read destination, priority, user context, order-preservation, and FQID fields. Attribute calls decode DPSECI object queues/options, SEC hardware accelerator counts, and API version. Congestion calls translate destination type/unit bitfields and threshold/message fields.

State and persistence behavior: no driver-owned persistent state; state lives in the MC object identified by token and in the caller's structs. The token returned by open is the session capability required for subsequent commands.

Dependencies and integration points: depends on `linux/fsl/mc.h`, command IDs/layouts from `dpseci_cmd.h`, public structs from `dpseci.h`, and DPAA2 CAAM code that manages DPSECI devices.

Risks and test signals: risks include strict ABI dependence on MC firmware command versions, endian/layout mistakes, unvalidated queue indices, and callers needing to close tokens on all paths. Test signals include API version 5.3 compatibility, successful open/enable/disable/reset, queue FQID retrieval matching DPL configuration, SEC capability fields matching hardware, and congestion notification round-trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.c -->
