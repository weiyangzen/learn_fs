# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni-cmd.h

Purpose: Defines the MC command ABI for DPAA2 Data Path Network Interface objects. It maps high-level DPNI operations to command IDs, command versions, compact bitfields, and little-endian command/response structs consumed by `dpni.c`.

Important APIs, types, and functions: Version and ID helpers include `DPNI_VER_MAJOR`, `DPNI_VER_MINOR`, `DPNI_CMD()`, `DPNI_CMD_V2()`, and `DPNI_CMD_V3()`. Command IDs cover object lifecycle, enable/reset, IRQs, pools, error behavior, QDID/data offsets, link/frame length, promiscuous/MAC/VLAN filters, distribution, QoS/FS rules, statistics, queues, taildrop, buffer layout, congestion notification, offloads, link config, and single-step PTP. Bitfield helpers are `DPNI_MASK()`, `dpni_set_field()`, and `dpni_get_field()`. Structs define every command and response payload, including the external 256-byte RX distribution key extension (`dpni_ext_set_rx_tc_dist`).

Control flow: No direct execution. `dpni.c` writes these layouts into `struct fsl_mc_command.params`, sets command headers and tokens, calls `mc_send_command()`, and decodes response payloads using these structs and bitfield macros.

State and persistence behavior: The header defines transient command wire formats only. Persistent hardware/firmware state is affected by the commands sent by callers, such as queues, filters, distribution, taildrop, congestion, shaping, offloads, and PTP configuration.

Dependencies and integration points: Includes `dpni.h` for shared public enums and limits, which makes it tightly coupled to the public DPNI type definitions. It is private to the DPNI command wrapper implementation and must track MC firmware ABI exactly.

Risks: This file is almost entirely ABI-sensitive. Command-version mismatches are particularly important: `SET_POOLS` uses V3, `ADD_VLAN_ID` and `SET_TX_SHAPING` use V2, and `GET_SINGLE_STEP_CFG` uses V2. Reused bitfield names such as `DPNI_DEST_TYPE_*` appear for multiple structs with compatible shifts; future divergent layouts would need separate names. `dpni_set_field()` ORs into the destination, so callers need zeroed command buffers or explicit clearing. MAC address payloads are stored reversed by `dpni.c`, so command structs must not be interpreted as normal byte order. The key-extension struct size/ordering must fit the 256-byte DMA buffer expected by MC.

Test signals: ABI smoke tests for each wrapper in `dpni.c`, command version compatibility against target firmware, IRQ get/mask/clear, pool association including backup mask and qdbin mode, queue get/set round-trip, MAC add/remove byte ordering, VLAN filter/action commands, RSS/FS/QoS key extension serialization, congestion/taildrop threshold programming, offload get/set, single-step PTP flags, and static checks for struct sizes if the MC ABI changes.
