# sources/distributed-fs/ceph-client/tools/testing/nvdimm/pmem_test.c

## Purpose
`pmem_test.c` provides a watermark function for the test-linked pmem module.

## Important APIs, Types, And Functions
`nfit_test_watermark(pmem)` defines and exports `pmem_test()`.

## Control Flow
The generated function logs a debug message and returns `0`.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
The watermark is linked into the `nd_pmem` test module and called by the nfit/ndtest module init paths to validate module composition.

## Risks
It is a sentinel only and does not validate pmem read/write, badblock, or DAX behavior.

## Test Signals
Presence and successful return of `pmem_test()` confirm the test module is linked as expected.
