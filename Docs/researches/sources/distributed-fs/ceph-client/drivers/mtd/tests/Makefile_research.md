# sources/distributed-fs/ceph-client/drivers/mtd/tests/Makefile

## Purpose
Builds optional MTD kernel test modules when `CONFIG_MTD_TESTS` is enabled.

## Important APIs, Types, and Functions
The Makefile adds modules for OOB, page, read, speed, stress, subpage, torture, NAND ECC, and NAND bit error tests. It also links `mtd_test.o` into each module through repeated `obj-$(CONFIG_MTD_TESTS)` lines and per-module `*-objs` assignments.

## Control Flow
Kbuild evaluates `CONFIG_MTD_TESTS`; when enabled it builds the listed module objects. Per-module object lists map module names such as `mtd_oobtest` to source files such as `oobtest.o`.

## State and Persistence
No runtime state exists. Build output and module availability are controlled by kernel configuration.

## Dependencies and Integration Points
This integrates the test sources into Kbuild under the MTD subsystem. The helper object `mtd_test.o` exports common symbols used by most test modules.

## Risks
Because `mtd_test.o` is listed repeatedly in `obj-*`, build behavior depends on Kbuild handling shared object linkage as intended. Enabling these modules exposes destructive tests that can erase user-selected MTD devices.

## Test Signals
Run kernel builds with `CONFIG_MTD_TESTS=m` or `y` and confirm all expected modules are produced and link against `mtd_test` helper symbols.
