<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/Makefile

## Purpose

This Makefile links the Turris Omnia MCU core and optional feature objects, plus the Turris signing key helper.

## Important APIs, Types, And Functions

`turris-omnia-mcu-y` starts with `turris-omnia-mcu-base.o`. Conditional object additions include GPIO, keyctl, sys-off/wakeup, TRNG, and watchdog files. `obj-$(CONFIG_TURRIS_SIGNING_KEY)` builds `turris-signing-key.o`.

## Control Flow

Kbuild includes optional MCU objects into the same `turris-omnia-mcu` module based on bool feature symbols. The signing key helper is a separate module/object governed by its tristate.

## State And Persistence

No runtime state exists here; it controls link composition and symbol availability.

## Dependencies And Integration Points

It integrates with the Kconfig symbols from the same directory and with exported helper functions declared in `turris-omnia-mcu.h`.

## Risks

Optional source files assume the corresponding `struct omnia_mcu` fields are compiled in. Link failures would indicate mismatched Kconfig guards or missing inline stubs.

## Test Signals

Run builds for core-only, all features, and individual feature toggles; check module dependencies for `turris-signing-key` when keyctl is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/Makefile -->
