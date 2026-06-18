# sources/distributed-fs/ceph-client/drivers/bluetooth/btintel_pcie.h

## Purpose
Defines the Intel Bluetooth PCIe hardware ABI and driver-private state used by `btintel_pcie.c`: CSR offsets and bit definitions, MSI-X cause values, power states, DMA ring sizes, context-info layout, TX/RX descriptors, RFH receive header, debug buffer metadata, dump metadata, and MMIO helper accessors.

## Important APIs, Types, And Functions
- Register definitions cover function control, hardware revision, RF ID, boot stage, IPC control/status/sleep, context-info DMA addresses, image response, mailboxes, MSI-X cause/mask/IVAR registers, debug registers, and peripheral memory access registers.
- Boot-stage and function-control bits model MAC/function init, bus-master disconnect, software reset, ROM/IML/OPFW stages, lockdown, warning, abort, halted, alive, and D3-ready status.
- Packed firmware ABI structs include `struct ctx_info`, `struct tfd`, `struct urbd0`, `struct frbd`, `struct urbd1`, and `struct rfh_hdr`.
- Driver state structs include `struct data_buf`, `struct ia`, `struct txq`, `struct rxq`, `struct btintel_pcie_dbgc`, `struct btintel_pcie_dump_header`, and `struct btintel_pcie_data`.
- Inline helpers wrap MMIO and peripheral memory operations: `btintel_pcie_rd_reg32`, `btintel_pcie_wr_reg8`, `btintel_pcie_wr_reg32`, `btintel_pcie_set_reg_bits`, `btintel_pcie_clr_reg_bits`, and `btintel_pcie_rd_dev_mem`.

## Control Flow
The header is declarative, but its structures prescribe the transport flow. Probe allocates one aligned DMA block and maps it into the fields described by `ctx_info`: index arrays, TX descriptors, RX descriptors, completion rings, doorbell vectors, MSI-X vectors, and DBGC fragment location. Runtime TX and RX update the index-array pointers in `struct ia` while the device consumes the descriptor queues defined here. Power management writes the sleep-control states declared in this header and interprets boot-stage bits to decide D0/D3/error/lockdown state.

## State And Persistence
`struct btintel_pcie_data` is the persistent per-device container. It stores hardware resource ownership, runtime synchronization primitives, cached registers, DMA resources, queue state, firmware alive context, coredump buffers, and PM state. The descriptor and context structs are persistent while the device is bound because firmware reads them by DMA address. `btintel_pcie_dump_header` persists metadata collected during setup and used later in firmware assert or user-triggered dumps.

## Dependencies And Integration Points
The header integrates with Linux PCI/MSI-X types, DMA addresses and pools, wait queues, workqueues, skb queues, Bluetooth HCI devices, and Intel common constants from `btintel.h`. The packed layouts must match the PCIe firmware contract; `btintel_pcie.c` writes the addresses into CSR registers and rings doorbells using the constants here.

## Risks And Edge Cases
Register or bit definition drift breaks hardware bring-up, interrupt routing, and PM transitions. Packed bitfields in descriptors and RFH headers are compiler-layout-sensitive but match the in-tree driver contract; changes require firmware ABI awareness. The comment spelling issues do not affect behavior, but the field semantics must remain exact because firmware treats many context fields as read-only host-provided configuration. Alignment constants and descriptor counts must match allocation and queue wrap logic in the C file.

## Test Signals
Build and runtime validation should confirm `sizeof(struct ctx_info)` and descriptor layouts expected by firmware, 128-byte alignment of the shared DMA block, correct CSR writes for context-info LSB/MSB and doorbells, valid boot-stage bit interpretation for ROM/IML/OP/D3/error states, and DBGC fragment content visible to firmware.
