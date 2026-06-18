# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qla3xxx.h

## Purpose

`qla3xxx.h` is the hardware contract header for the legacy QLogic QLA3xxx NIC HBA driver. It defines the packed on-wire/on-DMA IOCB formats, memory-mapped register page layouts, EEPROM/NVRAM structure, queue sizing constants, DMA buffer control blocks, and the main `struct ql3_adapter` state container consumed by the qla3xxx implementation.

The file contains no executable functions. Its behavior is expressed through fixed binary layouts, register bit definitions, and driver state fields that other qla3xxx source files use to program the ASIC, post transmit and receive buffers, interpret completions, manage link state, and recover from resets.

## Important APIs, Types, And Constants

Core DMA/firmware command structures:

- `struct ob_mac_iocb_req`, `struct ob_mac_iocb_rsp`: outbound MAC transmit request/response descriptors. Important fields are `opcode`, flag bits for interrupt/checksum/continuation semantics, `transaction_id`, `data_len`, IP header offsets, and up to three DMA buffer address/length entries.
- `struct ib_mac_iocb_rsp`: inbound MAC receive response with packet length and inbound address list pointer.
- `struct ob_ip_iocb_req`, `struct ob_ip_iocb_rsp`, `struct ib_ip_iocb_rsp`: IP-oriented command/response formats, including checksum result bits for 3032 hardware.
- `struct net_rsp_iocb`: generic response descriptor used in the response queue.
- IOCB opcodes such as `OPCODE_OB_MAC_IOCB_FN0`, `OPCODE_OB_MAC_IOCB_FN2`, `OPCODE_IB_MAC_IOCB`, and `OPCODE_IB_IP_IOCB`.
- Buffer length flags such as `OB_MAC_IOCB_REQ_E`, `OB_MAC_IOCB_REQ_C`, `OB_IP_IOCB_REQ_E`, and `OB_IP_IOCB_REQ_C` indicate list termination and continuation/OAL chaining.

Register and hardware layout types:

- `struct ql3xxx_common_registers`: mailbox registers, flash/NVRAM access registers, control/status, interrupt mask, queue producer/consumer indexes, and MADI access.
- `struct ql3xxx_port_registers`: page 0 port-control page, including MAC/PHY management registers, IP registers, statistics selectors, fatal error status, local RAM access, and port status.
- `struct ql3xxx_host_memory_registers`: page 1 queue DMA configuration for request, completion, large RX, and small RX queues.
- `struct ql3xxx_local_ram_registers`: page 2 memory allocator and table sizing state for buflets, IP/TCP hash tables, NCB, and DRB tables.
- Bit-field enums define `ispControlStatus`, interrupt mask, semaphore ownership, external/internal hardware config, port control/status, MII management, MAC config, statistics selector indexes, and fatal error bits.

Persistent device configuration:

- `struct eeprom_port_cfg`, `struct eeprom_bios_cfg`, `struct eeprom_function_cfg`, and `struct eeprom_data` model the EEPROM/NVRAM contents, including MAC addresses, subsystem IDs, port configuration, buffer/table sizing, serial/board strings, and checksum.
- EEPROM command constants cover FM93C56/66/86 style serial EEPROM opcodes, address/data bit widths, and bit-banged Auburn serial interface signals.

Queue and DMA state:

- Queue sizing constants: `NUM_REQ_Q_ENTRIES`, `NUM_RSP_Q_ENTRIES`, `NUM_LBUFQ_ENTRIES`, `JUMBO_NUM_LBUFQ_ENTRIES`, `NUM_SBUFQ_ENTRIES`, and `NUM_SMALL_BUFFERS`.
- `struct lrg_buf_q_entry` and `struct bufq_addr_element` define receive buffer queue entries and DMA address elements.
- `struct ql_rcv_buf_cb` tracks one RX skb, DMA mapping, physical address split, and free-list link.
- `struct oal_entry`, `struct oal`, and `MAX_OAL_CNT` implement outbound address list chaining for fragmented TX skbs beyond the three inline IOCB SG slots.
- `struct ql_tx_buf_cb` keeps the skb, IOCB entry, OAL pointer, segment count, and DMA unmap metadata for a transmit request.
- `struct ql3_adapter` is the central runtime state: PCI/netdev/NAPI references, spinlocks, MMIO base and current register page, shadow registers, request/response queues, TX/RX software rings, EEPROM copy, link state, MAC/PHY parameters, workqueue and delayed reset/link/timeout work, frame sizing, and feature flags.

## Control Flow And State Behavior

This header shapes driver control flow through state fields and register contracts rather than code:

1. Probe/setup code maps BAR space into `mmap_virt_base`, assigns `mem_map_registers`, selects pages through `current_page`, reads `nvram_data`, and programs queue base addresses in `ql3xxx_host_memory_registers`.
2. TX code allocates a request queue entry, fills `struct ob_mac_iocb_req`, uses inline DMA slots and optional `struct oal` continuation entries, advances `req_producer_index`, and later uses `struct ql_tx_buf_cb` plus completion `transaction_id` to unmap and free the skb.
3. RX setup posts large and small buffer queues using `struct lrg_buf_q_entry`, `bufq_addr_element`, and `ql_rcv_buf_cb` pools. Completion processing interprets inbound IOCBs, returns buffers, and maintains producer indexes and release counters.
4. Link and reset work is coordinated by `qdev->flags` bits such as `QL_RESET_ACTIVE`, `QL_RESET_START`, `QL_LINK_MASTER`, `QL_ADAPTER_UP`, `QL_LINK_UP`, and allocation-done flags.
5. EEPROM, flash, PHY, DDR, and driver-global operations are serialized through hardware semaphore bit definitions in `semaphoreReg`.

Persistent state lives in EEPROM/NVRAM (`struct eeprom_data`) and in hardware register state. Runtime state in `struct ql3_adapter` is volatile and rebuilt during probe, reset, MTU changes, and queue reallocation.

## Dependencies And Integration Points

The header depends on Linux kernel networking and PCI types through users of this header: `struct pci_dev`, `struct net_device`, `struct napi_struct`, `struct sk_buff`, `struct timer_list`, `struct workqueue_struct`, `struct delayed_work`, DMA mapping metadata macros, spinlocks, and endian-tagged integer types.

Integration points include:

- Linux netdev TX/RX paths via skb-backed `ql_tx_buf_cb` and `ql_rcv_buf_cb`.
- PCI/MMIO accessors through register layout structs stored as `__iomem` pointers.
- DMA APIs through `dma_addr_t` and `DEFINE_DMA_UNMAP_ADDR/LEN`.
- NAPI receive polling via the `napi` member.
- Workqueue/timer reset and link maintenance through `reset_work`, `tx_timeout_work`, `link_state_work`, and `adapter_timer`.
- MII/PHY and EEPROM code via register constants and bit-banged serial interface definitions.

## Risks And Edge Cases

- Binary layout risk is high. The IOCB structs are `#pragma pack(1)` and EEPROM/descriptor structures use exact endian and bit-field assumptions. Any field movement changes hardware ABI.
- `MS_64BITS(x)` and `LS_64BITS(x)` split DMA addresses; misuse or truncation would corrupt queue/buffer programming.
- Queue sizes are power-of-two and page-size motivated. Changing constants can break ring wrapping or hardware expectations.
- EEPROM structures use C bit-fields and comments note endianness sensitivity. Cross-endian behavior must be validated carefully.
- OAL chaining depends on `MAX_SKB_FRAGS` and flags in length words. Incorrect last/continuation bits can produce DMA past the intended scatterlist.
- Reset and allocation flags in `qdev->flags` are positional enum values intended for bit operations. Renumbering or mixing with masks would corrupt state checks.
- Register-page structures assume MMIO layout and 32-bit register width. Adding padding or compiling with unexpected packing would be unsafe.

## Test Signals

Good validation signals for changes touching this header include:

- Successful build of the qla3xxx driver with sparse/endian warnings enabled.
- TX/RX traffic over normal MTU and jumbo MTU, including fragmented skb TX that exercises OAL chaining.
- RX buffer recycling under memory pressure and DMA mapping error injection if available.
- Link up/down and PHY auto-negotiation tests for both port/MAC indexes.
- EEPROM read/checksum and MAC address extraction tests.
- Reset, TX timeout, and adapter down/up cycles that confirm flags and queue allocation state transitions.
- Runtime DMA API debug and KASAN/KMSAN checks for descriptor or buffer lifetime mistakes.
