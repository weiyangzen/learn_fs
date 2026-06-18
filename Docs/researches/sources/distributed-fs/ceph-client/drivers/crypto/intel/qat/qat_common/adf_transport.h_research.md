# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport.h

## Purpose
`adf_transport.h` is the public transport ring interface for QAT common code. It hides the internal ETR ring layout and exposes ring creation, message submission, flow-control checks, and ring removal to crypto, compression, and administrative users.

## Important APIs, Types, And Functions
The file forward-declares `struct adf_etr_ring_data`, defines `adf_callback_fn` as the response callback type, and declares `adf_create_ring()`, `adf_ring_nearly_full()`, `adf_send_message()`, and `adf_remove_ring()`. `adf_create_ring()` binds an accelerator, config section, bank, message count, message size, ring-name config key, callback, polling mode, and output ring pointer.

## Control Flow
The header has no executable control flow. It defines the contract consumed by service code: create a ring after transport initialization, submit firmware request messages with `adf_send_message()`, optionally use `adf_ring_nearly_full()` for backlog decisions, and remove the ring during service/device teardown.

## State And Persistence Behavior
The header exposes opaque ring state only by pointer. Ring lifetime and DMA resources are owned by `adf_transport.c`; clients persist only the returned pointer while the accelerator device and service are active.

## Dependencies And Integration Points
It includes `adf_accel_devices.h` and is used by `qat_algs_send.c`, VF/PF service setup, and QAT service code that needs TX/RX transport rings. The callback type integrates hardware response delivery with service-specific completion handlers such as symmetric, asymmetric, and compression callbacks.

## Risks
The API does not encode ownership or lifetime in types, so callers must not use a ring after service/device removal. `adf_send_message()` accepts a raw `u32 *` and assumes the message size matches the ring's configured firmware request width. Callback implementations must be safe in bottom-half/response context.

## Test Signals
Compile coverage should catch missing declarations. Runtime validation comes from service ring creation, correct `-EAGAIN`/`-ENOSPC` propagation through submit helpers, and callback delivery for each QAT service.
