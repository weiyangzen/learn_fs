# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_sram_mgr.h

## Purpose

`cc_sram_mgr.h` declares the internal SRAM allocator and SRAM descriptor-copy helper for the ccree driver. It provides a compact contract for modules that need fixed CryptoCell SRAM workspace.

## Important APIs, Types, And Functions

The header defines default `CC_CC_SRAM_SIZE` as 4096 if not supplied by the build, forward-declares `struct cc_drvdata`, defines `NULL_SRAM_ADDR`, and declares `cc_sram_mgr_init()`, `cc_sram_alloc()`, and `cc_set_sram_desc()`.

## Control Flow

There is no executable control flow in the header. The declarations support probe-time initialization, monotonic allocation, and descriptor construction in implementation files.

## State And Persistence Behavior

The header owns no state but documents that SRAM allocation returns offsets into volatile device SRAM. `NULL_SRAM_ADDR` is `(u32)-1`, so valid users must compare against that sentinel rather than zero.

## Dependencies And Integration Points

It is included by hash, AEAD, PM, driver, and SRAM manager code. `cc_set_sram_desc()` depends on `struct cc_hw_desc` being visible in callers through included descriptor definitions.

## Risks And Edge Cases

The default 4 KiB size must match the targeted hardware or platform override. Treating address 0 as allocation failure would be wrong because SRAM pools can start at offset 0 on newer hardware. Users must remember there is no free operation.

## Test Signals

Build coverage catches signature drift. Probe and crypto registration validate allocation sizes. Tests on older and newer CryptoCell revisions validate both threshold-based and zero-based SRAM pool starts.
