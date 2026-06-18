# sources/distributed-fs/ceph-client/drivers/soc/sophgo/Kconfig

## Purpose

This Kconfig file defines build options for Sophgo SoC support drivers under `drivers/soc/sophgo`.

## Important APIs, Types, and Functions

`SOPHGO_CV1800_RTCSYS` is a tristate option for the CV1800 RTC subsystem MFD parent and selects `MFD_CORE`. `SOPHGO_SG2044_TOPSYS` is a tristate option for the SG2044 TOP system-controller MFD parent and also selects `MFD_CORE`. The menu appears only when `ARCH_SOPHGO || COMPILE_TEST`.

## Control Flow

Kconfig evaluation exposes a "Sophgo SoC drivers" menu for native Sophgo builds or compile-test builds. Selecting either option causes the Makefile to build its corresponding module/object.

## State and Persistence Behavior

The file has no runtime state. It controls compile-time inclusion and module availability.

## Dependencies and Integration Points

It integrates the Sophgo MFD parent drivers with the kernel configuration system and the MFD subsystem dependency. Help text documents module names `cv1800-rtcsys` and `sg2044-topsys`.

## Risks and Edge Cases

Both options select MFD core but do not express OF or platform-bus dependencies explicitly, relying on broader kernel infrastructure. The CV1800 help text has a wording issue ("get support the"). Compile-test coverage is permitted even without Sophgo architecture.

## Test Signals

Run Kconfig generation for `ARCH_SOPHGO`, non-Sophgo with `COMPILE_TEST`, built-in, module, and disabled combinations. Confirm Makefile object selection matches the config symbols.
