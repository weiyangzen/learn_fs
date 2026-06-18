# sources/distributed-fs/ceph-client/drivers/iio/light/Makefile

## Purpose

This Makefile maps each `CONFIG_*` light-sensor Kconfig symbol to the object file that should be built for that driver. It is the build-system companion to `drivers/iio/light/Kconfig`.

## Important APIs, Types, and Functions

The important constructs are `obj-$(CONFIG_SYMBOL) += object.o` assignments. For this subset, the mappings are `ACPI_ALS -> acpi-als.o`, `ADJD_S311 -> adjd_s311.o`, `ADUX1020 -> adux1020.o`, `AL3000A -> al3000a.o`, `AL3010 -> al3010.o`, `AL3320A -> al3320a.o`, `APDS9160 -> apds9160.o`, `APDS9300 -> apds9300.o`, `APDS9306 -> apds9306.o`, `APDS9960 -> apds9960.o`, and `AS73211 -> as73211.o`.

## Control Flow

Kbuild expands each `obj-y` or `obj-m` value according to the generated `.config`. Built-in objects are linked into the kernel image or parent built-in archive; module objects become individual loadable modules with names derived from the object basename.

## State and Persistence Behavior

The file has no runtime state. Its build output persists as generated `.o`, `.ko`, and built-in archive content. Ordering is maintained alphabetically by comment convention.

## Dependencies and Integration Points

It integrates directly with the Kconfig symbols in the same directory, Kbuild's recursive make logic, and module metadata emitted by each C file. Multi-object drivers in later entries, such as ST UVIS25 core plus bus wrappers, show how this directory handles split implementations.

## Risks and Edge Cases

A symbol/object mismatch silently omits a configured driver or tries to build a missing file. Alphabetic drift is low risk but increases merge conflicts. Whitespace differences, such as the `STK3310` line spacing, are cosmetic unless they hide a typo.

## Test Signals

Focused tests are build-only: enable each listed symbol as `m` and confirm the expected `.ko` exists, then enable as `y` and confirm built-in linkage. Cross-check Kconfig help module names against generated module names.
