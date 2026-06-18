# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport.c

## Purpose
`adf_transport.c` implements the QAT ETR transport ring manager. It allocates coherent DMA rings, reserves ring slots inside banks, programs CSR ring base/config/head/tail registers, dispatches responses to service callbacks, initializes per-bank interrupt/coalescing state, and tears the transport down for a QAT acceleration device.

## Important APIs, Types, And Functions
The exported API is `adf_init_etr_data()`, `adf_cleanup_etr_data()`, `adf_create_ring()`, `adf_remove_ring()`, `adf_send_message()`, `adf_ring_nearly_full()`, and `adf_response_handler()`. Internal helpers include `adf_verify_ring_size()`, `adf_reserve_ring()`, `adf_init_ring()`, `adf_handle_response()`, `adf_init_bank()`, and `cleanup_bank()`. The file operates on `struct adf_etr_data`, `struct adf_etr_bank_data`, and `struct adf_etr_ring_data` from `adf_transport_internal.h`.

## Control Flow
`adf_init_etr_data()` allocates the transport root, allocates one bank structure per hardware bank, creates a `transport` debugfs directory, obtains the ETR CSR base, and initializes each bank. Bank initialization clears all ring CSRs, allocates ring metadata, shares the `inflights` counter between paired TX/RX rings using the device `tx_rx_gap`, chooses coalescing timers from config, installs debugfs, clears interrupt flags, and programs interrupt source selection.

`adf_create_ring()` validates bank, message size, configured ring number, and in-flight capacity, reserves the ring in the bank mask, fills ring metadata, allocates and initializes the DMA ring, enables hardware arbitration, creates debugfs, and optionally enables ring IRQs. `adf_send_message()` increments the shared in-flight counter, copies the firmware request into the ring tail slot, advances tail by message size modulo ring size, and writes the tail CSR. Responses are scanned until `ADF_RING_EMPTY_SIG`; each message calls the ring callback, decrements in-flight count, clears the slot, advances head, and finally writes the head CSR. `adf_response_handler()` processes non-empty IRQ-enabled rings and re-enables interrupt/coalescing flags. Removal disables IRQs and arbitration, clears CSRs, removes debugfs, unreserves the ring, and frees DMA memory.

## State And Persistence Behavior
All state is volatile kernel memory plus device CSRs. `accel_dev->transport` persists from transport init to cleanup. Banks persist with ring masks, IRQ masks, coalescing timers, CSR bases, debugfs dentries, and ring arrays. Rings persist with DMA base, DMA address, head/tail, thresholds, callback, lock, and shared in-flight counter. Ring contents are initialized and reset to `0x7f` so `ADF_RING_EMPTY_SIG` marks free response slots. There is no disk persistence.

## Dependencies And Integration Points
The file depends on hardware CSR operations from `GET_CSR_OPS()`, device-specific ring masks/gaps, `adf_cfg` configuration keys, debugfs helpers, DMA coherent allocation, QAT arbitration via `adf_update_ring_arb()`, and ISR/tasklet code that invokes `adf_response_handler()`. Crypto, compression, PKE, and admin clients create rings and submit 32/64/128-byte firmware requests through this layer.

## Risks
Ring sizing and alignment are hardware contracts; a wrong conversion can produce invalid modulo math or DMA base alignment failures. `atomic_t *inflights` is shared between TX/RX pairs, so incorrect `tx_rx_gap` or mask setup corrupts flow control. The response loop trusts callbacks and ring empty signatures; stale or malformed ring memory can stall processing. Error handling in bank cleanup is sensitive because allocated `inflights` exist only for TX rings. `adf_cleanup_etr_data()` also frees `etr_data->banks->rings` after per-bank cleanup has already freed each bank's rings, which is a notable double-free risk in this source snapshot.

## Test Signals
Useful signals are successful QAT probe, transport debugfs directories per bank/ring, valid ring head/tail movement, no DMA mapping/alignment errors, and successful crypto/compression request completions. Stress tests should cover full rings, backlog behavior, interrupt and polling modes, invalid config ring numbers, probe failure cleanup, repeated ring create/remove, and response handling under high concurrency.
