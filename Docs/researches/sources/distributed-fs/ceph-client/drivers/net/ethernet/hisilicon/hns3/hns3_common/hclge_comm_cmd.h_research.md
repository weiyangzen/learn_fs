# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_cmd.h

## Purpose

`hclge_comm_cmd.h` defines the shared command queue ABI between HNS3 driver code and firmware. It contains command descriptor flags, command queue register offsets, reset and timeout constants, the complete firmware opcode enum used by common/PF/VF code, firmware return status enums, firmware capability bit definitions, descriptor/ring/control structures, MMIO helpers, and public command queue APIs implemented in `hclge_comm_cmd.c`.

## Important APIs and Types

- Descriptor flags include `HCLGE_COMM_CMD_FLAG_IN`, `NEXT`, `WR`, and `NO_INTR`; `HCLGE_COMM_SEND_SYNC()` treats `NO_INTR` as synchronous polling mode.
- Register constants cover CSQ/CRQ base, depth, head, tail, vector0 command event registers, interrupt registers, and reset-ready bits.
- `enum hclge_opcode_type` is the firmware command namespace for generic, stats, DFX/register, MAC, PTP, pause/PFC, scheduler, buffer, TQP, TSO/GRO, RSS, promiscuous, VLAN, interrupts, flow director, mailbox, LED, PHY, WOL, RAS, and diagnostics commands.
- `enum hclge_comm_cmd_return_status` maps firmware descriptor return values before conversion to Linux errors.
- `enum HCLGE_COMM_CAP_BITS` and `enum HCLGE_COMM_API_CAP_BITS` define firmware-advertised feature bits.
- `struct hclge_desc` is the firmware command descriptor: opcode, flags, retval, reserved field, and six 32-bit data words.
- `struct hclge_comm_cmq_ring`, `struct hclge_comm_cmq`, and `struct hclge_comm_hw` model command queue DMA rings, queue state, trace hooks, and MMIO bases.
- Public APIs include descriptor setup/reuse, queue allocation/free/init/uninit, command send, firmware compatibility config, version/capability query, register init, and trace op installation.

## Control Flow and Integration

The header has no runtime flow by itself, but every command user constructs one or more `struct hclge_desc` values with an opcode from `enum hclge_opcode_type`, marks it read or write with the descriptor flags, and calls `hclge_comm_cmd_send()`. RSS and TQP stats in this subset use `HCLGE_OPC_RSS_*` and `HCLGE_OPC_QUERY_*_STATS`; other HNS3 modules use the rest of the opcode space.

## State and Persistence Behavior

The structures describe in-memory driver and DMA state. `struct hclge_comm_hw` persists for the lifetime of the PF/VF hardware object and owns command queue state. Descriptor memory is coherent DMA memory allocated during queue init and freed during queue uninit. `last_status` preserves the most recent firmware command status for diagnostics. No state is persisted outside the driver.

## Dependencies

The header includes Linux types and `hnae3.h` for device structures, capability bit definitions, and bitfield helpers. It assumes Linux PCI DMA/MMIO infrastructure in implementation files. Firmware ABI compatibility is critical because opcodes, descriptor layout, return codes, and capability bits must match firmware definitions.

## Risks and Edge Cases

- Opcode enum values are firmware ABI and must not drift.
- `HCLGE_COMM_SEND_SYNC()` is based on the `NO_INTR` bit, so descriptor flag misuse changes completion behavior.
- `HCLGE_DESC_DATA_LEN` fixes command payload to six words; command-specific structs cast over `desc.data` must fit.
- Capability bit mappings use firmware bit positions that are not contiguous and contain version-specific gaps.
- Register offsets and descriptor ring depth are hardware-specific; incorrect values can break probe or hang command submission.

## Test Signals

Validation should include compile coverage for all command users, static layout checks where available, successful admin command traffic on PF and VF devices, firmware error conversion checks, feature-gated behavior matching advertised capabilities, and RSS/TQP command users producing correct descriptors with the expected opcodes and flags.
