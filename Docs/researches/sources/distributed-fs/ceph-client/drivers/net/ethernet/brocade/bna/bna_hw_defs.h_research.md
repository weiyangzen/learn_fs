# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_hw_defs.h

## Purpose
`bna_hw_defs.h` defines BNA driver-side hardware constants, interrupt helper macros, doorbell encodings, queue descriptor structures, and CT/CT2 register/bit initialization macros. It bridges the raw register map in `bfi_reg.h` to the runtime `struct bna` register and bit-mask fields used by interrupt and queue code.

## Important APIs, Types, and Functions
- Resource defaults and limits: default TXQ/RXP/UCAM/RIT sizes, max MCAM, invalid RID, VLAN block constants, coalescing defaults, WI sizes, TX vector/data limits, small RX buffer size, and max priority.
- Register setup macros: `ct_reg_addr_init()`, `ct_bit_defn_init()`, `ct2_reg_addr_init()`, `ct2_bit_defn_init()`, and `bna_reg_addr_init()`.
- Interrupt classification and control: `BNA_IS_MBOX_INTR()`, `BNA_IS_HALT_INTR()`, `BNA_IS_ERR_INTR()`, `BNA_IS_MBOX_ERR_INTR()`, `BNA_IS_INTX_DATA_INTR()`, `bna_halt_clear()`, `bna_intx_disable()`, `bna_intx_enable()`, `bna_mbox_intr_disable()`, `bna_mbox_intr_enable()`, and `bna_intr_status_get()`.
- Doorbell helpers: `BNA_DOORBELL_Q_PRD_IDX()`, `BNA_DOORBELL_Q_STOP`, `BNA_DOORBELL_IB_INT_ACK()`, `bna_ib_start()`, `bna_ib_stop()`, `bna_txq_prod_indx_doorbell()`, and `bna_rxq_prod_indx_doorbell()`.
- Data structures: `bna_reg_offset`, `bna_bit_defn`, `bna_reg`, `bna_dma_addr`, `bna_txq_entry`, `bna_rxq_entry`, and `bna_cq_entry`.

## Control Flow and State
During `bna_init()`, `bna_reg_addr_init()` selects CT or CT2 based on PCI device ID and stores the correct interrupt status/mask addresses plus mailbox/error/halt bit masks. Interrupt paths use `bna_intr_status_get()` to read and clear non-mailbox interrupt status, then classify mailbox and error conditions. Mailbox interrupts can be masked/unmasked around IOC lifecycle transitions. Data-path queues ring producer-index doorbells with encoded values, and interrupt blocks are started/stopped by programming coalescing/ack/disable doorbell values.

## State and Persistence Behavior
The macros manipulate MMIO interrupt mask/status registers, IOC halt bits, IB doorbells, and queue doorbells. Driver state includes `struct bna_reg` and `struct bna_bit_defn` fields initialized from the device generation. Descriptor structs define DMA-visible queue entries consumed by hardware.

## Dependencies and Integration Points
The header includes `bfi_reg.h` for raw offsets and bit masks. It is included through `bna.h`/types by BNA core and datapath modules. It mirrors some descriptor constants from `bfi_enet.h`; both must stay ABI-compatible with firmware/hardware expectations.

## Risks
- Macro bodies evaluate arguments directly and may have side effects if passed complex expressions.
- Interrupt clear logic preserves mailbox bits while clearing other status; wrong masks can lose interrupts or leave interrupt storms.
- `bna_ib_ack()` ORs event counts into a cached doorbell value and relies on `BNA_IB_MAX_ACK_EVENTS` discipline elsewhere to avoid 16-bit overflow.
- CT/CT2 device ID selection lacks a default case; unsupported IDs leave register fields uninitialized.
- Descriptor structs require explicit endian handling by users.

## Test Signals
Signals include correct register initialization for CT and CT2 devices, mailbox interrupt masking/unmasking during IOC enable/disable, halt interrupt clear behavior, INTx data interrupt classification, IB start/stop with expected interrupt state, TX/RX producer doorbells advancing hardware queues, and descriptor layout compatibility with firmware completions.
