# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/Kconfig

## Purpose

This Kconfig file defines build-time configuration for the main Marvell 88E6xxx DSA switch driver family, its optional PTP support, and optional LED support. It explicitly describes the family driver as supporting most 88E6xxx chips except 88E6060, which is handled by the separate `mv88e6060.c` driver.

## Important APIs, Types, And Options

`NET_DSA_MV88E6XXX` is a tristate option depending on `NET_DSA` and selecting `IRQ_DOMAIN`, `NET_DSA_TAG_EDSA`, and `NET_DSA_TAG_DSA`. `NET_DSA_MV88E6XXX_PTP` is a bool controlled by whether the base driver and `PTP_1588_CLOCK` are built-in or modular-compatible. `NET_DSA_MV88E6XXX_LEDS` defaults to yes, depends on the base driver, LED class availability compatible with the base build mode, and LED triggers.

## Control Flow

Kconfig evaluation controls which objects are compiled from the paired Makefile. Enabling the base driver builds `mv88e6xxx.o`; enabling PTP adds hardware timestamp support objects; enabling LED support adds LED control objects. The selected DSA tag protocols and IRQ domain support ensure required subsystems are available.

## State And Persistence Behavior

There is no runtime state. Persistent effects are kernel configuration symbols recorded in the build configuration and used by Makefile conditionals and preprocessor paths.

## Dependencies And Integration Points

The file integrates with the kernel networking DSA menu, PTP clock subsystem, LED subsystem, and the `mv88e6xxx/Makefile`. Its explicit exclusion of 88E6060 is an integration boundary with `drivers/net/dsa/mv88e6060.c`.

## Risks

Dependency expressions for PTP and LED support must preserve built-in/module compatibility. If a feature object is added to the Makefile without a matching Kconfig dependency, builds can fail or expose unusable options. The LED dependency on `LEDS_CLASS=y || LEDS_CLASS=NET_DSA_MV88E6XXX` is important to avoid module/builtin ordering issues.

## Test Signals

Useful signals are configuration matrix builds for built-in and module variants, with and without `PTP_1588_CLOCK`, `LEDS_CLASS`, and `LEDS_TRIGGERS`, plus verification that the base option selects both DSA tag protocols and IRQ domain support.
