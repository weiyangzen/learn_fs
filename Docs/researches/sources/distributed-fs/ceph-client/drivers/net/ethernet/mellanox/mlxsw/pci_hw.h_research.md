# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci_hw.h

## Purpose
`pci_hw.h` defines PCI hardware constants and descriptor/CQE/EQE layout accessors for the mlxsw PCI backend. It centralizes BAR sizing, command-interface register offsets, reset timing, doorbell offsets, queue limits, descriptor sizes, WQE fields, CQE version handling, mirror metadata, timestamps, and EQE fields.

## Important APIs, Types, and Functions
- Constants define BAR0 size, page size, CIR register offsets/bits/status shift, reset wait/timeout, FW-ready register/magic, doorbell regions, queue counts, descriptor sizes, and scatter/gather limits.
- WQE accessors define completion, local-processing, type, checksum, byte-count, and DMA-address fields.
- `enum mlxsw_pci_cqe_v` distinguishes CQE v0/v1/v2. `mlxsw_pci_cqe_item_helpers()` dispatches version-specific field accessors.
- CQE accessors cover ingress source, LAG fields, WQE counter, byte count, trap ID, CRC/error/send flags, descriptor queue, mirror congestion/class/latency/reason, TX source metadata, ACL cookie/original length, owner bit, and timestamp fields.
- Inline helpers combine split fields such as mirror congestion and timestamp seconds/nanoseconds.
- EQE accessors cover event type/subtype, completion queue number, owner bit, command token/status, and command output parameters.

## Control Flow
This header has no standalone runtime flow. `pci.c` calls the generated accessors when setting WQEs, interpreting CQEs, polling owner bits, decoding mirror/sample metadata, and handling EQ events.

## State and Persistence
The header defines static item descriptors in the including translation unit and mutates caller-owned DMA buffers through generated accessors. Hardware queue memory layout is the persistent contract.

## Dependencies and Integration Points
It depends on `item.h` for generated accessors and on Linux bit operations. It is tightly coupled to `pci.c` queue setup and data-path code, and to firmware-reported CQE version support.

## Risks
Any field offset/shift mismatch breaks DMA descriptor interpretation. CQE v2 is larger than v0/v1; queue element size/count must match firmware AQ capabilities. Owner-bit accessor selection must match queue CQE version or NAPI can either miss completions or read hardware-owned entries. Timestamp/mirror metadata invalid sentinel values must be honored by callers.

## Test Signals
Use synthetic descriptor buffers to round-trip key WQE/CQE/EQE fields. Runtime validation includes TX/RX traffic over CQE v0/v1/v2 hardware, mirror and sample traps with metadata, PTP timestamps, command EQEs, and queue owner-bit transitions across wraparound.
