<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor.h -->
# sources/distributed-fs/ceph-client/drivers/dma/mv_xor.h

## Purpose
Private definitions for the Marvell XOR DMAEngine driver, including register offsets, descriptor layout, constants, and software channel/device structures.

## Important APIs, Types, And Functions
Defines descriptor pool sizing, byte-count limits, operation modes, interrupt/error bits, channel register-address macros, MBUS window register macros, and the `WINDOW_COUNT`. `struct mv_xor_device` stores register bases, optional clock, channel pointers, variant type, and cached MBUS windows. `struct mv_xor_chan` tracks descriptor slot lists, DMAEngine channel/device objects, IRQ/tasklet, dummy buffers, mode, and saved PM registers. `struct mv_xor_desc_slot` wraps one hardware descriptor slot and async descriptor. `struct mv_xor_desc` describes the 64-byte hardware descriptor with endian-specific field ordering and `mv_phy_src_idx` abstracts descriptor-swap indexing.

## Control Flow
No executable control flow is implemented here, but macros drive register access and descriptor construction in `mv_xor.c`. Endianness conditionals alter hardware descriptor field order and source index mapping at compile time.

## State And Persistence
The header defines the in-memory state layout used by the driver: descriptor pools, linked lists, dummy DMA buffers, cached windows, and saved register values. Actual state is allocated and mutated by `mv_xor.c` at runtime.

## Dependencies And Integration Points
Depends on Linux types, I/O accessors, DMAEngine types, and IRQ types. It is included by the Marvell XOR source and must match the hardware descriptor ABI exactly, including 64-byte slot size and endian layout.

## Risks And Edge Cases
Incorrect descriptor layout, slot sizing, or endian source indexing would corrupt hardware command interpretation. `MV_XOR_MIN_BYTE_COUNT` and `MV_XOR_MAX_BYTE_COUNT` constrain prep functions. Register macros assume `mv_xor_chan` has valid low/high MMIO bases and channel indices less than `MV_XOR_MAX_CHANNELS`.

## Test Signals
Compile coverage for little- and big-endian configurations, probe self-tests from `mv_xor.c`, and hardware validation of memcpy/XOR descriptors are the main signals that these definitions match the engine ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor.h -->
