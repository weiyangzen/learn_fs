# sources/distributed-fs/ceph-client/drivers/scsi/isci/scu_remote_node_context.h

Purpose: defines the SCU hardware SRAM layout for remote node contexts. The driver writes these structures before posting RNC commands so the controller can open connections to SAS/STP targets.

Important APIs/types: `struct ssp_remote_node_context` is the real layout used by current code. It contains the RNI, remote port width, logical port, nexus-loss timer enable, validity and context-type bits, remote SAS address low/high words, function number, arbitration wait fields, occupancy and inactivity timeouts, open-address-frame connection rate/features/source-zone/more-compatibility fields, and reserved words. `struct stp_remote_node_context` is a placeholder `u32 data[8]`. `union scu_remote_node_context` overlays SSP and STP formats.

Control flow: `remote_node_context.c` obtains the union entry from `ihost->remote_node_context_table`, zeroes one or more entries, fills the SSP view for both SAS and SATA devices, sets `is_valid` on post, clears it on invalidate, and posts 32-byte or 96-byte RNC commands depending on device type/topology. SAS address conversion is handled before writing the high/low fields.

State and persistence behavior: this header models hardware-visible persistent context RAM for the lifetime of an active remote device. The `is_valid` bit is the transition boundary between a staged context and one the SCU may consume. Timeout and OAF fields persist until the RNC is invalidated or rebuilt.

Dependencies/integration: consumed by host context-table storage and RNC construction. Values are coordinated with `scu_task_context.h` context commands and remote-node table allocation. Device parameters come from libsas domain devices and host user parameters.

Risks: C bitfield layout is compiler- and endian-sensitive, but this driver relies on it matching the SCU dword format. The STP structure is a placeholder while code still writes the SSP view for SATA-style devices, so future STP-specific fields would need coordinated changes. Incorrect `is_valid`, SAS address endianness, or port index fields can make every request fail with open reject or invalid RNC. Test signals include raw context dword inspection for SAS and SATA devices, post/invalidate bit toggling, direct versus expander SATA 32/96-byte posting, and timeout parameter propagation.
