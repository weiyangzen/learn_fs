# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/Kconfig

## Purpose
Defines configuration for the Arm Firmware Framework for Arm A-profile processors. `ARM_FFA_TRANSPORT` enables the FF-A bus and core interface for client drivers, while `ARM_FFA_SMCCC` selects the SMCCC-based transport helper.

## APIs, Types, And Functions
Kconfig symbols are `ARM_FFA_TRANSPORT`, a tristate depending on `OF` and `ARM64`, and `ARM_FFA_SMCCC`, a bool defaulting to the transport and depending on `ARM64 && HAVE_ARM_SMCCC_DISCOVERY`.

## Control Flow
When `ARM_FFA_TRANSPORT` is enabled, kbuild enters the FF-A Makefile and builds the bus/core module pieces. `ARM_FFA_SMCCC` gates the SMCCC transport implementation used to issue FF-A calls.

## State, Persistence, And Dependencies
Persistent state is limited to `.config`. Dependencies ensure FF-A is only exposed on ARM64 systems with device tree, and SMCCC transport only when SMCCC discovery is present.

## Integration Points
The symbols drive `arm_ffa/Makefile`, `common.h` transport stubs, and the runtime FF-A driver initialized by `rootfs_initcall()`.

## Risks And Test Signals
Risks are overly narrow dependencies that hide compile-test coverage or overly broad dependencies that expose uncallable firmware transport code. Build tests with `ARM_FFA_TRANSPORT=y/m` and SMCCC discovery coverage are the primary signals.
