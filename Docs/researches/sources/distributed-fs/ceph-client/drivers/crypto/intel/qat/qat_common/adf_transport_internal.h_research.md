# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_internal.h

## Purpose
`adf_transport_internal.h` defines the private ETR transport structures shared by transport implementation, debugfs, and ISR code. It is the concrete layout behind the opaque `adf_etr_ring_data` public pointer.

## Important APIs, Types, And Functions
`struct adf_etr_ring_data` stores coherent ring base, shared in-flight counter, callback, parent bank, DMA address, optional debug entry, spinlock, head/tail, threshold, ring number, ring size encoding, and message size encoding. `struct adf_etr_bank_data` stores ring array, response tasklet, CSR base, coalescing timer, bank number, ring/IRQ masks, lock, accelerator pointer, and debugfs dentries. `struct adf_etr_data` stores all banks and the transport debugfs root. It declares `adf_response_handler()` and debugfs add/remove functions with no-op stubs when debugfs is disabled.

## Control Flow
The header has no runtime control flow but defines lifecycle ownership. Transport init allocates `adf_etr_data`, banks, and ring arrays; create-ring fills individual ring records; ISR code schedules bank response handlers; debugfs code inspects the same structures; cleanup frees and clears them.

## State And Persistence Behavior
The structures are volatile per-device transport state. Ring head/tail are software mirrors of CSR positions. `inflights` persists for a TX/RX pair and is decremented in response handling. `ring_mask` and `irq_mask` are protected by bank lock and define reserved and interrupt-enabled rings.

## Dependencies And Integration Points
The header includes interrupt/tasklet and spinlock types plus the public transport header. It integrates transport with `adf_vf_isr.c`, PF/MSI-X ISR code outside this subset, and all QAT service users that keep ring pointers.

## Risks
Concurrency depends on using the correct lock: bank masks use the bank lock and ring head/tail use the ring lock in send paths, while response paths update head without the ring send lock. Structure layout is used by debugfs and cleanup, so ownership mistakes can leak or double-free ring debug entries, `inflights`, or ring arrays.

## Test Signals
Build coverage validates debugfs stub selection. Runtime stress of create/remove, interrupt response, and debugfs reads validates structure lifetime and lock coverage.
