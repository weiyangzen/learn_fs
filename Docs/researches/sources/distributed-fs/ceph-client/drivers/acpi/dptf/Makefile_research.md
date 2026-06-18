# sources/distributed-fs/ceph-client/drivers/acpi/dptf/Makefile

## Purpose
Builds the DPTF ACPI participant drivers selected by Kconfig.

## Important APIs, Types, And Functions
The object mappings are `obj-$(CONFIG_DPTF_POWER) += dptf_power.o` and `obj-$(CONFIG_DPTF_PCH_FIVR) += dptf_pch_fivr.o`.

## Control Flow
Kbuild expands each `obj-*` line according to the corresponding configuration value. Built-in selections compile into the kernel image, module selections produce loadable modules, and disabled selections omit the object.

## State And Persistence
No runtime state. Build output depends entirely on `.config`.

## Dependencies And Integration Points
Depends on Kbuild and the Kconfig symbols from the sibling `Kconfig`. It is included by the parent ACPI drivers Makefile.

## Risks
The file is simple; risk is limited to symbol/object drift if source files or Kconfig option names are renamed.

## Test Signals
Build tests should verify `dptf_power.o` and `dptf_pch_fivr.o` are produced for built-in/module configurations and absent when disabled.
