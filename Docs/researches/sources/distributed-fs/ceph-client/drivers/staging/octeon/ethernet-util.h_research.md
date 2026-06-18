# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-util.h

## Purpose
Small inline helpers for translating Octeon hardware buffer and port identifiers.

## Important APIs, Types, And Functions
Defines `cvm_oct_get_buffer_ptr()`, `INTERFACE()`, and `INDEX()`.

## Control Flow
RX/TX/free paths call `cvm_oct_get_buffer_ptr()` to recover the original aligned packet-buffer pointer from a `cvmx_buf_ptr`. Port setup and register programming call `INTERFACE()` and `INDEX()` to map IPD ports to helper interface/index values, with special handling for the POW virtual port.

## State And Persistence
No state.

## Dependencies And Integration Points
Depends on CVMX physical-address conversion and helper port mapping APIs. Included by most Octeon implementation files.

## Risks
`INTERFACE()` panics on illegal ports, so callers must validate hardware port ids. Buffer pointer arithmetic assumes Octeon FPA back-pointer semantics and 128-byte alignment.

## Test Signals
Known port/interface mappings, virtual POW port mapping to interface 10, invalid port panic expectations, and RX/TX buffer pointer round-trip tests.
