# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fau.h

## Purpose
This header provides inline APIs for Octeon's Fetch-and-Add Unit, a hardware atomic counter/register block. It supports synchronous fetch-add, tagwait fetch-add, asynchronous IOBDMA fetch-add into scratchpad, atomic add, and atomic write for 8/16/32/64-bit FAU registers.

## Important APIs, Types, and Functions
It defines the FAU I/O address bit fields, `cvmx_fau_op_size_t`, tagwait return structs for each width, and `cvmx_fau_async_tagwait_result_t`. Address builders `__cvmx_fau_store_address()`, `__cvmx_fau_atomic_address()`, and `__cvmx_fau_iobdma_data()` encode no-add/tagwait/register/size/value/scratch fields. Public inline APIs include `cvmx_fau_fetch_and_add*`, `cvmx_fau_tagwait_fetch_and_add*`, `cvmx_fau_async_fetch_and_add*`, `cvmx_fau_async_tagwait_fetch_and_add*`, `cvmx_fau_atomic_add*`, and `cvmx_fau_atomic_write*`.

## Control Flow
Synchronous fetch-add builds a special I/O load address and reads the old value with a width-specific helper. Smaller widths XOR the register address with endian swizzle constants. Tagwait forms set the tagwait bit and decode an error/value return. Async forms send an IOBDMA command to place the result in scratchpad. Atomic add/write forms write to a special I/O store address, using `noadd` to distinguish add from overwrite.

## State and Persistence Behavior
FAU register values are persistent hardware counters/registers until updated. Async operations write completion data to local scratchpad addresses supplied by the caller. The header itself keeps no software state.

## Dependencies and Integration Points
It depends on CVMX address builders, bit builders, I/O read/write helpers, scratchpad/IOBDMA send support, endian bitfield choices, and FAU register allocations from `cvmx-config.h`. It integrates with packet counters, synchronization primitives, POW/tag scheduling, and any fast shared counters in CVMX code.

## Risks
Only low bits of the add value are encoded for 32/64-bit operations, so large increments can truncate. Register alignment is width-specific and must match the typedef class. Async scratch addresses must be 8-byte aligned and reserved. Endian swizzling is required for sub-64-bit registers. Tagwait calls can return timeout/error and callers must inspect the error bit.

## Test Signals
Test 8/16/32/64-bit add and write operations, endian-correct subword registers, tagwait timeout handling, async scratchpad completion, counter wrap/truncation behavior, and concurrent multi-core increments.
