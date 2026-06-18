<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_11_0_cdr_table.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_11_0_cdr_table.h

## Purpose

`smu_11_0_cdr_table.h` provides two static 4096-byte PRBS7 CDR patterns for SMU11 memory dummy-table training: `NoDbiPrbs7` and `DbiPrbs7`. The data is copied by Navi10 PM code when constructing dummy memory tables for DBI and non-DBI modes.

## Important APIs, Types, and Functions

The file exports two `static unsigned int` arrays and no functions. `NoDbiPrbs7` contains repeating nibble patterns such as `0x0f0f0f0f`/`0xf0f0f0f0`; `DbiPrbs7` contains the corresponding DBI-transformed words. The arrays are deliberately 4096 bytes and documented as 256-byte aligned data, although the C declarations do not enforce an alignment attribute.

## Control Flow

No local control flow exists. `smu11/navi10_ppt.c` includes the header and selects one of the arrays, then copies `0x1000` bytes into a dummy table based on the memory/DBI path. The PMFW or memory-training path then consumes the table indirectly through SMU table upload.

## State and Persistence Behavior

The arrays are compile-time static data. Because they are defined in a header as `static`, each translation unit that includes it gets a private copy. The copied dummy table becomes transient driver/firmware state during training; the source arrays themselves are immutable except that they are not declared `const`.

## Dependencies

The file uses `#pragma pack(push, 1)`/`pop` and a simple include guard. It depends on consumers knowing the exact 4096-byte size and selecting the correct DBI variant. It has no dependency on SMU structures beyond the include site.

## Integration Points

The only direct integration found in this tree is `smu11/navi10_ppt.c`, where `memcpy(dummy_table, &NoDbiPrbs7[0], 0x1000)` or `memcpy(dummy_table, &DbiPrbs7[0], 0x1000)` seeds a PMFW dummy table.

## Risks and Edge Cases

The arrays are mutable static header definitions, so accidental writes in one translation unit would not affect others but could corrupt that unit's future training copies. Size assumptions are implicit; changing array length without changing the `0x1000` copy size can overrun or truncate. The comment says 256-byte aligned, but no attribute enforces it; consumers relying on source-array alignment instead of destination alignment would be fragile.

## Test Signals

Build coverage for `navi10_ppt.c`, static checks that both arrays are exactly 1024 `unsigned int` elements, memory-training smoke tests, and comparing uploaded dummy-table bytes against known-good PRBS7/DBI vectors are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_11_0_cdr_table.h -->
