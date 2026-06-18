# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_access_macros.h

## Purpose
`adf_transport_access_macros.h` centralizes constants and conversion macros for QAT ETR ring configuration. It translates compact hardware ring/message-size encodings into byte counts, builds ring config CSR values, defines watermarks and coalescing limits, and computes the maximum number of in-flight requests.

## Important APIs, Types, And Functions
Important constants include ring size encodings from `ADF_RING_SIZE_128` to `ADF_RING_SIZE_4M`, message sizes `ADF_MSG_SIZE_32/64/128`, `ADF_RING_EMPTY_SIG`, coalescing min/default/max values, and near-full/near-empty watermark values. Key macros are `ADF_MSG_SIZE_TO_BYTES()`, `ADF_BYTES_TO_MSG_SIZE()`, `ADF_SIZE_TO_RING_SIZE_IN_BYTES()`, `ADF_RING_SIZE_BYTES_MIN()`, `ADF_RING_SIZE_MODULO()`, `ADF_SIZE_TO_POW()`, `ADF_MAX_INFLIGHTS()`, `BUILD_RING_CONFIG()`, and `BUILD_RESP_RING_CONFIG()`.

## Control Flow
The file is macro-only. `adf_transport.c` uses the conversions when validating create-ring parameters, allocating DMA ring memory, moving head/tail pointers, building CSR config words, and computing near-full thresholds.

## State And Persistence Behavior
No runtime state is owned here. The constants define how transport code interprets ring metadata fields stored in `struct adf_etr_ring_data` and programmed into hardware CSRs.

## Dependencies And Integration Points
It includes `adf_accel_devices.h` and is tightly coupled to CSR operations and firmware request sizing. ISR, debugfs, and send paths all rely on the same byte/encoding conversions to agree on ring offsets.

## Risks
These macros are hardware contract code; off-by-one, endian, or shift mistakes affect all ring users. `ADF_RING_SIZE_IN_BYTES_TO_SIZE()` appears suspicious because it shifts `1 << (SIZE - 1)` rather than deriving an encoding from a byte size; current users rely mostly on the forward conversion. `ADF_MAX_INFLIGHTS()` must stay consistent with firmware ring capacity or flow control can overrun ring slots.

## Test Signals
Ring creation with each message size, ring debugfs size reporting, full-ring pressure tests, and CSR dumps provide validation. Static review should include macro expansion for 32/64/128-byte messages and 4K/16K ring defaults.
