# sources/distributed-fs/ceph-client/drivers/iio/addac/Makefile

## Purpose
This Makefile maps ADDAC Kconfig symbols to object files for the Linux IIO build.

## Important APIs, Types, And Functions
It defines `obj-$(CONFIG_AD74115) += ad74115.o`, `obj-$(CONFIG_AD74413R) += ad74413r.o`, and `obj-$(CONFIG_STX104) += stx104.o`. These lines are the build-system contract connecting Kconfig choices to compilation units.

## Control Flow
During kbuild evaluation, each `obj-$()` entry expands to `obj-y`, `obj-m`, or empty depending on the selected configuration. Built-in selections link into the kernel; module selections produce separate `.ko` modules.

## State And Persistence
The file has no runtime state. Its persistent effect is the kernel/module build graph.

## Dependencies And Integration Points
It integrates directly with `drivers/iio/addac/Kconfig` and kbuild. The entries are kept alphabetical, matching the local convention and making future additions easier to review.

## Risks And Test Signals
Risks are stale entries after renames, missing entries for new Kconfig symbols, or ordering churn. Test signals are successful `M=drivers/iio/addac` builds for each config, module artifact names matching Kconfig help, and no orphaned Kconfig symbols without corresponding objects.
