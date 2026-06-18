# sources/distributed-fs/ceph-client/drivers/iio/buffer/Kconfig

## Purpose
This Kconfig file defines selectable Industrial I/O buffer implementation modules: callback buffers, generic DMA buffers, DMAengine integration, hardware consumer buffers, kfifo buffers, and triggered-buffer helpers.

## Important APIs, Types, And Functions
The file defines `IIO_BUFFER_CB`, `IIO_BUFFER_DMA`, `IIO_BUFFER_DMAENGINE`, `IIO_BUFFER_HW_CONSUMER`, `IIO_KFIFO_BUF`, and `IIO_TRIGGERED_BUFFER`. `IIO_BUFFER_DMAENGINE` selects `IIO_BUFFER_DMA`; `IIO_TRIGGERED_BUFFER` selects `IIO_TRIGGER` and `IIO_KFIFO_BUF`.

## Control Flow
There is no runtime control flow. Build-time dependency resolution determines which C objects from the sibling Makefile are compiled and which helper APIs are available to drivers.

## State And Persistence
Kconfig state is persisted in kernel configuration artifacts such as `.config`, not in this source file. It controls module/built-in availability.

## Dependencies And Integration Points
This file is consumed by the kernel Kconfig system and matches object rules in `drivers/iio/buffer/Makefile`. Other IIO drivers select these symbols to gain buffer helper functionality.

## Risks
Missing `select` relationships can lead to link failures or unavailable helper APIs. The help text notes that kfifo buffers do not provide buffer events, so userspace polling semantics differ from event-driven buffers. Dependency descriptions should stay aligned with exported APIs and Makefile entries.

## Test Signals
Build tests should cover configurations for each symbol as built-in and module, especially DMAengine selecting generic DMA and triggered buffers selecting trigger plus kfifo support.
