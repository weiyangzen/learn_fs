# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_nic.h

Purpose: Declares NIC data/control packet structures and inline command builders for LiquidIO host-to-firmware network operations.

Important APIs, types, and functions: `struct octnic_ctrl_pkt` carries firmware control command, optional data/response buffers, UDD words, IQ selection, originating netdev, callback, and status. `struct octnic_data_pkt` carries host buffer cleanup type, byte count, prepared instruction, and IQ. `union octnic_cmd_setup` captures IQ, gather flag, timestamp flag, checksum offload bits, and data/gather count. `octnet_iq_is_full()` reports IQ pressure. `octnet_prepare_pci_cmd_o2()` and `_o3()` build CN6XXX and CN23XX data instructions, respectively, setting front-size, tag, group/QPG, raw/gather bits, data length, opcode/subcode, and packet parameter OSSP. `octnet_prepare_pci_cmd()` selects layout by chip.

Control flow: TX paths fill `octnic_cmd_setup`, call the prepare helper, then submit with `octnet_send_nic_data_pkt()`. Control paths use `octnet_send_nic_ctrl_pkt()` and soft-command response support.

State and persistence: The header builds transient command descriptors and inspects live IQ occupancy. It defines no durable state.

Dependencies and integration: Depends on LiquidIO firmware command formats in `liquidio_common.h`, `octeon_iq.h`, and queue metadata in `octeon_device`. It bridges netdev TX features to firmware instruction fields.

Risks: Incorrect chip detection or bitfield packing breaks packet delivery. Gather count vs data length must be correct. Timestamp and checksum flags are passed to firmware in `packet_params`, so feature negotiation must be consistent.

Test signals: Generated command fields for CN6XXX and CN23XX, scatter-gather vs linear packets, checksum/tunnel/timestamp flags, queue full threshold, and control command callback/status propagation.
