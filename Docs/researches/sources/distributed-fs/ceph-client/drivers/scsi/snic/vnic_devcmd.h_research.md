# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_devcmd.h

Purpose: this header defines the vNIC device-command ABI used for firmware control operations and devcmd2 ring commands.

Important APIs, types, and functions: command encoding macros `_CMDC`, `_CMDCNW`, `_CMD_DIR`, `_CMD_FLAGS`, `_CMD_VTYPE`, and `_CMD_N` pack direction, flags, vNIC type, and command number. `enum vnic_devcmd_cmd` defines firmware info, device-specific config, stats, notify, open/status/close, init/status/deinit, enable/disable, capability, and devcmd2 initialization commands. Error/status enums define firmware command outcomes. Structures define firmware info, notify buffer, provision info, legacy devcmd registers, devcmd2 descriptors, devcmd2 results, and ring sizing constants.

Control flow: `vnic_dev.c` builds commands with this ABI and submits them through devcmd2. Config, stats, notify, lifecycle, and initialization operations all map to these command values and argument conventions.

State and persistence: ABI structures are DMA/MMIO runtime protocol state. Notify data contains link status, port speed, MTU, message level, uplink interface, status, error, and link-down count. No data is persisted by this header.

Dependencies and integration: consumed by `vnic_dev.c` and included by `vnic_dev.h`. It is generic to multiple vNIC types but SNIC uses `_CMD_VTYPE_SCSI`-capable commands through `_CMD_VTYPE_ALL`.

Risks: packed bit layout is protocol-critical. Error codes are firmware-specific and are returned directly by devcmd2. NOWAIT commands do not produce results, so callers must not expect readback. The original MMIO devcmd struct remains defined but SNIC initializes only devcmd2 in this driver.

Test signals: verify command numbers and direction flags against firmware, devcmd2 result error propagation, unsupported capability command behavior, notify buffer sizing, and lifecycle command fallback from `CMD_ENABLE_WAIT` to `CMD_ENABLE`.
