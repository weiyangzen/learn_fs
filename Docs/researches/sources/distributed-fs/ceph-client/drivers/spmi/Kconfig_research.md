# sources/distributed-fs/ceph-client/drivers/spmi/Kconfig

## Purpose

`drivers/spmi/Kconfig` defines the build-time configuration menu for SPMI support and the platform controller drivers in this tree. It gates the common SPMI framework and selects which vendor controller implementations are built.

## Important APIs, Types, And Functions

The top-level `menuconfig SPMI` is a tristate that enables System Power Management Interface support. Child symbols are `SPMI_APPLE`, `SPMI_HISI3670`, `SPMI_MSM_PMIC_ARB`, and `SPMI_MTK_PMIF`. The Hisilicon and Qualcomm options select `IRQ_DOMAIN_HIERARCHY`; controller options depend on their architecture families or `COMPILE_TEST`, and several also depend on `HAS_IOMEM`.

## Control Flow And State

There is no runtime control flow. The file controls compilation and module availability. Enabling `SPMI` exposes the child menu; disabling it excludes the common framework, devres helpers, and all listed controller drivers through the companion Makefile.

## State And Persistence Behavior

The selected values persist in the kernel build configuration. `SPMI_MSM_PMIC_ARB` defaults to enabled on Qualcomm builds; the other platform drivers require explicit selection or dependency-driven builds.

## Dependencies And Integration Points

The symbols map directly to object selections in `drivers/spmi/Makefile`. `IRQ_DOMAIN_HIERARCHY` is selected for controllers that provide hierarchical interrupt domains. Architecture dependencies prevent accidental platform-driver exposure except for compile-test coverage.

## Risks And Test Signals

Risks are mostly configuration-level: missing `HAS_IOMEM` or IRQ-domain selections can break builds, overly narrow dependencies can hide compile coverage, and overly broad defaults can build unusable platform drivers. Test signals are `allmodconfig`, platform defconfig, `COMPILE_TEST` builds for Apple/Hisilicon/MediaTek/Qualcomm paths, and checking that each enabled symbol pulls the expected object files.
