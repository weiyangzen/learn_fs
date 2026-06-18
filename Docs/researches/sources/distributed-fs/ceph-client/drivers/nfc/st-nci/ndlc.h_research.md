# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/ndlc.h

## Purpose
`ndlc.h` declares the ST low-level transport object and exported NDLC lifecycle/send/receive API.

## Important APIs and types
- `struct llt_ndlc` stores the NCI device, physical ops/id, T1/T2 timers and active flags, receive/send/ack-pending queues, state-machine work item, parent device, hard-fault code, and powered flag.
- Prototypes expose `ndlc_open()`, `ndlc_close()`, `ndlc_send()`, `ndlc_recv()`, `ndlc_probe()`, and `ndlc_remove()`.

## Control flow and integration
Physical drivers allocate NDLC through `ndlc_probe()` and receive back an `llt_ndlc *`. The ST_NCI core opens/closes/sends through NDLC, while physical IRQ handlers feed received skbs through `ndlc_recv()`.

## State, dependencies, and risks
The structure concentrates link state shared across core and physical layers. `hard_fault` is the transport-wide latch for unrecoverable hardware errors. Consumers must respect that the header does not provide external locking; all state transitions are expected to go through NDLC functions and worker/timer callbacks.

## Test signals
Compile tests should validate both I2C and SPI users. Runtime tests should ensure hard-fault, powered, and queue states stay consistent across open, send, receive, close, and remove.
