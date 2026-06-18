# sources/distributed-fs/ceph-client/sound/soc/intel/keembay/kmb_platform.h

## Purpose
Defines Keem Bay I2S register offsets, bit fields, capabilities, DMA registers, clock configuration data, and the driver-private runtime state structure.

## Important APIs, Types, And Functions
Macros cover common I2S control registers, per-channel FIFO/enable/config registers, component-parameter field extractors, PSS reset/clock registers, interrupt masks, DMA handshake registers, supported channel constants, and capability bits. `struct i2s_clk_config_data` stores channels, data width, and sample rate. `struct kmb_i2s_info` stores MMIO bases, clocks, active stream state, capabilities, clock mode, DMA data, PIO substreams and pointers, and IEC958 state.

## Control Flow, State, And Persistence
The header has no control flow, but its structure layout is the persistent in-memory state for the platform driver from probe through stream operations.

## Dependencies And Integration Points
Used by `kmb_platform.c`; depends on Linux bitfield helpers, types, clocks through opaque pointers, and ASoC dmaengine data.

## Risks And Test Signals
Risks are incorrect register offsets or field definitions against the Keem Bay databook, mismatch between FIFO-depth extraction and hardware, and structure fields unused or inconsistently updated by DMA vs PIO paths. Test signals are register trace validation, PIO IRQ behavior, DMA handshake behavior, and all compatible variants probing correctly.
