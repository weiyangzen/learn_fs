# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_debugfs.h

## Purpose

`hclge_debugfs.h` defines PF debug command support types and constants shared by `hclge_debugfs.c` and error logging. It describes management-table decoding masks, DFX BD-number offsets, compact firmware response layouts, formatting lengths, and the exported helper for indexed debug command reads.

## Important Types And Constants

Management table masks decode VLAN, MAC, EtherType, egress type, PF/VF ID, queue, and drop fields. DFX offsets identify firmware-reported BD counts for BIOS, SSU, IGU, RPU, NCSI, RTC, PPP, RCB, TQP, and SSU_2 register groups. `struct hclge_qos_pri_map_cmd` models packed 4-bit priority-to-TC fields. `struct hclge_dbg_bitmap_cmd` provides byte and bitfield views for status bytes. `struct hclge_dbg_reg_common_msg`, `hclge_dbg_tcam_msg`, `hclge_dbg_dfx_message`, `hclge_dbg_reg_type_info`, and `hclge_dbg_func` drive table-based debug dispatch and register printing. `struct hclge_dbg_vlan_cfg` is a normalized aggregate of VLAN TX/RX offload state.

The declared API is `hclge_dbg_cmd_send(struct hclge_dev *hdev, struct hclge_desc *desc_src, int index, int bd_num, enum hclge_opcode_type cmd)`.

## Control Flow And State

The header has no runtime state. Its structures shape how `hclge_debugfs.c` builds descriptor chains, labels DFX outputs, picks read callbacks, and formats debug information into buffers or `seq_file` output.

## Dependencies And Integration Points

It includes `linux/etherdevice.h` and `hclge_cmd.h`, so it inherits the command descriptor ABI. `hclge_err.h` includes this header because error logging reuses debug command helpers for module register dumps.

## Risks

The bitfield layout in `hclge_qos_pri_map_cmd` and `hclge_dbg_bitmap_cmd` is compact but compiler-layout-sensitive, so it should stay aligned with how firmware returns byte-oriented fields on supported architectures. Formatting length constants must be large enough for all strings in the static tables. DFX offset constants must match firmware query order or debug register dumps will request the wrong BD counts.

## Test Signals

Compile with sparse and multiple compiler versions, exercise QoS priority map, DFX register, VLAN, and error-module debug paths, and compare printed field names/counts with firmware documentation.
