<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/Kconfig

## Purpose

This Kconfig file defines platform support for CZ.NIC Turris hardware, primarily the Turris Omnia MCU multi-function driver and the supporting Turris signing key type.

## Important APIs, Types, And Functions

`CZNIC_PLATFORMS` gates the menu. `TURRIS_OMNIA_MCU` enables the I2C MCU core. Optional bool features are GPIO/IRQ, system-off wakeup, watchdog, TRNG, and keyctl signing. `TURRIS_SIGNING_KEY` is a tristate helper selected by keyctl support.

## Control Flow

When the platform menu and MCU core are enabled, the subordinate feature options select additional source files into the same MCU module. Several options default to yes so supported hardware exposes all MCU features by default.

## State And Persistence

The file has no runtime state. It determines which portions of `struct omnia_mcu` and which registration functions are compiled.

## Dependencies And Integration Points

Dependencies express Armada/Turris platform scope, I2C, OF GPIO IRQ chips, RTC class, watchdog core, hw_random, keyrings, and asymmetric key support.

## Risks

Feature options are bools under a tristate core, so optional code is compiled into the MCU module rather than separate modules. TRNG depends on GPIO because it requests an MCU interrupt through the GPIO/IRQ layer. Keyctl selects the signing-key helper, adding key subsystem exposure.

## Test Signals

Build with each feature disabled/enabled, compile-test non-Armada configs, dependency resolution for HW_RANDOM and KEYS, and module link coverage for feature-specific inline stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/Kconfig -->
