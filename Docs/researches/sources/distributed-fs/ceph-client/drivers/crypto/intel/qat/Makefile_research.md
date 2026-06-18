# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/Makefile

## Purpose
This Makefile routes QAT Kconfig symbols to common and family-specific subdirectories.

## Important APIs, Types, And Functions
It sets `subdir-ccflags-y := -I$(src)/qat_common` and conditionally includes `qat_common/` plus subdirectories for DH895xCC, C3XXX, C62X, QAT_4XXX, QAT_420XX, QAT_6XXX, and legacy VF devices.

## Control Flow
When any QAT device selects `CRYPTO_DEV_QAT`, `qat_common/` is built. Each device-family symbol adds its matching subdirectory to the build.

## State And Persistence
No runtime state exists here. It affects include paths and object traversal during build.

## Dependencies And Integration Points
The include path makes common headers available to subdirectory code. The file is coupled to `qat/Kconfig` and each family subdirectory Makefile.

## Risks
Low to moderate build-system risk: common include-path changes affect all QAT family builds.

## Test Signals
Kernel build with multiple QAT family symbols enabled to confirm all subdirectories see `qat_common` headers.
