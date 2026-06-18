# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/isp/irqsrcs_isp_4_1.h

## Purpose
This header defines ISP 4.1 interrupt source IDs for AMDGPU image-signal-processor support. It maps semaphore timeout, ringbuffer, MIPI, I2C, flash, and debug events to numeric source IDs.

## Important APIs, Types, And Data
The file defines `ISP_4_1__SRCID__*` constants. Semaphore-related IDs include wait fail, wait incomplete, and signal incomplete timeouts. Ringbuffer event IDs cover base-address changes and write-pointer changes for ringbuffers 5 through 16. Notably ringbuffer 9 through 16 wrap into IDs `0x00` through `0x0F`, while ringbuffers 5 through 8 use `0x15` through `0x1C`. Peripheral IDs include `ISP_MIPI0`, `ISP_MIPI1`, `ISP_I2C0`, `ISP_I2C1`, `ISP_FLASH0`, `ISP_FLASH1`, and `ISP_DEBUG`.

## Control Flow
There are no functions. `amdgpu/isp_v4_1_0.c` and `isp_v4_1_1.c` include this header and use the ringbuffer write-pointer IDs to set up ISP interrupt handling for firmware/queue notifications.

## State And Persistence
The constants are immutable. Runtime state consists of IRQ registration and ISP queue/ring state that reacts to these source IDs.

## Dependencies And Integration Points
The header integrates with the ISP v4.1 AMDGPU IP implementation, SOC15 IH dispatch, ringbuffer notification handling, MIPI sensor paths, I2C pad interrupts, flash control, and debug reporting.

## Risks
The non-monotonic ringbuffer numbering is easy to misread: base/write-pointer IDs for ringbuffers 9-16 start at zero. Assuming source IDs increase with ring number across the whole range will misroute notifications. Missing semaphore timeout handling can hide firmware deadlocks.

## Test Signals
Build ISP v4.1.0 and v4.1.1. Runtime validation should cover ISP firmware queue/ringbuffer write-pointer interrupts for rings 9-16, MIPI input events, I2C pad events, flash interrupts, semaphore timeout diagnostics, and debug interrupt logging.
