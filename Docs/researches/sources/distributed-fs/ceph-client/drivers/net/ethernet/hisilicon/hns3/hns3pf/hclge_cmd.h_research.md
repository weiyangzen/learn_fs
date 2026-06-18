# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_cmd.h

## Purpose

`hclge_cmd.h` is the PF-side firmware command ABI header for the HNS3 `hclge` Ethernet driver. It does not implement command submission itself, but it defines the descriptor payload layouts, bit positions, limits, and helper aliases used by `hclge_main.c`, traffic management, DCB, debugfs, devlink-adjacent feature queries, and error handling. The common command transport is delegated to `hclge_comm_cmd.h`, with `hclge_cmd_setup_basic_desc()` mapped to the common helper and `hclge_cmd_send()` declared for PF command submission.

## Important APIs, Types, And Constants

The header declares `int hclge_cmd_send(struct hclge_hw *hw, struct hclge_desc *desc, int num)` and a large set of command payload structs. Key groups include queue and interrupt mapping (`hclge_tqp_map_cmd`, `hclge_ctrl_vector_chain_cmd`, `hclge_misc_vector`), packet buffer and waterline configuration (`hclge_tx_buff_alloc_cmd`, `hclge_rx_priv_buff_cmd`, `hclge_pkt_buf_alloc`, `hclge_rx_com_wl_buf_cmd`, `hclge_rx_pkt_buf_cmd`), PF/VF resource discovery (`hclge_func_status_cmd`, `hclge_pf_res_cmd`, `hclge_cfg_param_cmd`, `hclge_vf_num_cmd`), RSS and link status masks, MAC mode/speed/FEC/SFP structures, MAC/VLAN table commands, VLAN filter/offload commands, TSO/GRO and reset payloads, loopback and LED commands, Flow Director TCAM/action/counter payloads, SFP EEPROM multi-BD layout, device specs, PHY settings, and Wake-on-LAN commands.

Most multi-byte fields use `__le16`, `__le32`, or `__le64`, making the file part of the hardware ABI rather than a host-native in-memory contract. Many `*_B`, `*_S`, and `*_M` constants encode bit indices, shifts, and masks consumed through `hnae3_get_bit()`, `hnae3_get_field()`, `hnae3_set_bit()`, and similar helpers.

## Control Flow And Integration

The typical caller flow is: allocate or stack-create one or more `struct hclge_desc`, call `hclge_cmd_setup_basic_desc(desc, opcode, is_read)`, cast `desc.data` to one of these request/response structs, fill fields using CPU-to-little-endian conversions, optionally set `HCLGE_COMM_CMD_FLAG_NEXT` across a descriptor chain, and call `hclge_cmd_send()`. Read paths reverse the process with little-endian conversions after firmware updates descriptor data.

This header is included by `hclge_main.h`, `hclge_debugfs.h`, `hclge_regs.c`, PTP code, and error/debug paths. Debugfs and error handlers depend heavily on these layouts for register dumps, VLAN diagnostics, Flow Director inspection, and MAC tunnel interrupt handling.

## State And Persistence Behavior

The file itself has no persistent state. It defines the exact payloads used to move state between driver memory, firmware command queues, and hardware. Persistent driver effects occur in callers when firmware accepts configuration commands: queue maps, VLAN rules, MAC modes, traffic buffers, FEC modes, reset state, Flow Director rules, and WOL settings can survive beyond a single function call until reset or reconfiguration.

## Dependencies

Dependencies are Linux kernel base types, MMIO annotations, Ethernet helpers, `hnae3.h`, and the shared HNS3 command layer in `hclge_comm_cmd.h`. Correctness also depends on firmware opcode definitions and descriptor data size from the common command header.

## Risks

The highest risk is ABI drift: changing structure layout, field order, reserved padding, endian annotations, or bit constants can silently corrupt firmware commands. Several structures assume descriptor payload size constraints, so additions must account for the 24-byte descriptor data area and multi-BD chains. Bitfield use in `hclge_qos_pri_map_cmd` lives in `hclge_debugfs.h`, but this header also exposes many byte-level flags where host endianness and hardware documentation must be kept aligned. Command structs with `#pragma pack(1)` around `hclge_mac_ethertype_idx_rd_cmd` require special care because packing state can affect later definitions if not restored.

## Test Signals

Useful signals include successful driver probe and reset, `ethtool` link/FEC/WOL operations, VLAN add/delete and offload behavior, RSS and queue mapping validation, DCB/mqprio reconfiguration, Flow Director rule insertion and counter reads, SFP EEPROM reads, and debugfs register dumps that use the same payloads. Kernel sparse/endian checks are important because the header relies on explicit little-endian fields.
