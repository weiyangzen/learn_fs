# sources/distributed-fs/ceph-client/drivers/thunderbolt/Kconfig

## Purpose
This Kconfig file selects the unified USB4/Thunderbolt driver and optional debug/test features.

## Important APIs, Types, and Functions
Symbols are `USB4`, `USB4_DEBUGFS_WRITE`, `USB4_DEBUGFS_MARGINING`, `USB4_KUNIT_TEST`, and `USB4_DMA_TEST`. `USB4` depends on PCI and selects crypto/hash/NVMEM support; test and debug features depend on KUnit or debugfs as appropriate.

## Control Flow
There is no runtime flow. Kconfig choices determine whether the main `thunderbolt` module, dangerous debugfs write/margining paths, KUnit tests, and the DMA loopback test module are built.

## State and Persistence Behavior
No runtime state. Configuration persists in the kernel `.config`.

## Dependencies and Integration Points
It feeds the Thunderbolt Makefile and user-visible module availability. Debug options intentionally carry warnings for non-production use.

## Risks and Edge Cases
`USB4_DEBUGFS_WRITE` and margining expose hardware mutation and should not be enabled in distro kernels. KUnit requires built-in KUnit (`KUNIT=y`).

## Test Signals
Build matrix for module/built-in, debugfs options, KUnit, and DMA test; verify dependencies prevent unsupported combinations.
