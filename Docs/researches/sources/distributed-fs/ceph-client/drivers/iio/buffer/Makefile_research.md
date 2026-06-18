# sources/distributed-fs/ceph-client/drivers/iio/buffer/Makefile

## Purpose
The Makefile maps IIO buffer Kconfig symbols to their implementation objects.

## Important APIs, Types, And Functions
It builds `industrialio-buffer-cb.o`, `industrialio-buffer-dma.o`, `industrialio-buffer-dmaengine.o`, `industrialio-hw-consumer.o`, `industrialio-triggered-buffer.o`, and `kfifo_buf.o` according to their `CONFIG_*` symbols.

## Control Flow
There is no runtime behavior. Kbuild evaluates `obj-$(CONFIG_...)` assignments and includes matching objects in the kernel image or modules.

## State And Persistence
The file has no runtime state. It persists the build contract between Kconfig symbols and object names.

## Dependencies And Integration Points
It integrates with the kernel build system and must remain consistent with `drivers/iio/buffer/Kconfig` and source file names. The comment asks maintainers to preserve alphabetical ordering.

## Risks
Renaming a source file or Kconfig symbol without updating this Makefile breaks builds. Ordering is mostly maintainability, but missing `obj-*` entries silently omit enabled functionality.

## Test Signals
Use configuration matrix builds for all buffer symbols, plus module install checks to verify expected object/module names.
