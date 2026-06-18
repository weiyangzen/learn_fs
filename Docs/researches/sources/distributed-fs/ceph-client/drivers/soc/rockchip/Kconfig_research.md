# sources/distributed-fs/ceph-client/drivers/soc/rockchip/Kconfig

## Purpose

This Kconfig file exposes Rockchip SoC driver options for GRF default programming, IO-domain voltage selection, and DTPM hierarchy registration.

## Important APIs, Types, and Functions

`ROCKCHIP_GRF` is a bool defaulting on for `ARCH_ROCKCHIP`. `ROCKCHIP_IODOMAIN` is a tristate depending on OF. `ROCKCHIP_DTPM` is a tristate depending on `DTPM && m`, meaning it is module-oriented. The menu is visible when `ARCH_ROCKCHIP` or `COMPILE_TEST` is set.

## Control Flow

Kconfig controls which Makefile objects are built. Enabling `ROCKCHIP_GRF` compiles early GRF setup, `ROCKCHIP_IODOMAIN` compiles the regulator-notifier IO-domain driver, and `ROCKCHIP_DTPM` compiles the DTPM hierarchy module.

## State and Persistence Behavior

There is no runtime state in Kconfig. Choices persist in `.config`.

## Dependencies and Integration Points

It integrates with Rockchip architecture config, OF, DTPM, regulator, syscon, and the matching Makefile.

## Risks and Edge Cases

`ROCKCHIP_DTPM` depends on `m`, so built-in DTPM hierarchy behavior is intentionally not offered. `ROCKCHIP_IODOMAIN` lacks an explicit regulator dependency in this file and relies on broader build dependency resolution. Missing defaults could leave critical GRF setup disabled on real platforms.

## Test Signals

Run Rockchip defconfig, allmodconfig, and COMPILE_TEST builds. Verify object inclusion and dependency prompts, especially DTPM module-only behavior.
