# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc-cmd.h

Purpose: Defines the Management Complex command ABI for DPAA2 Data Path Real Time Counter objects. It is not a driver by itself; it is the private command layout consumed by `dprtc.c` when sending MC portal commands.

Important APIs, types, and constants: `DPRTC_CMD()` and `DPRTC_CMD_V2()` encode command IDs with base or v2 command versions. The command IDs cover open/close plus IRQ enable, mask, status, and clear operations. Packed structures such as `dprtc_cmd_open`, `dprtc_cmd_set_irq_enable`, `dprtc_cmd_set_irq_mask`, `dprtc_cmd_get_irq_status`, and response structures define exact little-endian payload layout for `struct fsl_mc_command.params`.

Control flow and state: The header contains no executable flow and no persistent state. Runtime state lives in MC firmware and is addressed by DPRTC object ID, token, IRQ index, event mask, and W1C status bits passed in these payloads.

Dependencies and integration points: Depends on kernel fixed-width little-endian types and on `linux/fsl/mc.h` conventions through its consumers. The `#pragma pack(push, 1)` section is an integration contract with the MC firmware ABI; field order, sizes, and endianness must match firmware exactly.

Risks: ABI drift is the main risk. `DPRTC_CMDID_SET_IRQ_MASK` uses command version 2 while related getters use base version, so changing versions without firmware coordination can break interrupt control. Missing endian conversion in consumers would corrupt object IDs, masks, or status.

Test signals: Useful signals are successful `dprtc_open()` token retrieval, IRQ enable/mask round trips, PPS/ETS event delivery, and sparse/build coverage that catches packed-structure or endian type misuse.
