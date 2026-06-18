# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/Makefile

## Purpose
Architecture-gated build metadata for the s390 Ultravisor UAPI selftest.

## Important APIs, Types, And Functions
Includes `Build.include`, checks `uname -m`, and on s390x defines `TEST_GEN_PROGS := test_uvdevice`, `LINUX_TOOL_ARCH_INCLUDE`, `CFLAGS += -Wall -Werror -static $(KHDR_INCLUDES) -I...`, then includes `../../../lib.mk`. On non-s390x it defines inert `all/clean/run_tests/install` targets.

## Control Flow
Non-s390x builds intentionally do nothing. s390x builds compile a static `test_uvdevice` binary with architecture UAPI include paths.

## State And Persistence
No runtime state beyond generated binary.

## Dependencies And Integration Points
Requires s390x architecture headers and `asm/uvdevice.h`. Pairs with `config` requesting the UV UAPI device.

## Risks
The `uname -m` gate means cross-build environments may skip unless build host reports s390x. Static `-Werror` builds can fail on warning changes.

## Test Signals
On s390x, successful build creates `test_uvdevice`; elsewhere silent no-op is expected.
