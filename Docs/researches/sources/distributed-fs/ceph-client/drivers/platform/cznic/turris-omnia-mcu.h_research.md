<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu.h -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu.h

## Purpose

This internal header defines the shared Turris Omnia MCU driver state, feature-specific fields, constants for MCU cryptographic sizes, and optional feature registration prototypes or stubs.

## Important APIs, Types, And Functions

`struct omnia_mcu` is the central state object. It always contains the I2C client, MCU type, feature bitmap, board serial/MAC/revision, and conditionally contains GPIO/IRQ state, RTC wake state, watchdog, hwrng, TRNG completion, signing completion/lock/signature/public key, and related fields. It declares `omnia_mcu_register_gpiochip()`, `omnia_mcu_request_irq()`, `omnia_mcu_register_keyctl()`, `omnia_mcu_register_sys_off_and_wakeup()`, `omnia_mcu_register_trng()`, and `omnia_mcu_register_watchdog()` or no-op inline stubs.

## Control Flow

`turris-omnia-mcu-base.c` includes this header and can call every registration helper regardless of feature configuration. Kconfig guards decide whether calls link to real implementations or return success from inline stubs.

## State And Persistence

The header defines the layout of all per-device runtime state. Persistent hardware data is cached in identity fields, while feature state fields mirror kernel-side state for GPIO, RTC, watchdog, RNG, and signing operations.

## Dependencies And Integration Points

It includes completion, gpio, hwrng, Ethernet address, interrupt, mutex, watchdog, and workqueue headers. It is private to the CZ.NIC platform driver directory.

## Risks

Conditional fields must remain aligned with conditional source files; using a field without the matching `CONFIG_` guard breaks builds. Inline stubs make absent features silently successful, so the core must rely on feature files to enforce real registration.

## Test Signals

Compile all feature combinations, inspect `struct omnia_mcu` field availability, and verify no optional source references fields outside their Kconfig guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu.h -->
