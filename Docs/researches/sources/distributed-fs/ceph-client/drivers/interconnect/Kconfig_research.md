# sources/distributed-fs/ceph-client/drivers/interconnect/Kconfig

## Purpose
`drivers/interconnect/Kconfig` defines the build-time configuration menu for the Linux interconnect framework, provider families, clock-wrapper support, and KUnit tests.

## Important APIs, Types, And Functions
The top-level `menuconfig INTERCONNECT` enables generic on-chip interconnect management. Within that menu it sources provider Kconfigs for `imx`, `mediatek`, `qcom`, and `samsung`. `INTERCONNECT_CLK` enables clock-backed interconnect nodes and depends on `COMMON_CLK`. `INTERCONNECT_KUNIT_TEST` builds the framework KUnit suite and defaults on under `KUNIT_ALL_TESTS`.

## Control Flow
Kconfig evaluation exposes child provider menus only when `INTERCONNECT` is enabled. Selected symbols drive the companion Makefile to build core, provider, clock, and test objects.

## State And Persistence
This file defines compile-time configuration only. It does not manage runtime state or persistence.

## Dependencies And Integration Points
It integrates with the kernel Kconfig system, provider subdirectories, common clock framework, and KUnit.

## Risks
Provider source lines must stay synchronized with subdirectory Makefile entries. `INTERCONNECT_CLK` has no prompt text, so it is selected by other configs rather than normally user-enabled. Test defaulting depends on global KUnit policy.

## Test Signals
Test menu visibility with `INTERCONNECT=n/y`, provider config inclusion, `INTERCONNECT_CLK` dependency on `COMMON_CLK`, KUnit default behavior, and Makefile symbol consistency.
