# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_sram_mgr.c

## Purpose

`cc_sram_mgr.c` provides a simple monotonic allocator for CryptoCell internal SRAM and helper code to build descriptor sequences that copy constant words into SRAM. It is used for MLLI workspace allocation and hash/AEAD constant staging.

## Important APIs, Types, And Functions

`cc_sram_mgr_init()` initializes `drvdata->sram_free_offset`, using `HOST_SEP_SRAM_THRESHOLD` on hardware older than revision 712 to skip ROM-reserved SRAM. `cc_sram_alloc()` returns a 4-byte-aligned SRAM offset or `NULL_SRAM_ADDR`. `cc_set_sram_desc()` appends BYPASS descriptors that write each source word as a constant to consecutive SRAM addresses.

## Control Flow

Initialization sets the starting offset once. Each allocation validates 4-byte alignment and remaining capacity, returns the current offset, and advances the free pointer. Constant-copy setup iterates over source words, initializing one descriptor per word with `set_din_const()`, `set_dout_sram()`, and `set_flow_mode(BYPASS)`.

## State And Persistence Behavior

The allocator state is only `drvdata->sram_free_offset`; it is monotonic and has no free operation. SRAM contents are volatile and lost across power-down, so users such as hash code must re-copy constants during resume. Allocation layout persists only for the driver lifetime.

## Dependencies And Integration Points

The file depends on `cc_driver.h`, host register definitions, descriptor setters, and `cc_sram_mgr.h`. It is called during driver probe before hash/cipher/AEAD resources are allocated, and by hash initialization to create SRAM-copy descriptors submitted through the request manager.

## Risks And Edge Cases

All allocations must be multiples of 4. The older-hardware threshold must itself be 4-byte aligned or initialization fails. There is no deallocation or compaction, so allocation order and size calculations must be stable. `cc_set_sram_desc()` assumes the caller provided enough descriptor slots for one descriptor per word.

## Test Signals

Probe logs should not show invalid SRAM threshold or insufficient space. Hash registration validates enough SRAM for digest constants. AEAD and MLLI-heavy operations validate shared SRAM allocation pressure. Suspend/resume tests validate that contents, not allocation offsets, are restored by users.
