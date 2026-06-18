
# sources/distributed-fs/ceph-client/include/trace/events/siox.h

## Purpose
Defines tracepoints for SIOX bus data transfer, exposing set-data and get-data operations with device name, data length, and payload bytes.

## Important APIs, Types, and Functions
Events are `siox_set_data` and `siox_get_data`. Both take a `struct siox_device *`, a byte buffer, and a length. Each record stores `dev_name(&sdevice->dev)`, length, and a dynamic byte array rendered as hex.

## Control Flow
SIOX bus/controller code emits the events when writing data to or reading data from a SIOX device. The tracepoint copies the data buffer into a dynamic trace array during `TP_fast_assign`.

## State and Persistence
No bus state is owned by the header. Trace records persist device names and payload snapshots in trace buffers, independent of the original buffer lifetime.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and `struct siox_device` from the SIOX subsystem. Integrates with SIOX bus drivers and device diagnostics.

## Risks
Payload tracing can expose device data and can be expensive for larger transfers. The tracepoint trusts the provided length and buffer pointer. Device names are strings, not stable hardware ids.

## Test Signals
Signals include SIOX read/write operations with tracing enabled, zero-length and maximum-length buffer coverage, device unbind while tracing, and trace hex output comparison against expected bus transactions.
