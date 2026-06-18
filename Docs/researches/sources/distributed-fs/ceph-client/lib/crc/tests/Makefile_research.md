# sources/distributed-fs/ceph-client/lib/crc/tests/Makefile

## Purpose
This Makefile builds the CRC KUnit test module/object when `CONFIG_CRC_KUNIT_TEST` is enabled.

## Important APIs, Types, and Functions
It contains one build rule: `obj-$(CONFIG_CRC_KUNIT_TEST) += crc_kunit.o`.

## Control Flow
Kbuild includes `crc_kunit.o` conditionally based on the Kconfig symbol.

## State and Persistence
No state exists.

## Dependencies and Integration Points
It integrates the CRC test suite under the kernel KUnit build system and depends on the surrounding lib/crc test Kconfig.

## Risks and Test Signals
The main risk is the test not being built due to a symbol mismatch. Test signal is that enabling `CONFIG_CRC_KUNIT_TEST` produces and runs the `crc` KUnit suite.
